from typing import Dict

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.responses import Response

from database import get_async_session

from .users_models import User
from .users_schemas import UserAdd, UserAuth
from .users_utils import (authenticate_user, create_access_token,
                          get_current_user, get_password_hash,
                          get_user_from_db)

router = APIRouter(prefix="/users", tags=["User"])


@router.post("/register")
async def register_user(
    user_data: UserAdd, session: AsyncSession = Depends(get_async_session)
) -> Dict[str, str]:
    """
    Эндпоинт для регистрации пользователя.

    :param user_data: Данные пользователя
    :param session: Асинхронная сессия
    :return: Ответ сервера
    """
    user = await get_user_from_db(username=user_data.username)
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="User already exists."
        )
    user_dict = user_data.model_dump()
    user_dict["password"] = get_password_hash(user_data.password)
    new_user = User(**user_dict)
    session.add(new_user)
    await session.commit()
    return {"message": "User successfully register."}


@router.post("/login")
async def auth_user(response: Response, user_data: UserAuth) -> Dict[str, str | None]:
    """
    Эндпоинт для аутентификации пользователя.

    :param response: Ответ сервера
    :param user_data: Данные пользователя
    :return: Ответ сервера
    """
    user = await authenticate_user(
        username=user_data.username, password=user_data.password
    )
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Wrong username or password.",
        )
    access_token = create_access_token({"sub": user.username})
    response.set_cookie(key="users_access_token", value=access_token, httponly=True)
    return {"access_token": access_token, "refresh_token": None}


@router.post("/logout/")
async def logout_user(response: Response) -> Dict[str, str]:
    """
    Эндпоинт для выхода пользователя из учетной записи.

    :param response: Ответ сервера
    :return: Ответ сервера
    """
    response.delete_cookie(key="users_access_token")
    return {"message": "User successfully logout"}
