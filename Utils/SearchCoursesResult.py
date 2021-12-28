import nextcord
import random

EMBED_COLORS = [0x12294b, 0xe84b38]
MAX_EMBED_ITEMS = 4


class SearchCoursesResult:
    def __init__(self, search_query, query_results):
        self.search_query = "Query: " + " ".join(search_query)
        self.query_results = query_results
        self.query_result_class_labels = [] if query_results is None else [x['label'] for x in query_results]

    def get_embed(self):
        embed = nextcord.Embed(title=self.search_query, color=random.choice(EMBED_COLORS))
        if self.query_results is None:
            embed.description = "No courses found for this query."
            return embed

        iter_range_max = min(MAX_EMBED_ITEMS, len(self.query_results))
        for i in range(iter_range_max):
            curr_res = self.query_results[i]

            desc = f"""*Relevant text:* {curr_res['description']}
            *Credit hours:* {curr_res['credit_hours']}
            *Most Recently Offered In:* {curr_res['yearterm']}             
            """
            name = curr_res['label'] + ": " + curr_res['name']
            embed.add_field(name=name, value=desc, inline=False)

        embed.set_footer(
            text=f"Showing the first {iter_range_max} results. Click the buttons below to get more information.")

        return embed

    def get_labels(self):
        """
        Returns list of courses that the query returned.
        """
        return self.query_result_class_labels



