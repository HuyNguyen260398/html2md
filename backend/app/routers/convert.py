from fastapi import APIRouter

from app.models import ApiResponse, ConvertRequest, ConvertResponse
from app.services.converter import convert_html_to_markdown

router = APIRouter(prefix="/convert", tags=["convert"])


@router.post("/")
def convert(body: ConvertRequest) -> ApiResponse[ConvertResponse]:
    markdown = convert_html_to_markdown(body.html)
    return ApiResponse(data=ConvertResponse(markdown=markdown), error=None)
