import sys
import os
import asyncio
import re
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
DEBUG_MODE = os.getenv('DEBUG_MODE', 'False').lower() in ('true', '1', 't', 'on')
log_level = "DEBUG" if DEBUG_MODE else "INFO"
logger.remove()  # Removes all handlers
logger.add(sys.stdout, level=log_level)  # Re-add with the desired level
logger.info(f"DEBUG_MODE: {DEBUG_MODE}")

app = Flask(__name__)

# Configure Discord
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Instructions placeholders
penelope_instructions = "this is penelope's custom instructions"
mariecaissie_instructions = "this is marie caissie's custom instructions"

async def handle_post_command(message, assistant_id, instructions):
    intCount = 0
    try:
        thread_response = client.beta.threads.create()
        varThread_id = thread_response.id
        client.beta.threads.messages.create(thread_id=varThread_id, role="user", content=message)
        run = client.beta.threads.runs.create(
            thread_id=varThread_id,
            assistant_id=assistant_id,
            instructions=instructions
        )
        while run.status in ['queued', 'in_progress', 'cancelling']:
            await asyncio.sleep(1)
            intCount += 1
            run = client.beta.threads.runs.retrieve(thread_id=varThread_id, run_id=run.id)
        if run.status == 'completed':
            listMessages = client.beta.threads.messages.list(thread_id=varThread_id)
            return [msg.content for msg in listMessages.data if msg.role == 'assistant']
    except Exception as e:
        logger.error(f"Error in handle_post_command: {e}")
        return []

async def extract_insight_and_masterpiece(texts):
    insight = ""
    masterpiece = ""
    for text in texts:
        insight_match = re.search("Insight: (.+)", text)
        if insight_match:
            insight = insight_match.group(1)
        masterpiece_match = re.search("Penelope's Masterpiece: (.+)", text)
        if masterpiece_match:
            masterpiece = masterpiece_match.group(1)
    return insight, masterpiece

@bot.event
async def on_ready():
    logger.info('Bot is online and ready.')

@bot.slash_command(name="post", description="Invoke Penelope for a message")
async def post(ctx, message: str):
    await ctx.defer()
    reply_texts = await handle_post_command(message, assistant_id_p, penelope_instructions)
    for reply_text in reply_texts:
        await ctx.followup.send(reply_text)  # Sending Penelope's full reply to Discord
    
    # Extract Insight and Masterpiece for Marie Caissie
    insight, masterpiece = extract_insight_and_masterpiece(reply_texts)
    combined_text = f"Insight: {insight} | Masterpiece: {masterpiece}"
    # This combined_text is ready to be sent to Marie Caissie for further processing.
    # Example: await handle_post_command(combined_text, assistant_id_mc, mariecaissie_instructions)
    # For demonstration purposes, we'll log it.
    logger.info(f"Prepared for Marie Caissie: {combined_text}")

if __name__ == '__main__':
    bot.run(DISCORD_TOKEN)
