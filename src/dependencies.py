"""
Shared dependencies for the Mem0 API
Initialization and security functions
"""

import os
import logging
from mem0 import Memory
from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'  # Structured logging format
)
logger = logging.getLogger(__name__)

# API Key security
API_KEY = os.getenv("API_KEY", "your_secure_api_key_here")
ADMIN_API_KEY = os.getenv("ADMIN_API_KEY", API_KEY)
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=True)
admin_key_header = APIKeyHeader(name="X-Admin-Key", auto_error=True)


async def verify_api_key(api_key: str = Security(api_key_header)):
    """Verify API key for memory operations"""
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return api_key


async def verify_admin_key(admin_key: str = Security(admin_key_header)):
    """Verify admin key for BI/admin operations"""
    if admin_key != ADMIN_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid Admin Key")
    return admin_key


# Mem0 configuration
def get_mem0_config():
    """Build Mem0 configuration from environment"""
    return {
        "llm": {
            "provider": "openai",
            "config": {
                "model": os.getenv("LLM_MODEL", "gpt-4o-mini"),
                "temperature": float(os.getenv("LLM_TEMPERATURE", "0.7")),
                "api_key": os.getenv("OPENAI_API_KEY")
            }
        },
        "vector_store": {
            "provider": "qdrant",
            "config": {
                "url": f"http://{os.getenv('QDRANT_HOST', 'localhost')}:{os.getenv('QDRANT_PORT', '6333')}",
                "api_key": os.getenv("QDRANT_API_KEY") if os.getenv("QDRANT_API_KEY") else None
            }
        }
    }


# Initialize Memory instance (singleton)
memory = Memory.from_config(get_mem0_config())
logger.info("Mem0 initialized successfully")

# Observability imports
try:
    from observability import (
        metrics_collector, 
        alert_manager, 
        log_structured,
        OpenAITracker
    )
    from business_intelligence import BusinessIntelligence
    OBSERVABILITY_ENABLED = True
    BI_ENABLED = True
    bi = BusinessIntelligence(memory)
    logger.info("Observability and BI modules loaded")
except ImportError as e:
    OBSERVABILITY_ENABLED = False
    BI_ENABLED = False
    metrics_collector = None
    alert_manager = None
    log_structured = None
    bi = None
    logger.warning(f"Observability/BI modules not found: {e}")

