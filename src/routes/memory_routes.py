"""
Memory management routes
CRUD operations for memories: add, search, get, update, delete, history, reset

How this file ties into the app:
- Imported and registered in `src/app.py`
- Uses the Mem0 `memory` singleton from `src/dependencies.py`

Teaching note:
- `infer=true` (default) means Mem0 uses an LLM to extract "facts" and decide what to store.
- `infer=false` is great for labs because it forces deterministic storage of raw messages.
"""

import time
from fastapi import APIRouter, HTTPException, Depends
from models import (
    AddMemoryRequest,
    SearchMemoryRequest,
    GetAllMemoriesRequest,
    UpdateMemoryRequest,
    DeleteMemoryRequest,
    GetMemoryHistoryRequest
)
from mem0_debug import set_mem0_request_context, reset_mem0_request_context
from dependencies import (
    memory,
    verify_api_key,
    logger,
    OBSERVABILITY_ENABLED,
    log_structured
)

router = APIRouter(prefix="/v1/memories", tags=["Memory Operations"])


@router.post("/add")
async def add_memory(
    request: AddMemoryRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Add memories from conversation messages
    
    Note: session_id is mapped to run_id for backward compatibility with v1.0.0
    """
    start_time = time.time()
    
    ctx_token = set_mem0_request_context(
        {
            "endpoint": "/v1/memories/add",
            "user_id": request.user_id,
            "agent_id": request.agent_id,
            "run_id": request.run_id or request.session_id,
            "infer": request.infer,
        }
    )

    try:
        # Convert Pydantic models to dicts
        messages = [msg.model_dump() for msg in request.messages]
        
        # Map legacy session_id to run_id (v1.0.0 compatibility)
        run_id = request.run_id or request.session_id
        
        # Build kwargs for memory.add - only include supported parameters
        kwargs = {}
        if request.user_id:
            kwargs["user_id"] = request.user_id
        if request.agent_id:
            kwargs["agent_id"] = request.agent_id
        if run_id:
            kwargs["run_id"] = run_id
        if request.metadata:
            kwargs["metadata"] = request.metadata
        # Deterministic lab option: infer=False stores raw messages
        kwargs["infer"] = request.infer
        if request.memory_type:
            kwargs["memory_type"] = request.memory_type
        if request.prompt:
            kwargs["prompt"] = request.prompt
        
        # Track OpenAI calls
        if OBSERVABILITY_ENABLED:
            log_structured(
                "info",
                "Starting memory.add operation",
                user_id=request.user_id,
                message_count=len(messages),
                has_metadata=bool(request.metadata)
            )
        
        result = memory.add(messages, **kwargs)
        
        # Log success
        if OBSERVABILITY_ENABLED:
            duration = time.time() - start_time
            log_structured(
                "info",
                "Memory.add completed",
                user_id=request.user_id,
                duration_ms=round(duration * 1000, 2),
                results_count=len(result) if isinstance(result, list) else 1
            )
        
        return {
            "status": "success",
            "data": result
        }
    except TypeError as e:
        logger.error(f"TypeError in memory.add: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Bad request for Memory.add(): {str(e)}")
    except Exception as e:
        if OBSERVABILITY_ENABLED:
            log_structured(
                "error",
                "Memory.add failed",
                user_id=request.user_id if hasattr(request, 'user_id') else None,
                error=str(e),
                duration_ms=round((time.time() - start_time) * 1000, 2)
            )
        logger.error(f"Error adding memory: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        reset_mem0_request_context(ctx_token)


@router.post("/search")
async def search_memory(
    request: SearchMemoryRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Search for relevant memories
    
    Note: session_id is mapped to run_id for backward compatibility with v1.0.0
    """
    try:
        # Map legacy session_id to run_id
        run_id = request.run_id or request.session_id
        
        kwargs = {"limit": request.limit}
        if request.user_id:
            kwargs["user_id"] = request.user_id
        if request.agent_id:
            kwargs["agent_id"] = request.agent_id
        if run_id:
            kwargs["run_id"] = run_id
        
        result = memory.search(query=request.query, **kwargs)
        
        return {
            "status": "success",
            "data": result
        }
    except Exception as e:
        logger.error(f"Error searching memory: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/get-all")
async def get_all_memories(
    request: GetAllMemoriesRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Get all memories for a user/agent/run
    
    Note: session_id is mapped to run_id for backward compatibility with v1.0.0
    """
    try:
        # Map legacy session_id to run_id
        run_id = request.run_id or request.session_id
        
        kwargs = {}
        if request.user_id:
            kwargs["user_id"] = request.user_id
        if request.agent_id:
            kwargs["agent_id"] = request.agent_id
        if run_id:
            kwargs["run_id"] = run_id
        
        result = memory.get_all(**kwargs)
        
        return {
            "status": "success",
            "data": result
        }
    except Exception as e:
        logger.error(f"Error getting all memories: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/update")
async def update_memory(
    request: UpdateMemoryRequest,
    api_key: str = Depends(verify_api_key)
):
    """Update a specific memory"""
    try:
        result = memory.update(memory_id=request.memory_id, data=request.data)
        
        return {
            "status": "success",
            "data": result
        }
    except Exception as e:
        logger.error(f"Error updating memory: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete")
async def delete_memory(
    request: DeleteMemoryRequest,
    api_key: str = Depends(verify_api_key)
):
    """Delete a specific memory"""
    try:
        memory.delete(memory_id=request.memory_id)
        
        return {
            "status": "success",
            "message": "Memory deleted successfully"
        }
    except Exception as e:
        logger.error(f"Error deleting memory: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/history")
async def get_memory_history(
    request: GetMemoryHistoryRequest,
    api_key: str = Depends(verify_api_key)
):
    """Get history of a specific memory"""
    try:
        result = memory.history(memory_id=request.memory_id)
        
        return {
            "status": "success",
            "data": result
        }
    except Exception as e:
        logger.error(f"Error getting memory history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/reset")
async def reset_memory(
    request: GetAllMemoriesRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Reset/delete all memories for a user/agent/run
    
    Note: session_id is mapped to run_id for backward compatibility with v1.0.0
    """
    try:
        # Map legacy session_id to run_id
        run_id = request.run_id or request.session_id
        
        kwargs = {}
        if request.user_id:
            kwargs["user_id"] = request.user_id
        if request.agent_id:
            kwargs["agent_id"] = request.agent_id
        if run_id:
            kwargs["run_id"] = run_id
        
        memory.reset(**kwargs)
        
        return {
            "status": "success",
            "message": "Memory reset successfully"
        }
    except Exception as e:
        logger.error(f"Error resetting memory: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

