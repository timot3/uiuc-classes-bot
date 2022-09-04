from typing import Iterable

import discord
import asyncio

from discord.ui import Item
from discord import Interaction

from Views.CourseButton import CourseButton


class ButtonsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=30)

    # item is course title (ie, CS 124)
    def add_class(self, course_title: str):
        self.add_item(CourseButton(course_title))
        return self

    def add_classes(self, items: Iterable[str]):
        for item in items:
            self.add_class(item)
        return self

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        self = self.clear_items()



