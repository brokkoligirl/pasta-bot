import requests
from bs4 import BeautifulSoup


page = requests.get("https://www.reddit.com/r/pasta/", headers={'User-Agent': 'imageBot'})
soup = BeautifulSoup(page.content, "html.parser")

images = soup.find_all('img')
img_srces = [image.get('src') for image in images]


cleaned_images = []
for img in img_srces:
    if "renderTimingPixel.png" not in img:
        cleaned_images.append(img)

print(cleaned_images)
