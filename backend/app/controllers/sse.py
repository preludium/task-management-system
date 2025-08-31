from fastapi import APIRouter, Request, Depends
from fastapi.responses import StreamingResponse
from typing import Optional
import logging

from app.services.sse import get_sse_service, SSEService
from app.schemas.sse import SSEConnectionInfo

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/sse/tasks", response_class=StreamingResponse)
async def task_updates_stream(
    request: Request,
    sse_service: SSEService = Depends(get_sse_service)
):
    """
    Server-Sent Events endpoint for real-time task updates.
    
    This endpoint establishes a persistent connection that streams
    task-related events (create, update, delete) to connected clients.
    """
    user_agent = request.headers.get("user-agent")
    
    connection_id = sse_service.add_connection(user_agent)
    
    logger.info(f"New SSE connection established: {connection_id}")
    
    async def event_stream():
        """Generate SSE event stream"""
        try:
            async for event_data in sse_service.get_connection_stream(connection_id):
                yield event_data
        except Exception as e:
            logger.error(f"Error in SSE stream for connection {connection_id}: {e}")
        finally:
            logger.info(f"SSE stream ended for connection {connection_id}")
    
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream; charset=utf-8",
        headers={
            "Content-Type": "text/event-stream; charset=utf-8",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control",
            "X-Accel-Buffering": "no",
        }
    )
