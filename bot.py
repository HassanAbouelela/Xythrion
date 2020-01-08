"""
> Xythrion
> Copyright (c) 2020 Xithrius
> MIT license, Refer to LICENSE for more info

The main file for the graphing bot.

Running the bot (python 3.8+):
    
    Installing requirements:
        $ python -m pip install --user -r requirements.txt

        Go to https://miktex.org/download and pick the item for your OS (200mb+).

    Starting the bot:
        Without logging:
            $ python bot.py

        with logging (log should show up in /tmp/discord.log):
            $ python bot.py log
"""


import json
import os
import traceback
import logging
import sys
import asyncio

from discord.ext import commands as comms
import discord

from modules.output import path, sp, get_extensions


def _logger():
    logger = logging.getLogger('discord')
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler(filename=path('tmp', 'discord.log'), encoding='utf-8', mode='w')
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(handler)


def cleanup():
    for item in os.listdir(path('tmp')):
        if item[-4:] != '.log':
            os.remove(path('tmp', item))


class Xythrion(comms.Bot):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Open config
        try:
            with open(path('config.json')) as f:
                self.token = json.load(f)['discord']
        except (FileNotFoundError, IndexError):
            sp.f('Config could not be found or read properly.')

        # Create asyncio loop
        self.loop = asyncio.get_event_loop()

        # Creating objects before loading cogs
        self.create_items()
        # self.create_courtines()

        self.add_cog(Main_Cog(self))

        for cog in get_extensions():
            self.load_extension(cog)

    def create_items(self):
        try:
            os.mkdir(path('tmp'))
        except FileExistsError:
            pass

    def create_courtines(self):
        future = asyncio.gather()
        # self.loop.create_task(func)
        self.loop.run_until_complete(future)

    async def on_ready(self):
        await self.change_presence(status=discord.ActivityType.playing, activity=discord.Game('with graphs'))
        sp.r('Awaiting...')

    #async def close(self):
    #    await super().close()


class Main_Cog(comms.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        return await self.bot.is_owner(ctx.author)

    @comms.command(aliases=['refresh', 'r'])
    async def reload(self, ctx):
        for cog in get_extensions():
            try:
                self.bot.unload_extension(cog)
                self.bot.load_extension(cog)
            except discord.ext.commands.ExtensionNotLoaded:
                self.bot.load_extension(cog)
            except Exception as e:
                sp.f(f'Loading {cog} error:')
                traceback.print_exception(type(e), e, e.__traceback__, file=sys.stderr)
        await ctx.send('Reloaded extensions.', delete_after=5)

    @comms.command(aliases=['logout'])
    async def exit(self, ctx):
        sp.c('Logging out...')
        await ctx.bot.logout()


if __name__ == "__main__":
    # Starting the logger, if requested from the command line.
    try:
        if sys.argv[1] == 'log':
            _logger()
    except IndexError:
        pass

    # Creating the bot object
    bot = Xythrion(command_prefix=comms.when_mentioned_or(';'),
                   case_insensitive=True)
    # Running the bot
    bot.run(bot.token, bot=True, reconnect=True)

    # Cleaning up the tmp directory
    cleanup()
