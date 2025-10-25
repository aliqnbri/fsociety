"""
Modern vulnerability scanner with Nuclei integration.
"""

from __future__ import annotations

from pathlib import Path

from fsociety.core.executor import execute_command, change_directory
from fsociety.core.logging_config import get_logger
from fsociety.core.menu import confirm, set_readline
from fsociety.core.repo import GitHubRepo
from fsociety.core.validation import validate_url

logger = get_logger(__name__)


class NucleiRepo(GitHubRepo):
    """Modern fast vulnerability scanner based on templates."""

    def __init__(self) -> None:
        super().__init__(
            path="projectdiscovery/nuclei",
            install={"go": "go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest"},
            description="Fast and customizable vulnerability scanner based on simple YAML based DSL",
        )

    def run(self) -> int:
        """Run Nuclei scanner."""
        set_readline([])

        target = input("\nEnter target URL or host: ").strip()
        if not target:
            logger.error("No target provided")
            return 1

        try:
            target = validate_url(target)
        except ValueError as e:
            logger.warning(f"URL validation warning: {e}")

        # Build command
        command = ["nuclei", "-u", target]

        # Ask for severity filter
        if confirm("\nFilter by severity? (Recommended for faster scans)"):
            print("\nSeverity levels: critical, high, medium, low, info")
            severity = input("Enter severity (e.g., 'critical,high'): ").strip()
            if severity:
                command.extend(["-s", severity])

        # Ask for template tags
        if confirm("\nFilter by template tags? (e.g., cve, owasp, wordpress)"):
            print("\nCommon tags: cve, owasp, tech, exposure, wordpress, joomla")
            tags = input("Enter tags (comma-separated): ").strip()
            if tags:
                command.extend(["-tags", tags])

        # Output file
        if confirm("\nSave results to file?"):
            output_file = input("Enter output file path (default: nuclei-results.txt): ").strip()
            if not output_file:
                output_file = "nuclei-results.txt"
            command.extend(["-o", output_file])

        # Update templates before scanning
        if confirm("\nUpdate Nuclei templates before scanning?"):
            logger.info("Updating Nuclei templates...")
            execute_command(["nuclei", "-update-templates"], timeout=120, check=False)

        logger.info(f"Running Nuclei scan on {target}...")
        logger.debug(f"Command: {' '.join(command)}")

        try:
            result = execute_command(
                command,
                timeout=600,
                check=False,
            )

            if result.success:
                logger.info("Nuclei scan completed successfully")
            else:
                logger.warning("Nuclei scan completed with warnings")

            return result.returncode

        except Exception as e:
            logger.error(f"Nuclei scan failed: {e}")
            return 1


nuclei = NucleiRepo()
