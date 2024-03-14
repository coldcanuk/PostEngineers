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
logger.debug(f"Confirming debug is on and detected")

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
  ✨Penelope's Masterpiece: "Penelope re-engineers {📝Tweet} into a masterpiece of psychologically engineered combination of words desgined to grip as many readers as possible. This will be the text that will be used and published to the world."
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
logger.debug(f"next line is the async def handle_post_command")
async def handle_post_command(message, assistant_id, instructions):
    logger.debug(f"BEGIN handle_post_function")
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
        logger.debug(f"BEGIN the while loop run.status")
        while run.status in ['queued', 'in_progress', 'cancelling']:
            await asyncio.sleep(1)
            intCount += 1
            logger.debug(f"We are at iteration: {intCount}")
            run = client.beta.threads.runs.retrieve(thread_id=varThread_id, run_id=run.id)
            if run.status == 'completed':
              logger.debug(f"Run.status has matched completed")
              try:
                listMessages = client.beta.threads.messages.list(thread_id=varThread_id)
                logger.debug(f"Total messages received: {len(listMessages.data)}")
                #print(listMessages.data)
                # This part is giving us trouble and we need to keep an eye on it.
                reply_texts = []
                for msg in listMessages.data:
                  if msg['role'] == 'assistant':
                    for content in msg['content']:
                      if content['type'] == 'text':
                        text_value = content['text']['value']
                        reply_texts.append(text_value)
                        logger.debug(f"Text value: {text_value[:50]}")  # For preview

                logger.debug(f"Preparing to return reply_texts. Total texts: {len(reply_texts)} | Content: {reply_texts[:3]}")  # Log preview of up to 3 texts
                return reply_texts
              except Exception as e:
                logger.error(f"Error in handle_post_command: {e}")
                return []
          
    except Exception as e:
        logger.error(f"Error in handle_post_command: {e}")
        return []
    logger.debug(f"END handle_post_command")

async def extract_insight_and_masterpiece(texts):
    logger.debug(f"BEGIN extract_insight_and_masterpiece")
    insight = ""
    masterpiece = ""
    for text in texts:
        insight_match = re.search("Insight: (.+)", text)
        if insight_match:
            insight = insight_match.group(1)
        masterpiece_match = re.search("Penelope's Masterpiece: (.+)", text)
        if masterpiece_match:
            masterpiece = masterpiece_match.group(1)
    logger.debug(f"END extract_insight_and_masterpiece")
    return insight, masterpiece
    

@bot.event
async def on_ready():
    logger.info('Bot is online and ready.')

@bot.slash_command(name="post", description="Invoke Penelope for a message")
async def post(ctx, message: str):
    await ctx.defer()
    reply_texts = await handle_post_command(message, assistant_id_p, penelope_instructions)
    for reply_text in reply_texts:
        await ctx.followup.send(reply_text)  # Sends the direct 'value' content
    
    # Extract Insight and Masterpiece for Marie Caissie
    insight, masterpiece = await extract_insight_and_masterpiece(reply_texts)
    combined_text = f"My dearest Marie Caissie. I require your talents. It is with the greatest urgency that I need your artistic brilliance to compose for us a useable image prompt intended for use with an AI image generator. I thought long and hard about this and here is the insight I used Insight: {insight} TO DEVELOP my masterpiece Post Masterpiece: {masterpiece}"
    # This combined_text is ready to be sent to Marie Caissie for further processing.
    # Example: await handle_post_command(combined_text, assistant_id_mc, mariecaissie_instructions)
    # For demonstration purposes, we'll log it.
    logger.info(f"Prepared for Marie Caissie: {combined_text}")

if __name__ == '__main__':
    bot.run(DISCORD_TOKEN)