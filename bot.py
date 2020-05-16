#from dotenv import load_dotenv
from discord.ext import commands
import discord
import re
import random
import pandas as pd
import requests
from bs4 import BeautifulSoup

TOKEN = ''


with open('config.txt', 'r') as f:
    TOKEN = f.readline()

# load_dotenv()

classes_offered = pd.read_csv('data/classes-fa-sp-2020.csv')
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
    await bot.change_presence(activity=discord.Game(name="ex: [CS 225]"))


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
                # check if page exists in course explorer
                course_page_exists = True
                course_explorer_online = False
                # verify course explorer website is online
                if requests.get("https://courses.illinois.edu/schedule/terms/"+course[0].upper()+"/"+course[1]).status_code == 200:
                    course_explorer_online = True
                    # verify course is a real class
                    soup = BeautifulSoup(requests.get("https://courses.illinois.edu/schedule/terms/"+course[0].upper()+"/"+course[1]).content, 'html.parser')
                    if "404" in soup.text:
                        course_page_exists = False
                # if course page exists, fetch class data
                if course_page_exists and course_explorer_online:
                    # get page & parse w BS4
                    page = requests.get("https://courses.illinois.edu/schedule/terms/"+course[0].upper()+"/"+course[1])
                    soup = BeautifulSoup(page.content, 'html.parser')
                    all_a_tags = soup.find_all('a')
                    # get all terms that the class has been offered
                    terms_offered = []
                    for a in all_a_tags:
                        if "Fall" in a.contents[0] or "Spring" in a.contents[0] or "Summer" in a.contents[0]:
                            terms_offered.append(a.contents[0].strip())
                    # get other class data (i.e. description, credit hours, full name)
                    most_recent_term = terms_offered[0]
                    term = most_recent_term.split()
                    course_page = requests.get("https://courses.illinois.edu/schedule/"+term[1]+"/"+term[0]+"/"+course[0].upper()+"/"+course[1])
                    new_soup = BeautifulSoup(course_page.content, 'html.parser')
                    class_name = new_soup.find("span", class_="app-label app-text-engage").contents[0]
                    class_info = new_soup.find_all("div", class_="col-sm-12")[3].find_all("p")
                    crh = class_info[0].contents[1]
                    desc = class_info[1].contents[0]
                    status = "Most recently offered in: "+most_recent_term
                    # build & send message on Discord
                    message_string = class_str +': ' + class_name + \
                        '\nCredit hours: ' + crh + \
                        '\nAverage GPA: N/A' + \
                        '\nStatus: ' + status + \
                        '\n> ' + desc
                    await message.channel.send(message_string)
                    message_string = ''
                else:
                    # if page not in course explorer, send the sad msg :(
                    await message.channel.send(class_str + ': Could not find this class. It is likely not offered in FA 2020.\n')
            else:
                print('responded to: ' + class_str + ' in channel: ' + message.channel.name)
                class_name = line['Name'].iloc[0].replace('&amp;', '&')
                line = line.loc[classes_offered['Class'] == class_str]
                crh = line['Credit Hours'].iloc[0]
                status = line['YearTerm'].iloc[0].strip()

                if status == '2020-fa':
                    status = 'Offered in FA-2020.'
                else:
                    status = 'Likely not offered in FA-2020.'


                gpa = get_recent_average_gpa(class_str)
                if gpa is None:
                    gpa = 'Not enough data.'
                else:
                    gpa = str(round(gpa, 2))

                desc = (line.iloc[0]['Description']).replace(' &amp;', '&')
                message_string = class_str +': ' + class_name + \
                    '\nCredit hours: ' + crh + \
                    '\nAverage GPA: ' + gpa + \
                    '\nStatus: ' + status + \
                    '\n> ' + desc
                await message.channel.send(message_string)
                message_string = ''


    await bot.process_commands(message)


# Feature added for fun
# @bot.command(name='8ball')
# async def await_8ball(ctx, arg):
#     #msg = msg.split(' ', 1)[1]
#     responses = ['It is certain.',
#                  'It is decidedly so.',
#                  'Without a doubt.',
#                  'Yes - definitely.',
#                  'You may rely on it.',
#                  'As I see it, yes.',
#                  'Most likely.',
#                  'Outlook good.',
#                  'Yes.',
#                  'Signs point to yes.',
#                  'Reply hazy, try again.',
#                  'Ask again later.',
#                  'Better not tell you now.',
#                  'Cannot predict now.',
#                  'Concentrate and ask again.',
#                  "Don't count on it.",
#                  'My reply is no.',
#                  'My sources say no.',
#                  'Outlook not so good',
#                  'Very doubtful']

#     await ctx.send(f'Question: {arg}\nAnswer: {random.choice(responses)}')



bot.run(TOKEN.strip())


# \[[A-Za-z]{2,4}\s?(\d{3})\]
