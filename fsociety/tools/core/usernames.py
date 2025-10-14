from __future__ import annotations

import asyncio
from pathlib import Path
from typing import AsyncIterator

import aiofiles

from fsociety.core.config import get_config


class UsernameManager:
    """Manage usernames asynchronously."""

    def __init__(self) -> None:
        config = get_config()
        self.username_file = config.usernames_file_path
        self._ensure_file()

    def _ensure_file(self) -> None:
        """Ensure username file exists."""
        if not self.username_file.exists():
            self.username_file.touch()

    async def get_usernames(self) -> list[str]:
        """Get all usernames asynchronously."""
        try:
            async with aiofiles.open(self.username_file, "r") as f:
                content = await f.read()
                return [
                    line.strip()
                    for line in content.splitlines()
                    if line.strip() and not line.startswith("#")
                ]
        except FileNotFoundError:
            return []

    async def add_username(self, username: str) -> None:
        """Add a new username."""
        if not username or not username.strip():
            raise ValueError("Username cannot be empty")

        usernames = await self.get_usernames()
        if username not in usernames:
            async with aiofiles.open(self.username_file, "a") as f:
                await f.write(f"{username}\n")

    async def remove_username(self, username: str) -> bool:
        """Remove a username."""
        usernames = await self.get_usernames()
        if username in usernames:
            usernames.remove(username)
            async with aiofiles.open(self.username_file, "w") as f:
                await f.write("\n".join(usernames) + "\n")
            return True
        return False

    async def iter_usernames(self) -> AsyncIterator[str]:
        """Iterate over usernames asynchronously."""
        usernames = await self.get_usernames()
        for username in usernames:
            yield username

    async def clear(self) -> None:
        """Clear all usernames."""
        async with aiofiles.open(self.username_file, "w") as f:
            await f.write("")

    async def import_usernames(self, file_path: Path) -> int:
        """Import usernames from a file."""
        count = 0
        async with aiofiles.open(file_path, "r") as f:
            content = await f.read()
            for line in content.splitlines():
                username = line.strip()
                if username and not username.startswith("#"):
                    await self.add_username(username)
                    count += 1
        return count


# Global instances
_username_manager: UsernameManager | None = None


def get_host_manager() -> HostManager:
    """Get global host manager instance."""
    global _host_manager
    if _host_manager is None:
        _host_manager = HostManager()
    return _host_manager


def get_username_manager() -> UsernameManager:
    """Get global username manager instance."""
    global _username_manager
    if _username_manager is None:
        _username_manager = UsernameManager()
    return _username_manager


async def get_usernames() -> list[str]:
    """Get all usernames (backward compatible)."""
    return await get_username_manager().get_usernames()


async def add_username(username: str) -> None:
    """Add a username (backward compatible)."""
    await get_username_manager().add_username(username)
