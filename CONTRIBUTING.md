# Contributing to Multi-Agent AI System

Thank you for your interest in contributing to this project! We welcome contributions from everyone.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/yourusername/multi-agent-ai-system.git`
3. Create a feature branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Test your changes thoroughly
6. Submit a pull request

## Development Setup

1. Install dependencies:
   ```bash
   uv sync
   ```

2. Set up your environment:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. Install Ollama and required models:
   ```bash
   ollama pull llama3.1:8b
   ```

## Code Style

- Follow PEP 8 for Python code
- Use type hints where appropriate
- Add docstrings for functions and classes
- Write clear, descriptive commit messages

## Testing

Before submitting a pull request:

1. Run the validation script:
   ```bash
   uv run python validate_setup.py
   ```

2. Test the web interface:
   ```bash
   uv run python test_web_ui.py
   ```

3. Ensure both agents start successfully:
   ```bash
   uv run python start_agents.py
   ```

## Submitting Changes

1. Push your changes to your fork
2. Submit a pull request with:
   - Clear description of changes
   - Any breaking changes noted
   - Test results included

## Reporting Issues

Please use GitHub Issues to report bugs or request features. Include:
- Steps to reproduce the issue
- Expected vs actual behavior
- System information (OS, Python version, etc.)

## Code of Conduct

Please be respectful and constructive in all interactions. We're all here to learn and improve the project together.

## Questions?

Feel free to open a GitHub Discussion if you have questions about contributing or need help getting started.
