"""
Pydantic models for request/response validation
Clean data models for the Mem0 API
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class Message(BaseModel):
    """Message in a conversation"""
    role: str = Field(..., description="Role of the message sender (user, assistant, system)", examples=["user", "assistant"])
    content: str = Field(..., description="Content of the message", examples=["I love playing poker"])
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "role": "user",
                    "content": "My name is Doug and I struggle with gambling addiction"
                }
            ]
        }
    }


class AddMemoryRequest(BaseModel):
    """Request model for adding memories"""
    messages: List[Message] = Field(..., description="List of conversation messages")
    user_id: Optional[str] = Field(None, description="User identifier (e.g., doug_123, marc_456)")
    agent_id: Optional[str] = Field(None, description="Agent identifier (optional)")
    run_id: Optional[str] = Field(None, description="Run identifier (replaces session_id in v1.0.0)")
    session_id: Optional[str] = Field(None, description="Legacy session identifier (mapped to run_id)")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata (optional)")
    version: Optional[str] = Field("v2", description="API version (v2 recommended)")
    output_format: Optional[str] = Field("v1.1", description="Output format version")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "messages": [
                        {
                            "role": "user",
                            "content": "My name is Doug and I live in Las Vegas. I struggle with card gambling."
                        },
                        {
                            "role": "assistant",
                            "content": "Hello Doug, I'm here to help you with your gambling challenges."
                        }
                    ],
                    "user_id": "doug_123"
                }
            ]
        }
    }


class SearchMemoryRequest(BaseModel):
    """Request model for searching memories"""
    query: str = Field(..., description="Search query (e.g., 'What is the user's name?')")
    user_id: Optional[str] = Field(None, description="User identifier (e.g., doug_123)")
    agent_id: Optional[str] = Field(None, description="Agent identifier (optional)")
    run_id: Optional[str] = Field(None, description="Run identifier (optional)")
    session_id: Optional[str] = Field(None, description="Legacy session identifier (optional)")
    limit: int = Field(10, description="Maximum number of results (1-100)")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "query": "What triggers gambling urges for the user?",
                    "user_id": "doug_123",
                    "limit": 10
                }
            ]
        }
    }


class UpdateMemoryRequest(BaseModel):
    """Request model for updating a memory"""
    memory_id: str = Field(..., description="Memory ID to update (UUID from get-all)")
    data: str = Field(..., description="New memory text")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "memory_id": "550e8400-e29b-41d4-a716-446655440000",
                    "data": "User's name is Douglas (preferred name: Doug)"
                }
            ]
        }
    }


class DeleteMemoryRequest(BaseModel):
    """Request model for deleting a memory"""
    memory_id: str = Field(..., description="Memory ID to delete (UUID from get-all)")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "memory_id": "550e8400-e29b-41d4-a716-446655440000"
                }
            ]
        }
    }


class GetAllMemoriesRequest(BaseModel):
    """Request model for getting all memories for a specific user/agent/run
    
    NOTE: You MUST provide at least ONE identifier (user_id, agent_id, or run_id)
    To get ALL memories across ALL users, use the admin endpoint: GET /admin/all-memories
    """
    user_id: Optional[str] = Field(None, description="User identifier (e.g., doug_123)")
    agent_id: Optional[str] = Field(None, description="Agent identifier (optional)")
    run_id: Optional[str] = Field(None, description="Run identifier (optional)")
    session_id: Optional[str] = Field(None, description="Legacy session identifier (optional)")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "user_id": "doug_123"
                }
            ]
        }
    }


class GetMemoryHistoryRequest(BaseModel):
    """Request model for getting memory history"""
    memory_id: str = Field(..., description="Memory ID to get history for (UUID from get-all)")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "memory_id": "550e8400-e29b-41d4-a716-446655440000"
                }
            ]
        }
    }

