import discord
from discord import app_commands
import re
import asyncio
import aiohttp
import json
import os

from MessageContent.CourseMessageContent import FailedRequestContent
from api import ClassAPI
from Views.ButtonsView import ButtonsView


intents = discord.Intents.default()
intents.members = True
intents.message_content = True
config = None

try:
    TOKEN = os.environ['CLASSBOT_TOKEN'].strip()
    TEST_GUILD = int(os.environ['TEST_GUILD'].strip())

except KeyError:
    with open('config.json') as f:
        config = json.load(f)
        TOKEN = config['bot_token']
        TEST_GUILD = config['test_guild_id']

classes_sent = {}  # The classes sent in a channel.


def get_all_courses_in_str(message: str) -> list:
    """
    :param message: The message to search for courses in.
    :return: A list of courses in the message.
    """
    # This regex explained:
    # ([A-Za-z]{2,4})  # first group: 2-4 letters
    # \s?  # optional space
    # (\d{3,4})  # second group: 3-4 digits
    # Convert result to a set to remove duplicates
    # then cast to list and return
    res = list(set(re.findall('([A-Za-z]{2,4})\s?(\d{3})', message)))
    # convert all first elements to uppercase
    res = [(x[0].upper(), x[1]) for x in res]
    return res


class MyClient(discord.Client):
    def __init__(self, test_guild, intents: discord.Intents = discord.Intents.default()):
        super().__init__(intents=intents)
        self.test_guild = test_guild
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        # This copies the global commands over to your guild.
        self.tree.copy_global_to(guild=self.test_guild)
        await self.tree.sync(guild=self.test_guild)


intents = discord.Intents.default()
test_guild = discord.Object(TEST_GUILD)
client = MyClient(intents=intents, test_guild=test_guild)


@client.event
async def on_ready():
    """
    Event called on bot ready (including launch).
    """
    print('Bot online.')
    print("Name: {}".format(client.user.name))
    print("ID: {}".format(client.user.id))

    print('In {} guilds'.format(len(client.guilds)))
    members = []  # sum([guild.member_count for guild in bot.guilds])
    total_members = 0
    for guild in client.guilds:
        for member in guild.members:
            members.append(member.id)
        total_members += guild.member_count
        print('In {}, with owner {}\t\tUsers: {}'.format(
            guild.id, guild.owner, guild.member_count))
        # print('Guild permissions: {}'.format(guild.me.guild_permissions))

    members = set(members)
    print('Serving a total of {} members'.format(total_members))
    print('Total unique members: {}'.format(len(members)))
    print("----------------")


@client.event
async def on_message(message: discord.Message):
    """
    Process every message the bot has access to. If a message contains a course in
    the format [`department` `code`] (ie, `[CS 124]`), retrieve the course and send
    a message in the channel the message was sent in with an embed for the class.
    """
    if message.author.bot:
        return

    print("Received content: {}".format(message.content))

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
            classes = get_all_courses_in_str(msg)

    # deprecate message parsing
        if len(classes) > 0:
            await message.channel.send("This format of course searching is deprecated. Please use slash commands (ex: "
                                       "`/course CS 225`).")


async def limit_classes_sent(channel: int, class_str: str) -> None:
    '''
    :param channel: The channel the class was sent in.
    :param class_str: the class sent ('CS125')
    :return: None
    '''
    if channel not in classes_sent:
        classes_sent[channel] = [class_str]
    else:
        classes_sent[channel] += [class_str]
    await asyncio.sleep(30)
    classes_sent[channel].remove(class_str)


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
    class_embed_list = []
    channel_id = interaction.channel_id
    async with aiohttp.ClientSession() as session:
        for course in courses:
            # check if course already in cache
            if channel_id in classes_sent and course in classes_sent[channel_id]:
                failed_request = FailedRequestContent(course[0], course[1])
                embed = failed_request.get_embed(":x: Already requested in the last 30 seconds. Slow down!")
                class_embed_list.append(embed)
                continue

            # Start asynchronous task that pops the class from the list in 30 seconds.
            # Limits spamming of classes
            asyncio.create_task(limit_classes_sent(channel_id, course))

            # make api call to get class
            embed_course = await ClassAPI().get_class(course, session=session)

            if embed_course is None:
                failed_request = FailedRequestContent(course[0], course[1])
                class_embed_list.append(failed_request.get_embed())
            else:
                class_embed_list.append(embed_course.get_embed())

    await interaction.response.send_message(embeds=class_embed_list)


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
