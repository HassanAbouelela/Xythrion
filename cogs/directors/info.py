"""
>> Xythrion
> Copyright (c) 2019 Xithrius
> MIT license, Refer to LICENSE for more info
"""


class Info_Director(comms.Cog):
    """Cog is meant to give information about owner and bot interactions."""

    def __init__(self, bot):

        #: Setting Robot(comms.Bot) as a class attribute
        self.bot = bot

    @comms.command()
    async def invite(self, ctx):
        """Gives the invite link of this bot. It is not 'essential', but it's still useful.
        
        Returns:
            The invite link so the bot can be invited to a server.
        
        """
        await ctx.send(f'https://discordapp.com/oauth2/authorize?client_id={self.bot.user.id}&scope=bot&permissions=32885952')

    @comms.command()
    async def about(self, ctx):
        """Returns information about this bot's origin
        
        Returns:
            An embed object with links to creator's information and bot's repository.
        
        """
        info = {
            'Twitter': 'https://twitter.com/_Xithrius',
            'Github': 'https://github.com/Xithrius/Xythrion'
        }
        em = discord.Embed(title='Project creation date: March 30, 2019', description='\n'.join(f'[`{k}`]({v})' for k, v in info.items()))
        await ctx.send(embed=em)

    @comms.command()
    async def website(self, ctx):
        """Returns website for the bot (this replaced the README).

        Returns:
            An embed object containing the website link for the bot.

        """
        em = discord.Embed(description='`https://xithrius.github.io/Xythrion/`')
        await ctx.send(embed=em)


def setup(bot):
    bot.add_cog(Info_Director(bot))