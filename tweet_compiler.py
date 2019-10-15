
# !/usr/bin/python3

import tweepy
import configparser
import datetime
import logging
import sys
import random

logger = logging.getLogger("pastabot.tweet_compiler")


def get_twitter_tokens(filename='config.ini'):
    """
    fetches twitter API tokens from config file
    :return: c_key, c_secret, a_token, a_token_secret
    """

    config = configparser.ConfigParser()
    config.read(filename)
    c_key = config['TWITTER']['consumer_key']
    c_secret = config['TWITTER']['consumer_secret']
    a_token = config['TWITTER']['access_token']
    a_token_secret = config['TWITTER']['access_token_secret']

    logger.debug("Grabbed twitter credensh from config file...")

    return c_key, c_secret, a_token, a_token_secret


def twitter_auth(c_key, c_secret, a_token, a_token_secret):
    """
    function for twitter authentication.
    :return: tweepy.API object
    """

    auth = tweepy.OAuthHandler(c_key, c_secret)
    auth.set_access_token(a_token, a_token_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True)

    logger.debug("Connected to twitter...")

    return api


def get_twitter_media_id(api, filename):

    """
    uploads a pic to twitter and returns media id needed to tweet the pic
    :param api: tweepy api object for twitter authentication
    :param filename: file selected for tweeting and uploading
    :return: media_id twitter needs for status updates with media attachments
    """

    with open(filename, 'rb') as file:
        upload = api.media_upload(filename=filename, file=file)
        media_id = [upload.media_id_string]

    logger.debug("Uploaded pic and got a media id...")

    return media_id


def get_local_trends(api, woeid=23424977):

    """
    :param api: tweepy api object for twitter authentication
    :param woeid: "Where On Earth ID", used for identifying locations, defaults to US (23424977)
    :return: list of current local trending topics for the given woeid
    """

    local_trends = api.trends_place(id=woeid)
    # returns [{'trends': [{'name': 'TheVoice', etc}, {'name': 'KUWTK', etc.}]}]
    trend_dict_list = local_trends[0]["trends"]
    # returns [{'name': 'TheVoice', etc}, {'name': 'KUWTK', etc.}]
    trend_list = [i["name"] for i in trend_dict_list]
    # returns ['TheVoice', 'KUWTK', etc.]

    logger.debug(f"Grabbed current local trends for woeid {woeid} from twitter...")

    return trend_list


def filter_non_offensive_hashtags(trend_list):
    """
    function for filtering out non-hashtag trends
    and hashtags that could potentially be offensive or inappropriate,
    i.e. everything that starts with #rip or contains words like
    shooting, death, terror, etc. since we do not want the bot to
    make light-hearted pasta conversation about people dying, obvi.
    :param trend_list: list of current trending topics
    :return: hashtags, a list with only hashtags and offensive words removed
    """

    hashtags = [trend.lower() for trend in trend_list if trend.startswith("#")]
    og_num_of_tags = len(hashtags)

    offensive_list = ["#rip", 'shooting', 'shooter', 'dead', 'death', 'attack',
                      'kill', 'suicide', 'murder', 'terror', 'died', 'pray']

    offensive_tags = []

    for tag in offensive_list:
        for trend in hashtags:
            if tag in trend:
                offensive_tags.append(trend)

    hashtags = [tag for tag in hashtags if not tag in offensive_tags]
    logger.debug(f"{og_num_of_tags-len(hashtags)} of {og_num_of_tags} hashtags removed during offensiveness screening")

    return hashtags


def select_tweet():
    """
    :return: random tweet from tweets.txt file
    """

    with open("tweets.txt", "r") as f:
        tweet_text = random.choice(f.readlines())
        logger.debug("Selected a status message...")

    return tweet_text


def compile_status(string, trend_hashtag):

    """
    compiles status out of
    :param string: a pre-selected tweet containing the word "hashtag"
                to be substituted with the actual hashtag of a trending topic
    :param trend_hashtag: the trending hashtag inserted into the message string
    :return: status message with current trend inserted, ready to be tweeted
    """

    try:
        one, two = string.split("hashtag")
        status_message = one + trend_hashtag + two

        logger.debug(f"Compiled Tweet: {status_message}")

    except ValueError:

        logger.exception(f"I couldn't compile a status out of: {string}, {trend_hashtag}")

        date = datetime.datetime.today()
        today = datetime.datetime.strftime(date, "%B %d")
        status_message = f"As a bot, I can't do much. But I can read a calendar. " \
            f"{today}, what an amazing day to look at some pasta ..."

    return status_message


def update_status(api, media_id, message):
    """
    updates status on twitter
    :param api: api object for twitter authentication
    :param media_id: twitter media id of the file being posted
    :param message: text for the status update
    """
    try:
        api.update_status(media_ids=media_id, status=message)
        logger.info("Posted tweet & pic to twitter.")

    except tweepy.TweepError as e:
        logger.fatal(f"Tweepy error occured: {e.response.text}\n"
                     f"Could not tweet. Pls help me.")

        sys.exit()
