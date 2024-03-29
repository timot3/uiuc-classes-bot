# API Wrapper for class api
import asyncio
from threading import Lock

import aiohttp
import requests
import json
import os

from config import BASE_API_URL
from utils import Course
from MessageContent.CourseMessageContent import CourseMessageContent
from MessageContent.SearchMessageContent import SearchMessageContent


# key: course name, value: dict that the api would return
course_cache = dict()

mutex = Lock()


def process_deg_attr(deg_attr: str):
    """
    Internal function to process degree attributes to split them to newlines.

    Example degree attribute that is processed:
    [AAS100] -> "Social & Beh Sci - Soc Sci, and Cultural Studies - US Minority course."

    We meed to split this into "Social & Beh Sci - Soc Sci" and "Cultural Studies - US Minority"
    If no attributes exist, return None.

    :param deg_attr degree attributes as stored on course explorer.
    :returns either `None` or degree attributes on newlines
    """
    if deg_attr is None or deg_attr == "None":
        return None
    deg_attr = deg_attr[: deg_attr.find(" course.")]
    deg_attr = deg_attr.split(", and ")
    return "\n".join(deg_attr)


def load_json_into_class(json_dict, load_section=True):
    """
    Loads a json object retrieved from the API into an EmbedCourse object.

    Sample Json:

    {
        "credit_hours": "3 hours.",
        "degree_attributes": "Quantitative Reasoning I course.",
        "description": "Basic concepts in computing and fundamental techniques for solving computational problems.
            Intended as a first course for computer science majors and others with a deep interest in computing.
            Credit is not given for both CS 124 and CS 125. Prerequisite: Three years of high school mathematics
            or MATH 112.",
        "gpa": "None",
        "label": "CS 124",
        "name": "Introduction to Computer Science I",
        "number": 124,
        "subject": "CS",
        "yearterm": "Spring 2022"
    }

    """
    # we don't always want the section -- what if the person didn't request it?
    section = None
    if load_section:
        section = json_dict["section"]
    return CourseMessageContent(
        subject=json_dict["subject"],
        number=json_dict["number"],
        section=section,
        name=json_dict["name"],
        hours=json_dict["credit_hours"],
        label=json_dict["label"],
        description=json_dict["description"],
        gpa=json_dict["gpa"],
        deg_attr=process_deg_attr(json_dict["degree_attributes"]),
        status=json_dict["yearterm"],
    )


async def cache_class(course: Course, raw: dict, time_length=600) -> None:
    """
    https://stackoverflow.com/questions/58774718/asyncio-in-corroutine-runtimeerror-no-running-event-loop
    :param course: the course requested (ie: 'CS 124')
    :param raw: dict of the response that would be returned
    :param time_length: How long to cache for (in seconds). Default 10 min
    :return: None
    """
    # convert course to uppercase
    course = (course.subject.upper(), course.number)
    if course in course_cache:
        return

    mutex.acquire()
    course_cache[course] = raw
    mutex.release()

    await asyncio.sleep(time_length)

    mutex.acquire()
    course_cache.pop(course)
    mutex.release()

    api_base_url = BASE_API_URL


async def get_class_from_api(course: Course, session: aiohttp.ClientSession = None):
    """Use Aiohttp to send an async api request"""
    # check if class is cached:
    # if course in course_cache:
    #     return course_cache[course]

    if session is None:
        session = aiohttp.ClientSession()
    params = {"subject": course.subject.upper(), "number": course.number}
    async with session.get(api_base_url + f"/api/classes/", params=params) as resp:
        if resp.status != 200:
            return None
        res = await resp.json()
        if len(res) == 0:
            return None

        # TODO: Handle multiple classes
        # res returns a list of classes, we only want the first one
        return res[0]


async def get_class(course: Course, session: aiohttp.ClientSession = None):
    """
    Gets a class from the API.

    :param course: tuple of (subject, number)
    :param session: the aiohttp session to use
    :return: EmbedCourse object
    """

    raw = await get_class_from_api(course, session)
    if raw is None:
        return None

    # asyncio.create_task(cache_class(course, raw))
    return load_json_into_class(raw, load_section=course.has_section())


async def search_classes_from_api(
    search_query: str, session: aiohttp.ClientSession = None
):
    """
    Makes a GET request to api/classes/search for the provided query.
    :param
    """
    if session is None:
        session = aiohttp.ClientSession()

    url = api_base_url + f"/api/classes/search/"

    if session is None:
        session = aiohttp.ClientSession()

    params = {"query": search_query}
    async with session.get(url, params=params) as resp:
        if resp.status != 200:
            return None
        res = await resp.json()
        if len(res) == 0:
            return None

        for item in res:
            if item["raw"]["label"] not in course_cache:
                course = Course(
                    subject=item["raw"]["subject"], number=item["raw"]["number"]
                )
                asyncio.create_task(cache_class(course, item["raw"]))

        return res


async def search_classes(query: str, session: aiohttp.ClientSession = None):
    """
    Searches for a class using the API.

    :param query: the query to search for
    :param session: the aiohttp session to use
    :return: SearchCoursesResult object
    """
    res = await search_classes_from_api(query, session)
    if res is None:
        return SearchMessageContent(query, None)

    return SearchMessageContent(query, res)
