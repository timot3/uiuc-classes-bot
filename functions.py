import asyncio
import re
import traceback
from typing import List

import aiohttp
import discord

from MessageContent.CourseMessageContent import FailedRequestContent
from api import ClassAPI

classes_sent = {}  # The classes sent in a channel.


def get_all_courses_in_str(message: str, bracketed: bool = False) -> List[tuple]:
    """
    :param message: The message to search for courses in.
    :return: A list of courses in the message.
    """
    # This regex explained:
    # ([A-Za-z]{2,4})  # first group: 2-4 letters
    # \s?  # optional space
    # (\d{3,4})  # second group: 3-4 digits
    # Convert result to a set to remove duplicates
    # then cast to list and return

    if bracketed:
        re_str = r"\[([A-Za-z]{2,4})\s?(\d{3})\s?(.{1,3})?\]"
        found = list(set(re.findall(re_str, message)))

    else:
        # When requeseting sections, the regex may end up capturing the next course as well.
        # Avoid this by taking the max of the two regexes.
        re_str1 = "([A-Za-z]{2,4})\s?(\d{3})\s?(.{1,3})?"
        re_str2 = "([A-Za-z]{2,4})\s?(\d{3})"

        # get the max finds
        found1 = list(set(re.findall(re_str1, message)))
        found2 = list(set(re.findall(re_str2, message)))
        if len(found2) > len(found1):
            found = found2
        else:
            found = found1

    # convert all first elements to uppercase
    # results may have 2 or 3 elements
    res = []
    for course in found:
        if len(course) == 2 or course[2] == "":
            res.append((course[0].upper(), course[1]))
        elif len(course) == 3:
            res.append((course[0].upper(), course[1], course[2].upper()))

    return res


async def get_course_info(course, session) -> discord.Embed:
    try:
        embed_course = await ClassAPI().get_class(course, session=session)
        if embed_course is None:
            failed_request = FailedRequestContent(course[0], course[1])
            return failed_request.get_embed()
        else:
            return embed_course.get_embed()
    except Exception as e:
        print(traceback.format_exc())
        failed_request = FailedRequestContent(course[0], course[1])
        return failed_request.get_embed()


async def get_course_embed_list(
    course_list: list, channel_id: int
) -> List[discord.Embed]:
    """
    :param course_list: A list of courses
    :return: A list of embeds for each course
    """
    class_embed_list = []
    courses_to_request = []
    # add
    async with aiohttp.ClientSession() as session:
        for course in course_list:
            # check if course already in cache
            if channel_id in classes_sent and course in classes_sent[channel_id]:
                failed_request = FailedRequestContent(course[0], course[1])
                embed = failed_request.get_embed(
                    ":x: Already requested in the last 30 seconds. Slow down!"
                )
                class_embed_list.append(embed)
                continue

            courses_to_request.append(course)
            # Start asynchronous task that pops the class from the list in 30 seconds.
            # Limits spamming of classes
            asyncio.create_task(limit_classes_sent(channel_id, course))

        # Get all the courses from the API
        class_embed_list += await asyncio.gather(
            *[get_course_info(course, session) for course in courses_to_request]
        )

    return class_embed_list


async def limit_classes_sent(channel: int, class_str: str) -> None:
    """
    :param channel: The channel the class was sent in.
    :param class_str: the class sent ('CS125')
    :return: None
    """
    if channel not in classes_sent:
        classes_sent[channel] = [class_str]
    else:
        classes_sent[channel] += [class_str]
    await asyncio.sleep(30)
    classes_sent[channel].remove(class_str)
