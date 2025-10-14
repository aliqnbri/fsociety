"""GPU acceleration tests for fsociety."""

from __future__ import annotations

import asyncio
import time

import pytest

from fsociety.core.config import get_config, GPUBackend
from fsociety.core.performance import get_gpu_memory_manager


class TestGPUDetection:
    """Test GPU detection and initialization."""
    
    def test_gpu_backend_detection(self):
        """Test GPU backend detection."""
        config = get_config()
        
        assert config.performance.gpu_backend in GPUBackend
        
        # Check if GPU is available
        try:
            import torch
            
            if torch.cuda.is_available():
                assert config.performance.gpu_backend == GPUBackend.CUDA
                assert config.performance.use_gpu is True
            elif torch.backends.mps.is_available():
                assert config.performance.gpu_backend == GPUBackend.METAL
                assert config.performance.use_gpu is True
        except ImportError:
            pytest.skip("PyTorch not installed")
    
    def test_cuda_availability(self):
        """Test CUDA availability and properties."""
        try:
            import torch
            
            if not torch.cuda.is_available():
                pytest.skip("CUDA not available")
            
            # Test device count
            device_count = torch.cuda.device_count()
            assert device_count > 0
            
            # Test device properties
            for i in range(device_count):
                props = torch.cuda.get_device_properties(i)
                assert props.total_memory > 0
                assert len(props.name) > 0
                
                print(f"\nGPU {i}: {props.name}")
                print(f"Memory: {props.total_memory / 1e9:.2f} GB")
                print(f"Compute Capability: {props.major}.{props.minor}")
        
        except ImportError:
            pytest.skip("PyTorch not installed")
    
    def test_metal_availability(self):
        """Test Metal (Apple Silicon) availability."""
        try:
            import torch
            
            if not torch.backends.mps.is_available():
                pytest.skip("Metal not available")
            
            # Test MPS device
            device = torch.device("mps")
            x = torch.randn(100, 100, device=device)
            assert x.device.type == "mps"
            
        except ImportError:
            pytest.skip("PyTorch not installed")


class TestGPUOperations:
    """Test GPU-accelerated operations."""
    
    def test_gpu_tensor_operations(self):
        """Test basic tensor operations on GPU."""
        try:
            import torch
            
            if not torch.cuda.is_available():
                pytest.skip("CUDA not available")
            
            device = torch.device("cuda:0")
            
            # Create tensors on GPU
            a = torch.randn(1000, 1000, device=device)
            b = torch.randn(1000, 1000, device=device)
            
            # Perform operations
            c = torch.matmul(a, b)
            
            assert c.device.type == "cuda"
            assert c.shape == (1000, 1000)
            
        except ImportError:
            pytest.skip("PyTorch not installed")
    
    def test_gpu_performance_vs_cpu(self):
        """Compare GPU vs CPU performance."""
        try:
            import torch
            
            if not torch.cuda.is_available():
                pytest.skip("CUDA not available")
            
            size = 2000
            
            # CPU benchmark
            cpu_device = torch.device("cpu")
            a_cpu = torch.randn(size, size, device=cpu_device)
            b_cpu = torch.randn(size, size, device=cpu_device)
            
            start = time.perf_counter()
            c_cpu = torch.matmul(a_cpu, b_cpu)
            cpu_time = time.perf_counter() - start
            
            # GPU benchmark
            gpu_device = torch.device("cuda:0")
            a_gpu = torch.randn(size, size, device=gpu_device)
            b_gpu = torch.randn(size, size, device=gpu_device)
            
            # Warm up
            _ = torch.matmul(a_gpu, b_gpu)
            torch.cuda.synchronize()
            
            start = time.perf_counter()
            c_gpu = torch.matmul(a_gpu, b_gpu)
            torch.cuda.synchronize()
            gpu_time = time.perf_counter() - start
            
            speedup = cpu_time / gpu_time
            
            print(f"\nMatrix Multiply ({size}x{size}):")
            print(f"CPU Time: {cpu_time:.4f}s")
            print(f"GPU Time: {gpu_time:.4f}s")
            print(f"Speedup: {speedup:.2f}x")
            
            # GPU should be faster for this size
            assert speedup > 1.0
            
        except ImportError:
            pytest.skip("PyTorch not installed")
    
    @pytest.mark.asyncio
    async def test_async_gpu_operations(self):
        """Test asynchronous GPU operations."""
        try:
            import torch
            
            if not torch.cuda.is_available():
                pytest.skip("CUDA not available")
            
            device = torch.device("cuda:0")
            
            async def gpu_task(size: int) -> float:
                """Perform GPU operation asynchronously."""
                a = torch.randn(size, size, device=device)
                b = torch.randn(size, size, device=device)
                
                result = await asyncio.to_thread(torch.matmul, a, b)
                torch.cuda.synchronize()
                
                return result.sum().item()
            
            # Run multiple GPU tasks concurrently
            tasks = [gpu_task(500) for _ in range(5)]
            results = await asyncio.gather(*tasks)
            
            assert len(results) == 5
            assert all(isinstance(r, float) for r in results)
            
        except ImportError:
            pytest.skip("PyTorch not installed")


class TestGPUMemoryManagement:
    """Test GPU memory management."""
    
    def test_memory_info(self):
        """Test GPU memory information retrieval."""
        gpu_manager = get_gpu_memory_manager()
        
        if not gpu_manager.torch_available:
            pytest.skip("PyTorch not available")
        
        info = gpu_manager.get_memory_info()
        
        if info:  # Only if GPU is available
            assert "allocated_gb" in info
            assert "reserved_gb" in info
            assert "total_gb" in info
            assert "free_gb" in info
            assert "utilization" in info
            
            assert info["total_gb"] > 0
            assert 0 <= info["utilization"] <= 100
    
    def test_cache_clearing(self):
        """Test GPU cache clearing."""
        try:
            import torch
            
            if not torch.cuda.is_available():
                pytest.skip("CUDA not available")
            
            gpu_manager = get_gpu_memory_manager()
            
            # Allocate memory
            device = torch.device("cuda:0")
            x = torch.randn(1000, 1000, device=device)
            
            # Get memory before clearing
            before = gpu_manager.get_memory_info()
            
            # Clear cache
            gpu_manager.clear_cache()
            
            # Get memory after clearing
            after = gpu_manager.get_memory_info()
            
            # Reserved memory should decrease
            assert after["reserved_gb"] <= before["reserved_gb"]
            
        except ImportError:
            pytest.skip("PyTorch not installed")
    
    @pytest.mark.asyncio
    async def test_auto_cleanup(self):
        """Test automatic GPU memory cleanup."""
        try:
            import torch
            
            if not torch.cuda.is_available():
                pytest.skip("CUDA not available")
            
            gpu_manager = get_gpu_memory_manager()
            device = torch.device("cuda:0")
            
            before = gpu_manager.get_memory_info()
            
            # Use auto cleanup context
            async with gpu_manager.auto_cleanup():
                # Allocate temporary memory
                x = torch.randn(1000, 1000, device=device)
                y = torch.randn(1000, 1000, device=device)
                z = torch.matmul(x, y)
            
            # Memory should be cleaned up
            after = gpu_manager.get_memory_info()
            
            # Check that cleanup occurred
            assert after["reserved_gb"] <= before["reserved_gb"] + 0.1
            
        except ImportError:
            pytest.skip("PyTorch not installed")


class TestAIGPUAcceleration:
    """Test AI operations with GPU acceleration."""
    
    @pytest.mark.asyncio
    async def test_ai_engine_gpu_device(self):
        """Test AI engine uses GPU when available."""
        from fsociety.ai.engine import AIEngine
        
        config = get_config()
        
        if not config.ai.enabled:
            pytest.skip("AI features disabled")
        
        ai_engine = AIEngine()
        
        try:
            import torch
            
            if torch.cuda.is_available():
                assert "cuda" in ai_engine.device
            elif torch.backends.mps.is_available():
                assert ai_engine.device == "mps"
            else:
                assert ai_engine.device == "cpu"
        
        except ImportError:
            pytest.skip("PyTorch not installed")
    
    @pytest.mark.asyncio
    async def test_embedding_gpu_acceleration(self):
        """Test embedding generation on GPU."""
        try:
            from sentence_transformers import SentenceTransformer
            import torch
            
            if not torch.cuda.is_available():
                pytest.skip("CUDA not available")
            
            # Test CPU
            model_cpu = SentenceTransformer("all-MiniLM-L6-v2", device="cpu")
            sentences = ["This is a test sentence."] * 100
            
            start = time.perf_counter()
            embeddings_cpu = model_cpu.encode(sentences)
            cpu_time = time.perf_counter() - start
            
            # Test GPU
            model_gpu = SentenceTransformer("all-MiniLM-L6-v2", device="cuda")
            
            start = time.perf_counter()
            embeddings_gpu = model_gpu.encode(sentences)
            gpu_time = time.perf_counter() - start
            
            speedup = cpu_time / gpu_time
            
            print(f"\nEmbedding Generation (100 sentences):")
            print(f"CPU Time: {cpu_time:.4f}s")
            print(f"GPU Time: {gpu_time:.4f}s")
            print(f"Speedup: {speedup:.2f}x")
            
            assert speedup > 1.0
            
        except ImportError:
            pytest.skip("Required packages not installed")


class TestGPUBenchmarks:
    """Benchmark GPU performance."""
    
    @pytest.mark.benchmark
    def test_benchmark_gpu_matmul(self, benchmark):
        """Benchmark GPU matrix multiplication."""
        try:
            import torch
            
            if not torch.cuda.is_available():
                pytest.skip("CUDA not available")
            
            device = torch.device("cuda:0")
            size = 2000
            
            def matmul():
                a = torch.randn(size, size, device=device)
                b = torch.randn(size, size, device=device)
                c = torch.matmul(a, b)
                torch.cuda.synchronize()
                return c
            
            benchmark(matmul)
            
        except ImportError:
            pytest.skip("PyTorch not installed")
    
    @pytest.mark.benchmark
    def test_benchmark_cpu_vs_gpu(self, benchmark):
        """Benchmark CPU vs GPU operations."""
        try:
            import torch
            
            if not torch.cuda.is_available():
                pytest.skip("CUDA not available")
            
            size = 1000
            
            # Create data
            a_cpu = torch.randn(size, size)
            b_cpu = torch.randn(size, size)
            
            a_gpu = a_cpu.cuda()
            b_gpu = b_cpu.cuda()
            
            # Benchmark both
            def cpu_op():
                return torch.matmul(a_cpu, b_cpu)
            
            def gpu_op():
                result = torch.matmul(a_gpu, b_gpu)
                torch.cuda.synchronize()
                return result
            
            cpu_result = benchmark(cpu_op)
            # Note: Would need separate benchmark run for GPU
            
        except ImportError:
            pytest.skip("PyTorch not installed")


@pytest.fixture(scope="module")
def gpu_available():
    """Check if GPU is available."""
    try:
        import torch
        return torch.cuda.is_available() or torch.backends.mps.is_available()
    except ImportError:
        return False


def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "gpu: mark test as requiring GPU"
    )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])