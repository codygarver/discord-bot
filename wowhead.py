#!/usr/bin/env python3

import json
import os
import pathlib
import requests
import sys
import xml.etree.ElementTree as ET

discord_webhook_url = os.environ["DISCORD_WEBHOOK_URL"]

rss_url = "https://www.wowhead.com/blue-tracker/news/us?rss"

def get_xml(url):
    response = requests.get(url)
    xml = response.content
    return xml

def get_root(xml):
    root = ET.fromstring(xml)
    return root

def get_items(channel):
    items = channel.findall("item")
    return items

def get_title(item):
    title = item.find("title").text
    return title

def get_link(item):
    link = item.find("link").text
    return link

def get_description(item):
    description = item.find("description").text
    return description

def get_pub_date(item):
    pub_date = item.find("pubDate").text
    return pub_date

def get_guid(item):
    guid = item.find("guid").text
    return guid

def get_channel(root):
    channel = root.find("channel")
    return channel

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
    # The name of the file where to store the loots
    loots_file_name = "wowhead.json"

    # A dictionary to store the new loots
    new_loots = {}

    # Read the dictionary from file
    if pathlib.Path(loots_file_name).exists():
        loots = read_json_file_to_dict(loots_file_name)
    else:
        loots = {}

    xml = get_xml(rss_url)

    root = get_root(xml)

    channel = get_channel(root)

    items = get_items(channel)

    for item in items:
        title = get_title(item)
        title = title.strip().lower()
        loot_title = "prime gaming loot"
        if loot_title not in title:
            continue

        link = get_link(item)
        pub_date = get_pub_date(item)
        guid = get_guid(item)

        # Update the dictionary
        loot_dict = {"url": link}
        if title not in loots:
            new_loots[title] = loot_dict

        # Update the dictionary
        loots[title] = loot_dict

    # Post new Mystery Gifts to Discord
    if new_loots:
        for title in new_loots:
            discord_json = { "content": title + "\n" + new_loots[title]["url"] }
            post_to_discord(discord_webhook_url, discord_json)

    # Write the dictionary to file
    write_dict_to_json_file(loots, loots_file_name)