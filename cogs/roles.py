import json
import logging
import discord

from discord.ext import commands
from utils.creator import Cases


class Roles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger('rotom')
        with open("config.json") as c:
            config = json.load(c)
            self.channel_id = config['channels']['serverlog']
        self.creator = Cases(self.bot, self.channel_id)

    @commands.group()
    async def role(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send(
                "You are missing a subcommand argument."
                "```Example:\n"
                "\t[p] role add <role> <user>\n"
                "\t{}role add Admin {}``` ".format(self.bot.command_prefix, ctx.author.name)
            )

    @commands.has_role("Wow!")
    @role.command(name="add")
    async def add_role(self, ctx, role: discord.Role, user: discord.Member = None):
        if user is None:
            user = ctx.author

        if role > ctx.author.top_role:
            return await ctx.send("I am unable to add a role greater than your top role in the server hierarchy")

        if user.id == ctx.author.id and role in user.roles:
            return await ctx.send("You already have that role.")
        elif role in user.roles:
            return await ctx.send(f"That user already has role `{role.name}`")

        else:
            try:
                await user.add_roles(role)
                await ctx.send(f"Added `{role.name}` to {user.name}")
            except discord.HTTPException as e:
                self.logger.error(e)

    @commands.has_role("Wow!")
    @role.command(name="remove")
    async def del_role(self, ctx, role: discord.Role, user: discord.Member = None):
        if user is None:
            user = ctx.author
        if role > ctx.author.top_role:
            return await ctx.send("I am unable to delete a role greater than your top role in the server hierarchy")

        if user.id == ctx.author.id and role not in user.roles:
            return await ctx.send("You don't have that role.")
        elif role not in user.roles:
            return await ctx.send(f"That user does not have that role: `{role.name}`")
        else:
            try:
                await user.remove_roles(role)
                await ctx.send(f"Removed `{role.name}` to {user.name} ")
            except discord.HTTPException as e:
                self.logger.error(e)

    @commands.has_role("Wow!")
    @role.command(name="info")
    async def info(self, ctx, role: discord.Role = None):
        if role is None:
            role = ctx.author.top_role

        role_count = len(ctx.guild.roles) - role.position
        emb = discord.Embed(colour=role.colour)
        emb.set_author(name=f"{role.name}")
        emb.add_field(name=f"**Members**", value=len(role.members), inline=False)
        emb.add_field(name="**Position**", value=role_count, inline=False)
        emb.add_field(name="**Color**", value=role.colour, inline=False)
        emb.add_field(name="**Mentionable**", value=role.mentionable, inline=False)
        emb.timestamp = role.created_at
        await ctx.send(embed=emb)

    @add_role.error
    @del_role.error
    async def role_handler(self, ctx, error):
        if isinstance(error, commands.RoleNotFound):
            await ctx.send("I wasn't able to find that role")
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send("I wasn't able to find that user")
        elif isinstance(error, discord.ext.commands.MissingRole):
            await ctx.send("You are missing the required role to run this command.")
        elif isinstance(error, commands.MissingRequiredArgument):
            if ctx.command.name == "add":
                await ctx.send(
                    "You are missing a required argument."
                    "```Example:\n"
                    "\t[p] role add <role> <user>\n"
                    "\t{}role add Admin {}``` ".format(self.bot.command_prefix, ctx.author.name)
                )
            if ctx.command.name == "remove":
                await ctx.send(
                    "You are missing a required argument."
                    "```Example:\n"
                    "\t[p] role remove <role> <user>\n"
                    "\t{}role remove Admin {}``` ".format(self.bot.command_prefix, ctx.author.name)
                )
        else:
            self.logger.error(error)
            await self.creator.create_error_case(ctx, error)


async def setup(bot):
    await bot.add_cog(Roles(bot))
