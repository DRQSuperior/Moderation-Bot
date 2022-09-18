import discord
from discord.ext import commands
from discord import Embed
import json
import random
import os
import sqlite3
import asyncio

with open('config.json') as f:
    config = json.load(f)

#Random color for embeds
def random_color():
    return random.randint(0, 0xFFFFFF)

bot = commands.Bot(command_prefix=config['prefix'], intents=discord.Intents.all())
bot.remove_command('help')


@bot.event
async def on_ready():
    print('Bot is ready.')

@bot.command()
async def help(ctx):
    embed = Embed(title='Help | Page 1', description='Help command', color=random_color())
    embed.add_field(name='`!`help', value='Shows this message', inline=True)
    embed.add_field(name='`!`ping', value='Pong!', inline=True)
    embed.add_field(name='`!`say', value='Make the bot say something', inline=True)
    embed.add_field(name='`!`clear', value='Clear messages', inline=True)
    embed.add_field(name='`!`kick', value='Kick a member', inline=True)
    embed.add_field(name='`!`ban', value='Ban a member', inline=True)
    embed.add_field(name='`!`unban', value='Unban a member', inline=True)
    embed.add_field(name='`!`mute', value='Mute a member', inline=True)
    embed.add_field(name='`!`unmute', value='Unmute a member', inline=True)
    message = await ctx.send(embed=embed)
    left = await message.add_reaction('⬅️')
    right = await message.add_reaction('➡️')

    #Checks reaction information and returns it
    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in ['⬅️', '➡️']

    try:
        while True:
            reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=check)
            #If the user clicks the left arrow
            if str(reaction.emoji) == '⬅️':
                #Removes the reaction
                await message.remove_reaction('⬅️', ctx.author)
                embed = Embed(title='Help | Page 1', description='Help command', color=random_color())
                embed.add_field(name='`!`help', value='Shows this message', inline=True)
                embed.add_field(name='`!`ping', value='Pong!', inline=True)
                embed.add_field(name='`!`say', value='Make the bot say something', inline=True)
                embed.add_field(name='`!`clear', value='Clear messages', inline=True)
                embed.add_field(name='`!`kick', value='Kick a member', inline=True)
                embed.add_field(name='`!`ban', value='Ban a member', inline=True)
                embed.add_field(name='`!`unban', value='Unban a member', inline=True)
                embed.add_field(name='`!`mute', value='Mute a member', inline=True)
                embed.add_field(name='`!`unmute', value='Unmute a member', inline=True)
                #Edit the message with the new embed
                await message.edit(embed=embed)
            #If the user clicks the right arrow
            elif str(reaction.emoji) == '➡️':
                #Remove the reaction
                await message.remove_reaction('➡️', ctx.author)
                embed = Embed(title='Help | Page 2', description='Help command', color=random_color())
                embed.add_field(name='`!`warn', value='Warn a member', inline=True)
                embed.add_field(name='`!`warnings', value='Check warnings of a member', inline=True)
                embed.add_field(name='`!`clearwarns', value='Clear warnings of a member', inline=True)
                embed.add_field(name='`!`lock', value='Lock a channel', inline=True)
                embed.add_field(name='`!`unlock', value='Unlock a channel', inline=True)
                embed.add_field(name='`!`nuke', value='Nuke a channel', inline=True)
                embed.add_field(name='`!`slowmode', value='Set slowmode of a channel', inline=True)
                embed.add_field(name='`!`serverinfo', value='Get info about the server', inline=True)
                embed.add_field(name='`!`userinfo', value='Get info about a member', inline=True)
                #Edit the message with the new embed
                await message.edit(embed=embed)
    except asyncio.TimeoutError:
        await message.clear_reactions()

@bot.command()
async def ping(ctx):
    embed = Embed(title='Pong!', description=f'{round(bot.latency * 1000)}ms', color=random_color())
    await ctx.send(embed=embed)

@bot.command()
async def say(ctx, *, message):
    embed = Embed(title='Message', description=message, color=random_color())
    await ctx.message.delete()
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount=5):
    await ctx.channel.purge(limit=amount)
    embed = Embed(title='Cleared Messages', description=f'Cleared {amount} messages', color=random_color())
    await ctx.send(embed=embed, delete_after=5)

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    embed = Embed(title='Kicked Member', description=f'Kicked {member.mention}', color=random_color())
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)
    embed = Embed(title='Banned Member', description=f'Banned {member.mention}', color=random_color())
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(ban_members=True)
async def unban(ctx, *, member):
    banned_users = await ctx.guild.bans()
    member_name, member_discriminator = member.split('#')

    #Loop through all the banned users
    for ban_entry in banned_users:
        user = ban_entry.user

        if (user.name, user.discriminator) == (member_name, member_discriminator):
            await ctx.guild.unban(user)
            embed = Embed(title='Unbanned Member', description=f'Unbanned {user.mention}', color=random_color())
            await ctx.send(embed=embed)
            return

@bot.command()
@commands.has_permissions(manage_roles=True)
async def mute(ctx, member: discord.Member):
    muted_role = discord.utils.get(ctx.guild.roles, name='Muted')

    # If the role doesn't exist, it will create it
    if not muted_role:
        muted_role = await ctx.guild.create_role(name='Muted')

        for channel in ctx.guild.channels:
            await channel.set_permissions(muted_role, speak=False, send_messages=False, read_message_history=True, read_messages=False)

    await member.add_roles(muted_role, reason=None)
    embed = Embed(title='Muted Member', description=f'Muted {member.mention}', color=random_color())
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(manage_roles=True)
async def unmute(ctx, member: discord.Member):
    #Removes the muted role from the member
    muted_role = discord.utils.get(ctx.guild.roles, name='Muted')

    await member.remove_roles(muted_role)
    embed = Embed(title='Unmuted Member', description=f'Unmuted {member.mention}', color=random_color())
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(manage_messages=True)
async def warn(ctx, member: discord.Member, *, reason=None):
    #Check if warnings.db exists
    if not os.path.isfile('warnings.db'):
        #Create warnings.db
        conn = sqlite3.connect('warnings.db')
        c = conn.cursor()
        #Creates table with 3 columns
        c.execute('CREATE TABLE warnings (user_id TEXT, guild_id TEXT, reason TEXT)')
        conn.commit()
        conn.close()

    #Connect to warnings.db
    conn = sqlite3.connect('warnings.db')
    c = conn.cursor()
    #Insert data into table
    c.execute('INSERT INTO warnings VALUES (?, ?, ?)', (member.id, ctx.guild.id, reason))
    conn.commit()
    conn.close()

    embed = Embed(title='Warned Member', description=f'Warned {member.mention}', color=random_color())
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(manage_messages=True)
async def warnings(ctx, member: discord.Member, aliases=['warns']):
    #Connect to warnings.db
    conn = sqlite3.connect('warnings.db')
    c = conn.cursor()
    #Get all the warnings of the member
    c.execute('SELECT * FROM warnings WHERE user_id = ? AND guild_id = ?', (member.id, ctx.guild.id))
    warnings = c.fetchall()
    conn.close()

    #Create an embed
    embed = Embed(title='Warnings', description=f'{member.mention} has {len(warnings)} warnings', color=random_color())
    #Loop through all the warnings
    for warning in warnings:
        #Add a field for each warning
        embed.add_field(name='Warning', value=warning[2], inline=False)
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(manage_messages=True)
async def clearwarns(ctx, member: discord.Member, aliases=['clearwarns']):
    #Check if warnings.db exists
    if not os.path.isfile('warnings.db'):
        conn = sqlite3.connect('warnings.db')
        c = conn.cursor()
        #Creates table if it doesn't exist
        c.execute('CREATE TABLE warnings (user_id TEXT, guild_id TEXT, reason TEXT)')
        conn.commit()
        conn.close()

    #Connect to database
    conn = sqlite3.connect('warnings.db')
    c = conn.cursor()
    #Delete all warnings for the specified user
    c.execute('DELETE FROM warnings WHERE user_id=? AND guild_id=?', (member.id, ctx.guild.id))
    conn.commit()
    conn.close()

    embed = Embed(title='Cleared Warnings', description=f'Cleared the warnings for {member.mention}', color=random_color())
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(manage_channels=True)
async def lock(ctx, channel: discord.TextChannel=None):
    if not channel:
        channel = ctx.channel

    await channel.set_permissions(ctx.guild.default_role, send_messages=False)
    embed = Embed(title='Locked Channel', description=f'Locked {channel.mention}', color=random_color())
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(manage_channels=True)
async def unlock(ctx, channel: discord.TextChannel=None):
    if not channel:
        channel = ctx.channel

    await channel.set_permissions(ctx.guild.default_role, send_messages=True)
    embed = Embed(title='Unlocked Channel', description=f'Unlocked {channel.mention}', color=random_color())
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(manage_channels=True)
async def slowmode(ctx, seconds: int, channel: discord.TextChannel=None, aliases=['slow']):
    if not channel:
        channel = ctx.channel

    await channel.edit(slowmode_delay=seconds)
    embed = Embed(title='Set Slowmode', description=f'Set the slowmode delay for {channel.mention} to {seconds} seconds', color=random_color())
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(manage_channels=True)
async def nuke(ctx, channel: discord.TextChannel=None):
    position = ctx.channel.position
    if not channel:
        channel = ctx.channel

    new_channel = await channel.clone(reason=None)
    await channel.delete()
    await new_channel.edit(position=position)
    embed = Embed(title='Nuked Channel', description=f'Nuked Channel!', color=random_color())
    await new_channel.send(embed=embed)

@bot.command()
async def serverinfo(ctx, aliases=['server']):
    embed = Embed(title=f'{ctx.guild.name} Server Info', description='Server Information', color=random_color())
    embed.add_field(name='Server ID', value=ctx.guild.id, inline=True)
    embed.add_field(name='Server Owner', value=ctx.guild.owner)
    embed.add_field(name='Server Created At', value=ctx.guild.created_at.strftime('%a, %#d %B %Y, %I:%M %p UTC'), inline=True)
    embed.add_field(name='Server Boost Level', value=ctx.guild.premium_tier, inline=True)
    embed.add_field(name='Server Boost Count', value=ctx.guild.premium_subscription_count, inline=True)
    embed.add_field(name='Server Member Count', value=ctx.guild.member_count, inline=True)
    embed.add_field(name='Server Text Channel Count', value=len(ctx.guild.text_channels), inline=True)
    embed.add_field(name='Server Voice Channel Count', value=len(ctx.guild.voice_channels), inline=True)
    embed.add_field(name='Server Role Count', value=len(ctx.guild.roles), inline=True)
    embed.add_field(name='Server Emoji Count', value=len(ctx.guild.emojis), inline=True)
    await ctx.send(embed=embed)

@bot.command()
async def userinfo(ctx, member: discord.Member=None, aliases=['user']):
    if not member:
        member = ctx.author

    embed = Embed(title=f'{member.name} User Info', description='User Information', color=random_color())
    embed.add_field(name='User ID', value=member.id)
    embed.add_field(name='User Status', value=member.status)
    embed.add_field(name='User Highest Role', value=member.top_role.mention)
    embed.add_field(name='User Joined At', value=member.joined_at.strftime('%a, %#d %B %Y, %I:%M %p UTC'))
    embed.set_thumbnail(url=member.avatar.url)
    await ctx.send(embed=embed)

bot.run(config['token'])