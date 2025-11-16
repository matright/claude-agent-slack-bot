# Claude Agent Slack Bot

A Slack bot built with Bolt for Python that integrates with Claude Agent SDK to provide AI-powered responses. The bot uses async Socket Mode and maintains conversation history per thread/channel.

## Prerequisites

- Python 3.10+ (required by Claude Agent SDK)
- Docker and Docker Compose (for containerized deployment)
- A Slack workspace where you have permissions to install apps
- A configured Slack app with Socket Mode enabled
- Anthropic API key for Claude Agent SDK

## Installation

### Environment Variables

Create a `.env` file in the project root with the following variables:

```bash
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_APP_TOKEN=xapp-your-app-token
ANTHROPIC_API_KEY=sk-ant-your-api-key
ANTHROPIC_BASE_URL=https://api.anthropic.com  # Optional: for custom endpoints
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

4. **ANTHROPIC_BASE_URL** (Optional):
   - Default: `https://api.anthropic.com`
   - Only needed for custom endpoints, proxies, or enterprise deployments
   - For standard usage, you can use the default or omit this variable

5. **CLAUDE_WORKING_DIR**:
   - Set this to a directory path where Claude can access context (optional)
   - Example: `/Users/yourusername/workspace` or your project directory

6. **CLAUDE_MODEL** (Optional):
   - Default: `haiku`
   - Choose the Claude model based on your needs:
     - `haiku`: Fast, cost-effective, suitable for most tasks
     - `sonnet`: Balanced performance, better for complex reasoning
     - `opus`: Most capable, highest cost, best for difficult tasks

7. **CLAUDE_PERMISSION_MODE** (Optional):
   - Default: `default`
   - Controls how Claude handles permissions:
     - `default`: Standard permission behavior (prompts for confirmations)
     - `acceptEdits`: Auto-accept file edits without prompting
     - `plan`: Planning mode - no execution, only planning
     - `bypassPermissions`: Bypass all permission checks (⚠️ use with caution!)
   - **Security Warning**: `acceptEdits` and `bypassPermissions` can be dangerous

8. **CLAUDE_ALLOWED_TOOLS** (Optional):
   - Default: empty (no tools enabled)
   - Comma-separated list of tools to enable
   - Available tools: `Read`, `Write`, `Bash`, `Glob`, `Grep`, `Edit`, etc.
   - Example: `CLAUDE_ALLOWED_TOOLS=Read,Write,Bash`
   - **Security Warning**: Enabling tools gives Claude file system and command execution access

9. **LOG_LEVEL** (Optional):
   - Default: `INFO`
   - Controls application logging verbosity
   - Options: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`
   - **Note**: Use `DEBUG` for detailed troubleshooting only - it is very verbose

### Setup Your Local Project

```bash
# Setup your python virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install the dependencies
pip install -r requirements.txt

# Start the bot
python -m app
```

## Docker Deployment

The bot can be run in a Docker container for consistent deployment across environments. The container includes all necessary dependencies including Claude Code CLI.

### Environment Variable Configuration

The application supports three methods for providing environment variables:

#### Option 1: Using .env File (Recommended for Development)
Docker Compose automatically loads variables from `.env` file in the project root:
```bash
cp .env.example .env
# Edit .env with your actual credentials
docker-compose up --build
```

#### Option 2: Shell Export (Alternative for Development)
Export variables to your shell before running docker-compose:
```bash
export SLACK_BOT_TOKEN=xoxb-your-token-here
export SLACK_APP_TOKEN=xapp-your-token-here
export ANTHROPIC_API_KEY=sk-ant-your-key-here
export CLAUDE_WORKING_DIR=/app/claude-cwd
docker-compose up --build
```

#### Option 3: Production Deployment (Platform Secrets)
For production, use your orchestration platform's secret management:
```bash
# Docker run with environment variables
docker run -e SLACK_BOT_TOKEN=xxx \
           -e SLACK_APP_TOKEN=xxx \
           -e ANTHROPIC_API_KEY=xxx \
           -e CLAUDE_WORKING_DIR=/app/claude-cwd \
           claude-agent-slack-bot:latest

# Kubernetes - use Secrets
# Docker Swarm - use docker secret
# Cloud platforms - use AWS Secrets Manager, GCP Secret Manager, etc.
```

**Important**: Never commit `.env` files or use them in production. Always use platform-specific secret management for deployed environments.

### Quick Start with Docker

1. **Create environment file**:
   ```bash
   cp .env.example .env
   # Edit .env with your actual credentials
   ```

2. **Build and run with Docker Compose**:
   ```bash
   docker-compose up --build
   ```

3. **Run in detached mode**:
   ```bash
   docker-compose up -d
   ```

4. **View logs**:
   ```bash
   docker-compose logs -f slack-bot
   ```

5. **Stop the bot**:
   ```bash
   docker-compose down
   ```

### Docker Architecture

The containerized bot includes:
- **Base Image**: Python 3.11-slim with Node.js 20 LTS
- **Claude Code CLI**: Installed globally for Claude Agent SDK
- **Health Check**: HTTP endpoint on `localhost:8080/health`
- **Resource Limits**: 1 CPU, 1GiB RAM (configurable)
- **Non-root User**: Runs as `appuser` (UID 1000) for security

### Volume Mounts

The Docker setup uses several volume mounts for persistence and configuration:

#### Claude Working Directory (Required)
```yaml
- ./claude-cwd:/app/claude-cwd
```
Persistent storage for Claude Agent SDK operations. Files created during conversations are stored here.

#### Project Claude Configuration (Optional)
```yaml
- ./.claude:/app/.claude:ro
```
Project-level Claude Code settings shared by the team. The `.claude/config.json` file contains:
- Default model settings
- Allowed tools configuration
- Project-specific preferences

**This folder is tracked in git** (only `config.json`) and shared across all developers.

#### User Claude Configuration (Optional, Development Only)
```yaml
- ~/.claude:/home/appuser/.claude:ro
```
Your personal Claude Code settings from `~/.claude/`. Useful for development to preserve personal preferences.

**This should NEVER be committed to git** - it contains user-specific settings and potentially sensitive data.

To enable this mount:
1. Copy the override example: `cp docker-compose.override.yml.example docker-compose.override.yml`
2. Uncomment the user Claude volume mount
3. Restart the container

### Configuration Files

#### `.env` File
Contains sensitive credentials (never commit this):
```bash
SLACK_BOT_TOKEN=xoxb-...
SLACK_APP_TOKEN=xapp-...
ANTHROPIC_API_KEY=sk-ant-...
CLAUDE_WORKING_DIR=/app/claude-cwd
```

Use `.env.example` as a template.

#### `docker-compose.yml`
Main Docker Compose configuration with:
- Service definition
- Volume mounts (Claude working dir + project config)
- Resource limits
- Health check configuration
- Logging settings

#### `docker-compose.override.yml` (Optional)
Local development customizations:
- Enable user Claude config mount
- Override environment variables
- Adjust resource limits
- Add debugging features

Copy from example:
```bash
cp docker-compose.override.yml.example docker-compose.override.yml
```

### Health Check

The bot includes a built-in health check endpoint for monitoring:

- **Endpoint**: `http://localhost:8080/health`
- **Response**: `{"status": "healthy", "conversations": N}`
- **Docker Health Check**: Automatically queries this endpoint every 30 seconds

Check health status:
```bash
# View health status
docker inspect --format='{{.State.Health.Status}}' claude-agent-slack-bot

# View health check logs
docker inspect --format='{{range .State.Health.Log}}{{.Output}}{{end}}' claude-agent-slack-bot
```

### Resource Management

Default resource limits (based on Claude Agent SDK recommendations):

```yaml
resources:
  limits:
    cpus: '1.0'
    memory: 1G
  reservations:
    cpus: '0.5'
    memory: 512M
```

Adjust in `docker-compose.yml` or create a `docker-compose.override.yml` for custom limits.

### Production Deployment

For production deployments, consider:

1. **State Persistence**: The bot currently uses in-memory conversation state. For multi-instance deployments, implement Redis (commented service included in `docker-compose.yml`)

2. **Secrets Management**: Use Docker secrets or external secret managers (Vault, AWS Secrets Manager) instead of `.env` files

3. **Monitoring**: Set up log aggregation and alerting
   ```bash
   # View structured logs
   docker-compose logs -f --tail=100 slack-bot
   ```

4. **Container Orchestration**: Deploy with Kubernetes, Docker Swarm, or cloud platforms
   - Recommended: Cloudflare Sandboxes, Modal, E2B, Fly Machines

5. **Scaling**: For horizontal scaling, implement external state store (Redis) first

### Troubleshooting

#### Health Check Failing
```bash
# Check if the health endpoint is responding
docker exec claude-agent-slack-bot curl http://localhost:8080/health

# Check application logs
docker-compose logs slack-bot
```

#### Permission Issues on Volume Mounts
The container runs as user `appuser` (UID 1000). If you encounter permission issues:
```bash
# Fix permissions on mounted directories
sudo chown -R 1000:1000 ./claude-cwd
```

#### Container Won't Start
```bash
# Check Docker logs for errors
docker-compose logs slack-bot

# Verify environment variables
docker-compose config

# Rebuild without cache
docker-compose build --no-cache
docker-compose up
```

#### Out of Memory
If the bot runs out of memory (especially with many concurrent conversations):
```bash
# Increase memory limit in docker-compose.override.yml
deploy:
  resources:
    limits:
      memory: 2G
```

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

### `app/app.py`

The main application file that:
- Initializes the Slack Bolt async app
- Loads environment variables from `.env` (via python-dotenv)
- Defines event handlers using decorators
- Starts both the Slack Socket Mode handler and health check server
- Handles graceful shutdown and cleanup

### `app/__main__.py`

Thin entry point wrapper that:
- Imports and executes the main() function from app.py
- Allows running the application as a module: `python -m app`

### Current Features

- **Claude Agent SDK Integration**: Powered by Claude AI (Haiku model) for intelligent responses
- **Conversation Memory**: Maintains conversation history per thread/channel for contextual follow-ups
- **app_mention**: Responds to bot mentions with AI-generated responses
- **Security**: No file system access (allowed_tools=[]), Claude operates in text-only mode
- **Health Check**: HTTP endpoint at `/health` for container monitoring and health checks
- **Graceful Shutdown**: Properly cleans up Claude SDK client connections on shutdown

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
