import random

from starlette.websockets import WebSocket


class Room:
    """Комната."""

    def __init__(self, connection: WebSocket) -> None:
        self.connections = [connection]
        self.is_private = random.choice([True])


class ConnectionManager:
    """Менеджер соединений."""

    def __init__(self) -> None:
        self.rooms = {}

    async def connect(self, websocket: WebSocket, room_id: str) -> None:
        """
        Метод для установки соединения.

        :param websocket: вебсокет
        :param room_id: ID комнаты
        """
        await websocket.accept()
        room = self.rooms.get(room_id)
        if room:
            if len(room.connections) >= 2:
                await websocket.close(code=4000)
            room.connections.append(websocket)
        else:
            room = Room(websocket)
            self.rooms[room_id] = room

    def disconnect(self, websocket: WebSocket, room_id: str) -> None:
        """
        Метод для разрыва соединения.

        :param websocket: вебсокет
        :param room_id: ID комнаты
        """
        room = self.rooms.get(room_id)
        room.connections.remove(websocket)
        if not room.connections:
            self.rooms.pop(room)

    # async def send_personal_message(self, message: str, websocket: WebSocket):
    #     await websocket.send_text(message)

    # async def broadcast(self, message: str):
    #     for room in self.rooms.values():
    #         for connection in room.connections:
    #             await connection.send_text(message)

    async def send_room_message(self, message: str, room_id: str) -> None:
        """
        Метод для отправки сообщения всем пользователям, находящимся в комнате.

        :param message: сообщение
        :param room_id: ID комнаты
        """
        room = self.rooms.get(room_id)
        for connection in room.connections:
            await connection.send_text(message)

    async def send_private_rooms_message(self, message: str) -> None:
        """
        Метод для отправки сообщения всем пользователям, находящимся в комнатах, в которых
        может состоять только 2 пользователя.

        :param message: сообщение
        """
        for room in self.rooms.values():
            if room.is_private:
                for connection in room.connections:
                    await connection.send_text(message)
