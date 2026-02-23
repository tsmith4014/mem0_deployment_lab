"""
Admin and Business Intelligence routes

These endpoints are optional "extras" for instructors/admins:
- system stats (basic operational overview)
- user activity summaries
- database health

Note: This repo intentionally does NOT include Slack integration. That can be a
stretch goal later (wire up a webhook and add authenticated endpoints).
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from dependencies import (
    verify_admin_key,
    logger,
    BI_ENABLED,
    bi,
    key_manager
)


class KeyRotateRequest(BaseModel):
    """Request body for key rotation"""
    rotate_api_key: bool = True
    rotate_admin_key: bool = True


class KeyRotateResponse(BaseModel):
    """Response from key rotation"""
    status: str
    message: str
    api_key: Optional[str] = None
    admin_api_key: Optional[str] = None
    warning: Optional[str] = None

router = APIRouter(prefix="/admin", tags=["Admin & Business Intelligence"])


@router.post("/keys/rotate", response_model=KeyRotateResponse)
async def rotate_keys(
    request: KeyRotateRequest = KeyRotateRequest(),
    admin_key: str = Depends(verify_admin_key)
):
    """
    Rotate API keys (Admin only)

    Generates new random keys and updates AWS SSM Parameter Store.
    Old keys will no longer work immediately after rotation.

    **IMPORTANT:** Save the returned keys - they won't be shown again!

    Requires X-Admin-Key header.

    Args:
        rotate_api_key: Whether to rotate the API key (default: true)
        rotate_admin_key: Whether to rotate the Admin API key (default: true)

    Returns:
        New key values. Store these securely!
    """
    try:
        if not request.rotate_api_key and not request.rotate_admin_key:
            raise HTTPException(
                status_code=400,
                detail="At least one key must be rotated"
            )

        new_keys = key_manager.rotate_keys(
            rotate_api_key=request.rotate_api_key,
            rotate_admin_key=request.rotate_admin_key
        )

        # Build response
        response = KeyRotateResponse(
            status="success",
            message="Keys rotated successfully",
            api_key=new_keys.get("api_key"),
            admin_api_key=new_keys.get("admin_api_key")
        )

        # Add warning if SSM prefix is not configured
        if not key_manager.ssm_prefix:
            response.warning = (
                "SSM_PREFIX not configured - keys updated in memory only. "
                "Keys will reset to original values on container restart."
            )

        logger.info(f"Keys rotated: api_key={request.rotate_api_key}, admin_key={request.rotate_admin_key}")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error rotating keys: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Key rotation failed: {str(e)}")


@router.get("/stats")
async def get_system_stats(admin_key: str = Depends(verify_admin_key)):
    """
    Get system overview stats (admin only)
    Requires X-Admin-Key header
    """
    if not BI_ENABLED:
        return {"error": "Business Intelligence not enabled"}
    
    try:
        stats = bi.get_system_overview()
        return {
            "status": "success",
            "data": stats
        }
    except Exception as e:
        logger.error(f"Error getting system stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users")
async def get_user_activity(
    days: int = 7,
    admin_key: str = Depends(verify_admin_key)
):
    """Get user activity report (admin only)"""
    if not BI_ENABLED:
        return {"error": "Business Intelligence not enabled"}
    
    try:
        report = bi.get_user_activity_report(days=days)
        return {
            "status": "success",
            "data": report
        }
    except Exception as e:
        logger.error(f"Error getting user activity: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user/{user_id}")
async def get_user_report(
    user_id: str,
    admin_key: str = Depends(verify_admin_key)
):
    """Get detailed report for a specific user (admin only)"""
    if not BI_ENABLED:
        return {"error": "Business Intelligence not enabled"}
    
    try:
        report = bi.get_user_deep_dive(user_id)
        return {
            "status": "success",
            "data": report
        }
    except Exception as e:
        logger.error(f"Error getting user report: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/common-memories")
async def get_common_memories(
    limit: int = 20,
    admin_key: str = Depends(verify_admin_key)
):
    """Get common memory patterns across all users"""
    if not BI_ENABLED:
        return {"error": "Business Intelligence not enabled"}
    
    try:
        analysis = bi.get_common_memories_analysis(limit=limit)
        return {
            "status": "success",
            "data": analysis
        }
    except Exception as e:
        logger.error(f"Error getting common memories: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/database-health")
async def get_database_health(admin_key: str = Depends(verify_admin_key)):
    """Get Qdrant database health metrics"""
    if not BI_ENABLED:
        return {"error": "Business Intelligence not enabled"}
    
    try:
        health = bi.get_database_health()
        return {
            "status": "success",
            "data": health
        }
    except Exception as e:
        logger.error(f"Error getting database health: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/all-memories")
async def get_all_memories_across_users(
    limit: int = 100,
    admin_key: str = Depends(verify_admin_key)
):
    """
    Get ALL memories across ALL users (Admin only)
    
    This queries Qdrant directly to retrieve memories without user filtering.
    Perfect for business owners who want to see everything.
    
    Args:
        limit: Maximum number of memories to return (default: 100, max: 1000)
    """
    try:
        import requests
        import os
        
        # Cap the limit
        limit = min(limit, 1000)
        
        # Query Qdrant directly
        qdrant_host = os.getenv("QDRANT_HOST", "mem0_qdrant")
        qdrant_port = os.getenv("QDRANT_PORT", "6333")
        qdrant_url = f"http://{qdrant_host}:{qdrant_port}"
        
        # Scroll through all points in the mem0 collection
        response = requests.post(
            f"{qdrant_url}/collections/mem0/points/scroll",
            json={
                "limit": limit,
                "with_payload": True,
                "with_vector": False
            }
        )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=500,
                detail=f"Qdrant error: {response.text}"
            )
        
        data = response.json()
        points = data.get("result", {}).get("points", [])
        
        # Format the results
        memories = []
        for point in points:
            payload = point.get("payload", {})
            memories.append({
                "id": point.get("id"),
                "memory": payload.get("data", ""),
                "user_id": payload.get("user_id"),
                "agent_id": payload.get("agent_id"),
                "run_id": payload.get("run_id"),
                "created_at": payload.get("created_at"),
                "updated_at": payload.get("updated_at"),
                "metadata": payload.get("metadata", {})
            })
        
        return {
            "status": "success",
            "data": {
                "total": len(memories),
                "limit": limit,
                "memories": memories
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting all memories: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

