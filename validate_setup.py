#!/usr/bin/env python3
"""Simple system validation script for AI Agents setup."""

import sys
import os
import subprocess
from pathlib import Path
import importlib.util


def print_header(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def check_python_version():
    """Check Python version."""
    print_header("Checking Python Version")
    version = sys.version_info
    print(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")
    if version >= (3, 13):
        print("✅ Python 3.13+ is being used")
        return True
    else:
        print("❌ Python 3.13+ is recommended")
        return False


def check_uv():
    """Check if UV is installed."""
    print_header("Checking UV")
    try:
        result = subprocess.run(["uv", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ UV is installed: {result.stdout.strip()}")
            return True
        else:
            print("❌ UV is not working properly")
            return False
    except FileNotFoundError:
        print("❌ UV is not installed")
        return False


def check_ollama():
    """Check if Ollama is installed and running."""
    print_header("Checking Ollama")
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Ollama is installed and running")
            return True
        else:
            print("❌ Ollama is not running")
            return False
    except FileNotFoundError:
        print("❌ Ollama is not installed")
        return False


def check_environment():
    """Check environment setup."""
    print_header("Checking Environment")

    # Check .env file
    if Path(".env").exists():
        print("✅ .env file exists")
    else:
        print("❌ .env file not found")
        return False

    # Check required directories
    required_dirs = ["base-ai-agent", "google-search-agent", "shared", "mcp-tools"]
    for dir_name in required_dirs:
        if Path(dir_name).exists():
            print(f"✅ {dir_name}/ directory exists")
        else:
            print(f"❌ {dir_name}/ directory not found")
            return False

    return True


def test_imports():
    """Test if critical imports work."""
    print_header("Testing Python Imports")

    try:
        # Test shared utilities
        from shared.utils import setup_logging

        print("✅ Shared utilities import successful")

        from shared.ollama_config import OllamaConfig

        print("✅ Ollama config import successful")

        from shared.memory_manager import MemoryManager

        print("✅ Memory manager import successful")

        # Test configuration using importlib to handle hyphens in directory names
        spec = importlib.util.spec_from_file_location(
            "config", Path.cwd() / "base-ai-agent" / "config.py"
        )
        config_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config_module)

        config = config_module.get_agent_config()
        print("✅ Base agent configuration loaded")

        return True

    except Exception as e:
        print(f"❌ Import error: {e}")
        return False


def main():
    """Main validation function."""
    print("🤖 AI Agents System Validation")
    print("Checking system requirements and setup...")

    checks = [
        check_python_version(),
        check_uv(),
        check_ollama(),
        check_environment(),
        test_imports(),
    ]

    passed = sum(checks)
    total = len(checks)

    print_header("Validation Summary")
    print(f"Passed: {passed}/{total} checks")

    if passed == total:
        print("✅ All checks passed! System is ready.")
        return True
    else:
        print("❌ Some checks failed. Please address the issues above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
