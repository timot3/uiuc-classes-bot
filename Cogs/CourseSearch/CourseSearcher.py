from typing import List

import nextcord
from nextcord.ext import commands

import re
from Utils.functions import send_classes
from Utils.functions import search_class


class CourseSearcher(commands.Cog):
    """Course Searching functionality"""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: nextcord.Message):
        """
        Process every message the bot has access to. If a message contains a course in
        the format [`department` `code`] (ie, `[CS 124]`), retrieve the course and send
        a message in the channel the message was sent in with an embed for the class.
        """
        if message.author.bot:
            return

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
                await send_classes(message.channel, course)

        # await self.bot.process_commands(message)

    @commands.command(name='search')
    async def search(self, ctx, *arg):
        await search_class(ctx.channel, arg)



def setup(bot):
    bot.add_cog(CourseSearcher(bot))
