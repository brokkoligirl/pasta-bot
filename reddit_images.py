import requests
import os
import praw
import configparser
from prawcore.exceptions import ResponseException
import re
import logging

logger = logging.getLogger("pastabot.reddit_images")


def get_reddit_tokens(filename="config.ini"):

    """
    grabs tokens needed for accessing reddit api from config file
    :param filename: name of config file, defaults to "config.ini"
    :return: client_id, client_secret, user_agent - credentials for accessing reddit API
    """

    config = configparser.ConfigParser()
    config.read(filename)
    client_id = config['REDDIT']['client_id']
    client_secret = config['REDDIT']['client_secret']
    user_agent = config['REDDIT']['user_agent']

    logger.debug("Grabbed reddit credensh from config file...")

    return client_id, client_secret, user_agent


def extract_image_urls(client_id, client_secret, user_agent, sub, amount):

    """
    :param client_id, client_secret, user_agent: reddit credentials for making API call
    :param sub: subreddit from which to extract the image urls
    :param amount: number of most recent submissions to parse
    :return: list of image urls
    """

    try:

        reddit = praw.Reddit(client_id=client_id,
                             client_secret=client_secret,
                             user_agent=user_agent)

        submissions = reddit.subreddit(sub).new(limit=amount)
        submission_urls = [submission.url for submission in submissions]
        image_urls = [item for item in submission_urls if item.endswith(".jpg")][::-1]  # puts newest pics last

        logger.debug(f"Succesfully grabbed image urls from r/{sub}")

        return image_urls

    except ResponseException as e:

        logger.exception("an error occured while grabbing urls from reddit: ", e,
                         "No urls were grabbed.")

        return []


def get_new_file_number():

    """
    iterates over the current directory's consecutively numbered file names
    and returns the next available number so no files will be overwritten
    """

    try:
        my_dir = os.listdir(os.getcwd())
        all_files = sorted([file for file in my_dir if file.endswith(".jpg")])
        last_file = all_files[-1]
        get_number = re.findall(r"\d+", last_file)[0]
        new_file_number = int(get_number) + 1

    except IndexError:
        new_file_number = 0

    logger.debug("Found new file number for newly grabbed pics...")

    return new_file_number


def filter_unused_pics(image_urls):

    """
    iterates through image url list comparing the urls against a tracking file
    that saves the url of the newest image each time it is run
    :return: list of new image urls that have not yet been saved to local directory
    """

    if len(image_urls) == 0:  # in case no urls were grabbed
        return []

    newest_pic = image_urls[-1]
    unused_pics = []

    try:
        with open("url_tracking.txt", "r") as f:
            last_url = f.read()

        logger.debug("reading latest url from tracking file...")

        # comparing url list with last url to avoid repeat posts
        if last_url in image_urls:
            for index, imgurl in enumerate(image_urls):
                if imgurl == last_url:
                    start_index = index + 1  # drop non-new pics from the list
                    unused_pics = image_urls[start_index:]
        else:
            unused_pics = image_urls

        # saving the last item from unused_pics as the new last file
        # so that only pics posted after that will be collected next time
        if len(unused_pics) > 0:
            with open("url_tracking.txt", 'w') as f:
                f.write(unused_pics[-1])

        else:
            logger.debug("No new pics found.")

    except FileNotFoundError: # in case there is no url tracking file yet
        with open("url_tracking.txt", "w") as f:
            f.write(newest_pic)
        unused_pics = image_urls
        logger.exception("No url tracking file found. Created one.")

    # reversing them so that the newest ones get used first
    return unused_pics[::-1]


def save_new_images(new_images_urls):
    """
    takes a list of image urls and downloads the images, saving them to
    current directory & giving the files consecutively numbered names
    """

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
            logger.debug("an image url could not be reached. "
                         "Status code was ", source.status_code)

            # TODO: save urls that couldn't be reached & try downloading again later

    logger.info(f"{counter} new images saved.")

