# Contributing to fsociety

Thank you for your interest in contributing to fsociety! This guide will help you get started.

## 🎯 Ways to Contribute

- 🐛 **Bug Reports**: Report bugs and issues
- 💡 **Feature Requests**: Suggest new features
- 📝 **Documentation**: Improve documentation
- 🔧 **Code**: Submit pull requests
- 🧪 **Testing**: Write and improve tests
- 🌍 **Translation**: Help translate the project
- 💬 **Community**: Help others in discussions

## 📋 Getting Started

### 1. Fork and Clone

```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/YOUR_USERNAME/fsociety.git
cd fsociety

# Add upstream remote
git remote add upstream https://github.com/fsociety-team/fsociety.git
```

### 2. Setup Development Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[all]"

# Install pre-commit hooks
pre-commit install
```

### 3. Create a Branch

```bash
# Update main branch
git checkout main
git pull upstream main

# Create feature branch
git checkout -b feature/your-feature-name

# Or for bug fixes
git checkout -b fix/bug-description
```

## 🔧 Development Workflow

### Code Style

We use modern Python 3.12+ features and follow these guidelines:

```python
# Use type hints
async def scan_target(target: str, options: dict[str, Any]) -> ScanResult:
    """Scan a target with given options."""
    pass

# Use match statements (Python 3.10+)
match scan_type:
    case ScanType.QUICK:
        return await quick_scan()
    case ScanType.DEEP:
        return await deep_scan()

# Use dataclasses
from dataclasses import dataclass

@dataclass
class Config:
    enabled: bool = True
    timeout: int = 30
```

### Code Quality Tools

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

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=fsociety --cov-report=html

# Run specific test file
pytest tests/test_core.py -v

# Run tests matching pattern
pytest -k "test_async" -v

# Run benchmarks
pytest --benchmark-only

# Run GPU tests (if GPU available)
pytest tests/test_gpu.py -v
```

### Writing Tests

```python
import pytest
from fsociety.core.config import Config

class TestConfig:
    """Test configuration system."""
    
    def test_config_initialization(self):
        """Test config initializes with defaults."""
        config = Config()
        assert config.version is not None
    
    @pytest.mark.asyncio
    async def test_async_operation(self):
        """Test async operations."""
        result = await some_async_function()
        assert result is not None
    
    @pytest.mark.benchmark
    def test_performance(self, benchmark):
        """Benchmark operation."""
        result = benchmark(some_function)
        assert result is not None
```

## 📝 Pull Request Guidelines

### Before Submitting

- [ ] Code follows project style guidelines
- [ ] All tests pass
- [ ] New tests added for new features
- [ ] Documentation updated
- [ ] Commit messages are clear and descriptive
- [ ] No merge conflicts with main

### PR Title Format

```
type(scope): description

Examples:
feat(ai): add GPU acceleration for model inference
fix(cache): resolve memory leak in file cache
docs(readme): update installation instructions
test(core): add integration tests for async operations
perf(scan): optimize concurrent scanning performance
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Test additions/changes
- `perf`: Performance improvements
- `refactor`: Code refactoring
- `style`: Code style changes
- `chore`: Build/tooling changes

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
Describe testing performed

## Checklist
- [ ] Tests pass locally
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
```

## 🏗️ Project Structure

```
fsociety/
├── __init__.py
├── __main__.py           # CLI entry point
├── __version__.py        # Version info
├── console.py           # Rich console
├── core/                # Core functionality
│   ├── config.py        # Configuration
│   ├── async_repo.py    # Async operations
│   ├── cache.py         # Caching system
│   └── performance.py   # Performance monitoring
├── ai/                  # AI features
│   ├── engine.py        # AI engine
│   └── exploit_assistant.py
├── information_gathering/
├── networking/
├── web_apps/
├── passwords/
└── obfuscation/

tests/
├── test_core.py
├── test_integration.py
├── test_gpu.py
└── conftest.py

examples/
└── basic_usage.py

docs/
└── ...
```

## 🎨 Adding New Features

### 1. Adding a New Tool

```python
# fsociety/information_gathering/new_tool.py

from fsociety.core.async_repo import AsyncGitHubRepo

class NewToolRepo(AsyncGitHubRepo):
    """Description of the tool."""
    
    def __init__(self) -> None:
        super().__init__(
            path="author/repo",
            install={"pip": "requirements.txt"},
            description="Tool description",
        )
    
    async def run(self) -> int:
        """Run the tool."""
        # Implementation
        pass

# Create instance
new_tool = NewToolRepo()
```

### 2. Adding CLI Commands

```python
# fsociety/__main__.py

@cli.command()
@click.argument("target")
async def scan(target: str) -> None:
    """Scan a target."""
    result = await perform_scan(target)
    console.print(result)
```

### 3. Adding AI Features

```python
# fsociety/ai/engine.py

async def new_analysis_method(
    self,
    data: dict[str, Any],
) -> AIResult:
    """New AI analysis method."""
    prompt = self._build_prompt(data)
    response = await self._generate(prompt)
    return self._parse_response(response)
```

## 📚 Documentation

### Docstring Format (Google Style)

```python
async def scan_target(
    target: str,
    scan_type: ScanType = ScanType.QUICK,
    timeout: int = 30,
) -> ScanResult:
    """Scan a target for vulnerabilities.
    
    Args:
        target: The target hostname or IP address.
        scan_type: Type of scan to perform.
        timeout: Timeout in seconds.
    
    Returns:
        ScanResult object containing scan results.
    
    Raises:
        ValueError: If target is invalid.
        TimeoutError: If scan times out.
    
    Examples:
        >>> result = await scan_target("example.com")
        >>> print(result.open_ports)
        [80, 443]
    """
    pass
```

### Adding Documentation

1. Update docstrings in code
2. Add examples in `examples/`
3. Update README.md if needed
4. Add to documentation site (if applicable)

## 🐛 Reporting Bugs

Use the [Issue Template](.github/ISSUE_TEMPLATE/bug-report.md):

```markdown
**Description**
Clear description of the bug

**To Reproduce**
Steps to reproduce the behavior

**Expected Behavior**
What you expected to happen

**Environment**
- OS: [e.g., Ubuntu 22.04]
- Python: [e.g., 3.12.0]
- fsociety: [e.g., 4.0.0]
- GPU: [e.g., NVIDIA RTX 4090]

**Additional Context**
Any other relevant information
```

## 💡 Feature Requests

Use the [Feature Request Template](.github/ISSUE_TEMPLATE/feature-request.md):

```markdown
**Problem Description**
What problem does this feature solve?

**Proposed Solution**
How should this feature work?

**Alternatives Considered**
What other solutions did you consider?

**Additional Context**
Any other relevant information
```

## 🌟 Best Practices

### 1. Async/Await

```python
# ✅ Good - Use async/await
async def process_items(items: list[str]) -> list[Result]:
    tasks = [process_item(item) for item in items]
    return await asyncio.gather(*tasks)

# ❌ Bad - Blocking operations
def process_items(items: list[str]) -> list[Result]:
    return [process_item(item) for item in items]
```

### 2. Type Hints

```python
# ✅ Good - Full type hints
async def scan(
    target: str,
    options: dict[str, Any] | None = None,
) -> ScanResult | None:
    pass

# ❌ Bad - No type hints
async def scan(target, options=None):
    pass
```

### 3. Error Handling

```python
# ✅ Good - Specific exceptions
try:
    result = await scan_target(target)
except TimeoutError:
    logger.error("Scan timed out")
    return None
except ValueError as e:
    logger.error(f"Invalid target: {e}")
    return None

# ❌ Bad - Bare except
try:
    result = await scan_target(target)
except:
    return None
```

### 4. Resource Cleanup

```python
# ✅ Good - Use context managers
async with gpu_manager.auto_cleanup():
    result = await gpu_operation()

# ❌ Bad - Manual cleanup
try:
    result = await gpu_operation()
finally:
    cleanup()
```

## 🔒 Security

- Never commit API keys or credentials
- Use environment variables for secrets
- Validate all user input
- Follow security best practices
- Report security issues privately to security@fsociety.dev

## 📞 Getting Help

- 💬 [Discord Community](https://discord.gg/fsociety)
- 📖 [Documentation](https://fsociety.dev/docs)
- 🐛 [Issue Tracker](https://github.com/fsociety-team/fsociety/issues)
- 📧 [Email](mailto:contact@fsociety.dev)

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

## 🙏 Recognition

Contributors are recognized in:
- README.md
- Release notes
- Hall of Fame (coming soon)

Thank you for contributing to fsociety! 🎉