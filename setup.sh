#!/bin/bash
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

# AI Agents Setup Script
# This script sets up the AI agents system on a new machine

set -e  # Exit on any error

echo "🤖 AI Agents Setup Script"
echo "=========================="
echo

# Function to print colored output
print_status() {
    echo -e "\033[1;34m$1\033[0m"
}

print_success() {
    echo -e "\033[1;32m✅ $1\033[0m"
}

print_error() {
    echo -e "\033[1;31m❌ $1\033[0m"
}

print_warning() {
    echo -e "\033[1;33m⚠️  $1\033[0m"
}

# Check if running on macOS or Linux
OS_TYPE=$(uname -s)
print_status "Detected OS: $OS_TYPE"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check and install UV
print_status "Checking UV installation..."
if command_exists uv; then
    print_success "UV is already installed: $(uv --version)"
else
    print_status "Installing UV..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
    if command_exists uv; then
        print_success "UV installed successfully"
    else
        print_error "Failed to install UV"
        exit 1
    fi
fi

# Check and install Ollama
print_status "Checking Ollama installation..."
if command_exists ollama; then
    print_success "Ollama is already installed"
else
    print_status "Installing Ollama..."
    curl -fsSL https://ollama.ai/install.sh | sh
    print_success "Ollama installed successfully"
fi

# Start Ollama service (if not running)
print_status "Checking Ollama service..."
if ! pgrep -f "ollama serve" > /dev/null; then
    print_status "Starting Ollama service..."
    if [[ "$OS_TYPE" == "Darwin" ]]; then
        # macOS
        nohup ollama serve > /dev/null 2>&1 &
    else
        # Linux
        systemctl --user start ollama 2>/dev/null || {
            nohup ollama serve > /dev/null 2>&1 &
        }
    fi
    sleep 3
fi

# Check if Ollama is responding
if ollama list > /dev/null 2>&1; then
    print_success "Ollama service is running"
else
    print_error "Ollama service is not responding"
    print_warning "You may need to start Ollama manually: 'ollama serve'"
fi

# Install recommended model
print_status "Checking for recommended models..."
if ollama list | grep -q "mistral-small:7b"; then
    print_success "mistral-small:7b is already installed"
elif ollama list | grep -q "llama3.1:8b"; then
    print_success "llama3.1:8b is already installed"
else
    print_status "Installing recommended model: mistral-small:7b"
    print_warning "This may take a few minutes depending on your internet connection..."
    ollama pull mistral-small:7b
    print_success "Model installed successfully"
fi

# Install Python dependencies
print_status "Installing Python dependencies..."
if [ -f "pyproject.toml" ]; then
    uv add google-adk
    uv add litellm
    uv add "google-adk[a2a]"
    uv add python-dotenv
    print_success "Dependencies installed successfully"
else
    print_error "pyproject.toml not found. Are you in the correct directory?"
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    print_status "Creating .env file..."
    cat > .env << EOF
# Environment Configuration for AI Agents

# Ollama Configuration
OLLAMA_API_BASE=http://localhost:11434

# Default model for the base AI agent
DEFAULT_MODEL=ollama_chat/mistral-small:7b

# ADK Configuration
LOG_LEVEL=INFO
ADK_WEB_PORT=8000
ADK_A2A_PORT=8001

# Memory Configuration
MEMORY_MAX_HISTORY=100
MEMORY_SEARCH_THRESHOLD=0.7
SESSION_TIMEOUT=3600
ENABLE_CROSS_SESSION_MEMORY=true

# Model Configuration
MODEL_TEMPERATURE=0.7
MODEL_MAX_TOKENS=2048
MODEL_CONTEXT_WINDOW=8192

# MCP Configuration (Future Feature)
ENABLE_MCP=false

# Google Search Agent Configuration (A2A)
GOOGLE_SEARCH_AGENT_HOST=localhost
GOOGLE_SEARCH_AGENT_PORT=8001
GOOGLE_SEARCH_AGENT_DEBUG=false
GOOGLE_SEARCH_AGENT_MODEL=gemini-2.0-flash-001
MAX_SEARCH_RESULTS=10
SEARCH_TIMEOUT=30

# Google Search API Configuration (Required for google-search-agent)
# Get these from: https://developers.google.com/custom-search/v1/overview
GOOGLE_SEARCH_API_KEY=your_google_api_key_here
GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id_here

# Development Settings
DEVELOPMENT_MODE=true
AUTO_RELOAD=true
EOF
    print_success ".env file created"
else
    print_success ".env file already exists"
fi

# Run validation
print_status "Validating setup..."
if python validate_setup.py; then
    print_success "Setup validation passed!"
else
    print_warning "Some validation checks failed, but you can still proceed"
fi

# Final instructions
echo
echo "🎉 Setup completed!"
echo
echo "Next steps:"
echo "1. Configure Google Search API (optional):"
echo "   - Get API key from: https://developers.google.com/custom-search/v1/overview"
echo "   - Update GOOGLE_SEARCH_API_KEY and GOOGLE_SEARCH_ENGINE_ID in .env"
echo
echo "2. Start the AI agents:"
echo "   python start_agents.py"
echo
echo "3. Open web interface:"
echo "   http://localhost:8000"
echo
echo "4. Test the system:"
echo "   - Try basic chat: 'Hello, how are you?'"
echo "   - Test search: 'Search for information about artificial intelligence'"
echo
print_success "Happy agent building! 🚀"
