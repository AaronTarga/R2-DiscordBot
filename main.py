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
async def load(ctx, extension):
    bot.load_extension(f'extensions.{extension}')

@bot.command()
async def unload(ctx, extension):
    bot.unload_extension(f'extensions.{extension}')

@bot.command(name="reload")
async def reloadSingle(ctx, extension):
    bot.unload_extension(f'extensions.{extension}')
    bot.load_extension(f'extensions.{extension}')

@bot.command(name="reload_all")
async def reloadAll(ctx):
    for fileName in os.listdir('./extensions'):
        if fileName.endswith('.py'):
            bot.unload_extension(f'extensions.{fileName[:-3]}')
            bot.load_extension(f'extensions.{fileName[:-3]}')

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