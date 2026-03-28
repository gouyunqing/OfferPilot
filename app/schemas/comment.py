from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from enum import Enum


class VoteType(str, Enum):
    up = "up"
    down = "down"
    cancel = "cancel"


class CommentUserRef(BaseModel):
    id: str
    nickname: str
    level: int
    level_icon: str


class CommentItem(BaseModel):
    id: str
    content: str
    content_blurred: bool
    user: CommentUserRef
    upvotes: int
    downvotes: int
    my_vote: Optional[str] = None
    created_at: datetime


class CommentCreateRequest(BaseModel):
    content: str


class CommentCreateResponse(BaseModel):
    id: str
    content: str
    exp_gained: int
    message: str


class CommentVoteRequest(BaseModel):
    vote_type: VoteType


class CommentVoteResponse(BaseModel):
    upvotes: int
    downvotes: int
    my_vote: Optional[str]
