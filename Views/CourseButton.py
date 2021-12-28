import nextcord
import asyncio
from nextcord import Interaction

from Utils.functions import send_classes


class CourseButton(nextcord.ui.Button):
    def __init__(self, name):
        super().__init__()
        self.label = name.replace('*', '')
        # self.style = style

    async def callback(self, interaction: Interaction):
        # check that the button was actually pressed
        # if isinstance(interaction, (nextcord.InteractionType.component)):
        # send class on button press
        await send_classes(interaction.channel, tuple(self.label.split(' ')))

        # disable button after press to prevent spam
        # self.disabled = True




