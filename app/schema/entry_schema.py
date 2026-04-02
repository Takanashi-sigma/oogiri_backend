from pydantic import BaseModel, model_validator, ConfigDict, Field
from datetime import datetime

class EntryCreate(BaseModel):
    contest_id: int
    content: str

class EntryRead(BaseModel):
    model_config=ConfigDict(from_attributes=True)

    id: int
    contest_id: int
    user_id: int
    content: str
    rating: float
    rd: float
    volatility: float
    comparisons_count: int
    wins: int
    losses: int
    created_at: datetime

class EntryUpdate(BaseModel):
    content: str | None = None

class RankingItemRead(BaseModel):
    rank: int
    entry_id: int
    content: str
    rating: float

class RankingListRead(BaseModel):
    items: list[RankingItemRead]
    has_more: bool

class MyRankingRead(BaseModel):
    rank: int
    entry_id: int
    content: str
    rating: float
