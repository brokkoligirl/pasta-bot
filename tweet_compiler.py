
# !/usr/bin/python3
import tweepy
import configparser
import random
import datetime


def get_twitter_tokens():

    config = configparser.ConfigParser()
    config.read('config.ini')
    c_key = config['TWITTER']['consumer_key']
    c_secret = config['TWITTER']['consumer_secret']
    a_token = config['TWITTER']['access_token']
    a_token_secret = config['TWITTER']['access_token_secret']

    return c_key, c_secret, a_token, a_token_secret


def twitter_auth(c_key, c_secret, a_token, a_token_secret):

    auth = tweepy.OAuthHandler(c_key, c_secret)
    auth.set_access_token(a_token, a_token_secret)
    api = tweepy.API(auth)

    return api


def get_twitter_media_id(api, filename):

    file = open(filename, 'rb')
    upload = api.media_upload(filename=filename, file=file)
    media_id = [upload.media_id_string]

    return media_id


def get_place_trends(api, woeid):
    # woeid (can be int or str): Yahoo! Where On Earth ID of the location (Global is 1)
    # list of woeids: https://codebeautify.org/jsonviewer/f83352
    local_trends = api.trends_place(id=woeid)
    # a list with 1 huge dict:
    trend_dict_list = local_trends[0]["trends"]
    # extracting a list with trends from the huge dict
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

    except ValueError:
        print("I couldn't compile a status out of these:")
        print("Text: ", string)
        print("Hashtag: ", trend_hashtag)

        date = datetime.datetime.today()
        today = datetime.datetime.strftime(date, "%B %d")
        status_message = f"As a bot, I can't do much. But I can read a calendar. " \
            f"{today}, what an amazing day to look at some pasta ..."

    return status_message
