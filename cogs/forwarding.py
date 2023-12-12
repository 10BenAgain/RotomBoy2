import discord
import json

from datetime import datetime
from discord.ext import commands


class Forwarding(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        with open("config.json") as c:
            config = json.load(c)
            self.channel_id = config['channels']['forwarding']

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.id == self.bot.user.id:
            return
        if message.guild is None:
            emb = discord.Embed(color=discord.Color.gold())
            emb.timestamp = datetime.now()
            emb.set_author(name=f"{message.author.name} ({message.author.id})",
                           icon_url=message.author.display_avatar)
            emb.description = message.content
            if len(message.attachments) == 1:
                for i in message.attachments:
                    emb.set_image(url=i.url)
            elif len(message.attachments) > 1:
                for i in message.attachments:
                    emb.description += f"\n> {i.url}\n"

            await self.bot.get_channel(self.channel_id).send(embed=emb)
            await message.add_reaction('✅')

    @commands.has_permissions(administrator=True)
    @commands.command(name='dm')
    async def dm(self, ctx, user: discord.Member, *, message: str):
        emb = discord.Embed(color=discord.Color.gold(), description=message)
        emb.description = "> {}".format(message)
        emb.set_author(
            name="Sent by the Owner of this Bot",
            icon_url=self.bot.user.display_avatar)

        try:
            await user.send(embed=emb)
        except discord.Forbidden:
            ctx.send("I wasn't able to send this user a direct message.")
        await ctx.send("Message delivered to **{}** : `{}`".format(user.name, user.id))
        await ctx.message.add_reaction('✅')


async def setup(bot):
    await bot.add_cog(Forwarding(bot))
