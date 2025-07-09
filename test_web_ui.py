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

"""Automated Web UI Testing Script for AI Agents."""

import requests
import time
import json
import sys
from datetime import datetime
from typing import Dict, Any, Optional


class WebUITester:
    """Automated tester for the AI Agents web UI."""

    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        a2a_url: str = "http://localhost:8001",
    ):
        self.base_url = base_url
        self.a2a_url = a2a_url
        self.test_results = []
        self.session = requests.Session()

    def log_test(
        self, test_name: str, status: str, details: str = "", response_time: float = 0
    ):
        """Log test results."""
        result = {
            "test_name": test_name,
            "status": status,
            "details": details,
            "response_time": response_time,
            "timestamp": datetime.now().isoformat(),
        }
        self.test_results.append(result)

        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_icon} {test_name}: {status}")
        if details:
            print(f"   {details}")
        if response_time > 0:
            print(f"   Response time: {response_time:.2f}s")

    def test_web_interface_accessibility(self):
        """Test if web interface is accessible."""
        try:
            start_time = time.time()
            response = self.session.get(self.base_url, timeout=10)
            response_time = time.time() - start_time

            if response.status_code == 200:
                self.log_test(
                    "Web Interface Accessibility",
                    "PASS",
                    f"Status: {response.status_code}",
                    response_time,
                )
                return True
            else:
                self.log_test(
                    "Web Interface Accessibility",
                    "FAIL",
                    f"Status: {response.status_code}",
                    response_time,
                )
                return False

        except Exception as e:
            self.log_test("Web Interface Accessibility", "FAIL", f"Error: {e}")
            return False

    def test_a2a_server_accessibility(self):
        """Test if A2A server is accessible."""
        try:
            start_time = time.time()
            response = self.session.get(
                f"{self.a2a_url}/a2a/google_search_agent/.well-known/agent.json",
                timeout=10,
            )
            response_time = time.time() - start_time

            if response.status_code == 200:
                try:
                    agent_info = response.json()
                    agent_name = agent_info.get("name", "Unknown")
                    self.log_test(
                        "A2A Server Accessibility",
                        "PASS",
                        f"Agent: {agent_name}",
                        response_time,
                    )
                    return True
                except json.JSONDecodeError:
                    self.log_test(
                        "A2A Server Accessibility",
                        "FAIL",
                        "Invalid JSON response",
                        response_time,
                    )
                    return False
            else:
                self.log_test(
                    "A2A Server Accessibility",
                    "FAIL",
                    f"Status: {response.status_code}",
                    response_time,
                )
                return False

        except Exception as e:
            self.log_test("A2A Server Accessibility", "FAIL", f"Error: {e}")
            return False

    def simulate_chat_request(self, message: str, timeout: int = 30) -> Optional[str]:
        """Simulate a chat request to the web interface."""
        # This is a simplified simulation - actual implementation would depend on the web UI framework
        # For now, we'll just test if the endpoint is responsive
        try:
            start_time = time.time()

            # Try to find API endpoint - this may vary based on implementation
            test_endpoints = [
                f"{self.base_url}/api/chat",
                f"{self.base_url}/chat",
                f"{self.base_url}/api/message",
            ]

            for endpoint in test_endpoints:
                try:
                    response = self.session.post(
                        endpoint, json={"message": message}, timeout=timeout
                    )
                    response_time = time.time() - start_time

                    if response.status_code == 200:
                        return response.text
                    elif response.status_code == 404:
                        continue  # Try next endpoint
                    else:
                        self.log_test(
                            f"Chat Test: {message[:30]}...",
                            "FAIL",
                            f"Status: {response.status_code}",
                            response_time,
                        )
                        return None

                except requests.exceptions.RequestException:
                    continue

            # If no endpoints work, log as warning (may need manual testing)
            self.log_test(
                f"Chat Test: {message[:30]}...",
                "WARN",
                "No API endpoint found - requires manual testing",
            )
            return None

        except Exception as e:
            self.log_test(f"Chat Test: {message[:30]}...", "FAIL", f"Error: {e}")
            return None

    def test_basic_chat_functionality(self):
        """Test basic chat functionality."""
        test_messages = ["Hello, how are you?", "What's your name?", "What can you do?"]

        for message in test_messages:
            response = self.simulate_chat_request(message)
            if response:
                self.log_test(f"Basic Chat: {message}", "PASS", "Response received")
            else:
                self.log_test(
                    f"Basic Chat: {message}", "WARN", "Manual testing required"
                )

    def test_search_functionality(self):
        """Test search functionality."""
        search_message = "Search for information about artificial intelligence"
        response = self.simulate_chat_request(search_message, timeout=45)

        if response:
            self.log_test("Search Functionality", "PASS", "Search response received")
        else:
            self.log_test("Search Functionality", "WARN", "Manual testing required")

    def test_system_health(self):
        """Test overall system health."""
        health_checks = [
            ("Web Interface", self.test_web_interface_accessibility),
            ("A2A Server", self.test_a2a_server_accessibility),
        ]

        healthy_services = 0
        for service_name, check_func in health_checks:
            if check_func():
                healthy_services += 1

        if healthy_services == len(health_checks):
            self.log_test("System Health", "PASS", "All services healthy")
        elif healthy_services > 0:
            self.log_test(
                "System Health",
                "WARN",
                f"{healthy_services}/{len(health_checks)} services healthy",
            )
        else:
            self.log_test("System Health", "FAIL", "No services responding")

    def run_all_tests(self):
        """Run all automated tests."""
        print("🤖 AI Agents Web UI Automated Testing")
        print("=" * 40)
        print(f"Testing Base URL: {self.base_url}")
        print(f"Testing A2A URL: {self.a2a_url}")
        print(f"Started at: {datetime.now()}")
        print()

        # Core system tests
        self.test_system_health()

        # Basic functionality tests
        self.test_basic_chat_functionality()

        # Advanced functionality tests
        self.test_search_functionality()

        # Generate summary
        self.print_summary()

    def print_summary(self):
        """Print test summary."""
        print("\n" + "=" * 40)
        print("TEST SUMMARY")
        print("=" * 40)

        pass_count = sum(1 for r in self.test_results if r["status"] == "PASS")
        fail_count = sum(1 for r in self.test_results if r["status"] == "FAIL")
        warn_count = sum(1 for r in self.test_results if r["status"] == "WARN")
        total_count = len(self.test_results)

        print(f"Total Tests: {total_count}")
        print(f"✅ Passed: {pass_count}")
        print(f"❌ Failed: {fail_count}")
        print(f"⚠️  Warnings: {warn_count}")

        if fail_count > 0:
            print("\nFAILED TESTS:")
            for result in self.test_results:
                if result["status"] == "FAIL":
                    print(f"  - {result['test_name']}: {result['details']}")

        if warn_count > 0:
            print("\nWARNINGS:")
            for result in self.test_results:
                if result["status"] == "WARN":
                    print(f"  - {result['test_name']}: {result['details']}")

        print(f"\nCompleted at: {datetime.now()}")

        # Recommendations
        print("\nRECOMMENDATIONS:")
        if fail_count > 0:
            print("- Check that both agents are running: python start_agents.py")
            print("- Verify ports 8000 and 8001 are available")
            print("- Check system requirements: python validate_setup.py")

        if warn_count > 0:
            print("- Some tests require manual verification via web interface")
            print("- See WEB_UI_TESTING.md for detailed manual testing scenarios")

        if pass_count == total_count:
            print("- All automated tests passed! System appears healthy.")
            print(
                "- For comprehensive testing, run manual tests from WEB_UI_TESTING.md"
            )

    def save_results(self, filename: str = "test_results.json"):
        """Save test results to JSON file."""
        with open(filename, "w") as f:
            json.dump(self.test_results, f, indent=2)
        print(f"\nTest results saved to: {filename}")


def main():
    """Main function."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Automated Web UI Testing for AI Agents"
    )
    parser.add_argument(
        "--base-url", default="http://localhost:8000", help="Base URL for web interface"
    )
    parser.add_argument(
        "--a2a-url", default="http://localhost:8001", help="A2A server URL"
    )
    parser.add_argument(
        "--save-results", action="store_true", help="Save results to JSON file"
    )

    args = parser.parse_args()

    # Create tester and run tests
    tester = WebUITester(args.base_url, args.a2a_url)
    tester.run_all_tests()

    if args.save_results:
        tester.save_results()

    # Exit with appropriate code
    fail_count = sum(1 for r in tester.test_results if r["status"] == "FAIL")
    sys.exit(1 if fail_count > 0 else 0)


if __name__ == "__main__":
    main()
