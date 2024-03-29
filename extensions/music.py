import discord
import os
import asyncio
from discord.ext import commands
import glob
import settings
import signal
import time
from collections import defaultdict
import re
import youtube_dl


# Suppress noise about console usage from errors
# youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'noplaylist': True,
    'default_search': 'auto',
    # bind to ipv4 since ipv6 addresses cause issues sometimes
    # 'source_address': '0.0.0.0'
}

ffmpeg_options = {
    'before_options': '-nostdin',
    'options': '-vn'
}

ytdl = None

# using defaultdicts in order to make a list for each server where server id is the key
queues = defaultdict(list)
song_titles = defaultdict(list)

global_volume = defaultdict(lambda: 0.5)

timeout = 120


async def join_channel(ctx):
    if ctx.message.author.voice:
        channel = ctx.message.author.voice.channel

        if ctx.voice_client != None:
            return await ctx.voice_client.move_to(channel)

        await channel.connect()
    else:
        raise Exception


async def stop(ctx):
    if ctx.voice_client is None:
        return await ctx.send(embed=discord.Embed(description="Must join channel to be able to leave channel", color=settings.error_color))

    if queues[ctx.guild.id] and len(queues[ctx.guild.id]) > 0:
        await Music.clear(ctx)

    await ctx.voice_client.disconnect()


async def resume_prev(ctx, backup):
    await asyncio.sleep(5)
    if backup:
        ctx.voice_client.play(discord.PCMVolumeTransformer(backup),
                              after=lambda e: print('Player error: %s' % e) if e else Music.play_next(ctx))
    else:
        await ctx.voice_client.disconnect()


async def playing_sound(ctx, filename):
    backup = None
    if ctx.voice_client and ctx.voice_client.is_playing():
        backup = ctx.voice_client.source
        ctx.voice_client.pause()
    else:
        try:
            await join_channel(ctx)
        except:
            return await ctx.send(embed=discord.Embed(description="Must be in voice channel to play music.", color=settings.error_color))

    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, filename)
    source = discord.PCMVolumeTransformer(
        discord.FFmpegPCMAudio(filename), volume=global_volume[ctx.guild.id])

    ctx.voice_client.play(source,
                          after=lambda e: print('Player error: %s' % e) if e else None)

    await resume_prev(ctx, backup)


class Music(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command(pass_context=True)
    async def join(self, ctx):
        """Joins a voice channel"""
        await join_channel(ctx)

    @commands.command()
    async def volume(self, ctx, volume: int):
        """Changes the player's volume"""

        if volume > 100 or volume < 0:
            return await ctx.send(embed=discord.Embed(description="Volume can only be set between 0 and 100", color=settings.error_color))

        if ctx.voice_client is not None and ctx.voice_client.source is not None:
            ctx.voice_client.source.volume = float(volume) / 100.0

        global global_volume
        global_volume[ctx.guild.id] = float(volume) / 100.0
        await ctx.send(embed=discord.Embed(description="**Changed volume to {}%**".format(volume), color=settings.color))

    @staticmethod
    async def sleep_stop(ctx):
        await asyncio.sleep(timeout)
        if not queues[ctx.guild.id] or len(queues[ctx.guild.id]) < 1:
            if ctx.voice_client != None:
                await stop(ctx)

    @commands.command(aliases=["leave"])
    async def stop(self, ctx):
        """Stops and disconnects the bot from voice"""
        await stop(ctx)

    @staticmethod
    def music_not_found_handler(signum, frame):
        print("Timeout has been reached")
        raise Exception("end of time")

    @staticmethod
    async def append_song(ctx, appended=False):
        # could take long if it has to load big playlists
        await ctx.send(embed=discord.Embed(description="Loading song/songs from url!", color=settings.color))
        index = 0
        if queues[ctx.guild.id] and len(queues[ctx.guild.id]) > 1:
            index = len(queues[ctx.guild.id]) - 1

        # if it isn't finished until 20 seconds it gets interrupted
        signal.signal(signal.SIGALRM, Music.music_not_found_handler)
        signal.alarm(timeout)

        try:
            data = ytdl.extract_info(
                queues[ctx.guild.id][index], download=False)
        except Exception:
            await ctx.send(embed=discord.Embed(description=" Couldn't retrieve song data", color=settings.error_color))
            if queues[ctx.guild.id]:
                queues[ctx.guild.id].pop(index)
            signal.alarm(0)
            return

        # cancel interrupt
        signal.alarm(0)
        if queues[ctx.guild.id]:
            if 'entries' in data:
                queues[ctx.guild.id].pop(index)
                # going through all songs in playlist and adding to queue
                for i, item in enumerate(data['entries']):
                    queues[ctx.guild.id].append(
                        data['entries'][i]['webpage_url'])
                    song_titles[ctx.guild.id].append(
                        data['entries'][i]['title'])
                await ctx.send(embed=discord.Embed(description=" Finished Loading songs into playlist:", color=settings.color))
                await Music.print_queue(ctx)
            else:
                title = data.get('title')
                for bad in settings.bad_music:
                    # if music title conatins filter word, troll message gets played and afterwards music continues
                    if re.match(f".*{bad}.*", title, re.IGNORECASE):
                        queues[ctx.guild.id].pop(len(queues[ctx.guild.id])-1)

                        await Music.play_random(ctx)
                        return
                song_titles[ctx.guild.id].append(title)
                if len(queues[ctx.guild.id]) > 1 and appended:
                    await ctx.send(embed=discord.Embed(description="Song [{}]({}) got queued in {}. position".format(title, queues[ctx.guild.id][len(queues[ctx.guild.id])-1], len(queues[ctx.guild.id])-1), color=settings.color))

    @staticmethod
    async def play_music(ctx, url=None):
        if url is None:
            if queues[ctx.guild.id] and len(queues[ctx.guild.id]) > 1:
                queues[ctx.guild.id].pop(0)
                song_titles[ctx.guild.id].pop(0)
            else:
                if queues[ctx.guild.id]:
                    queues[ctx.guild.id].pop(0)
                    song_titles[ctx.guild.id].pop(0)
                await ctx.send(embed=discord.Embed(description="There are no more songs to be played!", color=settings.color))
                await Music.sleep_stop(ctx)
                return
        else:
            if queues[ctx.guild.id]:
                queues[ctx.guild.id].append(url)
                await Music.append_song(ctx, True)
                return
            else:
                queues[ctx.guild.id] = []
                queues[ctx.guild.id].append(url)
                await Music.append_song(ctx)
        if queues[ctx.guild.id]:

            video_data = ytdl.extract_info(queues[ctx.guild.id][0],download=False)

            source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(
                video_data['url'], **ffmpeg_options), volume=global_volume[ctx.guild.id])
            ctx.voice_client.play(source,
                                  after=lambda e: print('Player error: %s' % e) if e else Music.play_next(ctx))

            await ctx.send(embed=discord.Embed(title="**Now playing:**", description="[{}]({})\n\n  **Volume:** {}%".format(video_data.get('title'), queues[ctx.guild.id][0], int(global_volume[ctx.guild.id]*100)), color=settings.color))

    @commands.command()
    async def play(self, ctx, url):
        """Plays music from a youtube url using youtube_dl"""
        try:
            await join_channel(ctx)
        except:
            return await ctx.send(embed=discord.Embed(description="Must be in voice channel to play music.", color=settings.error_color))

        global ytdl
        ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

        asyncio.run_coroutine_threadsafe(
            Music.play_music(ctx, url), ctx.voice_client.loop)

    @staticmethod
    def play_next(ctx):
        if ctx.voice_client:
            asyncio.run_coroutine_threadsafe(
                Music.play_music(ctx), ctx.voice_client.loop)

    @commands.command()
    async def skip(self, ctx, count: int = 1):
        """Let's you skip a specific number of songs"""
        if ctx.voice_client is None or not ctx.voice_client.is_playing():
            return await ctx.send(embed=discord.Embed(description="No song to skip", color=settings.error_color))

        if(count > 0 and queues[ctx.guild.id] and count < len(queues[ctx.guild.id])):
            '''
            range starts from 1 because current song already out of queue so if only 1 gets skipped player just needs to be stopped
            and then it will execute it's after function which causes the next song in the queue to play
            '''
            for i in range(1, count):
                queues[ctx.guild.id].pop(0)
                song_titles[ctx.guild.id].pop(0)

            # ctx.voice_client.source = discord.FFmpegPCMAudio(queues[ctx.guild.id][0], **ffmpeg_options)
            ctx.voice_client.stop()
        else:
            if queues[ctx.guild.id] and len(queues[ctx.guild.id]) > 1:
                await ctx.send(embed=discord.Embed(description="You can only skip positive numbers and to songs in the queue, not greater or smaller numbers!", color=settings.error_color))
            else:
                if ctx.voice_client.is_playing():
                    ctx.voice_client.stop()
                else:
                    await ctx.send(embed=discord.Embed(description="There are no songs to skip!", color=settings.error_color))

    @commands.command()
    async def current(self, ctx):
        """Gives info about the current song"""

        if ctx.voice_client is None or not ctx.voice_client.is_playing():
            return await ctx.send(embed=discord.Embed(description="Not connected to a voice channel.", color=settings.error_color))

        if song_titles[ctx.guild.id]:
            await ctx.send(embed=discord.Embed(title="**Currently playing:**", description="[{}]({})\n\n  **Volume:** {}%".format(song_titles[ctx.guild.id][0], queues[ctx.guild.id][0], int(global_volume[ctx.guild.id]*100)), color=settings.color))
        else:
            await ctx.send(embed=discord.Embed(description="Currrently no song is playing", color=settings.error_color))

    @commands.command()
    async def queue(self, ctx):
        """lists current songs in queue"""

        await self.print_queue(ctx)

    @staticmethod
    async def print_queue(ctx):
        if queues[ctx.guild.id] and len(song_titles[ctx.guild.id]) > 1:
            title = "**Songs currently in queue:**"
            queue_pretty = ""
            count = 0
            for i in range(0, len(queues[ctx.guild.id])):
                if(count > 0):
                    queue_pretty += f"**{count}:** [{song_titles[ctx.guild.id][i]}]({queues[ctx.guild.id][i]})\n"
                count += 1
            await ctx.send(embed=discord.Embed(title=title, description=queue_pretty, color=settings.color))
        else:
            await ctx.send(embed=discord.Embed(description="**There are currently no songs in the queue!**", color=settings.color))

    @commands.command(aliases=["clear"])
    async def clear_queue(self, ctx):
        """clears queue"""
        await Music.clear(ctx)
        if ctx.voice_client is not None and ctx.voice_client.is_playing():
            ctx.voice_client.stop()

    @staticmethod
    async def clear(ctx):
        global queues
        global song_titles

        queues[ctx.guild.id] = []
        song_titles[ctx.guild.id] = []


        await ctx.send(embed=discord.Embed(description="**Queue has been cleared!**", color=settings.color))

    @staticmethod
    def delete_music_files():
        files = glob.glob("*.webm")
        files = glob.glob("*.webm")
        files.extend(glob.glob("*.mp3"))
        files.extend(glob.glob("*.m4a"))
        files.extend(glob.glob("*.ogg"))
        files.extend(glob.glob("*.m4p"))
        files.extend(glob.glob("*.wma"))
        files.extend(glob.glob("*.flac"))
        files.extend(glob.glob("*.mp4"))
        files.extend(glob.glob("*.wav"))
        for f in files:
            os.remove(f)

    @commands.command(pass_context=True, no_pm=True)
    async def pause(self, ctx):
        """pauses currently played song"""

        if ctx.voice_client is None:
            return await ctx.send(embed=discord.Embed(description="Bot is not connected to voice channel", color=settings.error_color))

        if ctx.voice_client.is_playing():
            ctx.voice_client.pause()
        else:
            await ctx.send(embed=discord.Embed(description="**Player paused already**", color=settings.error_color))

    @commands.command(pass_context=True, no_pm=True)
    async def resume(self, ctx):
        """resumes currently played song"""

        if ctx.voice_client is None:
            return await ctx.send(embed=discord.Embed(description="Bot is not connected to voice channel", color=settings.error_color))

        if not ctx.voice_client.is_playing():
            ctx.voice_client.resume()
        else:
            await ctx.send(embed=discord.Embed(description="**Player is running already**", color=settings.error_color))

    @staticmethod
    async def play_random(ctx):

        filename = "../Sounds/ask_again.mp3"

        await playing_sound(ctx, filename)


class R2D2(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(pass_context=True)
    async def r2_scream(self, ctx):
        """Maken yousa comfortable"""

        await playing_sound(ctx, "../Sounds/R2 screaming.mp3")

    @commands.command(pass_context=True)
    async def r2_concerned(self, ctx):
        """Mesa concerned"""

        await playing_sound(ctx, "../Sounds/Concerned R2D2.mp3")

    @commands.command(pass_context=True)
    async def r2_excited(self, ctx):
        """Gets yousa goen"""

        await playing_sound(ctx, "../Sounds/Excited R2D2.mp3")

    @commands.command(pass_context=True)
    async def r2_laughing(self, ctx):
        """**Menacingly laughs**"""

        await playing_sound(ctx, "../Sounds/Laughing R2D2.mp3")

    @commands.command(pass_context=True)
    async def r2_sad(self, ctx):
        """Gives yousa depression """

        await playing_sound(ctx, "../Sounds/Sad R2D2.mp3")

    @commands.command(pass_context=True)
    async def r2_real_exciting(self, ctx):
        """Mesa really excited"""

        await playing_sound(ctx, "../Sounds/Very Excited R2D2.mp3")


def setup(client):
    client.add_cog(Music(client))
    client.add_cog(R2D2(client))
