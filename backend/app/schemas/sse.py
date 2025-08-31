from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from enum import Enum


class SSEEventType(str, Enum):
    TASK_CREATED = "task_created"
    TASK_UPDATED = "task_updated"
    TASK_DELETED = "task_deleted"
    CONNECTION_ESTABLISHED = "connection_established"
    HEARTBEAT = "heartbeat"


class SSEEvent(BaseModel):
    event: SSEEventType = Field(..., description="Type of SSE event")
    data: Dict[str, Any] = Field(..., description="Event data payload")
    id: Optional[str] = Field(None, description="Event ID for client tracking")
    retry: Optional[int] = Field(None, description="Retry interval in milliseconds")

    model_config = {"use_enum_values": True}

    def to_sse_format(self) -> str:
        lines = []
        
        if self.id:
            lines.append(f"id: {self.id}")
        
        lines.append(f"event: {self.event}")
        
        import json
        data_str = json.dumps(self.data)
        for line in data_str.split('\n'):
            lines.append(f"data: {line}")
        
        if self.retry:
            lines.append(f"retry: {self.retry}")
        
        lines.append("")
        lines.append("")
        
        return "\n".join(lines)


class SSEConnectionInfo(BaseModel):
    connection_id: str = Field(..., description="Unique connection identifier")
    connected_at: str = Field(..., description="Connection timestamp")
    user_agent: Optional[str] = Field(None, description="Client user agent")
    
    model_config = {"from_attributes": True}