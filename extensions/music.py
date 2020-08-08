import discord
import youtube_dl
import os
import asyncio
from discord.ext import commands
import glob
import settings
import signal
import time

# Suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options_playlist = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'flat-playlist': True,
    'default_search': 'auto',
    # bind to ipv4 since ipv6 addresses cause issues sometimes
    # 'source_address': '0.0.0.0'
}

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
    'options': '-vn'
}

ytdl = None

queue = []
song_titles = []

global_volume = 0.5

timeout = 60


class Music(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command(pass_context=True)
    async def join(self, ctx):
        """Joins a voice channel"""
        if ctx.message.author.voice:
            channel = ctx.message.author.voice.channel

            if ctx.voice_client != None:
                return await ctx.voice_client.move_to(channel)

            await channel.connect()
        else:
            raise Exception

    @commands.command()
    async def volume(self, ctx, volume: int):
        """Changes the player's volume"""

        if ctx.voice_client is not None:
            ctx.voice_client.source.volume = volume / 100

        global global_volume
        global_volume = volume / 100
        await ctx.send(embed=discord.Embed(description="**Changed volume to {}%**".format(volume), color=settings.color))

    async def sleep_stop(self, ctx):
        await asyncio.sleep(timeout)
        if not queue or len(queue) < 1:
            print("Bot inactive and no more songs to be played")
            if ctx.voice_client != None:
                await self.stop(ctx)

    @commands.command(aliases=["leave"])
    async def stop(self, ctx):
        """Stops and disconnects the bot from voice"""
        if ctx.voice_client is None:
            return await ctx.send(embed=discord.Embed(description="Must join channel to be able to leave channel", color=settings.error_color))

        if queue and len(queue) > 0:
            await self.clear(ctx)

        await ctx.voice_client.disconnect()

    def music_not_found_handler(self, signum, frame):
        print("Timeout has been reached")
        raise Exception("end of time")

    async def append_song(self, ctx, appended=False):
        # could take long if it has to load big playlists
        await ctx.send(embed=discord.Embed(description="Loading song/songs from url!", color=settings.color))
        index = 0
        if queue and len(queue) > 1:
            index = len(queue) - 1

        # if it isn't finished until 20 seconds it gets interrupted
        signal.signal(signal.SIGALRM, self.music_not_found_handler)
        signal.alarm(timeout)

        try:
            data = ytdl.extract_info(queue[index], download=False)
        except Exception:
            await ctx.send(embed=discord.Embed(description=" Couldn't retrieve song data", color=settings.error_color))
            if queue:
                queue.pop(index)
            signal.alarm(0)
            return
        # cancel interrupt
        signal.alarm(0)
        if queue:
            if 'entries' in data:
                queue.pop(index)
                # going through all songs in playlist and adding to queue
                for i, item in enumerate(data['entries']):
                    queue.append(data['entries'][i]['webpage_url'])
                    song_titles.append(data['entries'][i]['title'])
                await ctx.send(embed=discord.Embed(description=" Finished Loading songs into playlist:", color=settings.color))
                await self.print_queue(ctx)
            else:
                song_titles.append(data.get('title'))
                if len(queue) > 1 and appended:
                    await ctx.send(embed=discord.Embed(description="Song [{}]({}) got queued in {}. position".format(data.get('title'), queue[len(queue)-1], len(queue)-1), color=settings.color))

    async def play_music(self, ctx, url=None):

        if url is None:
            if queue and len(queue) > 1:
                queue.pop(0)
                song_titles.pop(0)
            else:
                if queue:
                    queue.pop(0)
                    song_titles.pop(0)
                await ctx.send(embed=discord.Embed(description="There are no more songs to be played!", color=settings.color))
                self.delete_music_files()
                await self.sleep_stop(ctx)
                return
        else:
            if queue:
                queue.append(url)
                await self.append_song(ctx, True)
                return
            else:
                queue.append(url)
                await self.append_song(ctx)
        if queue:
            data = ytdl.extract_info(queue[0], download=True)
            filename = ytdl.prepare_filename(data)
            source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(
                filename, **ffmpeg_options), volume=global_volume)
            ctx.voice_client.play(source,
                                  after=lambda e: print('Player error: %s' % e) if e else self.play_next(ctx))

            await ctx.send(embed=discord.Embed(title="**Now playing:**", description="[{}]({})\n\n  **Volume:** {}%".format(data.get('title'), queue[0], int(global_volume*100)), color=settings.color))

    @commands.command()
    async def play(self, ctx, url, playlist: int = 0):
        """Plays from a url (almost anything youtube_dl supports) when adding number greater 1 at end it queues playlists"""
        try:
            await self.join(ctx)
        except:
            return await ctx.send(embed=discord.Embed(description="Must be in voice channel to play music.", color=settings.error_color))

        global ytdl
        if playlist:
            ytdl = youtube_dl.YoutubeDL(ytdl_format_options_playlist)
        else:
            ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

        await self.play_music(ctx, url)

    def play_next(self, ctx):
        asyncio.run_coroutine_threadsafe(
            self.play_music(ctx), self.client.loop)

    @commands.command()
    async def skip(self, ctx, count: int = 1):
        """Let's you skip a specific number of songs"""
        if ctx.voice_client is None or not ctx.voice_client.is_playing():
            return await ctx.send(embed=discord.Embed(description="No song to skip", color=settings.error_color))

        if(count > 0 and queue and count < len(queue)):
            for i in range(1, count):
                queue.pop(0)
                song_titles.pop(0)
            await ctx.voice_client.stop()
        else:
            if queue and len(queue) > 1:
                await ctx.send(embed=discord.Embed(description="You can only skip positive numbers and to songs in the queue, not greater or smaller numbers!", color=settings.error_color))
            else:
                await ctx.send(embed=discord.Embed(description="There are no more songs in the queue!", color=settings.error_color))

    @commands.command()
    async def current(self, ctx):
        """Gives info about the current song"""

        if ctx.voice_client is None or not ctx.voice_client.is_playing():
            return await ctx.send(embed=discord.Embed(description="Not connected to a voice channel.", color=settings.error_color))

        if song_titles:
            await ctx.send(embed=discord.Embed(title="**Currently playing:**", description="[{}]({})\n\n  **Volume:** {}%".format(song_titles[0], queue[0], int(global_volume*100)), color=settings.color))
        else:
            await ctx.send(embed=discord.Embed(description="Currrently no song is playing", color=settings.error_color))

    @commands.command()
    async def queue(self, ctx):
        """lists current songs in queue"""

        await self.print_queue(ctx)

    async def print_queue(self, ctx):
        if queue and len(song_titles) > 1:
            title = "**Songs currently in queue:**"
            queue_pretty = ""
            count = 0
            for i in range(0, len(queue)):
                if(count > 0):
                    queue_pretty += f"**{count}:** [{song_titles[i]}]({queue[i]})\n"
                count += 1
            await ctx.send(embed=discord.Embed(title=title, description=queue_pretty, color=settings.color))
        else:
            await ctx.send(embed=discord.Embed(description="**There are currently no songs in the queue!**", color=settings.color))

    @commands.command(aliases=["clear"])
    async def clear_queue(self, ctx):
        """clears queue"""
        await self.clear(ctx)
        if ctx.voice_client is not None and ctx.voice_client.is_playing():
            await ctx.voice_client.stop()

    async def clear(self, ctx):
        global queue
        global song_titles
        queue = []
        song_titles = []

        self.delete_music_files()

        await ctx.send(embed=discord.Embed(description="**Queue has been cleared!**", color=settings.color))

    def delete_music_files(self):
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


class R2D2(commands.Cog):
    def __init__(self, client):
        self.client = client

    async def leave(self, ctx):
        await asyncio.sleep(5)
        if not queue or len(queue) < 1:
            await ctx.voice_client.disconnect()

    async def join(self, ctx):
        if ctx.message.author.voice:
            channel = ctx.message.author.voice.channel

            if ctx.voice_client != None:
                return await ctx.voice_client.move_to(channel)

            await channel.connect()
        else:
            raise Exception

    async def playing_sound(self, ctx, filename):
        if not queue or len(queue) < 1:

            try:
                await self.join(ctx)
            except:
                return await ctx.send(embed=discord.Embed(description="Must be in voice channel to play music.", color=settings.error_color))

            dirname = os.path.dirname(__file__)
            filename = os.path.join(dirname, filename)
            source = discord.PCMVolumeTransformer(
                discord.FFmpegPCMAudio(filename), volume=global_volume)

            ctx.voice_client.play(source,
                                  after=lambda e: print('Player error: %s' % e) if e else None)

            await self.leave(ctx)

        else:
            await ctx.send(embed=discord.Embed(description="**Bot plays music currently**", color=settings.error_color))

    @commands.command(pass_context=True)
    async def r2_scream(self, ctx):
        """Maken yousa comfortable"""

        await self.playing_sound(ctx, "../Sounds/R2 screaming.mp3")

    @commands.command(pass_context=True)
    async def r2_concerned(self, ctx):
        """Mesa concerned"""

        await self.playing_sound(ctx, "../Sounds/Concerned R2D2.mp3")

    @commands.command(pass_context=True)
    async def r2_excited(self, ctx):
        """Gets yousa goen"""

        await self.playing_sound(ctx, "../Sounds/Excited R2D2.mp3")

    @commands.command(pass_context=True)
    async def r2_laughing(self, ctx):
        """**Menacingly laughs**"""

        await self.playing_sound(ctx, "../Sounds/Laughing R2D2.mp3")

    @commands.command(pass_context=True)
    async def r2_sad(self, ctx):
        """Gives yousa depression """

        await self.playing_sound(ctx, "../Sounds/Sad R2D2.mp3")

    @commands.command(pass_context=True)
    async def r2_real_exciting(self, ctx):
        """Mesa really excited"""

        await self.playing_sound(ctx, "../Sounds/Very Excited R2D2.mp3")


def setup(client):
    client.add_cog(Music(client))
    client.add_cog(R2D2(client))
