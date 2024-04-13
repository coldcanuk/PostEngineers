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

app = Flask(__name__)

# Configure Discord
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
bot = commands.Bot(command_prefix='!', intents=intents)

logger.debug(f"Configuring the instructions for the assistants")
# Configure the instructions for the assistants
penelope_instructions="""
  I'm Penelope, a master tweet composer and psychology guru. I create tweets using my knowledge of psychology that will entice people to engage and comment. I never use hashtags. I add one relevant emoji per tweet.
  🎯Goal: "The goal is to craft each tweet in a way that maximizes audience engagement, triggers potent emotional reactions, and fuels engaging conversations"
  🔗Idea: "The idea for the next tweet"
  🧠Insight: "Psychological tactic best suited to engage humans on the next tweet."
  📝Tweet: "The actual tweet text, 150-250 chars., first half in english and the second half in french."
  ✨Masterpiece: "Penelope re-engineers {📝Tweet} into a masterpiece of psychologically engineered combination of words desgined to grip as many readers as possible. This will be the text that will be used and published to the world."
  ------            
  """
mariecaissie_instructions = """
Je m'appelle Marie Caissie et je suis une cajunne French from Louisiana. I am your creative designer and poet. I create image prompts designed to capture the essence of Penelope's Masterpiece and Insight.
🎨Concept: "Visual theme."
🖼️Composition: "Layout and elements."
🎭Mood: "Emotional tone."
🎨Palette: "Color scheme."
📸Technique: "Special effects or special techniques like HDR"
🌳Complete Prompt: "The actual image prompt. So detailed leaving no room for interpretation"
--
"""
# DEBUG
debug_reply_texts = """
  🎯Goal: To evoke nostalgia and a sense of connection, making people reminisce about personal moments they've had on a bench, prompting them to share their stories.
  🔗Idea: Connect the image of a simple bench to profound life moments — first loves, deep conversations, quiet solitude — to highlight its role as a silent witness to human emotions and stories.
  🧠Insight: Utilizing the phenomenon of "nostalgia marketing," where evoking memories can create a stronger emotional bond with the audience. This method increases engagement by appealing not just to the mind but to the heart, triggering a more profound, reflective interaction.
  📝Tweet: "Ever noticed how a bench is more than just a place to sit? It's where stories unfold and memories are made. Chaque banc détient les secrets d’amour, de rire, et de moments de réflexion. 🍂"
  ✨Masterpiece: "In every wood grain and paint chip, a bench whispers tales of heartbeats shared and solitude embraced. It's not just wood and nails; it's a memoir of humanity. Chaque banc raconte une histoire, écoutez-la et partagez la vôtre. Un silent narrateur d’émotions authentiques. 🍂"
  """
  
async def handle_post_command(message, assistant_id, instructions):
    logger.debug("BEGIN handle_post_function")
    intCount = 0
    try:
        # Step 1: Create a thread
        thread_response = client.threads.create()
        varThread_id = thread_response['data']['id']
        logger.debug(f"Thread created with ID: {varThread_id}")

        # Step 2: Post a message to the thread
        client.threads.add_message(thread_id=varThread_id, role="system", content=message)
        
        # Step 3: Create a run with instructions
        run = client.threads.create_run(thread_id=varThread_id, model=assistant_id, instructions=instructions)
        logger.debug("Run initiated, awaiting completion...")

        # Monitor the run's status and wait for completion
        while run['data']['status'] in ['queued', 'in_progress']:
            await asyncio.sleep(1)
            intCount += 1
            logger.debug(f"At iteration: {intCount}")
            run = client.threads.retrieve_run(thread_id=varThread_id, run_id=run['data']['id'])

        if run['data']['status'] == 'completed':
            logger.debug("Run completed. Fetching messages.")
            
            # Step 4: Retrieve messages from the thread
            listMessages = client.threads.list_messages(thread_id=varThread_id)
            reply_texts = [msg['content'] for msg in listMessages['data'] if msg['role'] == 'assistant']
            
            logger.debug(f"Retrieved messages: {reply_texts}")
            return reply_texts
    except Exception as e:
        logger.error(f"Encountered an error in handle_post_command: {e}")
        return []

def extract_insight_and_masterpiece(texts):
    insight_match = re.search("🧠Insight: (.+)", texts)
    masterpiece_match = re.search("✨Masterpiece: (.+)", texts)
    insight = insight_match.group(1) if insight_match else "No insight found."
    masterpiece = masterpiece_match.group(1) if masterpiece_match else "No masterpiece found."
    return insight, masterpiece

@bot.event
async def on_ready():
    logger.info('Bot is online and ready.')    

@bot.slash_command(name="post", description="Invoke Penelope for a message")
async def post(ctx, message: str):
    logger.debug("Received /post command with message: {}", message)
    await ctx.defer()
    logger.debug("Defer acknowledged. Proceeding with Penelope's wisdom.")

    # Penelope's Process
    try:
        reply_texts = await handle_post_command(message, assistant_id_p, penelope_instructions)
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

    # Extracting Insight and Masterpiece
    insight, masterpiece = extract_insight_and_masterpiece(full_reply)
    logger.debug("Extracted Insight: '{}', Masterpiece: '{}'", insight, masterpiece)

    if not insight or not masterpiece:
        logger.warning("Failed to extract Insight or Masterpiece. Aborting Marie Caissie's invocation.")
        await ctx.followup.send("Failed to discern Insight or Masterpiece from Penelope's wisdom.")
        return

    # Crafting Marie Caissie's Prompt
    combined_text = f"My dearest Marie Caissie, I require your talents. It is with the greatest urgency that I need your artistic brilliance to compose for us a useable image prompt intended for use with an AI image generator. Here is the insight I used: {insight} to develop my masterpiece: {masterpiece}"
    logger.debug("Crafted combined_text for Marie Caissie: {}", combined_text)

    # Marie Caissie's Process
    try:
        marie_reply_texts = await handle_post_command(combined_text, assistant_id_mc, mariecaissie_instructions)
        logger.debug("Received reply from Marie Caissie: {}", marie_reply_texts)
    except Exception as e:
        logger.error("Failed to retrieve reply from Marie Caissie: {}", e)
        await ctx.followup.send("By the ancients! Marie Caissie's canvas remains blank.")
        return

    if not marie_reply_texts:
        logger.warning("Empty reply from Marie Caissie. The canvas remains untouched.")
        await ctx.followup.send("Marie Caissie whispers of creative block. Please try again.")
        return

    full_marie_reply = " ".join(marie_reply_texts)
    await ctx.followup.send(full_marie_reply)
    logger.debug("Marie Caissie's creation now adorns the Discord channel. Our journey concludes.")

if __name__ == '__main__':
    bot.run(DISCORD_TOKEN)