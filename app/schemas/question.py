from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional, List
from enum import Enum


class QuestionType(str, Enum):
    bagu = "bagu"
    leetcode = "leetcode"


class RecruitType(str, Enum):
    campus = "campus"
    social = "social"


class RoundType(str, Enum):
    first = "first"
    second = "second"
    third = "third"
    hr = "hr"
    written = "written"


class SortBy(str, Enum):
    latest = "latest"
    hot = "hot"
    most_confirmed = "most_confirmed"


class CompanyRef(BaseModel):
    id: str
    name: str
    logo: str


class PositionRef(BaseModel):
    id: str
    name: str


class UploaderRef(BaseModel):
    id: str
    nickname: str
    level: int
    level_icon: str


class QuestionListItem(BaseModel):
    id: str
    type: QuestionType
    content_preview: str
    has_answer: bool
    companies: List[CompanyRef]
    position: PositionRef
    recruit_type: RecruitType
    round: RoundType
    interview_time: Optional[str] = None
    confirm_count: int
    comment_count: int
    favorite_count: int
    is_favorited: Optional[bool] = None
    is_confirmed: Optional[bool] = None
    uploader: UploaderRef
    created_at: datetime


class QuestionDetail(QuestionListItem):
    content: str
    answer: Optional[str] = None
    reward_remaining: float


class QuestionCreateRequest(BaseModel):
    type: QuestionType
    content: str
    answer: Optional[str] = None
    company_ids: List[str]
    position_id: str
    recruit_type: RecruitType
    round: RoundType
    interview_year: Optional[int] = None
    interview_quarter: Optional[int] = None
    leetcode_number: Optional[int] = None
    leetcode_url: Optional[str] = None

    @field_validator("company_ids")
    @classmethod
    def at_least_one_company(cls, v: List[str]) -> List[str]:
        if not v:
            raise ValueError("至少需要关联一个公司")
        return v


class QuestionCreateResponse(BaseModel):
    id: str
    type: QuestionType
    status: str
    exp_gained: int
    message: str


class QuestionListQuery(BaseModel):
    type: Optional[QuestionType] = None
    company_id: Optional[str] = None
    position_id: Optional[str] = None
    recruit_type: Optional[RecruitType] = None
    round: Optional[RoundType] = None
    sort_by: SortBy = SortBy.latest
    keyword: Optional[str] = None
    year: Optional[int] = None
    quarter: Optional[int] = None
    page: int = 1
    page_size: int = 20
