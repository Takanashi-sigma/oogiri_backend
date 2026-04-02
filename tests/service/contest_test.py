import pytest
from datetime import date
from fastapi import HTTPException
from unittest.mock import AsyncMock, patch

from app.model.contest_model import ContestStatus
from app.service.contest_service import (
    calculate_contest_status,
    create_contest_with_validation,
    get_contest_by_contest_id,
    update_contest_with_validation,
    list_contests,
    refresh_active_contest_status,
    delete_contest_by_contest_id,
)


def test_calculate_contest_status_draft():
    result = calculate_contest_status(
        start_at=date(2026, 4, 10),
        end_at=date(2026, 4, 20),
        today=date(2026, 4, 1),
    )
    assert result == ContestStatus.draft


def test_calculate_contest_status_open():
    result = calculate_contest_status(
        start_at=date(2026, 4, 1),
        end_at=date(2026, 4, 10),
        today=date(2026, 4, 5),
    )
    assert result == ContestStatus.open


def test_calculate_contest_status_closed():
    result = calculate_contest_status(
        start_at=date(2026, 3, 1),
        end_at=date(2026, 3, 10),
        today=date(2026, 4, 1),
    )
    assert result == ContestStatus.closed


@pytest.mark.asyncio
async def test_create_contest_with_validation_success():
    db = AsyncMock()
    contest_mock = AsyncMock()

    with patch(
        "app.service.contest_service.calculate_contest_status",
        return_value=ContestStatus.draft,
    ) as mock_calc, patch(
        "app.service.contest_service.create_contest",
        new=AsyncMock(return_value=contest_mock),
    ) as mock_create:
        result = await create_contest_with_validation(
            db=db,
            title="test title",
            prompt="test prompt",
            start_at=date(2026, 4, 10),
            end_at=date(2026, 4, 20),
            thumbnail_url="https://example.com/image.png",
        )

    assert result == contest_mock
    mock_calc.assert_called_once_with(
        start_at=date(2026, 4, 10),
        end_at=date(2026, 4, 20),
    )
    mock_create.assert_awaited_once_with(
        db,
        title="test title",
        status=ContestStatus.draft,
        prompt="test prompt",
        start_at=date(2026, 4, 10),
        end_at=date(2026, 4, 20),
        thumbnail_url="https://example.com/image.png",
    )


@pytest.mark.asyncio
async def test_create_contest_with_validation_invalid_date():
    db = AsyncMock()

    with pytest.raises(HTTPException) as exc_info:
        await create_contest_with_validation(
            db=db,
            title="test title",
            prompt="test prompt",
            start_at=date(2026, 4, 20),
            end_at=date(2026, 4, 10),
            thumbnail_url="https://example.com/image.png",
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "start_at must be before end_at"


@pytest.mark.asyncio
async def test_get_contest_by_contest_id_success():
    db = AsyncMock()
    contest_mock = AsyncMock()

    with patch(
        "app.service.contest_service.get_contest_by_id",
        new=AsyncMock(return_value=contest_mock),
    ) as mock_get:
        result = await get_contest_by_contest_id(db=db, contest_id=1)

    assert result == contest_mock
    mock_get.assert_awaited_once_with(db=db, contest_id=1)


@pytest.mark.asyncio
async def test_get_contest_by_contest_id_not_found():
    db = AsyncMock()

    with patch(
        "app.service.contest_service.get_contest_by_id",
        new=AsyncMock(return_value=None),
    ):
        with pytest.raises(HTTPException) as exc_info:
            await get_contest_by_contest_id(db=db, contest_id=1)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "contest not found"


@pytest.mark.asyncio
async def test_update_contest_with_validation_success():
    db = AsyncMock()

    contest_mock = AsyncMock()
    contest_mock.start_at = date(2026, 4, 10)
    contest_mock.end_at = date(2026, 4, 20)

    updated_contest = AsyncMock()

    with patch(
        "app.service.contest_service.get_contest_by_id",
        new=AsyncMock(return_value=contest_mock),
    ) as mock_get, patch(
        "app.service.contest_service.calculate_contest_status",
        return_value=ContestStatus.open,
    ) as mock_calc, patch(
        "app.service.contest_service.update_contest",
        new=AsyncMock(return_value=updated_contest),
    ) as mock_update:
        result = await update_contest_with_validation(
            db=db,
            contest_id=1,
            title="new title",
            prompt="new prompt",
            start_at=date(2026, 4, 11),
            end_at=date(2026, 4, 21),
        )

    assert result == updated_contest
    mock_get.assert_awaited_once_with(db=db, contest_id=1)
    mock_calc.assert_called_once_with(
        start_at=date(2026, 4, 11),
        end_at=date(2026, 4, 21),
    )
    mock_update.assert_awaited_once_with(
        db=db,
        contest=contest_mock,
        title="new title",
        prompt="new prompt",
        status=ContestStatus.open,
        start_at=date(2026, 4, 11),
        end_at=date(2026, 4, 21),
    )


@pytest.mark.asyncio
async def test_update_contest_with_validation_not_found():
    db = AsyncMock()

    with patch(
        "app.service.contest_service.get_contest_by_id",
        new=AsyncMock(return_value=None),
    ):
        with pytest.raises(HTTPException) as exc_info:
            await update_contest_with_validation(
                db=db,
                contest_id=1,
                title="new title",
                prompt="new prompt",
                start_at=date(2026, 4, 11),
                end_at=date(2026, 4, 21),
            )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "contest not found"


@pytest.mark.asyncio
async def test_update_contest_with_validation_invalid_date():
    db = AsyncMock()

    contest_mock = AsyncMock()
    contest_mock.start_at = date(2026, 4, 10)
    contest_mock.end_at = date(2026, 4, 20)

    with patch(
        "app.service.contest_service.get_contest_by_id",
        new=AsyncMock(return_value=contest_mock),
    ):
        with pytest.raises(HTTPException) as exc_info:
            await update_contest_with_validation(
                db=db,
                contest_id=1,
                start_at=date(2026, 4, 25),
                end_at=date(2026, 4, 20),
            )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "start_at must be on or before end_at"


@pytest.mark.asyncio
async def test_update_contest_with_validation_partial_update():
    db = AsyncMock()

    contest_mock = AsyncMock()
    contest_mock.start_at = date(2026, 4, 10)
    contest_mock.end_at = date(2026, 4, 20)

    updated_contest = AsyncMock()

    with patch(
        "app.service.contest_service.get_contest_by_id",
        new=AsyncMock(return_value=contest_mock),
    ), patch(
        "app.service.contest_service.calculate_contest_status",
        return_value=ContestStatus.open,
    ) as mock_calc, patch(
        "app.service.contest_service.update_contest",
        new=AsyncMock(return_value=updated_contest),
    ) as mock_update:
        result = await update_contest_with_validation(
            db=db,
            contest_id=1,
            title="title only changed",
            prompt=None,
            start_at=None,
            end_at=None,
        )

    assert result == updated_contest
    mock_calc.assert_called_once_with(
        start_at=date(2026, 4, 10),
        end_at=date(2026, 4, 20),
    )
    mock_update.assert_awaited_once_with(
        db=db,
        contest=contest_mock,
        title="title only changed",
        prompt=None,
        status=ContestStatus.open,
        start_at=date(2026, 4, 10),
        end_at=date(2026, 4, 20),
    )


@pytest.mark.asyncio
async def test_list_contests():
    db = AsyncMock()
    contests = [AsyncMock(), AsyncMock()]

    with patch(
        "app.service.contest_service.get_contests",
        new=AsyncMock(return_value=contests),
    ) as mock_get:
        result = await list_contests(db=db)

    assert result == contests
    mock_get.assert_awaited_once_with(db=db)


@pytest.mark.asyncio
async def test_refresh_active_contest_status_updates_changed_contests():
    db = AsyncMock()

    contest1 = AsyncMock()
    contest1.start_at = date(2026, 4, 10)
    contest1.end_at = date(2026, 4, 20)
    contest1.status = ContestStatus.draft

    contest2 = AsyncMock()
    contest2.start_at = date(2026, 3, 1)
    contest2.end_at = date(2026, 3, 10)
    contest2.status = ContestStatus.open

    contests = [contest1, contest2]

    with patch(
        "app.service.contest_service.get_contests_of_draft_or_open",
        new=AsyncMock(return_value=contests),
    ), patch(
        "app.service.contest_service.calculate_contest_status",
        side_effect=[ContestStatus.open, ContestStatus.closed],
    ):
        result = await refresh_active_contest_status(db=db)

    assert result == [contest1, contest2]
    assert contest1.status == ContestStatus.open
    assert contest2.status == ContestStatus.closed
    db.commit.assert_awaited_once()
    assert db.refresh.await_count == 2
    db.refresh.assert_any_await(contest1)
    db.refresh.assert_any_await(contest2)


@pytest.mark.asyncio
async def test_refresh_active_contest_status_no_changes():
    db = AsyncMock()

    contest1 = AsyncMock()
    contest1.start_at = date(2026, 4, 1)
    contest1.end_at = date(2026, 4, 10)
    contest1.status = ContestStatus.open

    contests = [contest1]

    with patch(
        "app.service.contest_service.get_contests_of_draft_or_open",
        new=AsyncMock(return_value=contests),
    ), patch(
        "app.service.contest_service.calculate_contest_status",
        return_value=ContestStatus.open,
    ):
        result = await refresh_active_contest_status(db=db)

    assert result == []
    db.commit.assert_not_awaited()
    db.refresh.assert_not_awaited()


@pytest.mark.asyncio
async def test_delete_contest_by_contest_id_success():
    db = AsyncMock()
    contest_mock = AsyncMock()

    with patch(
        "app.service.contest_service.get_contest_by_id",
        new=AsyncMock(return_value=contest_mock),
    ), patch(
        "app.service.contest_service.delete_contest",
        new=AsyncMock(),
    ) as mock_delete:
        result = await delete_contest_by_contest_id(db=db, contest_id=1)

    assert result is None
    mock_delete.assert_awaited_once_with(db=db, contest=contest_mock)
    db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_contest_by_contest_id_not_found():
    db = AsyncMock()

    with patch(
        "app.service.contest_service.get_contest_by_id",
        new=AsyncMock(return_value=None),
    ):
        with pytest.raises(HTTPException) as exc_info:
            await delete_contest_by_contest_id(db=db, contest_id=1)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "contest not found"