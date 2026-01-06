"""
Monitoring and Observability Module
Provides error tracking, analytics, logging, and performance monitoring.
"""

import os
import time
import logging
import traceback
from functools import wraps
from typing import Callable, Dict, Any, Optional
from datetime import datetime
import json

# Try to import Sentry (optional dependency)
try:
    import sentry_sdk
    from sentry_sdk.integrations.flask import FlaskIntegration
    from sentry_sdk.integrations.logging import LoggingIntegration
    SENTRY_AVAILABLE = True
except ImportError:
    SENTRY_AVAILABLE = False
    print("Warning: sentry-sdk not installed. Error tracking disabled.")
    print("Install with: pip install sentry-sdk")


class ErrorTracker:
    """Error tracking with Sentry integration"""
    
    def __init__(self, dsn: str = None, environment: str = "development"):
        """
        Initialize error tracker
        
        Args:
            dsn: Sentry DSN (Data Source Name)
            environment: Environment name (development, staging, production)
        """
        self.dsn = dsn or os.getenv('SENTRY_DSN')
        self.environment = environment
        self.enabled = False
        
        if SENTRY_AVAILABLE and self.dsn:
            self._init_sentry()
        else:
            logging.warning(
                "Sentry error tracking not initialized. "
                "Set SENTRY_DSN environment variable to enable."
            )
    
    def _init_sentry(self):
        """Initialize Sentry SDK"""
        try:
            # Logging integration
            sentry_logging = LoggingIntegration(
                level=logging.INFO,  # Capture info and above as breadcrumbs
                event_level=logging.ERROR  # Send errors as events
            )
            
            sentry_sdk.init(
                dsn=self.dsn,
                environment=self.environment,
                integrations=[
                    FlaskIntegration(),
                    sentry_logging,
                ],
                # Performance monitoring
                traces_sample_rate=0.1,  # 10% of transactions
                # Release tracking
                release=os.getenv('APP_VERSION', '3.0.0'),
                # Error sampling
                sample_rate=1.0,  # Send 100% of errors
                # Include local variables in stack traces
                attach_stacktrace=True,
                # Send default PII (personally identifiable information)
                send_default_pii=False,
            )
            
            self.enabled = True
            logging.info(f"Sentry initialized for {self.environment} environment")
        except Exception as e:
            logging.error(f"Failed to initialize Sentry: {e}")
    
    def capture_exception(self, error: Exception, context: Dict[str, Any] = None):
        """Capture an exception with optional context"""
        if self.enabled and SENTRY_AVAILABLE:
            with sentry_sdk.push_scope() as scope:
                if context:
                    for key, value in context.items():
                        scope.set_context(key, value)
                sentry_sdk.capture_exception(error)
        else:
            # Fallback to logging
            logging.error(f"Exception: {error}", exc_info=True)
            if context:
                logging.error(f"Context: {json.dumps(context, default=str)}")
    
    def capture_message(self, message: str, level: str = "info", context: Dict[str, Any] = None):
        """Capture a message with optional context"""
        if self.enabled and SENTRY_AVAILABLE:
            with sentry_sdk.push_scope() as scope:
                if context:
                    for key, value in context.items():
                        scope.set_context(key, value)
                sentry_sdk.capture_message(message, level=level)
        else:
            # Fallback to logging
            log_level = getattr(logging, level.upper(), logging.INFO)
            logging.log(log_level, message)
            if context:
                logging.log(log_level, f"Context: {json.dumps(context, default=str)}")
    
    def set_user(self, user_id: str, email: str = None, username: str = None):
        """Set user context for error tracking"""
        if self.enabled and SENTRY_AVAILABLE:
            sentry_sdk.set_user({
                "id": user_id,
                "email": email,
                "username": username,
            })
    
    def add_breadcrumb(self, message: str, category: str = "default", level: str = "info", data: Dict = None):
        """Add a breadcrumb for error context"""
        if self.enabled and SENTRY_AVAILABLE:
            sentry_sdk.add_breadcrumb(
                message=message,
                category=category,
                level=level,
                data=data or {}
            )


class Analytics:
    """Analytics tracking (Google Analytics, custom events)"""
    
    def __init__(self, tracking_id: str = None):
        """
        Initialize analytics
        
        Args:
            tracking_id: Google Analytics tracking ID (GA4 measurement ID)
        """
        self.tracking_id = tracking_id or os.getenv('GA_TRACKING_ID')
        self.enabled = bool(self.tracking_id)
        self.events = []
        
        if not self.enabled:
            logging.warning(
                "Analytics not initialized. "
                "Set GA_TRACKING_ID environment variable to enable."
            )
    
    def track_event(self, event_name: str, properties: Dict[str, Any] = None):
        """Track an event"""
        event = {
            'timestamp': datetime.now().isoformat(),
            'event': event_name,
            'properties': properties or {}
        }
        
        self.events.append(event)
        
        # Here you would send to Google Analytics or custom analytics service
        # For now, we'll just log it
        logging.info(f"Analytics Event: {event_name}", extra={'properties': properties})
    
    def track_page_view(self, path: str, title: str = None, user_id: str = None):
        """Track a page view"""
        self.track_event('page_view', {
            'path': path,
            'title': title,
            'user_id': user_id,
        })
    
    def track_api_call(self, endpoint: str, method: str, duration: float, status_code: int):
        """Track an API call"""
        self.track_event('api_call', {
            'endpoint': endpoint,
            'method': method,
            'duration_ms': duration * 1000,
            'status_code': status_code,
        })
    
    def track_voyage_created(self, voyage_id: str, module: str, user_id: str = None):
        """Track voyage creation"""
        self.track_event('voyage_created', {
            'voyage_id': voyage_id,
            'module': module,
            'user_id': user_id,
        })
    
    def track_excel_export(self, export_type: str, row_count: int, user_id: str = None):
        """Track Excel export"""
        self.track_event('excel_export', {
            'export_type': export_type,
            'row_count': row_count,
            'user_id': user_id,
        })
    
    def get_events(self, limit: int = 100) -> list:
        """Get recent events"""
        return self.events[-limit:]


class PerformanceMonitor:
    """Performance monitoring for API endpoints"""
    
    def __init__(self):
        self.metrics = {}
    
    def record_timing(self, endpoint: str, duration: float):
        """Record timing for an endpoint"""
        if endpoint not in self.metrics:
            self.metrics[endpoint] = {
                'count': 0,
                'total_time': 0,
                'min_time': float('inf'),
                'max_time': 0,
                'recent_times': []
            }
        
        metric = self.metrics[endpoint]
        metric['count'] += 1
        metric['total_time'] += duration
        metric['min_time'] = min(metric['min_time'], duration)
        metric['max_time'] = max(metric['max_time'], duration)
        
        # Keep last 100 measurements
        metric['recent_times'].append(duration)
        if len(metric['recent_times']) > 100:
            metric['recent_times'].pop(0)
    
    def get_stats(self, endpoint: str = None) -> Dict:
        """Get performance statistics"""
        if endpoint:
            if endpoint not in self.metrics:
                return {}
            
            metric = self.metrics[endpoint]
            return {
                'endpoint': endpoint,
                'count': metric['count'],
                'avg_time': metric['total_time'] / metric['count'] if metric['count'] > 0 else 0,
                'min_time': metric['min_time'] if metric['min_time'] != float('inf') else 0,
                'max_time': metric['max_time'],
            }
        else:
            # Return all stats
            return {
                ep: self.get_stats(ep)
                for ep in self.metrics.keys()
            }


# Global instances
error_tracker: Optional[ErrorTracker] = None
analytics: Optional[Analytics] = None
performance_monitor = PerformanceMonitor()


def init_monitoring(sentry_dsn: str = None, ga_tracking_id: str = None, environment: str = "development"):
    """
    Initialize monitoring services
    
    Args:
        sentry_dsn: Sentry DSN
        ga_tracking_id: Google Analytics tracking ID
        environment: Environment name
    """
    global error_tracker, analytics
    
    error_tracker = ErrorTracker(dsn=sentry_dsn, environment=environment)
    analytics = Analytics(tracking_id=ga_tracking_id)
    
    logging.info("Monitoring services initialized")


def track_errors(f: Callable) -> Callable:
    """Decorator to track errors in functions"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            if error_tracker:
                error_tracker.capture_exception(e, {
                    'function': f.__name__,
                    'args': str(args)[:1000],  # Limit size
                    'kwargs': str(kwargs)[:1000],
                })
            raise
    
    return decorated_function


def track_performance(f: Callable) -> Callable:
    """Decorator to track performance of functions"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        try:
            result = f(*args, **kwargs)
            return result
        finally:
            duration = time.time() - start_time
            performance_monitor.record_timing(f.__name__, duration)
            
            # Log slow operations (> 1 second)
            if duration > 1.0:
                logging.warning(f"Slow operation: {f.__name__} took {duration:.2f}s")
    
    return decorated_function


def monitor_api_endpoint(f: Callable) -> Callable:
    """Decorator to monitor API endpoints"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask import request
        
        start_time = time.time()
        endpoint = request.endpoint or f.__name__
        method = request.method
        
        # Add breadcrumb
        if error_tracker:
            error_tracker.add_breadcrumb(
                message=f"{method} {endpoint}",
                category="api",
                data={
                    'method': method,
                    'endpoint': endpoint,
                    'args': request.args.to_dict(),
                }
            )
        
        try:
            response = f(*args, **kwargs)
            status_code = getattr(response, 'status_code', 200)
            
            return response
        except Exception as e:
            status_code = 500
            if error_tracker:
                error_tracker.capture_exception(e, {
                    'endpoint': endpoint,
                    'method': method,
                    'args': request.args.to_dict(),
                    'form': request.form.to_dict(),
                })
            raise
        finally:
            duration = time.time() - start_time
            
            # Record performance
            performance_monitor.record_timing(f"{method}:{endpoint}", duration)
            
            # Track analytics
            if analytics:
                analytics.track_api_call(endpoint, method, duration, status_code)
    
    return decorated_function


class LogAggregator:
    """Centralized log aggregation"""
    
    def __init__(self, log_file: str = "logs/aggregated.log"):
        """
        Initialize log aggregator
        
        Args:
            log_file: Path to aggregated log file
        """
        self.log_file = log_file
        
        # Ensure log directory exists
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        # Configure logging
        self.logger = logging.getLogger('aggregator')
        self.logger.setLevel(logging.INFO)
        
        # File handler with JSON formatting
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        self.logger.addHandler(file_handler)
    
    def log_structured(self, level: str, event: str, data: Dict[str, Any]):
        """Log structured data as JSON"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'level': level,
            'event': event,
            'data': data
        }
        
        log_level = getattr(logging, level.upper(), logging.INFO)
        self.logger.log(log_level, json.dumps(log_entry))


# Health check endpoint data
health_status = {
    'status': 'healthy',
    'timestamp': None,
    'uptime_seconds': 0,
    'version': '3.0.0',
}


def update_health_status(status: str = 'healthy'):
    """Update health status"""
    health_status['status'] = status
    health_status['timestamp'] = datetime.now().isoformat()


def get_health_status() -> Dict[str, Any]:
    """Get current health status"""
    return {
        **health_status,
        'performance_metrics': performance_monitor.get_stats(),
    }


# Example usage
if __name__ == "__main__":
    # Initialize monitoring
    init_monitoring(
        sentry_dsn=os.getenv('SENTRY_DSN'),
        ga_tracking_id=os.getenv('GA_TRACKING_ID'),
        environment='development'
    )
    
    # Test error tracking
    if error_tracker:
        error_tracker.capture_message("Test message", level="info")
    
    # Test analytics
    if analytics:
        analytics.track_event('test_event', {'property': 'value'})
    
    # Test performance monitoring
    @track_performance
    def slow_function():
        time.sleep(0.1)
        return "Done"
    
    slow_function()
    print("Performance Stats:", performance_monitor.get_stats('slow_function'))
