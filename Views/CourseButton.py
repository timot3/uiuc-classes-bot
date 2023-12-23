import aiohttp
import discord
import asyncio
from discord import Interaction

from api import ClassAPI
from utils import Course


class CourseButton(discord.ui.Button):
    def __init__(self, name):
        super().__init__()
        self.label = name.replace("*", "")
        self._course = Course(
            subject=self.label.split(" ")[0], number=self.label.split(" ")[1]
        )

    async def callback(self, interaction: Interaction):
        async with aiohttp.ClientSession() as session:
            requested_class = await ClassAPI().get_class(self._course, session)
            await interaction.response.send_message(embed=requested_class.get_embed())

        self.disabled = True
