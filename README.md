<p align="center">
  <img src="https://raw.githubusercontent.com/fsociety-team/fsociety/main/images/fsociety.png" width="600px" alt="fsociety-team/fsociety" />
</p>

# fsociety

[![PyPI](https://img.shields.io/pypi/v/fsociety?color=orange&logo=pypi&logoColor=orange&style=flat-square)](https://pypi.org/project/fsociety/)
[![Python Version](https://img.shields.io/badge/python-3.12%2B-blue?logo=python&style=flat-square)](https://www.python.org/downloads/)
![PyPI - Downloads](https://img.shields.io/pypi/dm/fsociety?style=flat-square)
[![Docker Image Size (tag)](https://img.shields.io/docker/image-size/fsocietyteam/fsociety/latest?style=flat-square)](https://hub.docker.com/r/fsocietyteam/fsociety)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-organge.svg?logo=git&logoColor=organge&style=flat-square)](http://makeapullrequest.com)

## 🎯 A Modern Penetration Testing Framework (2025 Edition)

**fsociety** is a comprehensive, modular penetration testing framework that brings together the best open-source security tools in one unified interface. Now modernized with Python 3.12+ features, GPU acceleration, cloud security tools, and enhanced security.

[![Modern Features](https://img.shields.io/badge/MODERN_FEATURES.md-green?style=flat-square)](MODERN_FEATURES.md)
[![Quick Start](https://img.shields.io/badge/QUICKSTART.md-blue?style=flat-square)](QUICKSTART.md)
[![Changelog](https://img.shields.io/badge/CHANGELOG.md-red?style=flat-square)](CHANGELOG.md)

<p align="center">
  <img src="https://raw.githubusercontent.com/fsociety-team/fsociety/main/images/cli.png" width="600px" alt="fsociety cli" />
</p>

---

## ✨ What's New in 2025

### 🚀 Python 3.12+ Features
- **Pattern Matching**: Clean code with match/case
- **Type Safety**: 100% type hint coverage  
- **Better Errors**: Enhanced debugging
- **Performance**: Faster execution

### 🎮 GPU Acceleration
- **10-100x Faster**: GPU password cracking
- **Auto-Detection**: CUDA/OpenCL support
- **Multiple Hashes**: MD5, SHA, bcrypt, and more

### ☁️ Cloud Security (NEW!)
- **ScoutSuite**: Multi-cloud auditing (AWS/Azure/GCP)
- **Trivy**: Container security scanning
- Modern cloud-native security

### 🌐 New Tools
- **Nuclei**: Modern vulnerability scanner
- Enhanced existing tools
- Better performance & security

---

## ⚡ Quick Setup

### One-Line Install

```bash
git clone https://github.com/fsociety-team/fsociety.git && cd fsociety && chmod +x install.sh && ./install.sh
```

### Manual Install

```bash
git clone https://github.com/fsociety-team/fsociety.git
cd fsociety
pip install -e .
fsociety
```

---

## 📦 Installation Guide

### Prerequisites

**Required:**
- Python 3.12+ 
- pip 23.0+
- Git

**Optional:**
- hashcat (GPU acceleration)
- nmap (network scanning)
- Go (some tools)
- Docker (container scanning)

### Step-by-Step

#### 1. Install Python 3.12+

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt install python3.12 python3.12-venv python3-pip
```

**macOS:**
```bash
brew install python@3.12
```

**Arch:**
```bash
sudo pacman -S python
```

#### 2. Clone Repository

```bash
git clone https://github.com/fsociety-team/fsociety.git
cd fsociety
```

#### 3. Run Installer

```bash
chmod +x install.sh
./install.sh
```

The installer will:
- ✅ Check Python version
- ✅ Install system dependencies
- ✅ Create virtual environment
- ✅ Install Python packages
- ✅ Optionally install hashcat & Go
- ✅ Verify installation

#### 4. Start fsociety

```bash
# Activate venv if created
source venv/bin/activate

# Run
fsociety
```

### Platform-Specific

<details>
<summary><b>Kali Linux / Ubuntu / Debian</b></summary>

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y git python3-pip python3-venv nmap golang-go hashcat
git clone https://github.com/fsociety-team/fsociety.git
cd fsociety
./install.sh
```
</details>

<details>
<summary><b>Arch Linux</b></summary>

```bash
sudo pacman -Syu
sudo pacman -S git python-pip nmap go hashcat
git clone https://github.com/fsociety-team/fsociety.git
cd fsociety
./install.sh
```
</details>

<details>
<summary><b>macOS</b></summary>

```bash
brew install python@3.12 nmap go hashcat
git clone https://github.com/fsociety-team/fsociety.git
cd fsociety
./install.sh
```
</details>

<details>
<summary><b>Windows (WSL2)</b></summary>

```bash
# Install WSL2 Ubuntu first
# Then:
sudo apt update
git clone https://github.com/fsociety-team/fsociety.git
cd fsociety
./install.sh
```
</details>

---

## 🚀 Usage

### Basic Commands

```bash
fsociety              # Start interactive mode
fsociety --help       # Show help
fsociety --info       # Show version
fsociety --suggest    # Suggest a tool
```

### Interactive Mode

```
╔══════════════════════════════════════╗
║        fsociety v4.0.0              ║
║  Penetration Testing Framework       ║
╚══════════════════════════════════════╝

Categories:
  1. Information Gathering (7 tools)
  2. Networking (2 tools)
  3. Web Apps (3 tools)
  4. Passwords (5 tools)
  5. Cloud Security (2 tools) ⭐ NEW
  6. Obfuscation (1 tool)
  7. Utilities (5 tools)

fsociety> _
```

### Example Sessions

**Port Scanning:**
```bash
fsociety> 2           # Networking
fsociety> nmap        # Select nmap
Target: 192.168.1.1
Scan: 1               # Simple scan
```

**Subdomain Enum:**
```bash
fsociety> 1           # Info Gathering  
fsociety> sublist3r   # Subdomains
Domain: example.com
```

**GPU Hash Cracking:**
```bash
fsociety> 4           # Passwords
fsociety> hash_buster # Hash cracking
Hash: 5f4dcc3b5aa765d61d8327deb882cf99
Method: 2             # GPU
Wordlist: /usr/share/wordlists/rockyou.txt
```

**Nuclei Scan:**
```bash
fsociety> 3           # Web Apps
fsociety> nuclei      # Nuclei
Target: https://example.com
Severity: critical,high
Update: y
```

**Cloud Audit:**
```bash
fsociety> 5           # Cloud Security
fsociety> scoutsuite  # ScoutSuite
Provider: 1           # AWS
```

**Container Scan:**
```bash
fsociety> 5           # Cloud Security
fsociety> trivy       # Trivy
Type: 1               # Docker image
Image: nginx:latest
```

---

## 🛠️ Available Tools

### Information Gathering (7)
- **sqlmap** - SQL injection
- **Striker** - Recon scanner
- **Sublist3r** - Subdomains
- **Sherlock** - Social media OSINT
- **S3Scanner** - AWS S3 buckets
- **gitGraber** - GitHub secrets
- **HydraRecon** - Domain recon

### Networking (2)
- **nmap** - Port scanning
- **bettercap** - MITM attacks

### Web Apps (3)
- **XSStrike** - XSS scanner
- **Photon** - Web crawler
- **Nuclei** ⭐ - Modern vuln scanner

### Passwords (5)
- **cupp** - Password lists
- **Cr3d0v3r** - Credential checker
- **Hash-Buster** 🎮 - GPU hash cracker
- **changeme** - Default creds
- **traitor** - Privesc

### Cloud Security (2) ⭐ NEW
- **ScoutSuite** - Multi-cloud audit
- **Trivy** - Container scanner

### Obfuscation (1)
- **Cuteit** - IP obfuscation

### Utilities (5)
- host2ip, base64_decode, spawn_shell, suggest_tool, print_contributors

---

## 🎮 GPU Acceleration

### Setup

```bash
# Install hashcat
sudo apt install hashcat      # Ubuntu
sudo pacman -S hashcat        # Arch
brew install hashcat          # macOS

# Verify
hashcat --version
```

### Performance

| Hash | CPU | GPU (RTX 3080) | Speedup |
|------|-----|----------------|---------|
| MD5 | 100 MH/s | 10 GH/s | 100x |
| SHA256 | 50 MH/s | 2 GH/s | 40x |
| bcrypt | 5 KH/s | 50 KH/s | 10x |

### Usage

```python
from fsociety.core.gpu_accelerator import HashcatCracker, HashType

cracker = HashcatCracker()
password = cracker.crack_hash(
    hash_value="5f4dcc3b5aa765d61d8327deb882cf99",
    hash_type=HashType.MD5,
    wordlist="/usr/share/wordlists/rockyou.txt",
    use_gpu=True
)
```

---

## ⚙️ Configuration

**Location:** `~/.fsociety/fsociety.cfg`

```ini
[fsociety]
version = 4.0.0
ssh_clone = false    # Use SSH for git
os = debian          # Auto-detected
host_file = hosts.txt
usernames_file = usernames.txt
```

**Directories:**
```
~/.fsociety/
├── fsociety.cfg     # Config
├── fsociety.log     # Logs
├── hosts.txt        # Saved hosts
├── [tools]/         # Tool directories
└── .cache/          # Cache
```

**Environment:**
```bash
export FSOCIETY_LOG_LEVEL=DEBUG
export FSOCIETY_NO_GPU=1
```

---

## 🐋 Docker

```bash
# Run
docker run -it fsocietyteam/fsociety

# With GPU
docker run --gpus all -it fsocietyteam/fsociety

# Build
docker build -t fsociety .
```

---

## 📚 Documentation

- [QUICKSTART.md](QUICKSTART.md) - Quick start guide
- [MODERN_FEATURES.md](MODERN_FEATURES.md) - Feature docs
- [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) - Implementation
- [CHANGELOG.md](CHANGELOG.md) - Changes

---

## ❓ FAQ

**Q: Why Python 3.12+?**  
A: Modern features, better performance, enhanced error messages

**Q: Need GPU?**  
A: Optional. 10-100x faster for password cracking

**Q: Update fsociety?**
```bash
cd fsociety && git pull && pip install -e . --upgrade
```

**Q: Tool install failed?**  
A: Check logs: `~/.fsociety/fsociety.log`

**Q: Windows support?**  
A: Use WSL2 or Docker

**Q: Is it legal?**  
A: Yes, for authorized testing only. Get permission first!

---

## 🤝 Contributing

1. Fork repository
2. Create branch
3. Make changes
4. Add tests
5. Submit PR

See [CONTRIBUTING.md](CONTRIBUTING.md)

---

## 📄 License

MIT License - see [LICENSE](LICENSE)

---

## ⚠️ Legal Disclaimer

**fsociety is for authorized security testing only.**

✅ **MUST:**
- Have written permission
- Stay in scope
- Follow laws
- Responsible disclosure

❌ **PROHIBITED:**
- Unauthorized access
- Illegal activities
- Malicious use

**Authors NOT responsible for misuse.**

---

## 🙏 Acknowledgments

- Original fsociety-team
- hashcat team
- All tool authors
- Security community
- Contributors

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/fsociety-team/fsociety/issues)
- **Discussions**: [GitHub Discussions](https://github.com/fsociety-team/fsociety/discussions)
- **Twitter**: [@fsociety_team](https://twitter.com/fsociety_team)

---

**Made with ❤️ by the fsociety team**

**"Control is an illusion."**
