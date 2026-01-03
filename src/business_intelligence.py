"""
Business Intelligence module for Mem0 Stack

Purpose:
- Provide simple, instructor-friendly analytics on top of stored memories and API usage.
- Power `/admin/*` endpoints for demos (admin-only).

Teaching note:
This module uses lightweight heuristics (simple keyword matching) so students can
read and modify it easily. You can swap the theme by changing the keyword lists.
"""

import os
import requests
from typing import Dict, Any, List
from datetime import datetime
from collections import Counter, defaultdict
from mem0 import Memory
from observability import metrics_collector, log_structured


class BusinessIntelligence:
    """Generate business intelligence reports from Mem0 data"""
    
    def __init__(self, memory: Memory):
        self.memory = memory
    
    def get_system_overview(self) -> Dict[str, Any]:
        """Get high-level system statistics"""
        try:
            # Get metrics from observability
            metrics = metrics_collector.get_metrics()
            
            # Calculate totals
            summary = metrics.get('summary', {})
            total_requests = sum(m.get('total_requests', 0) for m in summary.values())
            total_errors = sum(m.get('total_errors', 0) for m in summary.values())
            total_tokens = sum(m.get('total_tokens', 0) for m in summary.values())
            total_cost = sum(m.get('total_cost_usd', 0) for m in summary.values())
            
            success_rate = ((total_requests - total_errors) / total_requests * 100 
                           if total_requests > 0 else 0)
            
            return {
                'total_api_requests': total_requests,
                'total_errors': total_errors,
                'success_rate_pct': round(success_rate, 2),
                'total_model_tokens': total_tokens,
                'total_cost_usd': round(total_cost, 4),
                'estimated_monthly_cost': round(total_cost * 30, 2),  # Rough estimate
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            log_structured("error", "Failed to get system overview", error=str(e))
            return {'error': str(e)}
    
    def get_user_activity_report(self, days: int = 7) -> Dict[str, Any]:
        """Get user activity statistics"""
        try:
            # Get recent requests from metrics
            metrics = metrics_collector.get_metrics()
            recent = metrics.get('recent_user_requests') or metrics.get('recent_requests', [])
            
            # Analyze user activity
            user_activity = defaultdict(lambda: {
                'request_count': 0,
                'memory_adds': 0,
                'searches': 0,
                'total_tokens': 0,
                'total_cost': 0.0,
                'last_active': None
            })
            
            for req in recent:
                metadata = req.get('metadata', {})
                user_id = req.get('user_id') or metadata.get('user_id')
                
                if not user_id:
                    continue
                
                user_activity[user_id]['request_count'] += 1
                user_activity[user_id]['total_tokens'] += req.get('tokens', 0)
                user_activity[user_id]['total_cost'] += req.get('cost_usd', 0)
                user_activity[user_id]['last_active'] = req.get('timestamp')
                
                endpoint = req.get('endpoint', '')
                if 'add' in endpoint:
                    user_activity[user_id]['memory_adds'] += 1
                elif 'search' in endpoint:
                    user_activity[user_id]['searches'] += 1
            
            # Sort by activity
            sorted_users = sorted(
                user_activity.items(),
                key=lambda x: x[1]['request_count'],
                reverse=True
            )
            
            return {
                'total_active_users': len(user_activity),
                'top_users': [
                    {
                        'user_id': user_id,
                        **stats
                    }
                    for user_id, stats in sorted_users[:10]
                ],
                'total_memory_adds': sum(u['memory_adds'] for u in user_activity.values()),
                'total_searches': sum(u['searches'] for u in user_activity.values()),
                'report_period_days': days,
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            log_structured("error", "Failed to get user activity", error=str(e))
            return {'error': str(e)}
    
    def get_common_memories_analysis(self, limit: int = 20) -> Dict[str, Any]:
        """Analyze common memory patterns across all users by querying Qdrant"""
        try:
            # Query Qdrant directly to get all memory points
            qdrant_url = f"http://{os.getenv('QDRANT_HOST', 'localhost')}:{os.getenv('QDRANT_PORT', '6333')}"
            
            # Scroll through all points in the mem0 collection
            response = requests.post(
                f"{qdrant_url}/collections/mem0/points/scroll",
                json={
                    "limit": 1000,  # Get up to 1000 memories
                    "with_payload": True,
                    "with_vector": False
                }
            )
            
            if response.status_code != 200:
                return {'error': f'Failed to query Qdrant: {response.status_code}'}
            
            data = response.json()
            points = data.get('result', {}).get('points', [])
            
            if not points:
                return {
                    'analysis_type': 'common_memory_patterns',
                    'total_memories': 0,
                    'message': 'No memories found in database',
                    'timestamp': datetime.utcnow().isoformat()
                }
            
            # Analyze actual memory data (simple keyword matching to keep the lab approachable)
            categories = Counter()
            topics = Counter()
            total_users = set()
            
            for point in points:
                payload = point.get('payload', {})
                memory_text = payload.get('data', '')
                user_id = payload.get('user_id')
                metadata = payload.get('metadata', {})
                
                if user_id:
                    total_users.add(user_id)
                
                # Extract metadata categories
                mem_type = metadata.get('type') if isinstance(metadata, dict) else None
                if mem_type:
                    categories[mem_type] += 1
                
                text_lower = memory_text.lower()

                # DevOps / cloud topics (fun + realistic for a Cloud Ops bootcamp)
                if 'kubernetes' in text_lower or 'k8s' in text_lower:
                    topics['Kubernetes'] += 1
                if 'terraform' in text_lower:
                    topics['Terraform'] += 1
                if 'docker' in text_lower:
                    topics['Docker'] += 1
                if 'aws' in text_lower:
                    topics['AWS'] += 1
                if 'python' in text_lower:
                    topics['Python'] += 1
                if 'linux' in text_lower:
                    topics['Linux'] += 1

                # Light "fun" topics that show personalization value
                if 'coffee' in text_lower:
                    topics['Coffee'] += 1
                if 'podcast' in text_lower:
                    topics['Podcasts'] += 1
                if 'hike' in text_lower or 'hiking' in text_lower:
                    topics['Hiking'] += 1
                if 'd&d' in text_lower or 'dnd' in text_lower:
                    topics['D&D'] += 1
            
            total_memories = len(points)
            
            # Build patterns from actual data
            patterns = []
            for pattern, count in topics.most_common(10):
                patterns.append({
                    'pattern': pattern,
                    'occurrence_count': count,
                    'percentage': round((count / total_memories) * 100, 1),
                    'category': 'topic'
                })
            
            # Generate insights from actual data
            insights = []
            if topics.get('Kubernetes', 0) >= 5:
                insights.append(f"Kubernetes is a frequent topic ({topics['Kubernetes']} mentions) — good candidate for a review session.")
            if topics.get('Terraform', 0) >= 5:
                insights.append(f"Terraform is a frequent topic ({topics['Terraform']} mentions) — consider an IaC lab extension.")
            
            return {
                'analysis_type': 'common_memory_patterns',
                'total_memories_analyzed': total_memories,
                'total_unique_users': len(total_users),
                'memory_type_breakdown': dict(categories),
                'common_patterns': patterns,
                'insights': insights if insights else ['Insufficient data for insights - need more memories'],
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            log_structured("error", "Failed to analyze common memories", error=str(e))
            return {'error': str(e)}
    
    def get_user_deep_dive(self, user_id: str) -> Dict[str, Any]:
        """Get detailed report for a specific user"""
        try:
            # Get all memories for user
            all_memories = self.memory.get_all(user_id=user_id)
            
            if isinstance(all_memories, dict):
                memories = all_memories.get('results', all_memories)
            else:
                memories = all_memories if all_memories else []
            
            # Analyze memories
            memory_types = Counter()
            facts = []
            total_chars = 0
            
            for mem in memories:
                memory_data = mem.get('memory', '') or mem.get('data', '')
                total_chars += len(memory_data)
                
                # Extract metadata
                metadata = mem.get('metadata', {})
                mem_type = metadata.get('type', 'unknown')
                memory_types[mem_type] += 1
                
                if mem_type == 'fact':
                    facts.append(memory_data)
            
            # Get user activity from metrics
            metrics = metrics_collector.get_metrics()
            user_requests = [
                req for req in (metrics.get('recent_user_requests') or metrics.get('recent_requests', []))
                if req.get('user_id') == user_id or req.get('metadata', {}).get('user_id') == user_id
            ]
            
            total_requests = len(user_requests)
            total_tokens = sum(req.get('tokens', 0) for req in user_requests)
            total_cost = sum(req.get('cost_usd', 0) for req in user_requests)
            
            return {
                'user_id': user_id,
                'total_memories': len(memories),
                'memory_breakdown': dict(memory_types),
                'profile_facts': facts[:3],  # Key facts
                'engagement_metrics': {
                    'total_api_requests': total_requests,
                    'total_tokens_used': total_tokens,
                    'total_cost_usd': round(total_cost, 4),
                    'avg_memory_length': round(total_chars / len(memories), 0) if memories else 0
                },
                'last_active': user_requests[-1].get('timestamp') if user_requests else None,
                'insights': self._generate_user_insights(memories),
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            log_structured("error", f"Failed to get user deep dive for {user_id}", error=str(e))
            return {'error': str(e), 'user_id': user_id}
    
    def _generate_user_insights(self, memories: List) -> List[str]:
        """Generate insights about a user"""
        insights = []
        
        if len(memories) < 5:
            insights.append("User is new - limited data for analysis")
        elif len(memories) > 20:
            insights.append("Highly engaged user - extensive memory history")
        
        return insights
    
    def get_database_health(self) -> Dict[str, Any]:
        """Get Qdrant database health and statistics by querying real database"""
        try:
            qdrant_url = f"http://{os.getenv('QDRANT_HOST', 'localhost')}:{os.getenv('QDRANT_PORT', '6333')}"
            
            # Get collection info
            import time
            start_time = time.time()
            
            collections_response = requests.get(f"{qdrant_url}/collections")
            
            if collections_response.status_code != 200:
                return {'error': f'Failed to query Qdrant: {collections_response.status_code}'}
            
            response_time_ms = round((time.time() - start_time) * 1000, 2)
            
            collections_data = collections_response.json()
            collections = collections_data.get('result', {}).get('collections', [])
            
            # Get detailed info for mem0 collection
            mem0_collection = {}
            for col in collections:
                if col.get('name') == 'mem0':
                    # Get full collection details
                    detail_response = requests.get(f"{qdrant_url}/collections/mem0")
                    if detail_response.status_code == 200:
                        detail_data = detail_response.json()
                        result = detail_data.get('result', {})
                        
                        mem0_collection = {
                            'total_points': result.get('points_count', 0),
                            'vectors_count': result.get('vectors_count', 0),
                            'indexed_vectors_count': result.get('indexed_vectors_count', 0),
                            'segments_count': result.get('segments_count', 0),
                            'status': result.get('status', 'unknown')
                        }
                    break
            
            # Get cluster info for health indicators
            cluster_response = requests.get(f"{qdrant_url}/cluster")
            cluster_status = 'unknown'
            if cluster_response.status_code == 200:
                cluster_data = cluster_response.json()
                cluster_status = cluster_data.get('result', {}).get('status', 'unknown')
            
            return {
                'database': 'qdrant',
                'status': 'operational' if mem0_collection.get('status') == 'green' else mem0_collection.get('status', 'operational'),
                'cluster_status': cluster_status,
                'collections': {
                    'mem0': mem0_collection if mem0_collection else {'error': 'Collection not found'},
                    'total_collections': len(collections)
                },
                'health_indicators': {
                    'response_time_ms': response_time_ms,
                    'qdrant_available': True
                },
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            log_structured("error", "Failed to get database health", error=str(e))
            return {
                'database': 'qdrant',
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }


def format_for_slack(*_args, **_kwargs):
    """
    Slack formatting helper (disabled).

    This repo does not ship Slack integration in the default lab path.
    Keep this function as a placeholder for a future stretch goal.
    """
    raise NotImplementedError("Slack integration is not included in this lab.")

