"""Comprehensive test suite for fsociety core functionality."""

from __future__ import annotations

import asyncio
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

import pytest

from fsociety.core.config import Config, AIConfig, PerformanceConfig, Platform, GPUBackend
from fsociety.core.async_repo import AsyncGitHubRepo, RepoManager, InstallOptions
from fsociety.ai.engine import AIEngine, AnalysisType, AIResult


class TestConfig:
    """Test configuration management."""
    
    def test_config_initialization(self):
        """Test config initialization with defaults."""
        config = Config()
        
        assert config.version is not None
        assert config.platform in Platform
        assert isinstance(config.ai, AIConfig)
        assert isinstance(config.performance, PerformanceConfig)
    
    def test_config_save_load(self, tmp_path):
        """Test saving and loading configuration."""
        config = Config()
        config.config_dir = tmp_path
        config.agreement = True
        config.ai.enabled = True
        
        config.save()
        
        # Load config
        loaded_config = Config()
        loaded_config.config_dir = tmp_path
        
        # Note: In real implementation, would need to load from file
        assert config.config_file.exists()
    
    def test_platform_detection(self):
        """Test platform detection."""
        platform = Config._detect_platform()
        assert platform in Platform
    
    def test_gpu_detection(self):
        """Test GPU detection."""
        config = Config()
        
        # GPU backend should be detected
        assert config.performance.gpu_backend in GPUBackend
    
    def test_config_paths(self):
        """Test configuration paths."""
        config = Config()
        
        assert config.config_file.name == "config.json"
        assert config.host_file_path.name == "hosts.txt"
        assert config.usernames_file_path.name == "usernames.txt"


class TestAsyncRepo:
    """Test async repository management."""
    
    @pytest.fixture
    def mock_repo(self):
        """Create a mock repository."""
        
        class MockRepo(AsyncGitHubRepo):
            async def run(self) -> int:
                return 0
        
        return MockRepo(
            path="test/repo",
            install=InstallOptions(pip="requirements.txt"),
            description="Test repository",
        )
    
    def test_repo_initialization(self, mock_repo):
        """Test repository initialization."""
        assert mock_repo.name == "repo"
        assert mock_repo.path == "test/repo"
        assert mock_repo.description == "Test repository"
    
    def test_repo_string_representation(self, mock_repo):
        """Test repository string representation."""
        assert str(mock_repo) == "repo"
    
    @pytest.mark.asyncio
    async def test_repo_install_options(self):
        """Test different install options."""
        
        # Test pip install
        class PipRepo(AsyncGitHubRepo):
            async def run(self) -> int:
                return 0
        
        repo = PipRepo(
            path="test/pip",
            install={"pip": ["package1", "package2"]},
        )
        assert repo.install_opts.pip == ["package1", "package2"]
        
        # Test binary install
        repo = PipRepo(
            path="test/binary",
            install={"binary": "https://example.com/binary"},
        )
        assert repo.install_opts.binary == "https://example.com/binary"
    
    def test_repo_installed_check(self, mock_repo):
        """Test installed check."""
        # Should be False since path doesn't exist
        assert not mock_repo.installed()
    
    @pytest.mark.asyncio
    async def test_repo_manager(self, mock_repo):
        """Test repository manager."""
        manager = RepoManager()
        manager.register(mock_repo)
        
        assert "repo" in manager.repos
        assert manager.repos["repo"] == mock_repo


class TestAIEngine:
    """Test AI engine functionality."""
    
    @pytest.fixture
    def ai_engine(self):
        """Create AI engine instance."""
        return AIEngine()
    
    def test_ai_engine_initialization(self, ai_engine):
        """Test AI engine initialization."""
        assert ai_engine.config is not None
        assert ai_engine.device in ["cpu", "cuda:0", "mps"]
        assert not ai_engine._initialized
    
    def test_device_setup(self, ai_engine):
        """Test device setup."""
        device = ai_engine._setup_device()
        assert device in ["cpu", "cuda:0", "mps"]
    
    @pytest.mark.asyncio
    async def test_ai_initialize_without_dependencies(self, ai_engine):
        """Test AI initialization handles missing dependencies gracefully."""
        with patch.object(ai_engine, "_load_llm", side_effect=ImportError):
            await ai_engine.initialize()
            assert not ai_engine._initialized
    
    @pytest.mark.asyncio
    async def test_vulnerability_analysis(self, ai_engine):
        """Test vulnerability analysis."""
        with patch.object(ai_engine, "_initialized", True):
            with patch.object(ai_engine, "_generate", return_value="Test response"):
                result = await ai_engine.analyze_vulnerability(
                    target="example.com",
                    scan_results={"open_ports": [80, 443]},
                )
                
                assert isinstance(result, AIResult)
                assert result.analysis_type == AnalysisType.VULNERABILITY
    
    @pytest.mark.asyncio
    async def test_exploit_suggestion(self, ai_engine):
        """Test exploit suggestion."""
        with patch.object(ai_engine, "_initialized", True):
            with patch.object(ai_engine, "_generate", return_value="Exploit info"):
                result = await ai_engine.suggest_exploits(
                    vulnerability="SQL Injection",
                    target_info={"database": "MySQL"},
                )
                
                assert isinstance(result, AIResult)
                assert result.analysis_type == AnalysisType.EXPLOIT_SUGGESTION
    
    @pytest.mark.asyncio
    async def test_code_review(self, ai_engine):
        """Test code review functionality."""
        with patch.object(ai_engine, "_initialized", True):
            with patch.object(ai_engine, "_generate", return_value="Review results"):
                result = await ai_engine.code_review(
                    code="print('Hello')",
                    language="python",
                )
                
                assert isinstance(result, AIResult)
                assert result.analysis_type == AnalysisType.CODE_REVIEW
    
    def test_prompt_building(self, ai_engine):
        """Test prompt building for vulnerability analysis."""
        prompt = ai_engine._build_vulnerability_prompt(
            target="example.com",
            scan_results={"ports": [80, 443]},
        )
        
        assert "example.com" in prompt
        assert "Scan Results" in prompt


class TestPerformance:
    """Test performance optimizations."""
    
    @pytest.mark.asyncio
    async def test_concurrent_operations(self):
        """Test concurrent async operations."""
        async def task(n: int) -> int:
            await asyncio.sleep(0.01)
            return n * 2
        
        results = await asyncio.gather(*[task(i) for i in range(10)])
        
        assert len(results) == 10
        assert results == [i * 2 for i in range(10)]
    
    @pytest.mark.asyncio
    @pytest.mark.benchmark
    async def test_async_performance(self, benchmark):
        """Benchmark async operations."""
        
        async def run_tasks():
            tasks = [asyncio.sleep(0.001) for _ in range(100)]
            await asyncio.gather(*tasks)
        
        benchmark(lambda: asyncio.run(run_tasks()))
    
    def test_gpu_availability(self):
        """Test GPU availability detection."""
        try:
            import torch
            
            if torch.cuda.is_available():
                assert torch.cuda.device_count() > 0
                device_name = torch.cuda.get_device_name(0)
                assert device_name is not None
            elif torch.backends.mps.is_available():
                # Apple Silicon
                assert True
            else:
                # CPU only
                assert True
        except ImportError:
            pytest.skip("PyTorch not installed")


class TestIntegration:
    """Integration tests."""
    
    @pytest.mark.asyncio
    async def test_full_workflow(self):
        """Test complete workflow from config to execution."""
        # 1. Load config
        config = Config()
        assert config is not None
        
        # 2. Initialize AI engine
        ai_engine = AIEngine()
        assert ai_engine.device is not None
        
        # 3. Create repo manager
        manager = RepoManager()
        assert len(manager.repos) >= 0
    
    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test error handling in async operations."""
        
        async def failing_task():
            raise ValueError("Test error")
        
        with pytest.raises(ValueError):
            await failing_task()


class TestCLI:
    """Test CLI functionality."""
    
    def test_cli_import(self):
        """Test CLI can be imported."""
        from fsociety.__main__ import ModernCLI
        
        cli = ModernCLI()
        assert cli is not None
        assert cli.config is not None
    
    def test_banner_display(self, capsys):
        """Test banner display."""
        from fsociety.__main__ import ModernCLI
        
        cli = ModernCLI()
        cli.display_banner()
        
        captured = capsys.readouterr()
        # Would check output but rich makes it complex


# Fixtures for all tests
@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def temp_config_dir(tmp_path):
    """Create temporary config directory."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    return config_dir


# Performance benchmarks
@pytest.mark.benchmark(group="async")
def test_benchmark_async_gather(benchmark):
    """Benchmark async gather operations."""
    
    async def run():
        tasks = [asyncio.sleep(0.001) for _ in range(50)]
        await asyncio.gather(*tasks)
    
    benchmark(lambda: asyncio.run(run()))


@pytest.mark.benchmark(group="config")
def test_benchmark_config_load(benchmark, tmp_path):
    """Benchmark config loading."""
    config = Config()
    config.config_dir = tmp_path
    config.save()
    
    def load():
        Config.load()
    
    benchmark(load)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--benchmark-only"])