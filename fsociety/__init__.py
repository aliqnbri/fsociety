"""fsociety - AI-Powered High-Performance Penetration Testing Framework."""

from __future__ import annotations

import sys

from fsociety.__version__ import (
    __author__,
    __copyright__,
    __description__,
    __license__,
    __title__,
    __version__,
)

# Minimum Python version check
if sys.version_info < (3, 12):
    raise RuntimeError("fsociety requires Python 3.12 or higher")

# Core imports
from fsociety.console import console
from fsociety.core.config import Config, get_config, reload_config

# AI imports (optional)
try:
    from fsociety.ai import (
        AIEngine,
        AIExploitAssistant,
        get_ai_engine,
        get_exploit_assistant,
    )
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False

# Performance monitoring
from fsociety.core.performance import (
    get_gpu_memory_manager,
    get_performance_monitor,
)

# Caching
from fsociety.core.cache import get_cache_manager

# Repository management
from fsociety.core.async_repo import get_repo_manager

__all__ = [
    # Version info
    "__version__",
    "__title__",
    "__description__",
    "__author__",
    "__license__",
    "__copyright__",
    # Core
    "console",
    "Config",
    "get_config",
    "reload_config",
    # Managers
    "get_repo_manager",
    "get_cache_manager",
    "get_performance_monitor",
    "get_gpu_memory_manager",
    # Constants
    "AI_AVAILABLE",
]

# Add AI exports if available
if AI_AVAILABLE:
    __all__.extend([
        "AIEngine",
        "AIExploitAssistant",
        "get_ai_engine",
        "get_exploit_assistant",
    ])


def info() -> None:
    """Print fsociety information."""
    from rich.panel import Panel
    from rich.table import Table
    
    table = Table(show_header=False, box=None)
    table.add_column("Key", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Version", __version__)
    table.add_row("Python", f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    table.add_row("Platform", sys.platform)
    table.add_row("AI Available", "Yes" if AI_AVAILABLE else "No")
    
    config = get_config()
    if config.performance.use_gpu:
        table.add_row("GPU Backend", config.performance.gpu_backend.value)
    
    panel = Panel(table, title="fsociety Information", border_style="cyan")
    console.print(panel)


# Setup logging
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)