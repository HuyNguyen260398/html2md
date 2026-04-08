from typing import Annotated

from fastapi import APIRouter, Depends

from app.config import Settings, settings
from app.models import ApiResponse, ExtractRequest, ExtractResponse
from app.services.fetcher import fetch_html

router = APIRouter(prefix="/extract", tags=["extract"])


def get_settings() -> Settings:
    return settings


SettingsDep = Annotated[Settings, Depends(get_settings)]


@router.post("/")
async def extract(
    body: ExtractRequest,
    app_settings: SettingsDep,
) -> ApiResponse[ExtractResponse]:
    url_str = str(body.url)
    html_content, title = await fetch_html(url_str, app_settings)
    return ApiResponse(
        data=ExtractResponse(html=html_content, title=title, url=url_str),
        error=None,
    )
