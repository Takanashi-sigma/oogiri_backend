from pydantic import BaseModel, model_validator, ConfigDict
from datetime import datetime

class ComparisonCreate(BaseModel):
    contest_id: int
    entry_a_id: int
    entry_b_id: int
    chosen_entry_id: int
    @model_validator(mode="after")
    def validate_entries(self):
        if self.entry_a_id == self.entry_b_id:
            raise ValueError("entry_a and entry_b must be different")
        if self.chosen_entry_id not in (self.entry_a_id, self.entry_b_id):
            raise ValueError("chosen_entry must be either entry_a_id or entry_b_id")
        return self

class ComparisonRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    contest_id: int
    voter_user_id: int
    entry_a_id: int
    entry_b_id: int
    chosen_entry_id: int
    entry_a_rating_before: float
    entry_b_rating_before: float
    entry_a_rd_before: float
    entry_b_rd_before: float
    entry_a_volatility_before: float
    entry_b_volatility_before: float
    entry_a_rating_after: float
    entry_b_rating_after: float
    entry_a_rd_after: float
    entry_b_rd_after: float
    entry_a_volatility_after: float
    entry_b_volatility_after: float
    created_at: datetime