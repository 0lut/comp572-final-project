import argparse
from utils import get_tile_images
from PIL import Image
from mosaics import Mosaic
from random import seed


parser = argparse.ArgumentParser(description='PhotoMosaics Sahin Olut')
parser.add_argument('--target_image', required=True, help="Path to target image")
parser.add_argument('--tile_images_folder', nargs=1, required=True, help="Path to folder for tile images")
parser.add_argument('--tile_size', nargs=2, required=True, help="Size tiles")
parser.add_argument('--metric', required=False, default='color_distance', help='mse, color_distance, emd, l1, ncc')
parser.add_argument('--n_reuse', required=False, default=float('inf'), type=int, help='Number of reuses for a tile')
parser.add_argument('--randomize', action='store_true')
parser.add_argument('--target_resize_factor', default=1.0, type=float)
parser.add_argument('--output_file_name',type=str)
parser.add_argument('--bw', action='store_true')
parser.add_argument('--color_scale', action='store_true')

parser.add_argument('--n_source_to_use', default=0, type=int)


args = parser.parse_args()
seed(231773)

args.tile_size = list(map(int, args.tile_size))
print(args.tile_images_folder)
source_tiles = get_tile_images(args.tile_images_folder[0], args.tile_size, args.n_source_to_use)
# for folder in args.tile_images_folder:
    # source_tiles.extend(get_tile_images(folder, args.tile_size))
# source_tiles = get_tile_images(args.tile_images_folder, args.tile_size)
target_img = Image.open(args.target_image)
target_img = target_img.resize([int(target_img.size[0]*args.target_resize_factor), int(target_img.size[1]*args.target_resize_factor)])
target_img.load()
m = Mosaic(target_img, source_tiles, args.tile_size, args.n_reuse, args.metric, args.randomize, args.bw, args.color_scale)
m.create().save("{}.jpeg".format(args.output_file_name))