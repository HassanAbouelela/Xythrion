'''

+----[ Demonically ]----------------------------+
|                                               |
|  Copyright (c) 2019 Xithrius                  |
|  MIT license, Refer to LICENSE for more info  |
|                                               |
+-----------------------------------------------+

'''


# //////////////////////////////////////////////////////////////////////////// #
# Libraries
# /////////////////////////////////////////////////////////
# Built-in modules, third-party modules, custom modules
# //////////////////////////////////////////////////////////////////////////// #


import os
import asyncio

from discord.ext import commands as comms
from google.cloud import texttospeech  # ssml must be well-formed according to: https://www.w3.org/TR/speech-synthesis/
import discord

from containers.essentials.errors import error_prompt
from containers.essentials.pathing import path


# //////////////////////////////////////////////////////////////////////////// #
# Text to speech cog
# /////////////////////////////////////////////////////////
# A cog dedicated to text to speech
# //////////////////////////////////////////////////////////////////////////// #


class TextToSpeechCog(comms.Cog):

    # //////////////////////// # Object(s): bot
    def __init__(self, bot):
        self.bot = bot

    # Error handling for GOOGLE_APPLICATION_CREDENTIALS
    try:
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = path('configuration', 'google_service_token.json')
    except FileNotFoundError:
        error_prompt('Google service token is not found. Read the HELP file section to find solutions.')

# //////////////////////////////////////////////// # Commands
# //////////////////////// # Text to speech through the bot's mic
    @comms.command(name='tts')
    @comms.is_owner()
    async def google_text_to_speech(self, ctx):
        lock = asyncio.Lock()
        await lock.acquire()
        try:
            client = texttospeech.TextToSpeechClient()
            synthesis_input = texttospeech.types.SynthesisInput(text=(ctx.message.content)[5:])
            voice = texttospeech.types.VoiceSelectionParams(language_code='en-AU-Standard-D', ssml_gender=texttospeech.enums.SsmlVoiceGender.MALE)
            audio_config = texttospeech.types.AudioConfig(audio_encoding=texttospeech.enums.AudioEncoding.MP3)
            response = client.synthesize_speech(synthesis_input, voice, audio_config)
            with open(path('media', 'audio', 'output.mp3'), 'wb') as out:
                out.write(response.audio_content)
        finally:
            lock.release()

        vc = ctx.guild.voice_client
        if not vc:
            vc = await ctx.author.voice.channel.connect()
        vc.play(discord.FFmpegPCMAudio(path('media', 'audio', 'output.mp3')))
        print(f"TTS: {ctx.message.author} said {(ctx.message.content)[5:]}")


def setup(bot):
    bot.add_cog(TextToSpeechCog(bot))