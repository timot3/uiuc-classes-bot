import pandas as pd
from utils.Course import Course
import discord
import xml.etree.ElementTree as ET
import urllib
from urllib.request import urlopen
import traceback
import asyncio
import requests
import math
from bs4 import BeautifulSoup

classes_sent = {}  # The classes sent in a channel.
classes_offered = pd.read_csv('data/2021-sp.csv')
classes_offered['Class'] = classes_offered['Subject'] + classes_offered['Number'].astype(str)
# class_gpa = pd.read_csv('data/uiuc-gpa-dataset.csv')
# class_gpa['Class'] = class_gpa['Subject'] + class_gpa['Number'].astype(str)


# Taken from Prof. Wade's reddit-uiuc-bot.

def get_recent_average_gpa(course):
    '''
    :param course: string that represents the class ('CS125')
    :return: The average gpa for that class
    '''
    gpa = classes_offered[classes_offered['Class'] == course]
    if len(gpa) > 0:
        gpa = gpa.iloc[0]['GPA']
        if math.isnan(gpa):
            return 'No data'
        else:
            return gpa
    else:
        return 'No data'

    # else:
    #     df = class_gpa[class_gpa["Class"] == course].groupby(
    #         "Class").agg("sum").reset_index()
    #     if len(df) == 0:
    #         return 'No data'
    #
    #     df["Count GPA"] = df["A+"] + df["A"] + df["A-"] + df["B+"] + df["B"] + df["B-"] + \
    #                       df["C+"] + df["C"] + df["C-"] + df["D+"] + df["D"] + df["D-"] + df["W"]
    #     df["Sum GPA"] = (4 * (df["A+"] + df["A"])) + (3.67 * df["A-"]) + \
    #                     (3.33 * df["B+"]) + (3 * df["B"]) + (2.67 * df["B-"]) + \
    #                     (2.33 * df["C+"]) + (2 * df["C"]) + (1.67 * df["C-"]) + \
    #                     (1.33 * df["D+"]) + (1 * df["D"]) + (0.67 * df["D-"])
    #
    #     df["Average GPA"] = df["Sum GPA"] / df["Count GPA"]
    #     gpa = df["Average GPA"].values[0]


    # if gpa is None:
    #     return 'No data'
    # else:
    #     return str(round(gpa, 2))


# returns string describing the online/in-person status of the class
def get_online_status(most_recent_url):
    try:
        # get total num of sections & num online
        r = requests.get(most_recent_url)
        soup = BeautifulSoup(r.content, 'html.parser')
        script = str(soup.find_all("script")[4])
        script = script.replace('\"','')
        script = script.replace('\\a','A')
        # print(script)
        online_sections = script.count('type:<div class=App-meeting\>Online')
        total_sections = script.count("crn")
        # decide which emoji to use based on % of sections online

        status_emoji = ":computer:" if int(online_sections) / int(total_sections) >= 0.5 else ":books:"
        # create string/desc of status
        online_status = f"{online_sections} of {total_sections} sections online. {status_emoji}"
    except Exception:
        print(traceback.format_exc())
        online_status = "N/A"

    return online_status


def get_class_url(course):
    '''
    :param course: either str or array
            --> If str: this means that we need to get the URL from the API.
            --> If array: We already know the term, so we can just get the URL
    :return: None
    '''

    if isinstance(course, str):
        # split the most recent url, take the 2nd element of arr
        url = course.split('https://courses.illinois.edu/cisapp/explorer/schedule/')[1].replace('.xml', '')
        return 'https://courses.illinois.edu/schedule/' + url
    else:
        return 'https://courses.illinois.edu/schedule/2020/fall/' + course[0].upper() + '/' + course[1]


def get_class_from_course_explorer(course):
    href = ''
    try:
        href = urlopen('https://courses.illinois.edu/cisapp/explorer/catalog/2021/spring/' + course[0].upper() + '/'
                       + course[1] + '.xml')

    except urllib.error.HTTPError:
        return None

    class_tree = ET.parse(href).getroot()

    class_id = class_tree.attrib['id']  # AAS 100
    # department_code, course_num = course.__get_class(class_id)  # AAS, 100
    label = class_tree.find('label').text  # Intro Asian American Studies
    description = class_tree.find('description').text  # Provided description of the class
    crh = class_tree.find('creditHours').text  # 3 hours.
    deg_attr = ',\n'.join(
        x.text for x in class_tree.iter('genEdAttribute'))  # whatever geneds the class satisfies
    class_link = class_tree.find('termsOffered').find('course')
    most_recent_url = 'https://courses.illinois.edu/schedule/2021/spring/'
    if class_link is None:
        year_term = 'None'
    else:
        year_term = class_link.text
        most_recent_url = get_class_url(class_link.attrib['href'])
        if year_term == 'Spring 2021':
            year_term = 'Offered in ' + year_term + '. :white_check_mark:'
        else:
            year_term = 'Most recently offered in ' + year_term + '.'

    gpa = get_recent_average_gpa(class_id.upper().replace(' ', ''))
    #  return __get_dict(year_term, class_id, department_code, course_num, label, description, crh, deg_attr)

    online_status = get_online_status(most_recent_url)

    return Course(class_id, label, crh, gpa, year_term, deg_attr, description, most_recent_url, online_status)


# def get_class_from_csv(course, line, class_str):
#     # Get information about a class.
#     class_name = line['Name'].iloc[0].replace('&amp;', '&')  # fix issues with the ampersand
#     line = line.loc[classes_offered['Class'] == class_str]
#     crh = line['Credit Hours'].iloc[0]
#     status = line['YearTerm'].iloc[0].strip()
#     desc = (line.iloc[0]['Description']).replace(' &amp;', '&')
#     deg_attr = line['Degree Attributes'].iloc[0]
#
#     if isinstance(deg_attr, str):
#         deg_attr = deg_attr.strip()
#         deg_attr = deg_attr.replace('and ', '\n').replace('course', '').replace('.', '')
#     else:
#         deg_attr = ''
#
#     status = 'Offered in Fall 2020. :white_check_mark:'
#
#     gpa = get_recent_average_gpa(class_str)
#
#     # Make a Class object with all information about the class.
#     url = get_class_url(course)
#
#     # get online/in-person status
#     if status == 'Offered in Fall 2020. :white_check_mark:':
#         online_status = get_online_status(url)
#     else:
#         online_status = "N/A"
#     return Course(class_str, class_name, crh, gpa, status, deg_attr, desc, url, online_status)


async def limit_classes_sent(channel, class_str):
    '''
    :param channel: The channel the class was sent in.
    :param class_str: the class sent ('CS125')
    :return: None
    '''
    if channel.id not in classes_sent:
        classes_sent[channel.id] = [class_str]
    else:
        classes_sent[channel.id] += [class_str]
    await asyncio.sleep(30)
    classes_sent[channel.id].remove(class_str)


async def send_class(channel, course):
    '''
    course: tuple containing department code and class number.
    course[0]: department code
    course[1]: class number
    '''
    class_str = course[0].upper() + course[1]
    if channel.id in classes_sent:
        if class_str in classes_sent[channel.id]:
            await channel.send(class_str + ' was already requested in the last 30 seconds. Slow down!')
            return

    # Start asynchronous task that pops the class from the list in 30 seconds.
    asyncio.create_task(limit_classes_sent(channel, class_str))

    # line = classes_offered.loc[classes_offered['Class'] == class_str]

    # if len(line) == 0:
    try:
        message_str = get_class_from_course_explorer(course)
        if message_str is None:
            await channel.send(class_str + ': couldn\'t find this class.')
        else:
            await channel.send(embed=message_str.get_embed())

    except Exception:
        await channel.send('I had an error processing this message. Please make an issue on github (https://github.com/timot3/uiuc-classes-bot/issues).')
        print(traceback.format_exc())

    # else:
    #     # send embed in channel
    #     message_str = get_class_from_csv(course, line, class_str)
    #     await channel.send(embed=message_str.get_embed())



