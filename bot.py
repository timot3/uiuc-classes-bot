#from dotenv import load_dotenv
from discord.ext import commands
import os
import discord
import re
import random
import pandas as pd

TOKEN = ''


with open('config.txt', 'r') as f:
    TOKEN = f.readline()

# load_dotenv()

classes_offered = pd.read_csv('data/2020-fa.csv')
classes_offered['Class'] = classes_offered['Subject'] + \
    classes_offered['Number'].astype(str)


class_gpa = pd.read_csv('data/uiuc-gpa-dataset.csv')

class_gpa['Class'] = class_gpa['Subject'] + class_gpa['Number'].astype(str)

# print(classes_offered.head())

bot = commands.Bot(command_prefix='$')


# Taken from Prof. Wade's reddit-uiuc-bot.
def get_recent_average_gpa(course):
    df = class_gpa[class_gpa["Class"] == course].groupby(
        "Class").agg("sum").reset_index()
    if len(df) == 0:
        return None

    df["Count GPA"] = df["A+"] + df["A"] + df["A-"] + df["B+"] + df["B"] + df["B-"] + \
        df["C+"] + df["C"] + df["C-"] + df["D+"] + df["D"] + df["D-"] + df["W"]
    df["Sum GPA"] = (4 * (df["A+"] + df["A"])) + (3.67 * df["A-"]) + \
        (3.33 * df["B+"]) + (3 * df["B"]) + (2.67 * df["B-"]) + \
        (2.33 * df["C+"]) + (2 * df["C"]) + (1.67 * df["C-"]) + \
        (1.33 * df["D+"]) + (1 * df["D"]) + (0.67 * df["D-"])

    df["Average GPA"] = df["Sum GPA"] / df["Count GPA"]
    return df["Average GPA"].values[0]

@bot.event
async def on_ready():
    print("logged in as: " + bot.user.name + '\n')
    await bot.change_presence(activity=discord.Game(name="a game"))


@bot.event
async def on_message(message):
    channel = message.channel
    if message.author == bot.user:
        return
    classes = re.findall(
        '\\\\?\[([A-Za-z]{2,4})\s?(\d{3})\\\\?\]', message.content)
    #print (classes[0])
    if (len(classes) > 0):
        #msg = []
        # await message.channel.send(classes)
        for course in classes:
            # msg.append('Class:' + )
            class_str = course[0].upper() + course[1]
            #line = classes_offered.loc[classes_offered['Subject']== course[0].upper()]
            line = classes_offered.loc[classes_offered['Class'] == class_str]
            if len(line) == 0:
                await message.channel.send(class_str + ': Could not find this class. It is likely not offered in FA 2020.\n')
            else:
                line = line.loc[classes_offered['Class'] == class_str]
                crh = line.iloc[0]['Credit Hours']
                gpa = get_recent_average_gpa(class_str)
                desc = (line.iloc[0]['Description'])
                message_string = class_str + '\nCredit hours: ' + \
                    crh + '\nAverage GPA: ' + str(round(gpa, 2)) + \
                    '\n> ' + desc
                await message.channel.send(message_string)
                message_string = ''

    print('responded to: ' + message.content)
    print(classes)

    await bot.process_commands(message)


@bot.command(name='8ball')
async def await_8ball(ctx, arg):
    #msg = msg.split(' ', 1)[1]
    responses = ['It is certain.',
                 'It is decidedly so.',
                 'Without a doubt.',
                 'Yes - definitely.',
                 'You may rely on it.',
                 'As I see it, yes.',
                 'Most likely.',
                 'Outlook good.',
                 'Yes.',
                 'Signs point to yes.',
                 'Reply hazy, try again.',
                 'Ask again later.',
                 'Better not tell you now.',
                 'Cannot predict now.',
                 'Concentrate and ask again.',
                 "Don't count on it.",
                 'My reply is no.',
                 'My sources say no.',
                 'Outlook not so good',
                 'Very doubtful']

    await ctx.send(f'Question: {arg}\nAnswer: {random.choice(responses)}')



bot.run(TOKEN)


# \[[A-Za-z]{2,4}\s?(\d{3})\]
