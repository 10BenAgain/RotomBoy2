import json

import discord
import logging

from datetime import datetime
from discord.ext import commands
from database.SQLFunctions import Database
from utils.creator import Cases, GENERIC_PROCESS_ERROR, MISSING_USER_ARGUMENT, Flags


class Mod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger('rotom')
        self.database = Database()
        self.logging_channel = None
        self.modlog_channel = None
        with open("config.json") as c:
            config = json.load(c)
            self.server_log_id = config['channels']['serverlog']
            self.mod_log_id = config['channels']['modlog']
            self.invite = config['invite']
        self.creator = Cases(self.bot, self.server_log_id)

    async def send_direct(self, user: discord.Member or discord.User, author: discord.Member, case, reason, count=None):
        dm = discord.Embed(colour=discord.Colour.red())
        if case == "kick":
            action = "kicked from"
        elif case == "warn":
            action = "warned in"
        else:
            action = "banned from"

        dm.set_author(name=f"You have been {action} {author.guild.name}",
                      icon_url=self.bot.user.display_avatar)
        dm.timestamp = datetime.now()
        dm.add_field(name="**Reason**", value=reason)
        dm.add_field(name="**Moderator**", value=author.name)

        if case in ["kick", "kickawrn"]:
            dm.add_field(name="**Invite**", value=self.invite)
            dm.description = "If you wish to rejoin, please use the link provided below."
            if count == 3:
                dm.description += f"\n\n> This is your 3rd warning, the next one will result in a ban"

        if count is None or case == "ban":
            return await user.send(embed=dm)
        else:
            dm.add_field(name="**Warn Count**", value=count)
            return await user.send(embed=dm)

    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    @commands.command(name='warn')
    async def warn(self, ctx, user: discord.Member, *, reason=None):
        if user == ctx.author:
            return await ctx.send("You cannot warn yourself.")
        if user.bot:
            return await ctx.send("You cannot warn bots.")
        if user == ctx.guild.owner:
            return await ctx.send("You cannot warn the server owner.")
        if reason is None:
            reason = "No reason was provided."
        try:
            self.database.add_warn(user.id,
                                   ctx.author.id,
                                   ctx.author.name,
                                   reason)
        except Exception as error:
            self.logger.exception(error)
            return await ctx.send("I wasn't able to add the database entry for this warn. "
                                  "Check console logs for details")

        count = self.database.count_warns(user.id)

        try:
            message = ("{} **Member**: {} has been warned (Warn #{}) | **Reason**: `{}`"
                       .format(Flags.warn.value, user.mention, count, reason))
            if count > 3:
                try:
                    await self.send_direct(
                        user,
                        ctx.author,
                        "ban",
                        reason,
                        count)
                except discord.Forbidden as error:
                    self.logger.exception(error)

                try:
                    await user.ban(reason=reason, delete_message_days=0)
                    await ctx.send(content="{} **Member**: {} has been banned for exceeding the warn limit! | "
                                           "**Final Warning**: {}"
                                   .format(Flags.ban.value, user.id, reason))
                    await self.creator.create_modlog_case(user, "ban", ctx.author, reason, count)
                except Exception as error:
                    self.logger.exception(error)

            elif count == 3:
                message += " | The next warning will be an automatic ban."
                await ctx.send(content=message)
                await self.creator.create_modlog_case(user, "warn", ctx.author, reason, count)
                try:
                    await self.send_direct(user, ctx.author, "warn", reason, count)
                except discord.Forbidden as error:
                    self.logger.exception(error)
                    await ctx.send("The user has been warned but I was unable to send them a direct message.")
            else:
                await ctx.send(content=message)
                await self.creator.create_modlog_case(user, "warn", ctx.author, reason, count)
                try:
                    await self.send_direct(user, ctx.author, "warn", reason, count)
                except discord.Forbidden as error:
                    self.logger.exception(error)
                    await ctx.send("The user has been warned but I was unable to send them a direct message.")

        except Exception as error:
            self.logger.exception(error)
            await self.creator.create_error_case(ctx, error)
            await ctx.send(GENERIC_PROCESS_ERROR)

    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    @commands.command(name='listwarns')
    async def list_warns(self, ctx, user: discord.User):
        if user.bot:
            return await ctx.send("Nope.")
        try:
            warns = self.database.get_all_warns(user.id)
        except Exception as error:
            self.logger.exception(error)
            return await ctx.send("I wasn't able to access the database entries. "
                                  "Check console logs for details")

        warn_count = self.database.count_warns(user.id)
        if warn_count != 0:
            emb = discord.Embed(colour=discord.Colour.dark_orange())
            emb.set_author(name="Warnings for {} ({})".format(user.name, user.id),
                           icon_url=user.display_avatar)
            emb.timestamp = datetime.now()
            case = 1
            for i in warns:
                emb.add_field(name=f"**Entry** (#{case})",
                              value=f"> `Warn ID:{i[0]}`\n> Moderator: {i[3]}\n> Reason: {i[4]}\n> Date: {i[5]}",
                              inline=False)
                case += 1
        else:
            return await ctx.send("This user has no warnings.")
        await ctx.send(embed=emb)

    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    @commands.command(name='delwarn')
    async def delete_warn(self, ctx, warn_id: int):
        try:
            # O(1) yay
            warn = self.database.check_warn_exist(warn_id)
            if warn[0] != 1:
                return await ctx.send(f"I wasn't able to find that warn id ({warn_id})")
            else:
                self.database.remove_warn(warn_id)
                return await ctx.send(f"Warn ({warn_id}) has been removed successfully")
        except Exception as error:
            await self.creator.create_error_case(ctx, error)
            await ctx.send(GENERIC_PROCESS_ERROR)

    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    @commands.command(name="clearwarns")
    async def clear_warns(self, ctx, user: discord.User):
        try:
            for i in self.database.get_all_warn_id(user.id):
                self.database.remove_warn(i[0])
            await ctx.send("All warns from user have been removed.")
        except Exception as error:
            await self.creator.create_error_case(ctx, error)
            await ctx.send(GENERIC_PROCESS_ERROR)

    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    @commands.command(name='kick')
    async def kick(self, ctx, user: discord.Member, *, reason=None):
        if user == ctx.author:
            return await ctx.send("You cannot kick yourself.")
        if user == ctx.guild.owner:
            return await ctx.send("You cannot kick the server owner.")
        if reason is None:
            reason = "No reason was provided."

        try:
            try:
                await self.send_direct(user, ctx.author, "kick", reason)
            except discord.Forbidden as e:
                self.logger.error(e)
                await ctx.send("I wasn't able to deliver a message to the user.")

            await user.kick()
            message = ("{} **Member**: {} has been kicked | **Reason**: `{}`"
                       .format(Flags.kick.value, user.mention, reason))
            await ctx.send(content=message)
            await self.creator.create_modlog_case(user, "kick", ctx.author, reason)
        except Exception as error:
            await self.creator.create_error_case(ctx, error)
            await ctx.send(GENERIC_PROCESS_ERROR)

    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    @commands.command(name="kickwarn")
    async def kick_warn(self, ctx, user: discord.Member, *, reason=None):
        if user == ctx.author:
            return await ctx.send("You cannot kick yourself.")
        if user == ctx.guild.owner:
            return await ctx.send("You cannot kick the server owner.")
        if reason is None:
            reason = "No reason was provided."
        try:
            self.database.add_warn(user.id,
                                   ctx.author.id,
                                   ctx.author.name,
                                   reason)
        except Exception as e:
            self.logger.exception(e)
            return await ctx.send("I wasn't able to add the database entry for this warn. "
                                  "Check console logs for details")

        count = self.database.count_warns(user.id)
        try:
            message = ("{} **Member**: {} has been kick-warned (Warn# {}) | **Reason**: `{}`"
                       .format(Flags.kick.value, user.mention, count, reason))
            if count > 3:
                try:
                    await self.send_direct(user, ctx.author, "ban", reason)
                except discord.Forbidden as e:
                    self.logger.error(e)
                    await ctx.send("I wasn't able to deliver a message to the user.")

                await user.ban(reason=reason, delete_message_days=0)
                await ctx.send(
                    content="{} **Member**: {} has been banned for exceeding the warn limit! | **Final Warning**: "
                            "{}"
                    .format(Flags.ban.value, user.id, reason))
                await self.creator.create_modlog_case(user, "ban", ctx.author, reason, count)

            elif count == 3:
                try:
                    await self.send_direct(user, ctx.author, "kick", reason, count)
                except discord.Forbidden as e:
                    self.logger.error(e)
                    await ctx.send("I wasn't able to deliver a message to the user.")

                message += " | The next warning will be an automatic ban."
                await user.kick()
                await ctx.send(content=message)
                await self.creator.create_modlog_case(user, "kickwarn", ctx.author, reason, count)

            else:
                try:
                    await self.send_direct(user, ctx.author, "kick", reason, count)
                except discord.Forbidden as e:
                    self.logger.error(e)
                    await ctx.send("I wasn't able to deliver a message to the user.")

                await user.kick()
                await ctx.send(content=message)
                await self.creator.create_modlog_case(user, "kickwarn", ctx.author, reason, count)
        except Exception as error:
            await self.creator.create_error_case(ctx, error)
            await ctx.send(GENERIC_PROCESS_ERROR)

    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    @commands.command(name="ban")
    async def user_ban(self, ctx, user: discord.User, *, reason=None):
        if user == ctx.author:
            return await ctx.send("You cannot ban yourself.")
        if user == ctx.guild.owner:
            return await ctx.send("You cannot ban the server owner.")
        if reason is None:
            reason = "No reason was provided."

        message = ("{} **User**: {} has been banned | **Reason**: `{}`"
                   .format(Flags.ban.value, user.id, reason))
        try:
            await ctx.guild.fetch_ban(user)
            await ctx.send("That user is already banned.")
        except discord.NotFound:
            pass

            try:
                try:
                    await self.send_direct(user, ctx.author, "ban", reason)
                except discord.Forbidden as e:
                    self.logger.error(e)
                    await ctx.send("I wasn't able to deliver a message to the user.")

                await ctx.guild.ban(user)
                await ctx.send(content=message)
                await self.creator.create_modlog_case(user, "ban", ctx.author, reason)
            except discord.NotFound as e:
                self.logger.error(e)
                await ctx.send("I wasn't able to find the specified user.")

            except Exception as error:
                await self.creator.create_error_case(ctx, error)
                await ctx.send(GENERIC_PROCESS_ERROR)

    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    @commands.command(name="unban")
    async def un_ban(self, ctx, user: discord.User, *, reason=None):
        try:
            await ctx.guild.unban(user)
            await ctx.send(f"**User**: ``{user.id}`` has been unbanned! | **Reason**: `{reason}`")
        except discord.NotFound:
            await ctx.send("I wasn't able to find that user's ban information. Are you sure they are a banned user?")
        except Exception as error:
            await self.creator.create_error_case(ctx, error)
            await ctx.send(GENERIC_PROCESS_ERROR)

    @warn.error
    @kick_warn.error
    @user_ban.error
    @un_ban.error
    async def mod_handler(self, ctx, error):
        if isinstance(error, commands.MemberNotFound):
            await ctx.send("I wasn't able to find that user")
        elif isinstance(error, commands.MissingRequiredArgument):
            if ctx.command.name == "warn":
                return await ctx.send(f"You are missing a required argument.\n"
                                      f"```Example:\n\t[p] warn <member> (reason=None)\n"
                                      f"\t{self.bot.command_prefix}warn {ctx.author.id} Breaking the rules```")
            if ctx.command.name == "kickwarn":
                return await ctx.send(f"You are missing a required argument.\n"
                                      f"```Example:\n\t[p] kickwarn <member> (reason=None)\n"
                                      f"\t{self.bot.command_prefix}kickwarn {ctx.author.id} Breaking the rules```")
            if ctx.command.name == "ban":
                return await ctx.send(f"You are missing a required argument.\n"
                                      f"```Example:\n\t[p] ban <member> (reason=None)\n"
                                      f"\t{self.bot.command_prefix}ban {ctx.author.id} Breaking the rules```")
            if ctx.command.name == "unban":
                return await ctx.send(f"You are missing a required argument.\n"
                                      f"```Example:\n\t[p] unban <member> (reason=None)\n"
                                      f"\t{self.bot.command_prefix}unban {ctx.author.id} A miracle has occurred```")
        else:
            await self.creator.create_error_case(ctx, error)

    @clear_warns.error
    @list_warns.error
    @delete_warn.error
    async def warn_handler(self, ctx, error):
        if isinstance(error, commands.MemberNotFound):
            await ctx.send("I wasn't able to find that user")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(MISSING_USER_ARGUMENT)
        else:
            await self.creator.create_error_case(ctx, error)
            self.logger.error(error)


async def setup(bot):
    await bot.add_cog(Mod(bot))
