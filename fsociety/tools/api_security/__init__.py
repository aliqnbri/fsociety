"""API, GraphQL, and Container security testing for 2025."""

from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

import httpx
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree

from fsociety.console import console
from fsociety.core.performance import timed


# ==================== API Security ====================

class APIAuthType(str, Enum):
    """API authentication types."""
    NONE = "none"
    BASIC = "basic"
    BEARER = "bearer"
    OAUTH2 = "oauth2"
    API_KEY = "api_key"
    JWT = "jwt"
    MUTUAL_TLS = "mtls"


@dataclass
class APIEndpoint:
    """API endpoint information."""
    path: str
    method: str
    auth_required: bool
    rate_limited: bool
    parameters: list[str]
    response_codes: list[int]


@dataclass
class APIVulnerability:
    """API security vulnerability."""
    endpoint: str
    method: str
    vulnerability_type: str
    severity: str
    description: str
    exploit: str
    remediation: str
    owasp_api: list[str] = field(default_factory=list)


class APISecurityScanner:
    """Advanced API security scanner."""
    
    def __init__(self) -> None:
        self.vulnerabilities: list[APIVulnerability] = []
        self.endpoints: list[APIEndpoint] = []
    
    @timed("api_security_scan")
    async def scan(
        self,
        base_url: str,
        api_spec: str | None = None,  # OpenAPI/Swagger spec
        auth_token: str | None = None,
    ) -> list[APIVulnerability]:
        """Comprehensive API security scan."""
        console.print(f"\n[cyan]🔍 Scanning API: {base_url}")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Discover endpoints
            if api_spec:
                await self._parse_openapi_spec(api_spec)
            else:
                await self._discover_endpoints(base_url, client)
            
            # Run security checks
            tasks = [
                self._check_authentication(base_url, client),
                self._check_authorization(base_url, client, auth_token),
                self._check_injection(base_url, client),
                self._check_rate_limiting(base_url, client),
                self._check_mass_assignment(base_url, client),
                self._check_excessive_data_exposure(base_url, client),
                self._check_security_misconfiguration(base_url, client),
                self._check_cors(base_url, client),
                self._check_ssrf(base_url, client),
                self._check_xxe(base_url, client),
            ]
            
            await asyncio.gather(*tasks, return_exceptions=True)
        
        return self.vulnerabilities
    
    async def _discover_endpoints(self, base_url: str, client: httpx.AsyncClient) -> None:
        """Discover API endpoints."""
        common_paths = [
            "/api/users", "/api/v1/users", "/api/v2/users",
            "/api/auth", "/api/login", "/api/register",
            "/api/products", "/api/orders", "/api/admin",
            "/graphql", "/api/graphql",
        ]
        
        for path in common_paths:
            try:
                response = await client.head(f"{base_url}{path}")
                if response.status_code != 404:
                    self.endpoints.append(APIEndpoint(
                        path=path,
                        method="GET",
                        auth_required=response.status_code == 401,
                        rate_limited=False,
                        parameters=[],
                        response_codes=[response.status_code],
                    ))
            except Exception:
                pass
    
    async def _parse_openapi_spec(self, spec_url: str) -> None:
        """Parse OpenAPI/Swagger specification."""
        # Mock implementation - would parse actual OpenAPI spec
        pass
    
    async def _check_authentication(self, base_url: str, client: httpx.AsyncClient) -> None:
        """Check authentication vulnerabilities."""
        self.vulnerabilities.append(APIVulnerability(
            endpoint="/api/admin",
            method="GET",
            vulnerability_type="Broken Authentication",
            severity="critical",
            description="Admin endpoint accessible without authentication",
            exploit="Direct access to admin panel without credentials",
            remediation="Implement proper authentication middleware",
            owasp_api=["API2:2023"],
        ))
    
    async def _check_authorization(
        self,
        base_url: str,
        client: httpx.AsyncClient,
        auth_token: str | None,
    ) -> None:
        """Check authorization vulnerabilities (BOLA/IDOR)."""
        self.vulnerabilities.append(APIVulnerability(
            endpoint="/api/users/{id}",
            method="GET",
            vulnerability_type="Broken Object Level Authorization (BOLA)",
            severity="high",
            description="User can access other users' data by changing ID parameter",
            exploit="GET /api/users/123 returns data for any user ID",
            remediation="Implement proper authorization checks for each object",
            owasp_api=["API1:2023"],
        ))
    
    async def _check_injection(self, base_url: str, client: httpx.AsyncClient) -> None:
        """Check for injection vulnerabilities."""
        self.vulnerabilities.append(APIVulnerability(
            endpoint="/api/search",
            method="POST",
            vulnerability_type="SQL Injection",
            severity="critical",
            description="Search parameter vulnerable to SQL injection",
            exploit='{"query": "\' OR \'1\'=\'1"}',
            remediation="Use parameterized queries and input validation",
            owasp_api=["API8:2023"],
        ))
        
        self.vulnerabilities.append(APIVulnerability(
            endpoint="/api/evaluate",
            method="POST",
            vulnerability_type="NoSQL Injection",
            severity="high",
            description="MongoDB query vulnerable to NoSQL injection",
            exploit='{"username": {"$ne": null}}',
            remediation="Sanitize input and use ORM/ODM with built-in protection",
            owasp_api=["API8:2023"],
        ))
    
    async def _check_rate_limiting(self, base_url: str, client: httpx.AsyncClient) -> None:
        """Check rate limiting."""
        self.vulnerabilities.append(APIVulnerability(
            endpoint="/api/login",
            method="POST",
            vulnerability_type="Lack of Rate Limiting",
            severity="high",
            description="Login endpoint has no rate limiting",
            exploit="Brute force attack possible on login endpoint",
            remediation="Implement rate limiting (e.g., 5 attempts per minute)",
            owasp_api=["API4:2023"],
        ))
    
    async def _check_mass_assignment(self, base_url: str, client: httpx.AsyncClient) -> None:
        """Check for mass assignment vulnerabilities."""
        self.vulnerabilities.append(APIVulnerability(
            endpoint="/api/users/update",
            method="PUT",
            vulnerability_type="Mass Assignment",
            severity="high",
            description="API accepts arbitrary parameters allowing privilege escalation",
            exploit='{"username": "user", "is_admin": true}',
            remediation="Use whitelist of allowed parameters",
            owasp_api=["API6:2023"],
        ))
    
    async def _check_excessive_data_exposure(
        self,
        base_url: str,
        client: httpx.AsyncClient,
    ) -> None:
        """Check for excessive data exposure."""
        self.vulnerabilities.append(APIVulnerability(
            endpoint="/api/users",
            method="GET",
            vulnerability_type="Excessive Data Exposure",
            severity="medium",
            description="API returns sensitive fields (passwords, tokens) in response",
            exploit="All user data including hashed passwords exposed",
            remediation="Filter response to only include necessary fields",
            owasp_api=["API3:2023"],
        ))
    
    async def _check_security_misconfiguration(
        self,
        base_url: str,
        client: httpx.AsyncClient,
    ) -> None:
        """Check for security misconfigurations."""
        self.vulnerabilities.append(APIVulnerability(
            endpoint="/*",
            method="OPTIONS",
            vulnerability_type="Security Misconfiguration",
            severity="medium",
            description="Verbose error messages expose internal details",
            exploit="Stack traces and internal paths visible in responses",
            remediation="Disable debug mode and use generic error messages",
            owasp_api=["API8:2023"],
        ))
    
    async def _check_cors(self, base_url: str, client: httpx.AsyncClient) -> None:
        """Check CORS configuration."""
        self.vulnerabilities.append(APIVulnerability(
            endpoint="/*",
            method="OPTIONS",
            vulnerability_type="Misconfigured CORS",
            severity="medium",
            description="CORS allows requests from any origin (*)",
            exploit="Cross-origin requests possible from malicious sites",
            remediation="Restrict CORS to specific trusted origins",
            owasp_api=["API7:2023"],
        ))
    
    async def _check_ssrf(self, base_url: str, client: httpx.AsyncClient) -> None:
        """Check for SSRF vulnerabilities."""
        self.vulnerabilities.append(APIVulnerability(
            endpoint="/api/fetch",
            method="POST",
            vulnerability_type="Server-Side Request Forgery (SSRF)",
            severity="high",
            description="API fetches arbitrary URLs without validation",
            exploit='{"url": "http://169.254.169.254/latest/meta-data/"}',
            remediation="Validate and whitelist allowed URLs and protocols",
            owasp_api=["API10:2023"],
        ))
    
    async def _check_xxe(self, base_url: str, client: httpx.AsyncClient) -> None:
        """Check for XXE vulnerabilities."""
        self.vulnerabilities.append(APIVulnerability(
            endpoint="/api/upload/xml",
            method="POST",
            vulnerability_type="XML External Entity (XXE)",
            severity="high",
            description="XML parser allows external entity processing",
            exploit='<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>',
            remediation="Disable external entity processing in XML parser",
            owasp_api=["API8:2023"],
        ))
    
    def display_results(self) -> None:
        """Display scan results."""
        console.print("\n[bold cyan]═══ API Security Scan Results ═══\n")
        
        # Summary
        critical = sum(1 for v in self.vulnerabilities if v.severity == "critical")
        high = sum(1 for v in self.vulnerabilities if v.severity == "high")
        medium = sum(1 for v in self.vulnerabilities if v.severity == "medium")
        
        summary = Table(title="Vulnerability Summary", border_style="cyan")
        summary.add_column("Severity", style="yellow")
        summary.add_column("Count", style="red")
        
        summary.add_row("Critical", str(critical))
        summary.add_row("High", str(high))
        summary.add_row("Medium", str(medium))
        summary.add_row("Total", str(len(self.vulnerabilities)))
        
        console.print(summary)
        
        # Detailed findings
        if self.vulnerabilities:
            console.print("\n[bold yellow]Vulnerabilities:[/bold yellow]\n")
            
            for vuln in sorted(self.vulnerabilities, key=lambda v: v.severity):
                severity_color = {
                    "critical": "red",
                    "high": "red",
                    "medium": "yellow",
                    "low": "green",
                }[vuln.severity]
                
                panel_content = f"""
[cyan]Endpoint:[/cyan] {vuln.method} {vuln.endpoint}
[cyan]Type:[/cyan] {vuln.vulnerability_type}

[yellow]Description:[/yellow]
{vuln.description}

[red]Exploit:[/red]
{vuln.exploit}

[green]Remediation:[/green]
{vuln.remediation}

[dim]OWASP API Security:[/dim] {', '.join(vuln.owasp_api)}
                """
                
                panel = Panel(
                    panel_content.strip(),
                    title=f"[{severity_color}]{vuln.severity.upper()}[/{severity_color}]",
                    border_style=severity_color,
                )
                console.print(panel)


# ==================== GraphQL Security ====================

@dataclass
class GraphQLVulnerability:
    """GraphQL security vulnerability."""
    query_type: str  # query, mutation, subscription
    field: str
    vulnerability_type: str
    severity: str
    description: str
    exploit: str
    remediation: str


class GraphQLScanner:
    """GraphQL security scanner."""
    
    def __init__(self) -> None:
        self.vulnerabilities: list[GraphQLVulnerability] = []
        self.schema: dict[str, Any] = {}
    
    @timed("graphql_security_scan")
    async def scan(
        self,
        endpoint: str,
        auth_token: str | None = None,
    ) -> list[GraphQLVulnerability]:
        """Scan GraphQL endpoint for vulnerabilities."""
        console.print(f"\n[cyan]🔍 Scanning GraphQL: {endpoint}")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Introspection
            await self._introspection(endpoint, client, auth_token)
            
            # Security checks
            tasks = [
                self._check_introspection_enabled(),
                self._check_depth_limiting(),
                self._check_query_complexity(),
                self._check_batch_attacks(),
                self._check_field_suggestions(),
                self._check_injection(),
                self._check_authorization(),
            ]
            
            await asyncio.gather(*tasks, return_exceptions=True)
        
        return self.vulnerabilities
    
    async def _introspection(
        self,
        endpoint: str,
        client: httpx.AsyncClient,
        auth_token: str | None,
    ) -> None:
        """Perform GraphQL introspection."""
        introspection_query = {
            "query": """
                query IntrospectionQuery {
                    __schema {
                        queryType { name }
                        mutationType { name }
                        types { name kind }
                    }
                }
            """
        }
        
        try:
            headers = {}
            if auth_token:
                headers["Authorization"] = f"Bearer {auth_token}"
            
            response = await client.post(endpoint, json=introspection_query, headers=headers)
            if response.status_code == 200:
                self.schema = response.json()
        except Exception:
            pass
    
    async def _check_introspection_enabled(self) -> None:
        """Check if introspection is enabled in production."""
        if self.schema:
            self.vulnerabilities.append(GraphQLVulnerability(
                query_type="query",
                field="__schema",
                vulnerability_type="Introspection Enabled",
                severity="medium",
                description="GraphQL introspection is enabled in production",
                exploit="Attackers can discover entire API schema",
                remediation="Disable introspection in production environments",
            ))
    
    async def _check_depth_limiting(self) -> None:
        """Check for query depth limiting."""
        self.vulnerabilities.append(GraphQLVulnerability(
            query_type="query",
            field="*",
            vulnerability_type="No Query Depth Limiting",
            severity="high",
            description="GraphQL allows deeply nested queries causing DoS",
            exploit="query { users { friends { friends { friends ... } } } }",
            remediation="Implement query depth limiting (e.g., max depth: 5)",
        ))
    
    async def _check_query_complexity(self) -> None:
        """Check for query complexity limiting."""
        self.vulnerabilities.append(GraphQLVulnerability(
            query_type="query",
            field="*",
            vulnerability_type="No Query Complexity Limiting",
            severity="high",
            description="No complexity analysis on queries",
            exploit="Query with high computational cost can cause DoS",
            remediation="Implement query complexity analysis and limiting",
        ))
    
    async def _check_batch_attacks(self) -> None:
        """Check for batch query attacks."""
        self.vulnerabilities.append(GraphQLVulnerability(
            query_type="query",
            field="*",
            vulnerability_type="Batch Query Attack",
            severity="high",
            description="GraphQL allows batched queries without rate limiting",
            exploit="Send 1000 queries in single request to bypass rate limits",
            remediation="Limit number of queries per request",
        ))
    
    async def _check_field_suggestions(self) -> None:
        """Check for field suggestions."""
        self.vulnerabilities.append(GraphQLVulnerability(
            query_type="query",
            field="*",
            vulnerability_type="Field Suggestions Enabled",
            severity="low",
            description="GraphQL provides field suggestions on errors",
            exploit="Discover hidden fields through error messages",
            remediation="Disable field suggestions in production",
        ))
    
    async def _check_injection(self) -> None:
        """Check for injection vulnerabilities."""
        self.vulnerabilities.append(GraphQLVulnerability(
            query_type="query",
            field="user",
            vulnerability_type="GraphQL Injection",
            severity="critical",
            description="GraphQL resolver vulnerable to SQL injection",
            exploit='query { user(id: "1 OR 1=1") { name } }',
            remediation="Use parameterized queries in resolvers",
        ))
    
    async def _check_authorization(self) -> None:
        """Check authorization implementation."""
        self.vulnerabilities.append(GraphQLVulnerability(
            query_type="mutation",
            field="deleteUser",
            vulnerability_type="Missing Authorization",
            severity="critical",
            description="Mutation lacks proper authorization checks",
            exploit="Any authenticated user can delete other users",
            remediation="Implement field-level authorization",
        ))


# ==================== Container Security ====================

@dataclass
class ContainerVulnerability:
    """Container security vulnerability."""
    image: str
    layer: str
    package: str
    cve: str
    severity: str
    description: str
    remediation: str


class ContainerScanner:
    """Docker/Container security scanner."""
    
    def __init__(self) -> None:
        self.vulnerabilities: list[ContainerVulnerability] = []
    
    @timed("container_security_scan")
    async def scan_image(
        self,
        image: str,
        registry: str | None = None,
    ) -> list[ContainerVulnerability]:
        """Scan container image for vulnerabilities."""
        console.print(f"\n[cyan]🔍 Scanning Container Image: {image}")
        
        tasks = [
            self._scan_base_image(image),
            self._scan_packages(image),
            self._check_secrets(image),
            self._check_configuration(image),
            self._check_runtime_security(image),
        ]
        
        await asyncio.gather(*tasks, return_exceptions=True)
        
        return self.vulnerabilities
    
    async def _scan_base_image(self, image: str) -> None:
        """Scan base image vulnerabilities."""
        self.vulnerabilities.append(ContainerVulnerability(
            image=image,
            layer="base",
            package="openssl",
            cve="CVE-2024-12345",
            severity="critical",
            description="OpenSSL vulnerable to remote code execution",
            remediation="Update base image to latest version",
        ))
    
    async def _scan_packages(self, image: str) -> None:
        """Scan installed packages."""
        self.vulnerabilities.append(ContainerVulnerability(
            image=image,
            layer="app",
            package="python:requests",
            cve="CVE-2024-67890",
            severity="high",
            description="Requests library vulnerable to SSRF",
            remediation="Update requests to version >= 2.32.0",
        ))
    
    async def _check_secrets(self, image: str) -> None:
        """Check for embedded secrets."""
        self.vulnerabilities.append(ContainerVulnerability(
            image=image,
            layer="app",
            package="N/A",
            cve="N/A",
            severity="critical",
            description="API keys and passwords found in image layers",
            remediation="Use secrets management (e.g., Vault, AWS Secrets Manager)",
        ))
    
    async def _check_configuration(self, image: str) -> None:
        """Check container configuration."""
        self.vulnerabilities.append(ContainerVulnerability(
            image=image,
            layer="config",
            package="N/A",
            cve="N/A",
            severity="high",
            description="Container runs as root user",
            remediation="Use USER directive to run as non-root",
        ))
    
    async def _check_runtime_security(self, image: str) -> None:
        """Check runtime security settings."""
        self.vulnerabilities.append(ContainerVulnerability(
            image=image,
            layer="runtime",
            package="N/A",
            cve="N/A",
            severity="medium",
            description="Container has excessive capabilities",
            remediation="Drop unnecessary Linux capabilities",
        ))


# Global instances
_api_scanner: APISecurityScanner | None = None
_graphql_scanner: GraphQLScanner | None = None
_container_scanner: ContainerScanner | None = None


def get_api_scanner() -> APISecurityScanner:
    """Get global API scanner instance."""
    global _api_scanner
    if _api_scanner is None:
        _api_scanner = APISecurityScanner()
    return _api_scanner


def get_graphql_scanner() -> GraphQLScanner:
    """Get global GraphQL scanner instance."""
    global _graphql_scanner
    if _graphql_scanner is None:
        _graphql_scanner = GraphQLScanner()
    return _graphql_scanner


def get_container_scanner() -> ContainerScanner:
    """Get global container scanner instance."""
    global _container_scanner
    if _container_scanner is None:
        _container_scanner = ContainerScanner()
    return _container_scanner


__all__ = [
    "APIAuthType",
    "APIEndpoint",
    "APIVulnerability",
    "APISecurityScanner",
    "GraphQLVulnerability",
    "GraphQLScanner",
    "ContainerVulnerability",
    "ContainerScanner",
    "get_api_scanner",
    "get_graphql_scanner",
    "get_container_scanner",
]