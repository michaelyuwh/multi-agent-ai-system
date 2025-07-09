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

# AI Agents Setup Script for Windows (PowerShell)
# This script sets up the AI agents system on Windows using PowerShell

param(
    [switch]$Force = $false
)

# Set error action preference
$ErrorActionPreference = "Stop"

# Function to print colored output
function Write-Status {
    param([string]$Message)
    Write-Host "ℹ️  $Message" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Error {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor Red
}

function Write-Warning {
    param([string]$Message)
    Write-Host "⚠️  $Message" -ForegroundColor Yellow
}

# Function to check if command exists
function Test-CommandExists {
    param([string]$Command)
    try {
        Get-Command $Command -ErrorAction Stop | Out-Null
        return $true
    }
    catch {
        return $false
    }
}

# Function to install UV
function Install-UV {
    Write-Status "Installing UV..."
    try {
        irm https://astral.sh/uv/install.ps1 | iex
        # Refresh PATH
        $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH", "User")
        Write-Success "UV installed successfully"
        return $true
    }
    catch {
        Write-Error "Failed to install UV: $_"
        Write-Warning "Please install UV manually from: https://github.com/astral-sh/uv"
        return $false
    }
}

# Function to install Ollama
function Install-Ollama {
    Write-Status "Installing Ollama..."
    try {
        # Download and install Ollama
        $ollamaUrl = "https://ollama.ai/download/windows"
        Write-Status "Please download and install Ollama from: $ollamaUrl"
        Write-Warning "After installation, please restart this script"
        Start-Process $ollamaUrl
        return $false
    }
    catch {
        Write-Error "Failed to start Ollama download: $_"
        return $false
    }
}

# Main script
Write-Host "🤖 AI Agents Setup Script (PowerShell)" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

Write-Status "Detected OS: Windows (PowerShell)"

# Check and install UV
Write-Status "Checking UV installation..."
if (Test-CommandExists "uv") {
    $uvVersion = uv --version
    Write-Success "UV is already installed: $uvVersion"
}
else {
    if (-not (Install-UV)) {
        exit 1
    }
}

# Check and install Ollama
Write-Status "Checking Ollama installation..."
if (Test-CommandExists "ollama") {
    Write-Success "Ollama is already installed"
}
else {
    if (-not (Install-Ollama)) {
        exit 1
    }
}

# Check if Ollama service is running
Write-Status "Checking Ollama service..."
$ollamaProcess = Get-Process -Name "ollama" -ErrorAction SilentlyContinue
if ($ollamaProcess) {
    Write-Success "Ollama service is running"
}
else {
    Write-Status "Starting Ollama service..."
    try {
        Start-Process -FilePath "ollama" -ArgumentList "serve" -WindowStyle Hidden
        Start-Sleep -Seconds 3
        Write-Success "Ollama service started"
    }
    catch {
        Write-Warning "Could not start Ollama service automatically. Please run 'ollama serve' manually."
    }
}

# Check if Ollama is responding
Write-Status "Checking Ollama connectivity..."
try {
    $null = ollama list 2>$null
    Write-Success "Ollama service is responding"
}
catch {
    Write-Error "Ollama service is not responding"
    Write-Warning "You may need to start Ollama manually: 'ollama serve'"
}

# Install recommended model
Write-Status "Checking for recommended models..."
$ollamaModels = ollama list 2>$null
if ($ollamaModels -match "mistral-small:7b") {
    Write-Success "mistral-small:7b is already installed"
}
elseif ($ollamaModels -match "llama3.1:8b") {
    Write-Success "llama3.1:8b is already installed"
}
else {
    Write-Status "Installing recommended model: mistral-small:7b"
    Write-Warning "This may take a few minutes depending on your internet connection..."
    try {
        ollama pull mistral-small:7b
        Write-Success "Model installed successfully"
    }
    catch {
        Write-Error "Failed to install model: $_"
    }
}

# Install Python dependencies
Write-Status "Installing Python dependencies..."
if (Test-Path "pyproject.toml") {
    try {
        uv add google-adk
        uv add litellm
        uv add "google-adk[a2a]"
        uv add python-dotenv
        Write-Success "Dependencies installed successfully"
    }
    catch {
        Write-Error "Failed to install dependencies: $_"
        exit 1
    }
}
else {
    Write-Error "pyproject.toml not found. Are you in the correct directory?"
    exit 1
}

# Create .env file if it doesn't exist
if (-not (Test-Path ".env")) {
    Write-Status "Creating .env file..."
    $envContent = @"
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
"@
    $envContent | Out-File -FilePath ".env" -Encoding UTF8
    Write-Success ".env file created"
}
else {
    Write-Success ".env file already exists"
}

# Run validation
Write-Status "Validating setup..."
try {
    python validate_setup.py
    Write-Success "Setup validation passed!"
}
catch {
    Write-Warning "Some validation checks failed, but you can still proceed"
}

# Final instructions
Write-Host ""
Write-Host "🎉 Setup completed!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:"
Write-Host "1. Configure Google Search API (optional):"
Write-Host "   - Get API key from: https://developers.google.com/custom-search/v1/overview"
Write-Host "   - Update GOOGLE_SEARCH_API_KEY and GOOGLE_SEARCH_ENGINE_ID in .env"
Write-Host ""
Write-Host "2. Start the AI agents:"
Write-Host "   python start_agents.py"
Write-Host ""
Write-Host "3. Open web interface:"
Write-Host "   http://localhost:8000"
Write-Host ""
Write-Host "4. Test the system:"
Write-Host "   - Try basic chat: 'Hello, how are you?'"
Write-Host "   - Test search: 'Search for information about artificial intelligence'"
Write-Host ""
Write-Success "Happy agent building! 🚀"
