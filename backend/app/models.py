from typing import Generic, TypeVar

from pydantic import AnyHttpUrl, BaseModel, Field

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    data: T | None = None
    error: str | None = None


class ExtractRequest(BaseModel):
    url: AnyHttpUrl


class ExtractResponse(BaseModel):
    html: str
    title: str | None = None
    url: str


class ConvertRequest(BaseModel):
    html: str = Field(min_length=1)


class ConvertResponse(BaseModel):
    markdown: str


class HealthResponse(BaseModel):
    status: str
