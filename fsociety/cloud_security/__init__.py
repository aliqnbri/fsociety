"""
Cloud security scanning tools.
"""

from __future__ import annotations

from fsociety.core.executor import execute_command, change_directory
from fsociety.core.logging_config import get_logger
from fsociety.core.menu import confirm, set_readline
from fsociety.core.repo import GitHubRepo
from fsociety.core.validation import validate_command_arg

logger = get_logger(__name__)


class ScoutSuiteRepo(GitHubRepo):
    """Multi-cloud security auditing tool (AWS, Azure, GCP, etc.)."""

    def __init__(self) -> None:
        super().__init__(
            path="nccgroup/ScoutSuite",
            install={"pip": "requirements.txt"},
            description="Multi-cloud security auditing tool for AWS, Azure, GCP, Alibaba Cloud, and more",
        )

    def run(self) -> int:
        """Run ScoutSuite cloud security audit."""
        set_readline([])

        print("\nScoutSuite - Multi-Cloud Security Auditing")
        print("\nSupported providers:")
        print("1. AWS (Amazon Web Services)")
        print("2. Azure (Microsoft Azure)")
        print("3. GCP (Google Cloud Platform)")
        print("4. Alibaba Cloud")
        print("5. Oracle Cloud")

        provider_choice = input("\nSelect cloud provider [1-5]: ").strip()

        provider_map = {
            "1": "aws",
            "2": "azure",
            "3": "gcp",
            "4": "aliyun",
            "5": "oci",
        }

        provider = provider_map.get(provider_choice)
        if not provider:
            logger.error(f"Invalid provider choice: {provider_choice}")
            return 1

        # Build command
        command = ["scout", provider]

        # Report name
        report_name = input(f"\nReport name (default: {provider}-audit): ").strip()
        if report_name:
            report_name = validate_command_arg(report_name)
            command.extend(["--report-name", report_name])

        logger.info(f"Running ScoutSuite audit for {provider}...")
        logger.info("Note: This requires valid cloud credentials configured")

        try:
            with change_directory(self.full_path):
                result = execute_command(
                    command,
                    timeout=1800,  # 30 minutes for cloud scans
                    check=False,
                )

            if result.success:
                logger.info("Cloud security audit completed successfully")
                logger.info("Check the generated HTML report for results")
            else:
                logger.error("Cloud security audit failed")
                if "credentials" in result.stderr.lower():
                    logger.error("Please configure cloud credentials first")

            return result.returncode

        except Exception as e:
            logger.error(f"ScoutSuite failed: {e}")
            return 1


class TrivyRepo(GitHubRepo):
    """Container and dependency vulnerability scanner."""

    def __init__(self) -> None:
        super().__init__(
            path="aquasecurity/trivy",
            install={
                "binary": "https://github.com/aquasecurity/trivy/releases/latest/download/trivy_Linux-64bit.tar.gz"
            },
            description="Comprehensive container and dependency vulnerability scanner",
        )

    def run(self) -> int:
        """Run Trivy scanner."""
        set_readline([])

        print("\nTrivy - Container & Dependency Scanner")
        print("\nScan types:")
        print("1. Docker image")
        print("2. Filesystem")
        print("3. Git repository")
        print("4. Kubernetes cluster")

        scan_type = input("\nSelect scan type [1-4]: ").strip()

        match scan_type:
            case "1":
                target_type = "image"
                target = input("Enter Docker image name (e.g., nginx:latest): ").strip()
            case "2":
                target_type = "fs"
                target = input("Enter filesystem path: ").strip()
            case "3":
                target_type = "repo"
                target = input("Enter Git repository URL: ").strip()
            case "4":
                target_type = "k8s"
                target = "cluster"
            case _:
                logger.error(f"Invalid scan type: {scan_type}")
                return 1

        if not target:
            logger.error("No target provided")
            return 1

        # Build command
        command = ["trivy", target_type, target]

        # Severity filter
        if confirm("\nFilter by severity?"):
            print("Severities: CRITICAL, HIGH, MEDIUM, LOW, UNKNOWN")
            severities = input("Enter severities (comma-separated, default: CRITICAL,HIGH): ").strip()
            if not severities:
                severities = "CRITICAL,HIGH"
            command.extend(["--severity", severities])

        # Output format
        if confirm("\nGenerate JSON report?"):
            output_file = input("Output file (default: trivy-report.json): ").strip()
            if not output_file:
                output_file = "trivy-report.json"
            command.extend(["-f", "json", "-o", output_file])

        logger.info(f"Running Trivy scan on {target}...")

        try:
            result = execute_command(
                command,
                timeout=600,
                check=False,
            )

            if result.success:
                logger.info("Trivy scan completed successfully")
            else:
                logger.warning("Trivy scan completed with warnings")

            return result.returncode

        except Exception as e:
            logger.error(f"Trivy scan failed: {e}")
            return 1


# Create instances
scoutsuite = ScoutSuiteRepo()
trivy = TrivyRepo()
