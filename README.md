In this project, I have developed a photomosaic creator program. The main goal of photomosaics is to resemble a target image using small tiles from the dataset. To achieve that, it is possible to use many different approaches such as some hierarchical approaches. My approach is to divide the target image into predefined tile size then randomly (not in order, such as bottom to top) try to find the best matches. The reason I do the matching randomly is to make sure some diversity, such as adjacent repeated texture could be matched to the same tile multiple times before it exhausts the number of uses. After the shuffle, I try to match all remaining source tiles to the target tile, where it is possible to match the source tiles for a predefined number of times. I generally kept it around 5 or less to make sure using different tiles. Moreover, after matching some tiles, we generally run out of the "good" tiles to use. To make the rest of the tiles usable, I followed two different ideas. The first one is to apply histogram matching to the source image using the target tile. It is not very aggressive unless the target tile has a repeating texture, such as a black shirt, but if the target's histogram is skewed, it makes the source's histogram very skewed too, which makes it sometimes over-aggressive. The second method I tried is to use color casting idea from the second homework, which also worked pretty well overall. To ensure further diversity, I pick K nearest tiles and choose one of them randomly. The main comparison metric that is used is Euclidean distance in average image colors, which is calculated as the mean of each R, G, B channel, then treating the triplet as a 3D point. I also tried using MSE and MAE but it is not fitting well with our purposes, as we want to capture the overall appearance as the tiles going to be very small. I also wanted to try Wasserstein distance between histograms but time did not permit for that, it would be fun to explore how the histogram difference metric behaves. 



Sometimes the histogram matching is way too aggressive, (as shown in alternative examples of set4, some images are washed out) in that case, using color casting becomes handy. In set5, this feature helped a bit, as it is sometimes hard to find images with a dominant color.



Example usage of the script:

`

python main.py --target_image ../data/windowsxp.jpeg --tile_images_folder ../data/landscapes_flicker --tile_size 12 12 --metric color_distance_faster --target_resize_factor 0.3  --output_file_name set4_mosaic --n_reuse 2  --randomize

`