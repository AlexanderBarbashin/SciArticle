from pydantic import BaseModel, Field


class UserAuth(BaseModel):
    """Модель пользователя для аутентификации. Родитель: BaseModel."""

    username: str = Field(..., min_length=5, max_length=50, description="Username")
    password: str = Field(..., min_length=8, max_length=50, description="Password")


class UserAdd(UserAuth):
    """Модель пользователя для регистрации. Родитель: UserAuth."""

    first_name: str = Field(..., min_length=2, max_length=50, description="Name")
    last_name: str = Field(..., min_length=2, max_length=50, description="Surname")
