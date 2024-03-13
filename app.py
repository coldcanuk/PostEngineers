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

@bot.event
async def on_ready():
    logger.info('Bot is online and ready.')
    bot_health_status = {"is_healthy": True}
    print('Bot is online and marked as healthy.')

@bot.slash_command(name="post", description="Post a message using Penelope")
async def post(ctx, message: str):
    logger.debug(f"Received post command with text: {message}")
    await ctx.defer()
    try:
        # Step 2: Add a message to the thread
        thread_response = client.assistants.create_run(
            assistant_id="asst_YGdZxXXnndYvtA0mxUMrnllX",
            inputs=[{"type": "text", "data": message}]
        )

        # Extract Penelope's response
        if thread_response['choices']:
            reply_text = thread_response['choices'][0]['message']['content'].strip()
            logger.debug(f"Penelope's response: {reply_text}")
            await ctx.followup.send(reply_text)
        else:
            await ctx.followup.send('No content generated.')
    except Exception as e:
        logger.error(f'Error: {e}')
        await ctx.followup.send('Something went wrong.')

if __name__ == '__main__':
    bot.run(DISCORD_TOKEN)
