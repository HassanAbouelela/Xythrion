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


import asyncio
import datetime
import json
import logging
import os
import sys
import traceback
import aiohttp
import asyncpg

import discord
from discord.ext import commands as comms
from hyper_status import Status

from modules import get_extensions, path


def _logger():
    """Logs information specifically for the discord package."""
    logger = logging.getLogger('discord')
    logger.setLevel(logging.DEBUG)
    if not os.path.isdir(path(f'tmp{os.sep}')):
        os.mkdir(path('tmp'))
    handler = logging.FileHandler(filename=path('tmp', 'discord.log'), encoding='utf-8', mode='w')
    handler.setFormatter(logging.Formatter('%(asctime)s  :  %(levelname)s  :  %(name)s  :  %(message)s'))
    logger.addHandler(handler)


def _cleanup():
    """Cleans up tmp/ after bot is logged out and shut down."""
    if os.path.isdir(path('tmp')):
        for item in os.listdir(path('tmp')):
            if item[-4:] != '.log':
                os.remove(path('tmp', item))


class Xythrion(comms.Bot):
    """The main class where all important attributes are set and tasks are ran."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Open config
        try:
            with open(path('config', 'config.json')) as f:
                self.config = json.load(f)
        except (FileNotFoundError, IndexError):
            Status('Config could not be found or read properly.', 'fail')

        # Create asyncio loop
        self.loop = asyncio.get_event_loop()
        self.loop.run_until_complete(self.create_courtines())

        # Add the main cog required for development and control.
        self.add_cog(Main_Cog(self))

        # Getting cogs ready to be laoded in.
        __cogs = get_extensions()

        # Attempt to set TTS environment. If there's a failiure, the TTS cog isn't loaded.
        try:
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = path('config', 'gsc.json')
        except FileNotFoundError:
            Status('Google Service Token .json file could not be found or opened. TTS is disabled.', 'fail')
            __cogs.remove('cogs.requesters.tts')

        # Loading the cogs in, one by one.
        for cog in __cogs:
            self.load_extension(cog)

    async def create_courtines(self):
        """Creates asynchronous database and session connection.
        
        Raises:
            Possible errors describing why connections could not be etablished.
        
        """
        try:
            self.pool = await asyncpg.create_pool(**self.config['db'], command_timeout=60)
            await self.check_database()
        except Exception as e:
            Status(f'Fatal error while creating connection to database: {e}', 'fail')

        self.session = aiohttp.ClientSession()

    async def check_database(self):
        """Checks if the database has the correct tables before starting the bot up."""
        async with self.pool.acquire() as conn:
            await conn.execute('''CREATE TABLE IF NOT EXISTS Messages(
                                    id serial PRIMARY KEY,
                                    identification BIGINT,
                                    message_date TIMESTAMP WITHOUT TIME ZONE NOT NULL
                                    )''')
            await conn.execute('''CREATE TABLE IF NOT EXISTS Runtime(
                                    id serial PRIMARY KEY,
                                    login TIMESTAMP WITHOUT TIME ZONE NOT NULL,
                                    logout TIMESTAMP WITHOUT TIME ZONE NOT NULL
                                    )''')

    async def on_ready(self):
        """Updates the bot status when logged in successfully."""
        self.startup_time = datetime.datetime.now()
        await self.change_presence(status=discord.ActivityType.playing, activity=discord.Game('with graphs'))
        Status('Awaiting...', 'ok')

    async def logout(self):
        """Subclassing the logout command to make sure connections are closed properly."""
        try:
            await self.session.close()
            await self.pool.close()
        except Exception:
            pass

        return await super().logout()


class Main_Cog(comms.Cog):
    """Cog required for development and control."""

    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        """Checks if user if owner.
        
        Returns:
            True or false based off of if user is an owner of the bot.
        
        """
        return await self.bot.is_owner(ctx.author)

    @comms.command(aliases=['refresh', 'r'])
    async def reload(self, ctx):
        """ """
        for cog in get_extensions():
            try:
                self.bot.unload_extension(cog)
                self.bot.load_extension(cog)
            except discord.ext.commands.ExtensionNotLoaded:
                self.bot.load_extension(cog)
            except Exception as e:
                Status(f'Loading {cog} error:', 'fail')
                traceback.print_exception(type(e), e, e.__traceback__, file=sys.stderr)
        await ctx.send('Reloaded extensions.', delete_after=5)

    @comms.command(aliases=['logout'])
    async def exit(self, ctx):
        """ """
        try:
            async with self.bot.pool.acquire() as conn:
                await conn.execute('''INSERT INTO Runtime(
                                    login, logout) VALUES($1, $2)''',
                                self.bot.startup_time, datetime.datetime.now())
        except AttributeError:
            pass
        Status('Logging out...', 'warn')
        await ctx.bot.logout()


if __name__ == "__main__":
    # Adding the temp folder if it doesn't exist.
    if not os.path.isdir(path('tmp')):
        os.mkdir(path('tmp'))

    # Starting the logger, if requested from the command line.
    try:
        if sys.argv[1] == 'log':
            _logger()
    except IndexError:
        pass

    # Creating the bot object
    bot = Xythrion(command_prefix=comms.when_mentioned_or(';'),
                   case_insensitive=True)
    # Checking important attribute before running
    # assert hasattr(bot, 'token'), 'Token '

    # Running the bot
    bot.run(bot.config['discord'], bot=True, reconnect=True)

    # Cleaning up the tmp directory
    _cleanup()
