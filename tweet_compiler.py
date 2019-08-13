
# !/usr/bin/python3

import tweepy
import configparser
import datetime
import logging

logger = logging.getLogger("pastabot.tweet_compiler")


def get_twitter_tokens():

    config = configparser.ConfigParser()
    config.read('config.ini')
    c_key = config['TWITTER']['consumer_key']
    c_secret = config['TWITTER']['consumer_secret']
    a_token = config['TWITTER']['access_token']
    a_token_secret = config['TWITTER']['access_token_secret']

    logger.info("Grqbbed twitter credensh from config file...")

    return c_key, c_secret, a_token, a_token_secret


def twitter_auth(c_key, c_secret, a_token, a_token_secret):

    auth = tweepy.OAuthHandler(c_key, c_secret)
    auth.set_access_token(a_token, a_token_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True)

    logger.info("Connected to twitter...")

    return api


def get_twitter_media_id(api, filename):

    file = open(filename, 'rb')
    upload = api.media_upload(filename=filename, file=file)
    media_id = [upload.media_id_string]

    logger.info("Uploaded pic and got a media id...")

    return media_id


def get_local_trends(api, woeid):

    # woeid (can be int or str): Yahoo! Where On Earth ID of the location (Global is 1)

    local_trends = api.trends_place(id=woeid)
    # a list with 1 huge dict:
    trend_dict_list = local_trends[0]["trends"]
    # extracting a list with trends from the huge dict
    trend_list = [i["name"] for i in trend_dict_list]

    logger.info(f"Grabbed current local trends for woeid {woeid} from twitter...")

    return trend_list


def non_offensive_hashtags(trend_list):

    # select trends that have a hashtag and that don't start with #rip since we don't want the bot
    # to make light-hearted pasta conversation about someone dying, obvi
    hashtags = [trend for trend in trend_list if trend.startswith("#") and not trend.startswith("#rip")]
    og_num_of_tags = len(hashtags)
    # this is a list of words that we also want to avoid in the hashtag we end up using for our bot's tweet
    # so we're looping through our current trends to check if any of them contain any of those words
    offensive_list = ['shooting', 'shooter', 'dead', 'death', 'attack',
                      'kill', 'suicide', 'murder', 'terror', 'died']
    for trend in hashtags:
        for tag in offensive_list:
            if tag in trend:
                hashtags.remove(trend)

    logger.info(f"{og_num_of_tags-len(hashtags)} of {og_num_of_tags} hashtags removed during offensiveness screening")

    return hashtags


def compile_status(string, trend_hashtag):
    try:
        one, two = string.split("hashtag")
        status_message = one + trend_hashtag + two

    except ValueError:
        logger.exception(f"I couldn't compile a status out of: {string}, {trend_hashtag}")

        date = datetime.datetime.today()
        today = datetime.datetime.strftime(date, "%B %d")
        status_message = f"As a bot, I can't do much. But I can read a calendar. " \
            f"{today}, what an amazing day to look at some pasta ..."

    logger.info(f"Compiled Tweet: {status_message}")

    return status_message


def update_status(api, media_id, message):
    api.update_status(media_ids=media_id, status=message)
    logger.info("Posted tweet & pic to twitter.")
