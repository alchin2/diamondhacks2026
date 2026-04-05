from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from service.chat_service import ChatService

router = APIRouter()
chat_service = ChatService()

# chatroom_id -> list of connected WebSockets
active_connections: dict[str, list[WebSocket]] = {}


async def verify_participant(chatroom_id: str, user_id: str) -> bool:
    """Check that the user is part of the chatroom's deal."""
    try:
        chatroom = chat_service.get_chatroom(chatroom_id)
        deal = chatroom.get("deals", {})
        return user_id in [deal.get("user1_id"), deal.get("user2_id")]
    except ValueError:
        return False


@router.websocket("/ws/chat/{chatroom_id}")
async def websocket_chat(websocket: WebSocket, chatroom_id: str):
    """
    WebSocket endpoint for real-time chat.
    Connect: ws://localhost:8000/ws/chat/{chatroom_id}?user_id={user_id}
    Send: {"content": "your message"}
    Receive: {"id": "...", "chatroom_id": "...", "sender_id": "...", "content": "...", "created_at": "..."}
    """
    user_id = websocket.query_params.get("user_id")
    if not user_id:
        await websocket.close(code=4001, reason="Missing user_id query param")
        return

    # Verify user is a participant in this chatroom
    if not await verify_participant(chatroom_id, user_id):
        await websocket.close(code=4003, reason="Not a participant in this chatroom")
        return

    await websocket.accept()

    # Track connection
    if chatroom_id not in active_connections:
        active_connections[chatroom_id] = []
    active_connections[chatroom_id].append(websocket)

    try:
        while True:
            data = await websocket.receive_json()
            content = data.get("content", "").strip()
            if not content:
                continue

            # Save message to DB
            message = chat_service.send_message(chatroom_id, user_id, content)

            # Broadcast to all connections in this chatroom
            for conn in active_connections.get(chatroom_id, []):
                try:
                    await conn.send_json(message)
                except Exception:
                    pass

    except WebSocketDisconnect:
        active_connections[chatroom_id].remove(websocket)
        if not active_connections[chatroom_id]:
            del active_connections[chatroom_id]
