import requests
import os
import praw
import configparser
from prawcore.exceptions import ResponseException


def get_reddit_tokens():

    # reads tokens needed for accessing reddit api from config file
    # or creates a template to be filled out with the user credensh

    config = configparser.ConfigParser()
    config.read('config.ini')
    client_id = config['REDDIT']['client_id']
    client_secret = config['REDDIT']['client_secret']
    user_agent = config['REDDIT']['user_agent']

    return client_id, client_secret, user_agent


def get_image_urls(sub, amount):

    # returns a list of image urls for a specified number of the most
    # recent  submissions from a subreddit

    try:
        client_id, client_secret, user_agent = get_reddit_tokens()

        reddit = praw.Reddit(client_id=client_id,
                             client_secret=client_secret,
                             user_agent=user_agent)

        submissions = reddit.subreddit(sub).new(limit=amount)
        submission_urls = [submission.url for submission in submissions]
        image_urls = [item for item in submission_urls if item.endswith(".jpg")]

        return image_urls

    except ResponseException:

        print("Client info is wrong. Check again.")

        return 0


def get_new_file_number():
    # iterates over the image directory's consecutively numbered filenames
    # and returns the next available number so no files will be overwritten

    my_dir = os.listdir(os.getcwd())
    all_files = sorted([file for file in my_dir if file.endswith(".jpg")])
    last_file = all_files[-1].rstrip(".jpg")
    new_file_number = int(last_file[-2:]) + 1

    return new_file_number


def get_unused_pics(image_urls):
    # iterates through image list comparing the urls to the newest
    # image url from the last run and cutting off the list at the
    # index of the duplicate to only get each image once
    # then overwrite the file with the url of the first item in the new list

    newest_pic = image_urls[0]
    unused_pics = []

    try:
        with open("url_tracking.txt", "r") as f:
            last_url = f.read()
        if last_url in image_urls:
            for index, imgurl in enumerate(image_urls):
                if imgurl == last_url:
                    end_index = index  # cut-off to avoid repeat pictures in the list
                    unused_pics = image_urls[:end_index]
        else:
            unused_pics = image_urls

        if len(unused_pics) > 0:
            with open("url_tracking.txt", 'w') as f:
                f.write(unused_pics[0])
        else:
            print("No new pics found.")

    except FileNotFoundError:
        with open("url_tracking.txt", "w") as f:
            f.write(newest_pic)
        unused_pics = image_urls

    return unused_pics


def save_new_images(new_images_urls):

    try:
        new_file_number = get_new_file_number()

    except:
        print("couldn't get last file number, starting count from zero")
        new_file_number = 0

    counter = 0

    for url in new_images_urls:
        source = requests.get(url)
        if source.status_code == 200:
            img_file = f'{img_directory}-{f"{new_file_number:02d}"}.jpg'
            img_data = requests.get(url).content
            open(img_file, 'wb').write(img_data)
        else:
            print("url cannot be reached")
        counter += 1
        new_file_number += 1

    print(f"{counter} new images saved.")


if __name__ == '__main__':

    subreddit = 'pasta'
    number = 10
    img_directory = f"{subreddit}pics"

    pasta_urls = get_image_urls(subreddit, number)

    try:
        os.mkdir(img_directory)
        os.chdir(img_directory)

    except FileExistsError:
        os.chdir(img_directory)

    new_images = get_unused_pics(pasta_urls)
    save_new_images(new_images)
