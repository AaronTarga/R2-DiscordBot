import discord
from discord.ext import commands
import settings

class Super(commands.Cog):

    def __init__(self,client):
        self.client = client

    def is_me(self,ctx,m):
        return m.author == self.client.user

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def clean(self,ctx,amount=5):
       deleted = await ctx.channel.purge(limit=amount)
       await ctx.chanel.send(embed = discord.Embed(description="**Deleted {} message(s)**".format(len(deleted)),color=settings.color))

def setup(client):
    client.add_cog(Super(client))
