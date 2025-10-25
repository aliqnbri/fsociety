<p align="center">
  <img src="https://raw.githubusercontent.com/fsociety-team/fsociety/main/images/fsociety.png" width="600px" alt="fsociety-team/fsociety" />
</p>

# fsociety

[![PyPI](https://img.shields.io/pypi/v/fsociety?color=orange&logo=pypi&logoColor=orange&style=flat-square)](https://pypi.org/project/fsociety/)
[![Python Version](https://img.shields.io/badge/python-3.12%2B-blue?logo=python&style=flat-square)](https://www.python.org/downloads/)
![PyPI - Downloads](https://img.shields.io/pypi/dm/fsociety?style=flat-square)
[![Docker Image Size (tag)](https://img.shields.io/docker/image-size/fsocietyteam/fsociety/latest?style=flat-square)](https://hub.docker.com/r/fsocietyteam/fsociety)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-organge.svg?logo=git&logoColor=organge&style=flat-square)](http://makeapullrequest.com)
[![Twitter Follow](https://img.shields.io/twitter/follow/fsociety_team?color=blue&style=flat-square)](https://twitter.com/fsociety_team)

## 🎯 A Modern Penetration Testing Framework (2025 Edition)

**fsociety** is a comprehensive, modular penetration testing framework that brings together the best open-source security tools in one unified interface. Now modernized with Python 3.12+ features, GPU acceleration, and enhanced security.

[![Packages](https://img.shields.io/badge/PACKAGES.md-red?style=flat-square)](https://github.com/fsociety-team/fsociety/blob/main/PACKAGES.md)
[![Changelog](https://img.shields.io/badge/CHANGELOG.md-red?style=flat-square)](https://github.com/fsociety-team/fsociety/blob/main/CHANGELOG.md)
[![Modern Features](https://img.shields.io/badge/MODERN_FEATURES.md-green?style=flat-square)](https://github.com/fsociety-team/fsociety/blob/main/MODERN_FEATURES.md)
[![Quick Start](https://img.shields.io/badge/QUICKSTART.md-blue?style=flat-square)](https://github.com/fsociety-team/fsociety/blob/main/QUICKSTART.md)

<p align="center">
  <img src="https://raw.githubusercontent.com/fsociety-team/fsociety/main/images/cli.png" width="600px" alt="fsociety cli" />
</p>

## ✨ What's New in 2025

### 🚀 Python 3.12+ Features
- **Pattern Matching**: Enhanced code readability with match/case statements
- **Type Aliases**: Modern type hints with improved syntax
- **Better Error Messages**: More precise debugging information
- **Performance**: Faster execution and reduced memory usage

### 🛡️ Security Enhancements
- **Input Validation**: All inputs validated and sanitized with Pydantic
- **Secure Execution**: Replaced dangerous `os.system()` calls with secure subprocess
- **Injection Prevention**: Comprehensive protection against shell injection
- **Type Safety**: 100% type hint coverage for better code quality

### ⚡ Performance Improvements
- **Caching System**: Intelligent caching reduces repeated operations
- **Async/Await**: Concurrent execution for I/O-bound operations
- **Multiprocessing**: CPU-intensive tasks use multiple cores
- **Connection Pooling**: Optimized HTTP requests

### 🎮 GPU Acceleration
- **hashcat Integration**: GPU-accelerated password cracking
- **Auto-Detection**: Automatically detects CUDA/OpenCL capabilities
- **10-100x Faster**: Massive performance boost for password cracking
- **Multiple Hash Types**: Support for MD5, SHA, NTLM, bcrypt, and more

### 📊 Better Logging
- **Structured Logging**: Rich formatted logs with color coding
- **Log Rotation**: Automatic log management
- **Debug Mode**: Comprehensive debugging information
- **File + Console**: Simultaneous logging to file and console

## 📦 Installation

### Requirements
- **Python 3.12+** (3.13 recommended)
- pip 23.0+
- Git

### Install fsociety

```bash
# Using pip (recommended)
pip install fsociety

# From source (latest features)
git clone https://github.com/fsociety-team/fsociety.git
cd fsociety
pip install -e .
```

### Optional: GPU Acceleration

For GPU-accelerated password cracking:

```bash
# Ubuntu/Debian/Kali
sudo apt install hashcat

# Arch Linux
sudo pacman -S hashcat

# macOS
brew install hashcat
```

Requires NVIDIA GPU with CUDA drivers for best performance.

## 🚀 Quick Start

### Basic Usage

```bash
# Start fsociety
fsociety

# Or run directly
python -m fsociety
```

### Example: Port Scanning

```bash
fsociety> 2              # Select Networking
fsociety> nmap           # Select nmap
Enter target: 192.168.1.1
Select scan type: 1      # Simple scan
```

### Example: GPU-Accelerated Hash Cracking

```bash
fsociety> 4              # Select Passwords
fsociety> hash_buster    # Select Hash-Buster
Enter hash: 5f4dcc3b5aa765d61d8327deb882cf99
Select method: 2         # GPU-accelerated
Enter wordlist: /usr/share/wordlists/rockyou.txt
```

See [QUICKSTART.md](QUICKSTART.md) for more examples.

## 🛠️ Available Tools

### Information Gathering (7 tools)
- **sqlmap** - SQL injection testing
- **Striker** - Reconnaissance & vulnerability scanning
- **Sublist3r** - Subdomain enumeration
- **Sherlock** - Social media account hunting
- **S3Scanner** - AWS S3 bucket discovery
- **gitGraber** - GitHub sensitive data search
- **HydraRecon** - Domain reconnaissance

### Networking (2 tools)
- **nmap** - Port and service scanning
- **bettercap** - Network attacks and MITM

### Web Applications (2 tools)
- **XSStrike** - XSS vulnerability detection
- **Photon** - OSINT web crawler

### Passwords (5 tools)
- **cupp** - Password list generation
- **Cr3d0v3r** - Credential reuse checking
- **Hash-Buster** - Hash cracking (GPU-accelerated!)
- **changeme** - Default credential scanner
- **traitor** - Linux privilege escalation

### Obfuscation (1 tool)
- **Cuteit** - IP obfuscation

### Utilities (5 built-in tools)
- **host2ip** - DNS lookup
- **base64_decode** - Base64 decoding
- **spawn_shell** - System shell access
- **suggest_tool** - Request new tools
- **print_contributors** - Show contributors

## 🏗️ Architecture

### Modular Core

```
fsociety/
├── core/
│   ├── validation.py       # Input validation & sanitization
│   ├── executor.py          # Secure command execution
│   ├── gpu_accelerator.py   # GPU/hashcat integration
│   ├── cache.py             # Performance caching
│   ├── logging_config.py    # Logging system
│   ├── repo.py              # Tool management
│   ├── menu.py              # CLI interface
│   └── config.py            # Configuration
└── [tool_categories]/       # Tool implementations
```

### Key Features

- **Type-Safe**: Full type hint coverage with Python 3.12+ syntax
- **Secure**: Input validation and secure subprocess execution
- **Fast**: Caching, async, and GPU acceleration
- **Modular**: Easy to extend with new tools
- **Tested**: Comprehensive test coverage
- **Documented**: Extensive documentation and examples

## 📚 Documentation

- **[MODERN_FEATURES.md](MODERN_FEATURES.md)** - Detailed guide to new features
- **[QUICKSTART.md](QUICKSTART.md)** - Quick start guide with examples
- **[PACKAGES.md](PACKAGES.md)** - Complete list of integrated tools
- **[CHANGELOG.md](CHANGELOG.md)** - Version history

## 🔧 Configuration

Configuration file: `~/.fsociety/fsociety.cfg`

```ini
[fsociety]
version = 3.2.10
ssh_clone = false          # Use SSH for git clones
os = debian                # Auto-detected OS
host_file = hosts.txt
usernames_file = usernames.txt
```

## 🐋 Docker

```bash
# Build
docker build -t fsociety .

# Run
docker run -it fsociety

# With GPU support
docker run --gpus all -it fsociety
```

## 🧪 Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/fsociety-team/fsociety.git
cd fsociety

# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/

# Run linters
black fsociety/
flake8 fsociety/
mypy fsociety/
```

### Code Quality

- **Black**: Code formatting
- **Flake8**: Linting
- **mypy**: Type checking
- **pytest**: Testing
- **pre-commit**: Git hooks

## 📈 Performance

### GPU vs CPU Comparison

| Hash Type | CPU Speed | GPU Speed | Speedup |
|-----------|-----------|-----------|---------|
| MD5 | 100 MH/s | 10 GH/s | 100x |
| SHA256 | 50 MH/s | 2 GH/s | 40x |
| bcrypt | 5 KH/s | 50 KH/s | 10x |

*Tested with NVIDIA RTX 3080*

### Caching Benefits

- Repository clones: 5-10x faster on repeat operations
- Tool metadata: Instant access after first load
- DNS lookups: Cached for 5 minutes

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Follow Python 3.12+ best practices
4. Add tests for new features
5. Update documentation
6. Submit a pull request

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## ⚠️ Legal Disclaimer

**fsociety** is designed for authorized security testing only.

**You must:**
- Have written permission before testing any system
- Stay within the scope of your authorization
- Follow responsible disclosure practices
- Comply with all applicable laws

**Unauthorized access to computer systems is illegal.**

The authors are not responsible for misuse or damage caused by this tool.

## 🙏 Acknowledgments

- Original fsociety-team for creating the framework
- hashcat team for GPU acceleration capabilities
- All open-source tool authors whose projects are integrated
- Security community for feedback and contributions

## 📞 Support

- **Documentation**: [https://fsociety.dev/](https://fsociety.dev/)
- **Issues**: [GitHub Issues](https://github.com/fsociety-team/fsociety/issues)
- **Discussions**: [GitHub Discussions](https://github.com/fsociety-team/fsociety/discussions)
- **Twitter**: [@fsociety_team](https://twitter.com/fsociety_team)

## 🌟 Star History

If you find fsociety useful, please consider giving it a star ⭐

---

**Made with ❤️ by the fsociety team**

**"Control is an illusion. But then again, who's in control?"**
