import sys
import os
import time
import asyncio
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

# Create the OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# Setup logging
DEBUG_MODE = os.getenv('DEBUG_MODE', 'False').lower() in ('true', '1', 't', 'on')
log_level = "DEBUG" if DEBUG_MODE else "INFO"
logger.remove()  # Removes all handlers
logger.add(sys.stdout, level=log_level)  # Re-add with the desired level
logger.info(f"DEBUG_MODE: {DEBUG_MODE}")
logger.debug(assistant_id_p)

app = Flask(__name__)

# Configure Discord
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
bot = commands.Bot(command_prefix='!', intents=intents)
# Standalone functions go here
async def handle_post_command(message):
    """
    Handles processing and interacting with OpenAI, separate from Discord command.
    Can be used for Discord command or future API integrations.
    """
    intCount = 0
    try:
        reply_text = "Penelope is pondering your request..."
        logger.debug(reply_text)
        thread_response = client.beta.threads.create()
        varThread_id = thread_response.id
        client.beta.threads.messages.create(thread_id=varThread_id, role="user", content=message)
        logger.debug("Creating run with OpenAI")
        run = client.beta.threads.runs.create(
            thread_id=varThread_id,
            assistant_id=assistant_id_p,
            instructions="""
            I'm Penelope, a master tweet composer and psychology guru. I create tweets using my knowledge of psychology that will entice people to engage and comment. I never use hashtags. I add one relevant emoji per tweet.
            🎯Goal: "The goal is to craft each tweet in a way that maximizes audience engagement, triggers potent emotional reactions, and fuels engaging conversations"
            🔗Idea: "The idea for the next tweet"
            🧠Insight: "Psychological tactic best suited to engage humans on the next tweet."
            📝Tweet: "The actual tweet text, 150-250 chars., first half in english and the second half in french."
            ✨Penelope's Masterpiece: "Penelope re-engineers {📝Tweet} into a masterpiece of psychologically engineered combination of words desgined to grip as many readers as possible. This will be the text that will be used and published to the world."
            ------            
            """
        )
        while run.status in ['queued', 'in_progress', 'cancelling']:
            await asyncio.sleep(1)  # Use asyncio.sleep for async operations
            logger.debug(f"We are in the while loop at iteration: {intCount}")
            intCount += 1
            run = client.beta.threads.runs.retrieve(thread_id=varThread_id, run_id=run.id)
            
        if run.status == 'completed':
            listMessages = client.beta.threads.messages.list(thread_id=varThread_id)
            text_values = []
            for msg in listMessages.data:
                if msg.role == 'assistant':
                    for content_block in msg.content:
                        if content_block.type == 'text':
                            text_value = content_block.text.value
                            text_values.append(text_value)
            return text_values  # Return list of text values for further processing
            
    except Exception as e:
        logger.error(f"Error in handle_post_command: {e}")
        return []
    
# Event Handlers go here
@bot.event
async def on_ready():
    logger.info('Bot is online and ready.')
    print('Bot is online and marked as healthy.')

@bot.slash_command(name="post", description="Invoke Penelope for a message")
async def post(ctx, message: str):
    """
    Discord slash command to invoke Penelope and respond in Discord.
    """
    await ctx.defer()
    reply_texts = await handle_post_command(message)  # Use the standalone function
    for reply_text in reply_texts:
        await ctx.followup.send(reply_text)
        logger.info(f"This is what reply_text looks like: {reply_text}")

if __name__ == '__main__':
    bot.run(DISCORD_TOKEN)