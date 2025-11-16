# Multi-stage Dockerfile for Claude Agent Slack Bot
# This container runs the Slack bot with Claude Agent SDK integration
# and supports mounting Claude configuration folders for persistence

# Stage 1: Base image with Node.js and Python
FROM python:3.11-slim AS base

# Install Node.js 20 LTS (required for Claude Code CLI)
# Using NodeSource repository for official Node.js builds
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        ca-certificates \
        gnupg && \
    mkdir -p /etc/apt/keyrings && \
    curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg && \
    echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_20.x nodistro main" | tee /etc/apt/sources.list.d/nodesource.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends nodejs && \
    rm -rf /var/lib/apt/lists/*

# Verify Node.js and npm installation
RUN node --version && npm --version

# Install Claude Code CLI globally
# This is required by the Claude Agent SDK for tool execution
RUN npm install -g @anthropic-ai/claude-code

# Stage 2: Application setup
FROM base AS application

# Set working directory
WORKDIR /app

# Create non-root user 'appuser' with UID 1000 (matches most Linux hosts)
# This improves security and allows proper file permissions on mounted volumes
RUN groupadd -g 1000 appuser && \
    useradd -r -u 1000 -g appuser -d /home/appuser -s /sbin/nologin -c "Application User" appuser && \
    mkdir -p /home/appuser/.claude && \
    chown -R appuser:appuser /home/appuser

# Create directories for Claude working directory and project config
RUN mkdir -p /app/claude-cwd /app/.claude && \
    chown -R appuser:appuser /app

# Copy requirements first for better Docker layer caching
# Dependencies are installed before copying application code
COPY --chown=appuser:appuser requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
# Application is organized in app/ directory with app.py containing the main logic
COPY --chown=appuser:appuser app/ ./app/

# Copy project-level Claude configuration
# The .claude directory contains project-level config.json that is tracked in git
COPY --chown=appuser:appuser .claude /app/.claude/

# Switch to non-root user for security
USER appuser

# Set environment variables
# CLAUDE_WORKING_DIR: Directory where Claude Agent SDK performs file operations
# Set to /app/claude-cwd which can be mounted as a volume for persistence
ENV CLAUDE_WORKING_DIR=/app/claude-cwd

# Health check endpoint runs on port 8080 (internal only, not exposed)
# This endpoint is used by Docker and orchestration platforms to verify container health
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Note: curl is not available in slim image by default
# If health check fails, install curl or use python for health check
# Alternative: RUN apt-get update && apt-get install -y curl

# Expose health check port (for documentation only, not published)
EXPOSE 8080

# Run the application
# Executes the app package which starts both the Slack bot and health check endpoint
# The __main__.py wrapper imports and runs main() from app.py
CMD ["python", "-m", "app"]
