from urllib.request import parse_http_list
import imageio
import argparse
import os
from concurrent.futures import ThreadPoolExecutor

parser = argparse.ArgumentParser(description='Video to frames splitting script')


parser.add_argument("--resized_size", help='resized size, it will make image square regardless')
parser.add_argument("--path_to_video", help="path to video to be splitted")
parser.add_argument('--folder_to_save', help='Directory to save the frames')
parser.add_argument('--sampling_rate', default=100, type=int, help='Sampling rate for each second (default is 3 frames per second)')


args = parser.parse_args()

os.makedirs(os.path.join(args.folder_to_save, 'frames'), exist_ok=True)


reader = imageio.get_reader('{}'.format(args.path_to_video))


with ThreadPoolExecutor(8) as exc:
    list(exc.map(lambda tup: imageio.imwrite('{}.jpg'.format(os.path.join(args.folder_to_save, 'frames', 'trailer4_'+str(tup[0]))), tup[1]) if tup[0] % args.sampling_rate == 0  else None, enumerate(reader)))




print('A total number of {} frames are saved!'.format(len(os.listdir(os.path.join(args.folder_to_save, 'frames')))))

# for frame_number, im in enumerate(reader):
#     # im is numpy array
#     # if frame_number % 60/args.sampling_rate == 0:
#     if frame_number % 60 == 0:
#         imageio.imwrite('{}.jpg'.format(os.path.join(args.folder_to_save, 'frames', str(frame_number))), im)
