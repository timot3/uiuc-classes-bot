import logging
from nextcord import activity, Interaction, SlashOption
from Utils.functions import send_classes, search_class, print_member_statistics
from nextcord.ext import commands, tasks
import nextcord
import os
import re
import aiohttp
import asyncio

startup_extensions = ['Cogs.InfoFunctions', 'Cogs.CourseSearch.CourseSearcher']
TESTING_GUILD_ID = 735523773515694144

# set up logging for nextcord
logger = logging.getLogger('nextcord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(
    filename='nextcord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter(
    '%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

try:
    TOKEN = os.environ['CLASSBOT_TOKEN'].strip()
except KeyError:
    # If testing locally, use this instead of the OS environment variables
    with open('config.txt') as f:
        TOKEN = f.readline().strip()

# init member caching (for member count across guilds)
intents = nextcord.Intents.default()
intents.members = True

# Discord is making message content a privileged intent as of April 30, 2022.
# https://support-dev.discord.com/hc/en-us/articles/4404772028055
# This change is to ensure the continued functionality of the bot.
intents.messages = True
activity = nextcord.Activity(
    type=nextcord.ActivityType.listening, name='c$info')

# Init the actual bot.
bot = commands.Bot(command_prefix=('c$', 'C$'), case_insensitive=True,
                   help_command=None, intents=intents, activity=activity)


# What to do when bot is online
@bot.event
async def on_ready():
    await print_member_statistics(bot)


@bot.slash_command(
    name="search",
    description="Classbot search command with querying",
    guild_ids=[TESTING_GUILD_ID],
)
async def test_search_slash(
        interaction: Interaction,
        query: str = SlashOption(name="query", description="Enter your search query: "),
):
    # Introducing SlashOption, how you control individual parameters. Using them, you can provide a custom name and
    # description, and even set if they are required or not, just like with arg2/ephemeral here!
    print(repr(query))
    embed, buttons = await search_class(query)
    await interaction.response.send_message(embed=embed, view=buttons)


# Run the bot.
async def start_func():
    # Load cogs
    for ext in startup_extensions:
        try:
            bot.load_extension(ext)
            print(f"Successfully loaded extension {ext}")
        except Exception as e:
            exc = f"{type(e).__name__,}: {e}"
            print(f"Failed to load extension {ext}\n{exc}")

    async with aiohttp.ClientSession() as session:
        bot.session = session
        try:
            await bot.start(TOKEN)
        except KeyboardInterrupt:
            raise SystemExit


loop = asyncio.get_event_loop()
loop.run_until_complete(start_func())
