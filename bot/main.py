import discord
from discord.ext import commands, tasks

import random
import os

import asyncio

# client = discord.Client(intents=intents)
usernames = []


def command_prefix(bot, message):
    if message.guild is None:
        return ''
    else:
        return '$'


TOKEN = os.getenv("DISCORD_TOKEN")

# Add users with errors to blacklist so that we don't keep making API calls to change these users.
memberBlacklist = []

# Get more advanced intents. Allows us to get offline users too, and check additional stuff
intents = discord.Intents.default()
intents.typing = False
intents.presences = True
intents.members = True

bot = commands.Bot(command_prefix=command_prefix, intents=intents)

bot.load_extension("maincog")
bot.run(TOKEN)
