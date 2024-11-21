from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException
from jose import JWTError
from passlib.context import CryptContext
from sqlalchemy import select
from starlette import status
from starlette.requests import Request

from config import ALGORITHM, SECRET_KEY
from database import async_session_maker
from users.users_models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Функция для проверки пароля пользователя.

    :param plain_password: введенный пароль
    :param hashed_password: хэшированный пароль
    :return: True | False
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Функция для хэширования пароля.

    :param password: пароль
    :return: хэшированный пароль
    """
    return pwd_context.hash(password)


async def get_user_from_db(username: str) -> User:
    """
    Функция для получения записи пользователя из базы данных.

    :param username: имя пользователя
    :return: пользователь
    """
    user_query = select(User).filter_by(username=username)
    async with async_session_maker() as session:
        user_query_result = await session.execute(user_query)
    user = user_query_result.scalars().one_or_none()
    return user


async def authenticate_user(username: str, password: str) -> User | None:
    """
    Функция для аутентификации пользователя.

    :param username: имя пользователя
    :param password: пароль пользователя
    :return: пользователь
    """
    user = await get_user_from_db(username=username)
    if (
        not user
        or verify_password(plain_password=password, hashed_password=user.password)
        is False
    ):
        return None
    return user


def create_access_token(data: dict) -> str:
    """
    Функция для создания токена.

    :param data: данные
    :return: токен
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=30)
    to_encode.update({"exp": expire})
    encode_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encode_jwt


def get_token(request: Request) -> str:
    """
    Функция для получения токена.

    :param request: запрос
    :return: токен
    """
    token = request.cookies.get("users_access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token not found."
        )
    return token


async def get_current_websocket_user(token: str) -> User:
    """
    Функция для получения текущего пользователя по вебсокету.

    :param token: токен
    :return: пользователь
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token not valid."
        )
    username = payload.get("sub")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Username not found."
        )
    async with async_session_maker() as session:
        user = await session.get(User, username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found."
        )
    return user


async def get_current_user(token: str = Depends(get_token)) -> User:
    """
    Функция для получения текущего пользователя.

    :param token: токен
    :return: пользователь
    """
    user = await get_current_websocket_user(token)
    return user
