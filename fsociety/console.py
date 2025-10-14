"""Enhanced console with modern Rich features and custom themes."""

from __future__ import annotations

from rich.console import Console
from rich.theme import Theme
from rich.traceback import install
from rich.logging import RichHandler
import logging

# Install rich traceback handler
install(show_locals=True, max_frames=10)

# Custom theme for fsociety
fsociety_theme = Theme({
    "command": "black on white bold",
    "warning": "bold yellow",
    "error": "bold red",
    "success": "bold green",
    "info": "bold cyan",
    "dim": "dim white",
    "highlight": "bold magenta",
    "url": "blue underline",
    "code": "green",
    "path": "cyan",
    "number": "yellow",
    # Security-related styles
    "vulnerability.critical": "bold white on red",
    "vulnerability.high": "bold red",
    "vulnerability.medium": "bold yellow",
    "vulnerability.low": "bold green",
    "exploit": "bold magenta",
    "target": "bold cyan",
    # Tool categories
    "tool.info": "cyan",
    "tool.network": "blue",
    "tool.web": "magenta",
    "tool.password": "yellow",
    "tool.exploit": "red",
})

# Create console with custom theme
console = Console(
    theme=fsociety_theme,
    highlight=True,
    force_terminal=True,
    force_interactive=True,
)

# Setup logging with Rich
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(
        console=console,
        rich_tracebacks=True,
        tracebacks_show_locals=True,
    )]
)

logger = logging.getLogger("fsociety")


# Utility functions for common console operations
def print_banner(text: str, style: str = "bold red") -> None:
    """Print a banner."""
    console.print(text, style=style, highlight=False)


def print_success(message: str) -> None:
    """Print success message."""
    console.print(f"✓ {message}", style="success")


def print_error(message: str) -> None:
    """Print error message."""
    console.print(f"✗ {message}", style="error")


def print_warning(message: str) -> None:
    """Print warning message."""
    console.print(f"⚠ {message}", style="warning")


def print_info(message: str) -> None:
    """Print info message."""
    console.print(f"ℹ {message}", style="info")


def print_vulnerability(severity: str, message: str) -> None:
    """Print vulnerability with appropriate styling."""
    style = f"vulnerability.{severity.lower()}"
    icon = {
        "critical": "🔴",
        "high": "🔴",
        "medium": "🟡",
        "low": "🟢",
    }.get(severity.lower(), "⚪")
    
    console.print(f"{icon} [{severity.upper()}] {message}", style=style)


def confirm_action(message: str, default: bool = False) -> bool:
    """Ask for user confirmation."""
    default_str = "Y/n" if default else "y/N"
    response = input(f"{message} ({default_str}): ").strip().lower()
    
    if not response:
        return default
    
    return response in ("y", "yes")