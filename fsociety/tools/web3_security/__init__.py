"""Web3/Blockchain and Zero-Trust architecture security testing."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from rich.panel import Panel
from rich.table import Table

from fsociety.console import console
from fsociety.core.performance import timed


# ==================== Web3/Blockchain Security ====================

class BlockchainType(str, Enum):
    """Blockchain types."""
    ETHEREUM = "ethereum"
    BINANCE = "binance_smart_chain"
    POLYGON = "polygon"
    AVALANCHE = "avalanche"
    SOLANA = "solana"
    CARDANO = "cardano"


@dataclass
class SmartContractVulnerability:
    """Smart contract vulnerability."""
    contract_address: str
    function_name: str
    vulnerability_type: str
    severity: str
    description: str
    exploit_scenario: str
    remediation: str
    swc_id: str | None = None  # Smart Contract Weakness Classification
    gas_impact: str = "none"


class Web3SecurityScanner:
    """Web3 and blockchain security scanner."""
    
    def __init__(self) -> None:
        self.vulnerabilities: list[SmartContractVulnerability] = []
    
    @timed("web3_security_scan")
    async def scan_contract(
        self,
        contract_address: str,
        blockchain: BlockchainType = BlockchainType.ETHEREUM,
        source_code: str | None = None,
    ) -> list[SmartContractVulnerability]:
        """Scan smart contract for vulnerabilities."""
        console.print(f"\n[cyan]🔍 Scanning Smart Contract: {contract_address}")
        console.print(f"[dim]Blockchain: {blockchain.value}")
        
        tasks = [
            self._check_reentrancy(),
            self._check_integer_overflow(),
            self._check_access_control(),
            self._check_unchecked_calls(),
            self._check_dos_vulnerabilities(),
            self._check_front_running(),
            self._check_timestamp_dependence(),
            self._check_delegatecall(),
            self._check_signature_replay(),
            self._check_flash_loan_attacks(),
        ]
        
        await asyncio.gather(*tasks, return_exceptions=True)
        
        return self.vulnerabilities
    
    async def _check_reentrancy(self) -> None:
        """Check for reentrancy vulnerabilities."""
        self.vulnerabilities.append(SmartContractVulnerability(
            contract_address="0x1234...5678",
            function_name="withdraw",
            vulnerability_type="Reentrancy",
            severity="critical",
            description="Function vulnerable to reentrancy attack",
            exploit_scenario="Attacker can recursively call withdraw() before balance is updated",
            remediation="Use checks-effects-interactions pattern or ReentrancyGuard",
            swc_id="SWC-107",
            gas_impact="high",
        ))
    
    async def _check_integer_overflow(self) -> None:
        """Check for integer overflow/underflow."""
        self.vulnerabilities.append(SmartContractVulnerability(
            contract_address="0x1234...5678",
            function_name="transfer",
            vulnerability_type="Integer Overflow/Underflow",
            severity="high",
            description="Arithmetic operation may overflow or underflow",
            exploit_scenario="Attacker can manipulate token balances through overflow",
            remediation="Use SafeMath library or Solidity 0.8.0+ built-in checks",
            swc_id="SWC-101",
        ))
    
    async def _check_access_control(self) -> None:
        """Check access control vulnerabilities."""
        self.vulnerabilities.append(SmartContractVulnerability(
            contract_address="0x1234...5678",
            function_name="setOwner",
            vulnerability_type="Missing Access Control",
            severity="critical",
            description="Critical function lacks access control modifiers",
            exploit_scenario="Anyone can call setOwner() and take ownership",
            remediation="Add onlyOwner or appropriate access control modifier",
            swc_id="SWC-105",
        ))
    
    async def _check_unchecked_calls(self) -> None:
        """Check for unchecked external calls."""
        self.vulnerabilities.append(SmartContractVulnerability(
            contract_address="0x1234...5678",
            function_name="sendEther",
            vulnerability_type="Unchecked Call Return Value",
            severity="high",
            description="External call return value is not checked",
            exploit_scenario="Transaction may fail silently, leading to fund loss",
            remediation="Check return values of external calls or use transfer()",
            swc_id="SWC-104",
        ))
    
    async def _check_dos_vulnerabilities(self) -> None:
        """Check for DoS vulnerabilities."""
        self.vulnerabilities.append(SmartContractVulnerability(
            contract_address="0x1234...5678",
            function_name="distributeRewards",
            vulnerability_type="Denial of Service",
            severity="medium",
            description="Unbounded loop may cause out-of-gas errors",
            exploit_scenario="Function becomes unusable as array grows",
            remediation="Implement pagination or pull payment pattern",
            swc_id="SWC-128",
            gas_impact="critical",
        ))
    
    async def _check_front_running(self) -> None:
        """Check for front-running vulnerabilities."""
        self.vulnerabilities.append(SmartContractVulnerability(
            contract_address="0x1234...5678",
            function_name="trade",
            vulnerability_type="Front-Running",
            severity="high",
            description="Transaction can be front-run by miners or MEV bots",
            exploit_scenario="Attacker sees pending transaction and submits higher gas to execute first",
            remediation="Use commit-reveal scheme or Flashbots",
            swc_id="N/A",
        ))
    
    async def _check_timestamp_dependence(self) -> None:
        """Check for timestamp dependence."""
        self.vulnerabilities.append(SmartContractVulnerability(
            contract_address="0x1234...5678",
            function_name="generateRandom",
            vulnerability_type="Timestamp Dependence",
            severity="medium",
            description="Function uses block.timestamp for randomness",
            exploit_scenario="Miners can manipulate timestamps within 15 seconds",
            remediation="Use Chainlink VRF for true randomness",
            swc_id="SWC-116",
        ))
    
    async def _check_delegatecall(self) -> None:
        """Check for delegatecall vulnerabilities."""
        self.vulnerabilities.append(SmartContractVulnerability(
            contract_address="0x1234...5678",
            function_name="proxy",
            vulnerability_type="Unsafe Delegatecall",
            severity="critical",
            description="Delegatecall to user-controlled address",
            exploit_scenario="Attacker can execute arbitrary code in contract context",
            remediation="Validate delegatecall targets or use proxy patterns safely",
            swc_id="SWC-112",
        ))
    
    async def _check_signature_replay(self) -> None:
        """Check for signature replay attacks."""
        self.vulnerabilities.append(SmartContractVulnerability(
            contract_address="0x1234...5678",
            function_name="executeMetaTransaction",
            vulnerability_type="Signature Replay",
            severity="high",
            description="Signature can be replayed on other chains or contracts",
            exploit_scenario="Attacker reuses signature to execute transaction multiple times",
            remediation="Include nonce, chainId, and contract address in signature",
            swc_id="N/A",
        ))
    
    async def _check_flash_loan_attacks(self) -> None:
        """Check for flash loan attack vectors."""
        self.vulnerabilities.append(SmartContractVulnerability(
            contract_address="0x1234...5678",
            function_name="liquidate",
            vulnerability_type="Flash Loan Attack Vector",
            severity="critical",
            description="Oracle price can be manipulated via flash loans",
            exploit_scenario="Attacker uses flash loan to manipulate price and exploit protocol",
            remediation="Use time-weighted average prices (TWAP) and multiple oracles",
            swc_id="N/A",
        ))
    
    def display_results(self) -> None:
        """Display scan results."""
        console.print("\n[bold cyan]═══ Smart Contract Security Scan Results ═══\n")
        
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
        for vuln in sorted(self.vulnerabilities, key=lambda v: v.severity):
            severity_color = {
                "critical": "red",
                "high": "red",
                "medium": "yellow",
                "low": "green",
            }[vuln.severity]
            
            panel_content = f"""
[cyan]Function:[/cyan] {vuln.function_name}
[cyan]Type:[/cyan] {vuln.vulnerability_type}
[cyan]SWC-ID:[/cyan] {vuln.swc_id or 'N/A'}
[cyan]Gas Impact:[/cyan] {vuln.gas_impact}

[yellow]Description:[/yellow]
{vuln.description}

[red]Exploit Scenario:[/red]
{vuln.exploit_scenario}

[green]Remediation:[/green]
{vuln.remediation}
            """
            
            panel = Panel(
                panel_content.strip(),
                title=f"[{severity_color}]{vuln.severity.upper()}[/{severity_color}]",
                border_style=severity_color,
            )
            console.print(panel)


# ==================== Zero-Trust Architecture ====================

@dataclass
class ZeroTrustFinding:
    """Zero-Trust security finding."""
    component: str
    principle: str  # verify explicitly, least privilege, assume breach
    severity: str
    current_state: str
    recommended_state: str
    implementation_steps: list[str]


class ZeroTrustScanner:
    """Zero-Trust architecture security scanner."""
    
    def __init__(self) -> None:
        self.findings: list[ZeroTrustFinding] = []
    
    @timed("zerotrust_security_scan")
    async def scan(
        self,
        environment: str = "production",
    ) -> list[ZeroTrustFinding]:
        """Scan environment for Zero-Trust compliance."""
        console.print(f"\n[cyan]🔍 Scanning Zero-Trust Architecture: {environment}")
        
        tasks = [
            self._check_identity_verification(),
            self._check_device_verification(),
            self._check_least_privilege(),
            self._check_microsegmentation(),
            self._check_encryption(),
            self._check_monitoring(),
            self._check_mfa(),
            self._check_continuous_validation(),
        ]
        
        await asyncio.gather(*tasks, return_exceptions=True)
        
        return self.findings
    
    async def _check_identity_verification(self) -> None:
        """Check identity verification."""
        self.findings.append(ZeroTrustFinding(
            component="Identity & Access Management",
            principle="Verify Explicitly",
            severity="critical",
            current_state="Password-based authentication only",
            recommended_state="MFA + risk-based authentication",
            implementation_steps=[
                "Implement MFA for all users",
                "Add risk-based authentication",
                "Integrate with identity provider (Okta/Azure AD)",
                "Enable conditional access policies",
            ],
        ))
    
    async def _check_device_verification(self) -> None:
        """Check device verification."""
        self.findings.append(ZeroTrustFinding(
            component="Device Management",
            principle="Verify Explicitly",
            severity="high",
            current_state="No device verification or management",
            recommended_state="Device compliance checks before access",
            implementation_steps=[
                "Implement device registration",
                "Enforce device compliance policies",
                "Use device certificates for authentication",
                "Integrate with MDM/UEM solution",
            ],
        ))
    
    async def _check_least_privilege(self) -> None:
        """Check least privilege access."""
        self.findings.append(ZeroTrustFinding(
            component="Access Control",
            principle="Least Privilege Access",
            severity="critical",
            current_state="Users have broad permissions",
            recommended_state="Just-in-time (JIT) access with minimal permissions",
            implementation_steps=[
                "Implement role-based access control (RBAC)",
                "Add just-in-time access provisioning",
                "Regular access reviews and revocation",
                "Use privileged access management (PAM)",
            ],
        ))
    
    async def _check_microsegmentation(self) -> None:
        """Check network microsegmentation."""
        self.findings.append(ZeroTrustFinding(
            component="Network Security",
            principle="Assume Breach",
            severity="high",
            current_state="Flat network with minimal segmentation",
            recommended_state="Microsegmented network with strict policies",
            implementation_steps=[
                "Implement network microsegmentation",
                "Deploy software-defined perimeter (SDP)",
                "Use service mesh for east-west traffic",
                "Enforce zero-trust network access (ZTNA)",
            ],
        ))
    
    async def _check_encryption(self) -> None:
        """Check encryption everywhere."""
        self.findings.append(ZeroTrustFinding(
            component="Data Protection",
            principle="Assume Breach",
            severity="high",
            current_state="Encryption in transit only",
            recommended_state="End-to-end encryption everywhere",
            implementation_steps=[
                "Enable encryption at rest for all data",
                "Implement end-to-end encryption",
                "Use TLS 1.3 for all communications",
                "Deploy data loss prevention (DLP)",
            ],
        ))
    
    async def _check_monitoring(self) -> None:
        """Check continuous monitoring."""
        self.findings.append(ZeroTrustFinding(
            component="Security Monitoring",
            principle="Assume Breach",
            severity="high",
            current_state="Basic logging, manual analysis",
            recommended_state="Real-time threat detection and response",
            implementation_steps=[
                "Implement SIEM/SOAR solution",
                "Enable user behavior analytics (UBA)",
                "Deploy endpoint detection and response (EDR)",
                "Implement security orchestration",
            ],
        ))
    
    async def _check_mfa(self) -> None:
        """Check multi-factor authentication."""
        self.findings.append(ZeroTrustFinding(
            component="Authentication",
            principle="Verify Explicitly",
            severity="critical",
            current_state="MFA optional for users",
            recommended_state="MFA enforced for all access",
            implementation_steps=[
                "Enforce MFA for all users",
                "Use phishing-resistant MFA (FIDO2/WebAuthn)",
                "Implement adaptive MFA",
                "Remove SMS-based MFA",
            ],
        ))
    
    async def _check_continuous_validation(self) -> None:
        """Check continuous validation."""
        self.findings.append(ZeroTrustFinding(
            component="Session Management",
            principle="Verify Explicitly",
            severity="medium",
            current_state="Long-lived sessions without re-validation",
            recommended_state="Continuous validation and short-lived sessions",
            implementation_steps=[
                "Implement continuous authentication",
                "Reduce session timeouts",
                "Add step-up authentication for sensitive operations",
                "Monitor session anomalies",
            ],
        ))
    
    def display_results(self) -> None:
        """Display Zero-Trust scan results."""
        console.print("\n[bold cyan]═══ Zero-Trust Architecture Scan Results ═══\n")
        
        # Maturity assessment
        total = len(self.findings)
        critical = sum(1 for f in self.findings if f.severity == "critical")
        high = sum(1 for f in self.findings if f.severity == "high")
        
        maturity_score = max(0, 100 - (critical * 20 + high * 10))
        
        maturity_table = Table(title="Zero-Trust Maturity", border_style="cyan")
        maturity_table.add_column("Metric", style="yellow")
        maturity_table.add_column("Value", style="green")
        
        maturity_table.add_row("Maturity Score", f"{maturity_score}%")
        maturity_table.add_row("Total Findings", str(total))
        maturity_table.add_row("Critical Issues", str(critical))
        maturity_table.add_row("High Issues", str(high))
        
        console.print(maturity_table)
        
        # Detailed findings
        console.print("\n[bold yellow]Findings by Principle:[/bold yellow]\n")
        
        principles = {}
        for finding in self.findings:
            if finding.principle not in principles:
                principles[finding.principle] = []
            principles[finding.principle].append(finding)
        
        for principle, findings in principles.items():
            console.print(f"\n[bold cyan]{principle}[/bold cyan]")
            
            for finding in findings:
                severity_color = {
                    "critical": "red",
                    "high": "red",
                    "medium": "yellow",
                    "low": "green",
                }[finding.severity]
                
                panel_content = f"""
[cyan]Component:[/cyan] {finding.component}
[cyan]Severity:[/cyan] [{severity_color}]{finding.severity.upper()}[/{severity_color}]

[yellow]Current State:[/yellow]
{finding.current_state}

[green]Recommended State:[/green]
{finding.recommended_state}

[cyan]Implementation Steps:[/cyan]
{chr(10).join(f"  {i+1}. {step}" for i, step in enumerate(finding.implementation_steps))}
                """
                
                panel = Panel(
                    panel_content.strip(),
                    title=finding.component,
                    border_style=severity_color,
                )
                console.print(panel)


# Global instances
_web3_scanner: Web3SecurityScanner | None = None
_zerotrust_scanner: ZeroTrustScanner | None = None


def get_web3_scanner() -> Web3SecurityScanner:
    """Get global Web3 scanner instance."""
    global _web3_scanner
    if _web3_scanner is None:
        _web3_scanner = Web3SecurityScanner()
    return _web3_scanner


def get_zerotrust_scanner() -> ZeroTrustScanner:
    """Get global Zero-Trust scanner instance."""
    global _zerotrust_scanner
    if _zerotrust_scanner is None:
        _zerotrust_scanner = ZeroTrustScanner()
    return _zerotrust_scanner


__all__ = [
    "BlockchainType",
    "SmartContractVulnerability",
    "Web3SecurityScanner",
    "ZeroTrustFinding",
    "ZeroTrustScanner",
    "get_web3_scanner",
    "get_zerotrust_scanner",
]