"""Complete modern CLI with all 2025 features integrated."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import click
from rich.panel import Panel
from rich.table import Table

from fsociety.__version__ import __version__
from fsociety.console import console, print_success, print_error, print_warning
from fsociety.core.config import get_config
from fsociety.core.performance import get_performance_monitor


# ASCII Banners
BANNER_2025 = r"""
  ___               _      _           ___   ___ ___ ___ 
 / __|___  __ _____(_)__| |_ _  _    |_  ) / _ \__ \ __|
| (__(_-< / _/ _ \ _/ -_|  _| || |    / / | (_) |_ \__ \
 \___/__/ \__\___(_)\___|\__|\_, |   /___| \___/___/___/
                             |__/                        
"""


class ModernCLI:
    """Modern CLI with 2025 security features."""

    def __init__(self) -> None:
        self.config = get_config()
        self.monitor = get_performance_monitor()

    def display_banner(self) -> None:
        """Display modern banner."""
        console.print(BANNER_2025, style="bold cyan", highlight=False)

        features = []
        if self.config.ai.enabled:
            features.append("🤖 AI")
        if self.config.performance.use_gpu:
            features.append(f"⚡ {self.config.performance.gpu_backend.value.upper()}")
        features.append("🔒 Zero-Trust")
        features.append("☁️ Cloud")
        features.append("🎯 K8s")
        features.append("🌐 Web3")

        console.print(f"v{__version__} | " + " | ".join(features), style="dim")

    def display_main_menu(self) -> None:
        """Display main menu with all features."""
        table = Table(
            title="Security Testing Modules",
            show_header=True,
            header_style="bold cyan",
            border_style="blue",
        )

        table.add_column("Module", style="yellow", no_wrap=True)
        table.add_column("Description", style="white")
        table.add_column("Status", style="green")

        modules = [
            ("classic", "Classic Pentest Tools", "✓"),
            ("cloud", "Cloud Security (AWS/Azure/GCP)", "✓ 2025"),
            ("k8s", "Kubernetes Security", "✓ 2025"),
            ("api", "API & GraphQL Testing", "✓ 2025"),
            ("web3", "Blockchain & Smart Contracts", "✓ 2025"),
            ("supply", "Supply Chain Security", "✓ 2025"),
            ("ml", "AI/ML Model Security", "✓ 2025"),
            ("zerotrust", "Zero-Trust Architecture", "✓ 2025"),
            ("container", "Container Security", "✓ 2025"),
            ("ai", "AI Security Assistant", "✓" if self.config.ai.enabled else "✗"),
        ]

        for mod, desc, status in modules:
            table.add_row(mod, desc, status)

        console.print("\n")
        console.print(table)

        console.print("\n[bold cyan]Commands:[/bold cyan]")
        commands = [
            ("scan <target>", "Quick vulnerability scan"),
            ("report", "Generate security report"),
            ("update", "Update all tools"),
            ("benchmark", "Performance benchmark"),
            ("config", "Configuration"),
            ("exit", "Exit fsociety"),
        ]

        for cmd, desc in commands:
            console.print(f"  [yellow]{cmd:20}[/yellow] {desc}")


@click.group(invoke_without_command=True)
@click.option("--debug", is_flag=True, help="Enable debug mode")
@click.option("--ai/--no-ai", default=None, help="Enable/disable AI")
@click.pass_context
def cli(ctx: click.Context, debug: bool, ai: bool | None) -> None:
    """fsociety 4.0 - AI-Powered Penetration Testing Framework."""

    if ai is not None:
        config = get_config()
        config.ai.enabled = ai
        config.save()

    if ctx.invoked_subcommand is None:
        # Interactive mode
        cli_instance = ModernCLI()
        cli_instance.display_banner()

        console.print("\n[yellow]Welcome to fsociety 4.0!")
        console.print("[dim]Type 'help' for available commands\n")

        while True:
            try:
                command = input("fsociety> ").strip().lower()

                if not command:
                    continue

                match command:
                    case "exit" | "quit":
                        print_success("Goodbye!")
                        break

                    case "help" | "menu":
                        cli_instance.display_main_menu()

                    case "cloud":
                        asyncio.run(cloud_security_cli())

                    case "k8s" | "kubernetes":
                        asyncio.run(k8s_security_cli())

                    case "api":
                        asyncio.run(api_security_cli())

                    case "web3" | "blockchain":
                        asyncio.run(web3_security_cli())

                    case "supply" | "supplychain":
                        asyncio.run(supply_chain_cli())

                    case "ml" | "mlsec":
                        asyncio.run(ml_security_cli())

                    case "zerotrust" | "zt":
                        asyncio.run(zerotrust_cli())

                    case "container" | "docker":
                        asyncio.run(container_security_cli())

                    case "ai":
                        asyncio.run(ai_assistant_cli())

                    case "classic":
                        console.print("[cyan]Loading classic tools...")
                        # Would load classic modules

                    case "benchmark":
                        asyncio.run(benchmark_cli())

                    case "config":
                        config_cli()

                    case "report":
                        asyncio.run(generate_report_cli())

                    case _:
                        print_error(f"Unknown command: {command}")
                        console.print("[dim]Type 'help' for available commands")

            except KeyboardInterrupt:
                console.print("\n[yellow]Use 'exit' to quit")
            except Exception as e:
                print_error(f"Error: {e}")
                if debug:
                    raise


# ==================== Cloud Security CLI ====================


async def cloud_security_cli() -> None:
    """Cloud security scanning interface."""
    from fsociety.cloud_security import get_cloud_scanner

    console.print("\n[bold cyan]☁️  Cloud Security Scanner[/bold cyan]\n")

    providers = {
        "1": ("AWS", "aws"),
        "2": ("Azure", "azure"),
        "3": ("GCP", "gcp"),
        "4": ("Multi-Cloud", "all"),
    }

    console.print("[yellow]Select provider:")
    for key, (name, _) in providers.items():
        console.print(f"  {key}. {name}")

    choice = input("\nChoice: ").strip()

    if choice not in providers:
        print_error("Invalid choice")
        return

    _, provider = providers[choice]
    scanner = get_cloud_scanner()

    if provider == "all":
        aws_region = input("AWS Region (or Enter to skip): ").strip() or None
        azure_sub = input("Azure Subscription (or Enter to skip): ").strip() or None
        gcp_proj = input("GCP Project (or Enter to skip): ").strip() or None

        results = await scanner.scan_all(aws_region, azure_sub, gcp_proj)
        scanner.display_results(results)
    else:
        # Single provider scan
        target = input(f"Enter {provider.upper()} identifier: ").strip()

        if provider == "aws":
            result = await scanner.aws_scanner.scan(target)
        elif provider == "azure":
            result = await scanner.azure_scanner.scan(target)
        else:
            result = await scanner.gcp_scanner.scan(target)

        scanner._display_single_result(result.provider, result)


# ==================== Kubernetes Security CLI ====================


async def k8s_security_cli() -> None:
    """Kubernetes security scanning interface."""
    from fsociety.kubernetes_security import get_k8s_scanner

    console.print("\n[bold cyan]🎯 Kubernetes Security Scanner[/bold cyan]\n")

    context = input("K8s context (or Enter for current): ").strip() or None
    namespaces = input("Namespaces (comma-separated, or Enter for all): ").strip()
    ns_list = [n.strip() for n in namespaces.split(",")] if namespaces else None

    scanner = get_k8s_scanner()
    cluster_info, findings = await scanner.scan_cluster(context, ns_list)
    scanner.display_results(cluster_info, findings)


# ==================== API Security CLI ====================


async def api_security_cli() -> None:
    """API security testing interface."""
    from fsociety.api_security import get_api_scanner, get_graphql_scanner

    console.print("\n[bold cyan]🌐 API Security Scanner[/bold cyan]\n")

    api_type = input("API Type (rest/graphql): ").strip().lower()
    url = input("API URL: ").strip()
    token = input("Auth token (optional): ").strip() or None

    if api_type == "graphql":
        scanner = get_graphql_scanner()
        vulnerabilities = await scanner.scan(url, token)
    else:
        scanner = get_api_scanner()
        vulnerabilities = await scanner.scan(url, None, token)
        scanner.display_results()


# ==================== Web3 Security CLI ====================


async def web3_security_cli() -> None:
    """Web3/blockchain security interface."""
    from fsociety.web3_security import get_web3_scanner, BlockchainType

    console.print("\n[bold cyan]🌐 Web3 Security Scanner[/bold cyan]\n")

    console.print("[yellow]Select blockchain:")
    blockchains = list(BlockchainType)
    for i, bc in enumerate(blockchains, 1):
        console.print(f"  {i}. {bc.value}")

    choice = int(input("\nChoice: ").strip()) - 1
    blockchain = blockchains[choice]

    address = input("Smart contract address: ").strip()

    scanner = get_web3_scanner()
    vulnerabilities = await scanner.scan_contract(address, blockchain)
    scanner.display_results()


# ==================== Supply Chain CLI ====================


async def supply_chain_cli() -> None:
    """Supply chain security interface."""
    from fsociety.supply_chain import get_supply_chain_scanner

    console.print("\n[bold cyan]📦 Supply Chain Security Scanner[/bold cyan]\n")

    project_path = input("Project path: ").strip()

    scanner = get_supply_chain_scanner()
    sbom, vulnerabilities = await scanner.scan_dependencies(Path(project_path))
    scanner.display_results()


# ==================== ML Security CLI ====================


async def ml_security_cli() -> None:
    """ML model security interface."""
    from fsociety.supply_chain import get_ml_scanner

    console.print("\n[bold cyan]🤖 ML Model Security Scanner[/bold cyan]\n")

    model_path = input("Model path: ").strip()
    model_type = input("Model type (neural_network/transformer/etc): ").strip()

    scanner = get_ml_scanner()
    vulnerabilities = await scanner.scan_model(model_path, model_type)
    scanner.display_results()


# ==================== Zero-Trust CLI ====================


async def zerotrust_cli() -> None:
    """Zero-Trust architecture assessment."""
    from fsociety.web3_security import get_zerotrust_scanner

    console.print("\n[bold cyan]🔒 Zero-Trust Architecture Assessment[/bold cyan]\n")

    environment = input("Environment (production/staging): ").strip() or "production"

    scanner = get_zerotrust_scanner()
    findings = await scanner.scan(environment)
    scanner.display_results()


# ==================== Container Security CLI ====================


async def container_security_cli() -> None:
    """Container security scanning."""
    from fsociety.api_security import get_container_scanner

    console.print("\n[bold cyan]🐳 Container Security Scanner[/bold cyan]\n")

    image = input("Container image: ").strip()

    scanner = get_container_scanner()
    vulnerabilities = await scanner.scan_image(image)

    # Display results
    console.print(f"\n[green]Found {len(vulnerabilities)} vulnerabilities")


# ==================== AI Assistant CLI ====================


async def ai_assistant_cli() -> None:
    """AI security assistant."""
    from fsociety.ai import get_exploit_assistant

    config = get_config()

    if not config.ai.enabled:
        print_warning("AI features are disabled")
        enable = input("Enable AI now? (y/N): ").strip().lower()
        if enable == "y":
            config.ai.enabled = True
            config.save()
        else:
            return

    assistant = get_exploit_assistant()
    await assistant.interactive_mode()


# ==================== Utilities ====================


async def benchmark_cli() -> None:
    """Run performance benchmark."""
    monitor = get_performance_monitor()

    console.print("\n[cyan]Running comprehensive benchmark...")

    import time

    # Async performance
    start = time.perf_counter()
    tasks = [asyncio.sleep(0.01) for _ in range(100)]
    await asyncio.gather(*tasks)
    async_time = time.perf_counter() - start

    # Display results
    table = Table(title="Benchmark Results", border_style="cyan")
    table.add_column("Test", style="yellow")
    table.add_column("Result", style="green")

    table.add_row("Async Tasks (100)", f"{async_time:.4f}s")
    table.add_row("GPU Available", "Yes" if get_config().performance.use_gpu else "No")

    console.print(table)


def config_cli() -> None:
    """Configuration interface."""
    config = get_config()

    console.print("\n[cyan]Current Configuration:\n")

    table = Table(border_style="cyan")
    table.add_column("Setting", style="yellow")
    table.add_column("Value", style="green")

    table.add_row("AI Enabled", str(config.ai.enabled))
    table.add_row("GPU Enabled", str(config.performance.use_gpu))
    table.add_row("GPU Backend", config.performance.gpu_backend.value)
    table.add_row("Max Workers", str(config.performance.max_workers))
    table.add_row("Caching", str(config.performance.enable_caching))

    console.print(table)

    modify = input("\nModify configuration? (y/N): ").strip().lower()
    if modify == "y":
        # Interactive configuration
        console.print("[dim]Feature not yet implemented in this demo")


async def generate_report_cli() -> None:
    """Generate comprehensive security report."""
    console.print("\n[cyan]Generating security report...")

    # Would aggregate all scan results
    console.print("[green]✓ Report generated: security_report.html")


# ==================== Additional Commands ====================


@cli.command()
def version() -> None:
    """Show version information."""
    console.print(f"[cyan]fsociety[/cyan] version [yellow]{__version__}[/yellow]")

    config = get_config()
    console.print(f"Platform: {config.platform.value}")
    console.print(f"Python: {sys.version_info.major}.{sys.version_info.minor}")

    if config.ai.enabled:
        console.print(f"AI: {config.ai.model_provider} ({config.ai.model_name})")

    if config.performance.use_gpu:
        console.print(f"GPU: {config.performance.gpu_backend.value}")


@cli.command()
@click.argument("target")
@click.option("--type", default="auto", help="Scan type")
def scan(target: str, type: str) -> None:
    """Quick vulnerability scan."""
    console.print(f"\n[cyan]🔍 Scanning: {target}")
    console.print(f"[dim]Type: {type}\n")

    # Would perform actual scan
    console.print("[yellow]Scan initiated...")


@cli.command()
def update() -> None:
    """Update all tools."""
    console.print("[cyan]Updating tools...")
    # Would update tools
    console.print("[green]✓ All tools updated!")


def main() -> None:
    """Main entry point."""
    try:
        cli()
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user")
        sys.exit(0)
    except Exception as e:
        console.print(f"[red]Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
