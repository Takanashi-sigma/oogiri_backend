from datetime import datetime, timezone, timedelta
from app.crud.jwt_login_crud import store_refresh_token, get_refrsh_token, revoke_refresh_token
from app.core.security import verify_password, create_access_token, create_refresh_token, new_jti


async def _decode_refresh_inline(token: str):
    from app.core.security import decode_refresh
    return decode_refresh(token)


async def issue_tokens(db, user_id: int):
    access = create_access_token(user_id)
    jti = new_jti()
    refresh = create_refresh_token(user_id, jti)
    payload = await _decode_refresh_inline(refresh)
    exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
    
    await store_refresh_token(db, user_id, jti, refresh, exp)
    return access, refresh


async def refresh_tokens(db, refresh_token: str, decode_refresh_fn):
    try:
        payload = decode_refresh_fn(refresh_token)
    except Exception:
        return None
    jti = payload.get("jti")
    if not jti:
        return None
    stored = await get_refrsh_token(db, jti)
    if not stored:
        return None
    if not verify_password(refresh_token, stored.hashed_token):
        return None
    await revoke_refresh_token(db, jti)
    return await issue_tokens(db, int(payload["sub"]))

    
