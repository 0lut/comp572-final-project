import flickrapi
import urllib
from PIL import Image
from concurrent.futures import ThreadPoolExecutor
import argparse
import os

parser = argparse.ArgumentParser(description='Flickr photo download script')
parser.add_argument("--tag", required=True, help='The tag to download from')
parser.add_argument("--resize", action='store_true')
parser.add_argument("--resized_size", help='resized size, it will make image square regardless')
parser.add_argument('--folder_to_save', help='Directory to save the downloads')
parser.add_argument('--n', default=300, type=int, help='Number of images to download')



args = parser.parse_args()

os.makedirs(args.folder_to_save, exist_ok=True)


API_KEY = '3412b9ead19eec82de74d538904144fa'
API_SECRET = '4547e85511cb128c'

flickr = flickrapi.FlickrAPI(API_KEY, API_SECRET)



print(args.tag)
photos = flickr.walk(text=args.tag,
                     tag_mode='all',
                     tags=args.tag,
                     extras='url_c',
                     per_page=100,           # may be you can try different numbers..
                     sort='relevance')

print(photos)
urls = []
ix = 0
for photo in photos:
    ix += 1
    url = photo.get('url_c')
    if url is not None:
        urls.append(url)
    if ix > args.n:
        break
    
    
with ThreadPoolExecutor(10) as p:
    list(p.map(lambda tup: urllib.request.urlretrieve(tup[0], '{}/000{}.jpg'.format(args.folder_to_save, tup[1])), zip(urls, range(len(urls)))))

# for ix, url in  enumerate(urls):
#     print(ix, url)
#     urllib.request.urlretrieve(url, '{}/000{}.jpg'.format(args.folder_to_save, ix))


# # Resize the image and overwrite it
# image = Image.open('00001.jpg') 
# image = image.resize((256, 256), Image.ANTIALIAS)
# image.save('00001.jpg')