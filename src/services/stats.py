"""
Statistics service for tracking event processing metrics.
"""

import asyncio
from datetime import datetime, timezone
from typing import Dict, Any
from threading import Lock
import logging

logger = logging.getLogger(__name__)


class EventStats:
    """Thread-safe event statistics tracker."""
    
    def __init__(self):
        self._lock = Lock()
        self._stats = {
            'total_events_received': 0,
            'total_events_forwarded': 0,
            'total_events_failed': 0,
            'events_by_tenant': {},
            'events_by_level': {},
            'last_event_time': None,
            'service_start_time': datetime.now(timezone.utc),
            'uptime_seconds': 0
        }
    
    def increment_received(self, tenant_id: str = None):
        """Increment received events counter."""
        with self._lock:
            self._stats['total_events_received'] += 1
            self._stats['last_event_time'] = datetime.now(timezone.utc)
            
            if tenant_id:
                if tenant_id not in self._stats['events_by_tenant']:
                    self._stats['events_by_tenant'][tenant_id] = {
                        'received': 0,
                        'forwarded': 0,
                        'failed': 0
                    }
                self._stats['events_by_tenant'][tenant_id]['received'] += 1
    
    def increment_forwarded(self, tenant_id: str = None, level: str = None):
        """Increment forwarded events counter."""
        with self._lock:
            self._stats['total_events_forwarded'] += 1
            
            if tenant_id:
                if tenant_id not in self._stats['events_by_tenant']:
                    self._stats['events_by_tenant'][tenant_id] = {
                        'received': 0,
                        'forwarded': 0,
                        'failed': 0
                    }
                self._stats['events_by_tenant'][tenant_id]['forwarded'] += 1
            
            if level:
                if level not in self._stats['events_by_level']:
                    self._stats['events_by_level'][level] = 0
                self._stats['events_by_level'][level] += 1
    
    def increment_failed(self, tenant_id: str = None):
        """Increment failed events counter."""
        with self._lock:
            self._stats['total_events_failed'] += 1
            
            if tenant_id:
                if tenant_id not in self._stats['events_by_tenant']:
                    self._stats['events_by_tenant'][tenant_id] = {
                        'received': 0,
                        'forwarded': 0,
                        'failed': 0
                    }
                self._stats['events_by_tenant'][tenant_id]['failed'] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current statistics."""
        with self._lock:
            current_time = datetime.now(timezone.utc)
            uptime = (current_time - self._stats['service_start_time']).total_seconds()
            
            stats_copy = self._stats.copy()
            stats_copy['uptime_seconds'] = uptime
            stats_copy['current_time'] = current_time.isoformat()
            
            # Calculate success rate
            total_processed = stats_copy['total_events_forwarded'] + stats_copy['total_events_failed']
            if total_processed > 0:
                stats_copy['success_rate'] = stats_copy['total_events_forwarded'] / total_processed
            else:
                stats_copy['success_rate'] = 0.0
            
            # Convert datetime objects to ISO strings for JSON serialization
            if stats_copy['last_event_time']:
                stats_copy['last_event_time'] = stats_copy['last_event_time'].isoformat()
            
            stats_copy['service_start_time'] = stats_copy['service_start_time'].isoformat()
            
            return stats_copy
    
    def reset_stats(self):
        """Reset all statistics."""
        with self._lock:
            self._stats = {
                'total_events_received': 0,
                'total_events_forwarded': 0,
                'total_events_failed': 0,
                'events_by_tenant': {},
                'events_by_level': {},
                'last_event_time': None,
                'service_start_time': datetime.now(timezone.utc),
                'uptime_seconds': 0
            }
            logger.info("Event statistics reset")


# Global statistics instance
event_stats = EventStats()
