import json
import logging
import sys

from discord.ext import commands
from utils.creator import Cases


class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger('rotom')
        self.cogs = "cogs."
        with open("config.json") as c:
            config = json.load(c)
            self.channel_id = config['channels']['serverlog']
        self.creator = Cases(self.bot, self.channel_id)

    @commands.has_permissions(administrator=True)
    @commands.command()
    async def reload(self, ctx, cog):
        if cog.lower() == "owner":
            return await ctx.send("Unable to reload owner cog.")

        if cog == "errors":
            await self.bot.reload_extension("utils.error_handler")
        else:
            await self.bot.reload_extension(self.cogs + cog.lower())
            await ctx.send(f"Reloaded extension `{cog.lower()}`")

    @commands.has_permissions(administrator=True)
    @commands.command()
    async def load(self, ctx, cog):
        if cog == "errors":
            await self.bot.reload_extension("utils.error_handler")
        else:
            await self.bot.reload_extension(self.cogs + cog.lower())
            await ctx.send(f"Reloaded extension `{cog.lower()}`")

    @commands.has_permissions(administrator=True)
    @commands.command()
    async def unload(self, ctx, cog):
        if cog.lower() == "owner":
            return await ctx.send("Unable to unload owner cog.")

        if cog == "errors":
            await self.bot.reload_extension("utils.error_handler")
        else:
            await self.bot.reload_extension(self.cogs + cog.lower())
            await ctx.send(f"Reloaded extension `{cog.lower()}`")

    @commands.has_permissions(administrator=True)
    @commands.command(name='shutdown')
    async def shutdown(self, ctx):
        wave = '\N{WAVING HAND SIGN}'
        await ctx.send("Shutting down... {}".format(wave))
        self.logger.info("Bot issued shutdown command. Exiting")
        try:
            await ctx.bot.close()
            sys.exit(-1)
        except Exception as e:
            self.logger.exception(e)

    @commands.has_permissions(administrator=True)
    @commands.command(name='shutdown')
    async def shutdown(self, ctx):
        wave = '\N{WAVING HAND SIGN}'
        await ctx.send("Restarting... {}".format(wave))
        self.logger.info("Bot issued restart command. Exiting")
        try:
            await ctx.bot.close()
            sys.exit(1)
        except Exception as e:
            self.logger.exception(e)

    @reload.error
    @load.error
    @unload.error
    async def cog_handler(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("You are missing a required argument. "
                           "Please specify the extension to reload")
        elif isinstance(error, commands.ExtensionAlreadyLoaded):
            await ctx.send("Extension is already loaded!")
        elif isinstance(error, commands.ExtensionNotFound):
            await ctx.send("I wasn't able to find the specified extension")
        elif isinstance(error, commands.ExtensionNotLoaded):
            await ctx.send("The specified extension is already loaded")

        elif isinstance(error, commands.CommandInvokeError):
            await ctx.send("I'm not sure if this extension exits. "
                           "Check you console logs for details")
        else:
            await self.creator.create_error_case(ctx, error)
            self.logger.exception(error)


async def setup(bot):
    await bot.add_cog(Owner(bot))
