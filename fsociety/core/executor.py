"""
Secure command execution module for fsociety.

This module provides safe subprocess execution with proper error handling,
timeout support, and shell injection prevention.
"""

from __future__ import annotations

import asyncio
import logging
import shlex
import subprocess
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from fsociety.core.validation import sanitize_shell_arg


logger = logging.getLogger(__name__)


class ExecutionError(Exception):
    """Raised when command execution fails."""

    def __init__(
        self,
        message: str,
        returncode: int | None = None,
        stdout: str | None = None,
        stderr: str | None = None,
    ) -> None:
        super().__init__(message)
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


class ExecutionResult:
    """Result of command execution."""

    def __init__(
        self,
        returncode: int,
        stdout: str,
        stderr: str,
        success: bool,
    ) -> None:
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr
        self.success = success

    def __bool__(self) -> bool:
        """Return True if execution was successful."""
        return self.success

    def __str__(self) -> str:
        """String representation of result."""
        status = "SUCCESS" if self.success else "FAILED"
        return f"ExecutionResult({status}, returncode={self.returncode})"


@contextmanager
def change_directory(path: str | Path):
    """
    Context manager for temporarily changing working directory.

    Args:
        path: Directory path to change to

    Example:
        >>> with change_directory("/tmp"):
        ...     # Work in /tmp
        ...     pass
        # Automatically returns to original directory
    """
    import os

    original_dir = Path.cwd()
    try:
        os.chdir(path)
        yield path
    finally:
        os.chdir(original_dir)


def execute_command(
    command: list[str] | str,
    *,
    cwd: str | Path | None = None,
    timeout: int | None = 300,
    check: bool = True,
    capture_output: bool = True,
    env: dict[str, str] | None = None,
    shell: bool = False,
) -> ExecutionResult:
    """
    Execute a command safely using subprocess.

    Args:
        command: Command to execute (list of args or string if shell=True)
        cwd: Working directory for command execution
        timeout: Timeout in seconds (None for no timeout)
        check: Whether to raise exception on non-zero exit code
        capture_output: Whether to capture stdout/stderr
        env: Environment variables to pass to subprocess
        shell: Whether to use shell (DANGEROUS - avoid when possible)

    Returns:
        ExecutionResult with command output and status

    Raises:
        ExecutionError: If command fails and check=True
        TimeoutError: If command times out

    Example:
        >>> result = execute_command(["ls", "-la"])
        >>> print(result.stdout)
    """
    # Convert string command to list if not using shell
    if isinstance(command, str) and not shell:
        command = shlex.split(command)

    logger.debug(f"Executing command: {command}")

    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            timeout=timeout,
            capture_output=capture_output,
            text=True,
            env=env,
            shell=shell,
            check=False,  # We'll handle checking ourselves
        )

        success = result.returncode == 0

        exec_result = ExecutionResult(
            returncode=result.returncode,
            stdout=result.stdout if capture_output else "",
            stderr=result.stderr if capture_output else "",
            success=success,
        )

        if check and not success:
            raise ExecutionError(
                f"Command failed with exit code {result.returncode}",
                returncode=result.returncode,
                stdout=exec_result.stdout,
                stderr=exec_result.stderr,
            )

        logger.debug(f"Command completed: {exec_result}")
        return exec_result

    except subprocess.TimeoutExpired as e:
        logger.error(f"Command timed out after {timeout}s: {command}")
        raise TimeoutError(
            f"Command timed out after {timeout} seconds"
        ) from e
    except FileNotFoundError as e:
        logger.error(f"Command not found: {command}")
        raise ExecutionError(
            f"Command not found: {command[0] if isinstance(command, list) else command}"
        ) from e
    except Exception as e:
        logger.error(f"Command execution failed: {e}")
        raise ExecutionError(f"Command execution failed: {e}") from e


async def execute_command_async(
    command: list[str] | str,
    *,
    cwd: str | Path | None = None,
    timeout: int | None = 300,
    check: bool = True,
    capture_output: bool = True,
    env: dict[str, str] | None = None,
) -> ExecutionResult:
    """
    Execute a command asynchronously.

    Args:
        command: Command to execute (list of args)
        cwd: Working directory for command execution
        timeout: Timeout in seconds
        check: Whether to raise exception on non-zero exit code
        capture_output: Whether to capture stdout/stderr
        env: Environment variables

    Returns:
        ExecutionResult with command output and status

    Raises:
        ExecutionError: If command fails and check=True
        TimeoutError: If command times out

    Example:
        >>> result = await execute_command_async(["ls", "-la"])
        >>> print(result.stdout)
    """
    if isinstance(command, str):
        command = shlex.split(command)

    logger.debug(f"Executing async command: {command}")

    try:
        process = await asyncio.create_subprocess_exec(
            *command,
            cwd=cwd,
            stdout=asyncio.subprocess.PIPE if capture_output else None,
            stderr=asyncio.subprocess.PIPE if capture_output else None,
            env=env,
        )

        stdout, stderr = await asyncio.wait_for(
            process.communicate(), timeout=timeout
        )

        success = process.returncode == 0

        exec_result = ExecutionResult(
            returncode=process.returncode or 0,
            stdout=stdout.decode() if stdout else "",
            stderr=stderr.decode() if stderr else "",
            success=success,
        )

        if check and not success:
            raise ExecutionError(
                f"Command failed with exit code {process.returncode}",
                returncode=process.returncode,
                stdout=exec_result.stdout,
                stderr=exec_result.stderr,
            )

        logger.debug(f"Async command completed: {exec_result}")
        return exec_result

    except asyncio.TimeoutError as e:
        logger.error(f"Async command timed out after {timeout}s: {command}")
        if process:
            process.kill()
            await process.wait()
        raise TimeoutError(
            f"Command timed out after {timeout} seconds"
        ) from e
    except Exception as e:
        logger.error(f"Async command execution failed: {e}")
        raise ExecutionError(f"Command execution failed: {e}") from e


def execute_python_script(
    script_path: str | Path,
    args: list[str] | None = None,
    **kwargs: Any,
) -> ExecutionResult:
    """
    Execute a Python script safely.

    Args:
        script_path: Path to Python script
        args: Arguments to pass to script
        **kwargs: Additional arguments passed to execute_command

    Returns:
        ExecutionResult with script output

    Example:
        >>> result = execute_python_script("script.py", ["--verbose"])
    """
    import sys

    command = [sys.executable, str(script_path)]
    if args:
        command.extend(args)

    return execute_command(command, **kwargs)


async def execute_python_script_async(
    script_path: str | Path,
    args: list[str] | None = None,
    **kwargs: Any,
) -> ExecutionResult:
    """
    Execute a Python script asynchronously.

    Args:
        script_path: Path to Python script
        args: Arguments to pass to script
        **kwargs: Additional arguments passed to execute_command_async

    Returns:
        ExecutionResult with script output

    Example:
        >>> result = await execute_python_script_async("script.py", ["--verbose"])
    """
    import sys

    command = [sys.executable, str(script_path)]
    if args:
        command.extend(args)

    return await execute_command_async(command, **kwargs)


async def execute_concurrent(
    commands: list[tuple[list[str], dict[str, Any]]],
    max_concurrent: int = 5,
) -> list[ExecutionResult]:
    """
    Execute multiple commands concurrently with a limit.

    Args:
        commands: List of (command, kwargs) tuples
        max_concurrent: Maximum number of concurrent executions

    Returns:
        List of ExecutionResults in order

    Example:
        >>> commands = [
        ...     (["ls", "-la"], {}),
        ...     (["pwd"], {}),
        ... ]
        >>> results = await execute_concurrent(commands)
    """
    semaphore = asyncio.Semaphore(max_concurrent)

    async def execute_with_semaphore(
        command: list[str], kwargs: dict[str, Any]
    ) -> ExecutionResult:
        async with semaphore:
            return await execute_command_async(command, **kwargs)

    tasks = [
        execute_with_semaphore(cmd, kwargs) for cmd, kwargs in commands
    ]
    return await asyncio.gather(*tasks, return_exceptions=False)
