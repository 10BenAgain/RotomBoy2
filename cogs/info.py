import logging

import discord

from discord.ext import commands


class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.star = 1182456812084146279
        self.logger = logging.getLogger('rotom')

    @commands.command(name='ping')
    async def ping(self, ctx):
        await ctx.send(f'**Pong!** Latency: {round(self.bot.latency * 1000)}ms')

    @commands.command(name='userinfo', aliases=['ui'])
    async def userinfo(self, ctx, user: discord.Member = None):
        if user is None:
            user = ctx.author

        emb = discord.Embed(colour=user.top_role.colour)
        emb.set_thumbnail(url=user.display_avatar)
        if user.nick is None:
            emb.set_author(name=f"{user.name}")
        else:
            emb.set_author(name=f"{user.name} ({user.nick})")
        emb.add_field(name="`Joined`", value="> {}"
                      .format(user.joined_at.strftime("%b %d, %Y")))
        emb.add_field(name="`Account Created`", value="> {}"
                      .format(user.created_at.strftime("%b %d, %Y")))
        if user.premium_since is not None:
            emb.add_field(name="**Boosted Since**", value="> {}"
                          .format(user.premium_since.strftime("%b %d, %Y")))
        if user.get_role(self.star) in user.roles:
            emb.description = "We got ourselves a star!"
        if user.roles is not None:
            if len(user.roles) > 1:
                roles = ''.join(f"{i.mention} " for i in reversed(user.roles[1:]))
                emb.add_field(name="`Roles`", value=roles, inline=False)
        emb.set_footer(text=user.id)
        await ctx.send(embed=emb)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if "https://discord.com/channels/" not in message.content:
            return
        try:
            msg = await (discord.ext.commands.MessageConverter()
                         .convert(await self.bot.get_context(message), argument=message.content))
        except commands.BadArgument as e:
            self.logger.error(e)
            return await message.channel.send("An unexpected error has occurred. Check your console for details")

        emb = discord.Embed(colour=discord.Colour.orange())
        emb.set_author(name=f"{msg.author.name} said: ", icon_url=msg.author.display_avatar)
        emb.add_field(name="Context", value=msg.jump_url, inline=False)
        emb.add_field(name="Author ID", value=msg.author.id)
        emb.add_field(name="Message ID", value=msg.id)

        # Assumes one link at a time
        if msg.embeds:
            top = msg.embeds[0]
            emb.description = top.description
        else:
            emb.description = msg.content

        if msg.attachments:
            first = msg.attachments[0]
            emb.set_image(url=first)
            emb.description = first.filename

        emb.timestamp = msg.created_at
        await message.channel.send(embed=emb)


async def setup(bot):
    await bot.add_cog(Info(bot))
