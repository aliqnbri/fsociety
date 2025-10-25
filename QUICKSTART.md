# fsociety Quick Start Guide

## Installation

### Prerequisites
- Python 3.12 or higher
- pip
- Git

### Basic Installation

```bash
# Clone the repository
git clone https://github.com/fsociety-team/fsociety.git
cd fsociety

# Install fsociety
pip install -e .

# Run fsociety
fsociety
```

### Docker Installation

```bash
# Build Docker image
docker build -t fsociety .

# Run fsociety in Docker
docker run -it fsociety
```

## Quick Usage

### 1. First Run

When you run fsociety for the first time:

```bash
fsociety
```

You'll see:
- Terms and conditions (accept to continue)
- Main menu with tool categories

### 2. Main Menu

```
fsociety - Modular Penetration Testing Framework

Categories:
1. Information Gathering (7 tools)
2. Networking (2 tools)
3. Web Apps (2 tools)
4. Passwords (5 tools)
5. Obfuscation (1 tool)
6. Utilities (5 tools)

Type a category number or tool name to continue...
```

### 3. Running a Tool

Example: Using nmap for port scanning

```bash
fsociety> 2              # Select Networking category
fsociety> nmap           # Select nmap tool

# Tool will install if not already installed
# Follow prompts to use the tool
```

## Common Use Cases

### Information Gathering

#### Subdomain Enumeration
```bash
fsociety> 1              # Information Gathering
fsociety> sublist3r      # Subdomain enumeration
Enter domain: example.com
```

#### SQL Injection Testing
```bash
fsociety> 1              # Information Gathering
fsociety> sqlmap         # SQL injection tool
Enter URL: http://example.com/page?id=1
```

### Network Scanning

#### Quick Port Scan
```bash
fsociety> 2              # Networking
fsociety> nmap           # Port scanner
Select scan type: 1      # Simple scan
Enter target: 192.168.1.1
```

#### Vulnerability Scan
```bash
fsociety> 2              # Networking
fsociety> nmap           # Port scanner
Select scan type: 3      # Vulnerability scan
Enter target: 192.168.1.1
```

### Password Cracking

#### Hash Cracking (with GPU)
```bash
fsociety> 4              # Passwords
fsociety> hash_buster    # Hash cracking
Enter hash: 5f4dcc3b5aa765d61d8327deb882cf99
Select method: 2         # GPU-accelerated
Enter wordlist: /usr/share/wordlists/rockyou.txt
```

#### Password List Generation
```bash
fsociety> 4              # Passwords
fsociety> cupp           # Password profiler
# Follow interactive prompts
```

### Web Application Testing

#### XSS Detection
```bash
fsociety> 3              # Web Apps
fsociety> xsstrike       # XSS detection
Enter URL: http://example.com
```

## Configuration

### Config File Location
```
~/.fsociety/fsociety.cfg
```

### Common Settings

```ini
[fsociety]
version = 3.2.10
agreement = true
ssh_clone = false          # Use SSH for git clones
os = debian                # Auto-detected OS
host_file = hosts.txt      # Hosts file name
usernames_file = usernames.txt
```

### Enable SSH Cloning
```bash
nano ~/.fsociety/fsociety.cfg

# Change:
ssh_clone = true
```

### Change Installation Directory
Edit the config or set environment variable:
```bash
export FSOCIETY_INSTALL_DIR=/custom/path
```

## GPU Acceleration Setup

### Install hashcat

#### Ubuntu/Debian/Kali
```bash
sudo apt update
sudo apt install hashcat
```

#### Arch Linux
```bash
sudo pacman -S hashcat
```

#### macOS
```bash
brew install hashcat
```

### Verify GPU Support
```bash
# Check NVIDIA GPU
nvidia-smi

# Check hashcat can see GPU
hashcat -I
```

### Test GPU Performance
```python
from fsociety.core.gpu_accelerator import HashcatCracker

cracker = HashcatCracker()
speeds = cracker.benchmark_gpu()
print(f"GPU Speed: {speeds}")
```

## Utilities

### Host Management
```bash
fsociety> 6              # Utilities
fsociety> host2ip        # DNS lookup
Enter host: example.com
```

### Base64 Decode
```bash
fsociety> 6              # Utilities
fsociety> base64_decode  # Base64 decoder
Enter encoded string: SGVsbG8gV29ybGQ=
```

### Spawn Shell
```bash
fsociety> 6              # Utilities
fsociety> spawn_shell    # Local shell
# Drops into system shell
```

## Troubleshooting

### Tool Installation Failed
```bash
# Reinstall the tool
fsociety> tool_name
# When prompted, confirm reinstallation
```

### GPU Not Detected
```bash
# Check NVIDIA drivers
nvidia-smi

# Reinstall hashcat
sudo apt install --reinstall hashcat

# Check OpenCL support
clinfo
```

### Permission Denied
```bash
# Some tools require root/sudo
sudo fsociety

# Or run specific tools with sudo
sudo nmap -sS target
```

### Network Issues (Git Clone)
```bash
# Use HTTPS instead of SSH
nano ~/.fsociety/fsociety.cfg
# Set: ssh_clone = false

# Or set proxy
export http_proxy=http://proxy:port
export https_proxy=http://proxy:port
```

## Tips and Tricks

### 1. Tab Completion
fsociety supports tab completion for commands and tool names.

### 2. Batch Operations
Use the utilities to manage multiple hosts:
```bash
# Add hosts to list
fsociety> host2ip
Enter host: example.com
Save to list? yes
```

### 3. Custom Wordlists
Store wordlists in `~/.fsociety/wordlists/` for easy access.

### 4. Performance Tuning
For GPU cracking, adjust workload profile:
- Profile 1: Low (for desktop use)
- Profile 2: Default
- Profile 3: High (dedicated cracking)
- Profile 4: Maximum (highest performance)

### 5. Logging
Enable debug logging:
```bash
export FSOCIETY_LOG_LEVEL=DEBUG
fsociety
```

View logs:
```bash
tail -f ~/.fsociety/fsociety.log
```

## Best Practices

### 1. Always Get Permission
Only use fsociety on systems you own or have explicit permission to test.

### 2. Use VMs for Testing
Test tools in virtual machines first to understand their behavior.

### 3. Keep Tools Updated
Regularly update fsociety and its tools:
```bash
cd /path/to/fsociety
git pull
pip install -e . --upgrade
```

### 4. Backup Configuration
```bash
cp ~/.fsociety/fsociety.cfg ~/.fsociety/fsociety.cfg.backup
```

### 5. Read Tool Documentation
Each tool has its own documentation. Check the tool's GitHub repository for details.

## Examples

### Full Penetration Test Workflow

#### 1. Reconnaissance
```bash
# Find subdomains
fsociety> sublist3r
Domain: target.com

# Scan open ports
fsociety> nmap
Target: target.com
Scan type: 2 (aggressive)
```

#### 2. Vulnerability Assessment
```bash
# SQL injection test
fsociety> sqlmap
URL: http://target.com/page?id=1

# XSS detection
fsociety> xsstrike
URL: http://target.com/search
```

#### 3. Exploitation (Authorized Only)
```bash
# Use appropriate tools based on findings
# Always have written permission!
```

#### 4. Post-Exploitation
```bash
# Hash cracking
fsociety> hash_buster
Hash: [captured hash]
Method: GPU-accelerated
```

## Resources

- **Main Documentation**: See MODERN_FEATURES.md
- **GitHub**: https://github.com/fsociety-team/fsociety
- **Issues**: https://github.com/fsociety-team/fsociety/issues

## Legal Notice

fsociety is designed for authorized security testing only. Unauthorized access to computer systems is illegal. Always:

1. Get written permission before testing
2. Stay within the scope of your authorization
3. Follow responsible disclosure practices
4. Comply with all applicable laws

---

Happy (ethical) hacking! 🎩
