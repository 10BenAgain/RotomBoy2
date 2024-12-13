import json
import discord

from datetime import datetime
from discord.ext import commands
from utils.creator import Cases


class Logs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        with open("config.json") as c:
            config = json.load(c)
            self.server_log_id = config['channels']['serverlog']
        self.creator = Cases(self.bot, self.server_log_id)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        logging_channel = self.bot.get_channel(self.server_log_id)
        emb = discord.Embed(colour=discord.Colour.green())
        emb.timestamp = member.joined_at
        emb.set_thumbnail(url=member.display_avatar)
        emb.set_author(
            name="{} {} has joined ({})".format("\N{SQUARED NEW}", member.name, member.id),
            icon_url=member.display_avatar
        )
        emb.add_field(
            name="**Member**",
            value=member.mention,
            inline=True
        )
        emb.add_field(
            name="**Member ID**",
            value=f"`{member.id}`",
            inline=True
        )
        emb.add_field(
            name="**Total Users**",
            value=member.guild.member_count,
            inline=True
        )
        emb.add_field(
            name="**Account Created on:**",
            value=member.created_at.strftime("%m/%d/%Y"),
            inline=True
        )
        await logging_channel.send(embed=emb)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        logging_channel = self.bot.get_channel(self.server_log_id)
        emb = discord.Embed(
            title="{} {} has left the guild".format("\N{DOOR}", member.name),
            color=discord.Colour.red()
        )
        emb.timestamp = datetime.now()
        emb.set_thumbnail(url=member.display_avatar)
        emb.add_field(name="**Member**", value=member.mention, inline=True)
        emb.add_field(name="**Member ID**", value=f"`{member.id}`", inline=True)
        emb.add_field(name="**Total Users**", value=member.guild.member_count, inline=True)

        await logging_channel.send(embed=emb)

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if message.author.id != self.bot.user.id:
            user = message.author
            emb = discord.Embed(colour=discord.Colour.red())
            emb.timestamp = datetime.now()

            # Checks if attachment was sent with no context
            if not message.content.isspace():
                if message.content != "":
                    emb.description = f"> {message.content}"

            emb.set_author(
                name="{} {} ({}) | Deleted message".format("\N{CROSS MARK}", user.name, user.id),
                icon_url=message.author.display_avatar
            )

            emb.add_field(name="**Channel**", value=message.channel.mention, inline=True)
            emb.add_field(name="**Member**", value=message.author.mention, inline=True)
            emb.add_field(name="**Message ID**", value=f"`{message.id}`", inline=True)

            if len(message.attachments) != 0:
                out = " "
                for i in message.attachments:
                    out += f"`{i.filename}`\n"
                emb.add_field(name="**Attachment(s)**", value=out)

            if len(message.stickers) != 0:
                out = " "
                for i in message.stickers:
                    out += f"`{i.name}`\n"
                emb.add_field(name="**Sticker(s)**", value=out)

            logging_channel = self.bot.get_channel(self.server_log_id)
            await logging_channel.send(embed=emb)

    @commands.Cog.listener()
    async def on_message_edit(self, origin: discord.Message, edit: discord.Message):
        if edit.pinned:
            return

        if origin.author.id != self.bot.user.id:
            if not origin.author.bot:
                emb = discord.Embed(colour=discord.Colour.orange())
                emb.timestamp = datetime.now()
                emb.description = f"**Original Message**:\n> {origin.content}\n\n**Edited Message**:\n> {edit.content}"

                emb.set_author(
                    name="{}{}  ({}) | Message edited"
                    .format(
                        "\N{SPEECH BALLOON}",
                        origin.author.name,
                        origin.author.id
                    ),
                    icon_url=origin.author.display_avatar)

                emb.add_field(name="**Channel**", value=origin.jump_url, inline=True)
                emb.add_field(name="**Member**", value=origin.author.mention, inline=True)
                emb.add_field(name="**Message ID**", value=f"`{origin.id}`", inline=True)
                logging_channel = self.bot.get_channel(self.server_log_id)

                await logging_channel.send(embed=emb)


async def setup(bot):
    await bot.add_cog(Logs(bot))
