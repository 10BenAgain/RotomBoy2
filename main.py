import os
import sys
import json
import discord
import asyncio
import logging

from discord.ext import commands
from os.path import isfile, join


def init_logs():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )
    return logging.getLogger('rotom')


if __name__ == '__main__':
    logger = init_logs()
    logger.info("Starting main bot loop")
    try:
        with open("config.json") as c:
            config = json.load(c)
            intents = discord.Intents.all()
            intents.members = True
            bot = commands.Bot(
                command_prefix=config['prefix'],
                description="Rotom",
                intents=intents
            )
    except FileNotFoundError:
        logger.critical("No config file found. Please makes sure 'config.json' is in your active directory")
        sys.exit(-1)


@bot.event
async def on_ready():
    login = f"Successfully logged in as {bot.user}"
    logger.info(login)
    await bot.change_presence(activity=discord.Game(name=config['status']))


async def main():
    async with bot:
        for cog in ["cogs." + f.replace('.py', '') for f in os.listdir('cogs') if isfile(join('cogs', f))]:
            try:
                await bot.load_extension(cog)
                logger.info(f"Cog {cog[5:]} was successfully loaded!")
            except Exception as e:
                logger.exception(f'Unable to load {cog}\n{e}')

        try:
            await bot.load_extension("utils.error_handler")
            logger.info("Error handler loaded")
        except Exception as e:
            logger.exception("Unable to load error handler\n{}".format(e))
        await bot.start(config['token'])


asyncio.run(main())
