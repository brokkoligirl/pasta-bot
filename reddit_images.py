import requests
import os
import praw
import configparser
from prawcore.exceptions import ResponseException
import re
import sys


def get_reddit_tokens():

    # reads tokens needed for accessing reddit api from config file

    config = configparser.ConfigParser()
    config.read('config.ini')
    client_id = config['REDDIT']['client_id']
    client_secret = config['REDDIT']['client_secret']
    user_agent = config['REDDIT']['user_agent']

    return client_id, client_secret, user_agent


def get_image_urls(sub, amount):

    # returns a list of image urls for (amount) of the most
    # recent submissions from a subreddit

    try:
        client_id, client_secret, user_agent = get_reddit_tokens()

        reddit = praw.Reddit(client_id=client_id,
                             client_secret=client_secret,
                             user_agent=user_agent)

        submissions = reddit.subreddit(sub).new(limit=amount)
        submission_urls = [submission.url for submission in submissions]
        image_urls = [item for item in submission_urls if item.endswith(".jpg")][::-1]  # puts newest pics last

        return image_urls

    except ResponseException as e:

        print(e)

        return []


def get_new_file_number():

    # iterates over the image directory's consecutively numbered file names
    # and returns the next available number so no files will be overwritten

    try:
        my_dir = os.listdir(os.getcwd())
        all_files = sorted([file for file in my_dir if file.endswith(".jpg")])
        last_file = all_files[-1]
        get_number = re.findall(r"\d+", last_file)[0]
        new_file_number = int(get_number) + 1

    except IndexError:
        new_file_number = 0

    return new_file_number


def get_unused_pics(image_urls):

    # iterates through image url list comparing the urls against a tracking file
    # that saves the url of the newest image each time it is run

    if len(image_urls) == 0:
        print("could not grab urls >:-(")
        sys.exit()

    newest_pic = image_urls[-1]
    unused_pics = []

    try:
        with open("url_tracking.txt", "r") as f:
            last_url = f.read()

        # comparing url list with last url to avoid repeat posts
        if last_url in image_urls:
            for index, imgurl in enumerate(image_urls):
                if imgurl == last_url:
                    start_index = index + 1  # drop non-new pics from the list
                    unused_pics = image_urls[start_index:]
        else:
            unused_pics = image_urls

        # saving the last item from unused_pics as the new last file
        # so that only pics posted after it will be collected next time
        if len(unused_pics) > 0:
            with open("url_tracking.txt", 'w') as f:
                f.write(unused_pics[-1])

        else:
            print("No new pics found.")

    except FileNotFoundError:
        with open("url_tracking.txt", "w") as f:
            f.write(newest_pic)
        unused_pics = image_urls

    # reversing them so that the newest ones get used first
    return unused_pics[::-1]


def save_new_images(new_images_urls):

    new_file_number = get_new_file_number()

    counter = 0

    for url in new_images_urls:
        source = requests.get(url)
        if source.status_code == 200:
            img_file = f'pastapics-{new_file_number+counter:04d}.jpg'
            img_data = requests.get(url).content
            open(img_file, 'wb').write(img_data)
            counter += 1
        else:
            print("image url cannot be reached rn")

    print(f"{counter} new images saved.")

