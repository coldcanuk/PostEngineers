import sys
import os
import re
import asyncio
import time
from flask import Flask
from discord.ext import commands
import discord
from loguru import logger
from openai import OpenAI

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
DEBUG_MODE = os.getenv('DEBUG_MODE', 'False').lower() in ('true', '1', 't', 'y')
log_level = "DEBUG" if DEBUG_MODE else "INFO"
logger.remove()  # Removes all handlers
logger.add(sys.stdout, level=log_level)  # Re-add with the desired level

app = Flask(__name__)

# Configure Discord
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
bot = commands.Bot(command_prefix='!', intents=intents)

logger.info("Finished setting up intents.")

# 
async def check_run_completion(thread_id, run_id):
    """
    Asynchronously checks the completion status of a specific run within an OpenAI thread.

    This function is designed to query the OpenAI API to retrieve the current status of a run given its thread ID and run ID. It serves as a utility to understand whether a submitted run (which could be generating text, processing commands, etc.) has been completed or is still in progress. This is crucial for asynchronous operations where subsequent steps depend on the completion of the run.

    Parameters:
    - thread_id (str): The unique identifier for the thread in which the run is taking place.
    - run_id (str): The unique identifier for the specific run whose status is to be checked.

    Returns:
    - run_details (Run): An object containing details about the run, including its current status.
    """
    return client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)

# 

async def wait_for_completion(thread_id, run_id):
    """
    Awaits the completion of a run in an OpenAI thread, employing a simple exponential backoff strategy for polling.
    """
    max_delay = 60
    delay = 1  # Start with a 1 second delay
    intCount = 0
    while True:
        logger.debug(f"We are at iteration: {intCount}")
        intCount += 1
        run_details = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
        logger.debug(f"Checking run completion, status: {run_details.status}")
        if run_details.status in ['completed', 'failed']:
            logger.debug("run_details.status has matched either completed or failed. Will now attempt return run_details")
            return run_details
        logger.debug(f"This is delay before:  {delay}")
        await asyncio.sleep(delay)
        delay = min(delay * 2, max_delay)  # Exponentially increase delay, up to a max
        logger.debug(f"This is delay after:   {delay}")
# 
async def handle_post_command(message, assistant_id):
    """
    Initiates a run with OpenAI's assistant and handles its completion and response retrieval.

    This function initiates a run by sending a user's message to a specified assistant within the OpenAI API, waits for the run to complete using the 'wait_for_completion' function, and then retrieves the assistant's response. It encapsulates the entire process of communicating with OpenAI's API from run initiation to response collection, handling exceptions and logging essential debugging information along the way.

    Parameters:
    - message (str): The content of the message to be processed by the assistant.
    - assistant_id (str): The unique identifier of the assistant to which the message is sent.

    Returns:
    - reply_texts (list): A list of strings representing the assistant's response, extracted from the run's final messages.
    """
    logger.debug("BEGIN handle_post_function")
    try:
        # Adjusted to directly use response attributes instead of dictionary access
        response = client.beta.threads.create_and_run(
            assistant_id=assistant_id,
            thread={"messages": [{"role": "user", "content": message}]}
        )

        logger.debug(f"Run initiated with assistant {assistant_id}, Thread ID: {response.thread_id}")

        run_details = await wait_for_completion(response.thread_id, response.id)
        
        if run_details.status != 'completed':
            raise RuntimeError(f"Run did not complete successfully: {run_details.status}")

        # Adjusted to fetch messages and then iterate over them to construct reply_texts
        listMessages = client.beta.threads.messages.list(thread_id=response.thread_id)
        reply_texts = [
            content_block.text.value for msg in listMessages.data 
            if msg.role == 'assistant' 
              for content_block in msg.content 
                if content_block.type == 'text'
        ]
        
        logger.debug("Just before the return of reply_texts")
        return reply_texts

    except Exception as e:
        logger.error("Encountered an error in handle_post_command")
        raise RuntimeError (f"Hit an error in the handle_post_command function: {e}")

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
        await ctx.followup.send("Ah, zounds! Encountered an issue invoking Penelope.")
        raise RuntimeError(f"Failed to retrieve reply from Penelope: {e}")

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