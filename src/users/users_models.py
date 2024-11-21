from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class User(Base):
    """Пользователь. Родитель: Base."""

    __tablename__ = "user"
    username: Mapped[str] = mapped_column(primary_key=True)
    first_name: Mapped[str]
    last_name: Mapped[str]
    password: Mapped[str]
