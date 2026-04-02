from pydantic import BaseModel, model_validator, ConfigDict, Field
from datetime import datetime

class ContestParticipationCreate(BaseModel):
    contest_id: int

class ContestParticipationRead(BaseModel):
    model_config=ConfigDict(from_attributes=True)
    
    id: int
    contest_id: int
    user_id: int
    has_submitted_entry: bool
    evaluation_count: int
    created_at: datetime

class ContestParticipationUpdate(BaseModel):
    has_submitted_entry: bool | None = None
    evaluation_count: int | None = Field(default=None, ge=0)

