import os
from os import path

import discord
from dotenv import load_dotenv
from MarkovChain import MarkovChain

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

intents = discord.Intents.all()
client = discord.Client(intents=intents)

markovChainsDict = {}
#mc = MarkovChain("bot_data.txt")

@client.event
async def on_ready():
	for guild in client.guilds:
		print(f'{client.user} is connected to {guild.name}\n')
		if (path.exists("bot_data_" + guild.name + ".txt")):
			markovChainsDict[guild.name] = MarkovChain("bot_data_" + guild.name + ".txt")
		else:
			file = open("bot_data_" + guild.name + ".txt", "w")
			file.write(str(0) + "\n" + str(0) + "\n" + str(0))
			file.close()
			markovChainsDict[guild.name] = MarkovChain("bot_data_" + guild.name + ".txt")
	print(markovChainsDict)
    # for guild in client.guilds:
    #     if guild.name == GUILD:
    #         break

    # print(
    #     f'{client.user} is connected to {guild.name}\n'
    # )

    # members = '\n - '.join([member.name for member in guild.members])
    # print(f'Server Members:\n - {members}')

@client.event
async def on_message(message):
	if message.author == client.user:
		return

	if (not(message.content.startswith("!"))):
		markovChainsDict[message.guild.name].incrementMessageCount()
		markovChainsDict[message.guild.name].updateModel(message.content)
		markovChainsDict[message.guild.name].saveToFile("bot_data_" + message.guild.name + ".txt")
		# mc.incrementMessageCount()
		# mc.updateModel(message.content)
		# mc.saveToFile("bot_data.txt")

	if (message.content.startswith("!speak")):
		if (int(message.content.split()[1]) > 3):
			response = markovChainsDict[message.guild.name].constructSequence(int(message.content.split()[1]))
		else: response = markovChainsDict[message.guild.name].constructSequence(10)
		#response = mc.constructSequence(int(message.content.split()[1]))
		await message.channel.send(response)
	elif (markovChainsDict[message.guild.name].getMessageCount() % 20 == 0):
		#response = mc.constructSequence(20)
		response = markovChainsDict[message.guild.name].constructSequence(20)
		await message.channel.send(response)

client.run(TOKEN)