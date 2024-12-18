import asyncio
import discord
import json
import logging
import os
import sys

from discord.ext import commands
from os.path import isfile, join


def init_logs() -> logging.Logger:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )
    return logging.getLogger('rotom')


def read_config(logger: logging.Logger) -> dict | None:
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
            return dict(
                token=config['token'],
                prefix=config['prefix'],
                status=config['status'],
            )
    except FileNotFoundError:
        logger.critical(
            "No config file found. "
            "Please makes sure 'config.json' is in your active directory"
        )
        sys.exit(-1)


def init_bot(config: dict) -> commands.Bot:
    intents = discord.Intents.all()
    intents.members = True
    return commands.Bot(
        description='Rotom',
        command_prefix=config['prefix'],
        activity=discord.Game(name=config['status']),
        intents=intents
    )


async def main() -> None:
    logger = init_logs()
    config = read_config(logger)
    bot = init_bot(config)
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


if __name__ == '__main__':
    asyncio.run(main())
