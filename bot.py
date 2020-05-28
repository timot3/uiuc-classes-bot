from utils.functions import send_class
from discord.ext import commands
import discord
import re

TOKEN = ''

with open('config.txt', 'r') as f:
    TOKEN = f.readline().strip()

bot = commands.Bot(command_prefix=('classbot ', 'Classbot '), case_insensitive=True, help_command=None)


# What to do when bot is online
@bot.event
async def on_ready():
    # Log events to console.
    print('Bot online.')
    print("Name: {}".format(bot.user.name))
    print("ID: {}".format(bot.user.id))
    # Set status
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name='classbot info'))


# Parse every message
@bot.event
async def on_message(message):
    # Make sure the bot does not respond to its own messages.
    if message.author.bot:
        return

    # TODO: Find gened requirements
    # geneds = re.findall('\[(\D*?)\]', message.content)
    # if len(geneds) > 0:
    #     get_geneds(geneds)
    #     return

    # Find all classes in an input string.
    # TODO Move string parsing to helepr function
    potential_message = '[' and ']' in message.content
    classes = []
    if potential_message:
        # Search for quotes in the message
        msg = message.content.split('\n')
        # All quotes start with '> ' and end with new line
        msg = [x for x in msg if not x.startswith('> ')]
        if len(msg) > 0:
            # Remake the message but without the quote part.
            msg = ''.join(x for x in msg)
            msg = msg.upper()
            # print(msg)
            # Parse the message. Converting to a set removes duplicates.
            classes = list(set(re.findall('\\\\?\[([A-Za-z]{2,4})\s?(\d{3})\\\\?\]', msg)))

    # Find all classes in an input string.
    if len(classes) > 6:
        await message.channel.send("To reduce spam, please limit your message to 6 or less classes.")
        # Iterate through the courses
    elif len(classes) > 0:
        for course in classes:
            await send_class(message.channel, course)

    await bot.process_commands(message)


# Add a help command to the bot.
@bot.command(name='info', aliases=['help'])
async def info(ctx):
    desc = 'To get a class, do [`department` `number`]. For example: `[cs 225]`. This is case insensitive, ' \
           'and the space between the department and the class number is optional. '
    embed = discord.Embed(title='Help', description=desc)
    embed.add_field(name='API Latency', value=str(round(bot.latency * 1000, 1))+'ms')
    embed.add_field(name='Contribute', value='https://github.com/timot3/uiuc-classes-bot/')
    await ctx.send(embed=embed)

# Run the bot.
bot.run(TOKEN.strip())
