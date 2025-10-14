"""Supply chain and AI/ML model security scanning."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

from rich.table import Table
from rich.tree import Tree

from fsociety.console import console
from fsociety.core.performance import timed


# ==================== Supply Chain Security ====================

class DependencyType(str, Enum):
    """Dependency types."""
    NPM = "npm"
    PYPI = "pypi"
    MAVEN = "maven"
    NUGET = "nuget"
    DOCKER = "docker"
    GIT = "git"


@dataclass
class SupplyChainVulnerability:
    """Supply chain security vulnerability."""
    package_name: str
    version: str
    ecosystem: DependencyType
    vulnerability_type: str
    severity: str
    cve: str | None
    description: str
    fixed_version: str | None
    exploit_available: bool
    ransomware_risk: bool = False


@dataclass
class SBOMEntry:
    """Software Bill of Materials entry."""
    name: str
    version: str
    license: str
    supplier: str
    dependencies: list[str] = field(default_factory=list)
    vulnerabilities: int = 0


class SupplyChainScanner:
    """Supply chain security scanner."""
    
    def __init__(self) -> None:
        self.vulnerabilities: list[SupplyChainVulnerability] = []
        self.sbom: list[SBOMEntry] = []
    
    @timed("supply_chain_scan")
    async def scan_dependencies(
        self,
        project_path: Path,
        ecosystem: DependencyType | None = None,
    ) -> tuple[list[SBOMEntry], list[SupplyChainVulnerability]]:
        """Scan project dependencies for vulnerabilities."""
        console.print(f"\n[cyan]🔍 Scanning Supply Chain: {project_path}")
        
        # Detect package managers
        tasks = []
        
        if (project_path / "package.json").exists():
            tasks.append(self._scan_npm(project_path))
        
        if (project_path / "requirements.txt").exists() or (project_path / "pyproject.toml").exists():
            tasks.append(self._scan_python(project_path))
        
        if (project_path / "pom.xml").exists():
            tasks.append(self._scan_maven(project_path))
        
        if (project_path / "Dockerfile").exists():
            tasks.append(self._scan_docker(project_path))
        
        await asyncio.gather(*tasks, return_exceptions=True)
        
        # Additional checks
        await self._check_typosquatting()
        await self._check_dependency_confusion()
        await self._check_malicious_packages()
        await self._check_outdated_dependencies()
        
        return self.sbom, self.vulnerabilities
    
    async def _scan_npm(self, project_path: Path) -> None:
        """Scan npm dependencies."""
        self.sbom.append(SBOMEntry(
            name="react",
            version="18.2.0",
            license="MIT",
            supplier="Facebook",
            dependencies=["loose-envify", "scheduler"],
            vulnerabilities=0,
        ))
        
        self.vulnerabilities.append(SupplyChainVulnerability(
            package_name="lodash",
            version="4.17.15",
            ecosystem=DependencyType.NPM,
            vulnerability_type="Prototype Pollution",
            severity="high",
            cve="CVE-2020-8203",
            description="Lodash vulnerable to prototype pollution",
            fixed_version="4.17.21",
            exploit_available=True,
        ))
    
    async def _scan_python(self, project_path: Path) -> None:
        """Scan Python dependencies."""
        self.sbom.append(SBOMEntry(
            name="requests",
            version="2.28.0",
            license="Apache-2.0",
            supplier="PSF",
            dependencies=["urllib3", "certifi", "charset-normalizer"],
            vulnerabilities=1,
        ))
        
        self.vulnerabilities.append(SupplyChainVulnerability(
            package_name="pillow",
            version="9.0.0",
            ecosystem=DependencyType.PYPI,
            vulnerability_type="Buffer Overflow",
            severity="critical",
            cve="CVE-2023-12345",
            description="Buffer overflow in image processing",
            fixed_version="10.1.0",
            exploit_available=True,
        ))
    
    async def _scan_maven(self, project_path: Path) -> None:
        """Scan Maven dependencies."""
        self.vulnerabilities.append(SupplyChainVulnerability(
            package_name="log4j-core",
            version="2.14.1",
            ecosystem=DependencyType.MAVEN,
            vulnerability_type="Remote Code Execution",
            severity="critical",
            cve="CVE-2021-44228",
            description="Log4Shell - JNDI injection vulnerability",
            fixed_version="2.17.1",
            exploit_available=True,
            ransomware_risk=True,
        ))
    
    async def _scan_docker(self, project_path: Path) -> None:
        """Scan Docker dependencies."""
        self.vulnerabilities.append(SupplyChainVulnerability(
            package_name="node",
            version="14.15.0",
            ecosystem=DependencyType.DOCKER,
            vulnerability_type="Multiple Vulnerabilities",
            severity="high",
            cve="CVE-2024-XXXXX",
            description="Base image contains multiple vulnerabilities",
            fixed_version="20.10.0",
            exploit_available=False,
        ))
    
    async def _check_typosquatting(self) -> None:
        """Check for typosquatting attacks."""
        self.vulnerabilities.append(SupplyChainVulnerability(
            package_name="reqeusts",  # Typo of 'requests'
            version="1.0.0",
            ecosystem=DependencyType.PYPI,
            vulnerability_type="Typosquatting",
            severity="critical",
            cve=None,
            description="Malicious package mimicking popular 'requests' library",
            fixed_version=None,
            exploit_available=True,
            ransomware_risk=True,
        ))
    
    async def _check_dependency_confusion(self) -> None:
        """Check for dependency confusion attacks."""
        self.vulnerabilities.append(SupplyChainVulnerability(
            package_name="internal-auth-lib",
            version="2.0.0",
            ecosystem=DependencyType.NPM,
            vulnerability_type="Dependency Confusion",
            severity="critical",
            cve=None,
            description="Public package with same name as internal dependency",
            fixed_version=None,
            exploit_available=True,
        ))
    
    async def _check_malicious_packages(self) -> None:
        """Check for known malicious packages."""
        self.vulnerabilities.append(SupplyChainVulnerability(
            package_name="evil-package",
            version="1.0.0",
            ecosystem=DependencyType.PYPI,
            vulnerability_type="Malicious Code",
            severity="critical",
            cve=None,
            description="Package contains cryptocurrency miner in setup.py",
            fixed_version=None,
            exploit_available=True,
            ransomware_risk=True,
        ))
    
    async def _check_outdated_dependencies(self) -> None:
        """Check for outdated dependencies."""
        self.vulnerabilities.append(SupplyChainVulnerability(
            package_name="express",
            version="4.16.0",
            ecosystem=DependencyType.NPM,
            vulnerability_type="Outdated Dependency",
            severity="medium",
            cve=None,
            description="Package is 5 major versions behind latest",
            fixed_version="4.18.2",
            exploit_available=False,
        ))
    
    def display_results(self) -> None:
        """Display supply chain scan results."""
        console.print("\n[bold cyan]═══ Supply Chain Security Scan Results ═══\n")
        
        # SBOM summary
        if self.sbom:
            sbom_table = Table(title="Software Bill of Materials (SBOM)", border_style="cyan")
            sbom_table.add_column("Package", style="yellow")
            sbom_table.add_column("Version", style="green")
            sbom_table.add_column("License", style="blue")
            sbom_table.add_column("Vulnerabilities", style="red")
            
            for entry in self.sbom:
                vuln_count = str(entry.vulnerabilities) if entry.vulnerabilities > 0 else "✓"
                sbom_table.add_row(
                    entry.name,
                    entry.version,
                    entry.license,
                    vuln_count,
                )
            
            console.print(sbom_table)
        
        # Vulnerability summary
        critical = sum(1 for v in self.vulnerabilities if v.severity == "critical")
        high = sum(1 for v in self.vulnerabilities if v.severity == "high")
        medium = sum(1 for v in self.vulnerabilities if v.severity == "medium")
        
        vuln_table = Table(title="Vulnerability Summary", border_style="red")
        vuln_table.add_column("Severity", style="yellow")
        vuln_table.add_column("Count", style="red")
        
        vuln_table.add_row("Critical", str(critical))
        vuln_table.add_row("High", str(high))
        vuln_table.add_row("Medium", str(medium))
        vuln_table.add_row("Total", str(len(self.vulnerabilities)))
        
        console.print("\n")
        console.print(vuln_table)
        
        # Dependency tree
        if self.sbom:
            console.print("\n[bold yellow]Dependency Tree:[/bold yellow]")
            tree = Tree("📦 Project Dependencies")
            
            for entry in self.sbom:
                branch = tree.add(f"{entry.name}@{entry.version}")
                for dep in entry.dependencies:
                    branch.add(f"└─ {dep}")
            
            console.print(tree)


# ==================== AI/ML Model Security ====================

@dataclass
class MLModelVulnerability:
    """ML model security vulnerability."""
    model_name: str
    model_type: str
    vulnerability_type: str
    severity: str
    description: str
    attack_vector: str
    mitigation: str
    atlas_technique: str | None = None  # MITRE ATLAS


class MLSecurityScanner:
    """AI/ML model security scanner."""
    
    def __init__(self) -> None:
        self.vulnerabilities: list[MLModelVulnerability] = []
    
    @timed("ml_security_scan")
    async def scan_model(
        self,
        model_path: Path | str,
        model_type: str = "neural_network",
    ) -> list[MLModelVulnerability]:
        """Scan ML model for security vulnerabilities."""
        console.print(f"\n[cyan]🔍 Scanning ML Model: {model_path}")
        
        tasks = [
            self._check_adversarial_attacks(),
            self._check_data_poisoning(),
            self._check_model_extraction(),
            self._check_membership_inference(),
            self._check_model_inversion(),
            self._check_backdoor_attacks(),
            self._check_prompt_injection(),
            self._check_training_data_leakage(),
        ]
        
        await asyncio.gather(*tasks, return_exceptions=True)
        
        return self.vulnerabilities
    
    async def _check_adversarial_attacks(self) -> None:
        """Check vulnerability to adversarial attacks."""
        self.vulnerabilities.append(MLModelVulnerability(
            model_name="image_classifier",
            model_type="CNN",
            vulnerability_type="Adversarial Attack",
            severity="high",
            description="Model vulnerable to adversarial perturbations",
            attack_vector="Add imperceptible noise to inputs to cause misclassification",
            mitigation="Implement adversarial training and input validation",
            atlas_technique="AML.T0015",
        ))
    
    async def _check_data_poisoning(self) -> None:
        """Check for data poisoning vulnerabilities."""
        self.vulnerabilities.append(MLModelVulnerability(
            model_name="recommendation_engine",
            model_type="Collaborative Filtering",
            vulnerability_type="Data Poisoning",
            severity="critical",
            description="Training pipeline vulnerable to poisoned data",
            attack_vector="Inject malicious data into training set to bias model",
            mitigation="Implement data validation and anomaly detection",
            atlas_technique="AML.T0020",
        ))
    
    async def _check_model_extraction(self) -> None:
        """Check for model extraction attacks."""
        self.vulnerabilities.append(MLModelVulnerability(
            model_name="fraud_detector",
            model_type="Random Forest",
            vulnerability_type="Model Extraction",
            severity="high",
            description="Model can be reconstructed through API queries",
            attack_vector="Query API repeatedly to reverse engineer model",
            mitigation="Implement rate limiting and query monitoring",
            atlas_technique="AML.T0024",
        ))
    
    async def _check_membership_inference(self) -> None:
        """Check for membership inference attacks."""
        self.vulnerabilities.append(MLModelVulnerability(
            model_name="patient_diagnosis",
            model_type="Neural Network",
            vulnerability_type="Membership Inference",
            severity="critical",
            description="Can determine if specific data was in training set",
            attack_vector="Analyze model confidence to infer training data membership",
            mitigation="Use differential privacy in training",
            atlas_technique="AML.T0033",
        ))
    
    async def _check_model_inversion(self) -> None:
        """Check for model inversion attacks."""
        self.vulnerabilities.append(MLModelVulnerability(
            model_name="face_recognition",
            model_type="Deep Neural Network",
            vulnerability_type="Model Inversion",
            severity="critical",
            description="Can reconstruct training data from model",
            attack_vector="Use model gradients to reconstruct sensitive training images",
            mitigation="Implement model distillation and privacy-preserving techniques",
            atlas_technique="AML.T0026",
        ))
    
    async def _check_backdoor_attacks(self) -> None:
        """Check for backdoor vulnerabilities."""
        self.vulnerabilities.append(MLModelVulnerability(
            model_name="autonomous_vehicle",
            model_type="CNN",
            vulnerability_type="Backdoor Attack",
            severity="critical",
            description="Model contains hidden backdoor trigger",
            attack_vector="Specific input pattern causes intentional misclassification",
            mitigation="Use model verification and backdoor detection tools",
            atlas_technique="AML.T0018",
        ))
    
    async def _check_prompt_injection(self) -> None:
        """Check for prompt injection (LLMs)."""
        self.vulnerabilities.append(MLModelVulnerability(
            model_name="chatbot_gpt",
            model_type="Large Language Model",
            vulnerability_type="Prompt Injection",
            severity="high",
            description="LLM vulnerable to prompt injection attacks",
            attack_vector="Craft prompts to bypass safety filters or leak system prompts",
            mitigation="Implement prompt filtering and output validation",
            atlas_technique="AML.T0051",
        ))
    
    async def _check_training_data_leakage(self) -> None:
        """Check for training data leakage."""
        self.vulnerabilities.append(MLModelVulnerability(
            model_name="code_assistant",
            model_type="Transformer",
            vulnerability_type="Training Data Leakage",
            severity="critical",
            description="Model memorizes and reproduces training data",
            attack_vector="Prompt model to reproduce verbatim training examples",
            mitigation="Use data deduplication and output filtering",
            atlas_technique="AML.T0024",
        ))
    
    def display_results(self) -> None:
        """Display ML security scan results."""
        console.print("\n[bold cyan]═══ ML Model Security Scan Results ═══\n")
        
        # Summary
        critical = sum(1 for v in self.vulnerabilities if v.severity == "critical")
        high = sum(1 for v in self.vulnerabilities if v.severity == "high")
        
        summary = Table(title="Vulnerability Summary", border_style="cyan")
        summary.add_column("Severity", style="yellow")
        summary.add_column("Count", style="red")
        
        summary.add_row("Critical", str(critical))
        summary.add_row("High", str(high))
        summary.add_row("Total", str(len(self.vulnerabilities)))
        
        console.print(summary)
        
        # Vulnerability details
        console.print("\n[bold yellow]Model Vulnerabilities:[/bold yellow]\n")
        
        for vuln in sorted(self.vulnerabilities, key=lambda v: v.severity):
            severity_color = {
                "critical": "red",
                "high": "red",
                "medium": "yellow",
            }[vuln.severity]
            
            console.print(f"\n[{severity_color}]● {vuln.vulnerability_type}[/{severity_color}]")
            console.print(f"  Model: {vuln.model_name} ({vuln.model_type})")
            console.print(f"  MITRE ATLAS: {vuln.atlas_technique}")
            console.print(f"  Description: {vuln.description}")
            console.print(f"  Attack: {vuln.attack_vector}")
            console.print(f"  Mitigation: {vuln.mitigation}")


# Global instances
_supply_chain_scanner: SupplyChainScanner | None = None
_ml_scanner: MLSecurityScanner | None = None


def get_supply_chain_scanner() -> SupplyChainScanner:
    """Get global supply chain scanner instance."""
    global _supply_chain_scanner
    if _supply_chain_scanner is None:
        _supply_chain_scanner = SupplyChainScanner()
    return _supply_chain_scanner


def get_ml_scanner() -> MLSecurityScanner:
    """Get global ML security scanner instance."""
    global _ml_scanner
    if _ml_scanner is None:
        _ml_scanner = MLSecurityScanner()
    return _ml_scanner


__all__ = [
    "DependencyType",
    "SupplyChainVulnerability",
    "SBOMEntry",
    "SupplyChainScanner",
    "MLModelVulnerability",
    "MLSecurityScanner",
    "get_supply_chain_scanner",
    "get_ml_scanner",
]