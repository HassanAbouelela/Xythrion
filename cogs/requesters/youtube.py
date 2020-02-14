"""
> Xythrion
> Copyright (c) 2020 Xithrius
> MIT license, Refer to LICENSE for more info
"""


import asyncio
import youtube_dl

from discord.ext import commands as comms
import discord


# Suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ''

info = {
 "ytdlopts": {
    "format": "bestaudio/best",
    "restrictfilenames": True,
    "noplaylist": True,
    "nocheckcertificate": True,
    "ignoreerrors": True,
    "logtostderr": False,
    "quiet": True,
    "panic": False,
    "fatal": False,
    "error": False,
    "no_warnings": True,
    "default_search": "auto",
    "source_address": "0.0.0.0"
 },
 "ffmpeg_options": {
    "options": "-vn -reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
 }
}
ytdl_format_options = info['ytdlopts']
ffmpeg_options = info['ffmpeg_options']
ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class YTDLSource(discord.PCMVolumeTransformer):
    """Creating player to stream audio from YouTube through bot's mic."""

    def __init__(self, source, *, data, volume=0.3):

        #: Subclassing the transformer for streaming.
        super().__init__(source, volume)

        #: YouTube video JSON data as python dictionary
        self.data = data

        #: Getting video information from extracted data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None):
        """Setting up player and data from Youtube url.
        
        Args:
            url (str): YouTube video url
            loop (bool): The bot's asyncio loop
        
        """
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url,
                                          download=False))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        #: Returning the source for the player
        return cls(discord.FFmpegPCMAudio(source=data['url'],
                   before_options=ffmpeg_options['options']), data=data)


class Youtube(comms.Cog):
    """Cog for commands dealing with the YTDLSource subclass."""

    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        """Checks user permissions from config file.
        
        Args:
            ctx: Context object where the command is called.
        
        Returns:
            True if user has permissions, False otherwise.

        """
        return await self.bot.is_owner(ctx.author)

    @comms.command()
    async def play(self, ctx, url):
        """Plays music from YouTube url

        Args:
            ctx: Context object where the command is called.

        """
        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop)
            ctx.voice_client.play(player,
                                  after=lambda e: print(f'Player error: {e}')
                                  if e else None)
        await ctx.send(f'Now playing: {player.title}')

    @comms.command()
    async def volume(self, ctx, volume: int):
        """Adjusting audio stream volume
        
        Args:
            volume (int): % volume that bot is to be set at

        """
        ctx.voice_client.source.volume = volume / 100
        await ctx.send(f"Changed volume to {volume}%")

    @comms.command()
    async def leave(self, ctx):
        """Leaves voice channel, if the bot is even in one."""
        await ctx.voice_client.disconnect()

    @comms.command()
    async def pause(self, ctx):
        """Pauses possible audio stream."""
        ctx.guild.voice_client.pause()

    @comms.command()
    async def resume(self, ctx):
        """Resumes possible audio stream."""
        ctx.guild.voice_client.resume()

    @comms.command()
    async def stop(self, ctx):
        """Stops the current audio stream."""
        ctx.voice_client.stop()

    @comms.command(name='join')
    async def _join(self, ctx):
        """Joins the channel the caller is currently in."""
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send(
                    f'{ctx.message.author.mention} is not in a voice chat')
        else:
            await ctx.voice_client.disconnect()
            await ctx.author.voice.channel.connect()

    @play.before_invoke
    async def ensure_voice(self, ctx):
        """Makes sure the player is ready before connecting to the voice channel."""
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send(f'{ctx.message.author.mention} is not in a voice chat.')
        elif ctx.voice_client.is_playing():
            await ctx.send(f"Prioritizing {ctx.message.author.mention}'s request.")
            ctx.voice_client.stop()

    @volume.before_invoke
    @leave.before_invoke
    @pause.before_invoke
    @resume.before_invoke
    async def ensure_voice_modifier(self, ctx):
        """Checking if the voice client is connected.
        
        Returns:
            A bot that is now in the voice channel that the caller is in.
        
        """
        if ctx.voice_client is None:
            await ctx.send(f'Cannot preform command {ctx.command.name}.')


def setup(bot):
    bot.add_cog(Youtube(bot))