from fastapi import Depends
from faststream.rabbit.fastapi import RabbitRouter
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.templating import Jinja2Templates, _TemplateResponse
from starlette.websockets import WebSocket, WebSocketDisconnect

from chat.models import ConnectionManager
from chat.schemas import Message
from users.users_models import User
from users.users_utils import (get_current_user, get_current_websocket_user,
                               get_token)

router = RabbitRouter("amqp://guest:guest@localhost:5672/", tags=["Chat"])

templates = Jinja2Templates(directory="src/templates")

manager = ConnectionManager()


@router.post("/")
async def post_message(message: Message) -> JSONResponse:
    """
    Эндпоинт для отправки сообщения.

    :param message: сообщение
    :return: ответ сервера
    """
    await router.broker.publish(message, "messages")
    return JSONResponse({"message": "Success, message add to queue."})


@router.get("/chat/{room_id}")
def get_chat_page(
    request: Request,
    room_id: str,
    token=Depends(get_token),
    user: User = Depends(get_current_user),
) -> _TemplateResponse:
    """
    Эндпоинт для отображения страниц чатов.

    :param request: запрос
    :param room_id: ID комнаты
    :param token: токен
    :param user: текущий пользователь
    :return: шаблон
    """
    return templates.TemplateResponse(
        "chat.html",
        {
            "request": request,
            "room_id": room_id,
            "token": token,
            "username": user.username,
        },
    )


@router.subscriber("messages")
async def subscriber_handler(message: Message) -> None:
    """
    Обработчик сообщений из очереди RabbitMQ.

    :param message: сообщение
    """
    await manager.send_private_rooms_message(message.msg)


@router.websocket("/updates/{room_id}")
async def get_updates(
    websocket: WebSocket,
    room_id: str,
    user: User = Depends(get_current_websocket_user),
) -> None:
    """
    Вебсокет для получения сообщения из очереди RabbitMQ и отправки в комнаты,
    где может состоять только 2 пользователя.

    :param websocket: вебсокет
    :param room_id: ID комнаты
    :param user: текущий пользователь
    """
    await manager.connect(websocket, room_id)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_room_message(
                f"User {user.username} says: {data}", room_id
            )
    except WebSocketDisconnect:
        manager.disconnect(websocket, room_id)
        await manager.send_room_message(f"User {user.username} left the chat", room_id)
