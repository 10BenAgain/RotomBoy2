import discord
from discord.ext import commands


class Misc(commands.Cog):
    """A random assortment of commands.
    The purpose of which to essentially troll the average THT member
    If Abel wants to add command or 'tag' into the bot, it should go here."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='explain', help='I need more context from you')
    async def explain(self, ctx):
        emb = discord.Embed(title="How to Properly Explain a Problem", colour=discord.Colour.red())
        emb.description = (
            "If you are having an issue you need to FULLY EXPLAIN the following things.\n\n"
            "> 1. Exactly what is supposed to happen but is not.\n"
            "> 2. What is happening instead.\n"
            "> 3. How to reproduce the error.\n\n"
            "Please make sure you have thoroughly read the Guides and FAQs before asking for further "
            "support"
        )
        await ctx.send(embed=emb)

    @commands.command(name='read', help='Reading is hard')
    async def cant_read(self, ctx):
        file = discord.File("cogs/assets/reading-sign.gif", filename="read.gif")
        embed = discord.Embed(color=discord.Color.purple())
        embed.set_image(url="attachment://read.gif")
        await ctx.send(file=file, embed=embed)
        await ctx.message.delete()

    @commands.command(name='noreplyping', help='ping me and I\'ll scream')
    async def no_reply_ping(self, ctx):
        file = discord.File("cogs/assets/discord-reply.gif", filename="ping.gif")
        embed = discord.Embed(color=discord.Color.dark_red())
        embed.set_image(url="attachment://ping.gif")
        await ctx.send(file=file, embed=embed)

    @commands.command(name='uc', help='Posts under construction image as embed')
    async def read(self, ctx):
        file = discord.File("cogs/assets/construct.jpeg", filename="uc.jpeg")
        embed = discord.Embed(color=discord.Color.blue())
        embed.set_image(url="attachment://uc.jpeg")
        await ctx.send(file=file, embed=embed)
        await ctx.message.delete()

    @commands.command(name='elder', help='The Elder')
    async def elder(self, ctx):
        embed = discord.Embed(title="The High Table", colour=discord.Color.yellow())
        embed.description = "> <@&810013892670521364>  Resides over the High Table and is immune to the server rules."
        await ctx.send(embed=embed)

    @commands.command(name='try', help='do it')
    async def try_it(self, ctx):
        await ctx.send('https://tryitands.ee')

    @commands.command(name='surprise', help='What is zacian.net?')
    async def try_it(self, ctx):
        await ctx.send(
            'Yes, the Zacian.net Pokémon you received in surprise trade is legal. You will not get banned '
            'or in trouble for having it. Keep it or release it, but do keep the Master Ball. It\'s a way '
            'to promote this server.'
        )

    @commands.group()
    async def sql(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("You are missing a required argument")

    @sql.command(name="warns")
    async def warns(self, ctx):
        await ctx.send(
            "```sql\nCREATE table warns(\nwarn_id INT PRIMARY KEY AUTO_INCREMENT,\nuser_id BIGINT,"
            "\nauthor_id BIGINT,\nauthor_name VARCHAR(25),\nreason VARCHAR(2000),\ndate_time datetime\n);```"
        )


async def setup(bot):
    await bot.add_cog(Misc(bot))
