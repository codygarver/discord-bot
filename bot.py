#!/usr/bin/env python3

from bs4 import BeautifulSoup
import datetime
import json
import os
import pathlib
import requests
import sys

discord_webhook_url = os.environ["DISCORD_WEBHOOK_URL"]


def get_table(soup):
    table = soup.find("table")
    return table

def get_rows(table):
    rows = table.find_all("tr")
    return rows

def get_columns(row):
    columns = row.find_all("td")
    return columns

def get_code(columns):
    code = columns[0].text.strip()
    return code

def get_gift(columns):
    pokemon = columns[1].text.strip()
    return pokemon

def get_date(columns):
    date = columns[2].text.strip()
    return date

def read_json_file_to_dict(file_name):
    # Read the file into a dictionary
    with open(file_name, "r") as file:
        dictionary = json.loads(file.read())
    return dictionary

def write_dict_to_json_file(dictionary, file_name):
    # Write the dictionary to a file
    with open(file_name, "w") as file:
        file.write(json.dumps(dictionary, indent=4))

def post_to_discord(discord_webhook_url, discord_json):
    result = requests.post(discord_webhook_url, json=discord_json)
    try:
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)
        sys.exit(1)
    else:
        print("Post succeeded!: ".format(
            result.status_code))


if __name__ == "__main__":
    page_url = "https://www.nintendolife.com/guides/pokemon-scarlet-and-violet-mystery-gift-codes-list"

    page = requests.get(page_url)

    soup = BeautifulSoup(page.content, "html.parser")

    codes_file_name = "mysterygifts.json"

    new_codes = {}

    if pathlib.Path(codes_file_name).exists():
        codes = read_json_file_to_dict(codes_file_name)
    else:
        codes = {}

    table = get_table(soup)

    rows = get_rows(table)
    for row in rows[1:]:
        # Get the code
        code = get_code(get_columns(row))

        # Get the gift
        gift = get_gift(get_columns(row))
        # Convert newlines to commas
        gift = gift.replace("\n", ", ")

        # Get the date
        date = get_date(get_columns(row))
        # Discard the time
        date = date.split("-")[0].strip()

        # Remove the suffixes from the day
        suffixes = "st", "nd", "rd", "th"
        for suffix in suffixes:
            date = date.replace(suffix, "")

        # Convert the date to a datetime object
        try:
            date = datetime.datetime.strptime(date, "%d %b %Y")
        except ValueError:
            date = datetime.datetime.strptime(date, "%d %B %Y")
        # Convert the date to YYYY-MM-DD
        date = date.strftime("%Y-%m-%d")

        # Update the dictionary
        code_dict = {"gift": gift, "expires": date}
        if code not in codes:
            new_codes[code] = code_dict

        codes[code] = code_dict

    discord_messages = []
    for code in new_codes:
        discord_messages.append(f":gift: New Pokemon Scarlet & Violet Mystery Gift code!: `{code}` - {codes[code]['gift']} - Expires {codes[code]['expires']}")

    for discord_message in discord_messages:
        discord_json = { "content": discord_message }
        post_to_discord(discord_webhook_url, discord_json)

    write_dict_to_json_file(codes, codes_file_name)
