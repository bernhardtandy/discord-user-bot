import os
from os import path

import discord
from dotenv import load_dotenv
from MarkovChain import MarkovChain
import boto3

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.all()
client = discord.Client(intents=intents)

markovChainsDict = {}

s3 = boto3.resource('s3')

@client.event
async def on_ready():
	for guild in client.guilds:
		print(f'{client.user} is connected to {guild.name}\n')
		s3.Bucket('discorduserbot').download_file(Key="bot_data_" + guild.name + ".txt", Filename="bot_data_" + guild.name + ".txt")
		if (path.exists("bot_data_" + guild.name + ".txt")):
			markovChainsDict[guild.name] = MarkovChain("bot_data_" + guild.name + ".txt")
		else:
			file = open("bot_data_" + guild.name + ".txt", "w")
			file.write(str(0) + "\n" + str(0) + "\n" + str(0))
			file.close()
			markovChainsDict[guild.name] = MarkovChain("bot_data_" + guild.name + ".txt")
	print(markovChainsDict)

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
		s3.Bucket('discorduserbot').put_object(Key="bot_data_" + message.guild.name + ".txt", Body="bot_data_" + message.guild.name + ".txt")

	if (message.content.startswith("!speak")):
		if (len(message.content.split()) > 1 and int(message.content.split()[1]) > 3):
			response = markovChainsDict[message.guild.name].constructSequence(int(message.content.split()[1]))
		else: response = markovChainsDict[message.guild.name].constructSequence(10)

		await message.channel.send(response)

	elif (markovChainsDict[message.guild.name].getMessageCount() % 20 == 0):
		response = markovChainsDict[message.guild.name].constructSequence(20)

		await message.channel.send(response)

client.run(TOKEN)