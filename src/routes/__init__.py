"""
Routes package for Mem0 API
Clean separation of concerns: Memory ops, Admin ops, Health checks
"""

from .memory_routes import router as memory_router
from .admin_routes import router as admin_router
from .health_routes import router as health_router

__all__ = ['memory_router', 'admin_router', 'health_router']

