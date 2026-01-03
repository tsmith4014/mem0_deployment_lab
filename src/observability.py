"""
Observability module for Mem0 API
Tracks requests, model usage (when available), metrics, and basic alerting.

How this file ties into the app:
- `src/middleware.py` records request metrics into `metrics_collector`.
- Routes can call `log_structured(...)` for consistent JSON logs.

Note on "cost":
- This lab can run on AWS Bedrock or OpenAI.
- Only OpenAI token/cost estimation is implemented today (see `OpenAITracker`).
"""

import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from collections import defaultdict
from threading import Lock

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)


class MetricsCollector:
    """Thread-safe metrics collection"""
    
    def __init__(self):
        self.lock = Lock()
        self.metrics = defaultdict(lambda: {
            'count': 0,
            'total_duration': 0.0,
            'errors': 0,
            'total_tokens': 0,
            'total_cost': 0.0,
            'users': set()  # Track unique users per endpoint
        })
        self.request_log = []
        self.max_log_size = 1000  # Keep last 1000 requests
        self.user_activity = defaultdict(lambda: {
            'add_count': 0,
            'search_count': 0,
            'update_count': 0,
            'delete_count': 0,
            'total_tokens': 0,
            'total_cost': 0.0,
            'first_seen': None,
            'last_seen': None
        })
        
    def record_request(self, endpoint: str, duration: float, success: bool, 
                      tokens: int = 0, cost: float = 0.0, error: Optional[str] = None,
                      metadata: Optional[Dict[str, Any]] = None):
        """Record a request with relevant metrics (filters health/metrics endpoints to reduce noise)."""
        # Filter out health checks and monitoring endpoints (teaching-friendly: focus on app usage)
        if endpoint in ["GET /health", "GET /health/detailed", "GET /metrics", "GET /alerts"]:
            return
        
        with self.lock:
            key = endpoint
            self.metrics[key]['count'] += 1
            self.metrics[key]['total_duration'] += duration
            self.metrics[key]['total_tokens'] += tokens
            self.metrics[key]['total_cost'] += cost
            
            if not success:
                self.metrics[key]['errors'] += 1
            
            # Track user activity (useful for multi-user demos and simple reporting)
            user_id = None
            if metadata:
                user_id = metadata.get('user_id')
                if user_id:
                    self.metrics[key]['users'].add(user_id)
                    
                    # Track per-user activity
                    now = datetime.utcnow().isoformat()
                    if self.user_activity[user_id]['first_seen'] is None:
                        self.user_activity[user_id]['first_seen'] = now
                    self.user_activity[user_id]['last_seen'] = now
                    self.user_activity[user_id]['total_tokens'] += tokens
                    self.user_activity[user_id]['total_cost'] += cost
                    
                    # Track action types
                    if 'add' in endpoint.lower():
                        self.user_activity[user_id]['add_count'] += 1
                    elif 'search' in endpoint.lower():
                        self.user_activity[user_id]['search_count'] += 1
                    elif 'update' in endpoint.lower():
                        self.user_activity[user_id]['update_count'] += 1
                    elif 'delete' in endpoint.lower():
                        self.user_activity[user_id]['delete_count'] += 1
            
            # Log entry
            log_entry = {
                'timestamp': datetime.utcnow().isoformat(),
                'endpoint': endpoint,
                'duration_ms': round(duration * 1000, 2),
                'success': success,
                'tokens': tokens,
                'cost_usd': round(cost, 6),
                'error': error,
                'metadata': metadata or {},
                'user_id': user_id  # Make user ID prominent
            }
            
            self.request_log.append(log_entry)
            
            # Trim log if needed
            if len(self.request_log) > self.max_log_size:
                self.request_log = self.request_log[-self.max_log_size:]
            
            # Structured log output (only for user activity)
            if user_id or 'admin' in endpoint.lower():  # Log user actions and admin queries
                logger.info(json.dumps(log_entry))
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics snapshot (user-focused)."""
        with self.lock:
            summary = {}
            for endpoint, data in self.metrics.items():
                avg_duration = (data['total_duration'] / data['count'] 
                               if data['count'] > 0 else 0)
                success_rate = ((data['count'] - data['errors']) / data['count'] * 100 
                               if data['count'] > 0 else 0)
                
                summary[endpoint] = {
                    'total_requests': data['count'],
                    'total_errors': data['errors'],
                    'success_rate_pct': round(success_rate, 2),
                    'avg_duration_ms': round(avg_duration * 1000, 2),
                    'total_tokens': data['total_tokens'],
                    'total_cost_usd': round(data['total_cost'], 4),
                    'unique_users': len(data['users'])
                }
            
            # Convert user activity for serialization (sets can't be JSON-encoded)
            user_summary = {}
            for user_id, activity in self.user_activity.items():
                user_summary[user_id] = {
                    'add_count': activity['add_count'],
                    'search_count': activity['search_count'],
                    'update_count': activity['update_count'],
                    'delete_count': activity['delete_count'],
                    'total_tokens': activity['total_tokens'],
                    'total_cost_usd': round(activity['total_cost'], 4),
                    'first_seen': activity['first_seen'],
                    'last_seen': activity['last_seen']
                }
            
            # Get only user-relevant recent requests (filter out health checks)
            user_requests = [r for r in self.request_log[-50:] if r.get('user_id')]
            
            return {
                'summary': summary,
                'user_activity': user_summary,
                'total_unique_users': len(self.user_activity),
                # Keep both keys for compatibility with earlier code.
                'recent_user_requests': user_requests,  # Only user actions, no health checks
                'recent_requests': user_requests,
                # "model_usage" is generic; OpenAI-specific cost tracking is optional.
                'model_usage': {
                    'total_cost_usd': round(sum(d['total_cost'] for d in self.metrics.values()), 4),
                    'total_tokens': sum(d['total_tokens'] for d in self.metrics.values())
                },
                'openai_costs': {
                    'total_cost_usd': round(sum(d['total_cost'] for d in self.metrics.values()), 4),
                    'total_tokens': sum(d['total_tokens'] for d in self.metrics.values())
                },
            }
    
    def get_recent_errors(self, limit: int = 20) -> list:
        """Get recent errors for alerting"""
        with self.lock:
            errors = [entry for entry in self.request_log if not entry['success']]
            return errors[-limit:]
    
    def check_alert_conditions(self) -> list:
        """Check if any alert conditions are met"""
        alerts = []
        
        with self.lock:
            for endpoint, data in self.metrics.items():
                if data['count'] < 10:
                    continue  # Need minimum sample size
                
                error_rate = (data['errors'] / data['count']) * 100
                
                # Alert if error rate > 20%
                if error_rate > 20:
                    alerts.append({
                        'type': 'high_error_rate',
                        'endpoint': endpoint,
                        'error_rate': round(error_rate, 2),
                        'threshold': 20,
                        'severity': 'high'
                    })
                
                # Alert if average duration > 5 seconds
                avg_duration = data['total_duration'] / data['count']
                if avg_duration > 5.0:
                    alerts.append({
                        'type': 'slow_response',
                        'endpoint': endpoint,
                        'avg_duration_sec': round(avg_duration, 2),
                        'threshold': 5.0,
                        'severity': 'medium'
                    })
                
                # Alert if cost is high (> $1 in metrics period)
                if data['total_cost'] > 1.0:
                    alerts.append({
                        'type': 'high_cost',
                        'endpoint': endpoint,
                        'total_cost_usd': round(data['total_cost'], 2),
                        'threshold': 1.0,
                        'severity': 'medium'
                    })
        
        return alerts


class OpenAITracker:
    """Track OpenAI API calls for cost and performance monitoring"""
    
    # Pricing per 1M tokens (as of Nov 2024)
    PRICING = {
        'gpt-4o-mini': {
            'input': 0.150,   # per 1M input tokens
            'output': 0.600   # per 1M output tokens
        },
        'gpt-4o': {
            'input': 2.50,
            'output': 10.00
        },
        'text-embedding-3-small': {
            'input': 0.020,
            'output': 0.0
        },
        'text-embedding-3-large': {
            'input': 0.130,
            'output': 0.0
        }
    }
    
    @classmethod
    def calculate_cost(cls, model: str, input_tokens: int, output_tokens: int = 0) -> float:
        """Calculate cost for OpenAI API call"""
        pricing = cls.PRICING.get(model, cls.PRICING['gpt-4o-mini'])
        
        input_cost = (input_tokens / 1_000_000) * pricing['input']
        output_cost = (output_tokens / 1_000_000) * pricing['output']
        
        return input_cost + output_cost
    
    @classmethod
    def log_openai_call(cls, operation: str, model: str, input_tokens: int, 
                       output_tokens: int, duration: float, success: bool, 
                       error: Optional[str] = None):
        """Log an OpenAI API call with full details"""
        cost = cls.calculate_cost(model, input_tokens, output_tokens)
        
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'service': 'openai',
            'operation': operation,
            'model': model,
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'total_tokens': input_tokens + output_tokens,
            'duration_ms': round(duration * 1000, 2),
            'cost_usd': round(cost, 6),
            'success': success,
            'error': error
        }
        
        logger.info(json.dumps(log_entry))
        
        return cost, input_tokens + output_tokens


class AlertManager:
    """Manage basic alerts (in-memory)."""
    
    def __init__(self):
        self.alert_history = []
        self.max_history = 100
    
    def record_alert(self, alert: Dict[str, Any]):
        """Record an alert (for now just logging)."""
        alert['timestamp'] = datetime.utcnow().isoformat()
        alert['acknowledged'] = False
        
        self.alert_history.append(alert)
        
        # Trim history
        if len(self.alert_history) > self.max_history:
            self.alert_history = self.alert_history[-self.max_history:]
        
        # Log alert
        logger.warning(json.dumps({
            'type': 'ALERT',
            'alert': alert
        }))
        
    
    def get_active_alerts(self) -> list:
        """Get unacknowledged alerts"""
        return [a for a in self.alert_history if not a.get('acknowledged', False)]


# Global instances
metrics_collector = MetricsCollector()
alert_manager = AlertManager()


def log_structured(level: str, message: str, **kwargs):
    """Log a structured message"""
    log_entry = {
        'timestamp': datetime.utcnow().isoformat(),
        'level': level.upper(),
        'message': message,
        **kwargs
    }
    
    if level.lower() == 'error':
        logger.error(json.dumps(log_entry))
    elif level.lower() == 'warning':
        logger.warning(json.dumps(log_entry))
    else:
        logger.info(json.dumps(log_entry))

