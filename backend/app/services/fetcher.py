import ipaddress
import socket

import httpx
from bs4 import BeautifulSoup
from readability import Document # type: ignore

from app.config import Settings
from app.exceptions import ExtractError


def _is_private_ip(ip: str) -> bool:
    """Return True if the IP address belongs to a private/reserved range."""
    try:
        addr = ipaddress.ip_address(ip)
        return (
            addr.is_private
            or addr.is_loopback
            or addr.is_link_local
            or addr.is_multicast
            or addr.is_reserved
            or addr.is_unspecified
        )
    except ValueError:
        return True


def _resolve_and_validate_host(url: str) -> None:
    """Resolve hostname to IPs and block private/reserved addresses (SSRF protection)."""
    try:
        from urllib.parse import urlparse

        hostname = urlparse(url).hostname
        if not hostname:
            raise ExtractError("Invalid URL: missing hostname.", status_code=422)

        results = socket.getaddrinfo(hostname, None)
    except ExtractError:
        raise
    except OSError as exc:
        raise ExtractError(
            f"Could not resolve host: {exc}", status_code=502
        ) from exc

    for _family, _type, _proto, _canonname, sockaddr in results:
        ip = sockaddr[0]
        if _is_private_ip(ip):
            raise ExtractError(
                "Requests to private or reserved IP addresses are not allowed.",
                status_code=422,
            )


def _extract_author(raw_html: str) -> str | None:
    """Extract the author name from common meta tag patterns."""
    soup = BeautifulSoup(raw_html, "lxml")
    candidates = [
        {"name": "author"},
        {"property": "article:author"},
        {"property": "og:article:author"},
        {"name": "twitter:creator"},
    ]
    for attrs in candidates:
        tag = soup.find("meta", attrs)
        if tag and tag.get("content"):
            value = tag["content"].strip().lstrip("@")
            # Skip values that look like profile URLs rather than names.
            if value and not value.startswith("http"):
                return value
    return None


def _extract_main_content(html: str) -> tuple[str, str | None]:
    """Use Mozilla Readability to isolate the main article body.

    Prepends the page title (h1) and author byline so they appear in the
    converted Markdown.

    Returns:
        (main_html, page_title)
    """
    doc = Document(html)
    title = doc.title() or None
    author = _extract_author(html)
    main_html = doc.summary(html_partial=False)

    # Inject title and author at the top of <body>.
    soup = BeautifulSoup(main_html, "lxml")
    body = soup.find("body")
    if body:
        if author:
            byline = soup.new_tag("p")
            em = soup.new_tag("em")
            em.string = f"By {author}"
            byline.append(em)
            body.insert(0, byline)
        if title:
            h1 = soup.new_tag("h1")
            h1.string = title
            body.insert(0, h1)

    return str(soup), title


async def fetch_html(url: str, settings: Settings) -> tuple[str, str | None]:
    """Fetch HTML from a public URL with SSRF protection and size limits.

    Returns:
        (html_content, page_title)
    """
    _resolve_and_validate_host(url)

    max_bytes = settings.max_response_size_mb * 1024 * 1024

    try:
        async with httpx.AsyncClient(
            timeout=settings.request_timeout_seconds,
            follow_redirects=True,
            max_redirects=5,
        ) as client:
            # Stream the response so we can enforce the size limit early.
            async with client.stream("GET", url) as response:
                # Check Content-Length header before downloading the body.
                content_length = response.headers.get("content-length")
                if content_length and int(content_length) > max_bytes:
                    raise ExtractError(
                        f"Response exceeds maximum allowed size of {settings.max_response_size_mb} MB.",
                        status_code=422,
                    )

                # Enforce only HTML / plain-text content types.
                content_type = response.headers.get("content-type", "")
                if not any(
                    ct in content_type for ct in ("text/html", "text/plain")
                ):
                    raise ExtractError(
                        f"Unsupported content type: {content_type!r}. Only text/html and text/plain are accepted.",
                        status_code=422,
                    )

                chunks: list[bytes] = []
                total = 0
                async for chunk in response.aiter_bytes():
                    total += len(chunk)
                    if total > max_bytes:
                        raise ExtractError(
                            f"Response exceeds maximum allowed size of {settings.max_response_size_mb} MB.",
                            status_code=422,
                        )
                    chunks.append(chunk)

                response.raise_for_status()

    except ExtractError:
        raise
    except httpx.TimeoutException as exc:
        raise ExtractError(
            "The request timed out. The target server may be too slow or unreachable.",
            status_code=504,
        ) from exc
    except httpx.HTTPStatusError as exc:
        raise ExtractError(
            f"The target server returned an error: HTTP {exc.response.status_code}.",
            status_code=502,
        ) from exc
    except httpx.RequestError as exc:
        raise ExtractError(
            f"Failed to reach the target URL: {exc}",
            status_code=502,
        ) from exc

    html_content = b"".join(chunks).decode(errors="replace")
    return _extract_main_content(html_content)
