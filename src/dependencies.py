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
    llm_provider = os.getenv("LLM_PROVIDER", "openai").strip()
    embedder_provider = os.getenv("EMBEDDER_PROVIDER", "openai").strip()

    openai_api_key = os.getenv("OPENAI_API_KEY")

    # Fail fast only when OpenAI is actually required
    if (llm_provider == "openai" or embedder_provider == "openai") and not openai_api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is required when LLM_PROVIDER=openai or EMBEDDER_PROVIDER=openai. "
            "If you want an AWS-only track, set LLM_PROVIDER=aws_bedrock and EMBEDDER_PROVIDER=aws_bedrock."
        )

    return {
        "llm": {
            "provider": llm_provider,
            "config": (
                {
                    "model": os.getenv("LLM_MODEL", "gpt-4o-mini"),
                    "temperature": float(os.getenv("LLM_TEMPERATURE", "0.7")),
                    "api_key": openai_api_key,
                }
                if llm_provider == "openai"
                else {
                    # AWS Bedrock LLM (optional AWS-only track)
                    #
                    # IMPORTANT: mem0ai currently maps aws_bedrock -> AWSBedrockLLM with BaseLlmConfig.
                    # So we must only pass BaseLlmConfig-compatible keys here.
                    #
                    # AWS region/credentials are read from environment variables (AWS_REGION, IAM role, etc.)
                    "model": os.getenv("LLM_MODEL", ""),
                    "temperature": float(os.getenv("LLM_TEMPERATURE", "0.7")),
                    "max_tokens": int(os.getenv("LLM_MAX_TOKENS", "2000")),
                    "top_p": float(os.getenv("LLM_TOP_P", "0.9")),
                    "top_k": int(os.getenv("LLM_TOP_K", "1")),
                }
            ),
        },
        "embedder": {
            "provider": embedder_provider,
            "config": (
                {
                    # OpenAI embeddings (default)
                    "model": os.getenv("EMBEDDER_MODEL", "text-embedding-3-small"),
                    "api_key": openai_api_key,
                    "openai_base_url": os.getenv("OPENAI_BASE_URL") or None,
                }
                if embedder_provider == "openai"
                else {
                    # AWS Bedrock embeddings (Titan recommended)
                    "model": os.getenv("EMBEDDER_MODEL", "amazon.titan-embed-text-v1"),
                    "aws_region": os.getenv("AWS_REGION", ""),
                    "aws_access_key_id": os.getenv("AWS_ACCESS_KEY_ID", "") or None,
                    "aws_secret_access_key": os.getenv("AWS_SECRET_ACCESS_KEY", "") or None,
                }
            ),
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

