import sys
import os
import asyncio
import re
from flask import Flask
from discord.ext import commands
import discord
from loguru import logger
from openai import OpenAI
import json
import backoff

# Load environment variables
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
ASSISTANT_PENELOPE = os.getenv('ASSISTANT_PENELOPE')
assistant_id_p = str(ASSISTANT_PENELOPE)
ASSISTANT_MARIECAISSIE = os.getenv('ASSISTANT_MARIECAISSIE')
assistant_id_mc = str(ASSISTANT_MARIECAISSIE)

# Create the OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)
# Setup logging
DEBUG_MODE = os.getenv('DEBUG_MODE', 'False').lower() in ('true', '1', 't', 'on')
log_level = "DEBUG" if DEBUG_MODE else "INFO"
logger.remove()  # Removes all handlers
logger.add(sys.stdout, level=log_level)  # Re-add with the desired level

app = Flask(__name__) # Initialize Flask application

# Configure Discord
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
bot = commands.Bot(command_prefix='!', intents=intents)
logger.info(f"finished setting up intents")

# Function handle_post_command
async def handle_post_command(message, assistant_id):
    logger.debug("BEGIN handle_post_function")
    try:
        response = client.beta.threads.create_and_run(
            assistant_id=assistant_id,
            stream="false",
            temperature=1,
            thread={"messages": [{"role": "user", "content": message}]}
        )

        varThread_id = response.thread_id
        logger.debug(f"Run initiated with assistant {assistant_id}, Thread ID: {varThread_id}")

        # Dynamic sleeping with exponential backoff
        @backoff.on_predicate(backoff.expo, lambda x: x.status not in ['completed', 'failed'], max_time=60)
        
        async def wait_for_completion(thread_id, run_id):
            return client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)

        run_details = await wait_for_completion(varThread_id, response.id)
        
        if run_details.status != 'completed':
            raise RuntimeError(f"Run did not complete successfully: {run_details.status}")

        listMessages = client.beta.threads.messages.list(thread_id=varThread_id)
        logger.debug("Begin adding data into reply_texts")
        reply_texts = [
            content_block.text.value for msg in listMessages.data 
            if msg.role == 'assistant' 
              for content_block in msg.content 
                if content_block.type == 'text'
        ]
        
        logger.debug("just before the return of reply_texts")
        return reply_texts

    except Exception as e:
        logger.error(f"Encountered an error in handle_post_command: {e}")
        return []

#
# BEGIN Section Event Handlers
#

# event on_ready
@bot.event
async def on_ready():
    logger.info('Bot is online and ready.')

# slash_command post
@bot.slash_command(name="post", description="Invoke Penelope for a message")
async def post(ctx, message: str):
    logger.debug("Received /post command with message: {}", message)
    await ctx.defer()
    logger.debug("Defer acknowledged. Proceeding with Penelope's wisdom.")

    # Penelope's Process
    try:
        reply_texts = await handle_post_command(message, assistant_id_p)
        logger.debug("Received reply from Penelope: {}", reply_texts)
    except Exception as e:
        logger.error("Failed to retrieve reply from Penelope: {}", e)
        await ctx.followup.send("Ah, zounds! Encountered an issue invoking Penelope.")
        return

    if not reply_texts:
        logger.warning("Empty reply from Penelope. Aborting the quest.")
        await ctx.followup.send("Penelope seems to be lost in thought. Please try again.")
        return

    full_reply = " ".join(reply_texts)
    await ctx.followup.send(full_reply)
    logger.debug("Dispatched Penelope's reply to the high seas of Discord.")

#
# END Section Event Handlers
#

if __name__ == '__main__': # Conditional check to confirm it is the main app running
    bot.run(DISCORD_TOKEN)