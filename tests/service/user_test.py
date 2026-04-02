import pytest
from fastapi import HTTPException
from unittest.mock import AsyncMock, patch

from app.service.user_service import (
    register_user,
    authenticate_user,
    get_user_by_id_with_validation,
)


@pytest.mark.asyncio
async def test_register_user_success():
    db = AsyncMock()

    user_mock = AsyncMock()

    with patch(
        "app.service.user_service.hash_password",
        return_value="hashed_password_123",
    ) as mock_hash, patch(
        "app.service.user_service.create_user_in_db",
        new=AsyncMock(return_value=user_mock),
    ) as mock_create:
        result = await register_user(
            db=db,
            email="test@example.com",
            plain_password="plain_password",
            name="sigma",
        )

    assert result == user_mock
    mock_hash.assert_called_once_with("plain_password")
    mock_create.assert_awaited_once_with(
        db,
        email="test@example.com",
        hashed_password="hashed_password_123",
        name="sigma",
    )


@pytest.mark.asyncio
async def test_authenticate_user_success():
    db = AsyncMock()

    user_mock = AsyncMock()
    user_mock.hashed_password = "hashed_pw"

    with patch(
        "app.service.user_service.get_user_by_email",
        new=AsyncMock(return_value=user_mock),
    ) as mock_get_user, patch(
        "app.service.user_service.verify_password",
        return_value=True,
    ) as mock_verify:
        result = await authenticate_user(
            db=db,
            email="test@example.com",
            plain_password="plain_password",
        )

    assert result == user_mock
    mock_get_user.assert_awaited_once_with(db, "test@example.com")
    mock_verify.assert_called_once_with("plain_password", "hashed_pw")


@pytest.mark.asyncio
async def test_authenticate_user_user_not_found():
    db = AsyncMock()

    with patch(
        "app.service.user_service.get_user_by_email",
        new=AsyncMock(return_value=None),
    ) as mock_get_user, patch(
        "app.service.user_service.verify_password",
        return_value=True,
    ) as mock_verify:
        result = await authenticate_user(
            db=db,
            email="test@example.com",
            plain_password="plain_password",
        )

    assert result is None
    mock_get_user.assert_awaited_once_with(db, "test@example.com")
    mock_verify.assert_not_called()


@pytest.mark.asyncio
async def test_authenticate_user_password_invalid():
    db = AsyncMock()

    user_mock = AsyncMock()
    user_mock.hashed_password = "hashed_pw"

    with patch(
        "app.service.user_service.get_user_by_email",
        new=AsyncMock(return_value=user_mock),
    ) as mock_get_user, patch(
        "app.service.user_service.verify_password",
        return_value=False,
    ) as mock_verify:
        result = await authenticate_user(
            db=db,
            email="test@example.com",
            plain_password="wrong_password",
        )

    assert result is None
    mock_get_user.assert_awaited_once_with(db, "test@example.com")
    mock_verify.assert_called_once_with("wrong_password", "hashed_pw")


@pytest.mark.asyncio
async def test_get_user_by_id_with_validation_success():
    db = AsyncMock()

    user_mock = AsyncMock()

    with patch(
        "app.service.user_service.get_user_by_id",
        new=AsyncMock(return_value=user_mock),
    ) as mock_get:
        result = await get_user_by_id_with_validation(db=db, user_id=1)

    assert result == user_mock
    mock_get.assert_awaited_once_with(db=db, user_id=1)


@pytest.mark.asyncio
async def test_get_user_by_id_with_validation_not_found():
    db = AsyncMock()

    with patch(
        "app.service.user_service.get_user_by_id",
        new=AsyncMock(return_value=None),
    ) as mock_get:
        with pytest.raises(HTTPException) as exc_info:
            await get_user_by_id_with_validation(db=db, user_id=1)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "user not found"
    mock_get.assert_awaited_once_with(db=db, user_id=1)