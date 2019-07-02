
# !/usr/bin/python3

import tweepy
import configparser
import os
import random
from time import sleep
from contextlib import contextmanager
import reddit_images as r


def get_twitter_tokens():

    config = configparser.ConfigParser()
    config.read('config.ini')
    consumer_key = config['TWITTER']['consumer_key']
    consumer_secret = config['TWITTER']['consumer_secret']
    access_token = config['TWITTER']['access_token']
    access_token_secret = config['TWITTER']['access_token_secret']
    return consumer_key, consumer_secret, access_token, access_token_secret


def get_filename_for_tweet():

    # selects the first image from sorted list of files in current directory
    directory = os.getcwd()
    my_dir = os.listdir(directory)
    all_files = sorted([file for file in my_dir if file.endswith(".jpg")])
    filename = all_files[0]

    return filename


def remove_tweeted_image():

    # removes the image after it's been tweeted
    delete_file = get_filename_for_tweet()
    os.remove(delete_file)


def get_twitter_media_id(filename):

    file = open(filename, 'rb')
    upload = api.media_upload(filename=filename, file=file)
    media_id = [upload.media_id_string]

    return media_id


def get_place_trends(woeid):
    # woeid (can be int or str): Yahoo! Where On Earth ID of the location (Global is 1)
    # list of woeids: https://codebeautify.org/jsonviewer/f83352
    local_trends = api.trends_place(id=woeid) # returns a list with 1 huge dict
    trend_dict_list = local_trends[0]["trends"] # extracting a list with trends from the huge dict
    just_trends = [i["name"] for i in trend_dict_list]

    return just_trends


def get_random_trending_hashtag(trend_list):
    # extracts a hashtag from the current trends
    hashtags = [trend for trend in trend_list if trend.startswith("#")]
    random_trend = random.choice(hashtags)

    return random_trend


def compile_status(string, trend_hashtag):
    try:
        one, two = string.split("hashtag")
        status_message = one + trend_hashtag + two
        return status_message
    except ValueError:
        print(string)
        print(trend_hashtag)

@contextmanager
def change_dir(destination):
    cwd = os.getcwd()
    try:
        os.chdir(destination)
        yield
    finally:
        os.chdir(cwd)


# if __name__ = "__main__"

subreddit = 'pasta'
img_directory = f"{subreddit}pics"
number = 25
delay = 60 * 60 * 17

consumer_key, consumer_secret, access_token, access_token_secret = get_twitter_tokens()

print('trying to connect...')

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

print('Connected!')

while True:

    if not os.path.exists(img_directory):
        os.mkdir(img_directory)

    pasta_urls = r.get_image_urls(subreddit, number)

    with change_dir(img_directory):
        new_images = r.get_unused_pics(pasta_urls)
        r.save_new_images(new_images)

    print("Selecting a status message...")
    with open("tweets.txt", "r") as f:
        tweet_text = random.choice(f.readlines())

    print("Looking at the current trends...")
    current_us_trends = get_place_trends(23424977)

    print("Selecting a hashtag...")
    hashtag = get_random_trending_hashtag(current_us_trends)

    with change_dir("pastapics"):
        print("Looking for a pic to tweet...")
        file_to_tweet = get_filename_for_tweet()

        print("Found one! Uploading it to twitter...")
        media_id = get_twitter_media_id(file_to_tweet)

        print("done. removing it from ur direc...")
        remove_tweeted_image()

    print("compiling tweet...")
    message = compile_status(tweet_text, hashtag)
    print(message)

    print("ready to tweet...")
    api.update_status(media_ids=media_id, status=message)

    print(f"Done! Sleeping for {delay/60/60} hours")
    sleep(delay)


