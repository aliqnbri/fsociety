"""Modern configuration system with type safety and validation."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Self

import orjson
from platformdirs import user_data_dir, user_config_dir

from fsociety.__version__ import __version__


class Platform(str, Enum):
    """Supported platforms."""
    LINUX = "linux"
    MACOS = "macos"
    WINDOWS = "windows"
    BSD = "bsd"
    UNKNOWN = "unknown"


class GPUBackend(str, Enum):
    """GPU acceleration backends."""
    NONE = "none"
    CUDA = "cuda"
    ROCM = "rocm"
    METAL = "metal"
    ONEAPI = "oneapi"


@dataclass
class AIConfig:
    """AI/ML configuration."""
    enabled: bool = False
    model_provider: str = "local"  # local, openai, anthropic
    model_name: str = "mistral-7b"
    api_key: str | None = None
    max_tokens: int = 2048
    temperature: float = 0.7
    use_gpu: bool = True
    gpu_backend: GPUBackend = GPUBackend.CUDA
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    vector_db_path: str | None = None


@dataclass
class PerformanceConfig:
    """Performance optimization settings."""
    max_workers: int = 4
    use_uvloop: bool = True
    enable_caching: bool = True
    cache_ttl: int = 3600
    connection_pool_size: int = 100
    timeout: int = 30
    retry_attempts: int = 3
    use_gpu: bool = False
    gpu_backend: GPUBackend = GPUBackend.NONE


@dataclass
class SecurityConfig:
    """Security settings."""
    ssh_clone: bool = False
    verify_ssl: bool = True
    max_file_size: int = 100 * 1024 * 1024  # 100MB
    allowed_protocols: list[str] = field(default_factory=lambda: ["https", "ssh"])
    rate_limit: int = 100  # requests per minute


@dataclass
class Config:
    """Main configuration class with type safety."""
    
    version: str = __version__
    platform: Platform = Platform.UNKNOWN
    install_dir: Path = field(default_factory=lambda: Path(user_data_dir("fsociety")))
    config_dir: Path = field(default_factory=lambda: Path(user_config_dir("fsociety")))
    
    # Sub-configurations
    ai: AIConfig = field(default_factory=AIConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    
    # User preferences
    agreement: bool = False
    theme: str = "dark"
    host_file: str = "hosts.txt"
    usernames_file: str = "usernames.txt"
    
    # Paths
    github_path: str = "fsociety-team/fsociety"
    
    def __post_init__(self) -> None:
        """Initialize configuration and detect platform."""
        self.platform = self._detect_platform()
        self._ensure_directories()
        self._detect_gpu()
    
    @staticmethod
    def _detect_platform() -> Platform:
        """Detect the current platform."""
        import platform
        import distro
        
        system = platform.system().lower()
        
        match system:
            case "darwin":
                return Platform.MACOS
            case "windows":
                return Platform.WINDOWS
            case "linux":
                return Platform.LINUX
            case "freebsd" | "openbsd" | "netbsd":
                return Platform.BSD
            case _:
                return Platform.UNKNOWN
    
    def _detect_gpu(self) -> None:
        """Detect available GPU backend."""
        try:
            import torch
            if torch.cuda.is_available():
                self.performance.gpu_backend = GPUBackend.CUDA
                self.performance.use_gpu = True
                self.ai.gpu_backend = GPUBackend.CUDA
                self.ai.use_gpu = True
            elif torch.backends.mps.is_available():  # Apple Silicon
                self.performance.gpu_backend = GPUBackend.METAL
                self.performance.use_gpu = True
                self.ai.gpu_backend = GPUBackend.METAL
                self.ai.use_gpu = True
        except ImportError:
            pass
    
    def _ensure_directories(self) -> None:
        """Ensure required directories exist."""
        for directory in [self.install_dir, self.config_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    @property
    def config_file(self) -> Path:
        """Path to the config file."""
        return self.config_dir / "config.json"
    
    @property
    def host_file_path(self) -> Path:
        """Path to the hosts file."""
        return self.install_dir / self.host_file
    
    @property
    def usernames_file_path(self) -> Path:
        """Path to the usernames file."""
        return self.install_dir / self.usernames_file
    
    def save(self) -> None:
        """Save configuration to file."""
        config_dict = {
            "version": self.version,
            "platform": self.platform.value,
            "ai": {
                "enabled": self.ai.enabled,
                "model_provider": self.ai.model_provider,
                "model_name": self.ai.model_name,
                "max_tokens": self.ai.max_tokens,
                "temperature": self.ai.temperature,
                "use_gpu": self.ai.use_gpu,
                "gpu_backend": self.ai.gpu_backend.value,
                "embedding_model": self.ai.embedding_model,
            },
            "performance": {
                "max_workers": self.performance.max_workers,
                "use_uvloop": self.performance.use_uvloop,
                "enable_caching": self.performance.enable_caching,
                "cache_ttl": self.performance.cache_ttl,
                "connection_pool_size": self.performance.connection_pool_size,
                "timeout": self.performance.timeout,
                "retry_attempts": self.performance.retry_attempts,
                "use_gpu": self.performance.use_gpu,
                "gpu_backend": self.performance.gpu_backend.value,
            },
            "security": {
                "ssh_clone": self.security.ssh_clone,
                "verify_ssl": self.security.verify_ssl,
                "max_file_size": self.security.max_file_size,
                "allowed_protocols": self.security.allowed_protocols,
                "rate_limit": self.security.rate_limit,
            },
            "agreement": self.agreement,
            "theme": self.theme,
            "host_file": self.host_file,
            "usernames_file": self.usernames_file,
            "github_path": self.github_path,
        }
        
        self.config_file.write_bytes(orjson.dumps(config_dict, option=orjson.OPT_INDENT_2))
    
    @classmethod
    def load(cls) -> Self:
        """Load configuration from file."""
        config = cls()
        
        if not config.config_file.exists():
            config.save()
            return config
        
        try:
            data = orjson.loads(config.config_file.read_bytes())
            
            # Update AI config
            if "ai" in data:
                for key, value in data["ai"].items():
                    if key == "gpu_backend":
                        value = GPUBackend(value)
                    if hasattr(config.ai, key):
                        setattr(config.ai, key, value)
            
            # Update performance config
            if "performance" in data:
                for key, value in data["performance"].items():
                    if key == "gpu_backend":
                        value = GPUBackend(value)
                    if hasattr(config.performance, key):
                        setattr(config.performance, key, value)
            
            # Update security config
            if "security" in data:
                for key, value in data["security"].items():
                    if hasattr(config.security, key):
                        setattr(config.security, key, value)
            
            # Update main config
            for key in ["agreement", "theme", "host_file", "usernames_file", "github_path"]:
                if key in data:
                    setattr(config, key, data[key])
            
        except Exception as e:
            print(f"Error loading config: {e}. Using defaults.")
        
        return config


# Global config instance
_config: Config | None = None


def get_config() -> Config:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        _config = Config.load()
    return _config


def reload_config() -> Config:
    """Reload configuration from file."""
    global _config
    _config = Config.load()
    return _config