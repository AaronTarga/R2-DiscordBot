import discord
import youtube_dl
import os
import asyncio
from discord.ext import commands
import glob
import settings

# Suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    # bind to ipv4 since ipv6 addresses cause issues sometimes
    'source_address': '0.0.0.0'
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

queue = []

global_volume = 0.5

class Music(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command(pass_context=True)
    async def join(self, ctx):
        """Joins a voice channel"""
        channel = ctx.message.author.voice.channel

        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)

        await channel.connect()

    @commands.command()
    async def volume(self, ctx, volume: int):
        """Changes the player's volume"""

        if ctx.voice_client is None:
            return await ctx.send(embed = discord.Embed(description="Not connected to a voice channel.",color=settings.error_color))

        ctx.voice_client.source.volume = volume / 100
        global global_volume
        global_volume = volume / 100
        await ctx.send(embed = discord.Embed(description="**Changed volume to {}%**".format(volume),color=settings.color))

    @commands.command(aliases=["leave"])
    async def stop(self, ctx):
        """Stops and disconnects the bot from voice"""

        await ctx.voice_client.disconnect()


    async def play_music(self, ctx, url=None):
        """Plays from a url (almost anything youtube_dl supports)"""

        await self.join(ctx)

        if url is None:
            if queue and len(queue) > 0:
                queue.pop(0)
            else:
                self.delete_music_files()
                return
        else:
            if queue and len(queue) > 0:
                queue.append(url)
                await ctx.send(embed = discord.Embed(description="Song got queued in {}. position".format(len(queue)-1), color = settings.color))
                return
            else:
                queue.append(url)

        await ctx.send(embed = discord.Embed(description="Loading songs from playlist into queue!", color = settings.color))
        data = ytdl.extract_info(queue[0], download=False)
        if 'entries' in data:
            queue.pop(0)
            #going through all songs in playlist and adding to queue
            for i,item in enumerate(data['entries']):
                queue.append(data['entries'][i]['webpage_url']  )
            await ctx.send(embed = discord.Embed(description=" Finished Loading songs into playlist:", color = settings.color))
        data = ytdl.extract_info(queue[0], download=True)
        filename = ytdl.prepare_filename(data)
        source = discord.PCMVolumeTransformer( discord.FFmpegPCMAudio(filename, **ffmpeg_options),volume = global_volume)
        ctx.voice_client.play(source,
        after=lambda e: print('Player error: %s' % e) if e else self.play_next(ctx))

        await ctx.send(embed = discord.Embed(title="**Now playing:**", description="[{}]({})\n\n  **Volume:** {}%".format(data.get('title'), queue[0], int(global_volume*100)), color = settings.color))

    @commands.command()
    async def play(self, ctx, url):
        await self.play_music(ctx,url)

    def play_next(self,ctx):
        asyncio.run_coroutine_threadsafe(self.play_music(ctx), self.client.loop)

    @commands.command()
    async def next(self,ctx):
       await ctx.voice_client.stop()

    @commands.command()
    async def queue(self,ctx):
        """lists current songs in queue"""
        if queue and len(queue) > 1:
            title = "**Songs currently in queue:**"
            queue_pretty = ""
            count = 0
            for url in queue:
                if(count > 0):
                    queue_pretty += f"**{count}:** {url}\n"
                count += 1
            await ctx.send(embed = discord.Embed(title=title,description=queue_pretty,color=settings.color))
        else:
            await ctx.send(embed = discord.Embed(description="**There are currently no songs in the queue!**",color=settings.color))

    @commands.command(aliases=["clear"])
    async def clear_queue(self,ctx):
        """clears queue"""
        global queue
        queue = []

        self.delete_music_files()

        await ctx.send(embed = discord.Embed(description="**Queue has been cleared!**",color=settings.color))
        if ctx.voice_client.is_playing():
            await ctx.voice_client.stop()

    def delete_music_files(self):
        files = glob.glob("*.webm")
        files.extend(glob.glob("*.mp3"))
        files.extend(glob.glob("*.m4a"))
        files.extend(glob.glob("*.ogg"))
        files.extend(glob.glob("*.m4p"))
        files.extend(glob.glob("*.wma"))
        files.extend(glob.glob("*.flac"))
        files.extend(glob.glob("*.mp4"))
        for f in files:
            os.remove(f)

    @commands.command(pass_context=True, no_pm=True)
    async def pause(self, ctx):
        """pauses currently played song"""
        if ctx.voice_client.is_playing():
            ctx.voice_client.pause()
        else:
            await ctx.send(embed = discord.Embed(description="**Player paused already**",color=settings.error_color))

    @commands.command(pass_context=True, no_pm=True)
    async def resume(self, ctx):
        """resumes currently played song"""
        if not ctx.voice_client.is_playing():
            ctx.voice_client.resume()
        else:
            await ctx.send(embed = discord.Embed(description="**Player is running already**",color=settings.error_color))

class R2D2(commands.Cog):
    def __init__(self, client):
        self.client = client

    async def join(self, ctx):
        channel = ctx.message.author.voice.channel

        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)

        await channel.connect()

    @commands.command(pass_context=True)
    async def r2_scream(self, ctx):
        """Maken yousa comfortable"""

        await self.join(ctx)

        dirname = os.path.dirname(__file__)
        filename = os.path.join(dirname, "../Sounds/R2 screaming.mp3")
        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(filename),volume = global_volume)
        ctx.voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else None)

    @commands.command(pass_context=True)
    async def r2_concerned(self, ctx):
        """Mesa concerned"""

        await self.join(ctx)

        dirname = os.path.dirname(__file__)
        filename = os.path.join(dirname, "../Sounds/Concerned R2D2.mp3")
        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(filename),volume = global_volume)
        ctx.voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else None)

    @commands.command(pass_context=True)
    async def r2_excited(self, ctx):
        """Gets yousa goen"""

        await self.join(ctx)

        dirname = os.path.dirname(__file__)
        filename = os.path.join(dirname, "../Sounds/Excited R2D2.mp3")
        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(filename),volume = global_volume)
        ctx.voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else None)

    @commands.command(pass_context=True)
    async def r2_laughing(self, ctx):
        """**Menacingly laughs**"""

        await self.join(ctx)

        dirname = os.path.dirname(__file__)
        filename = os.path.join(dirname, "../Sounds/Laughing R2D2.mp3")
        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(filename),volume = global_volume)
        ctx.voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else None)

    @commands.command(pass_context=True)
    async def r2_sad(self, ctx):
        """Gives yousa depression """

        await self.join(ctx)

        dirname = os.path.dirname(__file__)
        filename = os.path.join(dirname, "../Sounds/Sad R2D2.mp3")
        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(filename),volume = global_volume)
        ctx.voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else None)

    @commands.command(pass_context=True)
    async def r2_real_exciting(self, ctx):
        """Mesa really excited"""
        dirname = os.path.dirname(__file__)
        filename = os.path.join(dirname, "../Sounds/Very Excited R2D2.mp3")
        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(filename),volume = global_volume)
        ctx.voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else None)



def setup(client):
    client.add_cog(Music(client))
    client.add_cog(R2D2(client))
