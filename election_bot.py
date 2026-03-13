import discord
import logging
import json
import requests
import os
from dotenv import load_dotenv
from discord import app_commands
from civic_api import search_elections

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

# Called when the bot finishes logging in and setting up
@client.event
async def on_ready():
    # Syncs slash commands with Discord so they show up
    await tree.sync()
    print(f'Logged in as {client.user}')

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
    result = search_elections(start_date=start_date,
        end_date=end_date,
        query=query,
        country=country,
        province=province,
        district=district,
        election_type=election_type,
        limit=limit)
    
    if not result:
        result = "No results found. Fuck you."
    
    # Send the formatted result back to Discord
    await interaction.followup.send(result)

# Initialize retrieved bot token into variable
token = os.getenv("DISCORD_TOKEN")

# Run the bot
client.run(token, log_handler=handler)