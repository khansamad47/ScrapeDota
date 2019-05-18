import json
import os
import urllib.request as urlr

FILE_NAME = 'heroes_json.txt'
OUTPUT_DIR = 'hero_images'
IMAGE_EXTENSION = 'png'

def download_hero_images(file_name, output_dir):
    """
    This function downloads Dota2 images. It will download in a simple
    directory structure single serving urls should be independent on how 
    the images are locally stored
    """
    with open(file_name,'r') as json_file:
        hero_json = json.load(json_file)   
        try:
            os.mkdir(output_dir)
        except OSError:
            print ("Failed to create directory %s" % output_dir)
            return
        for hero in hero_json:
            print ("Processing %s." % hero['name'])
            hero_dir = output_dir + '/' + str(hero['hero_id'])
            os.mkdir(hero_dir)
            urlr.urlretrieve(hero['img_url'], hero_dir + '/main.' + IMAGE_EXTENSION);
            urlr.urlretrieve(hero['portrait_img_url'], hero_dir + '/portrait.' + IMAGE_EXTENSION);

            for ability in hero['abilities']:
                ability_img = hero_dir + '/ability_' + str(ability['ability_id'])  + '.' + IMAGE_EXTENSION
                urlr.urlretrieve(ability['img_url'], ability_img);


if __name__ == '__main__':
    download_hero_images(FILE_NAME, OUTPUT_DIR)
