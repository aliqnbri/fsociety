"""Performance monitoring and optimization utilities."""

from __future__ import annotations

import asyncio
import functools
import time
from collections import defaultdict
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from typing import Any, Callable, Coroutine, TypeVar

import psutil
from cachetools import TTLCache
from rich.live import Live
from rich.table import Table

from fsociety.console import console
from fsociety.core.config import get_config

T = TypeVar("T")


@dataclass
class PerformanceMetrics:
    """Performance metrics container."""
    
    operation: str
    count: int = 0
    total_time: float = 0.0
    min_time: float = float("inf")
    max_time: float = 0.0
    errors: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    
    @property
    def avg_time(self) -> float:
        """Calculate average execution time."""
        return self.total_time / self.count if self.count > 0 else 0.0
    
    @property
    def cache_hit_rate(self) -> float:
        """Calculate cache hit rate."""
        total = self.cache_hits + self.cache_misses
        return self.cache_hits / total if total > 0 else 0.0


class PerformanceMonitor:
    """Monitor and track performance metrics."""
    
    def __init__(self) -> None:
        self.metrics: dict[str, PerformanceMetrics] = defaultdict(
            lambda: PerformanceMetrics(operation="unknown")
        )
        self.config = get_config()
        self._monitoring = False
        self._monitor_task: asyncio.Task | None = None
    
    def record(
        self,
        operation: str,
        duration: float,
        error: bool = False,
        cache_hit: bool | None = None,
    ) -> None:
        """Record a performance metric."""
        metric = self.metrics[operation]
        metric.operation = operation
        metric.count += 1
        metric.total_time += duration
        metric.min_time = min(metric.min_time, duration)
        metric.max_time = max(metric.max_time, duration)
        
        if error:
            metric.errors += 1
        
        if cache_hit is True:
            metric.cache_hits += 1
        elif cache_hit is False:
            metric.cache_misses += 1
    
    def get_metrics(self, operation: str | None = None) -> dict[str, PerformanceMetrics]:
        """Get metrics for specific operation or all operations."""
        if operation:
            return {operation: self.metrics[operation]}
        return dict(self.metrics)
    
    def reset(self, operation: str | None = None) -> None:
        """Reset metrics."""
        if operation:
            if operation in self.metrics:
                del self.metrics[operation]
        else:
            self.metrics.clear()
    
    def display_report(self) -> None:
        """Display performance report."""
        table = Table(title="Performance Metrics", border_style="cyan")
        
        table.add_column("Operation", style="yellow")
        table.add_column("Count", justify="right", style="cyan")
        table.add_column("Avg Time", justify="right", style="green")
        table.add_column("Min", justify="right")
        table.add_column("Max", justify="right")
        table.add_column("Errors", justify="right", style="red")
        table.add_column("Cache Hit %", justify="right", style="magenta")
        
        for metric in sorted(self.metrics.values(), key=lambda m: m.total_time, reverse=True):
            if metric.count == 0:
                continue
            
            table.add_row(
                metric.operation,
                str(metric.count),
                f"{metric.avg_time:.3f}s",
                f"{metric.min_time:.3f}s",
                f"{metric.max_time:.3f}s",
                str(metric.errors),
                f"{metric.cache_hit_rate:.1%}" if metric.cache_hits + metric.cache_misses > 0 else "-",
            )
        
        console.print(table)
    
    async def start_monitoring(self, interval: float = 1.0) -> None:
        """Start continuous system monitoring."""
        self._monitoring = True
        self._monitor_task = asyncio.create_task(self._monitor_system(interval))
    
    async def stop_monitoring(self) -> None:
        """Stop system monitoring."""
        self._monitoring = False
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
    
    async def _monitor_system(self, interval: float) -> None:
        """Monitor system resources."""
        with Live(self._create_system_table(), refresh_per_second=1) as live:
            while self._monitoring:
                live.update(self._create_system_table())
                await asyncio.sleep(interval)
    
    def _create_system_table(self) -> Table:
        """Create system monitoring table."""
        table = Table(title="System Resources", border_style="cyan")
        
        table.add_column("Resource", style="yellow")
        table.add_column("Usage", style="green")
        
        # CPU
        cpu_percent = psutil.cpu_percent(interval=0.1)
        table.add_row("CPU", f"{cpu_percent:.1f}%")
        
        # Memory
        memory = psutil.virtual_memory()
        table.add_row("Memory", f"{memory.percent:.1f}% ({memory.used / 1e9:.1f}GB / {memory.total / 1e9:.1f}GB)")
        
        # Disk
        disk = psutil.disk_usage("/")
        table.add_row("Disk", f"{disk.percent:.1f}% ({disk.used / 1e9:.1f}GB / {disk.total / 1e9:.1f}GB)")
        
        # Network
        net_io = psutil.net_io_counters()
        table.add_row("Network Sent", f"{net_io.bytes_sent / 1e6:.1f} MB")
        table.add_row("Network Recv", f"{net_io.bytes_recv / 1e6:.1f} MB")
        
        # GPU if available
        try:
            import torch
            if torch.cuda.is_available():
                for i in range(torch.cuda.device_count()):
                    mem_used = torch.cuda.memory_allocated(i) / 1e9
                    mem_total = torch.cuda.get_device_properties(i).total_memory / 1e9
                    table.add_row(
                        f"GPU {i}",
                        f"{(mem_used / mem_total * 100):.1f}% ({mem_used:.1f}GB / {mem_total:.1f}GB)"
                    )
        except ImportError:
            pass
        
        return table


class AsyncCache:
    """Async-aware caching decorator with TTL."""
    
    def __init__(self, maxsize: int = 128, ttl: int = 300) -> None:
        self.cache: TTLCache = TTLCache(maxsize=maxsize, ttl=ttl)
        self.config = get_config()
        self.monitor = get_performance_monitor()
    
    def __call__(self, func: Callable[..., Coroutine[Any, Any, T]]) -> Callable[..., Coroutine[Any, Any, T]]:
        """Decorator for caching async functions."""
        
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            if not self.config.performance.enable_caching:
                return await func(*args, **kwargs)
            
            # Create cache key
            key = self._make_key(func.__name__, args, kwargs)
            
            # Check cache
            if key in self.cache:
                self.monitor.record(func.__name__, 0.0, cache_hit=True)
                return self.cache[key]
            
            # Execute function
            start = time.perf_counter()
            try:
                result = await func(*args, **kwargs)
                duration = time.perf_counter() - start
                
                # Store in cache
                self.cache[key] = result
                self.monitor.record(func.__name__, duration, cache_hit=False)
                
                return result
            except Exception as e:
                duration = time.perf_counter() - start
                self.monitor.record(func.__name__, duration, error=True)
                raise
        
        return wrapper
    
    @staticmethod
    def _make_key(func_name: str, args: tuple, kwargs: dict) -> str:
        """Create cache key from function arguments."""
        key_parts = [func_name]
        key_parts.extend(str(arg) for arg in args)
        key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
        return ":".join(key_parts)


def timed(operation: str | None = None):
    """Decorator to time async function execution."""
    
    def decorator(func: Callable[..., Coroutine[Any, Any, T]]) -> Callable[..., Coroutine[Any, Any, T]]:
        op_name = operation or func.__name__
        monitor = get_performance_monitor()
        
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            start = time.perf_counter()
            try:
                result = await func(*args, **kwargs)
                duration = time.perf_counter() - start
                monitor.record(op_name, duration)
                return result
            except Exception as e:
                duration = time.perf_counter() - start
                monitor.record(op_name, duration, error=True)
                raise
        
        return wrapper
    
    return decorator


@asynccontextmanager
async def performance_context(operation: str):
    """Context manager for timing code blocks."""
    monitor = get_performance_monitor()
    start = time.perf_counter()
    error = False
    
    try:
        yield
    except Exception:
        error = True
        raise
    finally:
        duration = time.perf_counter() - start
        monitor.record(operation, duration, error=error)


class RateLimiter:
    """Async rate limiter."""
    
    def __init__(self, calls: int, period: float) -> None:
        self.calls = calls
        self.period = period
        self.semaphore = asyncio.Semaphore(calls)
        self.timestamps: list[float] = []
    
    async def acquire(self) -> None:
        """Acquire rate limit slot."""
        async with self.semaphore:
            now = time.time()
            
            # Remove old timestamps
            self.timestamps = [ts for ts in self.timestamps if now - ts < self.period]
            
            if len(self.timestamps) >= self.calls:
                sleep_time = self.period - (now - self.timestamps[0])
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)
            
            self.timestamps.append(now)
    
    @asynccontextmanager
    async def __call__(self):
        """Context manager for rate limiting."""
        await self.acquire()
        yield


class ConnectionPool:
    """Async connection pool for network operations."""
    
    def __init__(self, size: int = 10) -> None:
        self.size = size
        self.semaphore = asyncio.Semaphore(size)
        self.active = 0
        self.total_acquired = 0
    
    @asynccontextmanager
    async def acquire(self):
        """Acquire connection from pool."""
        async with self.semaphore:
            self.active += 1
            self.total_acquired += 1
            try:
                yield
            finally:
                self.active -= 1
    
    def stats(self) -> dict[str, int]:
        """Get pool statistics."""
        return {
            "size": self.size,
            "active": self.active,
            "available": self.size - self.active,
            "total_acquired": self.total_acquired,
        }


class GPUMemoryManager:
    """Manage GPU memory for optimal performance."""
    
    def __init__(self) -> None:
        self.torch_available = False
        try:
            import torch
            self.torch = torch
            self.torch_available = torch.cuda.is_available()
        except ImportError:
            pass
    
    def get_memory_info(self, device: int = 0) -> dict[str, float]:
        """Get GPU memory information."""
        if not self.torch_available:
            return {}
        
        allocated = self.torch.cuda.memory_allocated(device) / 1e9
        reserved = self.torch.cuda.memory_reserved(device) / 1e9
        total = self.torch.cuda.get_device_properties(device).total_memory / 1e9
        
        return {
            "allocated_gb": allocated,
            "reserved_gb": reserved,
            "total_gb": total,
            "free_gb": total - allocated,
            "utilization": allocated / total * 100,
        }
    
    def clear_cache(self) -> None:
        """Clear GPU cache."""
        if self.torch_available:
            self.torch.cuda.empty_cache()
    
    @asynccontextmanager
    async def auto_cleanup(self):
        """Automatically cleanup GPU memory after operations."""
        try:
            yield
        finally:
            if self.torch_available:
                self.torch.cuda.synchronize()
                self.torch.cuda.empty_cache()


# Global instances
_performance_monitor: PerformanceMonitor | None = None
_gpu_memory_manager: GPUMemoryManager | None = None


def get_performance_monitor() -> PerformanceMonitor:
    """Get global performance monitor instance."""
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor()
    return _performance_monitor


def get_gpu_memory_manager() -> GPUMemoryManager:
    """Get global GPU memory manager instance."""
    global _gpu_memory_manager
    if _gpu_memory_manager is None:
        _gpu_memory_manager = GPUMemoryManager()
    return _gpu_memory_manager


# Convenience functions
async def benchmark_async(
    func: Callable[..., Coroutine[Any, Any, T]],
    *args: Any,
    iterations: int = 100,
    **kwargs: Any,
) -> dict[str, float]:
    """Benchmark an async function."""
    times = []
    
    for _ in range(iterations):
        start = time.perf_counter()
        await func(*args, **kwargs)
        times.append(time.perf_counter() - start)
    
    return {
        "min": min(times),
        "max": max(times),
        "mean": sum(times) / len(times),
        "total": sum(times),
        "iterations": iterations,
    }