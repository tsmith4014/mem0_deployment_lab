"""
Health and monitoring routes
Health checks, metrics, and alerts

How this file ties into the app:
- Imported and registered in `src/app.py`
- Provides unauthenticated endpoints useful for verification and demos:
  - `/health` for a simple uptime check
  - `/metrics` and `/alerts` when observability is enabled
"""

from fastapi import APIRouter, HTTPException
from dependencies import (
    logger,
    OBSERVABILITY_ENABLED,
    metrics_collector,
    alert_manager
)

router = APIRouter(tags=["Health & Monitoring"])


@router.get("/")
async def root():
    """Root endpoint - quick status check"""
    return {
        "status": "online",
        "service": "Mem0 Self-Hosted API",
        "version": "1.1.0"
    }


@router.get("/health")
async def health_check():
    """Basic health check"""
    try:
        return {
            "status": "healthy",
            "components": {
                "api": "operational",
                "memory": "operational",
                "vector_store": "operational"
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")


@router.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check with metrics summary"""
    try:
        health_data = {
            "status": "healthy",
            "components": {
                "api": "operational",
                "memory": "operational",
                "vector_store": "operational"
            }
        }
        
        if OBSERVABILITY_ENABLED:
            metrics = metrics_collector.get_metrics()
            health_data["metrics_summary"] = {
                "total_requests": sum(m["total_requests"] for m in metrics["summary"].values()),
                "total_errors": sum(m["total_errors"] for m in metrics["summary"].values()),
                "observability": "enabled"
            }
        
        return health_data
        
    except Exception as e:
        logger.error(f"Detailed health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")


@router.get("/metrics")
async def get_metrics():
    """
    Get API metrics and performance data
    No authentication required for monitoring
    """
    if not OBSERVABILITY_ENABLED:
        return {"error": "Observability not enabled"}
    
    try:
        metrics = metrics_collector.get_metrics()
        return {
            "status": "success",
            "data": metrics
        }
    except Exception as e:
        logger.error(f"Error getting metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/alerts")
async def get_alerts():
    """
    Get active alerts
    No authentication required for monitoring
    """
    if not OBSERVABILITY_ENABLED:
        return {"error": "Observability not enabled"}
    
    try:
        # Check for new alert conditions
        alerts = metrics_collector.check_alert_conditions()
        
        # Record any new alerts
        for alert in alerts:
            alert_manager.record_alert(alert)
        
        # Return active alerts
        active_alerts = alert_manager.get_active_alerts()
        
        return {
            "status": "success",
            "data": {
                "active_alerts": active_alerts,
                "recent_errors": metrics_collector.get_recent_errors(limit=10)
            }
        }
    except Exception as e:
        logger.error(f"Error getting alerts: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

