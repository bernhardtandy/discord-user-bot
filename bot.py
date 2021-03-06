import os
from os import path

import discord
from dotenv import load_dotenv
from MarkovChain import MarkovChain
import boto3
import time
import asyncio
import lz4.frame

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.all()
client = discord.Client(intents=intents)

markovChainsDict = {}

s3 = boto3.resource('s3')

async def file_upload_task():
	await client.wait_until_ready()
	while client.is_ready():
		try: 
			for key in markovChainsDict.keys():
				if (path.exists("bot_data_" + key + ".txt")):
					# s3.Bucket('discorduserbot2').upload_file(Key="bot_data_" + key + ".txt", Filename="bot_data_" + key + ".txt")

					data_file = open("bot_data_" + key + ".txt", "r")
					data_string = data_file.read()
					data_file.close()

					encoded_data = data_string.encode("utf-8")
					compressed = lz4.frame.compress(encoded_data)

					with lz4.frame.open("bot_data_" + key + "_compressed", mode="w") as file:
						file.write(compressed)

					print("Successfully compressed bot_data_" + key + ".txt")
					s3.Bucket('discorduserbot2').upload_file(Key="bot_data_" + key + "_compressed", Filename="bot_data_" + key + "_compressed")

			await asyncio.sleep(21600)
		except Exception as e:
			print(str(e))
			await asyncio.sleep(21600)


@client.event
async def on_ready():
	for guild in client.guilds:
		print(f'{client.user} is connected to {guild.name}\n')
		if (not(path.exists("bot_data_" + guild.name + ".txt"))):
			# s3.Bucket('discorduserbot2').download_file(Key="bot_data_" + guild.name + ".txt", Filename="bot_data_" + guild.name + ".txt")
			s3.Bucket('discorduserbot2').download_file(Key="bot_data_" + guild.name + "_compressed", Filename="bot_data_" + guild.name + "_compressed")

			with lz4.frame.open("bot_data_" + guild.name + "_compressed", mode="r") as file:
				compressed = file.read()
			decompressed = lz4.frame.decompress(compressed)
			decoded_data = decompressed.decode("utf-8")

			data_file = open("bot_data_" + guild.name + ".txt", "w")
			data_file.write(decoded_data)
			data_file.close()
			print("Successfully decompressed bot_data_" + guild.name + ".txt")

		if (path.exists("bot_data_" + guild.name + ".txt")):
			markovChainsDict[guild.name] = MarkovChain("bot_data_" + guild.name + ".txt")
		else:
			file = open("bot_data_" + guild.name + ".txt", "w")
			file.write(str(0) + "\n" + str(0) + "\n" + str(0) + "\n" + str(20))
			file.close()
			markovChainsDict[guild.name] = MarkovChain("bot_data_" + guild.name + ".txt")
	print(markovChainsDict)


@client.event
async def on_message(message):
	if message.author == client.user:
		return

	if (not(message.guild.name in markovChainsDict.keys())):
		markovChainsDict[message.guild.name] = MarkovChain("empty.txt")

	if (not(message.content.startswith("!")) and "@" not in message.content):
		markovChainsDict[message.guild.name].incrementMessageCount()
		markovChainsDict[message.guild.name].updateModel(message.content)
		markovChainsDict[message.guild.name].saveToFile("bot_data_" + message.guild.name + ".txt")

	if (message.content.startswith("!dubhelp")):
		response = "!speak <max_length> - DUB sends a message with up to <max_length> words (default 100) \n"
		response += "!frequency <number> - DUB will !speak in a channel every <number> messages (default 20, minimum 1, use -1 to stop bot from automatically speaking)" 
		await message.channel.send(response)
		return

	if (message.content.startswith("!frequency")):
		if (len(message.content.split()) > 1 and (int(message.content.split()[1]) > 0 or int(message.content.split()[1]) == -1)):
			markovChainsDict[message.guild.name].setSpeakFrequency(int(message.content.split()[1]))
		

	if (message.content.startswith("!speak")):
		if (len(message.content.split()) > 1 and int(message.content.split()[1]) > 3):
			response = markovChainsDict[message.guild.name].constructSequence(int(message.content.split()[1]))
		else: response = markovChainsDict[message.guild.name].constructSequence(100)

		await message.channel.send(response)

	elif (markovChainsDict[message.guild.name].getSpeakFrequency() > 0 and markovChainsDict[message.guild.name].getMessageCount() % markovChainsDict[message.guild.name].getSpeakFrequency() == 0):
		response = markovChainsDict[message.guild.name].constructSequence(100)

		await message.channel.send(response)


client.loop.create_task(file_upload_task())
client.run(TOKEN)