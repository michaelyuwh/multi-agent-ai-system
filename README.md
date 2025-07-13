# Cross-Platform Multi-Agent AI System with Google ADK

A sophisticated multi-agent AI system built with Google ADK featuring Agent-to-Agent (A2A) communication. The system includes a conversational base AI agent (using Ollama locally) and a specialized Google Search Agent that communicate via the A2A protocol.

## 🌟 Features

- **Multi-Agent Architecture**: Base AI agent with Google Search and Web Scraper Agent delegation
- **A2A Protocol Communication**: True agent-to-agent communication using A2A standard
- **Local AI Processing**: Uses Ollama for local conversation handling
- **Web Search Capabilities**: Google Custom Search integration via dedicated search agent
- **Intelligent Web Scraping**: Content extraction and AI-powered summarization
- **Cross-Platform Support**: Works on macOS and Windows
- **Modern Web Interface**: Beautiful UI for agent interaction
- **Memory Management**: Persistent conversation memory
- **Streaming Responses**: Real-time response streaming

## 🏗️ System Architecture

```
┌─────────────────┐     A2A       ┌──────────────────┐     A2A       ┌──────────────────┐
│   Base AI Agent │ ◄──────────► │ Google Search    │ ◄──────────► │ Web Scraper      │
│   (Ollama)      │               │ Agent (Port 8001)│               │ Agent (Port 8002)│
└─────────────────┘               └──────────────────┘               └──────────────────┘
         │                                                                     │
         │                                                                     │
    Web Interface                                                        Content Analysis
    (Port 8000)                                                            & Summarization
```

### Components

1. **Base AI Agent**
   - Conversational AI using Ollama (llama3.1:8b)
   - Handles general queries, coding help, explanations
   - Delegates search requests via A2A protocol
   - Enhanced with web scraping capabilities
   - Web interface for user interaction

2. **Google Search Agent**
   - Specialized agent for web searches
   - Uses Google Custom Search API
   - Gemini model for result processing
   - Exposes A2A server endpoints
   - Provides URLs for content scraping

3. **Web Scraper Agent** ✨ NEW
   - Intelligent web content extraction
   - Multi-URL scraping capabilities
   - AI-powered content summarization
   - Content cleaning and analysis
   - A2A server on port 8002

4. **A2A Communication Layer**
   - Standards-compliant Agent-to-Agent protocol
   - Secure inter-agent communication
   - Agent discovery via agent cards

## 🚀 Quick Start

### Prerequisites

- **Python 3.13+**
- **uv** (Python package manager)
- **Ollama** with llama3.1:8b model
- **Google API credentials** (for search functionality)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/michaelyuwh/multi-agent-ai-system.git
   cd multi-agent-ai-system
   ```

2. **Install dependencies**
   ```bash
   uv sync
   ```

3. **Set up Ollama**
   ```bash
   # Install Ollama (if not already installed)
   curl -fsSL https://ollama.com/install.sh | sh
   
   # Pull the required model
   ollama pull llama3.1:8b
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your Google API credentials
   ```

5. **Start the system**
   ```bash
   uv run python start_agents.py
   ```

6. **Access the web interface**
   - Open http://localhost:8000 in your browser
   - Start chatting with the AI agent!

## ⚙️ Configuration

### Environment Variables

Create a `.env` file with the following configuration:

```bash
# Google Search API Configuration
GOOGLE_SEARCH_API_KEY=your_api_key_here
GOOGLE_SEARCH_ENGINE_ID=your_engine_id_here

# Agent Configuration
GOOGLE_SEARCH_AGENT_URL=http://localhost:8001
MODEL_TEMPERATURE=0.7
MAX_SEARCH_RESULTS=10

# Memory Configuration
MEMORY_MAX_HISTORY=100
SESSION_TIMEOUT=3600
```

### Getting Google API Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable the "Custom Search API"
4. Create credentials (API Key)
5. Set up a Custom Search Engine at [Google CSE](https://cse.google.com/)

## 📖 Usage

### Basic Conversation
```
User: Hello, how are you?
Agent: Hello! I'm doing well, thank you for asking. I'm here to help you with any questions or tasks you might have...
```

### Web Search (A2A Delegation)
```
User: Search Google for Python tutorials
Agent: 🔍 Search Results for 'Python tutorials':

Based on current web search results:
1. **Learn Python - Python.org**
   - Official Python tutorial and documentation
   - https://docs.python.org/3/tutorial/
   ...
```

### Enhanced Search with Web Scraping ✨ NEW
```
User: Search for latest AI developments and give me a detailed summary
Agent: 🔍 Search Results for 'latest AI developments':

[Search results with links]

🌐 **Detailed Content Analysis:**

Based on comprehensive analysis of scraped content:

**Overview of Main Topics:**
- Advanced reasoning capabilities in large language models
- Breakthrough in multimodal AI systems combining text, image, and video
- New developments in AI safety and alignment research

**Key Insights:**
1. **GPT-4 and Beyond**: Recent improvements show significant advances in reasoning...
2. **Multimodal Integration**: New models can now seamlessly process and generate...
3. **Safety Research**: Major progress in AI alignment and controllability...

**Sources:**
1. [Recent AI Breakthroughs in 2025](https://example.com/ai-news)
2. [Multimodal AI Systems](https://example.com/multimodal)
3. [AI Safety Progress](https://example.com/safety)
```

## 🛠️ Development

### Project Structure

```
ai-agents/
├── base-ai-agent/          # Main conversational agent
│   ├── agent.py           # Agent with search and scraping tools
│   └── config.py          # Configuration
├── google-search-agent/    # Search specialist agent
│   ├── a2a_server.py      # A2A server implementation
│   ├── search_agent_executor.py
│   └── agent.py
├── web-scraper-agent/      # Web scraping specialist agent ✨ NEW
│   ├── a2a_server.py      # A2A server implementation
│   ├── scraper_agent_executor.py
│   └── agent.py
├── shared/                 # Shared utilities
│   ├── memory_manager.py
│   ├── ollama_config.py
│   └── utils.py
├── start_agents.py         # Main startup script (3 agents)
├── pyproject.toml         # Project configuration
└── README.md              # This file
```

### Running Individual Components

**Base AI Agent only:**
```bash
cd base-ai-agent
uv run adk web --port 8000 .
```

**Google Search Agent only:**
```bash
cd google-search-agent
uv run python a2a_server.py
```

**Web Scraper Agent only:**
```bash
cd web-scraper-agent
uv run python a2a_server.py
```

### Testing

```bash
# Run all tests
uv run pytest

# Test web interface
uv run python test_web_ui.py

# Validate setup
uv run python validate_setup.py
```

## 🔧 Troubleshooting

### Common Issues

1. **"Failed to load agents" in web interface**
   - Ensure you're running from the project root directory
   - Check that `agent.py` files contain `root_agent` definitions

2. **A2A communication errors**
   - Verify Google Search Agent is running on port 8001
   - Verify Web Scraper Agent is running on port 8002
   - Check that `.env` has correct agent URLs

3. **Ollama connection issues**
   - Ensure Ollama is running: `ollama serve`
   - Verify model is available: `ollama list`

4. **Google Search API errors**
   - Verify API key and Search Engine ID in `.env`
   - Check API quotas in Google Cloud Console

5. **Web scraping errors**
   - Check that target URLs are accessible
   - Verify scraper agent is running on port 8002
   - Some sites may block scraping attempts

### Logs and Debugging

- Check agent logs in the terminal output
- Enable debug mode: Set `GOOGLE_SEARCH_AGENT_DEBUG=true` in `.env`
- Use `--reload` flag for development: `uv run adk web --reload`

## 🚀 Deployment

### Production Considerations

- Use proper secret management for API keys
- Configure reverse proxy (nginx) for production
- Set up monitoring and logging
- Consider rate limiting for API endpoints

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make changes and test thoroughly
4. Submit a pull request

## 📋 Testing Checklist

- [ ] Basic conversation works without search
- [ ] Simple search delegation works via A2A
- [ ] Enhanced search with scraping works
- [ ] All three agents start successfully
- [ ] Web interface loads properly
- [ ] Cross-platform compatibility (macOS/Windows)

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Google ADK](https://github.com/google/adk) - Agent Development Kit
- [A2A Protocol](https://github.com/a2aproject/A2A) - Agent-to-Agent communication standard
- [Ollama](https://ollama.com/) - Local LLM serving
- The open-source AI community

## 📞 Support

- 📧 Issues: [GitHub Issues](https://github.com/michaelyuwh/multi-agent-ai-system/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/michaelyuwh/multi-agent-ai-system/discussions)

---

**Built with ❤️ using Google ADK and A2A Protocol**
