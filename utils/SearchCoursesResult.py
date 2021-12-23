import nextcord
from dataclasses import dataclass
import random

EMBED_COLORS = [0x12294b, 0xe84b38]
MAX_EMBED_ITEMS = 5


class SearchCoursesResult:
    def __init__(self, search_query, query_results):
        self.search_query = "Query: " + " ".join(search_query)
        self.query_results = query_results

    def get_embed(self):
        embed = nextcord.Embed(title=self.search_query, color=random.choice(EMBED_COLORS))
        if self.query_results is None:
            embed.description = "No courses found for this query."
            return embed

        for i in range(min(MAX_EMBED_ITEMS, len(self.query_results))):
            curr_res = self.query_results[i]

            desc = f"""Relevant text: {curr_res['description']}
            Credit hours: {curr_res['credit_hours']}             
            """
            name = curr_res['label'] + ": " + curr_res['name']
            embed.add_field(name=name, value=desc, inline=False)

        return embed



