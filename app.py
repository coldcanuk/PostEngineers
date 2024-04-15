import sys
import os
import re
import asyncio
import time
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
version="1.ah"
# Create the OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)
# Setup logging
DEBUG_MODE = os.getenv('DEBUG_MODE', 'False').lower() in ('true', '1', 't', 'y')
log_level = "DEBUG" if DEBUG_MODE else "INFO"
logger.remove()  # Removes all handlers
logger.add(sys.stdout, level=log_level)  # Re-add with the desired level
app = Flask(__name__)
# Configure Discord
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
bot = commands.Bot(command_prefix='!', intents=intents)
logger.debug(f"This is version: {version}")
logger.info("Finished setting up intents.")
#
def transform_to_json(raw_data):
  try:
    # Initialize an empty list to hold our transformed objects
    transformed_data = []    
    # Strip off the square brackets and split the string into its components
    entries = raw_data[0].strip('[]').split('\n\n')
    # Initialize an empty dictionary to construct our JSON object
    json_object = {}
    logger.debug("Begin for loop")
    for entry in entries:
    # Split each entry into key-value pairs
      key, value = entry.split(': ', 1)
      json_object[key] = value
        
    # Append the transformed object to our list
    transformed_data.append(json_object)
        
    # Convert our list of objects into a JSON string
    logger.debug("Begin conversion of our list of objects into a JSON string")
    json_data = json.dumps(transformed_data, ensure_ascii=False)
    logger.info("Successfully transformed the data to JSON.")
    return json_data
  except Exception as e:
    logger.error(f"An error occurred during transformation: {e}")
    return None
      
def start_createandrun(message, assistant_id):
    """
    This function starts the create_and_run
    
    Parameters:
    - message (str): The content of the message to be processed by the assistant.
    - assistant_id (str): The unique identifier of the assistant to which the message is sent.
    
    Returns 200ok
    """ 
    logger.debug("BEGIN start_createandrun")
    try:
      response = client.beta.threads.create_and_run(
        assistant_id=assistant_id,
        thread={"messages": [{"role": "user", "content": message}]}
      )
      logger.debug(f"Run initiated with assistant {assistant_id}, Thread ID: {response.thread_id}")
      strThreadID=response.thread_id
      logger.debug(f"Successfully create variable strThreadID and populated it:  {strThreadID}")
      strResponseID=response.id
      logger.debug(f"Successfully create variable strResponseID and populated it:  {strResponseID}")
      return strThreadID, strResponseID
    except Exception as e:
      logger.error("Encountered an error in handle_post_command with client.beta.threads.create_and_run")
      raise RuntimeError (f"Hit an error in the handle_post_command function with client.beta.threads.create_and_run:  {e}")

#
# BEGIN Section Event Handlers
#

# event on_ready
@bot.event
async def on_ready():
    logger.info('Bot is online and ready.')

# slash_command post
@bot.slash_command(name="post", description="Invoke Penelope for a message")
async def post(ctx, message: str):
    logger.debug("Received /post command with message: {}", message)
    await ctx.defer()
    logger.debug("Defer acknowledged. Proceeding with Penelope's wisdom.")
    intDelay=1
    intMaxDelay=120
    intStep=0
    # Penelope's create_and_run thread with openAI
    try:
      startmeup = start_createandrun(message, assistant_id_p)
      strThreadID=startmeup[0]
      strResponseID=startmeup[1]
      logger.debug(f"return strThreadID:  {strThreadID}  and strResponseID:  {strResponseID}")
    except Exception as e:
      await ctx.followup.send("Zap. Failed to start the create and run function")
      raise RuntimeError(f"Failed to start the create and run function:   {e}")
    # List Penelope's Run
    try:
      runsP = client.beta.threads.runs.retrieve(thread_id=strThreadID,run_id=strResponseID)
      status = runsP.status
    except Exception as e:
      await ctx.followup.send("Zap. Failed to list Penelope's Runs!")
      raise RuntimeError(f"Failed to list Penelope's Runs:    {e}")
    while status != "completed":
      logger.debug(f"Inside while loop at interation: {intStep}  and using a delay of:  {intDelay}")
      runsP = client.beta.threads.runs.retrieve(thread_id=strThreadID,run_id=strResponseID)
      status = runsP.status
      await asyncio.sleep(intDelay)
      intDelay = min(intDelay * 2, intMaxDelay)
      intStep += 1
      if status == "completed":
        try:
          getRun = client.beta.threads.messages.list(strThreadID)
          #await ctx.followup.send(getRun)
          # logger.debug("Completed send of raw output to Discord.")
          logger.debug("Completed getting the messages list as getRun")
          logger.debug("Breaking out of while loop")
          break
        except Exception as e:
          await ctx.followup.send("Zap, failed at retrieving the run!")
          logger.debug("Failed at retrieving the run!")
          raise RuntimeError(f"Failed to retrieve run using {strThreadID} and {strResponseID}")
    try:
        logger.debug("Formatting the reply so we can zero in on our content.")
        Preply_texts = [
          content_block.text.value for msg in getRun.data 
            if msg.role == 'assistant' 
              for content_block in msg.content 
                if content_block.type == 'text'
        ]
        await ctx.followup.send(Preply_texts)
    except Exception as e:
        logger.debug(f"Failed to format Preply_texts or & send to Discord:  {e}")
        await ctx.followup.send("Failed to format Preply_texts or & send to Discord, weird eh")
    logger.debug("Next, we are going to try to format the output into JSON")
    try:
      Preply_json = transform_to_json(Preply_texts)
      logger.debug(f"This is the length of Preply_json: {len(Preply_json)}")
      #print(Preply_json)
    except Exception as e:
      logger.debug("Failed to transform into JSON")
      raise RuntimeError("Failed to transform into JSON")
    await ctx.followup.send(Preply_json)
    objPreply = json.loads(Preply_json)
    strInsight = objPreply[0]['🎯Goal']
    #fullOut = f"this is the length for 🎯Goal:  {len(strInsight)}"
    #await ctx.followup.send(fullOut)
    """
    if not reply_texts:
        logger.warning("Empty reply from Penelope. Aborting the quest.")
        await ctx.followup.send("Penelope seems to be lost in thought. Please try again.")
        return
    logger.debug("Getting ready to dispatch Penelope's reply to Discord")
    full_reply = " ".join(reply_texts)
    await ctx.followup.send(full_reply)
    logger.debug("Dispatched Penelope's reply to the high seas of Discord.")
    """
#
# END Section Event Handlers
#

if __name__ == '__main__': # Conditional check to confirm it is the main app running
    bot.run(DISCORD_TOKEN)