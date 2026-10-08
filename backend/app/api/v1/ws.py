import asyncio
import json
from typing import Dict, List
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter(prefix="/ws", tags=["Real-Time WebSockets"])

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, claim_id: str, websocket: WebSocket):
        await websocket.accept()
        if claim_id not in self.active_connections:
            self.active_connections[claim_id] = []
        self.active_connections[claim_id].append(websocket)

    def disconnect(self, claim_id: str, websocket: WebSocket):
        if claim_id in self.active_connections:
            self.active_connections[claim_id].remove(websocket)
            if not self.active_connections[claim_id]:
                del self.active_connections[claim_id]

    async def broadcast_step(self, claim_id: str, step: str, progress: int, message: str):
        if claim_id in self.active_connections:
            payload = json.dumps({
                "claim_id": claim_id,
                "step": step,
                "progress": progress,
                "message": message
            })
            for connection in self.active_connections[claim_id]:
                try:
                    await connection.send_text(payload)
                except Exception:
                    pass

ws_manager = ConnectionManager()

@router.websocket("/triage/{claim_id}")
async def websocket_triage_endpoint(websocket: WebSocket, claim_id: str):
    await ws_manager.connect(claim_id, websocket)
    try:
        while True:
            # Keep alive and receive any client ping
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text(json.dumps({"type": "pong"}))
    except WebSocketDisconnect:
        ws_manager.disconnect(claim_id, websocket)
