import serial
import asyncio
import discord
from discord.ext import commands


class Controller(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.baud_rate = 9600
        self.port = "COM5"

        self.dev = serial.Serial(
            bytesize=8,
            port=self.port,
            baudrate=self.baud_rate
        )
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

    @commands.has_role(926328786990034955)
    @commands.command(name="press")
    async def press(self, ctx, button: str):
        combo = self.parse_button_arg(button)
        if combo <= 0 or combo == 3075:
            return

        ins = [2, combo, 0]

        try:
            for i in ins:
                step = f"{i}+"
                self.dev.write(step.encode(encoding='ascii'))
            self.dev.write("?".encode(encoding='ascii'))
            self.dev.flush()
            await ctx.send(f"Command {button.capitalize()} completed")
        except serial.SerialException as e:
            print("Serial port already in use!")
            raise e

    @commands.has_role(926328786990034955)
    @commands.command(name="hold")
    async def hold(self, ctx, button: str, duration: int):
        if duration > 1000:
            return

        combo = self.parse_button_arg(button)
        if combo <= 0 or combo == 3075:
            return

        ins = [2, combo, duration]

        try:
            for i in ins:
                step = f"{i}+"
                self.dev.write(step.encode(encoding='ascii'))
            self.dev.write("?".encode(encoding='ascii'))
            self.dev.flush()
            await ctx.send(f"Command {button.capitalize()} completed")
        except serial.SerialException as e:
            print("Serial port already in use!")
            raise e

    @commands.has_role("Wow!")
    @commands.command(name="stopdev")
    async def stop(self, ctx):
        try:
            self.dev.close()
        except ValueError:
            await ctx.send("Device already disconnected!")

        if self.dev.closed:
            await ctx.send("Device disconnected.")

    @commands.has_role("Wow!")
    @commands.command(name="startdev")
    async def start(self, ctx):
        try:
            self.dev.open()
        except serial.SerialException as e:
            raise e

        await ctx.send("Device connected.")


async def setup(bot):
    await bot.add_cog(Controller(bot))
