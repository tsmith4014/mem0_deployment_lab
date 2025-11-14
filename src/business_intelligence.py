"""
Business Intelligence module for Mem0 Stack
Provides analytics, reports, and insights for business owner via Slack
"""

import os
import json
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
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
                'total_openai_tokens': total_tokens,
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
            recent = metrics.get('recent_requests', [])
            
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
                user_id = metadata.get('user_id')
                
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
            
            # Analyze actual memory data
            memory_texts = []
            locations = Counter()
            triggers = Counter()
            categories = Counter()
            total_users = set()
            
            for point in points:
                payload = point.get('payload', {})
                memory_text = payload.get('data', '')
                user_id = payload.get('user_id')
                metadata = payload.get('metadata', {})
                
                if user_id:
                    total_users.add(user_id)
                
                memory_texts.append(memory_text.lower())
                
                # Extract metadata categories
                mem_type = metadata.get('type') if isinstance(metadata, dict) else None
                if mem_type:
                    categories[mem_type] += 1
                
                # Extract common patterns from text (simple keyword matching)
                text_lower = memory_text.lower()
                
                # Location patterns
                if 'las vegas' in text_lower or 'vegas' in text_lower:
                    locations['Las Vegas'] += 1
                if 'casino' in text_lower:
                    locations['Casino'] += 1
                    
                # Gambling types
                if 'card' in text_lower:
                    triggers['Card games'] += 1
                if 'slot' in text_lower or 'slots' in text_lower:
                    triggers['Slot machines'] += 1
                if 'dice' in text_lower:
                    triggers['Dice games'] += 1
                    
                # Substance triggers
                if 'alcohol' in text_lower or 'drinking' in text_lower:
                    triggers['Alcohol'] += 1
                if 'drug' in text_lower:
                    triggers['Drugs'] += 1
            
            total_memories = len(points)
            
            # Build patterns from actual data
            patterns = []
            for pattern, count in (locations + triggers).most_common(10):
                patterns.append({
                    'pattern': pattern,
                    'occurrence_count': count,
                    'percentage': round((count / total_memories) * 100, 1),
                    'category': 'location' if pattern in locations else 'trigger'
                })
            
            # Generate insights from actual data
            insights = []
            if 'Las Vegas' in locations and locations['Las Vegas'] > total_memories * 0.3:
                insights.append(f"{round((locations['Las Vegas']/total_memories)*100, 1)}% of users mention Las Vegas - consider local resources")
            if 'Card games' in triggers and triggers['Card games'] > 5:
                insights.append(f"Card games mentioned {triggers['Card games']} times - common gambling type")
            if 'Alcohol' in triggers:
                insights.append(f"Alcohol co-occurring in {triggers['Alcohol']} memories - consider dual-diagnosis content")
            
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
    
    def get_trigger_analysis(self) -> Dict[str, Any]:
        """Analyze gambling triggers across the user base by querying real memories"""
        try:
            # Query Qdrant for all memories
            qdrant_url = f"http://{os.getenv('QDRANT_HOST', 'localhost')}:{os.getenv('QDRANT_PORT', '6333')}"
            
            response = requests.post(
                f"{qdrant_url}/collections/mem0/points/scroll",
                json={
                    "limit": 1000,
                    "with_payload": True,
                    "with_vector": False
                }
            )
            
            if response.status_code != 200:
                return {'error': f'Failed to query Qdrant: {response.status_code}'}
            
            data = response.json()
            points = data.get('result', {}).get('points', [])
            
            # Categorize triggers from real memories
            environmental_triggers = []
            substance_triggers = []
            emotional_triggers = []
            severity_counts = {'high': 0, 'medium': 0, 'low': 0}
            
            for point in points:
                payload = point.get('payload', {})
                memory_text = payload.get('data', '').lower()
                metadata = payload.get('metadata', {})
                
                # Check metadata for trigger type
                if isinstance(metadata, dict) and metadata.get('type') == 'trigger':
                    # Categorize by keywords and metadata
                    sub_type = metadata.get('sub_type', '').lower()
                    severity = metadata.get('severity', 3)
                    
                    # Track severity
                    if severity >= 4:
                        severity_counts['high'] += 1
                    elif severity >= 2:
                        severity_counts['medium'] += 1
                    else:
                        severity_counts['low'] += 1
                    
                    # Categorize trigger
                    if any(word in memory_text or word in sub_type for word in ['casino', 'atm', 'payday', 'card table', 'slot']):
                        environmental_triggers.append(sub_type or memory_text[:30])
                    elif any(word in memory_text or word in sub_type for word in ['alcohol', 'drug', 'drinking', 'substance']):
                        substance_triggers.append(sub_type or memory_text[:30])
                    elif any(word in memory_text or word in sub_type for word in ['stress', 'lonely', 'bored', 'anger', 'sad', 'anxiety']):
                        emotional_triggers.append(sub_type or memory_text[:30])
                    else:
                        # Default to environmental
                        environmental_triggers.append(sub_type or memory_text[:30])
                else:
                    # Check memory text for trigger keywords even if not tagged
                    if any(word in memory_text for word in ['trigger', 'urge', 'craving']):
                        if any(word in memory_text for word in ['casino', 'atm', 'payday', 'card', 'slot']):
                            environmental_triggers.append(memory_text[:50])
                        elif any(word in memory_text for word in ['alcohol', 'drug', 'drink']):
                            substance_triggers.append(memory_text[:50])
                        elif any(word in memory_text for word in ['stress', 'lonely', 'bored', 'anger']):
                            emotional_triggers.append(memory_text[:50])
            
            total_triggers = len(environmental_triggers) + len(substance_triggers) + len(emotional_triggers)
            
            if total_triggers == 0:
                return {
                    'total_triggers_identified': 0,
                    'message': 'No triggers found in database. Add memories with type=trigger metadata.',
                    'timestamp': datetime.utcnow().isoformat()
                }
            
            # Build categories
            categories = []
            if environmental_triggers:
                categories.append({
                    'category': 'Environmental',
                    'count': len(environmental_triggers),
                    'percentage': round((len(environmental_triggers) / total_triggers) * 100, 1),
                    'examples': list(set(environmental_triggers))[:5]
                })
            if substance_triggers:
                categories.append({
                    'category': 'Substance-Related',
                    'count': len(substance_triggers),
                    'percentage': round((len(substance_triggers) / total_triggers) * 100, 1),
                    'examples': list(set(substance_triggers))[:5]
                })
            if emotional_triggers:
                categories.append({
                    'category': 'Emotional',
                    'count': len(emotional_triggers),
                    'percentage': round((len(emotional_triggers) / total_triggers) * 100, 1),
                    'examples': list(set(emotional_triggers))[:5]
                })
            
            # Generate insights
            insights = []
            if environmental_triggers and len(environmental_triggers) > total_triggers * 0.4:
                insights.append(f"Environmental triggers are most common ({round((len(environmental_triggers)/total_triggers)*100, 1)}%)")
            if substance_triggers:
                insights.append(f"Substance co-occurrence in {len(substance_triggers)} cases")
            if emotional_triggers and len(emotional_triggers) > 5:
                insights.append("Consider adding stress management and emotional regulation content")
            
            return {
                'total_triggers_identified': total_triggers,
                'trigger_categories': categories,
                'severity_distribution': severity_counts,
                'insights': insights if insights else ['Analyze more triggers to generate insights'],
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            log_structured("error", "Failed to analyze triggers", error=str(e))
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
            triggers = []
            facts = []
            total_chars = 0
            
            for mem in memories:
                memory_data = mem.get('memory', '') or mem.get('data', '')
                total_chars += len(memory_data)
                
                # Extract metadata
                metadata = mem.get('metadata', {})
                mem_type = metadata.get('type', 'unknown')
                memory_types[mem_type] += 1
                
                if mem_type == 'trigger':
                    triggers.append({
                        'content': memory_data,
                        'severity': metadata.get('severity', 'unknown'),
                        'sub_type': metadata.get('sub_type', 'unknown')
                    })
                elif mem_type == 'fact':
                    facts.append(memory_data)
            
            # Get user activity from metrics
            metrics = metrics_collector.get_metrics()
            user_requests = [
                req for req in metrics.get('recent_requests', [])
                if req.get('metadata', {}).get('user_id') == user_id
            ]
            
            total_requests = len(user_requests)
            total_tokens = sum(req.get('tokens', 0) for req in user_requests)
            total_cost = sum(req.get('cost_usd', 0) for req in user_requests)
            
            return {
                'user_id': user_id,
                'total_memories': len(memories),
                'memory_breakdown': dict(memory_types),
                'total_triggers_identified': len(triggers),
                'triggers': triggers[:5],  # Top 5
                'profile_facts': facts[:3],  # Key facts
                'engagement_metrics': {
                    'total_api_requests': total_requests,
                    'total_tokens_used': total_tokens,
                    'total_cost_usd': round(total_cost, 4),
                    'avg_memory_length': round(total_chars / len(memories), 0) if memories else 0
                },
                'last_active': user_requests[-1].get('timestamp') if user_requests else None,
                'insights': self._generate_user_insights(memories, triggers),
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            log_structured("error", f"Failed to get user deep dive for {user_id}", error=str(e))
            return {'error': str(e), 'user_id': user_id}
    
    def _generate_user_insights(self, memories: List, triggers: List) -> List[str]:
        """Generate insights about a user"""
        insights = []
        
        if len(memories) < 5:
            insights.append("User is new - limited data for analysis")
        elif len(memories) > 20:
            insights.append("Highly engaged user - extensive memory history")
        
        if len(triggers) > 5:
            insights.append(f"User has identified {len(triggers)} triggers - good self-awareness")
        elif len(triggers) == 0:
            insights.append("No triggers identified yet - consider trigger identification lesson")
        
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


def format_for_slack(data: Dict[str, Any], report_type: str) -> Dict[str, Any]:
    """Format report data for Slack display"""
    
    if report_type == 'system_overview':
        return {
            "response_type": "in_channel",
            "blocks": [
                {
                    "type": "header",
                    "text": {"type": "plain_text", "text": "📊 Mem0 System Overview"}
                },
                {
                    "type": "section",
                    "fields": [
                        {"type": "mrkdwn", "text": f"*Total Requests:*\n{data.get('total_api_requests', 0):,}"},
                        {"type": "mrkdwn", "text": f"*Success Rate:*\n{data.get('success_rate_pct', 0)}%"},
                        {"type": "mrkdwn", "text": f"*OpenAI Tokens:*\n{data.get('total_openai_tokens', 0):,}"},
                        {"type": "mrkdwn", "text": f"*Total Cost:*\n${data.get('total_cost_usd', 0)}"},
                        {"type": "mrkdwn", "text": f"*Est. Monthly:*\n${data.get('estimated_monthly_cost', 0)}"},
                        {"type": "mrkdwn", "text": f"*Errors:*\n{data.get('total_errors', 0)}"}
                    ]
                }
            ]
        }
    
    elif report_type == 'user_activity':
        blocks = [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": "👥 User Activity Report"}
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Active Users:* {data.get('total_active_users', 0)}\n*Memory Adds:* {data.get('total_memory_adds', 0)}\n*Searches:* {data.get('total_searches', 0)}"
                }
            }
        ]
        
        # Add top users
        top_users = data.get('top_users', [])[:5]
        if top_users:
            user_list = "\n".join([
                f"• `{u['user_id']}`: {u['request_count']} requests, ${u['total_cost']:.4f}"
                for u in top_users
            ])
            blocks.append({
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*Top Users:*\n{user_list}"}
            })
        
        return {"response_type": "in_channel", "blocks": blocks}
    
    elif report_type == 'triggers':
        blocks = [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": "🎯 Trigger Analysis"}
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Total Triggers Identified:* {data.get('total_triggers_identified', 0)}"
                }
            }
        ]
        
        # Add categories
        for cat in data.get('trigger_categories', []):
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{cat['category']}* ({cat['percentage']}%)\n{cat['count']} triggers: {', '.join(cat['examples'][:3])}"
                }
            })
        
        # Add insights
        insights = data.get('insights', [])
        if insights:
            blocks.append({
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*Key Insights:*\n" + "\n".join([f"• {i}" for i in insights])}
            })
        
        return {"response_type": "in_channel", "blocks": blocks}
    
    elif report_type == 'user_deep_dive':
        blocks = [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": f"🔍 User Report: {data.get('user_id', 'Unknown')}"}
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Total Memories:*\n{data.get('total_memories', 0)}"},
                    {"type": "mrkdwn", "text": f"*Triggers:*\n{data.get('total_triggers_identified', 0)}"},
                    {"type": "mrkdwn", "text": f"*API Requests:*\n{data.get('engagement_metrics', {}).get('total_api_requests', 0)}"},
                    {"type": "mrkdwn", "text": f"*Cost:*\n${data.get('engagement_metrics', {}).get('total_cost_usd', 0)}"}
                ]
            }
        ]
        
        # Add insights
        insights = data.get('insights', [])
        if insights:
            blocks.append({
                "type": "section",
                "text": {"type": "mrkdwn", "text": "*Insights:*\n" + "\n".join([f"• {i}" for i in insights])}
            })
        
        return {"response_type": "in_channel", "blocks": blocks}
    
    else:
        # Default formatting
        return {
            "response_type": "in_channel",
            "text": f"```{json.dumps(data, indent=2)}```"
        }

