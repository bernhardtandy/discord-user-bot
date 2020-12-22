import os
from os import path

import discord
from dotenv import load_dotenv
from MarkovChain import MarkovChain

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.all()
client = discord.Client(intents=intents)

markovChainsDict = {}

@client.event
async def on_ready():
	for guild in client.guilds:
		print(f'{client.user} is connected to {guild.name}')

@client.event
async def on_message(message):
	if message.author == client.user:
		return

	if (not(message.guild.name in markovChainsDict.keys())):
		markovChainsDict[message.guild.name] = MarkovChain("empty.txt")

	if (not(message.content.startswith("!"))):
		markovChainsDict[message.guild.name].incrementMessageCount()
		markovChainsDict[message.guild.name].updateModel(message.content)
		markovChainsDict[message.guild.name].saveToFile("bot_data_" + message.guild.name + ".txt")

	if (message.content.startswith("!speak")):
		if (len(message.content.split()) > 1 and int(message.content.split()[1]) > 3):
			response = markovChainsDict[message.guild.name].constructSequence(int(message.content.split()[1]))
		else: response = markovChainsDict[message.guild.name].constructSequence(10)

		await message.channel.send(response)

	elif (markovChainsDict[message.guild.name].getMessageCount() % 20 == 0):
		response = markovChainsDict[message.guild.name].constructSequence(20)

		await message.channel.send(response)

client.run(TOKEN)