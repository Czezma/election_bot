import requests
import json

# Parameters set to none by default so they're optional
def search_elections(start_date=None, end_date=None, query=None, country=None, province=None, district=None, election_type=None, limit=None):
   
    # Build the params dictionary with only what the user filled in
    # Skipping empty fields prevents sending blank values to the API
    user_input = {}
    if start_date:
        user_input["startDate"] = start_date
    if end_date:
        user_input["endDate"] = end_date
    if query:
        user_input["query"] = query
    if country:
        user_input["country"] = country
    if province:
        user_input["province"] = province
    if district:
        user_input["district"] = district
    if election_type:
        user_input["election_type"] = election_type
    if limit:
        user_input["limit"] = limit

    # Send the request, requests.get() automatically builds the
    # query string from user_input
    response = requests.get(
        "https://civicapi.org/api/v2/race/search", params=user_input)

    # Convert the raw API response text into a Python dictionary
    data = response.json()

    # Format the data into a readable string and return it
    formatted = format_elections(data)

    return formatted, data


def format_elections(data):
    output = ""

    # Loops through each election race returned by the API
    for race in data["races"]:
        # [:10] slices just the date potion, cutting off the timestamp
        output += "***" + race["election_name"] + "***\n"
        output += race["election_date"][:10] + "\n"
        # str() needed because percent_reporting is an integer, not a string
        output += str(race["percent_reporting"]) + "% Reporting\n\n"
        output += "Candidates:\n"

        # Loop through each candidate inside the current race
        for candidate in race["candidates"]:
            # Add a checkmark for winners, space for loser to keep alignment
            if candidate["winner"] == True:
                output += " ✓ **" + candidate["name"] + "**  " + f"{candidate['votes']:,}" + " votes  " + str(candidate["percent"]) + "%\n"
            else:
                output += "     " + candidate["name"] + "  " + f"{candidate['votes']:,}" + " votes  " + str(candidate["percent"]) + "%\n\n"

    return output

def get_race_map(race_id):
    # Fetch the map image for a given race ID
    url = f"https://civicapi.org/api/v2/race/{race_id}?generateMapPNG"
    response = requests.get(url)
    print(f"Map response for race {race_id}: {response.status_code}")
    print(f"Content: {response.content}")
    return response.content # returns raw image bytes