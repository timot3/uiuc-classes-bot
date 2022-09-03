import discord
import random

mistakes = ['Am I wrong?',
            'Did I make a mistake?',
            'Have a suggestion?']

# Illini Blue ('Midnight'), Illini Orange('Cinnabar)
colors = [0x12294b, 0xe84b38]


class MessageContent:
    def __init__(self):
        self.color = random.choice(colors)

    def get_embed(self) -> discord.Embed:
        raise NotImplementedError
