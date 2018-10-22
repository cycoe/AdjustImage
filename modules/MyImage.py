#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import math
from PIL import Image, ImageFilter

class MyImage(object):

    def __init__(self, img_path):
        self.img_path = img_path

    def adjust(self, width, height, radius):
        img_obj = Image.open(self.img_path)
        img_width = img_obj.size[0]
        img_height = img_obj.size[1]
        ratio = width / height
        ratio_ori = img_width / img_height
        if ratio_ori > ratio:
            new_width = int(ratio * img_height)
            new_height = img_height
            x_1 = (img_width - new_width) // 2
            y_1 = 0
            x_2 = x_1 + new_width
            y_2 = img_height
            new_height = int(img_width / new_width * img_height)
            new_width = img_width
        else:
            new_width = img_width
            new_height = int(img_width / ratio)
            x_1 = 0
            y_1 = (img_height - new_height) // 2
            x_2 = img_width
            y_2 = y_1 + new_height
            new_width = int(img_height / new_height * img_width)
            new_height = img_height
        img_obj = img_obj.crop((x_1, y_1, x_2, y_2))
        img_obj = img_obj.resize((new_width, new_height), Image.ANTIALIAS)
        img_obj = img_obj.filter(BlurFilter(radius=radius))

        cover_obj = Image.open(self.img_path)

        if ratio_ori > ratio:
            # cover_obj = cover_obj.resize((new_width, int(new_width / ratio_ori)))
            img_obj.paste(cover_obj, (0, (new_height - img_height) // 2))
        else:
            # cover_obj = cover_obj.resize((int(new_height * ratio_ori), new_height))
            img_obj.paste(cover_obj, ((new_width - img_width) // 2, 0))
        img_path_ = self.img_path.split(os.sep)
        img_path_[-1] = 'c_' + img_path_[-1]
        img_obj.save(os.sep.join(img_path_), quality=100)

class BlurFilter(ImageFilter.Filter):

    def __init__(self, radius=5, bounds=None):
        self.radius = radius
        self.bounds = bounds

    def filter(self, image):
        if self.bounds:
            clips = image.crop(self.bounds).gaussian_blur(self.radius)
            image.paste(clips, self.bounds)
            return image
        else:
            return image.gaussian_blur(self.radius)


if __name__ == "__main__":
    main()
