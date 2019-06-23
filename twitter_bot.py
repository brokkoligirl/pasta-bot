import tweepy
import os
import configparser

def get_tokens():
    config = configparser.ConfigParser()
    config.read('config.ini')
    consumer_key = config['TWITTER']['consumer_key']
    consumer_secret = config['TWITTER']['consumer_secret']
    access_token = config['TWITTER']['access_token']
    access_token_secret = config['TWITTER']['access_token_secret']
    return consumer_key, consumer_secret, access_token, access_token_secret


consumer_key, consumer_secret, access_token, access_token_secret = get_tokens()

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)

api.update_status(status="I loove pasta!")

# os.chdir("/Users/karolin/PycharmProjects/my_project/Pastabot/pastapics/")
#
# file = open('pastapics-2.jpg', 'rb')
# r1 = api.media_upload(filename='pastapics-2.jpg', file=file)
# print(r1)
# print(r1.media_id_string)
# media_ids = [r1.media_id_string]
# print(media_ids)
# api.update_status(media_ids=media_ids, status="<3")