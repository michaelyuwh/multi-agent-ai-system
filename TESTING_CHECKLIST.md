# Quick Web UI Testing Checklist

## Before Testing
- [ ] Start both agents: `python start_agents.py`
- [ ] Verify web interface loads: http://localhost:8000
- [ ] Verify A2A server responds: http://localhost:8001/a2a/google_search_agent/.well-known/agent.json

## Essential Tests (5 minutes)

### ✅ Basic Functionality
- [ ] **Hello Test**: Send "Hello, how are you?" → Should get friendly response
- [ ] **Identity Test**: Send "What's your name?" → Should introduce as BaseAI
- [ ] **Capabilities Test**: Send "What can you do?" → Should mention memory and search

### ✅ Memory System
- [ ] **Memory Storage**: Send "My name is [YourName]" → Note response
- [ ] **Memory Recall**: Send "What's my name?" → Should recall correctly
- [ ] **Memory Search**: Send "What do you remember about me?" → Should list stored info

### ✅ Search Integration
- [ ] **Basic Search**: Send "Search for AI news" → Should delegate to search agent
- [ ] **Search Results**: Verify results include URLs and descriptions
- [ ] **Search Time**: Response should arrive within 30 seconds

## Quick Verification Tests (10 minutes)

### ✅ Advanced Features
- [ ] **Status Check**: Send "What's your status?" → Should show system info
- [ ] **Profile Check**: Send "What's my profile?" → Should show user info
- [ ] **Memory Clear**: Send "Clear my memory" → Should confirm clearing

### ✅ Error Handling
- [ ] **Long Message**: Send 500+ character message → Should handle gracefully
- [ ] **Special Characters**: Send "Test émojis 🤖 and unicode ∑" → Should display correctly

### ✅ Cross-Session Memory
- [ ] **Session 1**: Share some information
- [ ] **Close/Reopen**: Close browser, reopen http://localhost:8000
- [ ] **Session 2**: Ask "What did we discuss?" → Should remember previous session

## Automated Testing

Run automated tests:
```bash
# Install testing dependencies
uv add requests

# Run automated web UI tests
python test_web_ui.py

# Optional: Save results to file
python test_web_ui.py --save-results
```

## Test Scenarios by Role

### 🧑‍💼 Business User Tests
- [ ] Ask about company information
- [ ] Request market research
- [ ] Test document summarization requests

### 👨‍💻 Developer Tests
- [ ] Ask for coding help
- [ ] Request technical documentation searches
- [ ] Test API integration questions

### 🎓 Student Tests
- [ ] Ask for explanations of concepts
- [ ] Request research assistance
- [ ] Test study material searches

## Performance Benchmarks

Track these metrics during testing:

| Test Type | Expected Response Time | Actual Time | Status |
|-----------|----------------------|-------------|---------|
| Simple Chat | < 5 seconds | _____ | ⭕ |
| Memory Query | < 3 seconds | _____ | ⭕ |
| Search Request | < 30 seconds | _____ | ⭕ |
| Status Check | < 3 seconds | _____ | ⭕ |

## Common Issues & Solutions

### ❌ Web interface won't load
- **Check**: `python start_agents.py` running?
- **Check**: Port 8000 available?
- **Solution**: Restart agents or check for port conflicts

### ❌ Search not working
- **Check**: A2A server running on port 8001?
- **Check**: Google API keys in .env file?
- **Solution**: Verify search agent configuration

### ❌ Memory not working
- **Check**: `ENABLE_CROSS_SESSION_MEMORY=true` in .env?
- **Check**: `memory_data` directory exists?
- **Solution**: Check memory configuration

### ❌ Slow responses
- **Check**: System resource usage
- **Check**: Ollama model size vs RAM
- **Solution**: Use smaller model or increase resources

## Test Results Template

```
Date: _________ Time: _________
Tester: _________________
OS: ___________________
Browser: _______________

Basic Functionality: ✅ ❌
Memory System: ✅ ❌  
Search Integration: ✅ ❌
Advanced Features: ✅ ❌
Error Handling: ✅ ❌
Performance: ✅ ❌

Issues Found:
_________________________
_________________________

Overall Rating: ⭐⭐⭐⭐⭐
Notes:
_________________________
_________________________
```

## Quick Commands Reference

```bash
# Start system
python start_agents.py

# Test system health
python validate_setup.py

# Run automated tests
python test_web_ui.py

# Check service status
curl http://localhost:8000
curl http://localhost:8001/a2a/google_search_agent/.well-known/agent.json

# Stop system
# Ctrl+C in terminal running start_agents.py
```

---

For detailed testing scenarios, see [WEB_UI_TESTING.md](WEB_UI_TESTING.md)
