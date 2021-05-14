import os
from PIL import Image
from sklearn.metrics import mean_squared_error, mean_absolute_error
import numpy as np
from concurrent.futures import ThreadPoolExecutor
from random import shuffle
from skimage.exposure import match_histograms


def hist_match(source, target):
    try:
        matched = match_histograms(source, target, multichannel=True).astype(np.uint8)
        matched = Image.fromarray(matched)
        return matched
    except:
        matched = Image.fromarray(source)
        return matched

def color_cast(source, target):
    try:
        source_clr = np.array([*get_color_of_tile(source)])
        target_clr = np.array([*get_color_of_tile(target)])
        ratio  = target_clr/source_clr
        return  Image.fromarray(np.clip(ratio * source, 0, 255).astype(np.uint8))
    except:
        return  Image.fromarray((source))

def get_tile_images(path_to_tile_folder, tile_size, n_to_use):
    tile_img_names = os.listdir(path_to_tile_folder)
    shuffle(tile_img_names)
    if n_to_use>0:
        tile_img_names = tile_img_names[:n_to_use]
    else:
        tile_img_names = tile_img_names

    tile_img_names = [os.path.join(path_to_tile_folder, pth) for pth in tile_img_names]
    tile_images = []

    def read_single(img_path):
        try:
            im = Image.open(img_path)
            im.load()
            im = im.resize(tile_size)
            if len(np.array(im).shape) == 2:
                return
            tile_images.append(im)
        except:
            print('Invalid image!')
        
    with ThreadPoolExecutor(16) as exc:
        list(exc.map(lambda x: read_single(x), tile_img_names))
    return tile_images

def get_color_of_tile(img):
    
    img = np.array(img)
    if len(img.shape) == 2:
        w, h = img.shape
        img_point = np.average(img.reshape(w * h, 1), axis=0)

    elif len(img.shape) == 3:
        w, h, c = img.shape
        img_point = (tuple(np.average(img.reshape(w * h, c), axis=0)))
    return img_point

def faster_color_distance(img1, img2):
    img1_point = img1.avg_color
    img2_point = img2.avg_color 
    dist = ((img1_point[0] - img2_point[0]) ** 2 +
                (img1_point[1] - img2_point[1]) ** 2 +
                (img1_point[2] - img2_point[2]) ** 2)

    return dist


def faster_color_distance_bw(img1, img2):
    img1_point = img1.avg_color
    img2_point = img2.avg_color 
    dist = (img1_point - img2_point)**2
    return dist

def color_distance_metric(img1, img2) -> float:
    # DEPRECATED 
    w, h, c = img1.shape
    img1_point = (tuple(np.average(img1.reshape(w * h, c), axis=0)))
    img2_point = (tuple(np.average(img2.reshape(w * h, c), axis=0)))

    dist = ((img1_point[0] - img2_point[0]) ** 2 +
                (img1_point[1] - img2_point[1]) ** 2 +
                (img1_point[2] - img2_point[2]) ** 2)
    return dist


def convert_tile_to_bw(tile_array):
    for ix in range(len(tile_array)):
        tile = tile_array[ix]
        tile.img = tile.img.convert('L')
        tile.as_np = np.array(tile.img)
        tile_array[ix] = tile
        tile.avg_color = get_color_of_tile(tile.img)
            
    return tile_array


def metric(img1, img2, type='mse'):
    # img1, img2 = np.array(img1), np.array(img2)


    # img1 = img1.reshape(img1.shape[0], -1)
    # img2 = img2.reshape(img2.shape[0], -1)



    metric_dict = {'mse': mse, 'l1': mae, 'color_distance': color_distance_metric, 'color_distance_faster': faster_color_distance, 'color_distance_faster_bw': faster_color_distance_bw}
    metric_fn = metric_dict.get(type, 'mse')
    return metric_fn(img1, img2)

def mse(img1, img2):
    img1 = img1.as_np
    img2 = img2.as_np
    # np.sum(mean_squared_error(img1[..., c], img2[..., c]) for c in range(3))
    return np.mean((img1.flatten() - img2.flatten())**2 )


def mae(img1, img2):
    img1 = img1.as_np
    img2 = img2.as_np

    # np.sum(mean_squared_error(img1[..., c], img2[..., c]) for c in range(3))
    return np.mean(abs(img1.flatten() - img2.flatten()) )