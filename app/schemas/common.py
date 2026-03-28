from __future__ import annotations
from pydantic import BaseModel
from typing import Any, Generic, List, TypeVar, Optional

T = TypeVar("T")


class Response(BaseModel, Generic[T]):
    code: int = 0
    message: str = "success"
    data: Optional[Any] = None

    @classmethod
    def ok(cls, data: Any = None, message: str = "success") -> Response:
        return cls(code=0, message=message, data=data)

    @classmethod
    def error(cls, code: int, message: str) -> Response:
        return cls(code=code, message=message, data=None)


class PagedData(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int
    has_more: bool


class PageQuery(BaseModel):
    page: int = 1
    page_size: int = 20

    def offset(self) -> int:
        return (self.page - 1) * self.page_size
