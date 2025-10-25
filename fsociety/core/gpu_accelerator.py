"""
GPU acceleration module for password cracking and intensive operations.

This module provides GPU-accelerated functionality for password cracking
using hashcat and CUDA/OpenCL when available.
"""

from __future__ import annotations

import logging
import shutil
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Literal

from fsociety.core.executor import execute_command, ExecutionError


logger = logging.getLogger(__name__)


class HashType(Enum):
    """Supported hash types for cracking."""

    MD5 = 0
    SHA1 = 100
    SHA256 = 1400
    SHA512 = 1700
    NTLM = 1000
    BCRYPT = 3200
    WPA_WPA2 = 2500
    MD5_CRYPT = 500
    SHA512_CRYPT = 1800


class AttackMode(Enum):
    """Hash cracking attack modes."""

    STRAIGHT = 0  # Dictionary attack
    COMBINATION = 1  # Combinator attack
    BRUTE_FORCE = 3  # Brute-force attack
    HYBRID_WORDLIST_MASK = 6  # Hybrid wordlist + mask
    HYBRID_MASK_WORDLIST = 7  # Hybrid mask + wordlist


@dataclass
class GPUInfo:
    """Information about available GPU resources."""

    has_cuda: bool
    has_opencl: bool
    has_hashcat: bool
    gpu_count: int
    gpu_devices: list[str]
    recommended_backend: Literal["cuda", "opencl", "cpu"] | None

    def is_available(self) -> bool:
        """Check if GPU acceleration is available."""
        return (self.has_cuda or self.has_opencl) and self.has_hashcat


def detect_gpu() -> GPUInfo:
    """
    Detect available GPU resources and capabilities.

    Returns:
        GPUInfo with detected capabilities

    Example:
        >>> gpu_info = detect_gpu()
        >>> if gpu_info.is_available():
        ...     print(f"GPU acceleration available: {gpu_info.recommended_backend}")
    """
    has_cuda = False
    has_opencl = False
    has_hashcat = shutil.which("hashcat") is not None
    gpu_count = 0
    gpu_devices = []
    recommended_backend = None

    # Check for CUDA
    try:
        nvidia_smi = shutil.which("nvidia-smi")
        if nvidia_smi:
            result = execute_command(
                [nvidia_smi, "--query-gpu=name", "--format=csv,noheader"],
                check=False,
                timeout=5,
            )
            if result.success:
                has_cuda = True
                gpu_devices = [
                    line.strip()
                    for line in result.stdout.strip().split("\n")
                    if line.strip()
                ]
                gpu_count = len(gpu_devices)
                recommended_backend = "cuda"
                logger.info(f"Detected {gpu_count} CUDA GPU(s): {gpu_devices}")
    except Exception as e:
        logger.debug(f"CUDA detection failed: {e}")

    # Check for OpenCL
    try:
        if has_hashcat:
            result = execute_command(
                ["hashcat", "-I"],
                check=False,
                timeout=5,
            )
            if result.success and "OpenCL" in result.stdout:
                has_opencl = True
                if not has_cuda:
                    recommended_backend = "opencl"
                logger.info("OpenCL support detected")
    except Exception as e:
        logger.debug(f"OpenCL detection failed: {e}")

    # Fallback to CPU
    if not has_cuda and not has_opencl:
        recommended_backend = "cpu"
        logger.info("No GPU detected, using CPU")

    return GPUInfo(
        has_cuda=has_cuda,
        has_opencl=has_opencl,
        has_hashcat=has_hashcat,
        gpu_count=gpu_count,
        gpu_devices=gpu_devices,
        recommended_backend=recommended_backend,
    )


class HashcatCracker:
    """GPU-accelerated password cracker using hashcat."""

    def __init__(self) -> None:
        """Initialize hashcat cracker."""
        self.gpu_info = detect_gpu()

        if not self.gpu_info.has_hashcat:
            logger.warning(
                "hashcat not found. Install with: apt install hashcat "
                "(Linux) or brew install hashcat (macOS)"
            )

    def crack_hash(
        self,
        hash_value: str,
        hash_type: HashType,
        wordlist: str | Path | None = None,
        attack_mode: AttackMode = AttackMode.STRAIGHT,
        *,
        mask: str | None = None,
        rules: str | Path | None = None,
        output_file: str | Path | None = None,
        use_gpu: bool = True,
        workload_profile: int = 3,
        timeout: int | None = None,
    ) -> str | None:
        """
        Crack a password hash using hashcat.

        Args:
            hash_value: The hash to crack
            hash_type: Type of hash (from HashType enum)
            wordlist: Path to wordlist file (for dictionary attacks)
            attack_mode: Attack mode to use
            mask: Mask for brute-force (e.g., "?a?a?a?a" for 4 chars)
            rules: Path to rules file
            output_file: Path to save cracked passwords
            use_gpu: Whether to use GPU acceleration
            workload_profile: Hashcat workload profile (1-4)
            timeout: Timeout in seconds

        Returns:
            Cracked password if successful, None otherwise

        Raises:
            ExecutionError: If hashcat execution fails
            ValueError: If required parameters are missing

        Example:
            >>> cracker = HashcatCracker()
            >>> password = cracker.crack_hash(
            ...     "5f4dcc3b5aa765d61d8327deb882cf99",
            ...     HashType.MD5,
            ...     wordlist="/usr/share/wordlists/rockyou.txt"
            ... )
        """
        if not self.gpu_info.has_hashcat:
            raise ExecutionError(
                "hashcat not installed. Please install it first."
            )

        # Validate parameters based on attack mode
        match attack_mode:
            case AttackMode.STRAIGHT | AttackMode.COMBINATION:
                if not wordlist:
                    raise ValueError(
                        f"{attack_mode.name} attack requires a wordlist"
                    )
            case AttackMode.BRUTE_FORCE:
                if not mask:
                    raise ValueError(
                        "BRUTE_FORCE attack requires a mask"
                    )

        # Build hashcat command
        command = ["hashcat"]

        # Attack mode
        command.extend(["-a", str(attack_mode.value)])

        # Hash type
        command.extend(["-m", str(hash_type.value)])

        # Workload profile
        command.extend(["-w", str(workload_profile)])

        # GPU/CPU selection
        if not use_gpu or not self.gpu_info.is_available():
            command.extend(["-D", "1"])  # Use CPU only
            logger.info("Using CPU for cracking")
        else:
            command.extend(["-D", "2"])  # Use GPU
            logger.info(
                f"Using GPU for cracking ({self.gpu_info.recommended_backend})"
            )

        # Output file
        if output_file:
            command.extend(["-o", str(output_file)])

        # Rules
        if rules:
            command.extend(["-r", str(rules)])

        # Show cracked passwords
        command.append("--show")

        # Hash to crack
        command.append(hash_value)

        # Wordlist or mask
        if wordlist:
            command.append(str(wordlist))
        elif mask:
            command.append(mask)

        logger.info(f"Starting hashcat with command: {' '.join(command)}")

        try:
            result = execute_command(
                command,
                timeout=timeout,
                check=False,
            )

            if result.success or result.returncode == 0:
                # Parse output for cracked password
                output = result.stdout.strip()
                if ":" in output:
                    # Format is hash:password
                    cracked = output.split(":", 1)[1]
                    logger.info(f"Successfully cracked hash: {hash_value}")
                    return cracked

            logger.warning(f"Failed to crack hash: {hash_value}")
            return None

        except TimeoutError:
            logger.error(f"Hashcat timed out after {timeout}s")
            return None
        except Exception as e:
            logger.error(f"Hashcat execution failed: {e}")
            raise

    def benchmark_gpu(self) -> dict[str, float]:
        """
        Run hashcat benchmark to test GPU performance.

        Returns:
            Dictionary of hash types and their speeds (H/s)

        Example:
            >>> cracker = HashcatCracker()
            >>> speeds = cracker.benchmark_gpu()
            >>> print(f"MD5 speed: {speeds.get('MD5', 0)} H/s")
        """
        if not self.gpu_info.has_hashcat:
            logger.error("hashcat not available for benchmarking")
            return {}

        logger.info("Running GPU benchmark...")

        try:
            result = execute_command(
                ["hashcat", "-b", "-m", "0"],  # Benchmark MD5
                timeout=60,
                check=False,
            )

            speeds = {}
            if result.success:
                # Parse benchmark output
                for line in result.stdout.split("\n"):
                    if "H/s" in line:
                        # Extract speed
                        parts = line.split()
                        for i, part in enumerate(parts):
                            if part.endswith("H/s"):
                                try:
                                    speed = float(
                                        parts[i - 1].replace(",", "")
                                    )
                                    speeds["MD5"] = speed
                                except (ValueError, IndexError):
                                    pass

            return speeds

        except Exception as e:
            logger.error(f"Benchmark failed: {e}")
            return {}


def install_hashcat() -> bool:
    """
    Attempt to install hashcat based on detected platform.

    Returns:
        True if installation successful, False otherwise

    Example:
        >>> if not shutil.which("hashcat"):
        ...     install_hashcat()
    """
    import distro

    try:
        # Detect platform
        if distro.id() in ("ubuntu", "debian", "kali"):
            result = execute_command(
                ["sudo", "apt", "install", "-y", "hashcat"],
                timeout=300,
                check=False,
            )
        elif distro.id() in ("arch", "manjaro"):
            result = execute_command(
                ["sudo", "pacman", "-S", "--noconfirm", "hashcat"],
                timeout=300,
                check=False,
            )
        elif distro.id() == "fedora":
            result = execute_command(
                ["sudo", "dnf", "install", "-y", "hashcat"],
                timeout=300,
                check=False,
            )
        else:
            logger.error(f"Unsupported distribution: {distro.id()}")
            return False

        if result.success:
            logger.info("hashcat installed successfully")
            return True
        else:
            logger.error(f"hashcat installation failed: {result.stderr}")
            return False

    except Exception as e:
        logger.error(f"Failed to install hashcat: {e}")
        return False
