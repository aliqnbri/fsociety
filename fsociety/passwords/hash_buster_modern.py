"""
Modern hash cracking tool with GPU acceleration support.

This module provides both online hash lookup and offline GPU-accelerated
cracking using hashcat.
"""

from __future__ import annotations

from pathlib import Path

from fsociety.core.executor import execute_python_script
from fsociety.core.gpu_accelerator import (
    HashcatCracker,
    HashType,
    AttackMode,
    detect_gpu,
)
from fsociety.core.logging_config import get_logger
from fsociety.core.menu import confirm, set_readline
from fsociety.core.repo import GitHubRepo
from fsociety.core.validation import validate_command_arg

logger = get_logger(__name__)


class HashBusterRepo(GitHubRepo):
    """Hash cracking tool with GPU acceleration."""

    def __init__(self) -> None:
        super().__init__(
            path="s0md3v/Hash-Buster",
            install={"pip": "requirements.txt"},
            description="Fast hash cracking with online lookup and GPU support",
        )
        self.cracker = HashcatCracker()

    def _detect_hash_type(self, hash_value: str) -> HashType | None:
        """
        Attempt to detect hash type based on length and format.

        Args:
            hash_value: Hash string to analyze

        Returns:
            Detected HashType or None
        """
        hash_len = len(hash_value)

        match hash_len:
            case 32 if hash_value.isalnum():
                return HashType.MD5
            case 40 if hash_value.isalnum():
                return HashType.SHA1
            case 64 if hash_value.isalnum():
                return HashType.SHA256
            case 128 if hash_value.isalnum():
                return HashType.SHA512
            case 32 if ":" not in hash_value:
                return HashType.NTLM
            case _:
                logger.warning(f"Could not detect hash type for: {hash_value}")
                return None

    def _run_online_lookup(self, hash_value: str) -> int:
        """Run online hash lookup using Hash-Buster."""
        logger.info("Running online hash lookup...")

        script_path = self.full_path / "buster.py"

        result = execute_python_script(
            script_path,
            args=[hash_value],
            cwd=self.full_path,
            timeout=120,
            check=False,
        )

        if result.success:
            logger.info("Online lookup completed successfully")
        else:
            logger.warning("Online lookup failed")

        return result.returncode

    def _run_gpu_cracking(
        self, hash_value: str, wordlist: Path | None = None
    ) -> int:
        """Run GPU-accelerated cracking with hashcat."""
        logger.info("Starting GPU-accelerated cracking...")

        # Detect GPU capabilities
        gpu_info = detect_gpu()

        if not gpu_info.is_available():
            logger.warning(
                "GPU acceleration not available. "
                "Install hashcat and ensure GPU drivers are installed."
            )
            return 1

        logger.info(
            f"GPU Info: {gpu_info.gpu_count} GPU(s), "
            f"Backend: {gpu_info.recommended_backend}"
        )

        # Detect hash type
        hash_type = self._detect_hash_type(hash_value)

        if not hash_type:
            logger.error("Could not detect hash type")
            return 1

        logger.info(f"Detected hash type: {hash_type.name}")

        # Get wordlist
        if not wordlist:
            # Try common wordlist locations
            common_wordlists = [
                Path("/usr/share/wordlists/rockyou.txt"),
                Path("/usr/share/wordlists/rockyou.txt.gz"),
                Path.home() / "wordlists" / "rockyou.txt",
            ]

            for wl in common_wordlists:
                if wl.exists():
                    wordlist = wl
                    logger.info(f"Using wordlist: {wordlist}")
                    break

        if not wordlist or not wordlist.exists():
            logger.error(
                "No wordlist found. Please specify a wordlist path."
            )
            return 1

        # Run hashcat
        try:
            cracked_password = self.cracker.crack_hash(
                hash_value=hash_value,
                hash_type=hash_type,
                wordlist=wordlist,
                attack_mode=AttackMode.STRAIGHT,
                use_gpu=True,
                workload_profile=3,
                timeout=300,
            )

            if cracked_password:
                logger.info(f"[bold green]Cracked![/bold green] Password: {cracked_password}")
                print(f"\n✓ Cracked! Password: {cracked_password}\n")
                return 0
            else:
                logger.warning("Could not crack hash with provided wordlist")
                print("\n✗ Could not crack hash\n")
                return 1

        except Exception as e:
            logger.error(f"GPU cracking failed: {e}")
            return 1

    def run(self) -> int:
        """
        Run hash cracking tool with multiple methods.

        Returns:
            Exit code
        """
        set_readline([])

        # Get hash from user
        hash_input = input("\nEnter hash to crack: ").strip()

        if not hash_input:
            logger.error("No hash provided")
            return 1

        hash_input = validate_command_arg(hash_input)

        # Choose cracking method
        print("\nCracking methods:")
        print("1. Online lookup (fast, requires internet)")
        print("2. GPU-accelerated cracking (slow, requires hashcat)")
        print("3. Try both (online first, then GPU if failed)")

        method = input("\nSelect method [1-3]: ").strip()

        match method:
            case "1":
                return self._run_online_lookup(hash_input)

            case "2":
                wordlist_input = input(
                    "\nEnter wordlist path (press Enter for default): "
                ).strip()

                wordlist = (
                    Path(wordlist_input) if wordlist_input else None
                )

                return self._run_gpu_cracking(hash_input, wordlist)

            case "3":
                # Try online first
                result = self._run_online_lookup(hash_input)

                if result == 0:
                    return 0

                # If online failed, try GPU
                if confirm("\nOnline lookup failed. Try GPU cracking?"):
                    wordlist_input = input(
                        "\nEnter wordlist path (press Enter for default): "
                    ).strip()

                    wordlist = (
                        Path(wordlist_input) if wordlist_input else None
                    )

                    return self._run_gpu_cracking(hash_input, wordlist)

                return result

            case _:
                logger.error(f"Invalid method selected: {method}")
                return 1


# Create instance
hash_buster = HashBusterRepo()
