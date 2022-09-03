import aiohttp
import discord
import asyncio
from discord import Interaction

from api import ClassAPI


class CourseButton(discord.ui.Button):
    def __init__(self, name):
        super().__init__()
        self.label = name.replace('*', '')
        # self.style = style

    async def callback(self, interaction: Interaction):
        async with aiohttp.ClientSession() as session:
            requested_class = await ClassAPI().get_class(tuple(self.label.split(' ')), session)
            await interaction.response.send_message(embed=requested_class.get_embed())





