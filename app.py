import os
import logging
from dotenv import load_dotenv

from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler

from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, AssistantMessage, TextBlock, ThinkingBlock

logging.basicConfig(level=logging.DEBUG)

load_dotenv()

# Initialization
app = AsyncApp(token=os.environ.get("SLACK_BOT_TOKEN"))

# Store ClaudeSDKClient instances per conversation (thread or channel)
claude_clients = {}


async def get_or_create_claude_client(conversation_key: str) -> ClaudeSDKClient:
    """Get or create a ClaudeSDKClient for a specific conversation.

    Args:
        conversation_key: Unique identifier for the conversation (channel:thread)

    Returns:
        ClaudeSDKClient instance for this conversation
    """
    if conversation_key not in claude_clients:
        options = ClaudeAgentOptions(
            model="haiku",
            permission_mode="default",
            allowed_tools=[],  # Empty for now, can be configured later
            cwd=os.environ.get("CLAUDE_WORKING_DIR")
        )
        # Creating client for persistent conversation history
        client = ClaudeSDKClient(options=options)
        # Connect the client (enter async context manager)
        await client.__aenter__()
        claude_clients[conversation_key] = client

    return claude_clients[conversation_key]


@app.event("app_mention")
async def handle_app_mention(event, say, logger):
    """Handle app mentions by sending the message to Claude Agent SDK.

    This handler:
    1. Extracts the message text from the Slack event
    2. Determines the conversation context (thread or channel)
    3. Sends an acknowledgment to the user
    4. Gets or creates a Claude client for persistent conversation
    5. Sends the query to Claude and collects responses
    6. Filters out reasoning (ThinkingBlock) and returns only final results (TextBlock)
    7. Sends a single final response to Slack
    """
    user_id = event.get("user")
    channel_id = event.get("channel")
    thread_ts = event.get("thread_ts") or event.get("ts")

    try:
        # Extract message text
        message_text = event.get("text", "")

        # Determine conversation key (thread or channel)
        conversation_key = f"{channel_id}:{thread_ts}"

        logger.info(f"Processing app_mention from user {user_id} in conversation {conversation_key}")

        # Send acknowledgment
        await say(
            text=f"Processing your request <@{user_id}>...",
            thread_ts=thread_ts
        )

        # Get or create Claude client for this conversation
        client = await get_or_create_claude_client(conversation_key)

        # Send query to Claude
        await client.query(message_text)

        # Collect responses, filtering out reasoning (ThinkingBlock)
        response_texts = []
        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    # Only collect TextBlock, skip ThinkingBlock and other types
                    if isinstance(block, TextBlock):
                        response_texts.append(block.text)

        # Send final collected response
        final_response = "\n".join(response_texts) if response_texts else "No response generated."

        await say(
            text=final_response,
            thread_ts=thread_ts
        )

        logger.info(f"Successfully processed app_mention for conversation {conversation_key}")

    except Exception as e:
        logger.error(f"Error processing app_mention: {e}", exc_info=True)
        await say(
            text=f"Sorry <@{user_id}>, I encountered an error: {str(e)}",
            thread_ts=thread_ts
        )


async def main():
    await AsyncSocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN")).start_async()

# Start Bolt app
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
