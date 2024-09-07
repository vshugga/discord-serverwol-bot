import discord
import subprocess
from discord.ext import commands
import time
import os
from config import bot_token
from wakeonlan import send_magic_packet
from config import *
import asyncio
from mcstatus import JavaServer
    
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.presences = True
players_online = 0
server_awake = False

# Use '!' as the command prefix
client = commands.Bot(command_prefix = "!", intents=intents)
activity_listening = discord.Activity(type=discord.ActivityType.listening, name="!wake")
server = JavaServer.lookup(host)


async def ping(host):
    # print('pinging')
    result = subprocess.run(['ping', '-w', '2', '-c', '1', host], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    # print(f'result: {result}')
    if result.returncode == 0:
        return True
    return False

async def update_status():
    global server_awake, players_online
    while True:
        if await ping(host): # if the server can be pinged
            status = server.status()
            p = status.players.online
            if p != players_online or not server_awake: # only trigger if something changed
                await client.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.playing, name=f"now: {p}"))
                players_online = p
            
            server_awake = True    
                
        elif server_awake: # if the server cant be pinged and server_awake is true
            await client.change_presence(status=discord.Status.idle, activity=activity_listening)
            server_awake = False

        await asyncio.sleep(2)

# When the bot is ready, recieve commands
@client.event
async def on_ready():
    print(f"Bot logged in as {client.user.name}")
    client.loop.create_task(update_status())

@client.command()
async def wake(ctx):
    '''send a WoL magic packet to wake server'''
    send_magic_packet(mac)
    # q = server.query()
    await ctx.send(f"https://c.tenor.com/ois66ovvHmAAAAAC/tenor.gif")

@client.command()
async def list(ctx):
    '''query server data'''
    if await ping(host):
        q = server.query()
        nl = '\n'
        msg = nl.join(q.players.names)
        po = q.players.online
        if po < 1:
            msg = "no one :("

        await ctx.send(f'Currently online:\n{msg}')
    else:
        await ctx.send(f'Server suspended: use `!wake`')
        


client.run(bot_token)

