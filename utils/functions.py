from itertools import islice
from typing import Union

import pandas as pd
from utils.Course import EmbedCourse, load_json_into_class
from utils.SearchCoursesResult import SearchCoursesResult
import nextcord
import traceback
import asyncio
import requests
import aiohttp

api_base_url = 'http://127.0.0.1:5000/'

classes_sent = {}  # The classes sent in a channel.

'''
:param course: string that represents the class ('CS125')
:return: The average gpa for that class
'''


async def print_member_statistics(bot):
    # Log events to console.
    print('Bot online.')
    print("Name: {}".format(bot.user.name))
    print("ID: {}".format(bot.user.id))

    print('In {} guilds'.format(len(bot.guilds)))
    members = []  # sum([guild.member_count for guild in bot.guilds])
    total_members = 0
    for guild in bot.guilds:
        for member in guild.members:
            members.append(member.id)
        total_members += guild.member_count
        print('In {}, with owner {}\t\tUsers: {}'.format(guild.name, guild.owner, guild.member_count))
        # print('Guild permissions: {}'.format(guild.me.guild_permissions))

    members = set(members)
    print('Serving a total of {} members'.format(total_members))
    print('Total unique members: {}'.format(len(members)))


async def limit_classes_sent(channel: nextcord.TextChannel, class_str: str) -> None:
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


def get_class_from_api(course: tuple) -> Union[EmbedCourse, None]:
    query = {'subject': course[0].upper(),
             'number': course[1]}
    url = api_base_url + f"api/classes/"
    res = requests.get(url, params=query)

    # not found!
    if res.status_code != 200 or len(res.json()) == 0:
        return None

    # always gets one class, so it's safe to do [0] to get the one and only class
    return load_json_into_class(res.json()[0])


async def send_classes(channel: nextcord.TextChannel, course: tuple) -> None:
    """
    :param channel The discord.Channel object that the message was requested.
    :param course: tuple containing department code and class number (ie "CS 124")
        - course[0]: department code
        - course[1]: class number
    """
    class_str = f"{course[0].upper()} {course[1]}"  # ensure proper formatting
    if channel.id in classes_sent:
        if class_str in classes_sent[channel.id]:
            await channel.send(class_str + ' was already requested in the last 30 seconds. Slow down!')
            return

    # Start asynchronous task that pops the class from the list in 30 seconds.
    asyncio.create_task(limit_classes_sent(channel, class_str))

    try:

        response = get_class_from_api(course)
        if response is None:
            await channel.send(class_str + ': couldn\'t find this class.')
        else:
            await channel.send(embed=response.get_embed())

    except Exception:
        await channel.send('I had an error processing this message. Please make an issue on github ('
                           'https://github.com/timot3/uiuc-classes-bot/issues).')
        print(traceback.format_exc())


def search_classes_from_api(search_query: tuple):
    query = {
        'query': '+'.join(search_query)
    }
    url = api_base_url + f"api/classes/search/"
    res = requests.get(url, params=query)

    # not found!
    if res.status_code != 200 or len(res.json()) == 0:
        return None

    # always gets one class, so it's safe to do [0] to get the one and only class

    return res.json()


async def search_class(channel: nextcord.TextChannel, search_query: tuple):
    res = search_classes_from_api(search_query)
    embed = SearchCoursesResult(search_query, res).get_embed()
    await channel.send(embed=embed)
