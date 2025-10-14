from __future__ import annotations

import asyncio
from pathlib import Path
from typing import AsyncIterator

import aiofiles

from fsociety.core.config import get_config


class HostManager:
    """Manage target hosts asynchronously."""

    def __init__(self) -> None:
        config = get_config()
        self.host_file = config.host_file_path
        self._ensure_file()

    def _ensure_file(self) -> None:
        """Ensure host file exists."""
        if not self.host_file.exists():
            self.host_file.touch()

    async def get_hosts(self) -> list[str]:
        """Get all hosts asynchronously."""
        try:
            async with aiofiles.open(self.host_file, "r") as f:
                content = await f.read()
                return [
                    line.strip()
                    for line in content.splitlines()
                    if line.strip() and not line.startswith("#")
                ]
        except FileNotFoundError:
            return []

    async def add_host(self, host: str) -> None:
        """Add a new host."""
        if not host or not host.strip():
            raise ValueError("Host cannot be empty")

        hosts = await self.get_hosts()
        if host not in hosts:
            async with aiofiles.open(self.host_file, "a") as f:
                await f.write(f"{host}\n")

    async def remove_host(self, host: str) -> bool:
        """Remove a host."""
        hosts = await self.get_hosts()
        if host in hosts:
            hosts.remove(host)
            async with aiofiles.open(self.host_file, "w") as f:
                await f.write("\n".join(hosts) + "\n")
            return True
        return False

    async def iter_hosts(self) -> AsyncIterator[str]:
        """Iterate over hosts asynchronously."""
        hosts = await self.get_hosts()
        for host in hosts:
            yield host

    async def clear(self) -> None:
        """Clear all hosts."""
        async with aiofiles.open(self.host_file, "w") as f:
            await f.write("")

    async def import_hosts(self, file_path: Path) -> int:
        """Import hosts from a file."""
        count = 0
        async with aiofiles.open(file_path, "r") as f:
            content = await f.read()
            for line in content.splitlines():
                host = line.strip()
                if host and not host.startswith("#"):
                    await self.add_host(host)
                    count += 1
        return count


# Global instances
_host_manager: HostManager | None = None


def get_host_manager() -> HostManager:
    """Get global host manager instance."""
    global _host_manager
    if _host_manager is None:
        _host_manager = HostManager()
    return _host_manager


# Backward compatibility functions
async def get_hosts() -> list[str]:
    """Get all hosts (backward compatible)."""
    return await get_host_manager().get_hosts()


async def add_host(host: str) -> None:
    """Add a host (backward compatible)."""
    await get_host_manager().add_host(host)
