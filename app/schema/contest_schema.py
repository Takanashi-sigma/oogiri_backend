from pydantic import BaseModel, model_validator, ConfigDict
from datetime import datetime, date
from app.model.contest_model import ContestStatus


class ContestCreate(BaseModel):
    title: str
    prompt: str
    thumbnail_url: str | None
    start_at: date
    end_at: date
    
    @model_validator(mode="after")
    def validate_dates(self):
        if self.start_at > self.end_at:
            raise ValueError("the start_at must be on or before end_at")
        return self

class ContestRead(BaseModel):
    model_config=ConfigDict(from_attributes=True)

    id: int
    title: str
    prompt: str
    thumbnail_url: str | None
    status: ContestStatus
    start_at: date
    end_at: date
    created_at: datetime

class ContestUpdate(BaseModel):
    title: str | None = None
    prompt: str | None = None
    start_at: date | None = None
    end_at: date | None = None
    
    @model_validator(mode="after")
    def validate_dates(self):
        if self.start_at is not None and self.end_at is not None:
            if self.start_at > self.end_at:
                raise ValueError("the start_at must be on or after end_at")

