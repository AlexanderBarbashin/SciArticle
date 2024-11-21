from contextlib import AbstractAsyncContextManager, asynccontextmanager

import uvicorn
from fastapi import FastAPI
from pika.adapters.blocking_connection import BlockingConnection
from pika.connection import ConnectionParameters

from chat.router import router as chat_router
from config import APP_HOST, APP_PORT, RABBIT_HOST, RABBIT_PORT
from users.users_router import router as users_router

connection_params = ConnectionParameters(
    host=RABBIT_HOST,
    port=RABBIT_PORT,
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AbstractAsyncContextManager:
    """
    Функция для подготовки приложения к работе.

    :param app: Приложение
    :return: Контекстный менеджер
    """

    with BlockingConnection(connection_params) as conn:
        with conn.channel() as ch:
            ch.queue_declare(queue="messages")
    yield


app = FastAPI(title="Test task SciArticle", lifespan=lifespan)

app.include_router(chat_router)
app.include_router(users_router)


if __name__ == "__main__":
    uvicorn.run(app=app, host=APP_HOST, port=int(APP_PORT))
