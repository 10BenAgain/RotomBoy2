import json
from datetime import datetime

import discord
import logging
from discord.ext import commands

from utils.creator import Cases


class ErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger('rotom')
        self.warn_icon = "\U0001F6AB"
        with open('config.json') as c:
            config = json.load(c)
            self.server_log_id = config['channels']['serverlog']
        self.case_creator = Cases(bot, self.server_log_id)

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error):
        if hasattr(ctx.command, 'on_error'):
            return

        if isinstance(error, discord.ext.commands.CommandNotFound):
            await ctx.send(" I wasn't able to find that command.")
        elif isinstance(error, discord.ext.commands.CheckFailure):
            await ctx.send(f"{self.warn_icon} You are missing the required permission to run this command.")
        elif isinstance(error, discord.ext.commands.BotMissingPermissions):
            await ctx.send(f"{self.warn_icon} I do not have the required permissions to do this.")
        elif isinstance(error, discord.ext.commands.CommandInvokeError):
            await ctx.send("An error has occurred while invoking this command. "
                           "Check your console logs for more details")
            self.logger.error(error)

            try:
                await self.case_creator.create_error_case(ctx, error)
            except discord.HTTPException:
                pass

        else:
            if ctx.command:
                await ctx.send(f"{self.warn_icon} An unexpected error occurred while processing this request.")
            self.logger.error(error)
            try:
                await self.case_creator.create_error_case(ctx, error)
            except discord.HTTPException:
                pass


async def setup(bot):
    await bot.add_cog(ErrorHandler(bot))
