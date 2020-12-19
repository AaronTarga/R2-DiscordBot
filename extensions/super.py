import discord
from discord.ext import commands
import settings
import main

class Super(commands.Cog):

    def __init__(self,client):
        self.client = client

    def is_me(self,ctx,m):
        return m.author == self.client.user

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def clean(self,ctx,amount=5):
        "Cleans given amount of messages(only for people who can delete messages)"
        if amount < 1:
            return await ctx.send(embed=discord.Embed(description="Amount of deleted messages must be greater than zero!", color=settings.error_color))
        message = await ctx.send(embed = discord.Embed(description='Check if you want to delete {} message(s).'.format(amount),color=settings.color))
        await message.add_reaction('✅')
        amount = amount + 2 #+2 to delete clean message itself and confirm clean message
        main.delete_message_ids[message.id] = amount


def setup(client):
    client.add_cog(Super(client))
