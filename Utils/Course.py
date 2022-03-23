import nextcord
import re
import random
from dataclasses import dataclass

# Illini Blue ('Midnight'), Illini Orange('Cinnabar)
colors = [0x12294b, 0xe84b38]

mistakes = ['Am I wrong?',
            'Did I make a mistake?',
            'Have a suggestion?']


# # Function to get department and class number.
# def get_class_id(class_code):
#     # Group 1:([A-Za-z]{2,4})
#     # Group 2:(\d{3})
#     temp = re.findall('([A-Za-z]{2,4})\s?(\d{3})', class_code)
#     return temp[0][0], temp[0][1]


# Example url: https://courses.illinois.edu/schedule/2022/Spring/CS/124
# year_term is status, ie "Spring 2022"
# course_name is the name of the course, ie "CS 124"
def get_url_from_year_term(year_term, course_name):
    print(year_term)
    year_term = year_term.split(' ')
    course_name = course_name.split(' ')
    base_url = 'https://courses.illinois.edu/schedule/'
    base_url += year_term[1] + '/' + year_term[0] + '/'
    base_url += course_name[0] + '/' + course_name[1]

    return base_url


# subject,number,name,hours,label,description,GPA
@dataclass
class EmbedCourse:
    label: str  # "CS 124"
    subject: str
    number: str  # "124"
    name: str  # "Introduction to Computer Science I"
    description: str  # "Basic concepts in computing and fundamental techniques for solving computational problems..."
    GPA: str  # "No Data"
    hours: str  # "3"
    deg_attr: str  # "Quantitative Reasoning"
    status: str  # "Offered in

    def get_embed(self) -> nextcord.Embed:
        """
        Returns the embed for this class to send in a channel.
        """
        title = self.label + ": " + self.name
        url = get_url_from_year_term(self.status, self.label)
        embed = nextcord.Embed(title=title, description=self.description, url=url, color=random.choice(colors))
        embed.add_field(name='Credit Hours', value=self.hours, inline=False)
        embed.add_field(name='Average GPA', value=self.GPA, inline=False)

        if self.deg_attr is not None:  # TODO add to api, API doesnt currently support this for some reason
            embed.add_field(name='Degree Attributes', value=self.deg_attr, inline=False)

        embed.add_field(name='Most Recently Offered In', value=self.status, inline=False)

        if random.random() < 0.25:
            embed.set_footer(text=random.choice(mistakes) + ' Make an issue on GitHub (timot3/uiuc-classes-bot).')

        return embed


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
    if deg_attr == 'None':
        return None
    deg_attr = deg_attr[:deg_attr.find(' course.')]
    deg_attr = deg_attr.split(', and ')
    return '\n'.join(deg_attr)

def load_json_into_class(json_dict):
    """
    Loads a json object retrieved from the API into an EmbedCourse object.

    Sample Json:

    {
        "Credit Hours": "3 hours.",
        "Degree Attributes": "Quantitative Reasoning I course.",
        "Description": "Basic concepts in computing and fundamental techniques for solving computational problems.
            Intended as a first course for computer science majors and others with a deep interest in computing.
            Credit is not given for both CS 124 and CS 125. Prerequisite: Three years of high school mathematics
            or MATH 112.",
        "GPA": "None",
        "Label": "CS 124",
        "Name": "Introduction to Computer Science I",
        "Number": 124,
        "Subject": "CS",
        "YearTerm": "Spring 2022"
    }

    """

    return EmbedCourse(subject=json_dict['subject'],
                       number=json_dict['number'],
                       name=json_dict['name'],
                       hours=json_dict['credit_hours'],
                       label=json_dict['label'],
                       description=json_dict['description'],
                       GPA=json_dict['gpa'],
                       deg_attr=process_deg_attr(json_dict['degree_attributes']),
                       status=json_dict['yearterm'])
