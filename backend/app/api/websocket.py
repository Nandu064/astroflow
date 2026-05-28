from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.broadcaster import connect, disconnect

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(ws: WebSocket) -> None:
    await connect(ws)
    try:
        # Keep alive — client can send pings, we just hold the connection
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        pass
    except Exception:
        pass
    finally:
        await disconnect(ws)
