import json

import discord
from discord.ext import commands


class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        with open("config.json") as c:
            config = json.load(c)
            self.welcome_channel = config['channels']['welcome']

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        welcome = self.bot.get_channel(self.welcome_channel)
        emb = discord.Embed(colour=discord.Colour.green())
        emb.title = f"Welcome to {member.guild.name}, {member.name}!"
        emb.description = "Make sure to read the <#1178078011711561771> and grab a role from <#1179588487763198022>"
        await welcome.send(content=member.mention, embed=emb)


async def setup(bot):
    await bot.add_cog(Welcome(bot))
