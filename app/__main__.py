"""Entry point for running the Claude Agent Slack Bot as a module.

Usage:
    python -m app
"""
from app.app import main
import asyncio

if __name__ == "__main__":
    asyncio.run(main())
