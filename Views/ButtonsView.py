from typing import Iterable

import nextcord
import asyncio

from nextcord.ui import Item
from nextcord import Interaction

from Views.CourseButton import CourseButton


class ButtonsView(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=30)
        # self.view = nextcord.ui.View(timeout=30)

    # item is course title (ie, CS 124)
    def add_class(self, course_title: str):
        self.add_item(CourseButton(course_title))
        # return self.view

    async def on_timeout(self):
        self.clear_items()

    def add_classes(self, items: Iterable[str]):
        for item in items:
            self.add_class(item)
        return self

