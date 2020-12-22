import os

import discord
from discord.ext import commands
from dotenv import load_dotenv
from MarkovChain import MarkovChain

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

intents = discord.Intents.all()
client = discord.Client(intents=intents)

mc = MarkovChain("bot_data.txt")

@client.event
async def on_ready():
    for guild in client.guilds:
        if guild.name == GUILD:
            break

    print(
        f'{client.user} is connected to {guild.name}\n'
    )

    members = '\n - '.join([member.name for member in guild.members])
    print(f'Server Members:\n - {members}')

@client.event
async def on_message(message):
	if message.author == client.user:
		return

	if (not(message.content.startswith("!"))):
		mc.incrementMessageCount()
		mc.updateModel(message.content)
		mc.saveToFile("bot_data.txt")

	if (message.content.startswith("!speak")):
		response = mc.constructSequence(int(message.content.split()[1]))
		await message.channel.send(response)
	elif (mc.getMessageCount() % 20 == 0):
		response = mc.constructSequence(20)
		await message.channel.send(response)

client.run(TOKEN)