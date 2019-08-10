#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import math
import numpy as np
from PIL import Image, ImageFilter


FADE_FACTOR = np.linspace(0, 1, 100, endpoint=True)
FADE_FACTOR_REVERSE = np.linspace(1, 0, 100, endpoint=True)


class MyImage(object):

    def __init__(self, img_path):
        self.img_path = img_path

    def adjust(self, width, height, radius):
        img_obj = Image.open(self.img_path)
        img_width = img_obj.size[0]
        img_height = img_obj.size[1]
        ratio = width / height
        ratio_ori = img_width / img_height

        if ratio_ori == ratio:
            img_obj.resize((width, height))
            self._save(img_obj)
            return

        if ratio_ori > ratio:
            crop_width = int(ratio * img_height)
            crop_height = img_height
            x_1 = (img_width - crop_width) // 2
            y_1 = 0
            x_2 = x_1 + crop_width
            y_2 = img_height
        else:
            crop_width = img_width
            crop_height = int(img_width / ratio)
            x_1 = 0
            y_1 = (img_height - crop_height) // 2
            x_2 = img_width
            y_2 = y_1 + crop_height
        img_obj = img_obj.crop((x_1, y_1, x_2, y_2))
        img_obj = img_obj.resize((width, height), Image.ANTIALIAS)
        img_obj = img_obj.filter(BlurFilter(radius=radius))

        # add cover
        cover_obj = Image.open(self.img_path)
        if ratio_ori > ratio:
            cover_obj = cover_obj.resize(width, int(width / ratio_ori))
        else:
            cover_obj = cover_obj.resize((int(height * ratio_ori), height))
        mask = np.ones((cover_obj.size[1], cover_obj.size[0])) * 255
        fadeLen = len(FADE_FACTOR)

        # mask
        if ratio_ori > ratio:
            mask = mask.T
        mask[:, :fadeLen] = mask[:, :fadeLen] * FADE_FACTOR
        mask[:, -fadeLen:] = mask[:, -fadeLen:] * FADE_FACTOR_REVERSE
        # 此将数组转成 np.uint8 非常重要，否则无法将数组转成合格的图片
        mask = mask.astype(np.uint8)
        if ratio_ori > ratio:
            mask = mask.T

        cover_blur_obj = cover_obj.filter(BlurFilter(radius=radius))
        cover_blur_obj.paste(cover_blur_obj, (0, 0), mask=Image.fromarray(mask))
        if ratio_ori > ratio:
            img_obj.paste(cover_blur_obj, (0, (height - int(width / ratio_ori)) // 2), mask=Image.fromarray(mask))
        else:
            img_obj.paste(cover_obj, ((width - int(height * ratio_ori)) // 2, 0), mask=Image.fromarray(mask))
        self._save(img_obj)

    def _save(self, img_obj):
        img_path_ = self.img_path.split('/')
        img_path_[-1] = 'c_' + img_path_[-1]
        img_obj.save('/'.join(img_path_).replace('.jpg', '.png'), quality=100)


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
