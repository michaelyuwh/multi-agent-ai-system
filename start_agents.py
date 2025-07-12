#!/usr/bin/env python3
# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Start script for both Base AI Agent and Google Search Agent."""

import os
import sys
import subprocess
import time
import signal
import threading
import platform
from pathlib import Path


def print_banner():
    """Print startup banner."""
    os_name = platform.system()
    banner = f"""
    ╔══════════════════════════════════════════════════════════════════════════════════════╗
    ║                                 AI Agent System                                      ║
    ║                                                                                      ║
    ║  🤖 Base AI Agent: Conversational AI with memory                                    ║
    ║  🔍 Google Search Agent: Web search capabilities                                    ║
    ║  🌐 Web Scraper Agent: Content extraction and summarization                        ║
    ║                                                                                      ║
    ║  OS: {os_name:<75} ║
    ║  Starting both agents for A2A communication...                                      ║
    ╚══════════════════════════════════════════════════════════════════════════════════════╝
    """
    print(banner)


def check_requirements():
    """Check if all requirements are met."""
    errors = []

    # Check if .env file exists
    if not Path(".env").exists():
        errors.append(".env file not found")

    # Check if UV is available
    try:
        subprocess.run(["uv", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        errors.append("UV is not installed or not available in PATH")

    # Check if Ollama is running (cross-platform)
    try:
        subprocess.run(["ollama", "list"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        errors.append("Ollama is not running or not available")

    return errors


def is_windows():
    """Check if running on Windows."""
    return platform.system() == "Windows"


def start_a2a_server():
    """Start the Google Search Agent A2A server."""
    print("🔍 Starting Google Search Agent A2A Server...")

    cmd = [
        "uv",
        "run",
        "python",
        "google-search-agent/a2a_server.py",
    ]

    # On Windows, we need to handle process creation differently
    if is_windows():
        return subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
        )
    else:
        return subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
        )


def start_web_scraper_agent():
    """Start the Web Scraper Agent A2A server."""
    print("🌐 Starting Web Scraper Agent A2A Server...")

    cmd = [
        "uv",
        "run",
        "python",
        "web-scraper-agent/a2a_server.py",
    ]

    # On Windows, we need to handle process creation differently
    if is_windows():
        return subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
        )
    else:
        return subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
        )


def start_web_interface():
    """Start the Base AI Agent web interface."""
    print("🌐 Starting Base AI Agent Web Interface...")

    cmd = [
        "uv",
        "run",
        "adk",
        "web",
        "--port",
        "8000",
        "--host",
        "127.0.0.1",
    ]

    # On Windows, we need to handle process creation differently
    if is_windows():
        return subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
        )
    else:
        return subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
        )


def monitor_process(process, name):
    """Monitor a process and print its output."""
    try:
        for line in process.stdout:
            print(f"[{name}] {line.strip()}")
    except Exception:
        pass


def main():
    """Main entry point."""
    print_banner()

    # Check requirements
    errors = check_requirements()
    if errors:
        print("❌ Requirements check failed:")
        for error in errors:
            print(f"   - {error}")
        print("\nPlease fix the issues above and try again.")
        sys.exit(1)

    print("✅ Requirements check passed!")
    print("\nStarting AI Agent System...")

    # Change to script directory
    os.chdir(Path(__file__).parent)

    processes = []

    try:
        # Start A2A server first
        a2a_process = start_a2a_server()
        processes.append(("Google Search Agent", a2a_process))

        # Wait a bit for A2A server to start
        time.sleep(3)

        # Start web scraper agent
        scraper_process = start_web_scraper_agent()
        processes.append(("Web Scraper Agent", scraper_process))

        # Wait a bit for web scraper agent to start
        time.sleep(3)

        # Start web interface
        web_process = start_web_interface()
        processes.append(("Web Interface", web_process))

        # Start monitoring threads
        threads = []
        for name, process in processes:
            thread = threading.Thread(target=monitor_process, args=(process, name))
            thread.daemon = True
            thread.start()
            threads.append(thread)

        print("\n🎉 All agents are starting up!")
        print("\n📋 Service URLs:")
        print("   🌐 Web Interface: http://localhost:8000")
        print("   🔍 Google Search Agent: http://localhost:8001")
        print("   🌐 Web Scraper Agent: http://localhost:8002")
        print("   📋 Search Agent JSON: http://localhost:8001/.well-known/agent.json")
        print("   📋 Scraper Agent JSON: http://localhost:8002/.well-known/agent.json")
        print(
            "\n💡 Enhanced Search Features:"
        )
        print("   • Simple search: 'Search Google for Python tutorials'")
        print("   • Search + scraping: 'Search for latest AI developments and summarize'")
        print("   • The base agent can delegate to both search and scraping agents!")
        print("\n⏹️  Press Ctrl+C to stop all services")

        # Cross-platform signal handling
        if is_windows():
            # On Windows, we use a different approach
            try:
                while True:
                    time.sleep(1)
                    # Check if processes are still running
                    if not any(p.poll() is None for _, p in processes):
                        break
            except KeyboardInterrupt:
                pass
        else:
            # Unix-style signal handling
            signal.signal(signal.SIGINT, lambda s, f: None)
            signal.pause()

    except KeyboardInterrupt:
        print("\n\n🛑 Stopping services...")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        # Terminate all processes (cross-platform)
        for name, process in processes:
            try:
                if is_windows():
                    # On Windows, use terminate() followed by kill() if needed
                    process.terminate()
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        process.kill()
                else:
                    # On Unix, use terminate()
                    process.terminate()
                print(f"   ✅ Stopped {name}")
            except Exception as e:
                print(f"   ⚠️  Error stopping {name}: {e}")

        print("👋 All services stopped. Goodbye!")


if __name__ == "__main__":
    main()
