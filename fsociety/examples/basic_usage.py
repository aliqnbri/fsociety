"""Example usage scripts for fsociety 4.0."""

import asyncio
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.progress import track

# Initialize console
console = Console()


async def example_basic_scan():
    """Example: Basic network scanning."""
    console.print("\n[bold cyan]Example 1: Basic Network Scanning[/bold cyan]")
    
    from fsociety.information_gathering.nmap_async import nmap_async
    
    # Single target scan
    console.print("\n[yellow]Scanning single target...")
    result = await nmap_async.scan("scanme.nmap.org", nmap_async.ScanType.QUICK)
    
    console.print(f"\n[green]Scan complete!")
    console.print(f"Host: {result.host}")
    console.print(f"Status: {result.status}")
    console.print(f"Open ports: {len(result.ports)}")
    
    for port in result.ports[:5]:
        console.print(f"  - Port {port['port']}: {port.get('service', 'unknown')}")


async def example_concurrent_scanning():
    """Example: Concurrent scanning of multiple targets."""
    console.print("\n[bold cyan]Example 2: Concurrent Scanning[/bold cyan]")
    
    from fsociety.information_gathering.nmap_async import nmap_async
    
    targets = [
        "scanme.nmap.org",
        "example.com",
        "github.com",
    ]
    
    console.print(f"\n[yellow]Scanning {len(targets)} targets concurrently...")
    
    # Scan all targets concurrently
    results = await nmap_async.batch_scan(targets, nmap_async.ScanType.SIMPLE)
    
    console.print(f"\n[green]All scans complete!")
    for result in results:
        console.print(f"\n{result.host}: {result.status}")
        console.print(f"  Open ports: {len(result.ports)}")


async def example_ai_analysis():
    """Example: AI-powered vulnerability analysis."""
    console.print("\n[bold cyan]Example 3: AI-Powered Analysis[/bold cyan]")
    
    from fsociety.ai import get_ai_engine
    from fsociety.core.config import get_config
    
    config = get_config()
    
    if not config.ai.enabled:
        console.print("[yellow]AI features are disabled. Enable with: fsociety config --ai")
        return
    
    ai_engine = get_ai_engine()
    await ai_engine.initialize()
    
    # Mock scan results
    scan_results = {
        "host": "vulnerable.example.com",
        "open_ports": [
            {"port": 80, "service": "http", "version": "Apache 2.4.1"},
            {"port": 3306, "service": "mysql", "version": "5.5.0"},
        ],
        "os": {"name": "Linux", "version": "Ubuntu 18.04"},
    }
    
    console.print("\n[yellow]Analyzing vulnerabilities with AI...")
    result = await ai_engine.analyze_vulnerability(
        target="vulnerable.example.com",
        scan_results=scan_results,
    )
    
    console.print(f"\n[green]AI Analysis Complete!")
    console.print(f"Severity: [{result.severity}]{result.severity.upper()}")
    console.print(f"Confidence: {result.confidence:.0%}")
    console.print(f"\nSummary: {result.summary}")
    
    if result.recommendations:
        console.print("\n[yellow]Recommendations:")
        for i, rec in enumerate(result.recommendations, 1):
            console.print(f"  {i}. {rec}")


async def example_exploit_generation():
    """Example: AI exploit generation."""
    console.print("\n[bold cyan]Example 4: AI Exploit Generation[/bold cyan]")
    
    from fsociety.ai import get_exploit_assistant
    from fsociety.core.config import get_config
    
    config = get_config()
    
    if not config.ai.enabled:
        console.print("[yellow]AI features are disabled.")
        return
    
    assistant = get_exploit_assistant()
    await assistant.initialize()
    
    console.print("\n[yellow]Generating exploit payload...")
    payload = await assistant.generate_payload(
        exploit_type="sql_injection",
        target_info={
            "database": "MySQL 5.5",
            "vulnerable_param": "id",
            "url": "http://example.com/page.php?id=1",
        },
    )
    
    console.print(f"\n[green]Payload generated!")
    console.print(Panel(payload[:500], title="Exploit Payload", border_style="green"))


async def example_caching():
    """Example: Using the caching system."""
    console.print("\n[bold cyan]Example 5: Caching System[/bold cyan]")
    
    from fsociety.core.cache import get_cache_manager
    import time
    
    cache = get_cache_manager()
    
    # Expensive operation
    async def expensive_computation(n: int) -> int:
        await asyncio.sleep(1)  # Simulate expensive operation
        return n ** 2
    
    # First call (cache miss)
    console.print("\n[yellow]First call (cache miss)...")
    start = time.time()
    result1 = await expensive_computation(100)
    time1 = time.time() - start
    
    # Store in cache
    await cache.set("computation:100", result1)
    
    # Second call (cache hit)
    console.print("[yellow]Second call (cache hit)...")
    start = time.time()
    result2 = await cache.get("computation:100")
    time2 = time.time() - start
    
    console.print(f"\n[green]Results:")
    console.print(f"First call: {time1:.3f}s")
    console.print(f"Second call: {time2:.3f}s")
    console.print(f"Speedup: {time1/time2:.1f}x")
    
    # Show cache stats
    stats = await cache.stats()
    console.print(f"\nCache hit rate: {stats.get('hit_rate', 0):.1%}")


async def example_performance_monitoring():
    """Example: Performance monitoring."""
    console.print("\n[bold cyan]Example 6: Performance Monitoring[/bold cyan]")
    
    from fsociety.core.performance import get_performance_monitor, timed
    
    monitor = get_performance_monitor()
    
    # Define timed operations
    @timed("fast_operation")
    async def fast_op():
        await asyncio.sleep(0.1)
    
    @timed("slow_operation")
    async def slow_op():
        await asyncio.sleep(0.5)
    
    console.print("\n[yellow]Running operations...")
    
    # Run operations
    for _ in range(5):
        await fast_op()
        await slow_op()
    
    # Display metrics
    console.print("\n[green]Performance Metrics:")
    monitor.display_report()


async def example_gpu_acceleration():
    """Example: GPU-accelerated operations."""
    console.print("\n[bold cyan]Example 7: GPU Acceleration[/bold cyan]")
    
    from fsociety.core.config import get_config
    from fsociety.core.performance import get_gpu_memory_manager
    
    config = get_config()
    gpu_manager = get_gpu_memory_manager()
    
    if not config.performance.use_gpu:
        console.print("[yellow]GPU acceleration not available")
        return
    
    console.print(f"\n[green]GPU Backend: {config.performance.gpu_backend.value}")
    
    try:
        import torch
        
        if torch.cuda.is_available():
            # Show GPU info
            info = gpu_manager.get_memory_info()
            console.print(f"\nGPU Memory:")
            console.print(f"  Total: {info['total_gb']:.2f} GB")
            console.print(f"  Free: {info['free_gb']:.2f} GB")
            console.print(f"  Utilization: {info['utilization']:.1f}%")
            
            # Perform GPU operation
            console.print("\n[yellow]Running GPU operation...")
            device = torch.device("cuda:0")
            
            async with gpu_manager.auto_cleanup():
                a = torch.randn(1000, 1000, device=device)
                b = torch.randn(1000, 1000, device=device)
                c = torch.matmul(a, b)
                torch.cuda.synchronize()
            
            console.print("[green]GPU operation complete!")
    
    except ImportError:
        console.print("[yellow]PyTorch not installed")


async def example_batch_operations():
    """Example: Batch operations with rate limiting."""
    console.print("\n[bold cyan]Example 8: Batch Operations[/bold cyan]")
    
    from fsociety.core.performance import RateLimiter
    
    # Create rate limiter (5 requests per second)
    limiter = RateLimiter(calls=5, period=1.0)
    
    async def api_call(i: int) -> str:
        async with limiter():
            await asyncio.sleep(0.1)  # Simulate API call
            return f"Result {i}"
    
    console.print("\n[yellow]Making 20 rate-limited API calls...")
    
    tasks = [api_call(i) for i in range(20)]
    results = await asyncio.gather(*tasks)
    
    console.print(f"\n[green]Completed {len(results)} calls with rate limiting")


def show_menu():
    """Show example menu."""
    console.print("\n[bold cyan]═══ fsociety 4.0 Examples ═══[/bold cyan]\n")
    
    examples = [
        ("1", "Basic Network Scanning", example_basic_scan),
        ("2", "Concurrent Scanning", example_concurrent_scanning),
        ("3", "AI-Powered Analysis", example_ai_analysis),
        ("4", "AI Exploit Generation", example_exploit_generation),
        ("5", "Caching System", example_caching),
        ("6", "Performance Monitoring", example_performance_monitoring),
        ("7", "GPU Acceleration", example_gpu_acceleration),
        ("8", "Batch Operations", example_batch_operations),
        ("9", "Run All Examples", None),
        ("0", "Exit", None),
    ]
    
    for num, name, _ in examples:
        console.print(f"  [{num}] {name}")
    
    return examples


async def main():
    """Main example runner."""
    examples_map = {
        "1": example_basic_scan,
        "2": example_concurrent_scanning,
        "3": example_ai_analysis,
        "4": example_exploit_generation,
        "5": example_caching,
        "6": example_performance_monitoring,
        "7": example_gpu_acceleration,
        "8": example_batch_operations,
    }
    
    while True:
        examples = show_menu()
        
        choice = input("\nSelect example (0-9): ").strip()
        
        if choice == "0":
            console.print("\n[yellow]Goodbye!")
            break
        
        elif choice == "9":
            console.print("\n[bold green]Running all examples...[/bold green]")
            for func in examples_map.values():
                try:
                    await func()
                    await asyncio.sleep(1)
                except Exception as e:
                    console.print(f"[red]Error: {e}")
        
        elif choice in examples_map:
            try:
                await examples_map[choice]()
            except Exception as e:
                console.print(f"\n[red]Error: {e}")
                import traceback
                traceback.print_exc()
        
        else:
            console.print("[red]Invalid choice!")
        
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user")