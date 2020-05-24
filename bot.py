# from dotenv import load_dotenv
from discord.ext import commands
import discord
import re
import random
import pandas as pd
import requests
from bs4 import BeautifulSoup

TOKEN = ''

with open('config.txt', 'r') as f:
    TOKEN = f.readline().strip()


class Class:
    def __init__(self):
        # self.class_name = ''
        self.title = ''
        self.url = 'https://courses.illinois.edu/schedule/terms/'
        self.crh = ''
        self.gpa = ''
        self.desc = ''
        self.deg_attr = ''
        self.status = ''

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


classes_offered = pd.read_csv('data/classes-fa-sp-2020.csv')
classes_offered['Class'] = classes_offered['Subject'] + classes_offered['Number'].astype(str)

class_gpa = pd.read_csv('data/uiuc-gpa-dataset.csv')

class_gpa['Class'] = class_gpa['Subject'] + class_gpa['Number'].astype(str)

bot = commands.Bot(command_prefix='classbot')


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


# What to do when bot is online: set status
@bot.event
async def on_ready():
    print('Bot online.')
    print("Name: {}".format(bot.user.name))
    print("ID: {}".format(bot.user.id))
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name='classbot info'))


def get_geneds(geneds):
    acp_aliases = ['advanced composition', 'adv comp', 'acp']
    wes_aliases = ['western', 'west', 'wes']
    nws_aliases = ['nonwestern', 'non western', 'nws', 'nonwest']
    usm_aliases = ['usm', 'us minorities', 'minority', 'us minority', 'us']
    hum_aliases = ['humanities', 'hum', 'human', 'arts']
    nst_aliases = ['natsci', 'natural science', 'nst']
    qre_aliases = ['quantitative reasoning', 'qre']
    sbs_aliases = ['social', 'behavioral', 'sbs']


# Parse every message
@bot.event
async def on_message(message):
    channel = message.channel
    # Make sure the bot does not respond to its own messages.
    if message.author == bot.user:
        return
    # Find gened requirements
    geneds = re.findall('\[(\D*?)\]', message.content)
    if len(geneds) > 0:
        get_geneds(geneds)
        return

    # Find all classes in an input string.
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
            # print(msg)
            # Parse the message.
            classes = re.findall('\\\\?\[([A-Za-z]{2,4})\s?(\d{3})\\\\?\]', msg)

    # Find all classes in an input string.
    # classes = re.findall('\\\\?\[([A-Za-z]{2,4})\s?(\d{3})\\\\?\]', message.content)
    # If classes found
    if len(classes) > 0 and potential_message:
        # Iterate through the courses
        for course in classes:
            class_str = course[0].upper() + course[1]
            line = classes_offered.loc[classes_offered['Class'] == class_str]

            if len(line) == 0:
                # check if page exists in course explorer
                course_page_exists = True
                course_explorer_online = False
                # verify course explorer website is online
                if requests.get("https://courses.illinois.edu/schedule/terms/" + course[0].upper() + "/" + course[
                    1]).status_code == 200:
                    course_explorer_online = True
                    # verify course is a real class
                    soup = BeautifulSoup(requests.get(
                        "https://courses.illinois.edu/schedule/terms/" + course[0].upper() + "/" + course[1]).content,
                                         'html.parser')
                    if "404" in soup.text:
                        course_page_exists = False
                # if course page exists, fetch class data
                if course_page_exists and course_explorer_online:
                    # get page & parse w BS4
                    page = requests.get(
                        "https://courses.illinois.edu/schedule/terms/" + course[0].upper() + "/" + course[1])
                    soup = BeautifulSoup(page.content, 'html.parser')
                    all_a_tags = soup.find_all('a')
                    # get all terms that the class has been offered
                    terms_offered = []
                    for a in all_a_tags:
                        if "Fall" in a.contents[0] or "Spring" in a.contents[0] or "Summer" in a.contents[0]:
                            terms_offered.append(a.contents[0].strip())
                            break
                    # get other class data (i.e. description, credit hours, full name)
                    most_recent_term = terms_offered[0]
                    term = most_recent_term.split()
                    course_page = requests.get(
                        "https://courses.illinois.edu/schedule/" + term[1] + "/" + term[0] + "/" + course[
                            0].upper() + "/" + course[1])
                    new_soup = BeautifulSoup(course_page.content, 'html.parser')
                    class_name = new_soup.find("span", class_="app-label app-text-engage").contents[0]

                    # May encounter errors with upper level classes 
                    # Loop through parts 3 and 5 of col-sm-12 to hopefully
                    # Find a non-empty p tag
                    class_info = new_soup.find_all("div", class_="col-sm-12")[3].find_all("p")

                    if len(class_info) == 0:
                        class_info = new_soup.find_all("div", class_="col-sm-12")[4].find_all("p")

                    crh = class_info[0].contents[1]

                    desc = ''
                    if len(class_info[1].contents) == 0:
                        desc = class_info[2].contents[0]
                    else:
                        desc = class_info[1].contents[0]

                    status = "Most recently offered in: " + most_recent_term
                    message_str = Class(class_str, class_name, crh, 'No data.', '',status, desc)

                    await message.channel.send(embed=message_str.get_embed())
                    message_string = ''
                else:
                    # if page not in course explorer, send the sad msg :(
                    await message.channel.send(class_str + ': Could not find this class.\n')
            else:
                # Get information about a class.
                class_name = line['Name'].iloc[0].replace('&amp;', '&')  # fix issues with the ampersand
                line = line.loc[classes_offered['Class'] == class_str]
                crh = line['Credit Hours'].iloc[0]
                status = line['YearTerm'].iloc[0].strip()
                desc = (line.iloc[0]['Description']).replace(' &amp;', '&')

                if status == '2020-fa':
                    status = 'Offered in fa-2020.'
                else:
                    status = 'Offered in sp-2020. May be offered in fa-2020.'

                gpa = get_recent_average_gpa(class_str)
                if gpa is None:
                    gpa = 'No data.'
                else:
                    gpa = str(round(gpa, 2))

                # Make a Class object with all information about the class.
                message_str = Class(class_str, class_name, crh, gpa, status, '', desc)
                # send embed in channel
                await message.channel.send(embed=message_str.get_embed())

    await bot.process_commands(message)


@bot.command(name='info')
async def info(ctx):
    desc = 'To get a class, do [`department` `number`]. For example: `[cs 225]`. This is case insensitive'
    embed = discord.Embed(title='Help', description=desc)
    embed.add_field(name='API Latency', value=str(round(bot.latency * 1000, 2))+'ms')
    embed.add_field(name='Contribute', value='https://github.com/timot3/uiuc-classes-bot/')
    await ctx.send(embed=embed)

# Run the bot.
bot.run(TOKEN)
