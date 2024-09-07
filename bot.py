import discord
import typing
import json
import enum
import time
import datetime
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='ploice!', intents=intents)
tree = bot.tree

# Load existing data from db.json
def load_db():
    try:
        with open('db.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# Save data to db.json
def save_db(data):
    with open('db.json', 'w') as f:
        json.dump(data, f, indent=4)

class truefalse(str, enum.Enum):
    Yes = "yes"
    No = "no"

def convert_time_to_seconds(time_str):
    time_unit = time_str[-1]  # Get the last character which indicates the unit (e.g., 'd')
    time_value = int(time_str[:-1])  # Get the numeric value (e.g., '4')

    if time_unit == 'w':
        return time_value * 604800  # 1 week = 604800 seconds
    elif time_unit == 'd':
        return time_value * 86400  # 1 day = 86400 seconds
    elif time_unit == 'h':
        return time_value * 3600  # 1 hour = 3600 seconds
    elif time_unit == 'm':
        return time_value * 60  # 1 minute = 60 seconds
    elif time_unit == 's':
        return time_value  # Already in seconds
    else:
        raise ValueError("Unsupported time unit")

@bot.event
async def on_ready():
    await bot.tree.sync()  # Synchronize the commands with Discord
    print(f"yiur bto is runnign :3")

@bot.hybrid_command(name="speak", description="says something")
@app_commands.describe(message="what to says")
async def speak(ctx: commands.Context, message: str):
    await ctx.send(message)

@bot.hybrid_command(name="ping", description="tests roundtrip latency")
async def ping(ctx: commands.Context):
    await ctx.send(f"<:amadaping:1280061745280454792> Pong!! ctqa brain has a latency of {round(bot.latency *1000)} ms")

@bot.hybrid_command(name="ban", description="yeet but harder")
@commands.has_permissions(ban_members=True)
@discord.app_commands.default_permissions(ban_members=True)
@app_commands.describe(user="the nerd to yeet")
@app_commands.describe(reason="reason (e.g. memes in general)")
async def ban(ctx: commands.Context, user: discord.User, reason: str = "No reason provided", appeal: truefalse = "yes"):
    # Define the button
    button = discord.ui.Button(label="Confirm", style=discord.ButtonStyle.secondary)

    # Define the callback function for the button
    async def button_callback(interaction: discord.Interaction):
        if interaction.user != ctx.author:
            await interaction.response.send_message("403 forbidden", ephemeral=True)
            return

        # Perform the ban and stuff
        try:
            db = load_db()
            # Retrieve the appeal message
            server_id = str(ctx.guild.id)
            appeal_info = db.get(server_id, {})
            # Ensure appeal_message is defined
            appeal_message = appeal_info.get("appeal_message", "you cant appeal this ban.") if appeal == "yes" else "you cant appeal this ban."
            await user.send(f"hello nerd you might have been banned from {ctx.guild.name} for `{reason}`. {appeal_message}")

       #you cant appeal this ban.
        except Exception as e:
            print(f"Failed to send DM: {e}")

        await interaction.guild.ban(user, reason=reason, delete_message_seconds=0)
        await interaction.response.edit_message(content=f"{user.mention} was permanently banned by {interaction.user.mention} for `{reason}`.", view=None)

    # Assign the callback to the button
    button.callback = button_callback

    view = discord.ui.View()
    view.add_item(button)
    await ctx.send(f"Banning {user.mention}?", view=view)

@ban.error
async def ban_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send("403 forbidden", ephemeral=True)

@bot.hybrid_command(name="appeal", description="how did we get here")
@commands.has_permissions(manage_guild=True)
@discord.app_commands.default_permissions(manage_guild=True)
@app_commands.describe(appeal="how the fuck do you appeal")
async def speak(ctx: commands.Context, appeal: str):
    # Load the database
    db = load_db()

    # Save the appeal message and server ID
    server_id = str(ctx.guild.id)
    # Ensure the server ID exists in the database
    if server_id not in db:
        db[server_id] = {}

    db[server_id]["appeal_message"] = appeal


    # Save the updated database
    save_db(db)
    await ctx.send(f"appeal message set to {appeal} for {ctx.guild.name}")

@bot.hybrid_command(name="kick", description="yeet")
@commands.has_permissions(kick_members=True)
@discord.app_commands.default_permissions(kick_members=True)
@app_commands.describe(user="the nerd to yeet")
@app_commands.describe(reason="reason (e.g. memes in general)")
@app_commands.describe(reason="if ban should be appealable. if /appeal wasnt run then this has no effect")
async def kick(ctx: commands.Context, user: discord.User, reason: str):
    # Define the button
    button = discord.ui.Button(label="Confirm", style=discord.ButtonStyle.secondary)

    # Define the callback function for the button
    async def button_callback(interaction: discord.Interaction):
        if interaction.user != ctx.author:
            await interaction.response.send_message("403 forbidden", ephemeral=True)
            return

        # Perform the kick and stuff
        try:
            await user.send(f"hello nerd you might have been kicked from {ctx.guild.name} for `{reason}`.")
        except Exception as e:
            print(f"Failed to send DM: {e}")

        await interaction.guild.kick(user, reason=reason)
        await interaction.response.edit_message(content=f"{user.mention} was kicked by {interaction.user.mention} for `{reason}`.", view=None)

    # Assign the callback to the button
    button.callback = button_callback

    view = discord.ui.View()
    view.add_item(button)
    await ctx.send(f"Kicking {user.mention}?", view=view)

@kick.error
async def kick_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send("403 forbidden", ephemeral=True)

@bot.hybrid_command(name="lock", description="lock emoji")
@commands.has_permissions(manage_channels=True)
@discord.app_commands.default_permissions(manage_channels=True)
async def lock(ctx: commands.Context):
    perms = ctx.channel.overwrites_for(ctx.guild.default_role)
    perms.send_messages=False
    await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=perms)
    await ctx.send(f"🔒 {ctx.channel.mention} has been locked by {ctx.author.mention}")
@lock.error
async def kick_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send("403 forbidden", ephemeral=True)

@bot.hybrid_command(name="unlock", description="key emoji")
@commands.has_permissions(manage_channels=True)
@discord.app_commands.default_permissions(manage_channels=True)
async def unlock(ctx: commands.Context):
    perms = ctx.channel.overwrites_for(ctx.guild.default_role)
    perms.send_messages=True
    await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=perms)
    await ctx.send(f"🔓 {ctx.channel.mention} has been unlocked by {ctx.author.mention}")
@unlock.error
async def kick_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send("403 forbidden", ephemeral=True)

@bot.hybrid_command(name="mute", description="hahah imagine being a mute")
@commands.has_permissions(moderate_members=True)
@discord.app_commands.default_permissions(moderate_members=True)
@app_commands.describe(user="your free trial of talking has ended")
@app_commands.describe(lengh="lengh of no yap perms (e.g. 4d)")
@app_commands.describe(reason="i muted you becuz your annoying")
async def mute(ctx: commands.Context, user: discord.User, lengh: str, reason: str):
    clock = convert_time_to_seconds(lengh)
    await ctx.send(f"{user.mention} was muted by {ctx.author.mention} for `{reason}`! This mute expires <t:{round(time.time()) + clock}:R>")
    try:
        await user.send(f"hello nerd you might have been muted in {ctx.guild.name} for `{reason}`.")
    except Exception as e:
        print(f"Failed to send DM: {e}")
    await user.timeout(datetime.timedelta(seconds=clock), reason=f"{reason}")
@mute.error
async def kick_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send("403 forbidden", ephemeral=True)

@bot.hybrid_command(name="unmute", description="wtf i can talk")
@commands.has_permissions(moderate_members=True)
@discord.app_commands.default_permissions(moderate_members=True)
@app_commands.describe(user="Mods, unmute this person")
@app_commands.describe(reason="why ummute tbh")
async def unmute(ctx: commands.Context, user: discord.User, reason: str):
    await ctx.send(f"{user.mention} was unmuted by {ctx.author.mention} for `{reason}`.")
    await user.timeout(None, reason=f"{reason}")
@unmute.error
async def kick_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send("403 forbidden", ephemeral=True)

@bot.hybrid_command(name="unban", description="unyeet??")
@commands.has_permissions(ban_members=True)
@discord.app_commands.default_permissions(ban_members=True)
@app_commands.describe(user="the nerd to... unyeet")
@app_commands.describe(reason="why was the user unyeet")
async def unban(ctx: commands.Context, user: discord.User, reason: str = "No reason provided"):
    await ctx.guild.unban(user, reason=reason)
    await ctx.send(content=f"{user.mention} was unbanned by {ctx.author.mention} for `{reason}`!!!")

@ban.error
async def ban_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send("403 forbidden", ephemeral=True)

@bot.hybrid_command(name="purge", description="Ooh, live the dream with a time machine")
@commands.has_permissions(manage_messages=True)
@discord.app_commands.default_permissions(manage_messages=True)
@app_commands.describe(user="user to purge")
@app_commands.describe(limit="max ammount is 1000")
async def purge(ctx: commands.Context, limit: int, user: discord.User = None):
    # Ensure the limit is within bounds
    limit = max(1, min(limit, 1000))

    # Define a check function to filter messages
    def check(msg):
        return user is None or msg.author == user

    # Perform the bulk delete
    deleted = await ctx.channel.purge(limit=limit, check=check)

    # Send a confirmation message
    await ctx.send(content=f"Last {len(deleted)} messages{' from ' + user.mention if user else ''} were purged by {ctx.author.mention}.")
@ban.error
async def ban_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send("403 forbidden", ephemeral=True)

@bot.hybrid_command(name="slowmode", description="change the speed of the chat")
@commands.has_permissions(manage_channels=True)
@discord.app_commands.default_permissions(manage_channels=True)
@app_commands.describe(slowmode="slowmode time. max is 6 hours you goob, please specifiy unit")
async def slowmode(ctx: commands.Context, slowmode: str):
    delay = convert_time_to_seconds(slowmode)
    await ctx.channel.edit(slowmode_delay=delay)
    await ctx.send(f":zzz: Now going at {slowmode} slowmode!")
@slowmode.error
async def ban_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send("403 forbidden", ephemeral=True)

@bot.hybrid_command(name="starboard", description="where good messages go")
@commands.has_permissions(manage_guild=True)
@discord.app_commands.default_permissions(manage_guild=True)
@app_commands.describe(channel="WHAT !")
@app_commands.describe(emoji=":staring_ctqa:")
@app_commands.describe(threshold="how many people need to care")
async def setstarboard(ctx: commands.Context, channel: discord.TextChannel, emoji: str = "⭐", threshold: int = 3):
    # Load the database
    db = load_db()

    # Save the starboard channel ID, emoji, threshold, and server ID
    server_id = str(ctx.guild.id)
    if server_id not in db:
        db[server_id] = {}
    db[server_id]["starboard_channel_id"] = channel.id
    db[server_id]["starboard_emoji"] = emoji
    db[server_id]["starboard_threshold"] = threshold

    # Save the updated database
    save_db(db)
    await ctx.send(f"⭐ Starboard channel set to {channel.mention} with emoji {emoji} and threshold {threshold} for {ctx.guild.name}")

@bot.event
async def on_raw_reaction_add(payload):
    # Load the database
    db = load_db()
    server_id = str(payload.guild_id)

    # Ensure the server is in the database
    if server_id not in db:
        return

    # Get the emoji and threshold from the database
    starboard_emoji = db[server_id].get("starboard_emoji")
    starboard_threshold = db[server_id].get("starboard_threshold", 3)  # Default threshold is 3 if not specified

    # If no emoji or threshold is found, return early
    if not starboard_emoji or not starboard_threshold:
        return

    # Compare the reaction emoji with the stored starboard emoji
    if payload.emoji.name == starboard_emoji or str(payload.emoji) == starboard_emoji:
        guild = bot.get_guild(payload.guild_id)
        channel = guild.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)

        for reaction in message.reactions:
            if (reaction.emoji == payload.emoji.name or str(reaction.emoji) == starboard_emoji) and reaction.count >= starboard_threshold:
                message_id = str(payload.message_id)

                # Check if the message already exists in the database
                if "starred_messages" in db[server_id] and message_id in db[server_id]["starred_messages"]:
                    return

                # Store the message ID and reaction count in the database
                if "starred_messages" not in db[server_id]:
                    db[server_id]["starred_messages"] = {}
                db[server_id]["starred_messages"][message_id] = reaction.count
                save_db(db)

                # Get the starboard channel ID from the database
                starboard_channel_id = db[server_id].get("starboard_channel_id")
                if not starboard_channel_id:
                    return

                starboard_channel = bot.get_channel(starboard_channel_id)
                jump_url = message.jump_url

                if starboard_channel:
                    embed = discord.Embed(description=message.content, color=discord.Color.gold())
                    embed.set_author(name=message.author.display_name, icon_url=message.author.avatar.url)
                    embed.add_field(name="Jump to message", value=f"[Click here]({jump_url})")

                    if len(message.attachments) > 0:
                        embed.set_image(url=message.attachments[0].url)

                    await starboard_channel.send(embed=embed)

bot.run("[Token Redacted]")

