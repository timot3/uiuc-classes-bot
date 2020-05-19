from discord.ext import commands
import discord

TOKEN = ''

with open('embed-config.txt', 'r') as f:
    TOKEN = f.readline()


bot.run(TOKEN.strip())
