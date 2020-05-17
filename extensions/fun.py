import discord
from discord.ext import commands
import random
import settings
import requests

class Fun(commands.Cog):

    def __init__(self,client):
        self.client = client

    @commands.command()
    async def echo(self,ctx,message):
         await ctx.send(embed = discord.Embed(description="**{}**".format(message),color=settings.color))

    @commands.command()
    async def ama(self,ctx,question):
        responses = [
            'It is known.',
            'You are gay',
            'I have the high ground',
            'I am just a simple man trying to make my way through the universe',
            'I know da wae',
            'Small pp',
            'I am the senate',
            'Happy Landing',
            'Execute order 66',
            'Bingo, bango, bongo, bish, bash, bosh!',
            'rare golden kappa'
        ]
        await ctx.send(embed = discord.Embed(description=f'Question: {question}\nAnswer: {random.choice(responses)}',color=settings.color))#
    # @ama.error
    # async def ama_error(self,ctx,error):
    #     if isinstance(error, commands.MissingRequiredArgument):
    #         await ctx.send('Argument missing')

    @commands.command()
    async def dad_joke(self,ctx):
        r = requests.get("https://icanhazdadjoke.com/",headers={"Accept":"application/json"})
        data = r.json()
        await ctx.send(embed = discord.Embed(description=data['joke'],color=settings.color))

    @commands.command()
    async def star_wars(self,ctx):
         r = requests.get("http://swquotesapi.digitaljedi.dk/api/SWQuote/RandomStarWarsQuote")
         data = r.json()
         await ctx.send(embed = discord.Embed(description=data['starWarsQuote'],color=settings.color))

    @commands.command()
    async def meme(self,ctx):
         r = requests.get("https://meme-api.herokuapp.com/gimme")
         data = r.json()
         await ctx.send(data['url'])

def setup(client):
    client.add_cog(Fun(client))