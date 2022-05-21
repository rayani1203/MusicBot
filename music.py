import discord
from discord.ext import commands
import youtube_dl
import os

client = commands.Bot(command_prefix='%')
songs_list = []


@client.command()
async def play(ctx, url: str):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    song = os.path.isfile("song.mp3")
    try:
        if song:
            os.remove('song.mp3')
    except PermissionError:
        await stop(ctx)
        await play(ctx, url)
    channel = ctx.message.author.voice.channel
    if not voice:
        vc = await channel.connect()
    songs_list.insert(0, url)

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([songs_list[0]])
    for file in os.listdir("./"):
        if file.endswith(".mp3"):
            os.rename(file, 'song.mp3')
    vc.play(discord.FFmpegPCMAudio('song.mp3'), after=lambda e: print('done', e))
    del songs_list[0]
    await play(ctx, songs_list[0])


@client.command()
async def queue(ctx, url: str):
    songs_list.append(url)
    if songs_list.index(url) == 0:
        await play(ctx, url)


@client.command()
async def join(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    try:
        channel = ctx.author.voice.channel
        if voice == None:
            await channel.connect()
    except:
        await ctx.send("Please join a voice channel before asking the bot to join")


@client.command()
async def leave(ctx):
    await ctx.voice_client.disconnect()
    # else:
        # await ctx.send('I am not currently connected to a voice channel')


@client.command()
async def pause(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        voice.pause()
    else:
        await ctx.send('The bot is not playing anything right now')


@client.command()
async def resume(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_paused():
        voice.resume()
    else:
        await ctx.send('There is no audio paused right now')


@client.command()
async def stop(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    voice.stop()


@client.command()
async def remove(ctx, url: str):
    songs_list.remove(url)

client.run(TOKEN)
