# Claude Agent Slack Bot

A Slack bot built with Bolt for Python that integrates with Claude Agent SDK to provide AI-powered responses. The bot uses async Socket Mode and maintains conversation history per thread/channel.

## Prerequisites

- Python 3.7+
- A Slack workspace where you have permissions to install apps
- A configured Slack app with Socket Mode enabled

## Installation

### Environment Variables

Create a `.env` file in the project root with the following variables:

```bash
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_APP_TOKEN=xapp-your-app-token
ANTHROPIC_API_KEY=sk-ant-your-api-key
CLAUDE_WORKING_DIR=/path/to/your/workspace
```

**Where to find these tokens:**

1. **SLACK_BOT_TOKEN**:
   - Go to [https://api.slack.com/apps](https://api.slack.com/apps)
   - Select your app
   - Navigate to **OAuth & Permissions**
   - Copy the **Bot User OAuth Token**

2. **SLACK_APP_TOKEN**:
   - Go to **Basic Information** in your app settings
   - Scroll to **App-Level Tokens**
   - Create a token with the `connections:write` scope
   - Copy the token

3. **ANTHROPIC_API_KEY**:
   - Go to [https://console.anthropic.com](https://console.anthropic.com)
   - Sign in or create an account
   - Navigate to **API Keys** in the settings
   - Create a new API key and copy it

4. **CLAUDE_WORKING_DIR**:
   - Set this to a directory path where Claude can access context (optional)
   - Example: `/Users/yourusername/workspace` or your project directory

### Setup Your Local Project

```bash
# Setup your python virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install the dependencies
pip install -r requirements.txt

# Start the bot
python3 app.py
```

## Project Structure

### `app.py`

The main application file that:
- Initializes the Slack Bolt async app
- Loads environment variables from `.env`
- Defines event handlers using decorators
- Starts the Socket Mode handler

### Current Features

- **Claude Agent SDK Integration**: Powered by Claude AI (Haiku model) for intelligent responses
- **Conversation Memory**: Maintains conversation history per thread/channel for contextual follow-ups
- **app_mention**: Responds to bot mentions with AI-generated responses
- **Security**: No file system access (allowed_tools=[]), Claude operates in text-only mode

## Slack App Configuration

Your Slack app should be configured with:
- **Socket Mode**: Enabled
- **Event Subscriptions**: `app_mention` event
- **OAuth Scopes**:
  - `app_mentions:read` (to receive mention events)
  - `chat:write` (to send messages)

## Adding New Features

Event handlers are defined inline in `app.py` using decorators:

```python
@app.event("event_type")
async def handler_name(event, say, logger):
    # Your handler logic
    pass
```

For slash commands:

```python
@app.command("/command-name")
async def command_handler(ack, command, respond):
    await ack()
    await respond("Response")
```
