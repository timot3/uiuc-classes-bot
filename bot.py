import discord
from discord import app_commands
from discord.ext import commands
import aiohttp
import json
import os

from api import ClassAPI
from Views.ButtonsView import ButtonsView
from functions import get_all_courses_in_str, get_course_embed_list

config = None

try:
    TOKEN = os.environ['CLASSBOT_TOKEN'].strip()

except KeyError:
    with open('config.json') as f:
        config = json.load(f)
        TOKEN = config['bot_token']


class MyClient(commands.Bot):
    def __init__(self, intents: discord.Intents = discord.Intents.default()):
        super().__init__(intents=intents, command_prefix="c$")


intents = discord.Intents.default()
intents.members = True
intents.message_content = True
client = MyClient(intents=intents)


@client.event
async def on_ready():
    """
    Event called on bot ready (including launch).
    """
    print('Bot online.')
    print("Name: {}".format(client.user.name))
    print("ID: {}".format(client.user.id))

    print('In {} guilds'.format(len(client.guilds)))
    members = []
    total_members = 0
    for guild in client.guilds:
        for member in guild.members:
            members.append(member.id)
        total_members += guild.member_count
        print('In {}, with owner {}\t\tUsers: {}'.format(
            guild.name, guild.owner, guild.member_count))

    members = set(members)
    print('Serving a total of {} members'.format(total_members))
    print('Total unique members: {}'.format(len(members)))
    print("----------------")

    print("Loading slash commands...")
    await client.tree.sync()
    print("Done loading slash commands.")


@client.event
async def on_message(message: discord.Message):
    """
    Process every message the bot has access to. If a message contains a course in
    the format [`department` `code`] (ie, `[CS 124]`), retrieve the course and send
    a message in the channel the message was sent in with an embed for the class.
    """
    if message.author.bot:
        return

    potential_message = '[' and ']' in message.content
    courses = []
    if potential_message:
        # Search for quotes in the message
        msg = message.content.split('\n')
        # All quotes start with '> ' and end with new line
        msg = [x for x in msg if not x.startswith('> ')]
        if len(msg) > 0:
            # Remake the message but without the quote part.
            msg = ''.join(x for x in msg)
            msg = msg.upper()
            courses = get_all_courses_in_str(msg)

        # deprecate message parsing
        if len(courses) > 0:
            embed_list = await get_course_embed_list(courses, message.channel.id)
            await message.channel.send(embeds=embed_list)


@client.tree.command(name="course")
@app_commands.describe(list_of_classes='List of course codes to look up')
async def respond_to_course(interaction: discord.Interaction, list_of_classes: str):
    courses = get_all_courses_in_str(list_of_classes)
    if len(courses) == 0:
        await interaction.response.send_message("No courses found in your message.")
        return
    elif len(courses) > 6:
        await interaction.response.send_message("Too many courses. Please limit to 6.")
        return

    embed_list = await get_course_embed_list(courses, interaction.channel.id)
    await interaction.response.send_message(embeds=embed_list)


@client.tree.command(name="search")
@app_commands.describe(query='The search query to execute')
async def search_class(interaction: discord.Interaction, query: str):
    async with aiohttp.ClientSession() as session:
        res = await ClassAPI().search_classes(query, session)
        embed = res.get_embed()
        buttons = ButtonsView().add_classes(res.get_labels())
        await interaction.response.send_message(embed=embed, view=buttons)


if __name__ == '__main__':
    client.run(TOKEN)
