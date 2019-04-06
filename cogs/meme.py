'''

+----[ Demonically ]----------------------------+
|                                               |
|  Copyright (c) 2019 Xithrius                  |
|  MIT license, Refer to LICENSE for more info  |
|                                               |
+-----------------------------------------------+

'''


# ///////////////////////////////////////////////////////// #
# Libraries
# ////////////////////////
# Built-in modules
# Third-party modules
# Custom modules
# ///////////////////////////////////////////////////////// #


# import json

from discord.ext import commands as comms

# from essentials.pathing import path, mkdir
# from essentials.errors import error_prompt, input_loop
# from essentials.welcome import welcome_prompt


# ///////////////////////////////////////////////////////// #
# Meme cog
# ////////////////////////
# Getting user-provided objects
# Also returning said objects
# ///////////////////////////////////////////////////////// #


class MemeCog(comms.Cog):

    def __init__(self, bot):
        self.bot = bot

    @comms.command(name='poem')
    async def poem(self, ctx, string):
        pass


def setup(bot):
    bot.add_cog(MemeCog(bot))
