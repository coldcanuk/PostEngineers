import sys
import os
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

# Setup logging based on an environment variable
DEBUG_MODE = os.getenv('DEBUG_MODE', 'False').lower() in ('true', '1', 't')
log_level = "DEBUG" if DEBUG_MODE else "INFO"
logger.add(sys.stdout, level=log_level)  # Output logs to stdout

app = Flask(__name__)

# Configure Discord
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Check if environment variables are loaded (at appropriate logging level)
logger.debug(f"DISCORD_TOKEN loaded: {'Yes' if DISCORD_TOKEN else 'No'}")
logger.debug(f"OPENAI_API_KEY loaded: {'Yes' if OPENAI_API_KEY else 'No'}")

bot_health_status = {"is_healthy": False}

@bot.event
async def on_ready():
    logger.info('Bot is online and ready.')
    global bot_health_status
    bot_health_status["is_healthy"] = True
    print('Bot is online and marked as healthy.')

@bot.slash_command(name="post", description="Post a message using Penelope")
async def post(ctx, message: str):
    logger.debug(f"Received post command with text: {message}")
    await ctx.defer()
    try:
        # Create a new thread to engage Penelope
        new_thread = client.beta.threads.create(assistant="asst_YGdZxXXnndYvtA0mxUMrnllX", messages=[{"role": "user", "content": message}])
        thread_id = new_thread["data"]["id"]
        # Retrieve the thread to get the response
        thread_response = client.beta.threads.retrieve(thread_id)
        reply_text = thread_response["data"]["messages"][-1]["content"].strip()
        
        logger.debug(f"Penelope's response: {reply_text}")
        
        if reply_text:
            await ctx.followup.send(reply_text)
        else:
            await ctx.followup.send('No content generated.')  # Use followup.send here
    except Exception as e:
        logger.error(f'Error: {e}')
        await ctx.followup.send('Something went wrong.')  # Use followup.send here

if __name__ == '__main__':
    bot.run(DISCORD_TOKEN)
