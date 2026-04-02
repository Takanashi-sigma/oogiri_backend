from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.core.database import get_db
from app.service.entry_service import entry_contest, get_comparison_candidates, get_my_entries, get_specific_entry, update_entry_content, get_ranking, delete_my_entry, get_specific_entry, get_rank_list, get_my_ranking, get_entry
from app.schema.entry_schema import EntryRead, EntryCreate, EntryUpdate, RankingListRead, MyRankingRead
from app.model.user_model import User

router = APIRouter(prefix="/entries", tags=["entries"])

@router.post("")
async def participate_contest(data: EntryCreate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await entry_contest(db=db, contest_id=data.contest_id, user_id=user.id, content=data.content)
    return result


@router.get("/{contest_id}/opponents", response_model=list[EntryRead])
async def get_opponents(contest_id: int, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await get_comparison_candidates(db=db, contest_id=contest_id, user_id=user.id)
    return result

@router.get("/me", response_model=list[EntryRead])
async def list_my_entries(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await get_my_entries(db=db, user_id=user.id)
    return result

@router.get("/{entry_id}", response_model=EntryRead)
async def get_detail_entry(entry_id: int, db: AsyncSession = Depends(get_db)):
    result = await get_entry(db=db, entry_id=entry_id)
    return result

@router.patch("/{entry_id}", response_model=EntryRead)
async def update_entry_content_in_draft(contest_id: int, entry_id: int, content: EntryUpdate, user: User = Depends(get_current_user), db: AsyncSession=Depends(get_db)):
    result = await update_entry_content(db=db, contest_id=contest_id, entry_id=entry_id, new_content=content, user_id=user.id)
    return result

@router.delete("/me/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_entry_api(entry_id: int, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await delete_my_entry(db=db, entry_id=entry_id, user_id=user.id)

@router.get("/me/{contest_id}", response_model=EntryRead)
async def get_my_entry(contest_id: int, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await get_specific_entry(db=db, user_id=user.id, contest_id=contest_id)
    return result

@router.get("/{contest_id}/ranking", response_model=RankingListRead)
async def get_ranking(contest_id: int, offset: int = Query(0,ge=0), limit: int = Query(9, ge=1, le=50), db: AsyncSession = Depends(get_db)):
    return await get_rank_list(db=db, contest_id=contest_id, offset=offset, limit=limit)

@router.get("/{contest_id}/ranking/me", response_model=MyRankingRead)
async def get_my_ranking_by_contest_id(contest_id: int, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await get_my_ranking(db=db, contest_id=contest_id, user_id=user.id)
