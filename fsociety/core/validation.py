"""
Input validation and sanitization module for fsociety.

This module provides comprehensive input validation for URLs, domains, IPs,
file paths, and other user inputs to prevent injection attacks and ensure
data integrity.
"""

from __future__ import annotations

import ipaddress
import re
import shlex
from pathlib import Path
from typing import TypeVar
from urllib.parse import urlparse

from pydantic import BaseModel, Field, field_validator


T = TypeVar("T")


class URLInput(BaseModel):
    """Validated URL input."""

    url: str = Field(..., min_length=1, max_length=2048)

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Validate URL format and scheme."""
        if not v:
            raise ValueError("URL cannot be empty")

        parsed = urlparse(v)
        if not parsed.scheme:
            # Try adding http:// prefix
            v = f"http://{v}"
            parsed = urlparse(v)

        if parsed.scheme not in ("http", "https", "ftp", "ftps"):
            raise ValueError(
                f"Invalid URL scheme: {parsed.scheme}. "
                "Allowed: http, https, ftp, ftps"
            )

        if not parsed.netloc:
            raise ValueError("URL must contain a valid domain/host")

        return v


class DomainInput(BaseModel):
    """Validated domain input."""

    domain: str = Field(..., min_length=1, max_length=253)

    @field_validator("domain")
    @classmethod
    def validate_domain(cls, v: str) -> str:
        """Validate domain format."""
        if not v:
            raise ValueError("Domain cannot be empty")

        # Remove protocol if present
        v = re.sub(r"^https?://", "", v)
        v = v.split("/")[0]  # Remove path

        # Basic domain validation
        domain_pattern = re.compile(
            r"^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+"
            r"[a-zA-Z]{2,}$"
        )

        if not domain_pattern.match(v):
            raise ValueError(
                f"Invalid domain format: {v}. "
                "Domain must be a valid DNS name"
            )

        return v


class IPAddressInput(BaseModel):
    """Validated IP address input."""

    ip: str = Field(..., min_length=7, max_length=45)

    @field_validator("ip")
    @classmethod
    def validate_ip(cls, v: str) -> str:
        """Validate IP address (IPv4 or IPv6)."""
        if not v:
            raise ValueError("IP address cannot be empty")

        try:
            ipaddress.ip_address(v)
        except ValueError as e:
            raise ValueError(f"Invalid IP address: {v}") from e

        return v


class FilePathInput(BaseModel):
    """Validated file path input."""

    path: str = Field(..., min_length=1, max_length=4096)

    @field_validator("path")
    @classmethod
    def validate_path(cls, v: str) -> str:
        """Validate file path format."""
        if not v:
            raise ValueError("File path cannot be empty")

        # Check for path traversal attempts
        if ".." in v or v.startswith("/etc") or v.startswith("/proc"):
            raise ValueError(
                f"Potentially dangerous path detected: {v}"
            )

        try:
            Path(v).resolve()
        except (OSError, RuntimeError) as e:
            raise ValueError(f"Invalid file path: {v}") from e

        return v


class CommandArgument(BaseModel):
    """Validated command argument."""

    arg: str = Field(..., max_length=1024)

    @field_validator("arg")
    @classmethod
    def validate_arg(cls, v: str) -> str:
        """Validate and sanitize command argument."""
        if not v:
            return v

        # Check for shell metacharacters
        dangerous_chars = [";", "&", "|", "`", "$", "(", ")", "<", ">", "\n"]
        if any(char in v for char in dangerous_chars):
            raise ValueError(
                f"Command argument contains dangerous characters: {v}"
            )

        return v


def sanitize_shell_arg(arg: str) -> str:
    """
    Sanitize a shell argument using shlex.quote().

    Args:
        arg: The argument to sanitize

    Returns:
        Sanitized argument safe for shell execution

    Example:
        >>> sanitize_shell_arg("test; rm -rf /")
        "'test; rm -rf /'"
    """
    return shlex.quote(arg)


def validate_url(url: str) -> str:
    """
    Validate and normalize a URL.

    Args:
        url: URL to validate

    Returns:
        Normalized URL

    Raises:
        ValueError: If URL is invalid

    Example:
        >>> validate_url("example.com")
        'http://example.com'
    """
    return URLInput(url=url).url


def validate_domain(domain: str) -> str:
    """
    Validate a domain name.

    Args:
        domain: Domain to validate

    Returns:
        Validated domain

    Raises:
        ValueError: If domain is invalid

    Example:
        >>> validate_domain("example.com")
        'example.com'
    """
    return DomainInput(domain=domain).domain


def validate_ip(ip: str) -> str:
    """
    Validate an IP address (IPv4 or IPv6).

    Args:
        ip: IP address to validate

    Returns:
        Validated IP address

    Raises:
        ValueError: If IP is invalid

    Example:
        >>> validate_ip("192.168.1.1")
        '192.168.1.1'
    """
    return IPAddressInput(ip=ip).ip


def validate_file_path(path: str) -> str:
    """
    Validate a file path.

    Args:
        path: File path to validate

    Returns:
        Validated file path

    Raises:
        ValueError: If path is invalid or dangerous

    Example:
        >>> validate_file_path("/tmp/test.txt")
        '/tmp/test.txt'
    """
    return FilePathInput(path=path).path


def validate_command_arg(arg: str) -> str:
    """
    Validate a command argument.

    Args:
        arg: Command argument to validate

    Returns:
        Validated argument

    Raises:
        ValueError: If argument contains dangerous characters

    Example:
        >>> validate_command_arg("--verbose")
        '--verbose'
    """
    return CommandArgument(arg=arg).arg


def parse_space_separated(input_str: str, validator_func=None) -> list[str]:
    """
    Parse space-separated input and optionally validate each item.

    Args:
        input_str: Space-separated string
        validator_func: Optional function to validate each item

    Returns:
        List of validated items

    Example:
        >>> parse_space_separated("example.com test.com", validate_domain)
        ['example.com', 'test.com']
    """
    items = input_str.strip().split()

    if validator_func:
        return [validator_func(item) for item in items]

    return items
