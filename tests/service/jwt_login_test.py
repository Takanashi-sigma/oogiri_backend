import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

from app.service.jwt_login_service import (
    _decode_refresh_inline,
    issue_tokens,
    refresh_tokens,
)


@pytest.mark.asyncio
async def test_decode_refresh_inline():
    fake_payload = {"sub": "1", "jti": "abc", "exp": 2000000000}

    with patch(
        "app.core.security.decode_refresh",
        return_value=fake_payload,
    ) as mock_decode:
        result = await _decode_refresh_inline("refresh_token_value")

    assert result == fake_payload
    mock_decode.assert_called_once_with("refresh_token_value")


@pytest.mark.asyncio
async def test_issue_tokens_success():
    db = AsyncMock()

    fake_access = "access_token_123"
    fake_refresh = "refresh_token_123"
    fake_jti = "jti_123"
    fake_payload = {
        "sub": "1",
        "jti": fake_jti,
        "exp": 2000000000,
    }

    with patch(
        "app.service.jwt_login_service.create_access_token",
        return_value=fake_access,
    ) as mock_create_access, patch(
        "app.service.jwt_login_service.new_jti",
        return_value=fake_jti,
    ) as mock_new_jti, patch(
        "app.service.jwt_login_service.create_refresh_token",
        return_value=fake_refresh,
    ) as mock_create_refresh, patch(
        "app.service.jwt_login_service._decode_refresh_inline",
        new=AsyncMock(return_value=fake_payload),
    ) as mock_decode_refresh, patch(
        "app.service.jwt_login_service.store_refresh_token",
        new=AsyncMock(),
    ) as mock_store:
        access, refresh = await issue_tokens(db=db, user_id=1)

    expected_exp = datetime.fromtimestamp(fake_payload["exp"], tz=timezone.utc)

    assert access == fake_access
    assert refresh == fake_refresh

    mock_create_access.assert_called_once_with(1)
    mock_new_jti.assert_called_once()
    mock_create_refresh.assert_called_once_with(1, fake_jti)
    mock_decode_refresh.assert_awaited_once_with(fake_refresh)
    mock_store.assert_awaited_once_with(
        db,
        1,
        fake_jti,
        fake_refresh,
        expected_exp,
    )


@pytest.mark.asyncio
async def test_refresh_tokens_decode_error():
    db = AsyncMock()

    def fake_decode(_token: str):
        raise Exception("invalid token")

    result = await refresh_tokens(
        db=db,
        refresh_token="bad_token",
        decode_refresh_fn=fake_decode,
    )

    assert result is None


@pytest.mark.asyncio
async def test_refresh_tokens_jti_missing():
    db = AsyncMock()

    def fake_decode(_token: str):
        return {"sub": "1"}

    result = await refresh_tokens(
        db=db,
        refresh_token="token",
        decode_refresh_fn=fake_decode,
    )

    assert result is None


@pytest.mark.asyncio
async def test_refresh_tokens_not_stored():
    db = AsyncMock()

    def fake_decode(_token: str):
        return {"sub": "1", "jti": "jti_123"}

    with patch(
        "app.service.jwt_login_service.get_refrsh_token",
        new=AsyncMock(return_value=None),
    ) as mock_get_token:
        result = await refresh_tokens(
            db=db,
            refresh_token="token",
            decode_refresh_fn=fake_decode,
        )

    assert result is None
    mock_get_token.assert_awaited_once_with(db, "jti_123")


@pytest.mark.asyncio
async def test_refresh_tokens_verify_password_failed():
    db = AsyncMock()

    stored = AsyncMock()
    stored.hashed_token = "hashed_refresh_token"

    def fake_decode(_token: str):
        return {"sub": "1", "jti": "jti_123"}

    with patch(
        "app.service.jwt_login_service.get_refrsh_token",
        new=AsyncMock(return_value=stored),
    ) as mock_get_token, patch(
        "app.service.jwt_login_service.verify_password",
        return_value=False,
    ) as mock_verify:
        result = await refresh_tokens(
            db=db,
            refresh_token="token",
            decode_refresh_fn=fake_decode,
        )

    assert result is None
    mock_get_token.assert_awaited_once_with(db, "jti_123")
    mock_verify.assert_called_once_with("token", "hashed_refresh_token")


@pytest.mark.asyncio
async def test_refresh_tokens_success():
    db = AsyncMock()

    stored = AsyncMock()
    stored.hashed_token = "hashed_refresh_token"

    def fake_decode(_token: str):
        return {"sub": "42", "jti": "jti_123"}

    new_tokens = ("new_access_token", "new_refresh_token")

    with patch(
        "app.service.jwt_login_service.get_refrsh_token",
        new=AsyncMock(return_value=stored),
    ) as mock_get_token, patch(
        "app.service.jwt_login_service.verify_password",
        return_value=True,
    ) as mock_verify, patch(
        "app.service.jwt_login_service.revoke_refresh_token",
        new=AsyncMock(),
    ) as mock_revoke, patch(
        "app.service.jwt_login_service.issue_tokens",
        new=AsyncMock(return_value=new_tokens),
    ) as mock_issue:
        result = await refresh_tokens(
            db=db,
            refresh_token="token",
            decode_refresh_fn=fake_decode,
        )

    assert result == new_tokens
    mock_get_token.assert_awaited_once_with(db, "jti_123")
    mock_verify.assert_called_once_with("token", "hashed_refresh_token")
    mock_revoke.assert_awaited_once_with(db, "jti_123")
    mock_issue.assert_awaited_once_with(db, 42)