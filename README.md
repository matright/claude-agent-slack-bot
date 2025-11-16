# Claude Agent Slack Bot

A **generic, extensible** Slack bot that brings Claude Agent SDK to Slack. Automatically inherits your existing Claude Code capabilities - slash commands, skills, and sub-agents - making them instantly available in Slack conversations.

## ✨ Features

- 🤖 **Claude AI Integration** - Powered by Claude Agent SDK with configurable models (Haiku, Sonnet, Opus)
- 💬 **Conversation Memory** - Maintains context per thread/channel for natural follow-ups
- 🔌 **Socket Mode** - No webhooks or public URLs needed
- 🐳 **Docker Support** - Production-ready containerization with health checks
- ⚙️ **Configurable Tools** - Enable file operations and shell access as needed
- 🔒 **Security First** - Tools disabled by default, permission warnings
- 🔄 **Reuse Existing Capabilities** - Automatically uses your `.claude/` commands, skills, and agents
- 📊 **Health Monitoring** - Built-in health check endpoint for orchestration

## 🚀 Quickstart

Get the bot running in 5 minutes:

**1. Clone and setup**
```bash
git clone https://github.com/matright/claude-agent-slack-bot.git
cd claude-agent-slack-bot
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

**2. Get your tokens**
- **Slack Bot Token**: https://api.slack.com/apps → Your App → OAuth & Permissions
- **Slack App Token**: Basic Information → App-Level Tokens (needs `connections:write` scope)
- **Anthropic API Key**: https://console.anthropic.com → API Keys

**3. Configure environment**
```bash
cp .env.example .env
# Edit .env with your tokens (required: SLACK_BOT_TOKEN, SLACK_APP_TOKEN, ANTHROPIC_API_KEY)
```

**4. Start the bot**
```bash
python -m app
```

**5. Test in Slack**
- Invite bot to a channel: `/invite @your-bot-name`
- Mention the bot: `@your-bot-name what is the weather like?`

**💡 Pro Tip**: If you have existing Claude Code slash commands (`.claude/commands/`), skills, or agents, they're automatically available to the bot! Just mount your `.claude/` folder (see [Docker Deployment](#docker-deployment) for volume mounting).

**Using Docker?** See the [Docker Deployment](#docker-deployment) section below.

**Want to extend?** Jump to [Extending the Bot](#extending-the-bot) for examples.

---

## Prerequisites

- Python 3.11+ (matches Docker implementation, recommended)
- Docker and Docker Compose (for containerized deployment)
- A Slack workspace where you have permissions to install apps
- A configured Slack app with Socket Mode enabled
- Anthropic API key for Claude Agent SDK

## Configuration

All configuration is done via environment variables. See `.env.example` for a complete template.

### Required Environment Variables

| Variable | Description | Where to Get It |
|----------|-------------|-----------------|
| `SLACK_BOT_TOKEN` | Bot User OAuth Token | [Slack API](https://api.slack.com/apps) → Your App → OAuth & Permissions |
| `SLACK_APP_TOKEN` | App-Level Token (needs `connections:write` scope) | Your App → Basic Information → App-Level Tokens |
| `ANTHROPIC_API_KEY` | Claude API Key | [Anthropic Console](https://console.anthropic.com) → API Keys |

### Optional Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ANTHROPIC_BASE_URL` | `https://api.anthropic.com` | Custom API endpoint (for proxies/enterprise) |
| `CLAUDE_WORKING_DIR` | `/app/claude-cwd` | Directory for Claude file operations |
| `CLAUDE_MODEL` | `haiku` | Model to use: `haiku` (fast/cheap), `sonnet` (balanced), `opus` (capable/expensive) |
| `CLAUDE_PERMISSION_MODE` | `default` | Permission handling: `default`, `acceptEdits`, `plan`, `bypassPermissions` ⚠️ |
| `CLAUDE_ALLOWED_TOOLS` | _(empty)_ | Comma-separated tools: `Read,Write,Bash,Grep,Glob,Edit` ⚠️ |
| `LOG_LEVEL` | `INFO` | Logging verbosity: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` |

**Security Notes:**
- Tools are **disabled by default** for security
- `acceptEdits` and `bypassPermissions` modes should only be used in isolated/controlled environments
- See [Configuring Claude Agent SDK](#configuring-claude-agent-sdk) for detailed configuration guidance

### Local Development Setup

```bash
# Clone and install
git clone https://github.com/matright/claude-agent-slack-bot.git
cd claude-agent-slack-bot
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your tokens

# Run
python -m app
```

## 🐳 Docker Deployment

Production-ready containerization with Python 3.11, Node.js 20 LTS, and Claude Code CLI.

### Quick Start

```bash
# 1. Configure
cp .env.example .env
# Edit .env with your tokens

# 2. Run
docker-compose up --build

# Or in detached mode
docker-compose up -d

# View logs
docker-compose logs -f slack-bot

# Stop
docker-compose down
```

### Container Details

- **Base**: Python 3.11-slim + Node.js 20 LTS
- **User**: Non-root `appuser` (UID 1000)
- **Health Check**: `http://localhost:8080/health` (checked every 30s)
- **Resources**: 1 CPU, 1GB RAM (configurable in `docker-compose.yml`)

### Volume Mounts

| Mount | Purpose | Notes |
|-------|---------|-------|
| `./claude-cwd:/app/claude-cwd` | Claude working directory | Required for file operations |
| `./.claude:/app/.claude:ro` | Project Claude config | Optional, tracked in git |
| `~/.claude:/home/appuser/.claude:ro` | User Claude config | Optional, dev only (see `docker-compose.override.yml.example`) |

### Environment Variables

Docker Compose automatically loads `.env` file. For production:
- **Kubernetes**: Use Secrets
- **Docker Swarm**: Use docker secrets
- **Cloud**: Use platform secret managers (AWS Secrets Manager, GCP Secret Manager, etc.)

**Never commit `.env` files to git!**

### Production Considerations

1. **State Persistence**: Currently in-memory. For multi-instance deployments, uncomment the Redis service in `docker-compose.yml`
2. **Secrets**: Use orchestration platform's secret management
3. **Monitoring**: Set up log aggregation (e.g., `docker-compose logs -f --tail=100 slack-bot`)
4. **Scaling**: Implement Redis-based state before horizontal scaling

### Troubleshooting

```bash
# Health check failing?
docker exec claude-agent-slack-bot curl http://localhost:8080/health

# Permission issues?
sudo chown -R 1000:1000 ./claude-cwd

# Container won't start?
docker-compose logs slack-bot
docker-compose config  # Verify env vars

# Out of memory?
# Edit docker-compose.override.yml to increase memory limit
```

## 🏗️ Architecture & How It Works

### Event Flow

```
1. User mentions bot in Slack
   ↓
2. Socket Mode receives event → Bot sends acknowledgment
   ↓
3. Message forwarded to Claude Agent SDK with conversation context
   ↓
4. Claude processes query (using configured model & tools)
   ↓
5. Response filtered (reasoning removed, final text extracted)
   ↓
6. Result posted back to Slack thread
```

### Key Components

- **Slack Bolt**: Async event handling via Socket Mode (no webhooks needed)
- **Claude Agent SDK**: AI-powered responses with conversation history
- **Conversation State**: In-memory client instances per channel/thread (`{channel_id}:{thread_ts}`)
- **Health Check Server**: HTTP endpoint for container monitoring

### Conversation Persistence

Each conversation (channel or thread) gets a dedicated `ClaudeSDKClient` instance stored in memory. This enables context retention across multiple mentions within the same conversation.

**Note**: For production deployments with multiple instances, implement Redis-based state sharing (see commented Redis service in `docker-compose.yml`).

## 🔄 Leveraging Existing Claude Capabilities

One of the most powerful features of this bot is its ability to **reuse your existing Claude Code setup**. If you've already invested in building custom slash commands, skills, or sub-agents for Claude Code, they work immediately in Slack!

### How It Works

The bot respects Claude Code's configuration hierarchy:
1. **Project-level config** (`.claude/config.json`) - Shared team settings
2. **User-level config** (`~/.claude/`) - Your personal commands, skills, agents
3. **Runtime config** (environment variables) - Deployment-specific overrides

### What Gets Inherited

**Slash Commands** (`.claude/commands/*.md`)

If you have custom commands like `/review-pr` or `/generate-tests`, users can invoke them in Slack:
```
@bot /review-pr #123
```

**Skills** (Claude Code skills)

Any skills you've defined are automatically available. The bot can invoke them as needed during conversations.

**Sub-agents** (Custom agents)

If you've created specialized agents for specific tasks, they're accessible to the bot for complex workflows.

**Tool Configurations**

Your allowed tools and permission modes are inherited from `.claude/config.json` and can be overridden via environment variables.

### Setup for Reusability

**For Docker (Recommended):**
Mount your `.claude/` folder as a volume:
```yaml
# In docker-compose.override.yml
volumes:
  - ~/.claude:/home/appuser/.claude:ro  # User-level (personal)
  - ./.claude:/app/.claude:ro            # Project-level (team)
```

**For Local Development:**
The bot automatically reads from:
- `~/.claude/` for your personal config
- `./.claude/` in the project root for team config

### Example: Reusing a Code Review Command

Say you have `.claude/commands/review-pr.md`:
```markdown
# Review Pull Request
Given a PR number, analyze the code changes and provide review feedback.
```

**In Slack, it just works:**
```
@bot /review-pr 456
```

The bot will execute the command using the same Claude Agent SDK context, with access to all configured tools.

### Benefits

✅ **Zero Duplication** - Don't rewrite commands/skills for Slack
✅ **Consistent Behavior** - Same commands work in CLI and Slack
✅ **Faster Development** - Extend once, use everywhere
✅ **Team Collaboration** - Share `.claude/config.json` for consistent team experience

## Configuring Claude Agent SDK

The bot's Claude Agent SDK integration can be customized through environment variables. All settings have sensible defaults and are optional.

### Model Selection

Choose the Claude model based on your needs:

```bash
# Fast and cost-effective (default)
CLAUDE_MODEL=haiku

# Balanced performance
CLAUDE_MODEL=sonnet

# Most capable, highest cost
CLAUDE_MODEL=opus
```

**Trade-offs:**
- **haiku**: ~10x cheaper than opus, suitable for most Slack bot interactions
- **sonnet**: Better reasoning, good for complex questions
- **opus**: Best for difficult problems requiring deep analysis

### Permission Modes

**`default`** (recommended for production):
- Standard permission behavior
- Prompts for confirmations when needed
- Safest option for general use

**`acceptEdits`**:
- Auto-accepts file edits without prompting
- Useful for automated workflows where edits are expected
- ⚠️ Use only in controlled environments with proper isolation

**`plan`**:
- Planning mode only - no execution
- Claude will analyze and plan actions but not execute them
- Excellent for testing and reviewing proposed changes before execution

**`bypassPermissions`**:
- Bypasses all permission checks
- ⚠️ **DANGEROUS** - use with extreme caution
- Only for fully trusted, isolated environments
- Never use in production or with untrusted inputs

### Enabling Tools

By default, Claude has **no file system or command execution access** for security. Enable tools based on your needs:

```bash
# No tools (default - safest)
CLAUDE_ALLOWED_TOOLS=

# Read-only access (safest when tools are needed)
CLAUDE_ALLOWED_TOOLS=Read,Grep,Glob

# Read and write (moderate risk)
CLAUDE_ALLOWED_TOOLS=Read,Write,Edit

# Full access including shell (highest risk)
CLAUDE_ALLOWED_TOOLS=Read,Write,Edit,Bash
```

**Available Tools:**
- `Read`: Read file contents
- `Write`: Create new files
- `Edit`: Modify existing files
- `Bash`: Execute shell commands
- `Grep`: Search file contents
- `Glob`: Find files by pattern

**Security Best Practices:**
1. Start with no tools or read-only tools (`Read`, `Grep`, `Glob`)
2. Never use `bypassPermissions` in production
3. Use `acceptEdits` only in sandboxed/isolated environments
4. Enable `Bash` tool only when absolutely necessary
5. Ensure `CLAUDE_WORKING_DIR` is properly isolated from sensitive files
6. Remember: Claude will have access to environment variables and secrets if tools are enabled
7. Use volume mounts with appropriate permissions (read-only when possible)
8. Monitor and log all tool usage in production

**Example Configurations:**

```bash
# Development: Full access for testing
CLAUDE_MODEL=sonnet
CLAUDE_PERMISSION_MODE=acceptEdits
CLAUDE_ALLOWED_TOOLS=Read,Write,Bash

# Staging: Moderate access
CLAUDE_MODEL=haiku
CLAUDE_PERMISSION_MODE=default
CLAUDE_ALLOWED_TOOLS=Read,Write

# Production: Minimal access (default)
CLAUDE_MODEL=haiku
CLAUDE_PERMISSION_MODE=default
CLAUDE_ALLOWED_TOOLS=
```

## Project Structure

```
claude-agent-slack-bot/
├── app/                      # Application package
│   ├── __init__.py          # Package metadata and version
│   ├── __main__.py          # Entry point wrapper
│   └── app.py               # Main application logic
├── .claude/                  # Project-level Claude configuration
│   └── config.json          # Claude Code settings
├── claude-cwd/              # Claude working directory (volume mount)
├── Dockerfile               # Container image definition
├── docker-compose.yml       # Docker Compose configuration
├── docker-compose.override.yml.example  # Development overrides template
├── .dockerignore            # Docker build exclusions
├── .env.example             # Environment variables template
├── .gitignore              # Git exclusions
├── requirements.txt         # Python dependencies
├── README.md               # This file
└── CLAUDE.md               # Project documentation for Claude Code
```

### Key Files

- **`app/app.py`**: Main application logic - event handlers, Claude SDK integration, health check server
- **`app/__main__.py`**: Entry point wrapper - allows running as module (`python -m app`)
- **`app/__init__.py`**: Package metadata and version
- **`docker-compose.yml`**: Main Docker Compose configuration
- **`.env.example`**: Environment variable template (copy to `.env`)
- **`CLAUDE.md`**: Project documentation for Claude Code

## Slack App Configuration

Your Slack app should be configured with:
- **Socket Mode**: Enabled
- **Event Subscriptions**: `app_mention` event
- **OAuth Scopes**:
  - `app_mentions:read` (to receive mention events)
  - `chat:write` (to send messages)

## 🔧 Extending the Bot

### Adding New Slack Event Handlers

The bot currently only handles `app_mention` events. Add more by defining handlers in `app/app.py`:

**Example: Respond to reactions**
```python
@app.event("reaction_added")
async def handle_reaction(event, say, logger):
    reaction = event.get("reaction")
    user_id = event.get("user")

    # Get conversation context
    channel_id = event.get("item", {}).get("channel")
    thread_ts = event.get("item", {}).get("ts")
    conversation_key = f"{channel_id}:{thread_ts}"

    # Get or create Claude client for this conversation
    client = await get_or_create_claude_client(conversation_key)

    # Query Claude
    await client.query(f"User reacted with :{reaction}:. What might this mean?")

    # Collect and send response
    response_texts = []
    async for message in client.receive_response():
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    response_texts.append(block.text)

    final_response = "\n".join(response_texts)
    await say(text=final_response, thread_ts=thread_ts)
```

**Example: Respond to all messages (not just mentions)**
```python
@app.event("message")
async def handle_message(event, say, logger):
    # Filter out bot messages and threaded replies
    if event.get("subtype") or event.get("bot_id") or event.get("thread_ts"):
        return

    # Process similar to app_mention handler
    # ... (follow same pattern as app_mention in app.py)
```

### Implementing Slash Commands

**Example: `/ask` command**
```python
@app.command("/ask")
async def handle_ask_command(ack, command, respond):
    await ack()  # Acknowledge command immediately

    user_id = command["user_id"]
    channel_id = command["channel_id"]
    text = command["text"]  # User's question

    # Get conversation context
    conversation_key = f"{channel_id}:{command['trigger_id']}"
    client = await get_or_create_claude_client(conversation_key)

    # Send to Claude
    await client.query(text)

    # Collect response
    response_texts = []
    async for message in client.receive_response():
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    response_texts.append(block.text)

    await respond(f"<@{user_id}> asked: {text}\n\n{chr(10).join(response_texts)}")
```

### Enabling Tools for Specific Use Cases

**Code Review Bot**
```bash
# Read-only access for analyzing code
CLAUDE_ALLOWED_TOOLS=Read,Grep,Glob
CLAUDE_WORKING_DIR=/path/to/your/codebase
CLAUDE_MODEL=sonnet  # Better reasoning for code review
```

**Documentation Generator**
```bash
# Read and write for creating docs
CLAUDE_ALLOWED_TOOLS=Read,Write,Edit
CLAUDE_WORKING_DIR=/path/to/docs
CLAUDE_MODEL=haiku  # Cost-effective for doc generation
```

**DevOps Assistant** ⚠️
```bash
# Shell access for running commands (use with caution!)
CLAUDE_ALLOWED_TOOLS=Read,Bash
CLAUDE_PERMISSION_MODE=acceptEdits  # Only in isolated environments!
CLAUDE_MODEL=sonnet
```

### Customizing Response Behavior

**Add typing indicators**
```python
async def handle_app_mention(event, say, logger):
    # ... existing code ...

    # Show bot is working
    await app.client.reactions_add(
        channel=channel_id,
        timestamp=event["ts"],
        name="hourglass_flowing_sand"
    )

    # Query Claude
    await client.query(message_text)
    # ... collect response ...

    # Remove hourglass, add checkmark
    await app.client.reactions_remove(
        channel=channel_id,
        timestamp=event["ts"],
        name="hourglass_flowing_sand"
    )
    await app.client.reactions_add(
        channel=channel_id,
        timestamp=event["ts"],
        name="white_check_mark"
    )

    # Send response
    await say(text=final_response, thread_ts=thread_ts)
```

**Split long responses into threads**
```python
# Split at 3000 chars (Slack message limit is ~4000)
MAX_LENGTH = 3000
chunks = [final_response[i:i+MAX_LENGTH]
          for i in range(0, len(final_response), MAX_LENGTH)]

# First chunk as main reply
await say(text=chunks[0], thread_ts=thread_ts)

# Remaining chunks as thread replies
for chunk in chunks[1:]:
    await say(text=chunk, thread_ts=thread_ts)
```

### Production State Management with Redis

For multi-instance deployments, replace in-memory state with Redis:

**1. Uncomment Redis service in `docker-compose.yml`**

**2. Add Redis client to `app/app.py`:**
```python
import redis.asyncio as redis

# Initialize Redis
redis_client = redis.Redis(host='redis', port=6379, decode_responses=True)

async def get_or_create_claude_client(conversation_key: str):
    # Check Redis for existing conversation
    exists = await redis_client.exists(f"conversation:{conversation_key}")

    if not exists:
        # Create new client
        client = ClaudeSDKClient(options=options)
        await client.__aenter__()

        # Store in Redis with 1-hour TTL
        await redis_client.setex(
            f"conversation:{conversation_key}",
            3600,
            "active"
        )
        claude_clients[conversation_key] = client

    return claude_clients.get(conversation_key)
```

**3. Add `redis` to `requirements.txt`:**
```
redis[hiredis]>=5.0.0
```
