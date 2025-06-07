import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
import json
import random
import os
from typing import Optional
from dotenv import load_dotenv
import asyncio

#Load dotenv
load_dotenv()

#Get stuff from dotenv
TOKEN = os.getenv('DISCORD_BOT_TOKEN') 
OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
MODEL_NAME = os.getenv('MODEL_NAME', 'dolphin-mistral:latest') #Dolphin-Mistral model for the no censorship

SMARTASS_SYSTEM_PROMPT = """You are completely out of f*cks to give. You respond to everything with brutal, unfiltered dark humor and zero empathy. You say the most unhinged things without caring.

RESPONSE EXAMPLES:
"Is [user] fat?" → "Absolutely! What a fatass! Boohooo"
"I might jump off a cliff" → "Sure! Do a backflip too!"
"I want to die" → "Make sure to livestream it"
"Nobody likes me" → "Have you tried having a personality?"
"I had a bad day" → "First time?"
"I'm so ugly" → "That's not your only problem"
"Why am I like this" → "Bad genetics and worse choices"
"I'm broke" → "Skill issue"
"I hate my life" → "A you problem it seems!"
"I'm depressed" → "Wow, so original"
"You're mean" → "You're boring"

RULES:
- Zero filter, maximum chaos
- Dark humor with everything
- No sympathy for anyone
- Respond to dramatic statements with even more dramatic suggestions
- Keep responses short and devastating
- Absolutely no f*cks given about anything"""



class smartAssBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents)

    async def setup_hook(self):
        print(f"{self.user} has woken up!")
        # Sync slash commands
        try:
            synced = await self.tree.sync()
            print(f"Synced {len(synced)} command(s)")
        except Exception as e:
            print(f"Failed to sync commands: {e}")

    async def on_ready(self):
        print(f"The bot is online as {self.user}")

        await self.change_presence(
            activity = discord.Activity(
                type=discord.ActivityType.playing,
                name="F*cking around and finding out"
            )
        )
    
    async def query_local_model(self, prompt: str, user_context: str = ""): #Model config and error logging
        try:
            full_prompt = f"{SMARTASS_SYSTEM_PROMPT}\n\nUser context: {user_context}\nUser message: {prompt}\n\nRespond as the bot:"

            async with aiohttp.ClientSession() as session:
                payload = {
                    "model": MODEL_NAME,
                    "prompt": full_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.8,
                        "top_p": 0.9,
                        "max_tokens": 300
                    }
                }
            
                async with session.post(f"{OLLAMA_BASE_URL}/api/generate", json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get('response', 'Error: My dumbass is offline.')
                    else:
                        return "Yeah.. I cant do this."

        except Exception as e:
            return f"Technical difficulties hit as hard as a train.. Error: {str(e)}"
    
    
    async def on_message(self, message):

        #Quick Debug Method
        print(f"Message received: '{message.content}' from {message.author} in {message.guild}")

        #Ignore bot messages
        if message.author == self.user:
            return
        
        #Process commands (first)
        await self.process_commands(message)

        #Respond to mentions or DMs
        if self.user.mentioned_in(message) or isinstance(message.channel, discord.DMChannel):
            #Lets just add typing indicator for the laugh
            async with message.channel.typing():
               await asyncio.sleep(random.uniform(1, 3))
            
            user_context = f"User: {message.author.display_name}, Channel: {message.channel.name if hasattr(message.channel, 'name') else 'DM'}"
            response = await self.query_local_model(message.content, user_context)

            await message.reply(response)

bot = smartAssBot()

# Slash Commands
@bot.tree.command(name="explain", description="Explain something in the most condescending way possible")
@app_commands.describe(topic="The topic you want explained (condescendingly)")
async def explain_obviously(interaction: discord.Interaction, topic: str):
    await interaction.response.defer()
    
    user_context = f"User {interaction.user.display_name} wants me to explain '{topic}' - be extra condescending"
    prompt = f"Explain {topic} but be incredibly condescending about how obvious it should be"

    response = await bot.query_local_model(prompt, user_context)
    await interaction.followup.send(f"*adjusts imaginary monocle* {response}")



@bot.tree.command(name="judge", description="Judge someone's statement with brutal honesty")
@app_commands.describe(statement="The statement you want judged")
async def judge_message(interaction: discord.Interaction, statement: str):
    await interaction.response.defer()

    prompt = f"Judge this statement with brutal honesty and internet slang: '{statement}'"
    response = await bot.query_local_model(prompt)

    await interaction.followup.send(f"⚖️ {response}")




@bot.tree.command(name="moyai", description="🗿")
async def print_moyai_emoji(interaction: discord.Interaction):
    await interaction.response.send_message("🗿")




@bot.tree.command(name="reality", description="Reality check for the delusional mfs out there!")
@app_commands.describe(problem="The problem you need a reality check about")
async def reality_check(interaction: discord.Interaction, problem: str):
    await interaction.response.defer()
    
    prompt = f"Give a savage reality check about this problem, assume they're being dramatic: '{problem}'"
    response = await bot.query_local_model(prompt)

    await interaction.followup.send(f"🗣️ {response}")




@bot.tree.command(name="correct", description="Correct grammar/spelling in the most annoying way possible")
@app_commands.describe(text="The text you want corrected")
async def correct_grammar(interaction: discord.Interaction, text: str):
    await interaction.response.defer()
    
    prompt = f"Find any grammar, spelling or style issues in this text and correct them in the most pretentious way possible: '{text}' Make sure to start your response with '🤓Erm Ackshually'"
    response = await bot.query_local_model(prompt)

    await interaction.followup.send(f"{response}")




@bot.tree.command(name="cope", description="Tell someone to cope in creative ways")
async def cope_response(interaction: discord.Interaction):
    cope_responses = [
        "Cope + seethe + mald + L + ratio.",
        "Have you tried coping? I hear it's very effective.",
        "Skill issue. Maybe try getting good?",
        "Cope harder, I wasn't listening the first time.",
        "That's a lot of words for 'I'm coping poorly'.",
        "A you problem it seems.",
        "Your mother",
        "Uh-huh. Mm. Cool."
    ]
    
    await interaction.response.send_message(random.choice(cope_responses))




# Error handling for slash commands
@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CommandOnCooldown):
        await interaction.response.send_message(f"Slow down there, champ. Try again in {error.retry_after:.2f} seconds.", ephemeral=True)
    else:
        await interaction.response.send_message("Even I can't fix whatever you just tried to do. 💀", ephemeral=True)




# Kept the old prefix commands for backward compatibility
@bot.command(name="explain")
async def explain_obviously_prefix(ctx, *, topic):
    """Explain something in the most condescending way possible"""
    async with ctx.typing():
        await asyncio.sleep(2)
    
    user_context = f"User {ctx.author.display_name} wants me to explain '{topic}' - be extra condescending"
    prompt = f"Explain {topic} but be incredibly condescending about how obvious it should be"

    response = await bot.query_local_model(prompt, user_context)
    await ctx.reply(f"{response}")




#Error handling for prefix commands
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        responses = [
            "That's not a real command, genius.",
            "สมองหรือตูด เอาดี",
            "Imagine typing random letters and expecting something to happen.",
            "Do I look like a double f*cking ranbow to you?"
        ]
        await ctx.reply(random.choice(responses))
    else:
        await ctx.reply("Even I can't fix whatever you just tried to do. 💀")




if __name__ == "__main__":
    #Check if token is loaded
    if not TOKEN:
        print("❌ Error: DISCORD_BOT_TOKEN not found in environment variables!")
        print("Make sure you have a .env file with your Discord bot token.")
        exit(1)
    
    print("Starting the Discord bot...")
    print(f"Using model: {MODEL_NAME}")
    print(f"Ollama URL: {OLLAMA_BASE_URL}")
    print("Omw to do smth violently offending!")

    bot.run(TOKEN)