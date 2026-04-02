from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.service.comparison_service import create_comparison_service, get_comparison_by_entry_id, get_comparisons_by_contest_id
from app.schema.comparison_schema import ComparisonRead, ComparisonCreate
from app.model.user_model import User

router = APIRouter(prefix="/comparisons", tags=["comparisons"])

@router.post("", response_model=ComparisonRead)
async def compare_opponents(data: ComparisonCreate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await create_comparison_service(db=db, contest_id=data.contest_id, entry_a_id=data.entry_a_id, entry_b_id=data.entry_b_id, chosen_entry_id=data.chosen_entry_id, voter_user_id=user.id)
    return result

@router.get("/{contest_id}", response_model=list[ComparisonRead])
async def list_comparisons(contest_id: int, db: AsyncSession = Depends(get_db)):
    result = await get_comparisons_by_contest_id(db=db, contest_id=contest_id)
    return result

@router.get("/{entry_id}", response_model=list[ComparisonRead])
async def list_comparison_by_entry_id(entry_id: int, db: AsyncSession = Depends(get_db)):
    result = await get_comparison_by_entry_id(db=db, entry_id=entry_id)
    return result

