from pydantic import BaseModel, EmailStr, constr, field_validator
import re

class UserCreate(BaseModel):
    email: EmailStr
    password: constr(min_length=8)
        
    @field_validator("password")
    def check_password(cls, password: str) -> str:
        password = str(password)
        if (
            len(password) < 8 
            or re.search(r"[A-Z]", password) is None 
            or re.search(r"[a-z]", password) is None 
            or re.search(r"\d", password) is None
            ):
            raise ValueError("8文字以上必要で大小英字と数字を含めてください。")
        #if len(password.encode("utf-8")) > 72:
        #    raise ValueError("パスワードは72バイト以内にしてください。")
        return password


class UserRead(BaseModel):
    id: int
    email: EmailStr
    is_active: bool
    is_admin: bool

    class Config:
        from_attributes = True
