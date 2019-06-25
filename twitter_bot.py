import tweepy
import configparser
import os


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


if __name__ == '__main__':

    consumer_key, consumer_secret, access_token, access_token_secret = get_twitter_tokens()

    print('trying to connect...')

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)

    print('Connected!\n')

    os.chdir('pastapics')

    file_to_tweet = get_filename_for_tweet()
    media_id = get_twitter_media_id(file_to_tweet)

    api.update_status(media_ids=media_id)

    remove_tweeted_image()



