import discord
from discord.ext import commands
import random
import os
import sys
import settings

bot = commands.Bot(command_prefix=';')

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
    for fileName in os.listdir('./extensions'):
        if fileName.endswith('.py'):
            bot.unload_extension(f'extensions.{fileName[:-3]}')
            bot.load_extension(f'extensions.{fileName[:-3]}')
    await ctx.send(embed = discord.Embed(description='Extensions have been reloaded!',color=settings.color))

@bot.event
async def on_command_error(ctx,error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(embed = discord.Embed(description="**Arguments missing**",color=settings.error_color))
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send(embed = discord.Embed(description="**Command not found plessen usen ;help**",color=settings.error_color))
    else:
        print(error)


for fileName in os.listdir('./extensions'):
    if fileName.endswith('.py'):
        bot.load_extension(f'extensions.{fileName[:-3]}')

bot.run(settings.token)