"""
Pydantic models for request/response validation
Clean data models for the Mem0 API

These models power:
- request validation (FastAPI automatically validates incoming JSON)
- Swagger UI schemas + example payloads (the "Try it out" defaults)

Teaching note:
The example payloads below use a fun, realistic theme: a DevOps "On-Call Buddy"
that remembers user preferences (how to get paged, tools they use, etc.). You can
swap the theme easily by updating the `json_schema_extra` examples.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class Message(BaseModel):
    """Message in a conversation"""
    role: str = Field(..., description="Role of the message sender (user, assistant, system)", examples=["user", "assistant"])
    content: str = Field(..., description="Content of the message", examples=["I'm on-call this week. Please page me by SMS after 8pm."])
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "role": "user",
                    "content": "My name is Riley. I'm on-call this week. Please page me by SMS after 8pm."
                }
            ]
        }
    }


class AddMemoryRequest(BaseModel):
    """Request model for adding memories"""
    messages: List[Message] = Field(..., description="List of conversation messages")
    user_id: Optional[str] = Field(None, description="User identifier (e.g., riley_123, casey_456)")
    agent_id: Optional[str] = Field(None, description="Agent identifier (optional)")
    run_id: Optional[str] = Field(None, description="Run identifier (replaces session_id in v1.0.0)")
    session_id: Optional[str] = Field(None, description="Legacy session identifier (mapped to run_id)")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata (optional)")
    infer: bool = Field(
        True,
        description="If true (default), Mem0 uses an LLM to decide what to store. If false, stores messages as raw memories (useful for deterministic labs).",
    )
    memory_type: Optional[str] = Field(
        None,
        description='Optional memory type (advanced). For procedural memory, use "procedural_memory" with agent_id.',
    )
    prompt: Optional[str] = Field(None, description="Optional custom prompt for memory extraction (advanced).")
    version: Optional[str] = Field("v2", description="API version (v2 recommended)")
    output_format: Optional[str] = Field("v1.1", description="Output format version")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "messages": [
                        {
                            "role": "user",
                            "content": "My name is Riley. I'm on-call this week. Please page me by SMS after 8pm."
                        },
                        {
                            "role": "assistant",
                            "content": "Got it. I’ll page you by SMS after 8pm while you’re on-call."
                        }
                    ],
                    "user_id": "riley_123",
                    "infer": True
                }
            ]
        }
    }


class SearchMemoryRequest(BaseModel):
    """Request model for searching memories"""
    query: str = Field(..., description="Search query (e.g., 'What is the user's name?')")
    user_id: Optional[str] = Field(None, description="User identifier (e.g., riley_123)")
    agent_id: Optional[str] = Field(None, description="Agent identifier (optional)")
    run_id: Optional[str] = Field(None, description="Run identifier (optional)")
    session_id: Optional[str] = Field(None, description="Legacy session identifier (optional)")
    limit: int = Field(10, description="Maximum number of results (1-100)")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "query": "How should I notify Riley after hours?",
                    "user_id": "riley_123",
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
                    "data": "Riley prefers SMS after 8pm when on-call."
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
    user_id: Optional[str] = Field(None, description="User identifier (e.g., riley_123)")
    agent_id: Optional[str] = Field(None, description="Agent identifier (optional)")
    run_id: Optional[str] = Field(None, description="Run identifier (optional)")
    session_id: Optional[str] = Field(None, description="Legacy session identifier (optional)")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "user_id": "riley_123"
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

