"""Modern async Nmap implementation with AI analysis."""

from __future__ import annotations

import asyncio
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

from rich.table import Table

from fsociety.console import console
from fsociety.core.async_repo import AsyncGitHubRepo
from fsociety.core.config import get_config
from fsociety.ai.engine import get_ai_engine


class ScanType(str, Enum):
    """Available scan types."""

    SIMPLE = "simple"
    QUICK = "quick"
    INTENSE = "intense"
    STEALTH = "stealth"
    COMPREHENSIVE = "comprehensive"
    VULNERABILITY = "vuln"


@dataclass
class ScanResult:
    """Scan result data structure."""

    host: str
    status: str
    ports: list[dict[str, Any]]
    os_info: dict[str, Any] | None = None
    vulnerabilities: list[dict[str, Any]] | None = None


class AsyncNmap(AsyncGitHubRepo):
    """Modern async Nmap wrapper with AI analysis."""

    SCAN_PROFILES = {
        ScanType.SIMPLE: "-T4 -F",
        ScanType.QUICK: "-T4 -F --version-light",
        ScanType.INTENSE: "-T4 -A -v",
        ScanType.STEALTH: "-sS -T2 -f",
        ScanType.COMPREHENSIVE: "-T4 -A -v -p-",
        ScanType.VULNERABILITY: "-sV --script vuln",
    }

    def __init__(self) -> None:
        super().__init__(
            path="nmap/nmap",
            install={
                "linux": "sudo apt-get install -y nmap",
                "macos": "brew install nmap",
                "platform_specific": {
                    "arch": "sudo pacman -Sy nmap",
                },
            },
            description="The Network Mapper - Modern async implementation",
        )
        self.config = get_config()
        self.ai_engine = None
        self.results_dir = self.config.install_dir / "scan_results"
        self.results_dir.mkdir(exist_ok=True)

    async def run(self) -> int:
        """Run interactive nmap scan."""
        console.print("\n[cyan]╔══════════════════════════════╗")
        console.print("[cyan]║     Nmap Scanner 4.0         ║")
        console.print("[cyan]╚══════════════════════════════╝\n")

        # Get target
        target = input("Enter target (IP/hostname/CIDR): ").strip()
        if not target:
            console.print("[red]Target required!")
            return 1

        # Select scan type
        console.print("\n[yellow]Available scan types:[/yellow]")
        for i, scan_type in enumerate(ScanType, 1):
            args = self.SCAN_PROFILES[scan_type]
            console.print(f"  {i}. {scan_type.value:15} {args}")

        selection = input("\nSelect scan type (1-6): ").strip()
        try:
            scan_type = list(ScanType)[int(selection) - 1]
        except (ValueError, IndexError):
            scan_type = ScanType.SIMPLE

        # AI analysis option
        use_ai = False
        if self.config.ai.enabled:
            response = input("\nUse AI analysis? (y/N): ").strip().lower()
            use_ai = response == "y"
            if use_ai:
                self.ai_engine = get_ai_engine()
                await self.ai_engine.initialize()

        # Run scan
        console.print(f"\n[cyan]Starting {scan_type.value} scan of {target}...")
        result = await self.scan(target, scan_type)

        # Display results
        await self.display_results(result)

        # AI analysis
        if use_ai and self.ai_engine:
            await self.ai_analysis(result)

        # Save results
        await self.save_results(result, target)

        return 0

    async def scan(
        self,
        target: str,
        scan_type: ScanType = ScanType.SIMPLE,
        output_format: str = "xml",
    ) -> ScanResult:
        """Perform async nmap scan."""
        args = self.SCAN_PROFILES[scan_type]
        output_file = self.results_dir / f"scan_{target.replace('/', '_')}.xml"

        cmd = f"nmap {args} -oX {output_file} {target}"

        console.print(f"[dim]Executing: {cmd}")

        # Run scan asynchronously
        stdout, stderr, returncode = await self.run_command(cmd)

        if returncode != 0:
            console.print(f"[red]Scan failed: {stderr}")
            raise RuntimeError(f"Nmap scan failed: {stderr}")

        # Parse results
        return await self.parse_results(output_file, target)

    async def parse_results(self, xml_file: Path, target: str) -> ScanResult:
        """Parse nmap XML output asynchronously."""

        def _parse() -> ScanResult:
            tree = ET.parse(xml_file)
            root = tree.getroot()

            host_elem = root.find(".//host")
            if host_elem is None:
                return ScanResult(host=target, status="down", ports=[])

            # Get host status
            status_elem = host_elem.find("status")
            status = status_elem.get("state", "unknown") if status_elem is not None else "unknown"

            # Parse ports
            ports = []
            for port_elem in host_elem.findall(".//port"):
                port_info = {
                    "port": port_elem.get("portid"),
                    "protocol": port_elem.get("protocol"),
                    "state": port_elem.find("state").get("state"),
                }

                service_elem = port_elem.find("service")
                if service_elem is not None:
                    port_info.update(
                        {
                            "service": service_elem.get("name", "unknown"),
                            "product": service_elem.get("product", ""),
                            "version": service_elem.get("version", ""),
                        }
                    )

                # Check for vulnerabilities
                script_output = []
                for script_elem in port_elem.findall(".//script"):
                    script_output.append(
                        {
                            "id": script_elem.get("id"),
                            "output": script_elem.get("output"),
                        }
                    )

                if script_output:
                    port_info["scripts"] = script_output

                ports.append(port_info)

            # Parse OS detection
            os_info = None
            osmatch_elem = host_elem.find(".//osmatch")
            if osmatch_elem is not None:
                os_info = {
                    "name": osmatch_elem.get("name"),
                    "accuracy": osmatch_elem.get("accuracy"),
                }

            return ScanResult(
                host=target,
                status=status,
                ports=ports,
                os_info=os_info,
            )

        # Parse in thread pool to avoid blocking
        return await asyncio.to_thread(_parse)

    async def display_results(self, result: ScanResult) -> None:
        """Display scan results in a formatted table."""
        console.print(f"\n[green]Scan Results for {result.host}")
        console.print(f"Status: [{'green' if result.status == 'up' else 'red'}]{result.status}")

        if result.os_info:
            console.print(f"OS: {result.os_info['name']} ({result.os_info['accuracy']}% accuracy)")

        if not result.ports:
            console.print("[yellow]No open ports found")
            return

        # Create results table
        table = Table(title=f"Open Ports ({len(result.ports)})", border_style="cyan")
        table.add_column("Port", style="yellow", no_wrap=True)
        table.add_column("State", style="green")
        table.add_column("Service", style="cyan")
        table.add_column("Version", style="white")

        for port in result.ports:
            table.add_row(
                f"{port['port']}/{port['protocol']}",
                port["state"],
                port.get("service", "unknown"),
                f"{port.get('product', '')} {port.get('version', '')}".strip(),
            )

        console.print(table)

        # Display vulnerabilities if found
        vulns = [p for p in result.ports if "scripts" in p]
        if vulns:
            console.print("\n[red]⚠ Potential Vulnerabilities Found:")
            for port in vulns:
                console.print(f"\n[yellow]Port {port['port']}:")
                for script in port["scripts"]:
                    console.print(f"  • {script['id']}")
                    console.print(f"    {script['output'][:200]}...")

    async def ai_analysis(self, result: ScanResult) -> None:
        """Perform AI-powered analysis of scan results."""
        console.print("\n[cyan]🤖 AI Analysis in progress...")

        # Prepare data for AI
        scan_data = {
            "host": result.host,
            "status": result.status,
            "open_ports": [
                {
                    "port": p["port"],
                    "service": p.get("service"),
                    "version": f"{p.get('product', '')} {p.get('version', '')}".strip(),
                }
                for p in result.ports
            ],
            "os": result.os_info,
        }

        # Get AI analysis
        ai_result = await self.ai_engine.analyze_vulnerability(
            target=result.host,
            scan_results=scan_data,
        )

        # Display AI insights
        console.print(f"\n[green]AI Analysis Summary:")
        console.print(f"Confidence: {ai_result.confidence:.0%}")
        console.print(f"Severity: [{self._severity_color(ai_result.severity)}]{ai_result.severity}")
        console.print(f"\n{ai_result.summary}")

        if ai_result.recommendations:
            console.print("\n[yellow]Recommendations:")
            for i, rec in enumerate(ai_result.recommendations, 1):
                console.print(f"  {i}. {rec}")

    def _severity_color(self, severity: str) -> str:
        """Get color for severity level."""
        colors = {
            "critical": "red",
            "high": "red",
            "medium": "yellow",
            "low": "green",
        }
        return colors.get(severity.lower(), "white")

    async def save_results(self, result: ScanResult, target: str) -> None:
        """Save scan results to JSON."""
        import orjson
        from datetime import datetime

        output_file = (
            self.results_dir / f"scan_{target.replace('/', '_')}_{datetime.now().isoformat()}.json"
        )

        data = {
            "timestamp": datetime.now().isoformat(),
            "target": target,
            "status": result.status,
            "ports": result.ports,
            "os_info": result.os_info,
        }

        output_file.write_bytes(orjson.dumps(data, option=orjson.OPT_INDENT_2))
        console.print(f"\n[green]✓ Results saved to: {output_file}")

    async def batch_scan(
        self,
        targets: list[str],
        scan_type: ScanType = ScanType.SIMPLE,
    ) -> list[ScanResult]:
        """Scan multiple targets concurrently."""
        max_concurrent = self.config.performance.max_workers
        semaphore = asyncio.Semaphore(max_concurrent)

        async def scan_with_limit(target: str) -> ScanResult:
            async with semaphore:
                return await self.scan(target, scan_type)

        console.print(f"[cyan]Scanning {len(targets)} targets with {max_concurrent} workers...")

        results = await asyncio.gather(
            *[scan_with_limit(t) for t in targets],
            return_exceptions=True,
        )

        # Filter out exceptions
        valid_results = [r for r in results if isinstance(r, ScanResult)]

        console.print(f"[green]✓ Completed {len(valid_results)}/{len(targets)} scans")

        return valid_results


# Create instance
nmap_async = AsyncNmap()


# Example usage
async def main():
    """Example usage."""
    nmap = AsyncNmap()

    # Single scan
    result = await nmap.scan("scanme.nmap.org", ScanType.QUICK)
    await nmap.display_results(result)

    # Batch scan
    targets = ["scanme.nmap.org", "example.com"]
    results = await nmap.batch_scan(targets, ScanType.SIMPLE)

    for result in results:
        await nmap.display_results(result)


if __name__ == "__main__":
    asyncio.run(main())
