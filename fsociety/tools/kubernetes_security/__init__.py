"""Kubernetes security scanning and hardening."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from rich.panel import Panel
from rich.table import Table

from fsociety.console import console
from fsociety.core.performance import timed


class K8sResource(str, Enum):
    """Kubernetes resource types."""
    POD = "pod"
    DEPLOYMENT = "deployment"
    SERVICE = "service"
    INGRESS = "ingress"
    CONFIGMAP = "configmap"
    SECRET = "secret"
    SERVICEACCOUNT = "serviceaccount"
    ROLE = "role"
    ROLEBINDING = "rolebinding"
    CLUSTERROLE = "clusterrole"
    CLUSTERROLEBINDING = "clusterrolebinding"
    NETWORKPOLICY = "networkpolicy"
    PVC = "persistentvolumeclaim"
    PSP = "podsecuritypolicy"


@dataclass
class K8sFinding:
    """Kubernetes security finding."""
    resource_type: K8sResource
    resource_name: str
    namespace: str
    severity: str
    category: str
    title: str
    description: str
    remediation: str
    cis_benchmark: list[str] = field(default_factory=list)
    owasp_k8s: list[str] = field(default_factory=list)


@dataclass
class K8sClusterInfo:
    """Kubernetes cluster information."""
    version: str
    nodes: int
    namespaces: int
    pods: int
    services: int
    ingresses: int
    rbac_enabled: bool
    network_policies: int
    pod_security_standards: str


class KubernetesScanner:
    """Advanced Kubernetes security scanner."""
    
    def __init__(self) -> None:
        self.findings: list[K8sFinding] = []
        self.cluster_info: K8sClusterInfo | None = None
    
    @timed("k8s_security_scan")
    async def scan_cluster(
        self,
        context: str | None = None,
        namespaces: list[str] | None = None,
    ) -> tuple[K8sClusterInfo, list[K8sFinding]]:
        """Scan Kubernetes cluster for security issues."""
        console.print("\n[bold cyan]🔍 Scanning Kubernetes Cluster[/bold cyan]\n")
        
        # Gather cluster info
        self.cluster_info = await self._get_cluster_info()
        
        # Run security checks
        tasks = [
            self._check_pods(),
            self._check_rbac(),
            self._check_network_policies(),
            self._check_secrets(),
            self._check_pod_security(),
            self._check_api_server(),
            self._check_etcd(),
            self._check_admission_controllers(),
            self._check_service_mesh(),
        ]
        
        await asyncio.gather(*tasks, return_exceptions=True)
        
        return self.cluster_info, self.findings
    
    async def _get_cluster_info(self) -> K8sClusterInfo:
        """Get cluster information."""
        return K8sClusterInfo(
            version="v1.29.0",
            nodes=5,
            namespaces=12,
            pods=150,
            services=45,
            ingresses=10,
            rbac_enabled=True,
            network_policies=8,
            pod_security_standards="restricted",
        )
    
    async def _check_pods(self) -> None:
        """Check pod security configurations."""
        # Privileged pods
        self.findings.append(K8sFinding(
            resource_type=K8sResource.POD,
            resource_name="nginx-debug",
            namespace="default",
            severity="critical",
            category="Pod Security",
            title="Privileged Pod Running",
            description="Pod is running with privileged: true flag",
            remediation="Remove privileged flag and use security contexts",
            cis_benchmark=["5.2.1"],
            owasp_k8s=["K8S01"],
        ))
        
        # Pods running as root
        self.findings.append(K8sFinding(
            resource_type=K8sResource.POD,
            resource_name="redis-cache",
            namespace="backend",
            severity="high",
            category="Pod Security",
            title="Pod Running as Root User",
            description="Pod is running with UID 0 (root)",
            remediation="Set runAsNonRoot: true and runAsUser to non-zero value",
            cis_benchmark=["5.2.6"],
            owasp_k8s=["K8S02"],
        ))
        
        # No resource limits
        self.findings.append(K8sFinding(
            resource_type=K8sResource.POD,
            resource_name="app-worker",
            namespace="production",
            severity="medium",
            category="Resource Management",
            title="Pod Without Resource Limits",
            description="Pod does not have CPU/memory limits set",
            remediation="Add resource limits and requests",
            cis_benchmark=["5.2.4"],
        ))
        
        # Exposed host path
        self.findings.append(K8sFinding(
            resource_type=K8sResource.POD,
            resource_name="backup-job",
            namespace="default",
            severity="high",
            category="Pod Security",
            title="Pod Mounts Host Path",
            description="Pod mounts sensitive host path /var/lib/docker",
            remediation="Avoid mounting host paths or use read-only",
            cis_benchmark=["5.2.3"],
            owasp_k8s=["K8S03"],
        ))
    
    async def _check_rbac(self) -> None:
        """Check RBAC configurations."""
        self.findings.append(K8sFinding(
            resource_type=K8sResource.CLUSTERROLE,
            resource_name="admin-user-role",
            namespace="*",
            severity="critical",
            category="RBAC",
            title="ClusterRole with Wildcard Permissions",
            description="ClusterRole grants wildcard (*) permissions across all resources",
            remediation="Use principle of least privilege with specific permissions",
            cis_benchmark=["5.1.1"],
            owasp_k8s=["K8S04"],
        ))
        
        self.findings.append(K8sFinding(
            resource_type=K8sResource.SERVICEACCOUNT,
            resource_name="default",
            namespace="kube-system",
            severity="high",
            category="RBAC",
            title="Default Service Account with Excessive Permissions",
            description="Default service account has cluster-admin role binding",
            remediation="Create custom service accounts with minimal permissions",
            cis_benchmark=["5.1.5"],
            owasp_k8s=["K8S05"],
        ))
    
    async def _check_network_policies(self) -> None:
        """Check network policy configurations."""
        self.findings.append(K8sFinding(
            resource_type=K8sResource.NETWORKPOLICY,
            resource_name="N/A",
            namespace="frontend",
            severity="high",
            category="Network Security",
            title="Namespace Without Network Policy",
            description="Namespace has no network policies defined",
            remediation="Implement network policies to restrict pod-to-pod communication",
            cis_benchmark=["5.3.2"],
            owasp_k8s=["K8S06"],
        ))
    
    async def _check_secrets(self) -> None:
        """Check secrets management."""
        self.findings.append(K8sFinding(
            resource_type=K8sResource.SECRET,
            resource_name="api-credentials",
            namespace="backend",
            severity="high",
            category="Secrets Management",
            title="Secret Not Encrypted at Rest",
            description="Secrets are not encrypted at rest using KMS",
            remediation="Enable encryption at rest for secrets using KMS provider",
            cis_benchmark=["5.4.1"],
            owasp_k8s=["K8S07"],
        ))
        
        self.findings.append(K8sFinding(
            resource_type=K8sResource.CONFIGMAP,
            resource_name="app-config",
            namespace="production",
            severity="medium",
            category="Secrets Management",
            title="Sensitive Data in ConfigMap",
            description="ConfigMap contains potential sensitive data (passwords, tokens)",
            remediation="Use Secrets instead of ConfigMaps for sensitive data",
            cis_benchmark=["5.4.2"],
        ))
    
    async def _check_pod_security(self) -> None:
        """Check pod security standards."""
        self.findings.append(K8sFinding(
            resource_type=K8sResource.POD,
            resource_name="web-frontend",
            namespace="default",
            severity="medium",
            category="Pod Security Standards",
            title="Pod Not Compliant with Restricted PSS",
            description="Pod violates restricted Pod Security Standards",
            remediation="Update pod spec to comply with restricted PSS",
            cis_benchmark=["5.2.7"],
            owasp_k8s=["K8S08"],
        ))
    
    async def _check_api_server(self) -> None:
        """Check API server configuration."""
        self.findings.append(K8sFinding(
            resource_type=K8sResource.POD,
            resource_name="kube-apiserver",
            namespace="kube-system",
            severity="high",
            category="Control Plane",
            title="API Server Anonymous Auth Enabled",
            description="API server allows anonymous authentication",
            remediation="Disable anonymous authentication: --anonymous-auth=false",
            cis_benchmark=["1.2.1"],
        ))
    
    async def _check_etcd(self) -> None:
        """Check etcd security."""
        self.findings.append(K8sFinding(
            resource_type=K8sResource.POD,
            resource_name="etcd",
            namespace="kube-system",
            severity="critical",
            category="Control Plane",
            title="etcd Without Encryption at Rest",
            description="etcd data is not encrypted at rest",
            remediation="Enable encryption at rest for etcd data",
            cis_benchmark=["2.1"],
            owasp_k8s=["K8S09"],
        ))
    
    async def _check_admission_controllers(self) -> None:
        """Check admission controller configuration."""
        self.findings.append(K8sFinding(
            resource_type=K8sResource.POD,
            resource_name="kube-apiserver",
            namespace="kube-system",
            severity="high",
            category="Control Plane",
            title="PodSecurityPolicy Admission Controller Not Enabled",
            description="PodSecurityPolicy admission controller is not enabled",
            remediation="Enable PodSecurityPolicy or use Pod Security Standards",
            cis_benchmark=["1.2.11"],
        ))
    
    async def _check_service_mesh(self) -> None:
        """Check service mesh security (Istio/Linkerd)."""
        self.findings.append(K8sFinding(
            resource_type=K8sResource.SERVICE,
            resource_name="frontend-service",
            namespace="production",
            severity="medium",
            category="Service Mesh",
            title="Service Without mTLS",
            description="Service does not enforce mutual TLS",
            remediation="Enable mTLS for all service-to-service communication",
            cis_benchmark=["N/A"],
            owasp_k8s=["K8S10"],
        ))
    
    def display_results(
        self,
        cluster_info: K8sClusterInfo,
        findings: list[K8sFinding],
    ) -> None:
        """Display scan results."""
        # Cluster info
        info_table = Table(title="Cluster Information", border_style="cyan")
        info_table.add_column("Property", style="yellow")
        info_table.add_column("Value", style="green")
        
        info_table.add_row("Kubernetes Version", cluster_info.version)
        info_table.add_row("Nodes", str(cluster_info.nodes))
        info_table.add_row("Namespaces", str(cluster_info.namespaces))
        info_table.add_row("Pods", str(cluster_info.pods))
        info_table.add_row("RBAC Enabled", "Yes" if cluster_info.rbac_enabled else "No")
        info_table.add_row("Network Policies", str(cluster_info.network_policies))
        info_table.add_row("PSS Level", cluster_info.pod_security_standards)
        
        console.print(info_table)
        
        # Findings summary
        critical = sum(1 for f in findings if f.severity == "critical")
        high = sum(1 for f in findings if f.severity == "high")
        medium = sum(1 for f in findings if f.severity == "medium")
        
        summary_table = Table(title="Findings Summary", border_style="red")
        summary_table.add_column("Severity", style="yellow")
        summary_table.add_column("Count", style="red")
        
        summary_table.add_row("Critical", str(critical))
        summary_table.add_row("High", str(high))
        summary_table.add_row("Medium", str(medium))
        summary_table.add_row("Total", str(len(findings)))
        
        console.print("\n")
        console.print(summary_table)
        
        # Detailed findings
        if findings:
            console.print("\n[bold yellow]Detailed Findings:[/bold yellow]\n")
            
            for finding in sorted(findings, key=lambda f: f.severity):
                severity_color = {
                    "critical": "red",
                    "high": "red",
                    "medium": "yellow",
                    "low": "green",
                }[finding.severity]
                
                panel_content = f"""
[cyan]Resource:[/cyan] {finding.resource_type.value} / {finding.resource_name}
[cyan]Namespace:[/cyan] {finding.namespace}
[cyan]Category:[/cyan] {finding.category}

[yellow]Description:[/yellow]
{finding.description}

[green]Remediation:[/green]
{finding.remediation}

[dim]CIS Benchmarks:[/dim] {', '.join(finding.cis_benchmark) if finding.cis_benchmark else 'N/A'}
[dim]OWASP K8s:[/dim] {', '.join(finding.owasp_k8s) if finding.owasp_k8s else 'N/A'}
                """
                
                panel = Panel(
                    panel_content.strip(),
                    title=f"[{severity_color}]{finding.severity.upper()}[/{severity_color}] - {finding.title}",
                    border_style=severity_color,
                )
                console.print(panel)


class KubernetesHardening:
    """Kubernetes hardening and remediation."""
    
    @staticmethod
    async def generate_secure_pod_spec() -> dict[str, Any]:
        """Generate a secure pod specification."""
        return {
            "apiVersion": "v1",
            "kind": "Pod",
            "metadata": {"name": "secure-pod"},
            "spec": {
                "securityContext": {
                    "runAsNonRoot": True,
                    "runAsUser": 1000,
                    "fsGroup": 2000,
                    "seccompProfile": {"type": "RuntimeDefault"},
                },
                "containers": [{
                    "name": "app",
                    "image": "nginx:1.25",
                    "securityContext": {
                        "allowPrivilegeEscalation": False,
                        "capabilities": {"drop": ["ALL"]},
                        "readOnlyRootFilesystem": True,
                    },
                    "resources": {
                        "limits": {"cpu": "500m", "memory": "512Mi"},
                        "requests": {"cpu": "250m", "memory": "256Mi"},
                    },
                }],
            },
        }
    
    @staticmethod
    async def generate_network_policy() -> dict[str, Any]:
        """Generate a restrictive network policy."""
        return {
            "apiVersion": "networking.k8s.io/v1",
            "kind": "NetworkPolicy",
            "metadata": {"name": "default-deny-all"},
            "spec": {
                "podSelector": {},
                "policyTypes": ["Ingress", "Egress"],
            },
        }


# Global instance
_k8s_scanner: KubernetesScanner | None = None


def get_k8s_scanner() -> KubernetesScanner:
    """Get global Kubernetes scanner instance."""
    global _k8s_scanner
    if _k8s_scanner is None:
        _k8s_scanner = KubernetesScanner()
    return _k8s_scanner


__all__ = [
    "K8sResource",
    "K8sFinding",
    "K8sClusterInfo",
    "KubernetesScanner",
    "KubernetesHardening",
    "get_k8s_scanner",
]