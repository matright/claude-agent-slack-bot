# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Slack Bolt for Python** application named "Claude Agent Slack Bot" that integrates with the **Claude Agent SDK** to provide AI-powered responses. When the bot is mentioned in Slack, it sends the user's message to Claude (using the Haiku model) and returns the response. The app uses async Socket Mode for Slack connectivity and maintains persistent conversation history per thread/channel.

## Environment Setup

Required environment variables (never commit these):
- `SLACK_BOT_TOKEN`: Bot User OAuth Token from Slack app OAuth & Permissions page
- `SLACK_APP_TOKEN`: App-level token with `connections:write` scope
- `ANTHROPIC_API_KEY`: Anthropic API key for Claude Agent SDK (get from https://console.anthropic.com)
- `CLAUDE_WORKING_DIR`: Working directory path for Claude Agent SDK operations (e.g., `/path/to/workspace`)

### Local Development Setup
```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file from template
cp .env.example .env
# Edit .env with your credentials

# Run the app
python -m app
```

### Docker Deployment Setup
```bash
# Option 1: Using .env file (Docker Compose auto-loads it)
cp .env.example .env
# Edit .env with your credentials
docker-compose up --build

# Option 2: Using shell exports
export SLACK_BOT_TOKEN=xoxb-your-token
export SLACK_APP_TOKEN=xapp-your-token
export ANTHROPIC_API_KEY=sk-ant-your-key
docker-compose up --build
```

**Important**: The docker-compose.yml no longer uses `env_file:` directive. Instead, it uses `environment:` with shell variable substitution. This allows Docker Compose to load from .env file automatically OR use shell-exported variables OR work with orchestration platforms.

## Development Commands

**Run the app**:
```bash
python -m app
```

Or with Docker:
```bash
docker-compose up
```

## Architecture

### Application Structure

The application is organized in the `app/` package:

**app/__main__.py** - Entry point wrapper:
- Thin wrapper that imports and executes main() from app.py
- Allows running as a Python module: `python -m app`

**app/app.py** - Main application logic:
- Uses `AsyncApp` from slack_bolt for async event handling
- Uses `AsyncSocketModeHandler` for WebSocket connection to Slack
- Socket Mode eliminates the need for a public URL during development
- Event handlers are defined inline using decorators
- Runs health check server on port 8080 for Docker health monitoring
- Handles graceful shutdown and cleanup of Claude SDK clients

### Current Event Handlers

**app_mention** (app/app.py:~50-115):
- Triggered when the bot is mentioned in any channel or thread
- Extracts the message text and conversation context (thread_ts or channel_id)
- Sends an acknowledgment message to the user
- Creates or retrieves a persistent ClaudeSDKClient for the conversation
- Sends the user's message to Claude Agent SDK (using Haiku model)
- Filters out reasoning messages (ThinkingBlock) and collects only final results (TextBlock)
- Sends a single consolidated response back to Slack
- Maintains conversation history per thread/channel for follow-up questions

## Claude Agent SDK Integration

### Configuration
The bot uses `ClaudeAgentOptions` with the following settings (app/app.py:~31-36):
- **Model**: `haiku` (fast, cost-effective Claude model)
- **Permission Mode**: `default` (standard execution mode)
- **Allowed Tools**: Empty list `[]` (no tools enabled, prevents file/system access)
- **Working Directory**: Set via `CLAUDE_WORKING_DIR` environment variable

### Conversation Management
- Each conversation is identified by a unique key: `{channel_id}:{thread_ts}`
- If a message is in a thread, the thread_ts is used; otherwise, the message timestamp is used
- `ClaudeSDKClient` instances are stored in a global dictionary for persistence
- This allows Claude to remember context across multiple @mentions in the same thread/channel
- Client instances are created on-demand and reused for subsequent messages in the same conversation

### Response Filtering
The bot filters Claude's responses to provide a clean user experience:
- **Included**: `TextBlock` messages (final responses and explanations)
- **Excluded**: `ThinkingBlock` messages (internal reasoning)
- All included text blocks are concatenated with newlines and sent as a single Slack message

### Adding Tools (Future Enhancement)
To enable Claude to use tools (Read, Write, Bash, etc.), modify the `allowed_tools` parameter in app/app.py:~34:
```python
allowed_tools=["Read", "Write", "Bash"]  # Example: enable file and bash operations
```

## Key Technical Notes

- Uses `python-dotenv` for environment variable management (.env file)
- Integrates `claude-agent-sdk` for AI-powered responses with persistent conversation history
- Async/await pattern throughout with `slack_bolt.async_app` and Claude Agent SDK
- Socket Mode connection (no webhooks, no public URL needed)
- The Slack app must be configured with the `app_mention` event subscription in the Slack API dashboard
- Logging set to DEBUG level for development visibility
- Client instances are kept in memory for conversation persistence (consider adding cleanup logic for production)

## Adding New Event Handlers

To add new event handlers, define them inline in app/app.py using decorators:

```python
@app.event("event_type")
async def handler_name(event, say, logger):
    # Your handler logic here
    pass
```

For slash commands:
```python
@app.command("/your-command")
async def command_handler(ack, command, respond):
    await ack()
    await respond("Response text")
```
