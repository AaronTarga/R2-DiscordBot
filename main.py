import discord
from discord.ext import commands
import random
import os
import sys
import settings

intents = discord.Intents.default()
intents.message_content = True


class R2Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=';', intents=intents)
        self.delete_message_ids: dict[int, int] = {}


bot = R2Bot()

@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.idle, activity=discord.Game('Hello, there!'))
    print('Bot is ready')

@bot.command()
@commands.has_permissions(administrator=True)
async def load(ctx, extension):
    """Loads given extension(only for admins)"""
    bot.load_extension(f'extensions.{extension}')
    await ctx.send(embed = discord.Embed(description='Extension has been loaded!',color=settings.color))

@bot.command()
@commands.has_permissions(administrator=True)
async def unload(ctx, extension):
    """Temporarly disables given extension(only for admins)"""
    bot.unload_extension(f'extensions.{extension}')
    await ctx.send(embed = discord.Embed(description='Extension has been disabled!',color=settings.color))

@bot.command(name="reload")
@commands.has_permissions(administrator=True)
async def reloadSingle(ctx, extension):
    """Reloads given extension(only for admins)"""
    bot.unload_extension(f'extensions.{extension}')
    bot.load_extension(f'extensions.{extension}')
    await ctx.send(embed = discord.Embed(description='Extension has been reloaded!',color=settings.color))

@bot.command(name="reload_all")
@commands.has_permissions(administrator=True)
async def reloadAll(ctx):
    """Reloads all extensions(only for admins)"""
    for fileName in sorted(os.listdir('./extensions')):
        if fileName.endswith('.py'):
            bot.unload_extension(f'extensions.{fileName[:-3]}')
            bot.load_extension(f'extensions.{fileName[:-3]}')
    await ctx.send(embed = discord.Embed(description='Extensions have been reloaded!',color=settings.color))

@bot.command(name="server")
async def getServer(ctx):
    """Prints the name of the server"""
    await ctx.send(embed = discord.Embed(description=f'Name of the server: {ctx.guild}',color=settings.color))

@bot.command(name="server_id")
async def getServerId(ctx):
    """Prints the id of the server"""
    await ctx.send(embed = discord.Embed(description=f'Id of the server: {ctx.guild.id}',color=settings.color))

@bot.event
async def on_command_error(ctx,error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(embed = discord.Embed(description="**Arguments missing**",color=settings.error_color))
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send(embed = discord.Embed(description="**Command not found plessen usen ;"
        "**",color=settings.error_color))
    elif isinstance(error, commands.MissingRole):
        await ctx.send(embed = discord.Embed(description="**You miss the role required for this command**",color=settings.error_color))
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send(embed = discord.Embed(description="**You don't have permissions to use this command**",color=settings.error_color))
    elif isinstance(error, commands.MissingAnyRole):
        await ctx.send(embed = discord.Embed(description="**You miss the role required for this command**",color=settings.error_color))
    elif isinstance(error, commands.BadArgument):
        await ctx.send(embed = discord.Embed(description="**Bad Argument given**",color=settings.error_color))
    else:
        print(error)


@bot.event
async def on_reaction_add(reaction,user):
    channel = reaction.message.channel
    message_id = reaction.message.id
    if reaction.emoji == '✅' and message_id in bot.delete_message_ids:
        if str(user) != 'R2D2#4772':
            deleted = await channel.purge(limit=bot.delete_message_ids[message_id])
            await channel.send(embed = discord.Embed(description='**Deleted {} message(s)**'.format(len(deleted) - 2),color=settings.color))
            bot.delete_message_ids.pop(message_id)

for fileName in sorted(os.listdir('./extensions')):
    if fileName.endswith('.py'):
        bot.load_extension(f'extensions.{fileName[:-3]}')

bot.run(settings.token)