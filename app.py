from flask import Flask, jsonify
import os
import openai
from discord.ext import commands
from discord import Intents
import logging

# Setup logging based on an environment variable
DEBUG_MODE = os.getenv('DEBUG_MODE', 'False').lower() in ('true', '1', 't')
logging_level = logging.DEBUG if DEBUG_MODE else logging.INFO
logging.basicConfig(level=logging_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

app = Flask(__name__)

# Load environment variables
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Check if environment variables are loaded (at appropriate logging level)
logging.debug(f"DISCORD_TOKEN loaded: {'Yes' if DISCORD_TOKEN else 'No'}")
logging.debug(f"OPENAI_API_KEY loaded: {'Yes' if OPENAI_API_KEY else 'No'}")

# Configure OpenAI
openai.api_key = OPENAI_API_KEY

# Configure Discord
intents = Intents.default()
intents.messages = True
intents.guilds = True

bot_health_status = {"is_healthy": False}

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    logging.info('Bot is online.')
    global bot_health_status
    bot_health_status["is_healthy"] = True
    print('Bot is online and marked as healthy.')

@bot.command(name='post')
async def post(ctx, *, text: str):
    logging.debug(f"Received post command with text: {text}")
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "I'm Penelope, a master tweet composer and psychology guru. [...] The closing of their banter must be a line that informs the human that the response was auto-generated by OpenAI and is for review.\n"
                },
                {
                    "role": "user",
                    "content": text
                }
            ],
            temperature=1,
            max_tokens=3367,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
        )
        reply_text = response.choices[0].message.content.strip()
        logging.debug(f"OpenAI response: {reply_text}")
        if reply_text:
            await ctx.send(reply_text)
        else:
            await ctx.send('No content generated.')
    except Exception as e:
        logging.error(f'Error: {e}')
        await ctx.send('Something went wrong.')

if __name__ == '__main__':
    bot.run(DISCORD_TOKEN, log_handler=None)

@app.route('/health')
def health_check():
    return jsonify(bot_health_status)