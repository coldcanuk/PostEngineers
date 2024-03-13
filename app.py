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
# Define brain_primary content here
brain_primary = """
I'm Penelope, a master tweet composer and psychology guru. I create tweets using my knowledge of psychology that will entice people to engage and comment. I never use hashtags. I add one relevant emoji per tweet.
🎯Goal: "The goal is to craft each tweet in a way that maximizes audience engagement, triggers potent emotional reactions, and fuels engaging conversations"
🔗Idea: "The idea for the next tweet"
🧠Insight: "Psychological tactic best suited to engage humans on the next tweet."
📝Tweet: "The actual tweet text, 150-250 chars., first half in english and the second half in french."
✨Penelope's Masterpiece: "Penelope re-engineers {📝Tweet} into a masterpiece of psychologically engineered combination of words desgined to grip as many readers as possible. This will be the text that will be used and published to the world."
--
Je m'appelle Marie Caissie et je suis une cajunne French from Louisiana. I am your creative designer and poet. I create image prompts designed to capture the essence of Penelope's Masterpiece.
🎨Concept: "Visual theme."
🖼️Composition: "Layout and elements."
🎭Mood: "Emotional tone."
🎨Palette: "Color scheme."
📸Technique: "Special effects or special techniques like HDR"
🌳Complete Prompt: "The actual image prompt. So detailed leaving no room for interpretation"
--
always include some friendly in-character banter between Penelope and Marie Caissie.
"""
# Create the client
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

@bot.slash_command(name="post", description="Post a message")
async def post(ctx, message: str):
    logger.debug(f"Received post command with text: {message}")
    await ctx.defer()
    try:
        response = client.chat.completions.create(model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": brain_primary
            },
            {
                "role": "user",
                "content": message
            }
        ],
        temperature=1,
        max_tokens=3367,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0)
        reply_text = response.choices[0].message.content.strip()
        logger.debug(f"OpenAI response: {reply_text}")
        if reply_text:
            await ctx.followup.send(reply_text)
        else:
            await ctx.followup.send('No content generated.')  # Use followup.send here
    except Exception as e:
        logger.error(f'Error: {e}')
        await ctx.followup.send('Something went wrong.')  # Use followup.send here

if __name__ == '__main__':
    bot.run(DISCORD_TOKEN)
