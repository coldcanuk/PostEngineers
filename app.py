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
ASSISTANT_PENELOPE = os.getenv('ASSISTANT_PENELOPE')
assistant_id_p = ASSISTANT_PENELOPE
# Create the OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# Setup logging
DEBUG_MODE = os.getenv('DEBUG_MODE', 'False').lower() in ('true', '1', 't')
log_level = "DEBUG" if DEBUG_MODE else "INFO"
logger.add(sys.stdout, level=log_level)
logger.info(ASSISTANT_PENELOPE)
logger.info(assistant_id_p)
app = Flask(__name__)

# Configure Discord
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Configure OpenAI Assistants
# assistant_id_p = "asst_YGdZxXXnndYvtA0mxUMrnllX"  # Penelope

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
        varThread_id = thread_response.id
        client.beta.threads.messages.create(
            thread_id=varThread_id,
            role="user",
            content=message
        )
        run = client.beta.threads.runs.create(
            thread_id=varThread_id,
            assistant_id=assistant_id_p,
            instructions="Please provide a detailed response. Always include emojis and you must always follow your preconfigured instructions."
        )
        while run.status in ['queued', 'in_progress', 'cancelling']:
            time.sleep(1)
            intCount += 1
            # reply_text = "Penelope has been thinking for " + str(intCount) + " seconds." # Uncomment only if you need to debug the while loop
            await ctx.followup.send(reply_text)
            run = client.beta.threads.runs.retrieve(thread_id=varThread_id, run_id=run.id)
        if run.status == 'completed':
            listMessages = client.beta.threads.messages.list(thread_id=varThread_id)
            for msg in listMessages.data:
                if msg.role == 'assistant':
                    # Direct extraction from the 'content' attribute of 'msg'
                    for content_block in msg.content:  # Iterate through the 'content' list
                        if content_block.type == 'text':  # Check for 'text' type content
                            text_value = content_block.text.value  # Access the 'value' directly
                            await ctx.followup.send(text_value)  # Send the extracted text
    except Exception as e:
        logger.error(f'Error: {e}')
        await ctx.followup.send('Something went wrong.')

if __name__ == '__main__':
    bot.run(DISCORD_TOKEN)