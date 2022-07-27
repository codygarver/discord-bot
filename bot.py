#!/usr/bin/env python3

import datetime
import os
import pytz
import re
import requests
import sys
import tweepy

discord_webhook_url = os.environ["DISCORD_WEBHOOK_URL"]
tweet_regex = os.environ["TWEET_REGEX"]
twitter_access_token = os.environ["TWITTER_ACCESS_TOKEN"]
twitter_access_token_secret = os.environ["TWITTER_ACCESS_TOKEN_SECRET"]
twitter_account_scanned = os.environ["TWITTER_ACCOUNT_SCANNED"]
twitter_api_key = os.environ["TWITTER_API_KEY"]
twitter_api_key_secret = os.environ["TWITTER_API_KEY_SECRET"]


def get_tweets(api):
    tweets = api.user_timeline(screen_name=twitter_account_scanned,
                               # 200 is the maximum allowed count
                               count=200,
                               exclude_replies=True,
                               include_rts=False,
                               # Necessary to keep full_text
                               # otherwise only the first 140 words are extracted
                               tweet_mode="extended"
                               )

    time_period = pytz.UTC.localize(
        datetime.datetime.utcnow() - datetime.timedelta(hours=6))

    tweet_urls = []
    for tweet in tweets:
        if tweet.created_at > time_period and re.search(tweet_regex, tweet.full_text, re.IGNORECASE):
            # print(tweet.full_text)
            tweet_url = "https://twitter.com/" + \
                twitter_account_scanned + "/status/" + tweet.id_str
            tweet_urls = tweet_urls + [tweet_url]

    return tweet_urls


def get_twitter_api():
    auth = tweepy.OAuthHandler(twitter_api_key, twitter_api_key_secret)
    auth.set_access_token(twitter_access_token, twitter_access_token_secret)

    api = tweepy.API(auth)

    try:
        api.verify_credentials()
    except Exception as e:
        print("Authentication FAILED!")
        print(e)
        sys.exit(1)

    return api


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
    api = get_twitter_api()
    tweet_urls = get_tweets(api)
    if tweet_urls:
        for url in tweet_urls:
            discord_json = {"content": url}
            post_to_discord(discord_webhook_url, discord_json)
