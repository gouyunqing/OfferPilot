from pydantic import BaseModel


class FavoriteCreateRequest(BaseModel):
    question_id: str


class FavoriteCreateResponse(BaseModel):
    favorite_count: int
    question_favorite_count: int
