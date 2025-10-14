"""AI Engine with GPU acceleration for intelligent security analysis."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, AsyncIterator

from fsociety.console import console
from fsociety.core.config import get_config, GPUBackend


class AnalysisType(str, Enum):
    """Types of security analysis."""
    VULNERABILITY = "vulnerability"
    RECOMMENDATION = "recommendation"
    THREAT_DETECTION = "threat_detection"
    CODE_REVIEW = "code_review"
    EXPLOIT_SUGGESTION = "exploit_suggestion"


@dataclass
class AIResult:
    """AI analysis result."""
    analysis_type: AnalysisType
    confidence: float
    summary: str
    details: dict[str, Any]
    recommendations: list[str]
    severity: str  # low, medium, high, critical


class AIEngine:
    """High-performance AI engine for security analysis."""
    
    def __init__(self) -> None:
        self.config = get_config()
        self.device = self._setup_device()
        self.model = None
        self.tokenizer = None
        self.embedder = None
        self._initialized = False
    
    def _setup_device(self) -> str:
        """Setup computation device based on available hardware."""
        if not self.config.ai.use_gpu:
            return "cpu"
        
        match self.config.ai.gpu_backend:
            case GPUBackend.CUDA:
                try:
                    import torch
                    if torch.cuda.is_available():
                        device = f"cuda:0"
                        console.print(
                            f"[green]✓ GPU detected: {torch.cuda.get_device_name(0)}"
                        )
                        return device
                except ImportError:
                    pass
            
            case GPUBackend.METAL:
                try:
                    import torch
                    if torch.backends.mps.is_available():
                        console.print("[green]✓ Apple Silicon GPU detected")
                        return "mps"
                except ImportError:
                    pass
            
            case _:
                pass
        
        console.print("[yellow]⚠ GPU not available, using CPU")
        return "cpu"
    
    async def initialize(self) -> None:
        """Initialize AI models asynchronously."""
        if self._initialized:
            return
        
        console.print("[cyan]Initializing AI engine...")
        
        try:
            # Load LLM for analysis
            await self._load_llm()
            
            # Load embedder for similarity search
            await self._load_embedder()
            
            self._initialized = True
            console.print("[green]✓ AI engine initialized successfully")
            
        except Exception as e:
            console.print(f"[red]✗ Failed to initialize AI: {e}")
            console.print("[yellow]AI features will be disabled")
    
    async def _load_llm(self) -> None:
        """Load language model."""
        match self.config.ai.model_provider:
            case "local":
                await self._load_local_model()
            case "openai":
                await self._load_openai_client()
            case "anthropic":
                await self._load_anthropic_client()
            case _:
                raise ValueError(f"Unknown provider: {self.config.ai.model_provider}")
    
    async def _load_local_model(self) -> None:
        """Load local transformer model."""
        from transformers import AutoModelForCausalLM, AutoTokenizer
        import torch
        
        model_name = self.config.ai.model_name
        
        # Load in separate thread to avoid blocking
        self.tokenizer = await asyncio.to_thread(
            AutoTokenizer.from_pretrained, model_name
        )
        
        self.model = await asyncio.to_thread(
            AutoModelForCausalLM.from_pretrained,
            model_name,
            torch_dtype=torch.float16 if self.device != "cpu" else torch.float32,
            device_map=self.device if self.device != "cpu" else None,
        )
        
        if self.device == "cpu":
            self.model = self.model.to(self.device)
    
    async def _load_openai_client(self) -> None:
        """Setup OpenAI client."""
        from openai import AsyncOpenAI
        
        if not self.config.ai.api_key:
            raise ValueError("OpenAI API key not configured")
        
        self.model = AsyncOpenAI(api_key=self.config.ai.api_key)
    
    async def _load_anthropic_client(self) -> None:
        """Setup Anthropic client."""
        from anthropic import AsyncAnthropic
        
        if not self.config.ai.api_key:
            raise ValueError("Anthropic API key not configured")
        
        self.model = AsyncAnthropic(api_key=self.config.ai.api_key)
    
    async def _load_embedder(self) -> None:
        """Load sentence embedding model."""
        from sentence_transformers import SentenceTransformer
        
        self.embedder = await asyncio.to_thread(
            SentenceTransformer,
            self.config.ai.embedding_model,
            device=self.device,
        )
    
    async def analyze_vulnerability(
        self,
        target: str,
        scan_results: dict[str, Any],
    ) -> AIResult:
        """Analyze scan results for vulnerabilities."""
        if not self._initialized:
            await self.initialize()
        
        prompt = self._build_vulnerability_prompt(target, scan_results)
        response = await self._generate(prompt)
        
        return self._parse_vulnerability_response(response)
    
    async def suggest_exploits(
        self,
        vulnerability: str,
        target_info: dict[str, Any],
    ) -> AIResult:
        """Suggest potential exploits for identified vulnerabilities."""
        if not self._initialized:
            await self.initialize()
        
        prompt = f"""
        Analyze the following vulnerability and suggest potential exploitation methods:
        
        Vulnerability: {vulnerability}
        Target Info: {target_info}
        
        Provide:
        1. Exploitation difficulty (1-10)
        2. Required tools and techniques
        3. Step-by-step exploitation guide
        4. Potential countermeasures
        
        Format response as JSON.
        """
        
        response = await self._generate(prompt)
        return self._parse_exploit_response(response)
    
    async def code_review(
        self,
        code: str,
        language: str = "python",
    ) -> AIResult:
        """Perform AI-powered security code review."""
        if not self._initialized:
            await self.initialize()
        
        prompt = f"""
        Perform a security code review of this {language} code:
        
        ```{language}
        {code}
        ```
        
        Identify:
        1. Security vulnerabilities
        2. Best practice violations
        3. Potential attack vectors
        4. Recommended fixes
        
        Prioritize findings by severity.
        """
        
        response = await self._generate(prompt)
        return self._parse_code_review_response(response)
    
    async def threat_detection(
        self,
        network_data: dict[str, Any],
    ) -> AIResult:
        """Detect potential threats in network data."""
        if not self._initialized:
            await self.initialize()
        
        # Use embeddings for anomaly detection
        embeddings = await self._create_embeddings(str(network_data))
        
        # Compare with known threat patterns
        threats = await self._find_similar_threats(embeddings)
        
        return AIResult(
            analysis_type=AnalysisType.THREAT_DETECTION,
            confidence=0.85,
            summary="Threat analysis completed",
            details={"threats": threats},
            recommendations=["Monitor suspicious activity", "Update firewall rules"],
            severity="medium",
        )
    
    async def _generate(self, prompt: str) -> str:
        """Generate AI response based on configured provider."""
        match self.config.ai.model_provider:
            case "local":
                return await self._generate_local(prompt)
            case "openai":
                return await self._generate_openai(prompt)
            case "anthropic":
                return await self._generate_anthropic(prompt)
            case _:
                raise ValueError("Invalid AI provider")
    
    async def _generate_local(self, prompt: str) -> str:
        """Generate using local model."""
        import torch
        
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        
        with torch.no_grad():
            outputs = await asyncio.to_thread(
                self.model.generate,
                **inputs,
                max_new_tokens=self.config.ai.max_tokens,
                temperature=self.config.ai.temperature,
                do_sample=True,
            )
        
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return response[len(prompt):]  # Remove prompt from response
    
    async def _generate_openai(self, prompt: str) -> str:
        """Generate using OpenAI API."""
        response = await self.model.chat.completions.create(
            model=self.config.ai.model_name,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=self.config.ai.max_tokens,
            temperature=self.config.ai.temperature,
        )
        return response.choices[0].message.content
    
    async def _generate_anthropic(self, prompt: str) -> str:
        """Generate using Anthropic API."""
        response = await self.model.messages.create(
            model=self.config.ai.model_name,
            max_tokens=self.config.ai.max_tokens,
            temperature=self.config.ai.temperature,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text
    
    async def _create_embeddings(self, text: str | list[str]) -> Any:
        """Create embeddings for similarity search."""
        if isinstance(text, str):
            text = [text]
        
        return await asyncio.to_thread(self.embedder.encode, text)
    
    async def _find_similar_threats(self, embeddings: Any) -> list[dict[str, Any]]:
        """Find similar threat patterns using vector similarity."""
        # Placeholder - would use FAISS or ChromaDB for actual implementation
        return []
    
    def _build_vulnerability_prompt(
        self,
        target: str,
        scan_results: dict[str, Any],
    ) -> str:
        """Build prompt for vulnerability analysis."""
        return f"""
        Analyze the following security scan results for target: {target}
        
        Scan Results:
        {scan_results}
        
        Provide:
        1. Identified vulnerabilities (with CVE if applicable)
        2. Severity assessment (critical/high/medium/low)
        3. Exploitation likelihood
        4. Recommended remediation steps
        
        Format response as structured JSON.
        """
    
    def _parse_vulnerability_response(self, response: str) -> AIResult:
        """Parse vulnerability analysis response."""
        # Simplified parser - real implementation would parse JSON
        return AIResult(
            analysis_type=AnalysisType.VULNERABILITY,
            confidence=0.9,
            summary="Vulnerability analysis completed",
            details={"raw_response": response},
            recommendations=["Apply security patches", "Update configurations"],
            severity="high",
        )
    
    def _parse_exploit_response(self, response: str) -> AIResult:
        """Parse exploit suggestion response."""
        return AIResult(
            analysis_type=AnalysisType.EXPLOIT_SUGGESTION,
            confidence=0.85,
            summary="Exploit analysis completed",
            details={"raw_response": response},
            recommendations=["Use with caution", "Obtain proper authorization"],
            severity="high",
        )
    
    def _parse_code_review_response(self, response: str) -> AIResult:
        """Parse code review response."""
        return AIResult(
            analysis_type=AnalysisType.CODE_REVIEW,
            confidence=0.88,
            summary="Code review completed",
            details={"raw_response": response},
            recommendations=["Fix identified issues", "Add security tests"],
            severity="medium",
        )


# Global AI engine instance
_ai_engine: AIEngine | None = None


def get_ai_engine() -> AIEngine:
    """Get the global AI engine instance."""
    global _ai_engine
    if _ai_engine is None:
        _ai_engine = AIEngine()
    return _ai_engine