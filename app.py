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
        
        thread_response = client.beta.threads.create()
        varThread_id = thread_response['data']['id']
        logger.debug(f"this is the thread id: {varThread_id}")
        client.beta.threads.messages.create(
            thread_id=varThread_id,
            role="user",
            content=message
        )
        logger.debug(f"finished creating threads.messages")
        logger.debug(f"creating threads.runs")
        run = client.beta.threads.runs.create(
            thread_id=varThread_id,
            assistant_id=assistant_id_p,
            instructions="Please provide a detailed response."
        )
        logger.debug(f"finished creating threads.runs, begin while loop")
        while run.status in ['queued', 'in_progress', 'cancelling']:
            time.sleep(1)
            intCount += 1  
            reply_text = "Penelope has been thinking for " + str(intCount) + " seconds."
            await ctx.followup.send(reply_text)
            run = client.beta.threads.runs.retrieve(
                thread_id=varThread_id,
                run_id=run.id
            )
        logger.debug(f"finished while loop, begin condition check")
        if run.status == 'completed':
            listMessages = client.beta.threads.messages.list(
                thread_id=varThread_id
            )
            # Extract and send only the assistant's messages as a response
            assistant_messages = [msg for msg in listMessages['data'] if msg['role'] == 'assistant']
            for msg in assistant_messages:
                await ctx.followup.send(msg['content'])
        else:
            runStatus = run.status
            logger.debug(f'Run Status: {runStatus}')

    except Exception as e:
        logger.error(f'Error: {e}')
        await ctx.followup.send('Something went wrong.')

if __name__ == '__main__':
    bot.run(DISCORD_TOKEN)