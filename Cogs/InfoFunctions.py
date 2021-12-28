import nextcord
from nextcord.ext import commands
import asyncio

# Add a help command to the bot.
class InfoFunctions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='info', aliases=['help'])
    async def await_info(self, ctx):
        desc = 'To get a class, do [`department` `number`]. For example: `[cs 225]`. This is case insensitive, ' \
            'and the space between the department and the class number is optional. '
        embed = nextcord.Embed(title='Help', description=desc, url='https://github.com/timot3/uiuc-classes-bot/')
        embed.add_field(name='AP - c$AP', value='Links the UIUC AP credit page')
        embed.add_field(name='Geneds - c$Gened', value='Links the Geneds by GPA page.')
        embed.add_field(name='Search - c$search <query>', value='Runs a search with the given query.')

        embed.add_field(name='API Latency', value=str(round(self.bot.latency * 1000, 1))+'ms.')
        embed.set_footer(text='Having issues with the bot? Click the "Help" text at the top of this embed, and make an issue on Github.')
        await ctx.send(embed=embed)


    @commands.command(name='AP', aliases=['Ap', 'ap'])
    async def await_ap(self, ctx):
        await ctx.send('https://admissions.illinois.edu/Apply/Freshman/college-credit-AP')


    @commands.command(name='geneds', aliases=['gened'])
    async def await_ap(self, ctx):
        await ctx.send('http://waf.cs.illinois.edu/discovery/every_gen_ed_at_uiuc_by_gpa/')


    @commands.command(name='users', aliases=['usercount'])
    async def await_usercount(self, ctx):
        members = []
        for guild in self.bot.guilds:
            for member in guild.members:
                members.append(member.id)
        total_members = len(members)
        unique_members = len(set(members))
        guilds = len(self.bot.guilds)
        await ctx.send('Online with {} servers and {} total members (Unique members: {}).'
                    .format(guilds, total_members, unique_members))

def setup(bot):
    bot.add_cog(InfoFunctions(bot))