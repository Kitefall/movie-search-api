from typing import Optional

from pydantic import BaseModel, EmailStr, field_validator


def validate_password(password: str) -> str:
    if ' ' in password:
        raise ValueError('Пароль не должен содержать пробелов')
    if password.islower() or password.isupper():
        raise ValueError('Пароль должен содержать большие и маленькие буквы')
    if not any(char.isdigit() for char in password):
        raise ValueError('Пароль должен содержать хотя бы одну цифру')
    if password.isdigit():
        raise ValueError('Пароль не должен состоять только из цифр')
    return password


class UserBase(BaseModel):
    name: str
    email: EmailStr


class UserCreate(UserBase):
    password: str

    @field_validator('password')
    def password_strength(cls, password):
        return validate_password(password)


class UserUpdate(BaseModel):
    name: Optional[str] = None
    password: Optional[str] = None

    @field_validator('password')
    def password_strength(cls, password):
        if password is None:
            return password
        return validate_password(password)


class UserDelete(BaseModel):
    id: int


class UserLogin(BaseModel):
    email: EmailStr
    password: str
