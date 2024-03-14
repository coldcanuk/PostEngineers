import sys
import os
import time
from flask import Flask
from discord.ext import commands
import discord
from loguru import logger
from openai import OpenAI

# Load environment variables
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Create the OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# Setup logging
DEBUG_MODE = os.getenv('DEBUG_MODE', 'False').lower() in ('true', '1', 't')
log_level = "DEBUG" if DEBUG_MODE else "INFO"
logger.add(sys.stdout, level=log_level)

app = Flask(__name__)

# Configure Discord
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Configure OpenAI Assistants
assistant_id_p = "asst_YGdZxXXnndYvtA0mxUMrnllX"  # Penelope

# Event Handlers
@bot.event
async def on_ready():
    logger.info('Bot is online and ready.')
    print('Bot is online and marked as healthy.')

@bot.slash_command(name="post", description="Invoke Penelope for a message")
async def post(ctx, message: str):
    logger.debug(f"Received post command with text: {message}")
    intCount = 0
    await ctx.defer()
    try:
        reply_text = "Penelope is pondering your request..."
        logger.debug(f"Penelope's response: {reply_text}")
        await ctx.followup.send(reply_text)
        logger.debug("begin client.beta.threads.create")
        thread_response = client.beta.threads.create()
        logger.debug("finished client.beta.threads.create")
        
        # Adjusted to correctly extract thread ID from the response object
        logger.debug("begin populating variable for the thread id")
        varThread_id = thread_response.id  # Adjust this based on the actual attribute/method
        logger.debug(f"Thread ID: {varThread_id}")
        logger.debug(f"Begin beta.threads.messages.create")
        client.beta.threads.messages.create(
            thread_id=varThread_id,
            role="user",
            content=message
        )
        logger.debug(f"Finish beta.threads.messages.create")
        logger.debug(f"Begin beta.threads.runs.create")
        run = client.beta.threads.runs.create(
            thread_id=varThread_id,
            assistant_id=assistant_id_p,
            instructions="Please provide a detailed response."
        )
        logger.debug(f"Finished beta.threads.runs.create")
        while run.status in ['queued', 'in_progress', 'cancelling']:
            time.sleep(1)
            intCount += 1
            reply_text = "Penelope has been thinking for " + str(intCount) + " seconds."
            await ctx.followup.send(reply_text)
            run = client.beta.threads.runs.retrieve(thread_id=varThread_id, run_id=run.id)
        logger.debug(f"begin the condition check")
        if run.status == 'completed':
            logger.debug(f"we have matched completed for run.status condition check")
            listMessages = client.beta.threads.messages.list(thread_id=varThread_id)
            for msg in listMessages.data:
                if msg.role == 'assistant':
                    logger.debug(f"we have matched msg.role equal assistant")
                    # Extracting the text value from each message
                    logger.debug(f"Check if the msg has the text_content attribute")
                    # logger.debug(msg) # only uncomment if something buggerred and you need to see a dump of the variable in the log
                    if hasattr(msg, 'text_content'):  # Check if the msg has the text_content attribute
                        logger.debug(f"Begin to Iterate through content blocks")
                        ii = 0
                        for content_block in msg.text_content:  # Iterate through content blocks
                            logger.debug(f"This is interation number: ") + str(ii)
                            ii += 1
                            if content_block.type == 'text':  # Ensure we're dealing with text content
                                logger.debug("content_block.type is equal to text which means we are dealing with text content")
                                text_value = content_block.text.value  # Extract the text value
                                await ctx.followup.send(text_value)
        else:
            logger.debug(f"we hit the else condition for run.status")
            runStatus = run.status
            logger.debug(f'Run Status: {runStatus}')
        logger.debug(f"we are done the if else condition for run.status")
    except Exception as e:
        logger.error(f'Error: {e}')
        await ctx.followup.send('Something went wrong.')

if __name__ == '__main__':
    bot.run(DISCORD_TOKEN)