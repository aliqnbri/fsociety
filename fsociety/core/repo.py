"""
Modern GitHub repository management with Python 3.12 features.

This module provides secure, type-safe repository cloning, installation,
and execution capabilities for fsociety tools.
"""

from __future__ import annotations

from abc import ABCMeta, abstractmethod
from pathlib import Path
from shutil import rmtree, which
from typing import Any

from git import RemoteProgress, Repo
from rich.progress import BarColumn, Progress, TaskID
from rich.table import Table

from fsociety.console import console
from fsociety.core.cache import cached
from fsociety.core.config import INSTALL_DIR, get_config
from fsociety.core.executor import (
    ExecutionError,
    ExecutionResult,
    change_directory,
    execute_command,
)
from fsociety.core.logging_config import get_logger
from fsociety.core.menu import confirm

logger = get_logger(__name__)
config = get_config()


class InstallError(Exception):
    """Raised when installation fails."""

    pass


class CloneError(Exception):
    """Raised when cloning fails."""

    pass


class GitProgress(RemoteProgress):
    """Progress reporter for git operations."""

    def __init__(self) -> None:
        super().__init__()
        self.progress = Progress(
            "[progress.description]{task.description}",
            BarColumn(None),
            "[progress.percentage]{task.percentage:>3.0f}%",
            "[progress.filesize]{task.fields[msg]}",
        )
        self.current_opcode: int | None = None
        self.task: TaskID | None = None

    def update(
        self,
        opcode: int,
        count: int,
        max_value: int,
        msg: str | None = None,
    ) -> None:
        """Update progress bar based on git operation."""
        opcode_strs = {
            self.COUNTING: "Counting",
            self.COMPRESSING: "Compressing",
            self.WRITING: "Writing",
            self.RECEIVING: "Receiving",
            self.RESOLVING: "Resolving",
            self.FINDING_SOURCES: "Finding sources",
            self.CHECKING_OUT: "Checking out",
        }
        stage, real_opcode = opcode & self.STAGE_MASK, opcode & self.OP_MASK

        try:
            count = int(count)
            max_value = int(max_value)
        except ValueError:
            return

        if self.current_opcode != real_opcode:
            if self.task:
                self.progress.update(
                    self.task, total=1, completed=1, msg=""
                )
            self.current_opcode = real_opcode
            self.task = self.progress.add_task(
                opcode_strs[real_opcode].ljust(15), msg=""
            )

        if stage & self.BEGIN:
            self.progress.start()
        if stage & self.END:
            self.progress.stop()
        if self.task:
            self.progress.update(
                self.task, msg=msg or "", total=max_value, completed=count
            )


def print_pip_deps(packages: str | list[str]) -> None:
    """
    Display pip dependencies in a formatted table.

    Args:
        packages: Path to requirements.txt or list of package names
    """
    requirements: list[str] = []

    match packages:
        case str(path) if Path(path).exists():
            with open(path, encoding="utf-8") as req_file:
                requirements = [
                    line.strip()
                    for line in req_file
                    if line.strip() and not line.startswith("#")
                ]
        case list(pkgs):
            requirements = pkgs
        case _:
            logger.error(f"Invalid packages format: {type(packages)}")
            raise ValueError("Invalid packages format")

    table = Table("Packages", title="Pip Dependencies")
    for req in requirements:
        table.add_row(req)

    console.print()
    console.print(table)


# Python 3.12 type alias
InstallConfig = str | dict[str, str | list[str]]


class GitHubRepo(metaclass=ABCMeta):
    """
    Base class for GitHub repository-based tools.

    This class provides secure installation and execution capabilities
    for security tools hosted on GitHub.
    """

    def __init__(
        self,
        path: str = "fsociety-team/fsociety",
        install: InstallConfig = "pip install -e .",
        description: str | None = None,
    ) -> None:
        """
        Initialize a GitHub repository tool.

        Args:
            path: GitHub repository path (e.g., "owner/repo")
            install: Installation configuration (command or dict)
            description: Tool description
        """
        self.path = path
        self.name = self.path.split("/")[-1]
        self.install_options = install
        self.full_path = Path(INSTALL_DIR) / self.name
        self.description = description
        self.scriptable_os = ["debian", "windows", "macos", "arch"]

        logger.debug(f"Initialized {self.name} at {self.full_path}")

    def __str__(self) -> str:
        """Return normalized tool name."""
        return self.name.lower().replace("-", "_")

    @cached(ttl=300)
    def _get_clone_url(self) -> str:
        """Get clone URL based on configuration."""
        if config.getboolean("fsociety", "ssh_clone"):
            return f"git@github.com:{self.path}.git"
        return f"https://github.com/{self.path}"

    def clone(self, overwrite: bool = False) -> Path:
        """
        Clone or update the repository.

        Args:
            overwrite: Whether to overwrite existing repository

        Returns:
            Path to cloned repository

        Raises:
            CloneError: If cloning fails
        """
        logger.info(f"Cloning {self.path}...")

        try:
            if self.full_path.exists():
                if not overwrite:
                    logger.debug(f"Pulling latest changes for {self.name}")
                    repo = Repo(str(self.full_path))
                    repo.remotes.origin.pull()
                    return self.full_path

                logger.warning(f"Removing existing {self.name}")
                rmtree(self.full_path)

            url = self._get_clone_url()
            logger.info(f"Cloning from {url}")

            Repo.clone_from(url, str(self.full_path), progress=GitProgress())

            if not self.full_path.exists():
                raise CloneError(f"{self.full_path} not found after clone")

            logger.info(f"Successfully cloned {self.name}")
            return self.full_path

        except Exception as e:
            logger.error(f"Clone failed: {e}")
            raise CloneError(f"Failed to clone {self.path}: {e}") from e

    def _install_pip(
        self, packages: str | list[str]
    ) -> ExecutionResult:
        """Install pip packages."""
        match packages:
            case list(pkg_list):
                logger.info(f"Installing pip packages: {pkg_list}")
                print_pip_deps(pkg_list)

                if not confirm(
                    "Do you want to install these packages?"
                ):
                    raise InstallError("User cancelled")

                packages_str = " ".join(pkg_list)
                command = ["pip", "install", *pkg_list]

            case str(req_file):
                requirements_path = self.full_path / "requirements.txt"
                logger.info(f"Installing from {requirements_path}")
                print_pip_deps(str(requirements_path))

                if not confirm(
                    f"Do you want to install packages from {requirements_path}?"
                ):
                    raise InstallError("User cancelled")

                command = ["pip", "install", "-r", str(requirements_path)]

            case _:
                raise InstallError(f"Invalid pip config: {packages}")

        return execute_command(command, timeout=600)

    def _install_go(self, go_command: str) -> ExecutionResult:
        """Install using go."""
        if not which("go"):
            raise InstallError("Go is not installed")

        logger.info(f"Installing with go: {go_command}")
        return execute_command(go_command, shell=True, timeout=600)

    def _install_binary(self, binary_url: str) -> ExecutionResult:
        """Download and install binary."""
        logger.info(f"Downloading binary from {binary_url}")

        # Ensure directory exists
        self.full_path.mkdir(parents=True, exist_ok=True)

        binary_path = self.full_path / self.name

        # Download based on available tools
        if which("curl"):
            download_cmd = [
                "curl",
                "-L",
                "-o",
                str(binary_path),
                "-s",
                binary_url,
            ]
        elif which("wget"):
            download_cmd = [
                "wget",
                "-q",
                "-O",
                str(binary_path),
                binary_url,
            ]
        else:
            raise InstallError(
                "Neither curl nor wget is available for download"
            )

        # Download
        result = execute_command(download_cmd, timeout=300)

        # Make executable
        if result.success:
            execute_command(["chmod", "+x", str(binary_path)])

        return result

    def _install_brew(self, brew_opts: str) -> ExecutionResult:
        """Install using Homebrew."""
        if not which("brew"):
            raise InstallError("Homebrew is not installed")

        logger.info(f"Installing with brew: {brew_opts}")
        command = ["brew"] + brew_opts.split()
        return execute_command(command, timeout=600)

    def install(
        self, no_confirm: bool = False, clone: bool = True
    ) -> None:
        """
        Install the tool.

        Args:
            no_confirm: Skip confirmation prompts
            clone: Whether to clone repository first

        Raises:
            InstallError: If installation fails
        """
        if not no_confirm and not confirm(
            f"\nDo you want to install https://github.com/{self.path}?"
        ):
            logger.info("Installation cancelled by user")
            console.print("Cancelled")
            return

        try:
            # Clone repository if needed
            if clone:
                self.clone()

            # No installation needed
            if not self.install_options:
                logger.info(f"{self.name} installed (no build required)")
                return

            # Execute installation based on type
            install_dir = self.full_path if clone else Path(INSTALL_DIR)

            with change_directory(install_dir):
                match self.install_options:
                    case dict(options):
                        self._install_from_dict(options)
                    case str(command):
                        logger.info(f"Running install command: {command}")
                        execute_command(command, shell=True, timeout=600)
                    case _:
                        raise InstallError(
                            f"Invalid install config: {self.install_options}"
                        )

            logger.info(f"{self.name} installed successfully")

        except ExecutionError as e:
            logger.error(f"Installation failed: {e}")
            raise InstallError(f"Failed to install {self.name}: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error during installation: {e}")
            raise InstallError(
                f"Installation failed with unexpected error: {e}"
            ) from e

    def _install_from_dict(self, options: dict[str, Any]) -> None:
        """Handle dictionary-based installation configuration."""
        target_os = config.get("fsociety", "os")

        match options:
            case {"pip": packages}:
                self._install_pip(packages)

            case {"go": go_cmd} if which("go"):
                self._install_go(go_cmd)

            case {"binary": bin_url}:
                self._install_binary(bin_url)

            case {"brew": brew_opts} if which("brew"):
                self._install_brew(brew_opts)

            case {**opts} if target_os in opts and target_os in self.scriptable_os:
                command = str(opts[target_os])
                logger.info(f"Running platform-specific command: {command}")
                execute_command(command, shell=True, timeout=600)

            case _:
                available_keys = list(options.keys())
                raise InstallError(
                    f"Platform not supported. Available options: {available_keys}. "
                    f"Missing required tools or unsupported OS: {target_os}"
                )

    def installed(self) -> bool:
        """
        Check if tool is installed.

        Returns:
            True if tool is installed, False otherwise
        """
        is_installed = self.full_path.exists()
        logger.debug(f"{self.name} installed: {is_installed}")
        return is_installed

    @abstractmethod
    def run(self) -> int:
        """
        Run the tool.

        Returns:
            Exit code (0 for success, non-zero for failure)
        """
        pass
