import os
import platform
from selenium import webdriver
from selenium.webdriver.common.by import By
import requests
import time
import exiftool
wd = webdriver.Firefox()


def get_images_from_google(wd, delay):
    url = "http://127.0.0.1:5000/about"
    wd.get(url)
    time.sleep(delay)
    image_urls = set()
    images = wd.find_elements(
        By.TAG_NAME, "img")

    for image in images:
        if image.get_attribute('src'):
            print(image.get_attribute('src'))
            if image.get_attribute('src') in image_urls:
                break

            if image.get_attribute('src') and 'http' in image.get_attribute('src'):
                image_urls.add(image.get_attribute('src'))
                print(f"Found {len(image_urls)}")
    return image_urls


def download_image(download_path, url, file_name):
    try:
        image_content = requests.get(url).content
        with open(f'{download_path}{file_name}', "wb") as img_file:
            img_file.write(image_content)
        print("Success")
    except Exception as e:
        print('FAILED -', e)


urls = get_images_from_google(wd, 5)

folder = f'{os.path.join(os.path.dirname(__file__))}/Images/'

for i, url in enumerate(urls):
    download_image(
        folder, url, str(i) + ".jpg")

wd.quit()

if platform.system() == 'Windows':
    with exiftool.ExifToolHelper(executable=f'{os.path.join(os.path.dirname(__file__))}/ExifTool/exiftool.exe') as et:
        for image in os.listdir(folder):
            image_path = os.path.join(folder, image)
            metadata = et.get_metadata(image_path)
            for key, value in metadata[0].items():
                print(f"{key}: {value}")
                if "License" in key:
                    if "BY" in value or "NC" in value or "ND" in value or "Do Not Train" in value:
                        print("-----")
                        print("Image is licensed for AI use an will be deleted")
                        print("-----")
                        os.remove(image_path)
                        break
else:
    with exiftool.ExifToolHelper(executable=f'{os.path.join(os.path.dirname(__file__))}/ExifTool/Perl_ExifTool/exiftool') as et:
        for image in os.listdir(folder):
            image_path = os.path.join(folder, image)
            metadata = et.get_metadata(image_path)
            for key, value in metadata[0].items():
                print(f"{key}: {value}")
                if "License" in key:
                    if "BY" in value or "NC" in value or "ND" in value or "Do Not Train" in value:
                        print("-----")
                        print("Image is licensed for AI use an will be deleted")
                        print("-----")
                        os.remove(image_path)
                        break
