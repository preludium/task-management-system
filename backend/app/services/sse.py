import asyncio
import logging
import uuid
from typing import Dict, Optional, AsyncGenerator
from datetime import datetime
from contextlib import asynccontextmanager

from app.schemas.sse import SSEEvent, SSEEventType, SSEConnectionInfo

logger = logging.getLogger(__name__)


class SSEConnection:
    """Represents a single SSE connection"""
    
    def __init__(self, connection_id: str, user_agent: Optional[str] = None):
        self.connection_id = connection_id
        self.user_agent = user_agent
        self.connected_at = datetime.utcnow()
        self.queue: asyncio.Queue = asyncio.Queue()
        self.is_active = True
    
    async def send_event(self, event: SSEEvent) -> bool:
        """Send an event to this connection"""
        if not self.is_active:
            return False
        
        try:
            await self.queue.put(event.to_sse_format())
            return True
        except Exception as e:
            logger.warning(f"Failed to send event to connection {self.connection_id}: {e}")
            self.is_active = False
            return False
    
    async def close(self):
        """Close the connection"""
        self.is_active = False
        # Clear the queue
        while not self.queue.empty():
            try:
                self.queue.get_nowait()
            except asyncio.QueueEmpty:
                break
    
    def get_info(self) -> SSEConnectionInfo:
        """Get connection information"""
        return SSEConnectionInfo(
            connection_id=self.connection_id,
            connected_at=self.connected_at.isoformat(),
            user_agent=self.user_agent
        )


class SSEService:
    """Service for managing Server-Sent Events connections and broadcasting"""
    
    def __init__(self):
        self.connections: Dict[str, SSEConnection] = {}
        self._cleanup_task: Optional[asyncio.Task] = None
        self._cleanup_interval = 30  # seconds
        self._heartbeat_interval = 30  # seconds
        self._heartbeat_task: Optional[asyncio.Task] = None
    
    async def start(self):
        """Start the SSE service background tasks"""
        if self._cleanup_task is None or self._cleanup_task.done():
            self._cleanup_task = asyncio.create_task(self._cleanup_dead_connections())
            logger.info("SSE cleanup task started")
        
        if self._heartbeat_task is None or self._heartbeat_task.done():
            self._heartbeat_task = asyncio.create_task(self._send_heartbeats())
            logger.info("SSE heartbeat task started")
    
    async def stop(self):
        """Stop the SSE service and cleanup resources"""
        # Cancel background tasks
        if self._cleanup_task and not self._cleanup_task.done():
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        if self._heartbeat_task and not self._heartbeat_task.done():
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass
        
        # Close all connections
        for connection in list(self.connections.values()):
            await connection.close()
        
        self.connections.clear()
        logger.info("SSE service stopped")
    
    def add_connection(self, user_agent: Optional[str] = None) -> str:
        """Add a new SSE connection and return connection ID"""
        connection_id = str(uuid.uuid4())
        connection = SSEConnection(connection_id, user_agent)
        self.connections[connection_id] = connection
        
        logger.info(f"New SSE connection added: {connection_id}")
        return connection_id
    
    async def remove_connection(self, connection_id: str) -> bool:
        """Remove an SSE connection"""
        if connection_id in self.connections:
            connection = self.connections[connection_id]
            await connection.close()
            del self.connections[connection_id]
            logger.info(f"SSE connection removed: {connection_id}")
            return True
        return False
    
    async def get_connection_stream(self, connection_id: str) -> AsyncGenerator[str, None]:
        """Get the event stream for a specific connection"""
        if connection_id not in self.connections:
            logger.warning(f"Attempted to get stream for non-existent connection: {connection_id}")
            return
        
        connection = self.connections[connection_id]
        
        # Send connection established event
        welcome_event = SSEEvent(
            event=SSEEventType.CONNECTION_ESTABLISHED,
            data={
                "connection_id": connection_id,
                "timestamp": datetime.utcnow().isoformat(),
                "message": "SSE connection established"
            },
            id=str(uuid.uuid4())
        )
        
        await connection.send_event(welcome_event)
        
        try:
            while connection.is_active:
                try:
                    # Wait for events with timeout to allow periodic checks
                    event_data = await asyncio.wait_for(
                        connection.queue.get(), 
                        timeout=1.0
                    )
                    yield event_data
                except asyncio.TimeoutError:
                    # Timeout is normal, just continue the loop
                    continue
                except Exception as e:
                    logger.error(f"Error in SSE stream for {connection_id}: {e}")
                    break
        finally:
            # Cleanup connection when stream ends
            await self.remove_connection(connection_id)
    
    async def broadcast_event(self, event: SSEEvent) -> int:
        """Broadcast an event to all active connections"""
        if not self.connections:
            logger.debug("No active SSE connections to broadcast to")
            return 0
        
        successful_sends = 0
        failed_connections = []
        
        for connection_id, connection in self.connections.items():
            success = await connection.send_event(event)
            if success:
                successful_sends += 1
            else:
                failed_connections.append(connection_id)
        
        # Remove failed connections
        for connection_id in failed_connections:
            await self.remove_connection(connection_id)
        
        logger.info(f"Broadcasted event {event.event} to {successful_sends} connections")
        return successful_sends

    async def _cleanup_dead_connections(self):
        """Background task to cleanup dead connections"""
        while True:
            try:
                await asyncio.sleep(self._cleanup_interval)
                
                dead_connections = []
                for connection_id, connection in self.connections.items():
                    if not connection.is_active:
                        dead_connections.append(connection_id)
                
                for connection_id in dead_connections:
                    await self.remove_connection(connection_id)
                
                if dead_connections:
                    logger.info(f"Cleaned up {len(dead_connections)} dead SSE connections")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in SSE cleanup task: {e}")
    
    async def _send_heartbeats(self):
        """Background task to send heartbeat events"""
        while True:
            try:
                await asyncio.sleep(self._heartbeat_interval)
                
                if self.connections:
                    heartbeat_event = SSEEvent(
                        event=SSEEventType.HEARTBEAT,
                        data={
                            "timestamp": datetime.utcnow().isoformat(),
                            "active_connections": len(self.connections)
                        },
                        id=str(uuid.uuid4())
                    )
                    
                    await self.broadcast_event(heartbeat_event)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in SSE heartbeat task: {e}")


# Global SSE service instance
sse_service = SSEService()


async def get_sse_service() -> SSEService:
    """Dependency to get the SSE service instance"""
    await sse_service.start()
    return sse_service


@asynccontextmanager
async def sse_service_lifespan():
    """Context manager for SSE service lifecycle management"""
    await sse_service.start()
    try:
        yield sse_service
    finally:
        await sse_service.stop()