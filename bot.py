from utils.functions import send_class
from discord.ext import commands
import discord
import re

TOKEN = ''

with open('config.txt', 'r') as f:
    TOKEN = f.readline().strip()

bot = commands.Bot(command_prefix=('c!', 'C!'), case_insensitive=True, help_command=None)


# What to do when bot is online
@bot.event
async def on_ready():
    # Log events to console.
    print('Bot online.')
    print("Name: {}".format(bot.user.name))
    print("ID: {}".format(bot.user.id))

    print('In {} guilds'.format(len(bot.guilds)))
    members = sum([guild.member_count for guild in bot.guilds])
    print('Serving a total amount of {} members'.format(members))
    # Set status
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name='c!info'))


# Parse every message
@bot.event
async def on_message(message):
    # Make sure the bot does not respond to its own messages.
    if message.author.bot:
        return

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
async def await_info(ctx):
    desc = 'To get a class, do [`department` `number`]. For example: `[cs 225]`. This is case insensitive, ' \
           'and the space between the department and the class number is optional. '
    embed = discord.Embed(title='Help', description=desc, url='https://github.com/timot3/uiuc-classes-bot/')
    embed.add_field(name='AP - c!AP', value='Links the UIUC AP credit page')
    embed.add_field(name='Geneds - c!Gened', value='Links the Geneds by GPA page.')

    embed.add_field(name='API Latency', value=str(round(bot.latency * 1000, 1))+'ms.')
    embed.set_footer(text='Having issues with the bot? Send a DM to @10x engineer#9075')
    await ctx.send(embed=embed)


@bot.command(name='AP')
async def await_ap(ctx):
    await ctx.send('https://admissions.illinois.edu/Apply/Freshman/college-credit-AP')


@bot.command(name='geneds', aliases=['gened'])
async def await_ap(ctx):
    await ctx.send('http://waf.cs.illinois.edu/discovery/every_gen_ed_at_uiuc_by_gpa/')


@bot.command(name='users', aliases=['usercount'])
async def await_usercount(ctx):
    members = sum([guild.member_count for guild in bot.guilds])
    guilds = len(bot.guilds)
    await ctx.send('Serving {} servers, with {} total members.'.format(guilds, members))

# Run the bot.
bot.run(TOKEN.strip())
