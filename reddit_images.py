import requests
from bs4 import BeautifulSoup
import os


def get_new_file_number():

    # iterates through the image directory's consecutively numbered filenames
    # and returns the next available number so no files will be overwritten

    path = os.getcwd()

    for root, dirs, files in os.walk(path):
        my_files = sorted([fi for fi in files if fi.endswith(".jpg")])
        raw_name = my_files[-1].rstrip(".jpg")
        file_number = int(raw_name[-1]) + 1

    return file_number


def get_sub_images(url):

    # takes subreddit name as argument
    r_url = f'https://www.reddit.com/r/{url}/new/'

    page = requests.get(r_url, headers={'User-Agent': 'imageBot'})
    soup = BeautifulSoup(page.text, "html.parser")

    # saves als img urls in a list and throws out random reddit pixels

    images = soup.find_all('img')
    unclean_img_srces = [image.get('src') for image in images]
    img_srces = [x for x in unclean_img_srces if x is not None]

    image_urls = [i for i in img_srces if "renderTimingPixel.png" not in i]

    # changes cwd to new directory (or creates it first)

    img_directory = f"{url}pics"

    try:
        os.mkdir(img_directory)
        os.chdir(img_directory)

    except FileExistsError:
        os.chdir(img_directory)

    # iterating through the image list and comparing the urls to the newest
    # image url from the last run and cutting off the list at the
    # index of the duplicate to only get each image once
    # then overwrite the file with the url of the first item in the new list

    newest_pic = image_urls[0]
    unused_pics = []

    try:
        with open("url_tracking.txt", "r") as f:
            last_url = f.read()
        for index, imgurl in enumerate(image_urls):
            if imgurl == last_url:
                end_index = index       # end_index darf nicht mit eingeschlossen sein
                unused_pics = image_urls[:end_index]
                if len(unused_pics) > 0:
                    with open("url_tracking.txt", 'w') as f:
                        f.write(unused_pics[0])
                else:
                    return "No new pics found."

    except FileNotFoundError:
        with open("url_tracking.txt", "w") as f:
            f.write(newest_pic)
        unused_pics = image_urls

    try:
        new_file_number = get_new_file_number()
        print(new_file_number)

    except:
        print("couldn't get last file number")
        new_file_number = 0

    counter = 0

    for url in unused_pics:
        source = requests.get(url)
        if source.status_code == 200:
            img_file = f'{img_directory}-{new_file_number}.jpg'
            img_data = requests.get(url).content
            open(img_file, 'wb').write(img_data)
        else:
            return "url cannot be reached"
        counter += 1
        new_file_number +=1

    return f"{counter} new images saved."


print(get_sub_images("pasta"))
