"""
FastAPI middleware for request tracking and observability

What is middleware?
Middleware runs "around" every request/response. It's a great place to add
cross-cutting concerns like logging, metrics, tracing, and auth.

How this file ties into the app:
- `src/app.py` conditionally installs `ObservabilityMiddleware` when observability is enabled.
- This middleware records request-level metrics into `metrics_collector` (see `src/observability.py`).
"""

import time
import json
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from typing import Callable
from observability import metrics_collector, log_structured


class ObservabilityMiddleware(BaseHTTPMiddleware):
    """Middleware to track all API requests"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Start timing
        start_time = time.time()
        
        # Extract request details
        path = request.url.path
        method = request.method
        client_ip = request.client.host if request.client else "unknown"
        
        # Try to extract user_id from request body (useful for per-user metrics)
        user_id = None
        try:
            if method in ["POST", "PUT", "DELETE"] and request.headers.get("content-type", "").startswith("application/json"):
                # Store the original body
                body = await request.body()
                # Parse JSON to extract user_id
                try:
                    body_json = json.loads(body) if body else {}
                    user_id = body_json.get("user_id")
                except (json.JSONDecodeError, TypeError):
                    pass
                # Create new request with body intact
                async def receive():
                    return {"type": "http.request", "body": body}
                request._receive = receive
        except Exception:
            pass
        
        # Log incoming request (keep logs focused on user/admin activity)
        if user_id or 'admin' in path:
            log_structured(
                "info",
                f"Incoming {method} request",
                path=path,
                method=method,
                client_ip=client_ip,
                user_agent=request.headers.get("user-agent", "unknown"),
                user_id=user_id
            )
        
        # Process request
        success = True
        error_msg = None
        status_code = 200
        
        try:
            response = await call_next(request)
            status_code = response.status_code
            success = 200 <= status_code < 400
            
            return response
            
        except Exception as e:
            success = False
            status_code = 500
            error_msg = str(e)
            log_structured(
                "error",
                f"Request failed: {error_msg}",
                path=path,
                method=method,
                error=error_msg,
                user_id=user_id
            )
            raise
            
        finally:
            # Calculate duration
            duration = time.time() - start_time
            
            # Record metrics (include user_id when present for per-user reporting)
            endpoint = f"{method} {path}"
            metadata = {
                'method': method,
                'path': path,
                'status_code': status_code,
                'client_ip': client_ip
            }
            if user_id:
                metadata['user_id'] = user_id
            
            metrics_collector.record_request(
                endpoint=endpoint,
                duration=duration,
                success=success,
                error=error_msg,
                metadata=metadata
            )
            
            # Log response (keep logs focused on user/admin activity)
            if user_id or 'admin' in path:
                log_structured(
                    "info" if success else "error",
                    f"Request completed: {method} {path}",
                    path=path,
                    method=method,
                    status_code=status_code,
                    duration_ms=round(duration * 1000, 2),
                    success=success,
                    user_id=user_id
                )

