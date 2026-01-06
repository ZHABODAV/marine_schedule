import time
import functools
import logging
from typing import Callable, Any, Dict
from .logger import setup_logger

logger = setup_logger('profiler')

class PerformanceMonitor:
    """Simple performance stats collector."""
    _stats: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def record(cls, name: str, duration: float):
        if name not in cls._stats:
            cls._stats[name] = {'count': 0, 'total_time': 0.0, 'max_time': 0.0}
        
        stats = cls._stats[name]
        stats['count'] += 1
        stats['total_time'] += duration
        stats['max_time'] = max(stats['max_time'], duration)

    @classmethod
    def get_stats(cls):
        return cls._stats
    
    @classmethod
    def log_stats(cls):
        """Log all collected statistics."""
        if not cls._stats:
            return
            
        logger.info("=" * 40)
        logger.info("PERFORMANCE STATISTICS")
        logger.info("=" * 40)
        
        # Sort by total time descending
        sorted_stats = sorted(
            cls._stats.items(), 
            key=lambda x: x[1]['total_time'], 
            reverse=True
        )
        
        for name, stats in sorted_stats:
            avg_time = stats['total_time'] / stats['count']
            logger.info(
                f"{name:<40} | "
                f"Count: {stats['count']:<5} | "
                f"Total: {stats['total_time']:.4f}s | "
                f"Avg: {avg_time:.4f}s | "
                f"Max: {stats['max_time']:.4f}s"
            )
        logger.info("=" * 40)

def profile_performance(func: Callable) -> Callable:
    """
    Decorator to measure and log the execution time of a function.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            end_time = time.perf_counter()
            duration = end_time - start_time
            
            # Record stats
            func_name = f"{func.__module__}.{func.__qualname__}"
            PerformanceMonitor.record(func_name, duration)
            
            # Log slow operations (> 100ms)
            if duration > 0.1:
                logger.info(f"Performance: {func_name} took {duration:.4f} seconds")
    return wrapper
