# fsociety 4.0 Setup Guide

Complete guide for setting up fsociety with all features including AI and GPU acceleration.

## Table of Contents

- [Quick Start](#quick-start)
- [System Requirements](#system-requirements)
- [Installation Methods](#installation-methods)
- [Configuration](#configuration)
- [GPU Setup](#gpu-setup)
- [AI Features](#ai-features)
- [Development Setup](#development-setup)
- [Troubleshooting](#troubleshooting)

## Quick Start

### Minimal Installation

```bash
# Install with pip
pip install fsociety

# Run fsociety
fsociety
```

### With AI Features

```bash
# Install with AI support
pip install "fsociety[ai]"

# Configure AI
fsociety config --ai

# Run with AI enabled
fsociety --ai
```

## System Requirements

### Minimum Requirements

- **OS**: Linux, macOS, or Windows
- **Python**: 3.12 or higher
- **RAM**: 4GB minimum, 8GB recommended
- **Disk**: 2GB free space

### Recommended for AI Features

- **RAM**: 16GB+
- **GPU**: NVIDIA GPU with 6GB+ VRAM (for GPU acceleration)
- **Disk**: 10GB+ free space (for AI models)

### Supported Platforms

| Platform | Status | Notes |
|----------|--------|-------|
| Ubuntu 22.04+ | ✅ Fully Supported | Recommended |
| Debian 11+ | ✅ Fully Supported | |
| macOS 12+ | ✅ Fully Supported | GPU via Metal |
| Windows 10+ | ✅ Supported | Limited GPU support |
| Arch Linux | ✅ Supported | |

## Installation Methods

### 1. PyPI (Recommended)

```bash
# Standard installation
pip install fsociety

# With AI features
pip install "fsociety[ai]"

# With GPU support
pip install "fsociety[ai,gpu]"

# Complete installation (development)
pip install "fsociety[all]"
```

### 2. From Source

```bash
# Clone repository
git clone https://github.com/fsociety-team/fsociety.git
cd fsociety

# Install in development mode
pip install -e ".[all]"

# Install pre-commit hooks
pre-commit install
```

### 3. Docker

```bash
# CPU-only version
docker pull fsocietyteam/fsociety:latest
docker run -it fsocietyteam/fsociety

# GPU-accelerated version
docker pull fsocietyteam/fsociety:gpu
docker run --gpus all -it fsocietyteam/fsociety:gpu
```

### 4. Build from Source

```bash
# Install build dependencies
pip install build

# Build package
python -m build

# Install locally
pip install dist/fsociety-*.whl
```

## Configuration

### Basic Configuration

```bash
# Interactive configuration
fsociety config

# View current config
fsociety config --show

# Reset to defaults
fsociety config --reset
```

### Configuration File

Location: `~/.config/fsociety/config.json`

```json
{
  "version": "4.0.0",
  "platform": "linux",
  "ai": {
    "enabled": true,
    "model_provider": "local",
    "model_name": "mistral-7b",
    "use_gpu": true,
    "gpu_backend": "cuda"
  },
  "performance": {
    "max_workers": 8,
    "use_uvloop": true,
    "enable_caching": true,
    "cache_ttl": 3600,
    "use_gpu": true
  },
  "security": {
    "ssh_clone": true,
    "verify_ssl": true,
    "rate_limit": 100
  }
}
```

### Environment Variables

```bash
# AI Configuration
export FSOCIETY_AI_PROVIDER="openai"
export FSOCIETY_AI_API_KEY="your-api-key"
export FSOCIETY_AI_MODEL="gpt-4"

# Performance
export FSOCIETY_MAX_WORKERS="16"
export FSOCIETY_USE_GPU="true"

# Paths
export FSOCIETY_CONFIG_DIR="~/.config/fsociety"
export FSOCIETY_DATA_DIR="~/.local/share/fsociety"
```

## GPU Setup

### NVIDIA CUDA

#### Linux

```bash
# Install CUDA Toolkit 12.x
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-ubuntu2204.pin
sudo mv cuda-ubuntu2204.pin /etc/apt/preferences.d/cuda-repository-pin-600
sudo apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/3bf863cc.pub
sudo add-apt-repository "deb https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/ /"
sudo apt-get update
sudo apt-get -y install cuda

# Install PyTorch with CUDA
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121

# Verify installation
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
```

#### Windows

1. Download and install [CUDA Toolkit](https://developer.nvidia.com/cuda-downloads)
2. Install PyTorch with CUDA:

```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```

### AMD ROCm (Linux only)

```bash
# Add ROCm repository
wget -q -O - https://repo.radeon.com/rocm/rocm.gpg.key | sudo apt-key add -
echo 'deb [arch=amd64] https://repo.radeon.com/rocm/apt/5.7 ubuntu main' | sudo tee /etc/apt/sources.list.d/rocm.list

# Install ROCm
sudo apt update
sudo apt install rocm-hip-sdk

# Install PyTorch with ROCm
pip install torch torchvision --index-url https://download.pytorch.org/whl/rocm5.7
```

### Apple Silicon (Metal)

```bash
# PyTorch with Metal support (macOS 12.3+)
pip install torch torchvision

# Verify Metal support
python -c "import torch; print(f'MPS available: {torch.backends.mps.is_available()}')"
```

## AI Features

### Local Models

```bash
# Install with AI dependencies
pip install "fsociety[ai]"

# Configure for local models
fsociety config
# Select: AI Provider -> local
# Select: Model -> mistral-7b (or your preferred model)

# Models will be downloaded automatically on first use
# Location: ~/.cache/huggingface/
```

### OpenAI API

```bash
# Set API key
export FSOCIETY_AI_API_KEY="sk-..."

# Configure
fsociety config
# Select: AI Provider -> openai
# Select: Model -> gpt-4

# Or via command line
fsociety config --ai-provider openai --ai-model gpt-4
```

### Anthropic (Claude)

```bash
# Set API key
export FSOCIETY_AI_API_KEY="sk-ant-..."

# Configure
fsociety config --ai-provider anthropic --ai-model claude-3-opus-20240229
```

### Model Selection

| Model | Provider | Size | Speed | Quality | GPU Req |
|-------|----------|------|-------|---------|---------|
| Mistral-7B | Local | 7B | Fast | Good | 6GB |
| Llama-2-13B | Local | 13B | Medium | Better | 12GB |
| GPT-3.5 | OpenAI | - | Very Fast | Good | No |
| GPT-4 | OpenAI | - | Slow | Excellent | No |
| Claude 3 Opus | Anthropic | - | Medium | Excellent | No |

## Development Setup

### Prerequisites

```bash
# Install development dependencies
pip install "fsociety[dev]"

# Or individual tools
pip install pytest pytest-asyncio pytest-cov black ruff mypy
```

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/fsociety-team/fsociety.git
cd fsociety

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in editable mode
pip install -e ".[all]"

# Install pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# With coverage
pytest --cov=fsociety --cov-report=html

# Run specific test file
pytest tests/test_core.py

# Run with verbose output
pytest -v -s

# Run benchmarks
pytest --benchmark-only

# Run async tests only
pytest -k async
```

### Code Quality

```bash
# Format code
black fsociety tests

# Lint code
ruff check fsociety tests --fix

# Type check
mypy fsociety

# Run all checks
pre-commit run --all-files
```

### Building Documentation

```bash
# Install docs dependencies
pip install mkdocs mkdocs-material mkdocstrings[python]

# Serve locally
mkdocs serve

# Build static site
mkdocs build
```

## Troubleshooting

### Common Issues

#### Import Errors

```bash
# Ensure fsociety is installed
pip install --upgrade fsociety

# Check Python version
python --version  # Should be 3.12+

# Verify installation
python -c "import fsociety; print(fsociety.__version__)"
```

#### GPU Not Detected

```bash
# Check NVIDIA driver
nvidia-smi

# Verify PyTorch CUDA
python -c "import torch; print(torch.cuda.is_available())"

# Check CUDA version
nvcc --version

# Reinstall PyTorch with correct CUDA version
pip uninstall torch torchvision
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```

#### Performance Issues

```bash
# Enable caching
fsociety config --enable-caching

# Increase workers
fsociety config --max-workers 16

# Enable uvloop (Linux/macOS)
fsociety config --use-uvloop

# Check system resources
fsociety benchmark
```

#### AI Models Not Loading

```bash
# Check disk space
df -h

# Clear model cache
rm -rf ~/.cache/huggingface/

# Reinstall AI dependencies
pip install --upgrade "fsociety[ai]"

# Test with smaller model
fsociety config --ai-model mistral-7b
```

### Getting Help

- 📖 [Documentation](https://fsociety.dev/docs)
- 💬 [Discord Community](https://discord.gg/fsociety)
- 🐛 [Report Issues](https://github.com/fsociety-team/fsociety/issues)
- 📧 [Email Support](mailto:contact@fsociety.dev)

### Performance Tuning

```bash
# Benchmark current setup
fsociety benchmark

# Optimize for your system
fsociety config --optimize

# Monitor performance
fsociety --monitor
```

## Next Steps

1. **Complete Tutorial**: [Getting Started Guide](https://fsociety.dev/tutorial)
2. **Watch Videos**: [YouTube Channel](https://youtube.com/@fsociety)
3. **Join Community**: [Discord Server](https://discord.gg/fsociety)
4. **Contribute**: [Contributing Guide](CONTRIBUTING.md)

---

**Need Help?** Join our [Discord](https://discord.gg/fsociety) or open an [issue](https://github.com/fsociety-team/fsociety/issues)!