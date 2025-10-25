# fsociety Modern Features Guide

## Overview

fsociety has been modernized with Python 3.12+ features, GPU acceleration, improved security, and better performance. This guide covers all the new features and improvements.

## 🚀 What's New in 2025

### Python 3.12+ Features

#### 1. Type Parameter Syntax
The codebase now uses modern type hints with the new `type` statement:

```python
type InstallConfig = str | dict[str, str | list[str]]
```

#### 2. Pattern Matching (match/case)
Enhanced code readability with structural pattern matching:

```python
match attack_mode:
    case AttackMode.STRAIGHT | AttackMode.COMBINATION:
        if not wordlist:
            raise ValueError("Attack requires a wordlist")
    case AttackMode.BRUTE_FORCE:
        if not mask:
            raise ValueError("BRUTE_FORCE attack requires a mask")
```

#### 3. Improved Error Messages
Python 3.12's enhanced error messages help with debugging:
- Better traceback information
- Precise error locations
- More context in exceptions

### 🛡️ Security Improvements

#### Input Validation
All user inputs are now validated using Pydantic:

```python
from fsociety.core.validation import validate_url, validate_domain, validate_ip

# Automatically validates and sanitizes
url = validate_url("example.com")  # Returns: http://example.com
```

#### Secure Command Execution
Replaced dangerous `os.system()` calls with secure subprocess execution:

```python
from fsociety.core.executor import execute_command

# Safe execution with timeout and error handling
result = execute_command(
    ["nmap", "-sV", target],
    timeout=300,
    check=True
)
```

#### Shell Injection Prevention
All command arguments are sanitized:

```python
from fsociety.core.validation import sanitize_shell_arg

safe_arg = sanitize_shell_arg(user_input)
```

### ⚡ Performance Enhancements

#### 1. Caching System
Expensive operations are cached to improve performance:

```python
from fsociety.core.cache import cached

@cached(ttl=300)  # Cache for 5 minutes
def expensive_operation():
    # This result will be cached
    return compute_something()
```

#### 2. Async/Await Support
Concurrent operations for better performance:

```python
from fsociety.core.executor import execute_command_async

# Run commands concurrently
result = await execute_command_async(["tool", "arg"])
```

#### 3. Multiprocessing
CPU-intensive tasks use multiprocessing for better performance.

### 🎮 GPU Acceleration

#### Overview
fsociety now supports GPU-accelerated password cracking using hashcat with CUDA/OpenCL.

#### GPU Detection
Automatically detects available GPU resources:

```python
from fsociety.core.gpu_accelerator import detect_gpu

gpu_info = detect_gpu()
if gpu_info.is_available():
    print(f"GPU available: {gpu_info.recommended_backend}")
    print(f"GPU count: {gpu_info.gpu_count}")
    print(f"Devices: {gpu_info.gpu_devices}")
```

#### Hash Cracking with GPU
Use GPU acceleration for password cracking:

```python
from fsociety.core.gpu_accelerator import HashcatCracker, HashType, AttackMode

cracker = HashcatCracker()

# Crack MD5 hash with GPU
password = cracker.crack_hash(
    hash_value="5f4dcc3b5aa765d61d8327deb882cf99",
    hash_type=HashType.MD5,
    wordlist="/usr/share/wordlists/rockyou.txt",
    attack_mode=AttackMode.STRAIGHT,
    use_gpu=True,
    workload_profile=3  # Maximum performance
)

if password:
    print(f"Cracked: {password}")
```

#### Supported Hash Types
- MD5
- SHA1, SHA256, SHA512
- NTLM
- bcrypt
- WPA/WPA2
- And many more...

#### Attack Modes
1. **Dictionary Attack** - Use wordlist
2. **Brute Force** - Try all combinations
3. **Hybrid** - Wordlist + mask combinations

### 📊 Logging System

#### Structured Logging
Comprehensive logging with multiple handlers:

```python
from fsociety.core.logging_config import setup_logging

# Setup logging with Rich formatting
logger = setup_logging(
    level="INFO",
    log_file="~/.fsociety/fsociety.log",
    rich_formatting=True
)

logger.info("Application started")
logger.warning("This is a warning")
logger.error("This is an error")
```

#### Log Levels
- **DEBUG**: Detailed information for debugging
- **INFO**: General informational messages
- **WARNING**: Warning messages
- **ERROR**: Error messages
- **CRITICAL**: Critical errors

#### Log Rotation
Logs are automatically rotated:
- Maximum size: 10 MB
- Backup count: 5 files

### 🏗️ Modular Architecture

#### New Core Modules

##### 1. `fsociety.core.validation`
Input validation and sanitization:
- URL validation
- Domain validation
- IP address validation
- File path validation
- Command argument sanitization

##### 2. `fsociety.core.executor`
Secure command execution:
- Subprocess management
- Timeout support
- Error handling
- Async execution
- Context managers

##### 3. `fsociety.core.gpu_accelerator`
GPU-accelerated operations:
- GPU detection
- Hashcat integration
- Hash type detection
- Performance benchmarking

##### 4. `fsociety.core.cache`
Caching and performance:
- Disk-based caching
- TTL support
- Decorator-based caching
- In-memory memoization

##### 5. `fsociety.core.logging_config`
Logging configuration:
- Rich formatting
- File handlers
- Console handlers
- Rotation support

### 📦 Updated Dependencies (2025)

All dependencies updated to latest versions:

```
distro>=1.9.0           # Platform detection
GitPython>=3.1.45       # Git operations
requests>=2.32.5        # HTTP client
rich>=14.2.0            # Terminal formatting
urllib3>=2.2.3          # HTTP library
aiohttp>=3.10.0         # Async HTTP
pydantic>=2.9.0         # Data validation
psutil>=6.0.0           # System monitoring
```

## 🔧 Installation

### Requirements
- Python 3.12 or higher
- pip 23.0+
- Git

### Optional (for GPU acceleration)
- NVIDIA GPU with CUDA support
- hashcat installed
- NVIDIA drivers

### Install fsociety

```bash
# Clone repository
git clone https://github.com/fsociety-team/fsociety.git
cd fsociety

# Install
pip install -e .
```

### Install hashcat (for GPU features)

#### Ubuntu/Debian/Kali
```bash
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

## 📖 Usage Examples

### Basic Usage

```bash
# Start fsociety
fsociety

# Or run directly
python -m fsociety
```

### Using GPU-Accelerated Tools

#### 1. Hash Cracking with GPU

```bash
# Start fsociety
fsociety

# Select: Passwords → Hash-Buster
# Choose method: 2 (GPU-accelerated cracking)
# Enter hash: 5f4dcc3b5aa765d61d8327deb882cf99
# Wordlist: /usr/share/wordlists/rockyou.txt
```

#### 2. Benchmark GPU Performance

```python
from fsociety.core.gpu_accelerator import HashcatCracker

cracker = HashcatCracker()
speeds = cracker.benchmark_gpu()
print(f"MD5 speed: {speeds.get('MD5', 0)} H/s")
```

### Advanced Usage

#### 1. Enable Debug Logging

```bash
# Set environment variable
export FSOCIETY_LOG_LEVEL=DEBUG
fsociety
```

#### 2. Use Custom Configuration

```bash
# Edit config file
nano ~/.fsociety/fsociety.cfg

# Enable SSH cloning
[fsociety]
ssh_clone = true
```

#### 3. Clear Cache

```python
from fsociety.core.cache import Cache

cache = Cache()
cache.clear()  # Clear all cached data
```

## 🐛 Bug Fixes

### Critical Fixes

1. **s3scanner Domain Bug** - Fixed domain concatenation issue where multiple domains were merged without newlines
2. **Command Injection** - Replaced all `os.system()` calls with secure subprocess execution
3. **Input Validation** - Added comprehensive input validation to prevent injection attacks
4. **Directory Context** - Fixed directory changing issues with context managers

### Performance Fixes

1. **Caching** - Added caching to reduce repeated expensive operations
2. **Async Operations** - Implemented async execution for concurrent tasks
3. **Connection Pooling** - Improved HTTP request performance

## 🔒 Security Best Practices

### 1. Always Validate Input
```python
from fsociety.core.validation import validate_url

# This will raise ValueError for invalid URLs
url = validate_url(user_input)
```

### 2. Use Context Managers
```python
from fsociety.core.executor import change_directory

# Automatically returns to original directory
with change_directory("/tmp"):
    # Work in /tmp
    pass
```

### 3. Set Timeouts
```python
from fsociety.core.executor import execute_command

# Always set reasonable timeouts
result = execute_command(cmd, timeout=300)
```

### 4. Check Results
```python
result = execute_command(cmd, check=False)

if result.success:
    print("Success:", result.stdout)
else:
    print("Failed:", result.stderr)
```

## 🎯 Performance Tips

### 1. Use GPU When Available
For password cracking, always use GPU acceleration when available - it's 10-100x faster than CPU.

### 2. Enable Caching
Caching can significantly improve performance for repeated operations.

### 3. Use Async for I/O-Bound Tasks
When running multiple network or I/O operations, use async execution.

### 4. Optimize Workload Profile
For hashcat, adjust the workload profile (1-4):
- 1: Low (for desktop use)
- 2: Default
- 3: High (dedicated cracking)
- 4: Nightmare (maximum performance)

## 🧪 Testing

### Run Tests
```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/

# With coverage
pytest --cov=fsociety tests/
```

## 📚 API Reference

### Validation Module
```python
from fsociety.core.validation import (
    validate_url,
    validate_domain,
    validate_ip,
    validate_file_path,
    sanitize_shell_arg,
)
```

### Executor Module
```python
from fsociety.core.executor import (
    execute_command,
    execute_command_async,
    execute_python_script,
    change_directory,
    ExecutionResult,
)
```

### GPU Accelerator Module
```python
from fsociety.core.gpu_accelerator import (
    detect_gpu,
    HashcatCracker,
    HashType,
    AttackMode,
)
```

### Cache Module
```python
from fsociety.core.cache import (
    Cache,
    cached,
    memoize,
)
```

### Logging Module
```python
from fsociety.core.logging_config import (
    setup_logging,
    get_logger,
)
```

## 🤝 Contributing

Contributions are welcome! Please ensure:

1. Code follows Python 3.12+ best practices
2. All inputs are validated
3. All commands use secure execution
4. Tests are included
5. Documentation is updated

## 📄 License

MIT License - see LICENSE file for details.

## 🙏 Acknowledgments

- fsociety-team for the original framework
- hashcat team for GPU acceleration capabilities
- All tool authors whose projects are integrated

## 📞 Support

- GitHub Issues: https://github.com/fsociety-team/fsociety/issues
- Documentation: https://fsociety.dev/

---

**Note**: This is a penetration testing framework intended for authorized security testing only. Unauthorized access to computer systems is illegal.
