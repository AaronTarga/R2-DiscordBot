import discord
from discord.ext import commands
import settings
import re
import asyncio
timeout = 10

class Manage(commands.Cog):

    def __init__(self,client):
        self.client = client

    @staticmethod
    async def get_user_object(ctx,user_id):
        pattern = "<@!(\d*)"
        result = re.search(pattern,user_id)
        if result == None:
             await ctx.send(embed = discord.Embed(description="Could not find user!",color=settings.error_color))
        id = int(result.group(1))
        return await ctx.guild.fetch_member(id)

    @commands.command()
    async def user_roles(self,ctx,user_id):
        """Lists roles of a user."""
        member = await Manage.get_user_object(ctx,user_id)
        if member == None:
            return

        await ctx.send(embed = discord.Embed(description="**{}**".format(member.roles),color=settings.color))

    @commands.command()
    async def user_since(self,ctx,user_id):
        """Get date when user joined the server."""
        member = await Manage.get_user_object(ctx,user_id)
        if member == None:
            return

        await ctx.send(embed = discord.Embed(description="**{}**".format(member.created_at),color=settings.color))

    @commands.command()
    async def user_avatar(self,ctx,user_id):
        """Get url of the avatar of a user."""
        member = await Manage.get_user_object(ctx,user_id)
        if member == None:
            return

        await ctx.send(embed = discord.Embed(description="**{}**".format(member.avatar_url),color=settings.color))

    @commands.command()
    @commands.has_role("Owner")
    async def fullmute(self,ctx,user_id):
        """Mutes and deafens user!"""
        member = await Manage.get_user_object(ctx,user_id)
        if member == None:
            return

        await member.edit(mute=True,deafen=True)
        await ctx.send(embed = discord.Embed(description="**{} has been given a fullmute!**".format(member),color=settings.color))
        await asyncio.sleep(timeout)
        await member.edit(mute=False,deafen=False)

    @commands.command()
    @commands.has_role("Owner")
    async def mute(self,ctx,user_id):
        """Mutes user!"""
        member = await Manage.get_user_object(ctx,user_id)
        if member == None:
            return

        await member.edit(mute=True,deafen=False)
        await ctx.send(embed = discord.Embed(description="**{} has been given a mute!**".format(member),color=settings.color))
        await asyncio.sleep(timeout)
        await member.edit(mute=False,deafen=False)


def setup(client):
    client.add_cog(Manage(client))