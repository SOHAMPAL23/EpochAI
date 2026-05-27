"""
Performance monitoring and benchmarking utilities
"""

import time
import functools
import psutil
import gc
from typing import Dict, Any, Callable, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

from config.logging_config import get_logger

logger = get_logger('performance')


@dataclass
class PerformanceMetrics:
    """Performance metrics data class"""
    execution_time: float
    memory_usage_mb: float
    cpu_percent: float
    function_name: str
    timestamp: datetime
    parameters: Optional[Dict[str, Any]] = None
    result_size: Optional[int] = None


class PerformanceMonitor:
    """Monitor and track performance metrics"""
    
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self.metrics_history = []
        self.function_stats = {}
    
    def record_metrics(self, metrics: PerformanceMetrics):
        """Record performance metrics"""
        self.metrics_history.append(metrics)
        
        # Maintain history size
        if len(self.metrics_history) > self.max_history:
            self.metrics_history.pop(0)
        
        # Update function statistics
        func_name = metrics.function_name
        if func_name not in self.function_stats:
            self.function_stats[func_name] = {
                'call_count': 0,
                'total_time': 0.0,
                'min_time': float('inf'),
                'max_time': 0.0,
                'avg_memory': 0.0,
                'total_memory': 0.0
            }
        
        stats = self.function_stats[func_name]
        stats['call_count'] += 1
        stats['total_time'] += metrics.execution_time
        stats['min_time'] = min(stats['min_time'], metrics.execution_time)
        stats['max_time'] = max(stats['max_time'], metrics.execution_time)
        stats['total_memory'] += metrics.memory_usage_mb
        stats['avg_memory'] = stats['total_memory'] / stats['call_count']
    
    def get_function_stats(self, function_name: str) -> Optional[Dict[str, Any]]:
        """Get statistics for a specific function"""
        if function_name not in self.function_stats:
            return None
        
        stats = self.function_stats[function_name].copy()
        if stats['call_count'] > 0:
            stats['avg_time'] = stats['total_time'] / stats['call_count']
        else:
            stats['avg_time'] = 0.0
        
        return stats
    
    def get_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        if not self.metrics_history:
            return {'message': 'No performance data available'}
        
        recent_metrics = self.metrics_history[-100:]  # Last 100 calls
        
        execution_times = [m.execution_time for m in recent_metrics]
        memory_usage = [m.memory_usage_mb for m in recent_metrics]
        
        summary = {
            'total_calls': len(self.metrics_history),
            'recent_calls': len(recent_metrics),
            'avg_execution_time': sum(execution_times) / len(execution_times),
            'min_execution_time': min(execution_times),
            'max_execution_time': max(execution_times),
            'avg_memory_usage': sum(memory_usage) / len(memory_usage),
            'max_memory_usage': max(memory_usage),
            'functions_monitored': len(self.function_stats),
            'top_functions_by_time': self._get_top_functions_by_time(),
            'top_functions_by_memory': self._get_top_functions_by_memory()
        }
        
        return summary
    
    def _get_top_functions_by_time(self, limit: int = 5) -> list:
        """Get top functions by total execution time"""
        sorted_functions = sorted(
            self.function_stats.items(),
            key=lambda x: x[1]['total_time'],
            reverse=True
        )
        
        return [
            {
                'function': name,
                'total_time': stats['total_time'],
                'avg_time': stats['total_time'] / stats['call_count'],
                'call_count': stats['call_count']
            }
            for name, stats in sorted_functions[:limit]
        ]
    
    def _get_top_functions_by_memory(self, limit: int = 5) -> list:
        """Get top functions by average memory usage"""
        sorted_functions = sorted(
            self.function_stats.items(),
            key=lambda x: x[1]['avg_memory'],
            reverse=True
        )
        
        return [
            {
                'function': name,
                'avg_memory': stats['avg_memory'],
                'max_memory': max([m.memory_usage_mb for m in self.metrics_history 
                                 if m.function_name == name], default=0),
                'call_count': stats['call_count']
            }
            for name, stats in sorted_functions[:limit]
        ]
    
    def clear_history(self):
        """Clear performance history"""
        self.metrics_history.clear()
        self.function_stats.clear()
        logger.info("Performance history cleared")


# Global performance monitor instance
performance_monitor = PerformanceMonitor()


def benchmark_function(include_memory: bool = True, include_params: bool = False):
    """
    Decorator to benchmark function performance
    
    Args:
        include_memory: Whether to include memory usage monitoring
        include_params: Whether to include function parameters in metrics
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Get initial memory usage
            process = psutil.Process() if include_memory else None
            initial_memory = process.memory_info().rss / 1024 / 1024 if process else 0
            
            # Record start time
            start_time = time.time()
            
            try:
                # Execute function
                result = func(*args, **kwargs)
                
                # Calculate execution time
                execution_time = time.time() - start_time
                
                # Get final memory usage
                final_memory = process.memory_info().rss / 1024 / 1024 if process else 0
                memory_usage = max(0, final_memory - initial_memory)
                
                # Get CPU usage (approximate)
                cpu_percent = process.cpu_percent() if process else 0
                
                # Determine result size
                result_size = None
                if hasattr(result, '__len__'):
                    try:
                        result_size = len(result)
                    except:
                        pass
                
                # Create metrics
                metrics = PerformanceMetrics(
                    execution_time=execution_time,
                    memory_usage_mb=memory_usage,
                    cpu_percent=cpu_percent,
                    function_name=func.__name__,
                    timestamp=datetime.now(),
                    parameters={'args_count': len(args), 'kwargs_count': len(kwargs)} if include_params else None,
                    result_size=result_size
                )
                
                # Record metrics
                performance_monitor.record_metrics(metrics)
                
                # Log performance if execution time is significant
                if execution_time > 0.1:  # Log if > 100ms
                    logger.info(f"{func.__name__} executed in {execution_time:.4f}s, "
                              f"memory: {memory_usage:.2f}MB")
                
                return result
                
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(f"{func.__name__} failed after {execution_time:.4f}s: {str(e)}")
                raise
        
        return wrapper
    return decorator


class MemoryProfiler:
    """Simple memory profiler for tracking memory usage"""
    
    def __init__(self):
        self.snapshots = []
    
    def take_snapshot(self, label: str = ""):
        """Take a memory snapshot"""
        process = psutil.Process()
        memory_info = process.memory_info()
        
        snapshot = {
            'label': label,
            'timestamp': datetime.now(),
            'rss_mb': memory_info.rss / 1024 / 1024,
            'vms_mb': memory_info.vms / 1024 / 1024,
            'percent': process.memory_percent()
        }
        
        self.snapshots.append(snapshot)
        return snapshot
    
    def get_memory_diff(self, start_label: str, end_label: str) -> Optional[Dict[str, float]]:
        """Get memory difference between two snapshots"""
        start_snapshot = None
        end_snapshot = None
        
        for snapshot in self.snapshots:
            if snapshot['label'] == start_label:
                start_snapshot = snapshot
            elif snapshot['label'] == end_label:
                end_snapshot = snapshot
        
        if not start_snapshot or not end_snapshot:
            return None
        
        return {
            'rss_diff_mb': end_snapshot['rss_mb'] - start_snapshot['rss_mb'],
            'vms_diff_mb': end_snapshot['vms_mb'] - start_snapshot['vms_mb'],
            'percent_diff': end_snapshot['percent'] - start_snapshot['percent'],
            'time_diff_seconds': (end_snapshot['timestamp'] - start_snapshot['timestamp']).total_seconds()
        }
    
    def clear_snapshots(self):
        """Clear all snapshots"""
        self.snapshots.clear()


def optimize_memory():
    """Force garbage collection to optimize memory usage"""
    initial_memory = psutil.Process().memory_info().rss / 1024 / 1024
    
    # Force garbage collection
    collected = gc.collect()
    
    final_memory = psutil.Process().memory_info().rss / 1024 / 1024
    memory_freed = initial_memory - final_memory
    
    logger.info(f"Memory optimization: freed {memory_freed:.2f}MB, collected {collected} objects")
    
    return {
        'memory_freed_mb': memory_freed,
        'objects_collected': collected,
        'initial_memory_mb': initial_memory,
        'final_memory_mb': final_memory
    }


class Timer:
    """Context manager for timing code blocks"""
    
    def __init__(self, name: str = "Timer", log_result: bool = True):
        self.name = name
        self.log_result = log_result
        self.start_time = None
        self.end_time = None
        self.elapsed_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        self.elapsed_time = self.end_time - self.start_time
        
        if self.log_result:
            logger.info(f"{self.name}: {self.elapsed_time:.4f}s")
    
    def get_elapsed_time(self) -> Optional[float]:
        """Get elapsed time in seconds"""
        return self.elapsed_time


def profile_system_resources() -> Dict[str, Any]:
    """Get current system resource usage"""
    process = psutil.Process()
    
    return {
        'cpu_percent': process.cpu_percent(),
        'memory_percent': process.memory_percent(),
        'memory_rss_mb': process.memory_info().rss / 1024 / 1024,
        'memory_vms_mb': process.memory_info().vms / 1024 / 1024,
        'num_threads': process.num_threads(),
        'num_fds': process.num_fds() if hasattr(process, 'num_fds') else 0,
        'system_cpu_percent': psutil.cpu_percent(),
        'system_memory_percent': psutil.virtual_memory().percent,
        'system_disk_percent': psutil.disk_usage('/').percent if hasattr(psutil, 'disk_usage') else 0
    }