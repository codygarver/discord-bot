#!/usr/bin/env python3

from bs4 import BeautifulSoup
import datetime
import json
import os
import pathlib
import requests
import sys
import time
from functools import wraps

discord_webhook_url = os.environ["DISCORD_WEBHOOK_URL"]

def retry(retries=3, delay=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt < retries - 1:
                        print(f"Error: {e}. Retrying in {delay} seconds...")
                        time.sleep(delay)
                        continue
                    else:
                        raise e
        return wrapper
    return decorator

@retry(retries=3, delay=1)
def fetch_page(url):
    response = requests.get(url)
    if response.status_code != 200:
        raise ValueError(f"Failed to fetch the page, status code: {response.status_code}")
    return response

@retry(retries=3, delay=1)
def parse_html(content):
    return BeautifulSoup(content, "html.parser")

@retry(retries=3, delay=1)
def post_to_discord(discord_webhook_url, discord_json):
    result = requests.post(discord_webhook_url, json=discord_json)
    result.raise_for_status()
    print("Post succeeded!: ".format(result.status_code))

def get_table(soup):
    table = soup.find("table")
    if not table:
        raise ValueError("Table not found in the HTML content")
    return table

def get_rows(table):
    rows = table.find_all("tr")
    if not rows:
        raise ValueError("No rows found in the table")
    return rows

def get_columns(row):
    columns = row.find_all("td")
    if not columns:
        raise ValueError("No columns found in the row")
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

if __name__ == "__main__":
    # The URL of the page to scrape
    page_url = "https://www.nintendolife.com/guides/pokemon-scarlet-and-violet-mystery-gift-codes-list"

    # Get the page
    page = fetch_page(page_url)

    # Parse the page
    soup = parse_html(page.content)

    # The name of the file where to store the codes
    codes_file_name = "mysterygifts.json"

    # A dictionary to store the new codes
    new_codes = {}

    # Read the dictionary from file
    if pathlib.Path(codes_file_name).exists():
        codes = read_json_file_to_dict(codes_file_name)
    else:
        codes = {}

    try:
        # Get the table
        table = get_table(soup)

        # Get the rows
        rows = get_rows(table)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Iterate over the rows
    for row in rows[1:]:
        try:
            # Get the columns
            columns = get_columns(row)

            # Get the code
            code = get_code(columns)

            # Get the gift
            gift = get_gift(columns)
            # Convert newlines to commas
            gift = gift.replace("\n", ", ")

            # Get the date
            date = get_date(columns)
            # Discard the time
            date = date.split("-")[0].strip()

            # Remove the suffixes from the day
            suffixes = "st", "nd", "rd", "th"
            for suffix in suffixes:
                date = date.replace(suffix, "")

            # Replace Sept with Sep
            date = date.replace("Sept", "Sep")

            date_formats = "%d %b %Y", "%d %B %Y", "%d %b, %Y"

            date_stripped = None

            print(f"Trying to convert {date}")
            # Try to convert the date to a datetime object
            for date_format in date_formats:
                try:
                    date_stripped = datetime.datetime.strptime(date, date_format)
                    print(f"Success: {date} is a suitable date for {date_format}")
                    # Convert the date to YYYY-MM-DD
                    date = date_stripped.strftime("%Y-%m-%d")
                    break
                except:
                    print(f"Error: {date} is not a suitable date for {date_format}")
                    pass

            # Update the dictionary
            code_dict = {"gift": gift, "expires": date}
            if code not in codes:
                new_codes[code] = code_dict

            # Update the dictionary
            codes[code] = code_dict

        except ValueError as e:
            print(f"Error processing row: {e}")
            continue

    # Post new Mystery Gifts to Discord
    if new_codes:
        for code in new_codes:
            discord_message = f"New Pokemon Scarlet & Violet Mystery Gift :gift: code: `{code}` - {codes[code]['gift']} - Expires {codes[code]['expires']}"
            discord_json = {"content": discord_message}
            try:
                post_to_discord(discord_webhook_url, discord_json)
            except Exception as e:
                print(f"Error posting to Discord: {e}")

    # Write the dictionary to file
    write_dict_to_json_file(codes, codes_file_name)
