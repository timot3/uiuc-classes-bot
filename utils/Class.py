import discord
import re
import random


class Class:

    def __init__(self, name, title, crh, gpa, status, deg_attr,desc):
        self.class_name = name
        self.title = name + ': ' + title
        dept, num = self.__get_class(name)
        self.url = 'https://courses.illinois.edu/schedule/terms/' + dept + '/' + num
        self.crh = crh
        self.gpa = gpa
        self.desc = desc
        self.deg_attr = deg_attr
        self.status = status

    def get_embed(self):
        colors = [0x12294b, 0xe84b38]
        embed = discord.Embed(title=self.title, description=self.desc, url=self.url, color=random.choice(colors))
        embed.add_field(name='Credit Hours', value=self.crh, inline=False)
        embed.add_field(name='Average GPA', value=self.gpa, inline=False)
        embed.add_field(name='Status', value=self.status, inline=False)
        return embed

    def __get_class(self, str):
        temp = re.findall('([A-Za-z]{2,4})\s?(\d{3})', str)
        return temp[0][0], temp[0][1]
