import discord
import logging
import json
import requests
import os
import io
from dotenv import load_dotenv
from discord import app_commands
from discord.ext import tasks
from itertools
from civic_api import search_elections, get_race_map

# For Discord rich presence
activities = [
    discord.Activity(type=discord.ActivityType.watching, name="the polls"),
    discord.Activity(type=discord.ActivityType.listening, name="to voters"),
    discord.Game(name="electoral college"),
    discord.Activity(type=discord.ActivityType.competing, name="the 2026 midterms"),
]

# Retrieve bot token from .env
load_dotenv()

# Initialize the error and debug log, 'w' means "overwrite on each run"
handler = logging.FileHandler(filename='errors_and_debug.log', encoding='utf-8', mode='w')

# Intents/default permissions + allows message content
intents = discord.Intents.default()
intents.message_content = True

# The client is the connection to Discord
client = discord.Client(intents=intents)

# CommandTree is what registers and handles slash commands
tree = app_commands.CommandTree(client)

# Loops through each rich presence every 30 seconds, cosmetic
@tasks.loop(seconds=30)
async def rotate_status():
    await client.change_presence(activity=next(activity_cycle))

# Called when the bot finishes logging in and setting up
@client.event
async def on_ready():
    # Syncs slash commands with Discord so they show up
    await tree.sync()
    print(f'Logged in as {client.user}')

    # Begins the rotation of the different rich presences
    global activity_cycle
    activity_cycle = itertools.cycle(activities)
    rotate_status.start()

# Register the /election slash command
@tree.command(name="election", description="Search for an election")
@app_commands.describe(
    start_date="Start date (YYYY-MM-DD)",
    end_date="End date (YYYY-MM-DD)",
    query="Search query",
    country="Country (Ex. US)",
    province="Province/State (Ex. TX)",
    district="District (Ex. TX-04)",
    election_type="Election type (Ex. Primary, General)",
    limit="Result limit (Ex. 4)"
)
# Takes user input from slash commands and passes them to search_elections() in civic_api.py
async def election(interaction: discord.Interaction,
                   start_date: str = None,
                   end_date: str = None,
                   query: str = None,
                   country: str = None,
                   province: str = None,
                   district: str = None,
                   election_type: str = None,
                   limit: str = None):

    # Tell Discord to wait while the API call runs
    await interaction.response.defer()

    # Call the civic_api.py function with whatever the user provided
    result, data = search_elections(start_date=start_date,
        end_date=end_date,
        query=query,
        country=country,
        province=province,
        district=district,
        election_type=election_type,
        limit=limit)
    
    if not result:
        result = "No results found."
    
    # Send the formatted result back to Discord
    await interaction.followup.send(result)

    # Send a map image for each race that has one
    for race in data["races"]:
        if race["has_map"]:
            image_bytes = get_race_map(race["id"])
            file = discord.File(io.BytesIO(image_bytes), filename="map.png")
            # Send the race name as a label, then the map right after
            await interaction.followup.send(content=f"***{race['election_name']}***", file=file)

# Initialize retrieved bot token into variable
token = os.getenv("DISCORD_TOKEN")

# Run the bot
client.run(token, log_handler=handler)
