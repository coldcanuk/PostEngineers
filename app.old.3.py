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
  
logger.debug(f"next line is the async def handle_post_command")

async def handle_post_command(message, assistant_id):
    logger.debug("BEGIN handle_post_function")
    try:
        # Initiating a thread and run with the assistant in one action
        run_response = client.beta.threads.create_and_run(
            assistant_id=assistant_id,
            thread={
                "messages": [
                    {"role": "user", "content": message}
                ]
            }
        )
        varRun_id = run_response.data.id
        varThread_id = run_response.data.thread_id
        logger.debug(f"Run initiated with assistant {assistant_id}")
        logger.debug(f"The run ID is: {varRun_id}")
        logger.debug(f"The thread ID is:{varThread_id}")
        logger.debug("awaiting completion...")
        # The digital vigil begins
        intCount = 0
        logger.debug(f"The digit vigil begins at iteration count: {intCount}")
        logger.debug("BEGIN the while loop run.status")
        while run_response.data.status in ['queued', 'in_progress', 'cancelling']:
            await asyncio.sleep(1)
            intCount += 1
            logger.debug(f"We are at iteration: {intCount}")
            run_response = client.beta.threads.runs.retrieve(thread_id=varThread_id, run_id=varRun_id)
            if run_response.data.status == 'completed':
                logger.debug("Run.status has matched completed")
                break  # Exiting the loop as our quest for wisdom has reached fruition

        # Retrieving the fruits of our patience
        if run_response.data.status == 'completed':
            reply_texts = [msg.content for msg in run_response.data.messages if msg.role == 'assistant']
            logger.debug(f"Retrieved messages: {reply_texts}")
        else:
            logger.warning("The muse remains silent or the query was lost in the cosmos.")
            reply_texts = []

        return reply_texts

    except Exception as e:
        logger.error(f"Encountered an error in handle_post_command: {e}")
        return []

# Extract Insight and Masterpiece from Penelope's reply and return them as insight, masterpiece
def extract_insight_and_masterpiece(texts):
    logger.debug(f"BEGIN extract_insight_and_masterpiece")
    print("Debugging texts:", texts)  # Temporarily added for debugging
    insight = ""
    masterpiece = ""
    for text in texts:
        print("Processing text:", text)  # Temporarily added for debugging
        insight_match = re.search("Insight: (.+)", text)
        if insight_match:
            insight = insight_match.group(1)
        masterpiece_match = re.search("Masterpiece: (.+)", text)
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
    debug_object_reply = ""
    intCount2 = 0
    for reply_text in reply_texts:
        #logger.debug(f"Reply iteration: {intCount2} ")
        await ctx.followup.send(reply_text)  # Sends the direct 'value' content
        debug_object_reply = debug_object_reply + reply_text
        logger.debug(f" reply_text had something and we appended it to debug_object_reply")
    logger.debug(f"sent text to Discord. Now setting combined_text as the user prompt for Marie Caissie")
    logger.info(f"Creating our custom object")
    insight = "Insight: 1 DEBUG SET"
    masterpiece = "Masterpiece: 2 DEBUG SET"
    logger.info(f"Insight's length is: {len(insight)}")
    logger.info(f"Masterpiece's length is: {len(masterpiece)}")
    combined_text = "I am the DEBUG combined_text of " + insight + " and the " + masterpiece + "   "
    logger.info(f"Prepared for Marie Caissie, the output of combined_text is: {combined_text}")
    logger.debug(f"reply_text's type is: {type(reply_texts)}")
    logger.debug(f"debug_object_reply's type is: {type(debug_object_reply)}")
    logger.debug(f"debug_reply_texts length is: {len(debug_reply_texts)}")
    logger.debug(f"reply_texts length is: {len(reply_texts)}")
    logger.debug(f"debug_object_reply length is: {len(debug_object_reply)}")
    logger.debug(f"-----------------------------")
    logger.debug(f"-----------------------------")
    logger.debug(f"attempting to print the object.......")
    #logger.debug(f"......: {(debug_object_reply)}")
    #logger.debug(debug_object_reply)
    logger.debug(f"......: {str(debug_object_reply)}")                 
    data_dict = {}
    for line in debug_object_reply:
      # Assuming each line starts with an emoji followed by the key name and the text
      key, value = line.split(':', 1)
      # Removing the leading emoji and trimming whitespace for the key
      key = key.strip()[1:].strip()
      # Trimming whitespace for the value
      value = value.strip()
      data_dict[key] = value

    # Serializing the dictionary to a JSON formatted string
    penelope_reply_data = json.dumps(data_dict, indent=4, ensure_ascii=False)
    print (penelope_reply_data)
    
    #insight = data_dict.get('Insight', 'Default Insight')
    #masterpiece = data_dict.get('Masterpiece', 'Default Masterpiece')


        
    #
    # print(f"{debug_object_reply}")
    #
    #logger.debug(f"debug_object_reply: {str(debug_object_reply)}")
    #print(debug_object_reply)
    #insight, masterpiece = extract_insight_and_masterpiece(debug_reply_texts) # Sends the direct 'value' content to be parse for Marie Caissie
    logger.info(f"new Insight's length is: {len(insight)}")
    logger.info(f"new Masterpiece's length is: {len(masterpiece)}")
  



    
    #print(foo)
    #print(reply_texts)
    

    


#
    #combined_text = f"My dearest Marie Caissie. I require your talents. It is with the greatest urgency that I need your artistic brilliance to compose for us a useable image prompt intended for use with an AI image generator. I thought long and hard about this and here is the insight I used Insight: {insight} TO DEVELOP my masterpiece Post Masterpiece: {masterpiece}"
    #logger.debug(f"the value of insight is: {insight}")
    #logger.debug(f"the value of masterpiece is: {masterpiece}")
    #combined_text = f"My dearest Marie Caissie. I require your talents. It is with the greatest urgency that I need your artistic brilliance to compose for us a useable image prompt intended for use with an AI image generator. I thought long and hard about this and here is the insight I used Insight: {insight} TO DEVELOP my masterpiece Post Masterpiece: {masterpiece}"
    # This combined_text is ready to be sent to Marie Caissie for further processing.
    # Example: await handle_post_command(combined_text, assistant_id_mc, mariecaissie_instructions)
    # For demonstration purposes, we'll log it.
    #print("Debug reply_text content: ", reply_texts)

if __name__ == '__main__':
    bot.run(DISCORD_TOKEN)