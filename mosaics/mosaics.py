from collections import Counter
import numpy as np
from PIL import Image
from utils import metric, get_color_of_tile, convert_tile_to_bw, hist_match, color_cast
from random import choice, shuffle, seed, randint
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

class Tile:
    def __init__(self, img, coor, avg_color=None):
        self.img = img
        self.coor = coor
        self.avg_color = avg_color
        self.as_np = np.array(img)

class Mosaic:
    def __init__(self, target_img, source_tiles, tile_size, reuse_count=float('inf'), metric_type='color_distance', randomize=False, bw=False, color_scale=False):
        self.target_img = target_img
        self.reuse_count = reuse_count
        self.source_tiles = source_tiles
        self.tile_size = tile_size
        self.randomize = randomize
        self.target_tiles = []
        self.bw = bw
        self.color_scale = color_scale
        self._get_target_tiles()
        self._process_source_tiles()
        shuffle(self.target_tiles)
        shuffle(self.source_tiles)
        self.tile_use_count = Counter(range(len(self.source_tiles)))
        if bw:
            self.target_tiles = convert_tile_to_bw(self.target_tiles)
            self.source_tiles = convert_tile_to_bw(self.source_tiles)

        self.metric = lambda img1, img2: metric(img1, img2, metric_type)
        print(len(self.target_tiles), len(self.source_tiles))


    def _process_source_tiles(self):
        processed_tiles = []
        for source_img in self.source_tiles:
            avg_color = get_color_of_tile(source_img)
            tile = Tile(source_img, None, avg_color)
            processed_tiles.append(tile)
        
        self.source_tiles = processed_tiles



    def _get_target_tiles(self):
        W, H = self.target_img.size

        W_tile, H_tile = self.tile_size
        M, N = int(W / W_tile), int(H / H_tile)

        for i in range(M):
            for j in range(N):
                img = self.target_img.crop((i * W_tile, j * H_tile, (i + 1) * W_tile, (j + 1) * H_tile))
                avg_color = get_color_of_tile(img)
                tile = Tile(img, (i * W_tile, j * H_tile, (i + 1) * W_tile, (j + 1) * H_tile), avg_color)

                self.target_tiles.append(tile)


    def create(self):
        matched_tiles = []
        if not self.randomize and not self.color_scale:
            with ThreadPoolExecutor(8) as exc:
                matched_tiles = list(exc.map(lambda target_tile: self.get_closest_tile(target_tile), self.target_tiles))
        elif self.randomize:
            with ThreadPoolExecutor(8) as exc:
                matched_tiles = list(exc.map(lambda target_tile: self.get_closest_tile_randomized(target_tile), self.target_tiles))
        elif self.color_scale:
            with ThreadPoolExecutor(8) as exc:
                matched_tiles = list(exc.map(lambda target_tile: self.get_closest_tile_randomized_colorcast(target_tile), self.target_tiles))


        if self.bw:
            mosaic = Image.new('L', self.target_img.size)
        else:
            mosaic = Image.new('RGB', self.target_img.size)
        # for i in :
        with ThreadPoolExecutor(8) as exc:
            list(exc.map(lambda i: mosaic.paste(matched_tiles[i].img, matched_tiles[i].coor), range(len(matched_tiles))))

        return mosaic   



    def get_closest_tile(self, target_tile):
        
        target_tile_img = target_tile
        target_tile_coor = target_tile.coor
        min_dist = self.metric(target_tile_img, self.source_tiles[0])
        best_match = self.source_tiles[0]
        best_match_ix = 0
        for ix, source_tile in enumerate(self.source_tiles):
            # try:
            curr_dist = self.metric(target_tile_img, source_tile)
        
            if curr_dist < min_dist and self.tile_use_count[ix] < self.reuse_count:
                best_match = source_tile
                min_dist = curr_dist
                best_match_ix = ix
            # except:
                # pass
        self.tile_use_count[best_match_ix] += 1
        return Tile(best_match.img, target_tile_coor)
        
            
    def get_closest_tile_randomized(self, target_tile):

        surrogate_tiles = []
        target_tile_img = target_tile
        target_tile_coor = target_tile.coor
        min_dist = self.metric(target_tile_img, self.source_tiles[0])
        best_match = self.source_tiles[0]
        best_match_ix = 0
        # surrogate_tiles.append({'sim': min_dist, 'ix': best_match_ix, 'tile':best_match, 'coor': target_tile_coor})
        for ix, source_tile in enumerate(self.source_tiles):
            # try:
            curr_dist = self.metric(target_tile_img, source_tile)
        
            if curr_dist < min_dist and self.tile_use_count[ix] < self.reuse_count:
                best_match = source_tile
                min_dist = curr_dist
                best_match_ix = ix
                surrogate_tiles.append({'sim': min_dist, 'ix': best_match_ix, 'tile':best_match})

            # except:
                # pass
        # surrogate_tiles = sorted(surrogate_tiles, key=lambda d: d['sim'])[:5]  ataturk
        surrogate_tiles = sorted(surrogate_tiles, key=lambda d: d['sim'])[:8]
        try:
            matched_tile_d = choice(surrogate_tiles)
        except:

            best_match_ix = randint(0, len(self.source_tiles)-1)
            matched_tile_d = {'ix': best_match_ix, 'tile':self.source_tiles[best_match_ix], 'sim':self.metric(target_tile_img, self.source_tiles[best_match_ix])}
            matched_tile_d['tile'].img = hist_match(matched_tile_d['tile'].as_np, target_tile.as_np)
        if matched_tile_d['sim']>5900:
            matched_tile_d['tile'].img = hist_match(matched_tile_d['tile'].as_np, target_tile.as_np)

        best_match_ix = matched_tile_d['ix']
        best_match = matched_tile_d['tile']
        self.tile_use_count[best_match_ix] += 1

        return Tile(best_match.img, target_tile_coor)

    def get_closest_tile_randomized_colorcast(self, target_tile):

        surrogate_tiles = []
        target_tile_img = target_tile
        target_tile_coor = target_tile.coor
        min_dist = self.metric(target_tile_img, self.source_tiles[0])
        best_match = self.source_tiles[0]
        best_match_ix = 0
        # surrogate_tiles.append({'sim': min_dist, 'ix': best_match_ix, 'tile':best_match, 'coor': target_tile_coor})
        for ix, source_tile in enumerate(self.source_tiles):
            # try:
            curr_dist = self.metric(target_tile_img, source_tile)
        
            if curr_dist < min_dist and self.tile_use_count[ix] < self.reuse_count:
                best_match = source_tile
                min_dist = curr_dist
                best_match_ix = ix
                surrogate_tiles.append({'sim': min_dist, 'ix': best_match_ix, 'tile':best_match})

            # except:
                # pass
        # surrogate_tiles = sorted(surrogate_tiles, key=lambda d: d['sim'])[:5]  ataturk
        surrogate_tiles = sorted(surrogate_tiles, key=lambda d: d['sim'])[:5]
        try:
            matched_tile_d = choice(surrogate_tiles)
        except:

            best_match_ix = randint(0, len(self.source_tiles)-1)
            matched_tile_d = {'ix': best_match_ix, 'tile':self.source_tiles[best_match_ix], 'sim':self.metric(target_tile_img, self.source_tiles[best_match_ix])}
            # matched_tile_d['tile'].img = color_cast(matched_tile_d['tile'].as_np, target_tile.as_np)
        # if matched_tile_d['sim']>1900:
        matched_tile_d['tile'].img = color_cast(matched_tile_d['tile'].as_np, target_tile.as_np)

        best_match_ix = matched_tile_d['ix']
        best_match = matched_tile_d['tile']
        self.tile_use_count[best_match_ix] += 1

        return Tile(best_match.img, target_tile_coor)




