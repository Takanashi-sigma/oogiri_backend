import pytest
from unittest.mock import AsyncMock, patch

from app.service.comparison_service import create_comparison_service


@pytest.mark.asyncio
async def test_create_comparison_success():
    db = AsyncMock()

    # ===== ダミーデータ =====
    entry_a = AsyncMock()
    entry_a.id = 1
    entry_a.user_id = 10
    entry_a.contest_id = 100
    entry_a.rating = 1500
    entry_a.rd = 350
    entry_a.volatility = 0.06
    entry_a.comparisons_count = 0
    entry_a.wins = 0
    entry_a.losses = 0

    entry_b = AsyncMock()
    entry_b.id = 2
    entry_b.user_id = 20
    entry_b.contest_id = 100
    entry_b.rating = 1500
    entry_b.rd = 350
    entry_b.volatility = 0.06
    entry_b.comparisons_count = 0
    entry_b.wins = 0
    entry_b.losses = 0

    participation = AsyncMock()
    participation.user_id = 99

    rating_result = {
        "a_rating": 1600,
        "b_rating": 1400,
        "a_rd": 300,
        "b_rd": 300,
        "a_volatility": 0.05,
        "b_volatility": 0.05,
    }

    comparison_mock = AsyncMock()

    with patch("app.service.comparison_service.validate_comparison_inputs",
               return_value=(entry_a, entry_b, participation)), \
         patch("app.service.comparison_service.rate_1vs1",
               return_value=rating_result), \
         patch("app.service.comparison_service.create_comparison",
               return_value=comparison_mock), \
         patch("app.service.comparison_service.update_rating_status") as mock_update_rating, \
         patch("app.service.comparison_service.update_evaluation_count") as mock_update_eval:

        result = await create_comparison_service(
            db=db,
            contest_id=100,
            voter_user_id=99,
            entry_a_id=1,
            entry_b_id=2,
            chosen_entry_id=1
        )

    # ===== 検証 =====
    assert result == comparison_mock

    # rating更新が2回呼ばれてる
    assert mock_update_rating.call_count == 2

    # evaluation_count更新
    mock_update_eval.assert_called_once()

    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(comparison_mock)