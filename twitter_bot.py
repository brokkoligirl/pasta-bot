import tweepy
import os

consumer_key = "QdcKh0LamPfL2ScWr10EWA1el"
consumer_secret = "7siUopf5oooJZ6KHl9Dt84XQBjIVYs2lWNsumRhAqDrp9P8Mc7"
access_token = "1141316510880870400-xvhXYgBK24b5lASdlYcJcbUBuXTfek"
access_token_secret = "p27bHEQmFA0fGxiRJb76d4ul9tsr4imcDXvR3hwuW4cbA"

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)

# api.update_status(status="I love pasta!")

os.chdir("/Users/karolin/PycharmProjects/my_project/Pastabot/pastapics/")

file = open('pastapics-2.jpg', 'rb')
r1 = api.media_upload(filename='pastapics-2.jpg', file=file)
print(r1)
print(r1.media_id_string)
media_ids = [r1.media_id_string]
print(media_ids)
api.update_status(media_ids=media_ids, status="<3")