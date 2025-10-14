"""Comprehensive integration tests for fsociety."""

from __future__ import annotations

import asyncio
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest

from fsociety.__version__ import __version__
from fsociety.ai.engine import AIEngine, get_ai_engine
from fsociety.ai.exploit_assistant import AIExploitAssistant, get_exploit_assistant
from fsociety.core.async_repo import AsyncGitHubRepo, RepoManager, get_repo_manager
from fsociety.core.cache import CacheManager, get_cache_manager
from fsociety.core.config import Config, get_config
from fsociety.core.performance import (
    GPUMemoryManager,
    PerformanceMonitor,
    get_gpu_memory_manager,
    get_performance_monitor,
)


class TestFullIntegration:
    """Test complete system integration."""
    
    @pytest.mark.asyncio
    async def test_complete_workflow(self):
        """Test a complete penetration testing workflow."""
        # 1. Initialize configuration
        config = get_config()
        assert config is not None
        assert config.version == __version__
        
        # 2. Setup performance monitoring
        monitor = get_performance_monitor()
        assert monitor is not None
        
        # 3. Initialize cache system
        cache = get_cache_manager()
        assert cache is not None
        
        # 4. Setup repository manager
        repo_manager = get_repo_manager()
        assert repo_manager is not None
        
        # 5. If AI enabled, initialize AI components
        if config.ai.enabled:
            ai_engine = get_ai_engine()
            assert ai_engine is not None
            
            exploit_assistant = get_exploit_assistant()
            assert exploit_assistant is not None
    
    @pytest.mark.asyncio
    async def test_scan_and_analyze_workflow(self):
        """Test scanning and AI analysis workflow."""
        config = get_config()
        
        # Mock scan results
        scan_results = {
            "host": "example.com",
            "status": "up",
            "open_ports": [
                {"port": 80, "service": "http", "version": "nginx 1.18.0"},
                {"port": 443, "service": "https", "version": "nginx 1.18.0"},
                {"port": 22, "service": "ssh", "version": "OpenSSH 8.2p1"},
            ],
            "os": {"name": "Linux", "accuracy": "95%"},
        }
        
        # If AI enabled, perform analysis
        if config.ai.enabled:
            with patch.object(AIEngine, "_generate", return_value="Mock analysis"):
                ai_engine = get_ai_engine()
                ai_engine._initialized = True
                
                result = await ai_engine.analyze_vulnerability(
                    target="example.com",
                    scan_results=scan_results,
                )
                
                assert result is not None
                assert result.summary is not None
    
    @pytest.mark.asyncio
    async def test_concurrent_operations(self):
        """Test concurrent scanning operations."""
        config = get_config()
        monitor = get_performance_monitor()
        
        # Create multiple mock tasks
        async def mock_scan(target: str) -> dict:
            await asyncio.sleep(0.1)  # Simulate scan time
            return {"target": target, "status": "complete"}
        
        # Run multiple scans concurrently
        targets = [f"target{i}.com" for i in range(10)]
        tasks = [mock_scan(target) for target in targets]
        
        results = await asyncio.gather(*tasks)
        
        assert len(results) == 10
        assert all(r["status"] == "complete" for r in results)
    
    @pytest.mark.asyncio
    async def test_caching_performance(self):
        """Test caching improves performance."""
        cache = get_cache_manager()
        await cache.clear()
        
        # Test cache miss
        result1 = await cache.get("test_key")
        assert result1 is None
        
        # Set value
        await cache.set("test_key", {"data": "test_value"})
        
        # Test cache hit
        result2 = await cache.get("test_key")
        assert result2 is not None
        assert result2["data"] == "test_value"
        
        # Verify stats
        stats = await cache.stats()
        assert stats["total_requests"] > 0
    
    @pytest.mark.asyncio
    async def test_performance_monitoring(self):
        """Test performance monitoring system."""
        monitor = get_performance_monitor()
        monitor.reset()
        
        # Record some metrics
        monitor.record("test_operation", 0.5)
        monitor.record("test_operation", 0.3)
        monitor.record("test_operation", 0.7)
        
        # Get metrics
        metrics = monitor.get_metrics("test_operation")
        assert "test_operation" in metrics
        
        metric = metrics["test_operation"]
        assert metric.count == 3
        assert 0.3 <= metric.avg_time <= 0.7
    
    @pytest.mark.asyncio
    async def test_gpu_memory_management(self):
        """Test GPU memory management."""
        gpu_manager = get_gpu_memory_manager()
        
        if gpu_manager.torch_available:
            info = gpu_manager.get_memory_info()
            
            assert "allocated_gb" in info
            assert "total_gb" in info
            assert "free_gb" in info
            
            # Test auto cleanup
            async with gpu_manager.auto_cleanup():
                # Simulate GPU operations
                pass
    
    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test error handling across components."""
        # Test config error handling
        config = Config()
        assert config is not None
        
        # Test cache error handling
        cache = get_cache_manager()
        result = await cache.get("nonexistent_key")
        assert result is None
        
        # Test AI error handling with invalid input
        if config.ai.enabled:
            with patch.object(AIEngine, "_generate", side_effect=Exception("Test error")):
                ai_engine = get_ai_engine()
                ai_engine._initialized = True
                
                with pytest.raises(Exception):
                    await ai_engine.analyze_vulnerability("test", {})
    
    @pytest.mark.asyncio
    async def test_repo_operations(self):
        """Test repository operations."""
        
        class TestRepo(AsyncGitHubRepo):
            async def run(self) -> int:
                return 0
        
        repo = TestRepo(
            path="test/repo",
            description="Test repository",
        )
        
        assert repo.name == "repo"
        assert str(repo) == "repo"
        assert not repo.installed()  # Should not exist
    
    @pytest.mark.asyncio
    async def test_ai_exploit_workflow(self):
        """Test AI-powered exploit generation."""
        config = get_config()
        
        if not config.ai.enabled:
            pytest.skip("AI features disabled")
        
        with patch.object(AIEngine, "_generate", return_value="Mock exploit"):
            exploit_assistant = get_exploit_assistant()
            exploit_assistant._initialized = True
            
            payload = await exploit_assistant.generate_payload(
                exploit_type="sql_injection",
                target_info={"database": "mysql"},
            )
            
            assert payload is not None
    
    def test_config_persistence(self, tmp_path):
        """Test configuration save and load."""
        config = Config()
        config.config_dir = tmp_path
        
        # Modify config
        config.ai.enabled = True
        config.performance.max_workers = 16
        
        # Save
        config.save()
        
        # Verify file exists
        assert config.config_file.exists()
        
        # Verify content
        import orjson
        data = orjson.loads(config.config_file.read_bytes())
        assert data["ai"]["enabled"] is True
        assert data["performance"]["max_workers"] == 16


class TestPerformanceBenchmarks:
    """Benchmark critical operations."""
    
    @pytest.mark.asyncio
    @pytest.mark.benchmark
    async def test_cache_performance(self, benchmark):
        """Benchmark cache operations."""
        cache = get_cache_manager()
        
        async def cache_operations():
            for i in range(100):
                await cache.set(f"key_{i}", f"value_{i}")
                await cache.get(f"key_{i}")
        
        benchmark(lambda: asyncio.run(cache_operations()))
    
    @pytest.mark.asyncio
    @pytest.mark.benchmark
    async def test_concurrent_scans(self, benchmark):
        """Benchmark concurrent operations."""
        
        async def mock_scans():
            async def scan():
                await asyncio.sleep(0.01)
                return {"status": "complete"}
            
            tasks = [scan() for _ in range(50)]
            await asyncio.gather(*tasks)
        
        benchmark(lambda: asyncio.run(mock_scans()))


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    @pytest.mark.asyncio
    async def test_empty_scan_results(self):
        """Test handling of empty scan results."""
        config = get_config()
        
        if config.ai.enabled:
            with patch.object(AIEngine, "_generate", return_value="No results"):
                ai_engine = get_ai_engine()
                ai_engine._initialized = True
                
                result = await ai_engine.analyze_vulnerability(
                    target="empty.com",
                    scan_results={},
                )
                
                assert result is not None
    
    @pytest.mark.asyncio
    async def test_large_data_handling(self):
        """Test handling of large data sets."""
        cache = get_cache_manager()
        
        # Create large data
        large_data = {"data": "x" * 10000}
        
        await cache.set("large_key", large_data)
        result = await cache.get("large_key")
        
        assert result is not None
        assert len(result["data"]) == 10000
    
    @pytest.mark.asyncio
    async def test_concurrent_cache_access(self):
        """Test concurrent cache operations."""
        cache = get_cache_manager()
        
        async def concurrent_operations():
            tasks = []
            for i in range(50):
                tasks.append(cache.set(f"key_{i}", f"value_{i}"))
                tasks.append(cache.get(f"key_{i}"))
            
            await asyncio.gather(*tasks)
        
        await concurrent_operations()
        
        stats = await cache.stats()
        assert stats["total_requests"] > 0


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])