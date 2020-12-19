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
        "Cleans given amount of messages(only for people who can delete messages)"
        if amount < 1:
            return await ctx.send(embed=discord.Embed(description="Amount of deleted messages must be greater than zero!", color=settings.error_color))
        amount = amount + 1 #+1 to delete clean message itselft too
        deleted = await ctx.channel.purge(limit=amount)
        await ctx.send(embed = discord.Embed(description='**Deleted {} message(s)**'.format(len(deleted)),color=settings.color))

@client.event
async def on_reaction_add(reaction,user):
    channel = reaction.message.channel
    await ctx.send_message(channel, '{} has reacted with {} to the message: {}'.format(user.name,reaction.emoji,reaction.message.content))


def setup(client):
    client.add_cog(Super(client))
