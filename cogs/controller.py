import json

import discord.ext.commands
import serial
import logging

from discord.ext import commands
from utils.creator import Cases, GENERIC_PROCESS_ERROR, MISSING_USER_ARGUMENT, Flags

dev = serial.Serial()


class Controller(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.logger = logging.getLogger('rotom')

        with open("config.json", "r") as f:
            config = json.load(f)
            self.port = config["port"]
            self.baud_rate = config["baud_rate"]
            self.bytesize = config["bytesize"]
            self.player_role = config["role"]
            self.serverlog = config["serverlog"]

        self.creator = Cases(self.bot, self.serverlog)

        try:
            dev.bytesize = 8
            dev.port = self.port
            dev.baudrate = self.baud_rate
            dev.open()
            self.logger.info("Connection to serial port successful")
        except serial.SerialTimeoutException as e:
            self.logger.exception(f"Serial device timout occurred:\n{e}")
        except serial.SerialException as e:
            self.logger.exception(f"Unable to connect to serial device:\n{e}")

        self.button_bits = {
            "A": 0x1,
            "B": 0x2,
            "X": 0x4,
            "Y": 0x8,
            "LEFT": 0x10,
            "RIGHT": 0x20,
            "UP": 0x40,
            "DOWN": 0x80,
            "L": 0x100,
            "R": 0x200,
            "SELECT": 0x400,
            "START": 0x800,
        }

    def parse_button_arg(self, inpt: str):
        if inpt is None:
            return 0

        args = inpt.split("+")
        num = 0
        for arg in args:
            if arg.upper() in self.button_bits.keys():
                num += self.button_bits[arg.upper()]

        return num

    @commands.command(name="press")
    async def press(self, ctx, button: str):
        if ctx.author.get_role(self.player_role) not in ctx.author.roles:
            raise discord.ext.commands.MissingRole(ctx)

        combo = self.parse_button_arg(button)
        if combo <= 0 or combo == 3075:
            return

        ins = [2, combo, 0]

        try:
            for i in ins:
                step = f"{i}+"
                dev.write(step.encode(encoding='ascii'))
            dev.write("?".encode(encoding='ascii'))
            dev.flush()
            await ctx.send(f"Command {button.capitalize()} completed")
        except serial.SerialException as e:
            raise e

    @commands.command(name="hold")
    async def hold(self, ctx, button: str, duration: int):
        if ctx.author.get_role(self.player_role) not in ctx.author.roles:
            raise discord.ext.commands.MissingRole(ctx)

        if duration > 1000:
            return

        combo = self.parse_button_arg(button)
        if combo <= 0 or combo == 3075:
            return

        ins = [2, combo, duration]

        try:
            for i in ins:
                step = f"{i}+"
                dev.write(step.encode(encoding='ascii'))
            dev.write("?".encode(encoding='ascii'))
            dev.flush()
            await ctx.send(f"Command {button.capitalize()} completed")
        except serial.SerialException as e:
            raise e

    @commands.has_permissions(administrator=True)
    @commands.group()
    async def dev(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("You are missing a required argument")

    @dev.command(name="stop")
    async def stop(self, ctx):
        if not dev.is_open:
            await ctx.send("Device already disconnected!")
        else:
            try:
                dev.close()
                await ctx.send(
                    "Device disconnected on {} ({})"
                    .format(self.port, self.baud_rate)
                )
            except serial.SerialException as e:
                raise e

    @dev.command(name="start")
    async def start(self, ctx):
        if dev.is_open:
            await ctx.send("Device already connected!")
        else:
            try:
                dev.open()
                await ctx.send(
                    "Device connected on {} ({})"
                    .format(self.port, self.baud_rate)
                )
            except serial.SerialException as e:
                raise e

    @press.error
    @hold.error
    async def warn_handler(self, ctx, error):
        if isinstance(error, discord.ext.commands.MissingRole):
            await ctx.send("You are missing the required role to run this command.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(MISSING_USER_ARGUMENT)
        else:
            await self.creator.create_error_case(ctx, error)
            self.logger.error(error)


async def setup(bot):
    await bot.add_cog(Controller(bot))


# Make sure that mfer is closed
async def teardown(bot):
    dev.close()
