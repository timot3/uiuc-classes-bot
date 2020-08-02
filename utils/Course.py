import discord
import re
import random

# Illini Blue ('Midnight'), Illini Orange('Cinnabar)
colors = [0x12294b, 0xe84b38]

mistakes = ['Am I wrong?',
            'Did I make a mistake?',
            'Have a suggestion? Make an issue on GitHub, or',
            'Want to add this to your own server?']


# Function to get department and class number.
def get_class_id(class_code):
    # Group 1:([A-Za-z]{2,4})
    # Group 2:(\d{3})
    temp = re.findall('([A-Za-z]{2,4})\s?(\d{3})', class_code)
    return temp[0][0], temp[0][1]


class Course:

    def __init__(self, name, title, crh, gpa, status, deg_attr, desc, url, online_status):
        self.class_name = name
        self.title = name + ': ' + title
        dept, num = get_class_id(name)
        self.url = url
        self.crh = crh
        self.gpa = gpa
        self.desc = desc
        self.deg_attr = deg_attr
        self.status = status
        self.online_status = online_status


    def get_embed(self):
        embed = discord.Embed(title=self.title, description=self.desc, url=self.url, color=random.choice(colors))
        # print(self.title)
        # print(self.desc)
        embed.add_field(name='Credit Hours', value=self.crh, inline=False)
        # print(self.crh)
        embed.add_field(name='Average GPA', value=self.gpa, inline=False)
        # print(self.gpa)
        # print(self.deg_attr)
        if len(self.deg_attr) > 0:
            embed.add_field(name='Degree Attributes', value=self.deg_attr, inline=False)

        embed.add_field(name='Status', value=self.status, inline=False)
        embed.add_field(name='Online/In-Person Status', value=self.online_status, inline=False)
        # print(repr(self.status))

        if random.random() < 0.25:
            embed.set_footer(text=random.choice(mistakes) + ' DM @10x engineer#9075.')

        return embed
