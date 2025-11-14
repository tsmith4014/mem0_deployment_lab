"""
Wrapper for OpenAI calls to track tokens, cost, and performance
This wraps/monkeypatches mem0's OpenAI usage for observability
"""

import time
from typing import Any, Optional
from functools import wraps
from observability import OpenAITracker, log_structured, metrics_collector


def track_openai_call(operation: str):
    """Decorator to track OpenAI API calls"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            success = True
            error = None
            tokens = 0
            cost = 0.0
            model = "unknown"
            
            try:
                result = func(*args, **kwargs)
                
                # Try to extract token usage from result
                if hasattr(result, 'usage'):
                    usage = result.usage
                    input_tokens = getattr(usage, 'prompt_tokens', 0)
                    output_tokens = getattr(usage, 'completion_tokens', 0)
                    tokens = input_tokens + output_tokens
                    model = getattr(result, 'model', 'unknown')
                    
                    # Calculate cost
                    cost, _ = OpenAITracker.log_openai_call(
                        operation=operation,
                        model=model,
                        input_tokens=input_tokens,
                        output_tokens=output_tokens,
                        duration=time.time() - start_time,
                        success=True,
                        error=None
                    )
                
                return result
                
            except Exception as e:
                success = False
                error = str(e)
                log_structured(
                    "error",
                    f"OpenAI call failed: {operation}",
                    operation=operation,
                    error=error
                )
                raise
                
            finally:
                duration = time.time() - start_time
                
                # Record in metrics collector
                metrics_collector.record_request(
                    endpoint=f"openai.{operation}",
                    duration=duration,
                    success=success,
                    tokens=tokens,
                    cost=cost,
                    error=error,
                    metadata={'model': model, 'operation': operation}
                )
        
        return wrapper
    return decorator


class OpenAICallLogger:
    """Context manager for tracking OpenAI calls in mem0 operations"""
    
    def __init__(self, operation: str, model: str = "gpt-4o-mini"):
        self.operation = operation
        self.model = model
        self.start_time = None
        
    def __enter__(self):
        self.start_time = time.time()
        log_structured(
            "info",
            f"Starting OpenAI operation: {self.operation}",
            operation=self.operation,
            model=self.model
        )
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        success = exc_type is None
        error = str(exc_val) if exc_val else None
        
        if not success:
            log_structured(
                "error",
                f"OpenAI operation failed: {self.operation}",
                operation=self.operation,
                error=error,
                duration_ms=round(duration * 1000, 2)
            )
        else:
            log_structured(
                "info",
                f"OpenAI operation completed: {self.operation}",
                operation=self.operation,
                duration_ms=round(duration * 1000, 2)
            )
        
        return False  # Don't suppress exceptions
    
    def log_tokens(self, input_tokens: int, output_tokens: int):
        """Log token usage for this operation"""
        cost, total_tokens = OpenAITracker.log_openai_call(
            operation=self.operation,
            model=self.model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            duration=time.time() - self.start_time,
            success=True
        )
        
        metrics_collector.record_request(
            endpoint=f"openai.{self.operation}",
            duration=time.time() - self.start_time,
            success=True,
            tokens=total_tokens,
            cost=cost,
            metadata={'model': self.model}
        )

