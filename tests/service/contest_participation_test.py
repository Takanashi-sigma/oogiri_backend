import pytest
from fastapi import HTTPException
from unittest.mock import AsyncMock, patch

from app.service.contest_participation_service import (
    participate_contest,
    get_contest_participations,
    get_my_contest_participation,
    update_evaluation_count,
    delete_contest_participation_by_contest_id,
)


@pytest.mark.asyncio
async def test_participate_contest_success():
    db = AsyncMock()

    participation_mock = AsyncMock()

    with patch(
        "app.service.contest_participation_service.get_contest_participation_by_user_and_contest_id",
        new=AsyncMock(return_value=None),
    ), patch(
        "app.service.contest_participation_service.create_contest_participation",
        new=AsyncMock(return_value=participation_mock),
    ) as mock_create:
        result = await participate_contest(db=db, user_id=1, contest_id=10)

    assert result == participation_mock
    mock_create.assert_awaited_once_with(db=db, contest_id=10, user_id=1)


@pytest.mark.asyncio
async def test_participate_contest_already_participated():
    db = AsyncMock()

    existing_participation = AsyncMock()

    with patch(
        "app.service.contest_participation_service.get_contest_participation_by_user_and_contest_id",
        new=AsyncMock(return_value=existing_participation),
    ):
        with pytest.raises(HTTPException) as exc_info:
            await participate_contest(db=db, user_id=1, contest_id=10)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "participation only once"


@pytest.mark.asyncio
async def test_get_contest_participations_success():
    db = AsyncMock()

    participations = [AsyncMock(), AsyncMock()]

    with patch(
        "app.service.contest_participation_service.get_contest_participation_by_contest_id",
        new=AsyncMock(return_value=participations),
    ):
        result = await get_contest_participations(db=db, contest_id=10)

    assert result == participations


@pytest.mark.asyncio
async def test_get_contest_participations_not_found():
    db = AsyncMock()

    with patch(
        "app.service.contest_participation_service.get_contest_participation_by_contest_id",
        new=AsyncMock(return_value=[]),
    ):
        with pytest.raises(HTTPException) as exc_info:
            await get_contest_participations(db=db, contest_id=10)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "contest participtions not found"


@pytest.mark.asyncio
async def test_get_my_contest_participation_success():
    db = AsyncMock()

    participation = AsyncMock()

    with patch(
        "app.service.contest_participation_service.get_contest_participation_by_user_and_contest_id",
        new=AsyncMock(return_value=participation),
    ):
        result = await get_my_contest_participation(db=db, contest_id=10, user_id=1)

    assert result == participation


@pytest.mark.asyncio
async def test_get_my_contest_participation_not_found():
    db = AsyncMock()

    with patch(
        "app.service.contest_participation_service.get_contest_participation_by_user_and_contest_id",
        new=AsyncMock(return_value=None),
    ):
        with pytest.raises(HTTPException) as exc_info:
            await get_my_contest_participation(db=db, contest_id=10, user_id=1)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "not found contest_participation"


@pytest.mark.asyncio
async def test_update_evaluation_count_success():
    db = AsyncMock()

    contest_participation = AsyncMock()
    contest_participation.evaluation_count = 5
    contest_participation.has_submitted_entry = True

    entry = AsyncMock()

    updated_participation = AsyncMock()

    with patch(
        "app.service.contest_participation_service.get_contest_participation_by_user_and_contest_id",
        new=AsyncMock(return_value=contest_participation),
    ), patch(
        "app.service.contest_participation_service.get_entry_by_user_and_contest_id",
        new=AsyncMock(return_value=entry),
    ), patch(
        "app.service.contest_participation_service.update_contest_participation",
        new=AsyncMock(return_value=updated_participation),
    ) as mock_update:
        result = await update_evaluation_count(db=db, user_id=1, contest_id=10)

    assert contest_participation.evaluation_count == 6
    assert result == updated_participation
    mock_update.assert_awaited_once_with(
        db=db,
        contest_participation=contest_participation,
        evaluation_count=6,
        has_submitted_entry=True,
    )


@pytest.mark.asyncio
async def test_update_evaluation_count_contest_participation_not_found():
    db = AsyncMock()

    with patch(
        "app.service.contest_participation_service.get_contest_participation_by_user_and_contest_id",
        new=AsyncMock(return_value=None),
    ):
        with pytest.raises(HTTPException) as exc_info:
            await update_evaluation_count(db=db, user_id=1, contest_id=10)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "contest_participation not found"


@pytest.mark.asyncio
async def test_update_evaluation_count_entry_not_found():
    db = AsyncMock()

    contest_participation = AsyncMock()
    contest_participation.evaluation_count = 5
    contest_participation.has_submitted_entry = True

    with patch(
        "app.service.contest_participation_service.get_contest_participation_by_user_and_contest_id",
        new=AsyncMock(return_value=contest_participation),
    ), patch(
        "app.service.contest_participation_service.get_entry_by_user_and_contest_id",
        new=AsyncMock(return_value=None),
    ):
        with pytest.raises(HTTPException) as exc_info:
            await update_evaluation_count(db=db, user_id=1, contest_id=10)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "entry not found"


@pytest.mark.asyncio
async def test_delete_contest_participation_by_contest_id_success():
    db = AsyncMock()

    contest_participation = AsyncMock()

    with patch(
        "app.service.contest_participation_service.get_contest_participation_by_user_and_contest_id",
        new=AsyncMock(return_value=contest_participation),
    ), patch(
        "app.service.contest_participation_service.delete_contest_participation",
        new=AsyncMock(),
    ) as mock_delete:
        result = await delete_contest_participation_by_contest_id(
            db=db,
            contest_id=10,
            user_id=1,
        )

    assert result is None
    mock_delete.assert_awaited_once_with(db=db, contest=contest_participation)
    db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_contest_participation_by_contest_id_not_found():
    db = AsyncMock()

    with patch(
        "app.service.contest_participation_service.get_contest_participation_by_user_and_contest_id",
        new=AsyncMock(return_value=None),
    ):
        with pytest.raises(HTTPException) as exc_info:
            await delete_contest_participation_by_contest_id(
                db=db,
                contest_id=10,
                user_id=1,
            )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "contest_participation not found"