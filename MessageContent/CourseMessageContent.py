import discord
import re
import random
from MessageContent.MessageContent import MessageContent



mistakes = ['Am I wrong?',
            'Did I make a mistake?',
            'Have a suggestion?']


# Example url: https://courses.illinois.edu/schedule/2022/Spring/CS/124
# year_term is status, ie "Spring 2022"
# course_name is the name of the course, ie "CS 124"
def get_url_from_year_term(year_term, course_name):
    year_term = year_term.split(' ')
    course_name = course_name.split(' ')
    base_url = 'https://courses.illinois.edu/schedule/'
    base_url += year_term[1] + '/' + year_term[0] + '/'
    base_url += course_name[0] + '/' + course_name[1]

    return base_url

class CourseMessageContent(MessageContent):
    def __init__(self, subject=None, number=None, name=None, hours=None, label=None, description=None, gpa=None,
                 deg_attr=None, status=None):
        super().__init__()
        self.subject = subject  # CS
        self.number = number  # 124
        self.name = name  # Introduction to Computer Science I
        self.hours = hours  # 3
        self.label = label  # CS 124
        self.description = description  # Basic concepts in computing and ...
        self.gpa = gpa  # No Data
        self.deg_attr = deg_attr  # Quantitative Reasoning
        self.status = status  # Offered in ...

    def get_embed(self) -> discord.Embed:
        """
        Returns the embed for this class to send in a channel.
        """
        title = self.label + ": " + self.name
        url = get_url_from_year_term(self.status, self.name)
        embed = discord.Embed(title=title, description=self.description, url=url, color=self.color)
        embed.add_field(name='Credit Hours', value=self.hours, inline=False)
        embed.add_field(name='Average GPA', value=self.gpa, inline=False)

        if self.deg_attr is not None:  # TODO add to api, API doesnt currently support this for some reason
            embed.add_field(name='Degree Attributes', value=self.deg_attr, inline=False)

        embed.add_field(name='Most Recently Offered In', value=self.status, inline=False)

        if random.random() < 0.25:
            embed.set_footer(text=random.choice(mistakes) + ' Make an issue on GitHub (timot3/uiuc-classes-bot).')
        elif random.random() < 0.5:
            embed.set_footer(text='This project is run entirely by one student, and would not be available without '
                                  'your support! Please consider donating at https://www.buymeacoffee.com/timot3.') 

        return embed


class FailedRequestContent(MessageContent):
    def __init__(self, subject=None, number=None):
        # set the color to red
        self.color = 0xff0000

        if subject is None or number is None:
            self.label = ""
        else:
            self.label = subject.upper() + " " + number

    def get_embed(self, description=None) -> discord.Embed:
        """
        Returns the embed for this class to send in a channel.
        """
        if description is None:
            description = ":x: No courses found for this query."
        embed = discord.Embed(title=self.label, color=self.color)
        embed.description = description
        return embed
