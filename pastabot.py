import configparser
import os
import sys
import random
import logging
import logging.config
from contextlib import contextmanager
from time import sleep
import numpy as np
import reddit_images as r
import tweet_compiler as t
import sentiments as s

logger = logging.getLogger("pastabot")


def config_file_checker():

    if not os.path.exists('config.ini'):
        config = configparser.ConfigParser()
        config['TWITTER'] = {'consumer_key': 'your consumer key here',
                             'consumer_secret': 'your consumer secret here',
                             'access_token': 'your access token here',
                             'access_token_secret': 'your access token secret here'}
        config['REDDIT'] = {'client_id': 'your client_id here',
                            'client_secret': 'your client_secret here',
                            'user_agent': 'your user_agent here'}
        with open('config.ini', 'w') as configfile:
            config.write(configfile)

        logger.info('I have created a config.ini file for u. '
                    'Please fill in ur twitter and reddit credensh to proceed.')

        sys.exit()


def get_filename_for_tweet():

    # selects the first image from sorted list of files in current directory
    try:
        directory = os.getcwd()
        my_dir = os.listdir(directory)
        all_files = sorted([file for file in my_dir if file.endswith(".jpg")])
        filename = all_files[0]

        logger.info("selected a file for tweeting.")

        return filename

    except IndexError:
        # if dir is empty
        logger.exception("no files in the directory. cannot tweet until new pics are available >:-(")

        sys.exit()


def remove_tweeted_image():

    # removes the image after it's been tweeted
    delete_file = get_filename_for_tweet()
    os.remove(delete_file)

    logger.info("removed the file that was just tweeted.")


@contextmanager
def change_dir(destination):
    cwd = os.getcwd()
    try:
        os.chdir(destination)
        yield
    finally:
        os.chdir(cwd)


def main():

    logging.config.fileConfig('logging.conf')
    logger = logging.getLogger("pastabot")
    logger.info("Program started!")

    config_file_checker()

    subreddit = 'pasta'
    img_directory = f"{subreddit}pics"
    number_of_posts = 25
    delay = 16 * 60 * 60  # 16 hours
    num_of_tweets = 80

    consumer_key, consumer_secret, access_token, access_token_secret = t.get_twitter_tokens()

    logger.info('trying to connect to twitter...')

    api = t.twitter_auth(consumer_key, consumer_secret, access_token, access_token_secret)

    logger.info('Connected!')

    while True:

        if not os.path.exists(img_directory):
            os.mkdir(img_directory)

        pasta_urls = r.get_image_urls(subreddit, number_of_posts)

        with change_dir(img_directory):
            new_images = r.get_unused_pics(pasta_urls)
            r.save_new_images(new_images)

        current_us_trends = t.get_local_trends(api, 23424977)

        hashtags = t.non_offensive_hashtags(current_us_trends)

        # inserting this loop for the highly unlikely case that ALL current trends
        # are filtered out because they all contain one of the words we labeled inaprop for our bot
        while not hashtags:
            logger.info("All the trends seem kind of inapprope rn..."
                        "gonna sleep for a while until better topics come along.")
            sleep(2*60*60)
            current_us_trends = t.get_local_trends(api, 23424977)
            hashtags = t.non_offensive_hashtags(current_us_trends)

        # filtering out hashtags with tweets that have an avg polarity <0.1
        sentiment = 0
        while sentiment < 0.1:

            hashtag = random.choice(hashtags)
            logging.info(f"Selected hashtag: {hashtag}")

            # analyzing sentiments ...
            logging.info("analyzing sentiments...")
            tweet_list = s.grab_trending_tweets_tweepy(hashtag, num_of_tweets, api=api)
            og_sentiments = s.analyze_tweet_list(tweet_list)

            # cleaning the tweets we grabbed to see how that changes the sentiment
            first_cleanse = [s.tweet_cleaner(tweet) for tweet in tweet_list]
            lemmatized_tweets = [s.tokenize_lemmatize(tweet) for tweet in first_cleanse]
            no_stopwords = [s.remove_stopwords(tweet) for tweet in lemmatized_tweets]

            cleaned_tweets = [" ".join(tweet) for tweet in no_stopwords]
            # rejoining lemmatized tweets into single strings for textblob
            clean_sentiments = s.analyze_tweet_list(cleaned_tweets)

            logging.info(f"Looked at {num_of_tweets} tweets about {hashtag}. "
                         f"mean sentiment before cleaning: {np.mean(og_sentiments)},"
                         f"mean sentiment after cleaning: {np.mean(clean_sentiments)}")

            sentiment = 0.5 * (np.mean(og_sentiments) + np.mean(clean_sentiments))

        with open("tweets.txt", "r") as f:
            tweet_text = random.choice(f.readlines())
            logger.info("Selected a status message...")

        with change_dir(img_directory):
            file_to_tweet = get_filename_for_tweet()
            media_id = t.get_twitter_media_id(api, file_to_tweet)
            message = t.compile_status(tweet_text, hashtag)
            t.update_status(api, media_id, message)

            remove_tweeted_image()

        logger.info(f"Done! Sleeping for {delay/60/60} hours")
        sleep(delay)


main()
