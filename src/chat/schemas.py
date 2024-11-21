from pydantic import BaseModel


class Message(BaseModel):
    """Модель сообщения. Родитель: BaseModel."""

    msg: str
