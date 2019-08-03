import configparser
import os
import sys
import random
from contextlib import contextmanager
from time import sleep
import reddit_images as r
import tweet_compiler as t


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

        print('I have created a config.ini file for u. '
              'Please fill in ur twitter and reddit credensh to proceed.')

        sys.exit()


def get_filename_for_tweet():

    # selects the first image from sorted list of files in current directory
    try:
        directory = os.getcwd()
        my_dir = os.listdir(directory)
        all_files = sorted([file for file in my_dir if file.endswith(".jpg")])
        filename = all_files[0]

        return filename

    except IndexError:
        # if dir is empty
        print("no files in the directory. cannot tweet until new pics are available >:-(")
        sys.exit()


def remove_tweeted_image():

    # removes the image after it's been tweeted
    delete_file = get_filename_for_tweet()
    os.remove(delete_file)


@contextmanager
def change_dir(destination):
    cwd = os.getcwd()
    try:
        os.chdir(destination)
        yield
    finally:
        os.chdir(cwd)


def main():

    config_file_checker()

    subreddit = 'pasta'
    img_directory = f"{subreddit}pics"
    number_of_posts = 25
    delay = 16 * 60 * 60  # 16 hours

    consumer_key, consumer_secret, access_token, access_token_secret = t.get_twitter_tokens()

    print('trying to connect...')

    api = t.twitter_auth(consumer_key, consumer_secret, access_token, access_token_secret)

    print('Connected!')

    while True:

        if not os.path.exists(img_directory):
            os.mkdir(img_directory)

        pasta_urls = r.get_image_urls(subreddit, number_of_posts)

        with change_dir(img_directory):
            new_images = r.get_unused_pics(pasta_urls)
            r.save_new_images(new_images)

        print("Selecting a status message...")
        with open("tweets.txt", "r") as f:
            tweet_text = random.choice(f.readlines())

        print("Looking at the current trends...")
        current_us_trends = t.get_place_trends(api, 23424977)

        print("Selecting a hashtag...")
        hashtag = t.get_random_trending_hashtag(current_us_trends)

        with change_dir("pastapics"):
            print("Looking for a pic to tweet...")
            file_to_tweet = get_filename_for_tweet()

            print("Found one! Uploading it to twitter...")
            media_id = t.get_twitter_media_id(api, file_to_tweet)

            print("done. removing it from ur direc...")
            remove_tweeted_image()

        print("compiling tweet...")
        message = t.compile_status(tweet_text, hashtag)

        print("ready to tweet...")
        api.update_status(media_ids=media_id, status=message)

        print(f"Done! Sleeping for {delay/60/60} hours")
        sleep(delay)


main()