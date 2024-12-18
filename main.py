import os
import sys
import json
import discord
import asyncio
import logging

from discord.ext import commands
from os.path import isfile, join


def init_logs() -> logging.Logger:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )
    return logging.getLogger('rotom')


def init_bot(logger) -> commands.Bot | None:
    intents = discord.Intents.all()
    intents.members = True
    try:
        with open("config.json") as c:
            config = json.load(c)

            return commands.Bot(
                command_prefix=config['prefix'],
                description="Rotom",
                intents=intents,
                token=config['token']
            )
    except FileNotFoundError:
        logger.critical("No config file found. Please makes sure 'config.json' is in your active directory")
        sys.exit(-1)


def list_cogs() -> list[str]:
    return ["cogs." + f.replace('.py', '') for f in os.listdir('cogs') if isfile(join('cogs', f))]


async def main() -> None:
    logger = init_logs()
    bot = init_bot(logger)
    async with bot:
        for cog in list_cogs():
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

        try:
            with open("config.json") as c:
                config = json.load(c)
        except Exception as e:
            logger.exception("Unable to read bot token!\n{}".format(e))

        await bot.start(config['token'])


if __name__ == '__main__':
    asyncio.run(main())
