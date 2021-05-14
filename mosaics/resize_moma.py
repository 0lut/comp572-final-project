from PIL import Image
import os


image_files = os.listdir('moma/')
image_files = [os.path.join('moma', p) for p in image_files]

for f in image_files:
    try:
        im = Image.open(f)
        im.load()
        if im.size[0] == 128:
            continue
        im = im.resize([128, 128])
        im.save(f)
    except:
        pass