import configparser
import os
import sys
import random
import logging
import logging.config
from contextlib import contextmanager
from time import sleep
import numpy as np
import reddit_images as reddit
import tweet_compiler as twitter
import sentiments

logger = logging.getLogger("pastabot")
logging.config.fileConfig('logging.conf')


def check_config_file(filename='config.ini'):
    """
    checks if config.ini file exists and creates a template config file if not
    :param filename: filename of config file that is returned
    :return:
    """

    if not os.path.exists(filename):
        config = configparser.ConfigParser()
        config['TWITTER'] = {'consumer_key': 'your consumer key here',
                             'consumer_secret': 'your consumer secret here',
                             'access_token': 'your access token here',
                             'access_token_secret': 'your access token secret here'}
        config['REDDIT'] = {'client_id': 'your client_id here',
                            'client_secret': 'your client_secret here',
                            'user_agent': 'your user_agent here'}
        with open(filename, 'w') as configfile:
            config.write(configfile)

        logger.info('I have created a config.ini file for u. '
                    'Please fill in ur twitter and reddit credensh to proceed.')

        sys.exit()


def get_filename_for_tweet():
    """
    :return: first image in current directory of ordered img files
    """

    try:
        directory = os.getcwd()
        my_dir = os.listdir(directory)
        all_files = sorted([file for file in my_dir if file.endswith(".jpg")])
        filename = all_files[0]

        logger.debug("selected a file for tweeting.")

        return filename

    except IndexError:
        # if dir is empty
        logger.fatal("no files in the directory. cannot tweet until new pics are available >:-(")

        # TODO: wait instead of exit

        sys.exit()


def remove_tweeted_image():
    """
    funtion for removing image that has been tweeted
    calls get_filename_for_tweet() and deletes the returned file
    """
    delete_file = get_filename_for_tweet()
    os.remove(delete_file)

    logger.debug("removed the file that was just tweeted.")


@contextmanager
def change_dir(destination):
    cwd = os.getcwd()
    try:
        os.chdir(destination)
        yield
    finally:
        os.chdir(cwd)


def main():

    logger.info("Program started!")
    check_config_file()

    subreddit = 'pasta'
    img_directory = f"{subreddit}pics"
    number_of_posts = 25
    delay = random.randrange(12, 18) * 60 * 60  # 12-18 hours
    num_of_tweets = 80

    # grabbing API credentials
    consumer_key, consumer_secret, access_token, access_token_secret = twitter.get_twitter_tokens()
    client_id, client_secret, user_agent = reddit.get_reddit_tokens()

    logger.debug('trying to connect to twitter...')

    api = twitter.twitter_auth(consumer_key, consumer_secret, access_token, access_token_secret)

    logger.info('Connected to twitter!')

    while True:

        if not os.path.exists(img_directory):
            os.mkdir(img_directory)

        pasta_urls = reddit.extract_image_urls(client_id, client_secret, user_agent,
                                               subreddit, number_of_posts)

        with change_dir(img_directory):
            new_images = reddit.filter_unused_pics(pasta_urls)
            reddit.save_new_images(new_images)

        current_us_trends = twitter.get_local_trends(api, 23424977)

        hashtags = twitter.filter_non_offensive_hashtags(current_us_trends)

        # inserting this loop for the highly unlikely case that ALL current trends
        # are filtered out because they all contain words labeled inappropriate for our bot
        while not hashtags:
            logger.info("All the trends seem kind of inapprope rn..."
                        "gonna sleep for a while until better topics come along.")
            sleep(2*60*60)
            current_us_trends = twitter.get_local_trends(api, 23424977)
            hashtags = twitter.filter_non_offensive_hashtags(current_us_trends)

        # filtering out hashtags with tweets that have an avg polarity <0.1
        sentiment = 0
        while sentiment < 0.1:

            hashtag = random.choice(hashtags)
            logging.debug(f"Selected hashtag: {hashtag}")

            # analyzing sentiments
            logging.debug("analyzing sentiments...")
            tweet_list = sentiments.grab_trending_tweets(api, hashtag, num_of_tweets)
            og_sentiments = sentiments.analyze_tweet_list(tweet_list)

            # cleaning the tweets we grabbed to see how that changes the sentiment
            first_cleanse = [sentiments.cleanse_tweet(tweet) for tweet in tweet_list]
            lemmatized_tweets = [sentiments.tokenize_lemmatize_tweet(tweet) for tweet in first_cleanse]
            no_stopwords = [sentiments.remove_stopwords(tweet) for tweet in lemmatized_tweets]

            # rejoining lemmatized tweets into single strings for textblob
            cleaned_tweets = [" ".join(tweet) for tweet in no_stopwords]

            clean_sentiments = sentiments.analyze_tweet_list(cleaned_tweets)

            logging.debug(f"Looked at {num_of_tweets} tweets about {hashtag}. "
                          f"mean sentiment before cleaning: {np.mean(og_sentiments)},"
                          f"mean sentiment after cleaning: {np.mean(clean_sentiments)}")

            # TODO: save topics, tweets and sentiments to sql db to improve sentiment analysis
            # using the avg of both (cleaned and uncleaned) sentiments for now
            sentiment = 0.5 * (np.mean(og_sentiments) + np.mean(clean_sentiments))

        tweet_text = twitter.select_tweet()

        with change_dir(img_directory):
            file_to_tweet = get_filename_for_tweet()
            media_id = twitter.get_twitter_media_id(api, file_to_tweet)
            message = twitter.compile_status(tweet_text, hashtag)
            twitter.update_status(api, media_id, message)

            remove_tweeted_image()

        logger.info(f"Done! Sleeping for {delay/60/60} hours")
        sleep(delay)


if __name__ == '__main__':

    main()

