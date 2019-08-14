#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import math
import numpy as np
from PIL import Image, ImageFilter
from PyQt5.QtCore import QThread, pyqtSignal


def fade(x, k):
    return 3 / k**2 * x**2 - 2 / k**3 * x**3


class MyImage(QThread):

    finishSignal = pyqtSignal()
    messageSignal = pyqtSignal(str)

    def __init__(self, imagePath):
        super(MyImage, self).__init__()
        self._imgPath = imagePath

    def setParams(self, width, height, depth, radius):
        self._width = width
        self._height = height
        self._depth = depth
        self._radius = radius
        if self._depth > 1 / 3 * min(self._width, self._height):
            self._depth = int(1 / 3 * min(self._width, self._height))
            self.messageSignal.emit('浸入深度过大，已被重设为 {}'.format(self._depth))
        if self._depth != 0:
            self._kernel = fade(np.arange(0, self._depth, 1), self._depth)
            self._kernelR = fade(np.arange(self._depth - 1, -1, -1), self._depth)
        return self

    def run(self):
        imgObj = Image.open(self._imgPath)
        imgWidth = imgObj.size[0]
        imgHeight = imgObj.size[1]
        ratio = self._width / self._height
        ratioOri = imgWidth / imgHeight

        # 如果比例不变，直接缩放并保存
        if ratioOri == ratio:
            imgObj.resize((self._width, self._height), Image.ANTIALIAS)
            self._save(imgObj)
            self.finishSignal.emit()
            return

        if ratioOri > ratio:
            cropWidth = int(ratio * imgHeight)
            cropHeight = imgHeight
            x1 = (imgWidth - cropWidth) // 2
            y1 = 0
            x2 = x1 + cropWidth
            y2 = imgHeight
        else:
            cropWidth = imgWidth
            cropHeight = int(imgWidth / ratio)
            x1 = 0
            y1 = (imgHeight - cropHeight) // 2
            x2 = imgWidth
            y2 = y1 + cropHeight
        imgObj = imgObj.crop((x1, y1, x2, y2))
        imgObj = imgObj.resize((self._width, self._height), Image.ANTIALIAS)
        imgObj = imgObj.filter(BlurFilter(radius=self._radius))

        # add cover
        coverObj = Image.open(self._imgPath)
        coverObj = coverObj.convert('RGBA')
        if ratioOri > ratio:
            coverObj = coverObj.resize(
                (self._width, int(self._width / ratioOri)), Image.ANTIALIAS
            )
        else:
            coverObj = coverObj.resize(
                (int(self._height * ratioOri), self._height), Image.ANTIALIAS
            )
        mask = np.array(np.asarray(coverObj.split()[3]))

        if self._depth != 0:
            mask[:, :self._depth] = mask[:, :self._depth] * self._kernel
            mask[:, -self._depth:] = mask[:, -self._depth:] * self._kernelR
            mask = mask.T
            mask[:, :self._depth] = mask[:, :self._depth] * self._kernel
            mask[:, -self._depth:] = mask[:, -self._depth:] * self._kernelR
            mask = mask.T
        # 此将数组转成 np.uint8 非常重要，否则无法将数组转成合格的图片
        mask = mask.astype(np.uint8)

        coverBlurObj = coverObj.filter(BlurFilter(radius=self._radius))
        coverBlurObj.paste(coverObj, (0, 0), mask=Image.fromarray(mask))
        if ratioOri > ratio:
            imgObj.paste(
                coverBlurObj,
                (0, (self._height - int(self._width / ratioOri)) // 2),
                mask=Image.fromarray(mask)
            )
        else:
            imgObj.paste(
                coverBlurObj,
                ((self._width - int(self._height * ratioOri)) // 2, 0),
                mask=Image.fromarray(mask)
            )
        self._save(imgObj)
        self.finishSignal.emit()

    def _save(self, imgObj):
        imgPath_ = self._imgPath.split('/')
        imgPath_[-1] = 'c_' + imgPath_[-1]
        imgObj.save('/'.join(imgPath_).replace('.jpg', '.png'), quality=100)


class BlurFilter(ImageFilter.Filter):

    def __init__(self, radius=5, bounds=None):
        self._radius = radius
        self._bounds = bounds

    def filter(self, image):
        if self._bounds:
            clips = image.crop(self._bounds).gaussian_blur(self._radius)
            image.paste(clips, self._bounds)
            return image
        else:
            return image.gaussian_blur(self._radius)


if __name__ == "__main__":
    main()
