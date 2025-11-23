"""WebSocket endpoints for real-time AI content streaming."""
from typing import Dict, Set
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
import json
import uuid

from app.database import get_db
from app.models.user import User
from app.models.content import Content
from app.core.security import decode_access_token
from app.services.claude import ClaudeService
from app.core.logging import logger

router = APIRouter()


class ConnectionManager:
    """Manages WebSocket connections for real-time streaming."""

    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        """Accept and store a new WebSocket connection."""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"WebSocket connected: {client_id}")

    def disconnect(self, client_id: str):
        """Remove a WebSocket connection."""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            logger.info(f"WebSocket disconnected: {client_id}")

    async def send_message(self, message: dict, client_id: str):
        """Send a message to a specific client."""
        if client_id in self.active_connections:
            websocket = self.active_connections[client_id]
            await websocket.send_json(message)

    async def send_text_chunk(self, text: str, client_id: str):
        """Send a text chunk to a specific client."""
        await self.send_message({"type": "chunk", "content": text}, client_id)

    async def send_error(self, error: str, client_id: str):
        """Send an error message to a specific client."""
        await self.send_message({"type": "error", "message": error}, client_id)

    async def send_complete(self, content_id: str, client_id: str):
        """Send completion message to a specific client."""
        await self.send_message(
            {"type": "complete", "content_id": content_id}, client_id
        )


manager = ConnectionManager()


async def get_websocket_user(
    token: str = Query(...), db: AsyncSession = Depends(get_db)
) -> User:
    """Authenticate WebSocket connection via token query parameter."""
    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        if not user_id:
            raise ValueError("Invalid token")

        from sqlalchemy import select

        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            raise ValueError("User not found")

        return user
    except Exception as e:
        logger.error(f"WebSocket authentication failed: {str(e)}")
        raise


@router.websocket("/ws/content/generate")
async def websocket_generate_content(
    websocket: WebSocket,
    token: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """
    WebSocket endpoint for real-time AI content generation streaming.

    Expected message format:
    {
        "type": "blog_post" | "email" | "social_post" | "video_script",
        "campaign_id": "uuid",
        "prompt": "content generation prompt",
        "title": "optional title",
        "metadata": {}
    }
    """
    client_id = str(uuid.uuid4())

    try:
        # Authenticate user
        user = await get_websocket_user(token, db)

        # Connect WebSocket
        await manager.connect(websocket, client_id)

        # Send connection confirmation
        await manager.send_message(
            {"type": "connected", "message": "Ready to generate content"}, client_id
        )

        claude_service = ClaudeService()

        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)

            try:
                content_type = message.get("type")
                campaign_id = message.get("campaign_id")
                prompt = message.get("prompt")
                title = message.get("title")
                metadata = message.get("metadata", {})

                if not content_type or not prompt:
                    await manager.send_error(
                        "Missing required fields: type and prompt", client_id
                    )
                    continue

                # Create content record
                content = Content(
                    user_id=user.id,
                    campaign_id=campaign_id if campaign_id else None,
                    type=content_type,
                    title=title,
                    body="",  # Will be updated as we stream
                    metadata=metadata,
                    status="generating",
                )
                db.add(content)
                await db.commit()
                await db.refresh(content)

                # Send content ID to client
                await manager.send_message(
                    {"type": "started", "content_id": str(content.id)}, client_id
                )

                # Stream content generation
                generated_text = ""
                async for chunk in claude_service.generate_content_stream(
                    prompt=prompt, max_tokens=3000
                ):
                    generated_text += chunk
                    await manager.send_text_chunk(chunk, client_id)

                # Update content with final generated text
                content.body = generated_text
                content.status = "draft"
                await db.commit()

                # Send completion message
                await manager.send_complete(str(content.id), client_id)

                logger.info(
                    f"Content generated successfully: {content.id} for user {user.id}"
                )

            except Exception as e:
                logger.error(f"Error generating content: {str(e)}")
                await manager.send_error(f"Generation failed: {str(e)}", client_id)

                # Update content status to failed if it exists
                if "content" in locals():
                    content.status = "failed"
                    content.metadata = {
                        **(content.metadata or {}),
                        "error": str(e),
                    }
                    await db.commit()

    except WebSocketDisconnect:
        manager.disconnect(client_id)
        logger.info(f"WebSocket disconnected normally: {client_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        manager.disconnect(client_id)


@router.websocket("/ws/analytics")
async def websocket_analytics(
    websocket: WebSocket,
    token: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """
    WebSocket endpoint for real-time analytics updates.

    Streams analytics events as they happen for the authenticated user.
    """
    client_id = str(uuid.uuid4())

    try:
        # Authenticate user
        user = await get_websocket_user(token, db)

        # Connect WebSocket
        await manager.connect(websocket, client_id)

        # Send connection confirmation
        await manager.send_message(
            {"type": "connected", "message": "Analytics stream ready"}, client_id
        )

        # Keep connection alive and send periodic updates
        while True:
            # Wait for ping/pong to keep connection alive
            try:
                data = await websocket.receive_text()
                message = json.loads(data)

                if message.get("type") == "ping":
                    await manager.send_message({"type": "pong"}, client_id)

            except WebSocketDisconnect:
                break

    except WebSocketDisconnect:
        manager.disconnect(client_id)
        logger.info(f"Analytics WebSocket disconnected: {client_id}")
    except Exception as e:
        logger.error(f"Analytics WebSocket error: {str(e)}")
        manager.disconnect(client_id)
