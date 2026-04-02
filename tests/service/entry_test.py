import pytest
from fastapi import HTTPException
from unittest.mock import AsyncMock, patch

from app.model.contest_model import ContestStatus
from app.model.entry_model import Entry
from app.service.entry_service import (
    can_join_ranking,
    entry_contest,
    get_my_entries,
    list_entry_by_contest_id,
    get_ranking,
    get_entry,
    get_rank_list,
    get_my_ranking,
    get_specific_entry,
    get_comparison_candidates,
    update_rating_status,
    update_entry_content,
    delete_my_entry,
)


def test_can_join_ranking_true():
    participation = AsyncMock()
    participation.has_submitted_entry = True
    participation.evaluation_count = 50

    assert can_join_ranking(participation) is True


def test_can_join_ranking_false():
    participation = AsyncMock()
    participation.has_submitted_entry = True
    participation.evaluation_count = 49

    assert can_join_ranking(participation) is False


@pytest.mark.asyncio
async def test_entry_contest_success():
    db = AsyncMock()

    participation = AsyncMock()
    participation.has_submitted_entry = False

    contest = AsyncMock()
    contest.status.value = "draft"

    created_entry = AsyncMock()
    created_entry.id = 1
    created_entry.contest_id = 10
    created_entry.user_id = 100
    created_entry.content = "テスト回答"
    created_entry.rating = 1500.0
    created_entry.rd = 350.0
    created_entry.volatility = 0.06
    created_entry.comparisons_count = 0
    created_entry.wins = 0
    created_entry.losses = 0
    created_entry.created_at = "2026-04-01T00:00:00"

    with patch(
        "app.service.entry_service.get_entry_by_user_and_contest_id",
        new=AsyncMock(return_value=None),
    ), patch(
        "app.service.entry_service.create_contest_participation",
        new=AsyncMock(),
    ), patch(
        "app.service.entry_service.get_contest_participation_by_user_and_contest_id",
        new=AsyncMock(return_value=participation),
    ), patch(
        "app.service.entry_service.get_contest_by_id",
        new=AsyncMock(return_value=contest),
    ), patch(
        "app.service.entry_service.create_entry",
        new=AsyncMock(return_value=created_entry),
    ):
        result = await entry_contest(
            db=db,
            contest_id=10,
            user_id=100,
            content="テスト回答",
        )

    assert result["id"] == 1
    assert result["contest_id"] == 10
    assert result["user_id"] == 100
    assert result["content"] == "テスト回答"
    assert result["contest_status"] == "draft"
    assert participation.has_submitted_entry is True
    db.commit.assert_awaited_once()
    db.refresh.assert_awaited_once_with(participation)


@pytest.mark.asyncio
async def test_entry_contest_already_entered():
    db = AsyncMock()

    with patch(
        "app.service.entry_service.get_entry_by_user_and_contest_id",
        new=AsyncMock(return_value=AsyncMock()),
    ):
        with pytest.raises(HTTPException) as exc_info:
            await entry_contest(db=db, contest_id=10, user_id=100, content="test")

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "participation is only once"


@pytest.mark.asyncio
async def test_entry_contest_participation_not_found():
    db = AsyncMock()

    with patch(
        "app.service.entry_service.get_entry_by_user_and_contest_id",
        new=AsyncMock(return_value=None),
    ), patch(
        "app.service.entry_service.create_contest_participation",
        new=AsyncMock(),
    ), patch(
        "app.service.entry_service.get_contest_participation_by_user_and_contest_id",
        new=AsyncMock(return_value=None),
    ):
        with pytest.raises(HTTPException) as exc_info:
            await entry_contest(db=db, contest_id=10, user_id=100, content="test")

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "contest participation not found"


@pytest.mark.asyncio
async def test_entry_contest_contest_not_found():
    db = AsyncMock()
    participation = AsyncMock()

    with patch(
        "app.service.entry_service.get_entry_by_user_and_contest_id",
        new=AsyncMock(return_value=None),
    ), patch(
        "app.service.entry_service.create_contest_participation",
        new=AsyncMock(),
    ), patch(
        "app.service.entry_service.get_contest_participation_by_user_and_contest_id",
        new=AsyncMock(return_value=participation),
    ), patch(
        "app.service.entry_service.get_contest_by_id",
        new=AsyncMock(return_value=None),
    ):
        with pytest.raises(HTTPException) as exc_info:
            await entry_contest(db=db, contest_id=10, user_id=100, content="test")

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "contest not found"


@pytest.mark.asyncio
async def test_entry_contest_create_entry_fail():
    db = AsyncMock()
    participation = AsyncMock()
    contest = AsyncMock()

    with patch(
        "app.service.entry_service.get_entry_by_user_and_contest_id",
        new=AsyncMock(return_value=None),
    ), patch(
        "app.service.entry_service.create_contest_participation",
        new=AsyncMock(),
    ), patch(
        "app.service.entry_service.get_contest_participation_by_user_and_contest_id",
        new=AsyncMock(return_value=participation),
    ), patch(
        "app.service.entry_service.get_contest_by_id",
        new=AsyncMock(return_value=contest),
    ), patch(
        "app.service.entry_service.create_entry",
        new=AsyncMock(side_effect=Exception("db error")),
    ):
        with pytest.raises(HTTPException) as exc_info:
            await entry_contest(db=db, contest_id=10, user_id=100, content="test")

    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == "fail"
    db.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_my_entries_success():
    db = AsyncMock()
    entries = [AsyncMock(), AsyncMock()]

    with patch(
        "app.service.entry_service.get_entry_by_user_id",
        new=AsyncMock(return_value=entries),
    ):
        result = await get_my_entries(db=db, user_id=1)

    assert result == entries


@pytest.mark.asyncio
async def test_get_my_entries_not_found():
    db = AsyncMock()

    with patch(
        "app.service.entry_service.get_entry_by_user_id",
        new=AsyncMock(return_value=[]),
    ):
        with pytest.raises(HTTPException) as exc_info:
            await get_my_entries(db=db, user_id=1)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "entry not found"


@pytest.mark.asyncio
async def test_list_entry_by_contest_id_success():
    db = AsyncMock()
    entries = [AsyncMock()]

    with patch(
        "app.service.entry_service.get_entry_by_contest_id",
        new=AsyncMock(return_value=entries),
    ):
        result = await list_entry_by_contest_id(db=db, contest_id=10)

    assert result == entries


@pytest.mark.asyncio
async def test_list_entry_by_contest_id_not_found():
    db = AsyncMock()

    with patch(
        "app.service.entry_service.get_entry_by_contest_id",
        new=AsyncMock(return_value=[]),
    ):
        with pytest.raises(HTTPException) as exc_info:
            await list_entry_by_contest_id(db=db, contest_id=10)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "entry not found"


@pytest.mark.asyncio
async def test_get_ranking_success():
    db = AsyncMock()
    ranking = [AsyncMock()]

    with patch(
        "app.service.entry_service.get_ranking_entries",
        new=AsyncMock(return_value=ranking),
    ):
        result = await get_ranking(db=db, contest_id=10, offset=0, limit=10)

    assert result == ranking


@pytest.mark.asyncio
async def test_get_ranking_not_found():
    db = AsyncMock()

    with patch(
        "app.service.entry_service.get_ranking_entries",
        new=AsyncMock(return_value=[]),
    ):
        with pytest.raises(HTTPException) as exc_info:
            await get_ranking(db=db, contest_id=10, offset=0, limit=10)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "ranking not found"


@pytest.mark.asyncio
async def test_get_entry_success():
    db = AsyncMock()
    entry = AsyncMock()

    with patch(
        "app.service.entry_service.get_entry_by_entry_id",
        new=AsyncMock(return_value=entry),
    ):
        result = await get_entry(db=db, entry_id=1)

    assert result == entry


@pytest.mark.asyncio
async def test_get_entry_not_found():
    db = AsyncMock()

    with patch(
        "app.service.entry_service.get_entry_by_entry_id",
        new=AsyncMock(return_value=None),
    ):
        with pytest.raises(HTTPException) as exc_info:
            await get_entry(db=db, entry_id=1)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "entry not found"


@pytest.mark.asyncio
async def test_get_rank_list_success():
    db = AsyncMock()

    entry1 = AsyncMock()
    entry1.id = 1
    entry1.content = "a"
    entry1.rating = 1600

    entry2 = AsyncMock()
    entry2.id = 2
    entry2.content = "b"
    entry2.rating = 1500

    with patch(
        "app.service.entry_service.get_ranking_entries",
        new=AsyncMock(return_value=[entry1, entry2]),
    ), patch(
        "app.service.entry_service.count_entries_by_contest_id",
        new=AsyncMock(return_value=5),
    ):
        result = await get_rank_list(db=db, contest_id=10, offset=0, limit=2)

    assert result == {
        "items": [
            {"rank": 1, "entry_id": 1, "content": "a", "rating": 1600},
            {"rank": 2, "entry_id": 2, "content": "b", "rating": 1500},
        ],
        "has_more": True,
    }


@pytest.mark.asyncio
async def test_get_rank_list_no_more():
    db = AsyncMock()

    entry1 = AsyncMock()
    entry1.id = 1
    entry1.content = "a"
    entry1.rating = 1600

    with patch(
        "app.service.entry_service.get_ranking_entries",
        new=AsyncMock(return_value=[entry1]),
    ), patch(
        "app.service.entry_service.count_entries_by_contest_id",
        new=AsyncMock(return_value=1),
    ):
        result = await get_rank_list(db=db, contest_id=10, offset=0, limit=10)

    assert result["has_more"] is False


@pytest.mark.asyncio
async def test_get_my_ranking_success():
    db = AsyncMock()

    my_entry = AsyncMock()
    my_entry.id = 1
    my_entry.content = "my answer"
    my_entry.rating = 1550

    with patch(
        "app.service.entry_service.get_entry_by_user_and_contest_id",
        new=AsyncMock(return_value=my_entry),
    ), patch(
        "app.service.entry_service.count_entries_above_me",
        new=AsyncMock(return_value=3),
    ):
        result = await get_my_ranking(db=db, contest_id=10, user_id=100)

    assert result == {
        "rank": 4,
        "entry_id": 1,
        "content": "my answer",
        "rating": 1550,
    }


@pytest.mark.asyncio
async def test_get_my_ranking_not_found():
    db = AsyncMock()

    with patch(
        "app.service.entry_service.get_entry_by_user_and_contest_id",
        new=AsyncMock(return_value=None),
    ):
        with pytest.raises(HTTPException) as exc_info:
            await get_my_ranking(db=db, contest_id=10, user_id=100)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "entry not found"


@pytest.mark.asyncio
async def test_get_specific_entry_success():
    db = AsyncMock()
    entry = AsyncMock()

    with patch(
        "app.service.entry_service.get_entry_by_user_and_contest_id",
        new=AsyncMock(return_value=entry),
    ):
        result = await get_specific_entry(db=db, user_id=1, contest_id=10)

    assert result == entry


@pytest.mark.asyncio
async def test_get_specific_entry_not_found():
    db = AsyncMock()

    with patch(
        "app.service.entry_service.get_entry_by_user_and_contest_id",
        new=AsyncMock(return_value=None),
    ):
        with pytest.raises(HTTPException) as exc_info:
            await get_specific_entry(db=db, user_id=1, contest_id=10)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "entry not found"


@pytest.mark.asyncio
async def test_get_comparison_candidates_success():
    db = AsyncMock()
    entries = [AsyncMock(), AsyncMock()]

    with patch(
        "app.service.entry_service.get_random_two_entries_excluding_user",
        new=AsyncMock(return_value=entries),
    ):
        result = await get_comparison_candidates(db=db, contest_id=10, user_id=1)

    assert result == entries


@pytest.mark.asyncio
async def test_get_comparison_candidates_not_enough():
    db = AsyncMock()

    with patch(
        "app.service.entry_service.get_random_two_entries_excluding_user",
        new=AsyncMock(return_value=[AsyncMock()]),
    ):
        with pytest.raises(HTTPException) as exc_info:
            await get_comparison_candidates(db=db, contest_id=10, user_id=1)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "entries must be two comparisons"


@pytest.mark.asyncio
async def test_update_rating_status_success():
    db = AsyncMock()

    entry = AsyncMock(spec=Entry)

    updated_entry = AsyncMock()

    db.get = AsyncMock(return_value=entry)

    with patch(
        "app.service.entry_service.update_entry",
        new=AsyncMock(return_value=updated_entry),
    ) as mock_update:
        result = await update_rating_status(
            db=db,
            entry_id=1,
            rating=1600,
            rd=300,
            volatility=0.05,
            comparisons_count=5,
            wins=3,
            losses=2,
        )

    assert result == updated_entry
    db.get.assert_awaited_once_with(Entry, 1)
    mock_update.assert_awaited_once_with(
        db=db,
        entry=entry,
        rating=1600,
        rd=300,
        volatility=0.05,
        comparisons_count=5,
        wins=3,
        losses=2,
    )


@pytest.mark.asyncio
async def test_update_rating_status_not_found():
    db = AsyncMock()
    db.get = AsyncMock(return_value=None)

    with pytest.raises(HTTPException) as exc_info:
        await update_rating_status(
            db=db,
            entry_id=1,
            rating=1600,
            rd=300,
            volatility=0.05,
            comparisons_count=5,
            wins=3,
            losses=2,
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "entry not found"


@pytest.mark.asyncio
async def test_update_entry_content_success():
    db = AsyncMock()

    contest = AsyncMock()
    contest.status = ContestStatus.draft

    entry = AsyncMock()
    entry.user_id = 100

    updated_entry = AsyncMock()

    with patch(
        "app.service.entry_service.get_contest_by_id",
        new=AsyncMock(return_value=contest),
    ), patch(
        "app.service.entry_service.get_entry_by_entry_id",
        new=AsyncMock(return_value=entry),
    ), patch(
        "app.service.entry_service.update_entry",
        new=AsyncMock(return_value=updated_entry),
    ) as mock_update:
        result = await update_entry_content(
            db=db,
            user_id=100,
            contest_id=10,
            entry_id=1,
            new_content="new text",
        )

    assert result == updated_entry
    mock_update.assert_awaited_once_with(db=db, entry=entry, content="new text")


@pytest.mark.asyncio
async def test_update_entry_content_entry_not_found():
    db = AsyncMock()
    contest = AsyncMock()
    contest.status = ContestStatus.draft

    with patch(
        "app.service.entry_service.get_contest_by_id",
        new=AsyncMock(return_value=contest),
    ), patch(
        "app.service.entry_service.get_entry_by_entry_id",
        new=AsyncMock(return_value=None),
    ):
        with pytest.raises(HTTPException) as exc_info:
            await update_entry_content(
                db=db,
                user_id=100,
                contest_id=10,
                entry_id=1,
                new_content="new text",
            )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "entry not_found"


@pytest.mark.asyncio
async def test_update_entry_content_contest_not_found():
    db = AsyncMock()
    entry = AsyncMock()
    entry.user_id = 100

    with patch(
        "app.service.entry_service.get_contest_by_id",
        new=AsyncMock(return_value=None),
    ), patch(
        "app.service.entry_service.get_entry_by_entry_id",
        new=AsyncMock(return_value=entry),
    ):
        with pytest.raises(HTTPException) as exc_info:
            await update_entry_content(
                db=db,
                user_id=100,
                contest_id=10,
                entry_id=1,
                new_content="new text",
            )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "contest not found"


@pytest.mark.asyncio
async def test_update_entry_content_contest_started():
    db = AsyncMock()

    contest = AsyncMock()
    contest.status = ContestStatus.open

    entry = AsyncMock()
    entry.user_id = 100

    with patch(
        "app.service.entry_service.get_contest_by_id",
        new=AsyncMock(return_value=contest),
    ), patch(
        "app.service.entry_service.get_entry_by_entry_id",
        new=AsyncMock(return_value=entry),
    ):
        with pytest.raises(HTTPException) as exc_info:
            await update_entry_content(
                db=db,
                user_id=100,
                contest_id=10,
                entry_id=1,
                new_content="new text",
            )

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "this contest has alredy started"


@pytest.mark.asyncio
async def test_update_entry_content_other_user_entry():
    db = AsyncMock()

    contest = AsyncMock()
    contest.status = ContestStatus.draft

    entry = AsyncMock()
    entry.user_id = 999

    with patch(
        "app.service.entry_service.get_contest_by_id",
        new=AsyncMock(return_value=contest),
    ), patch(
        "app.service.entry_service.get_entry_by_entry_id",
        new=AsyncMock(return_value=entry),
    ):
        with pytest.raises(HTTPException) as exc_info:
            await update_entry_content(
                db=db,
                user_id=100,
                contest_id=10,
                entry_id=1,
                new_content="new text",
            )

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "cannot update others entry"


@pytest.mark.asyncio
async def test_delete_my_entry_success():
    db = AsyncMock()

    entry = AsyncMock()
    entry.user_id = 100
    entry.contest_id = 10

    participation = AsyncMock()

    with patch(
        "app.service.entry_service.get_entry_by_entry_id",
        new=AsyncMock(return_value=entry),
    ), patch(
        "app.service.entry_service.get_contest_participation_by_user_and_contest_id",
        new=AsyncMock(return_value=participation),
    ), patch(
        "app.service.entry_service.delete_contest_participation",
        new=AsyncMock(),
    ) as mock_delete_participation, patch(
        "app.service.entry_service.delete_entry",
        new=AsyncMock(),
    ) as mock_delete_entry:
        result = await delete_my_entry(db=db, entry_id=1, user_id=100)

    assert result is None
    mock_delete_participation.assert_awaited_once_with(
        db=db,
        contest_participation=participation,
    )
    mock_delete_entry.assert_awaited_once_with(db=db, entry=entry)
    db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_my_entry_entry_not_found():
    db = AsyncMock()

    with patch(
        "app.service.entry_service.get_entry_by_entry_id",
        new=AsyncMock(return_value=None),
    ):
        with pytest.raises(HTTPException) as exc_info:
            await delete_my_entry(db=db, entry_id=1, user_id=100)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "entry not found"


@pytest.mark.asyncio
async def test_delete_my_entry_other_user_entry():
    db = AsyncMock()

    entry = AsyncMock()
    entry.user_id = 999
    entry.contest_id = 10

    participation = AsyncMock()

    with patch(
        "app.service.entry_service.get_entry_by_entry_id",
        new=AsyncMock(return_value=entry),
    ), patch(
        "app.service.entry_service.get_contest_participation_by_user_and_contest_id",
        new=AsyncMock(return_value=participation),
    ):
        with pytest.raises(HTTPException) as exc_info:
            await delete_my_entry(db=db, entry_id=1, user_id=100)

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "you cant delete this entry"
