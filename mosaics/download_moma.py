# https://collectionapi.metmuseum.org/public/collection/v1/search?q=%22%22&hasImages=true

import json
import requests
import os 
import urllib
from concurrent.futures import ThreadPoolExecutor


os.makedirs('moma', exist_ok=True)
objectIDs = None
with open('../data/moma.json') as f:
    objectIDs = json.load(f)['objectIDs']


def download( objectID):
    try:
        link = "https://collectionapi.metmuseum.org/public/collection/v1/objects/{}".format(objectID)
        response = requests.get(link)
        response = response.json()
        image_link = response['primaryImage']
        urllib.request.urlretrieve(image_link, 'moma/{}.jpg'.format(objectID))
    except:
        print("error occured on {}".format(objectID))

with ThreadPoolExecutor(8) as exc:
    list(exc.map(lambda x: download(x),objectIDs))
