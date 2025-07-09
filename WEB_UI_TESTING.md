# Web UI Testing Guide for AI Agents

This guide provides comprehensive testing scenarios for the AI Agents web interface to ensure all functionality works correctly.

## Prerequisites

1. **Start the system**:
   ```bash
   python start_agents.py
   ```

2. **Verify services are running**:
   - Base AI Agent: http://localhost:8000
   - Google Search Agent: http://localhost:8001 (A2A server)

3. **Open web interface**: http://localhost:8000

## Test Categories

### 🧪 1. Basic Functionality Tests

#### Test 1.1: Initial Connection
- **Action**: Open http://localhost:8000
- **Expected**: Web interface loads with chat input field
- **Success Criteria**: 
  - Page loads without errors
  - Chat input is visible and functional
  - No console errors in browser dev tools

#### Test 1.2: Simple Chat
- **Input**: `Hello, how are you today?`
- **Expected**: Friendly response acknowledging the greeting
- **Success Criteria**:
  - Response appears within 10 seconds
  - Response is contextually appropriate
  - No error messages

#### Test 1.3: Agent Identity
- **Input**: `What's your name and what can you do?`
- **Expected**: Agent introduces itself as BaseAI and lists capabilities
- **Success Criteria**:
  - Mentions memory capabilities
  - Mentions search delegation
  - Mentions local Ollama usage

### 🧠 2. Memory System Tests

#### Test 2.1: Basic Memory Storage
- **Step 1**: `My name is [YourName] and I work as a [YourJob]`
- **Step 2**: `I live in [YourCity]`
- **Step 3**: `What do you remember about me?`
- **Expected**: Agent recalls all three pieces of information
- **Success Criteria**:
  - Name is remembered correctly
  - Job is remembered correctly
  - City is remembered correctly

#### Test 2.2: Memory Search
- **Step 1**: `I love programming in Python and building AI applications`
- **Step 2**: `My favorite food is pizza`
- **Step 3**: `Tell me what you know about my programming interests`
- **Expected**: Agent retrieves and mentions Python and AI programming
- **Success Criteria**:
  - Relevant information is retrieved
  - Irrelevant information (food) is not mentioned

#### Test 2.3: Cross-Session Memory
- **Step 1**: Have a conversation and share personal information
- **Step 2**: Close browser tab/window
- **Step 3**: Reopen http://localhost:8000 (new session)
- **Step 4**: `What did we discuss in our previous conversation?`
- **Expected**: Agent remembers information from previous session
- **Success Criteria**:
  - Previous conversation details are recalled
  - Memory persists across browser sessions

### 🔍 3. Google Search Agent Integration Tests

#### Test 3.1: Basic Search Delegation
- **Input**: `Search for information about artificial intelligence trends`
- **Expected**: Agent delegates to Google Search Agent and returns results
- **Success Criteria**:
  - Response indicates search was performed
  - Multiple search results are provided
  - Results include titles, URLs, and descriptions
  - Response time is reasonable (under 30 seconds)

#### Test 3.2: Current Events Search
- **Input**: `Find recent news about space exploration`
- **Expected**: Up-to-date news articles about space exploration
- **Success Criteria**:
  - Results are recent (current year)
  - Multiple news sources
  - Relevant to space exploration

#### Test 3.3: Technical Search
- **Input**: `Search for Python machine learning tutorials`
- **Expected**: Technical resources and tutorials
- **Success Criteria**:
  - Results are technically relevant
  - Mix of tutorial and documentation links
  - Appropriate for programming audience

### 🛠️ 4. Advanced Feature Tests

#### Test 4.1: Agent Status Check
- **Input**: `What's your current status?`
- **Expected**: Detailed system status information
- **Success Criteria**:
  - Ollama service status
  - Memory statistics
  - Configuration validation
  - Health indicators

#### Test 4.2: Memory Management
- **Input**: `Clear my memory`
- **Expected**: Confirmation that memory has been cleared
- **Follow-up**: `What do you remember about me?`
- **Expected**: Agent indicates no previous information
- **Success Criteria**:
  - Memory clearing is confirmed
  - Subsequent queries show no memory of previous conversation

#### Test 4.3: User Profile Extraction
- **Step 1**: Share various personal details over multiple messages
- **Step 2**: `What's my user profile?`
- **Expected**: Structured summary of shared information
- **Success Criteria**:
  - Information is organized logically
  - Key details are highlighted
  - Format is easy to read

### 🚨 5. Error Handling Tests

#### Test 5.1: Long Message Handling
- **Input**: [Very long message with 2000+ characters]
- **Expected**: Graceful handling or appropriate error message
- **Success Criteria**:
  - No system crash
  - Clear error message if rejected
  - Or successful processing if supported

#### Test 5.2: Special Characters
- **Input**: `Test with émojis 🤖, spëcial çhars, and unicode: ∮ E⋅da = Q, n → ∞, ∑ f(i)`
- **Expected**: Proper handling of special characters and emojis
- **Success Criteria**:
  - Characters display correctly
  - Response handles unicode properly
  - No encoding errors

#### Test 5.3: Search Service Interruption
- **Setup**: Stop the Google Search Agent (Ctrl+C in A2A server terminal)
- **Input**: `Search for something`
- **Expected**: Error message about search service unavailability
- **Success Criteria**:
  - Clear error message
  - Agent continues to function for non-search queries
  - Graceful degradation

#### Test 5.4: Model Overload
- **Input**: Multiple rapid messages (send 5-10 messages quickly)
- **Expected**: All messages are processed, possibly with queue delays
- **Success Criteria**:
  - No messages are lost
  - Responses eventually arrive
  - System remains stable

### 📱 6. User Interface Tests

#### Test 6.1: Browser Compatibility
- **Test in multiple browsers**:
  - Chrome
  - Firefox
  - Safari (macOS)
  - Edge (Windows)
- **Success Criteria**: Consistent functionality across browsers

#### Test 6.2: Responsive Design
- **Test at different screen sizes**:
  - Desktop (1920x1080)
  - Tablet (768x1024)
  - Mobile (375x667)
- **Success Criteria**: Interface remains usable at all sizes

#### Test 6.3: Chat History Display
- **Action**: Have a long conversation (10+ exchanges)
- **Expected**: Chat history is properly displayed
- **Success Criteria**:
  - All messages are visible
  - Scroll functionality works
  - Message formatting is consistent

### 🔄 7. Performance Tests

#### Test 7.1: Response Time
- **Measure response times for**:
  - Simple chat: < 5 seconds
  - Memory queries: < 3 seconds
  - Search queries: < 30 seconds
- **Success Criteria**: All responses within expected timeframes

#### Test 7.2: Concurrent Users
- **Setup**: Open multiple browser tabs/windows
- **Action**: Send different messages from each tab
- **Expected**: All sessions work independently
- **Success Criteria**:
  - Each session maintains separate context
  - No interference between sessions
  - System remains responsive

#### Test 7.3: Extended Session
- **Action**: Keep browser open for 1+ hours with occasional messages
- **Expected**: Session remains active and responsive
- **Success Criteria**:
  - No session timeout issues
  - Memory persists throughout session
  - Performance doesn't degrade

## Test Results Template

Use this template to document your test results:

```
## Test Session: [Date/Time]

### Environment
- OS: [Windows/macOS/Linux]
- Browser: [Chrome/Firefox/Safari/Edge] [Version]
- Python Version: [Version]
- Ollama Model: [Model Name]

### Test Results

| Test ID | Test Name | Status | Notes |
|---------|-----------|--------|-------|
| 1.1 | Initial Connection | ✅/❌ | |
| 1.2 | Simple Chat | ✅/❌ | |
| 1.3 | Agent Identity | ✅/❌ | |
| 2.1 | Basic Memory Storage | ✅/❌ | |
| ... | ... | ... | |

### Issues Found
- [List any issues or unexpected behavior]

### Performance Notes
- [Response times, any lag noticed]

### Overall Assessment
- [System stability, user experience notes]
```

## Troubleshooting Common Issues

### Issue: Web interface won't load
- **Check**: Are both agents running? (`python start_agents.py`)
- **Check**: Is port 8000 available? (`lsof -i :8000` or `netstat -an | grep 8000`)
- **Solution**: Restart agents or use different port

### Issue: Search not working
- **Check**: Is Google Search Agent running on port 8001?
- **Check**: Are Google API credentials configured in .env?
- **Solution**: Verify A2A server is running and credentials are set

### Issue: Memory not persisting
- **Check**: Is `ENABLE_CROSS_SESSION_MEMORY=true` in .env?
- **Check**: Does the `memory_data` directory exist and is writable?
- **Solution**: Verify memory configuration and permissions

### Issue: Slow responses
- **Check**: System resource usage (CPU/RAM)
- **Check**: Ollama model size vs available RAM
- **Solution**: Use smaller model or increase system resources

## Automated Testing Script

For automated testing, you can use this Python script:

```python
# Save as test_web_ui.py
import requests
import time

def test_web_ui():
    base_url = "http://localhost:8000"
    
    # Test basic connectivity
    try:
        response = requests.get(base_url, timeout=10)
        if response.status_code == 200:
            print("✅ Web interface is accessible")
        else:
            print(f"❌ Web interface returned status {response.status_code}")
    except Exception as e:
        print(f"❌ Cannot connect to web interface: {e}")
    
    # Add more automated tests here...

if __name__ == "__main__":
    test_web_ui()
```

Run with: `python test_web_ui.py`

## Reporting Issues

When reporting issues, please include:
1. Test scenario that failed
2. Expected vs actual behavior
3. System information (OS, browser, Python version)
4. Console errors (if any)
5. Screenshots (if UI-related)

This helps ensure the AI Agents system works reliably across all supported platforms and use cases.
