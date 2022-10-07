import discord
from discord.ext import commands
import youtube_dl
import os
from dotenv import load_dotenv

load_dotenv()

client = commands.Bot(command_prefix='%')
songs_list = []

#Play song when appropriate command is given
@client.command()
async def play(ctx, url: str):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    #Look for any previously downloaded song
    song = os.path.isfile("song.mp3")
    try:
        if song:
            #Actively manage memory by removing any song that has finished playing
            os.remove('song.mp3')
    except PermissionError:
        #In case of an error, stop and retry play procedure
        await stop(ctx)
        await play(ctx, url)
    #Get which channel the request was made from
    channel = ctx.message.author.voice.channel
    #If the bot is not already in the requested channel, join the channel
    if not voice:
        vc = await channel.connect()
    #Add the requested song to the queue if not already in the queue
    if songs_list[0] != url:
        songs_list.insert(0, url)

    #Configure YoutubeDL to download song, then download the song
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
    #Name the downloaded song song.mp3
    for file in os.listdir("./"):
        if file.endswith(".mp3"):
            os.rename(file, 'song.mp3')
    #Play the song in the voice channel
    vc.play(discord.FFmpegPCMAudio('song.mp3'), after=lambda e: print('done', e))
    #Remove the song from the queue once it has begun playing
    del songs_list[0]
    #Play the next song in the queue automatically
    await play(ctx, songs_list[0])


@client.command()
#Add a provided url into the queue
async def queue(ctx, url: str):
    songs_list.append(url)
    if songs_list.index(url) == 0:
        await play(ctx, url)


@client.command()
#Join the voice channel the author of the request is in
async def join(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    try:
        channel = ctx.author.voice.channel
        if voice == None:
            await channel.connect()
    except:
        await ctx.send("Please join a voice channel before asking the bot to join")

#Leave current voice channel
@client.command()
async def leave(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice:
        await ctx.voice_client.disconnect()
    else:
        await ctx.send('I am not currently connected to a voice channel')

#Pause current song if playing
@client.command()
async def pause(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        voice.pause()
    else:
        await ctx.send('The bot is not playing anything right now')

#Resume current song if paused
@client.command()
async def resume(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_paused():
        voice.resume()
    else:
        await ctx.send('There is no audio paused right now')

#Completely stop playing current song
@client.command()
async def stop(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    voice.stop()


@client.command()
async def remove(ctx, url: str):
    songs_list.remove(url)

TOKEN = os.getenv('TOKEN')
client.run(TOKEN)