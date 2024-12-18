import discord
import logging

from enum import Enum
from datetime import datetime
from discord.ext import commands

GENERIC_PROCESS_ERROR = (
    "Oops! I wasn't able to process that request. "
    "Please check your console logs for details"
)

MISSING_USER_ARGUMENT = (
    "You are missing a required argument. "
    "Please specify a user ID"
)


class Flags(Enum):
    warn = "\U0001F6A9"
    unban = "\U0001F3F3"
    kick = "\U0001F462"
    ban = "\U0001FA93"


class Cases:
    def __init__(self, bot: commands.Bot, log_channel: int):
        self.bot = bot
        self.channel_id = log_channel
        self.logger = logging.getLogger('rotom')

    async def create_error_case(self, ctx: commands.Context, error: Exception):
        emb = discord.Embed(colour=discord.Colour.red())
        emb.set_author(
            name="An unhandled error has occurred",
            url=ctx.message.jump_url,
            icon_url=ctx.author.display_avatar
        )
        emb.description = f"```{error}```"
        emb.add_field(name="`Type`", value=f"> {type(error).__name__}")
        emb.add_field(name="`Author`", value=f"> {ctx.author.mention}")
        emb.add_field(name="`Command`", value=f"> {ctx.command.name}")
        emb.add_field(name="`Context`", value=f"> {ctx.message.jump_url}")
        emb.timestamp = datetime.now()
        self.logger.exception(error)
        await self.bot.get_channel(self.channel_id).send(embed=emb)

    async def create_modlog_case(self, user, case: str, author: discord.Member, reason, count=None):
        emb = discord.Embed(colour=discord.Colour.dark_grey())

        if case == "warn":
            emb.description = f"> Warn {Flags.warn.value}"
        elif case == "kick":
            emb.description = f"> Kick {Flags.kick.value}"
        elif case == "kickwarn":
            emb.description = f"> Kick-warn {Flags.kick.value}"
        elif case == "ban":
            emb.description = f"> Ban {Flags.ban.value}"
        elif case == "unban":
            emb.description = f"> Unban {Flags.unban.value}"
        else:
            emb.description = f"> How did we get here?"

        emb.set_author(
            name="{} | ({})".format(user.name, user.id),
            icon_url=user.display_avatar
        )
        emb.timestamp = datetime.now()
        emb.add_field(name="**Reason**", value=f"> {reason}")
        emb.add_field(name="**Moderator**", value=f"> {author.name}\n> {author.id}")

        if count is None:
            return await self.bot.get_channel(self.channel_id).send(embed=emb)
        else:
            emb.add_field(name="**Warn Count**", value=f"> {count}")
            return await self.bot.get_channel(self.channel_id).send(embed=emb)
