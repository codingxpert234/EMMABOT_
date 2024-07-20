import discord
from discord.ext import commands
import yt_dlp
import asyncio

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

FFMPEG_OPTIONS = {'options': '-vn'}
YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': True}

class MusicBot(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.queue = []

    @commands.command()
    async def play(self, ctx, *, search):
        voice_channel = ctx.author.voice.channel if ctx.author.voice else None
        if not voice_channel:
            return await ctx.send("You're not connected to a voice channel 😮")

        if not ctx.voice_client:
            await voice_channel.connect()

        async with ctx.typing():
            with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info(f"ytsearch:{search}", download=False)
                if 'entries' in info:
                    info = info['entries'][0]

                url = info['url']
                title = info['title']
                self.queue.append((url, title))
                await ctx.send(f'Added to queue: **{title}**')

        if not ctx.voice_client.is_playing():
            await self.play_next(ctx)

    async def play_next(self, ctx):
        if self.queue:
            url, title = self.queue.pop(0)
            source = await discord.FFmpegOpusAudio.from_probe(url, **FFMPEG_OPTIONS)
            ctx.voice_client.play(source, after=lambda _: self.client.loop.create_task(self.play_next(ctx)))
            await ctx.send(f'Now Playing **{title}**')
        elif not ctx.voice_client.is_playing():
            await ctx.send("Queue is empty")

    @commands.command()
    async def skip(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.send("Skipped")

    @commands.command()
    async def stop(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.send("Stopped playing")
        else:
            await ctx.send("The bot is not playing anything.")

    @commands.command()
    async def resume(self, ctx):
        if ctx.voice_client and not ctx.voice_client.is_playing():
            ctx.voice_client.resume()
            await ctx.send("Resumed playing")
        else:
            await ctx.send("The bot is already playing or there's nothing to resume.")

    @commands.command()
    async def disconnect(self, ctx):
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            await ctx.send("Disconnected from the voice channel")
        else:
            await ctx.send("The bot is not connected to any voice channel.")

client = commands.Bot(command_prefix='?', intents=intents)

async def main():
    await client.add_cog(MusicBot(client))
    await client.start('MTI2MzQ3Njg1OTk3NTQ5OTkyOA.GIHyXb.oU59jK6WoZOiIa2LPQXuwJ-yWoa5MrV5XImyI4')

asyncio.run(main())
