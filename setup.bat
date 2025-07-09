@echo off
REM Copyright 2025 Google LLC
REM
REM Licensed under the Apache License, Version 2.0 (the "License");
REM you may not use this file except in compliance with the License.
REM You may obtain a copy of the License at
REM
REM     http://www.apache.org/licenses/LICENSE-2.0
REM
REM Unless required by applicable law or agreed to in writing, software
REM distributed under the License is distributed on an "AS IS" BASIS,
REM WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
REM See the License for the specific language governing permissions and
REM limitations under the License.

REM AI Agents Setup Script for Windows
REM This script sets up the AI agents system on Windows

setlocal enabledelayedexpansion

echo 🤖 AI Agents Setup Script (Windows)
echo ===================================
echo.

REM Function to print colored output (basic Windows version)
echo [INFO] Detected OS: Windows

REM Check if UV is installed
echo [INFO] Checking UV installation...
uv --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ UV is already installed
    for /f "tokens=*" %%i in ('uv --version') do echo    %%i
) else (
    echo [INFO] Installing UV...
    echo Please install UV manually from: https://github.com/astral-sh/uv
    echo Or use PowerShell: irm https://astral.sh/uv/install.ps1 ^| iex
    echo.
    echo After installing UV, please run this script again.
    pause
    exit /b 1
)

REM Check if Ollama is installed
echo [INFO] Checking Ollama installation...
ollama --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Ollama is already installed
) else (
    echo [INFO] Installing Ollama...
    echo Please install Ollama manually from: https://ollama.ai/
    echo.
    echo After installing Ollama, please run this script again.
    pause
    exit /b 1
)

REM Check if Ollama service is running
echo [INFO] Checking Ollama service...
tasklist /fi "imagename eq ollama.exe" 2>nul | find /i "ollama.exe" >nul
if %errorlevel% equ 0 (
    echo ✅ Ollama service is running
) else (
    echo [INFO] Starting Ollama service...
    start "" ollama serve
    timeout /t 3 /nobreak >nul
)

REM Check if Ollama is responding
ollama list >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Ollama service is responding
) else (
    echo ❌ Ollama service is not responding
    echo ⚠️  You may need to start Ollama manually
    echo    Run: ollama serve
)

REM Install recommended model
echo [INFO] Checking for recommended models...
ollama list | findstr /i "mistral-small:7b" >nul
if %errorlevel% equ 0 (
    echo ✅ mistral-small:7b is already installed
    goto :dependencies
)

ollama list | findstr /i "llama3.1:8b" >nul
if %errorlevel% equ 0 (
    echo ✅ llama3.1:8b is already installed
    goto :dependencies
)

echo [INFO] Installing recommended model: mistral-small:7b
echo ⚠️  This may take a few minutes depending on your internet connection...
ollama pull mistral-small:7b
if %errorlevel% equ 0 (
    echo ✅ Model installed successfully
) else (
    echo ❌ Failed to install model
)

:dependencies
REM Install Python dependencies
echo [INFO] Installing Python dependencies...
if exist pyproject.toml (
    uv add google-adk
    uv add litellm
    uv add "google-adk[a2a]"
    uv add python-dotenv
    echo ✅ Dependencies installed successfully
) else (
    echo ❌ pyproject.toml not found. Are you in the correct directory?
    pause
    exit /b 1
)

REM Create .env file if it doesn't exist
if not exist .env (
    echo [INFO] Creating .env file...
    (
        echo # Environment Configuration for AI Agents
        echo.
        echo # Ollama Configuration
        echo OLLAMA_API_BASE=http://localhost:11434
        echo.
        echo # Default model for the base AI agent
        echo DEFAULT_MODEL=ollama_chat/mistral-small:7b
        echo.
        echo # ADK Configuration
        echo LOG_LEVEL=INFO
        echo ADK_WEB_PORT=8000
        echo ADK_A2A_PORT=8001
        echo.
        echo # Memory Configuration
        echo MEMORY_MAX_HISTORY=100
        echo MEMORY_SEARCH_THRESHOLD=0.7
        echo SESSION_TIMEOUT=3600
        echo ENABLE_CROSS_SESSION_MEMORY=true
        echo.
        echo # Model Configuration
        echo MODEL_TEMPERATURE=0.7
        echo MODEL_MAX_TOKENS=2048
        echo MODEL_CONTEXT_WINDOW=8192
        echo.
        echo # MCP Configuration ^(Future Feature^)
        echo ENABLE_MCP=false
        echo.
        echo # Google Search Agent Configuration ^(A2A^)
        echo GOOGLE_SEARCH_AGENT_HOST=localhost
        echo GOOGLE_SEARCH_AGENT_PORT=8001
        echo GOOGLE_SEARCH_AGENT_DEBUG=false
        echo GOOGLE_SEARCH_AGENT_MODEL=gemini-2.0-flash-001
        echo MAX_SEARCH_RESULTS=10
        echo SEARCH_TIMEOUT=30
        echo.
        echo # Google Search API Configuration ^(Required for google-search-agent^)
        echo # Get these from: https://developers.google.com/custom-search/v1/overview
        echo GOOGLE_SEARCH_API_KEY=your_google_api_key_here
        echo GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id_here
        echo.
        echo # Development Settings
        echo DEVELOPMENT_MODE=true
        echo AUTO_RELOAD=true
    ) > .env
    echo ✅ .env file created
) else (
    echo ✅ .env file already exists
)

REM Run validation
echo [INFO] Validating setup...
python validate_setup.py
if %errorlevel% equ 0 (
    echo ✅ Setup validation passed!
) else (
    echo ⚠️  Some validation checks failed, but you can still proceed
)

REM Final instructions
echo.
echo 🎉 Setup completed!
echo.
echo Next steps:
echo 1. Configure Google Search API ^(optional^):
echo    - Get API key from: https://developers.google.com/custom-search/v1/overview
echo    - Update GOOGLE_SEARCH_API_KEY and GOOGLE_SEARCH_ENGINE_ID in .env
echo.
echo 2. Start the AI agents:
echo    python start_agents.py
echo.
echo 3. Open web interface:
echo    http://localhost:8000
echo.
echo 4. Test the system:
echo    - Try basic chat: 'Hello, how are you?'
echo    - Test search: 'Search for information about artificial intelligence'
echo.
echo ✅ Happy agent building! 🚀
echo.
pause
