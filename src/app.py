"""
Self-hosted Mem0 API Server
Clean, modular FastAPI application with observability

This is the FastAPI entrypoint:
- Registers routers (`/v1/memories/*`, `/admin/*`, `/health`, etc.)
- Adds optional observability middleware
- Configures OpenAPI/Swagger to require API keys on the right routes
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dependencies import logger, OBSERVABILITY_ENABLED

# Import observability middleware
if OBSERVABILITY_ENABLED:
    from middleware import ObservabilityMiddleware

# Import route modules
from routes import memory_router, admin_router, health_router, demo_router

# Initialize FastAPI app with proper OpenAPI security configuration
app = FastAPI(
    title="Mem0 Self-Hosted API",
    description="Self-hosted Mem0 memory layer with vector database and observability",
    version="1.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    swagger_ui_parameters={
        "persistAuthorization": True,  # Remember authorization between page refreshes
    }
)

# Configure OpenAPI security schemes
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    from fastapi.openapi.utils import get_openapi
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # Define both security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "X-API-Key": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key",
            "description": "API Key for Memory Operations (all /v1/memories/* endpoints)"
        },
        "X-Admin-Key": {
            "type": "apiKey",
            "in": "header",
            "name": "X-Admin-Key",
            "description": "Admin Key for Business Intelligence and Admin Operations (all /admin/* endpoints)"
        }
    }
    
    # Apply security to each endpoint based on its path
    if "paths" in openapi_schema:
        for path, path_item in openapi_schema["paths"].items():
            for method, operation in path_item.items():
                if method.upper() in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
                    # All v1 endpoints require X-API-Key (memory + demo seed routes)
                    if path.startswith("/v1/"):
                        operation["security"] = [{"X-API-Key": []}]
                    # Admin operations need X-Admin-Key
                    elif path.startswith("/admin/"):
                        operation["security"] = [{"X-Admin-Key": []}]
                    # Health/metrics don't need auth (remove any existing security)
                    elif path in ["/", "/health", "/health/detailed", "/metrics", "/alerts"]:
                        operation["security"] = []
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Add observability middleware (FIRST, before CORS)
if OBSERVABILITY_ENABLED:
    app.add_middleware(ObservabilityMiddleware)
    logger.info("Observability middleware enabled")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register route modules
app.include_router(health_router)        # Health checks, metrics, alerts
app.include_router(memory_router)        # Memory CRUD operations
app.include_router(admin_router)         # Business intelligence, admin ops
app.include_router(demo_router)          # Demo seed endpoints for class

logger.info("All route modules registered")


if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    
    logger.info("=" * 60)
    logger.info("Starting Mem0 API Server")
    logger.info("=" * 60)
    logger.info(f"Host: {host}")
    logger.info(f"Port: {port}")
    
    if OBSERVABILITY_ENABLED:
        logger.info(f"Metrics: http://{host}:{port}/metrics")
        logger.info(f"Alerts: http://{host}:{port}/alerts")
        logger.info(f"Health: http://{host}:{port}/health/detailed")
    
    logger.info(f"Docs: http://{host}:{port}/docs")
    logger.info("=" * 60)
    
    uvicorn.run(
        "app:app",
        host=host,
        port=port,
        reload=False,
        log_level="info"
    )
