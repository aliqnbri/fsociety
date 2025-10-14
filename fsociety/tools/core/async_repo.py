"""Async repository management with GPU acceleration support."""

from __future__ import annotations

import asyncio
import shutil
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Coroutine

import aiofiles
import httpx
from git import Repo, RemoteProgress
from rich.progress import Progress, TaskID, BarColumn, TimeRemainingColumn

from fsociety.console import console
from fsociety.core.config import get_config


@dataclass
class InstallOptions:
    """Installation options for a repository."""
    pip: str | list[str] | None = None
    binary: str | None = None
    go: str | None = None
    brew: str | None = None
    platform_specific: dict[str, str] | None = None


class AsyncGitProgress(RemoteProgress):
    """Async git progress reporter."""
    
    def __init__(self) -> None:
        super().__init__()
        self.progress = Progress(
            "[progress.description]{task.description}",
            BarColumn(),
            "[progress.percentage]{task.percentage:>3.0f}%",
            TimeRemainingColumn(),
        )
        self.task: TaskID | None = None
        self.current_op: int | None = None
    
    def update(
        self,
        op_code: int,
        cur_count: int | str,
        max_count: int | str | None = None,
        message: str = "",
    ) -> None:
        """Update progress display."""
        op_names = {
            self.COUNTING: "Counting",
            self.COMPRESSING: "Compressing",
            self.WRITING: "Writing",
            self.RECEIVING: "Receiving",
            self.RESOLVING: "Resolving",
            self.FINDING_SOURCES: "Finding sources",
            self.CHECKING_OUT: "Checking out",
        }
        
        stage = op_code & self.STAGE_MASK
        real_op = op_code & self.OP_MASK
        
        try:
            cur_count = int(cur_count)
            max_count = int(max_count) if max_count else 100
        except (ValueError, TypeError):
            return
        
        if self.current_op != real_op:
            if self.task:
                self.progress.update(self.task, completed=max_count)
            self.current_op = real_op
            op_name = op_names.get(real_op, "Processing")
            self.task = self.progress.add_task(f"[cyan]{op_name}", total=max_count)
        
        if stage & self.BEGIN:
            self.progress.start()
        
        if self.task:
            self.progress.update(self.task, completed=cur_count)
        
        if stage & self.END:
            self.progress.stop()


class AsyncGitHubRepo(ABC):
    """Modern async GitHub repository manager."""
    
    def __init__(
        self,
        path: str,
        install: InstallOptions | dict[str, Any] | str | None = None,
        description: str | None = None,
    ) -> None:
        self.path = path
        self.name = path.split("/")[-1]
        self.description = description or f"GitHub repository: {path}"
        
        # Parse install options
        if isinstance(install, dict):
            self.install_opts = InstallOptions(**install)
        elif isinstance(install, str):
            self.install_opts = InstallOptions(pip=install)
        else:
            self.install_opts = install or InstallOptions()
        
        self.config = get_config()
        self.full_path = self.config.install_dir / self.name
    
    def __str__(self) -> str:
        return self.name.lower().replace("-", "_")
    
    async def clone(self, overwrite: bool = False) -> Path:
        """Clone repository asynchronously."""
        if self.full_path.exists():
            if not overwrite:
                # Pull latest changes
                await asyncio.to_thread(self._pull_repo)
                return self.full_path
            shutil.rmtree(self.full_path)
        
        url = f"https://github.com/{self.path}"
        if self.config.security.ssh_clone:
            url = f"git@github.com:{self.path}.git"
        
        console.print(f"[cyan]Cloning {self.path}...")
        await asyncio.to_thread(
            Repo.clone_from,
            url,
            self.full_path,
            progress=AsyncGitProgress(),
        )
        
        return self.full_path
    
    def _pull_repo(self) -> None:
        """Pull latest changes from remote."""
        repo = Repo(self.full_path)
        origin = repo.remotes.origin
        origin.pull()
    
    async def install(self, no_confirm: bool = False) -> None:
        """Install repository dependencies."""
        if not no_confirm:
            response = input(
                f"\n[yellow]Install {self.path}? (y/N):[/yellow] "
            ).lower()
            if response != "y":
                console.print("[red]Installation cancelled.")
                return
        
        await self.clone()
        
        # Install based on options
        if self.install_opts.pip:
            await self._install_pip()
        elif self.install_opts.binary:
            await self._install_binary()
        elif self.install_opts.go:
            await self._install_go()
        elif self.install_opts.brew:
            await self._install_brew()
        elif self.install_opts.platform_specific:
            await self._install_platform_specific()
    
    async def _install_pip(self) -> None:
        """Install Python dependencies."""
        if isinstance(self.install_opts.pip, list):
            packages = " ".join(self.install_opts.pip)
            cmd = f"pip install {packages}"
        else:
            req_file = self.full_path / "requirements.txt"
            cmd = f"pip install -r {req_file}"
        
        console.print(f"[cyan]Installing Python dependencies...")
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await proc.communicate()
    
    async def _install_binary(self) -> None:
        """Download and install binary."""
        if not self.install_opts.binary:
            return
        
        async with httpx.AsyncClient() as client:
            response = await client.get(self.install_opts.binary)
            binary_path = self.full_path / self.name
            
            async with aiofiles.open(binary_path, "wb") as f:
                await f.write(response.content)
            
            binary_path.chmod(0o755)
    
    async def _install_go(self) -> None:
        """Install Go package."""
        if not self.install_opts.go:
            return
        
        proc = await asyncio.create_subprocess_shell(
            self.install_opts.go,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await proc.communicate()
    
    async def _install_brew(self) -> None:
        """Install with Homebrew."""
        if not self.install_opts.brew:
            return
        
        cmd = f"brew {self.install_opts.brew}"
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await proc.communicate()
    
    async def _install_platform_specific(self) -> None:
        """Install using platform-specific commands."""
        if not self.install_opts.platform_specific:
            return
        
        platform = self.config.platform.value
        if platform not in self.install_opts.platform_specific:
            console.print(f"[red]Platform {platform} not supported.")
            return
        
        cmd = self.install_opts.platform_specific[platform]
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await proc.communicate()
    
    def installed(self) -> bool:
        """Check if repository is installed."""
        return self.full_path.exists()
    
    @abstractmethod
    async def run(self) -> int:
        """Run the tool (must be implemented by subclass)."""
        pass
    
    async def run_command(self, cmd: str, cwd: Path | None = None) -> tuple[str, str, int]:
        """Run a command asynchronously and return output."""
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=cwd or self.full_path,
        )
        
        stdout, stderr = await proc.communicate()
        return (
            stdout.decode() if stdout else "",
            stderr.decode() if stderr else "",
            proc.returncode or 0,
        )


class RepoManager:
    """Manager for multiple repositories with concurrent operations."""
    
    def __init__(self) -> None:
        self.repos: dict[str, AsyncGitHubRepo] = {}
        self.config = get_config()
    
    def register(self, repo: AsyncGitHubRepo) -> None:
        """Register a repository."""
        self.repos[str(repo)] = repo
    
    async def install_all(
        self,
        repos: list[AsyncGitHubRepo] | None = None,
        max_concurrent: int | None = None,
    ) -> None:
        """Install multiple repositories concurrently."""
        repos = repos or list(self.repos.values())
        max_concurrent = max_concurrent or self.config.performance.max_workers
        
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def install_with_semaphore(repo: AsyncGitHubRepo) -> None:
            async with semaphore:
                await repo.install(no_confirm=True)
        
        tasks = [install_with_semaphore(repo) for repo in repos]
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def update_all(self) -> None:
        """Update all installed repositories."""
        installed = [repo for repo in self.repos.values() if repo.installed()]
        
        async def update_repo(repo: AsyncGitHubRepo) -> None:
            try:
                await repo.clone(overwrite=False)
                console.print(f"[green]✓ Updated {repo.name}")
            except Exception as e:
                console.print(f"[red]✗ Failed to update {repo.name}: {e}")
        
        tasks = [update_repo(repo) for repo in installed]
        await asyncio.gather(*tasks, return_exceptions=True)


# Global repo manager
_repo_manager: RepoManager | None = None


def get_repo_manager() -> RepoManager:
    """Get the global repository manager."""
    global _repo_manager
    if _repo_manager is None:
        _repo_manager = RepoManager()
    return _repo_manager