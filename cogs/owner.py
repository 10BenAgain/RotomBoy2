import os
import sys
import json
import logging
import subprocess

from discord.ext import commands
from utils.creator import Cases


class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger('rotom')
        self.cogs = "cogs."
        self.cog_path = os.path.join(os.getcwd(), "cogs")
        if os.path.exists(self.cog_path):
            self.cog_list = []
            for cog in os.listdir(self.cog_path):
                if os.path.isfile(os.path.join(self.cog_path, cog)):
                    self.cog_list.append(cog.replace(".py", "").lower())

        with open("config.json") as c:
            config = json.load(c)
            self.channel_id = config['channels']['serverlog']
        self.creator = Cases(self.bot, self.channel_id)

    @commands.has_permissions(administrator=True)
    @commands.command()
    async def reload(self, ctx, cog: str):
        if cog.lower() not in self.cog_list:
            return await ctx.send("The specified extension does not appear in my working directory.")

        if cog.lower() == "owner":
            return await ctx.send("Unable to reload owner cog.")
        try:
            if cog == "errors":
                await self.bot.reload_extension("utils.error_handler")
            else:
                await self.bot.reload_extension(self.cogs + cog.lower())
            await ctx.send(f"Reloaded extension `{cog.lower()}`")
        except commands.ExtensionAlreadyLoaded:
            await ctx.send("The specified extension is already loaded")
        except commands.ExtensionNotLoaded:
            await ctx.send("The specified extension has not be previously loaded")

    @commands.has_permissions(administrator=True)
    @commands.command()
    async def load(self, ctx, cog: str):
        if cog.lower() not in self.cog_list:
            return await ctx.send("The specified extension does not appear in my working directory.")

        try:
            if cog == "errors":
                await self.bot.load_extension("utils.error_handler")
            else:
                await self.bot.load_extension(self.cogs + cog.lower())
            await ctx.send(f"Loaded extension `{cog.lower()}`")
        except commands.ExtensionAlreadyLoaded:
            await ctx.send("The specified extension is already loaded")

    @commands.has_permissions(administrator=True)
    @commands.command()
    async def unload(self, ctx, cog: str):
        if cog.lower() not in self.cog_list:
            return await ctx.send("The specified extension does not appear in my working directory.")

        if cog.lower() == "owner":
            return await ctx.send("Unable to unload owner cog.")
        try:
            if cog == "errors":
                await self.bot.unload_extension("utils.error_handler")
            else:
                await self.bot.unload_extension(self.cogs + cog.lower())
            await ctx.send(f"Unloaded extension `{cog.lower()}`")
        except commands.ExtensionNotLoaded:
            await ctx.send("The specified extension has not be previously loaded")

    @commands.has_permissions(administrator=True)
    @commands.command(name='shutdown')
    async def shutdown(self, ctx):
        wave = '\N{WAVING HAND SIGN}'
        await ctx.send("Shutting down... {}".format(wave))
        self.logger.info("Bot issued shutdown command. Exiting")
        try:
            await ctx.bot.close()
            sys.exit(0) # on-success
        except Exception as e:
            self.logger.exception(e)
            await self.creator.create_error_case(ctx, e)

    @commands.has_permissions(administrator=True)
    @commands.command(name='restart')
    async def restart(self, ctx):
        wave = '\N{WAVING HAND SIGN}'
        await ctx.send("Restarting... {}".format(wave))
        self.logger.info("Bot issued restart command. Exiting")
        try:
            await ctx.bot.close()
            sys.exit(1)
        except Exception as e:
            self.logger.exception(e)
            await self.creator.create_error_case(ctx, e)

    @commands.has_permissions(administrator=True)
    @commands.group()
    async def git(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("You are missing a required argument")

    @git.command(name="status")
    async def git_status(self, ctx):
        try:
            output = subprocess.run(['git', 'status'], check=True, shell=True, capture_output=True)
            formatted = output.stdout.decode('utf-8').strip("'")
            await ctx.send(f"```bash\n{formatted}```")
        except subprocess.CalledProcessError as e:
            self.logger.exception(e)
            await self.creator.create_error_case(ctx, e)

    @git.command(name="pull")
    async def git_pull(self, ctx):
        try:
            output = subprocess.run(['git', 'pull'], check=True, shell=True, capture_output=True)
            formatted = output.stdout.decode('utf-8').strip("'")
            await ctx.send(f"```bash\n{formatted}```")
        except subprocess.CalledProcessError as e:
            self.logger.exception(e)
            await self.creator.create_error_case(ctx, e)

    @git.command(name="add")
    async def git_add(self, ctx, arg):
        try:
            subprocess.run(['git', 'add', arg], check=True, shell=True, capture_output=True)
            output = subprocess.run(['git', 'status'], check=True, shell=True, capture_output=True)
            formatted = output.stdout.decode('utf-8').strip("'")
            await ctx.send(f"```bash\n{formatted}```")
        except subprocess.CalledProcessError as e:
            self.logger.exception(e)
            await self.creator.create_error_case(ctx, e)

    @git.command(name="commit")
    async def git_commit(self, ctx, message=None):
        if message is None:
            message = f"Committed by {ctx.author.name} via Discord commands"
        try:
            output = subprocess.run(['git', 'commit', '-m', message], check=True, shell=True, capture_output=True)
            formatted = output.stdout.decode('utf-8').strip("'")
            await ctx.send(f"```bash\n{formatted}```")
        except subprocess.CalledProcessError as e:
            self.logger.exception(e)
            await self.creator.create_error_case(ctx, e)

    @git.command(name="push")
    async def git_push(self, ctx):
        try:
            output = subprocess.run(['git', 'push'], check=True, shell=True, capture_output=True)
            formatted = output.stdout.decode('utf-8').strip("'")
            await ctx.send(f"```bash\n{formatted}```")
        except subprocess.CalledProcessError as e:
            self.logger.exception(e)
            await self.creator.create_error_case(ctx, e)

    @reload.error
    @load.error
    @unload.error
    async def cog_handler(self, ctx, error: Exception):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("You are missing a required argument. "
                           "Please specify the extension to reload")
        elif isinstance(error, commands.CommandInvokeError):
            self.logger.exception(error)
            await self.creator.create_error_case(ctx, error)

        else:
            await self.creator.create_error_case(ctx, error)
            self.logger.exception(error)


async def setup(bot):
    await bot.add_cog(Owner(bot))
