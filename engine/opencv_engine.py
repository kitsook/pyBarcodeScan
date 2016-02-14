# Copyright (c) 2016 Clarence Ho (clarenceho at gmail dot com)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# reference: http://www.pyimagesearch.com/2014/11/24/detecting-barcodes-images-python-opencv/

import numpy
import math
import cv2
from PIL import Image
import zbar_engine


def rotatePoint(pt, mat):
    newX = pt[0] * mat[0][0] + pt[1] * mat[0][1] + mat[0][2]
    newY = pt[0] * mat[1][0] + pt[1] * mat[1][1] + mat[1][2]
    return (newX, newY)

# calculate new image size after rotation
def newBouncingBox(size, deg):
    width = size[0]
    height = size[1]

    rad = math.radians(deg)
    sin = abs(math.sin(rad))
    cos = abs(math.cos(rad))

    newWidth = int(width * cos + height * sin) + 1
    newHeight = int(width * sin + height * cos) + 1

    return (newWidth, newHeight)

def processFile(fileName):
    result = []

    # load the image and convert it to grayscale
    image = cv2.imread(fileName)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # compute the Scharr gradient magnitude representation of the images
    # in both the x and y direction
    gradX = cv2.Sobel(gray, ddepth = cv2.cv.CV_32F, dx = 1, dy = 0, ksize = -1)
    gradY = cv2.Sobel(gray, ddepth = cv2.cv.CV_32F, dx = 0, dy = 1, ksize = -1)

    # subtract the y-gradient from the x-gradient
    gradient = cv2.subtract(gradX, gradY)
    gradient = cv2.convertScaleAbs(gradient)

    # blur and threshold the image
    blurred = cv2.blur(gradient, (3, 3))
    (_, thresh) = cv2.threshold(blurred, 225, 255, cv2.THRESH_BINARY)

    # construct a closing kernel and apply it to the thresholded image
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (21, 7))
    closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

    # perform a series of erosions and dilations
    closed = cv2.erode(closed, None, iterations = 4)
    closed = cv2.dilate(closed, None, iterations = 4)

    # find the contours in the image, and sort the contours by their area
    (cnts, _) = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # handle the biggest 3 entries
    for c in sorted(cnts, key = cv2.contourArea, reverse = True)[:3]:

        # get the rotated bounding box
        rect = cv2.minAreaRect(c)
        box = numpy.int0(cv2.cv.BoxPoints(rect))

        # draw a bounding box around the detected barcode
        #cv2.drawContours(image, [box], -1, (0, 255, 0), 3)

        # create a rotation matrix to level the box
        rotMatrix = cv2.getRotationMatrix2D(rect[0], rect[2], 1.0)
        rotRect = tuple([rotatePoint(i, rotMatrix) for i in cv2.cv.BoxPoints(rect)])
        rotBox = numpy.int0(rotRect)

        boxWidth, boxHeight = numpy.int0(rect[1])
        boxOrigX, boxOrigY = numpy.int0((rect[0][0] - rect[1][0] / 2.0, rect[0][1] - rect[1][1] / 2.0))

        rotWidth, rotHeight = newBouncingBox((image.shape[1], image.shape[0]), rect[2])

        # rotate the image
        rotImage = cv2.warpAffine(image, rotMatrix, (rotWidth, rotHeight), flags=cv2.INTER_LINEAR)
        #cv2.drawContours(rotImage, [rotBox], -1, (0, 0, 255), 2)

        #(imgH,imgW) = rotImage.shape[:2]
        #while imgW > 1024 or imgH > 1024:
        #    rotImage = cv2.pyrDown(rotImage)
        #    (imgH,imgW) = rotImage.shape[:2]
        #cv2.imshow("Image", rotImage)
        #cv2.waitKey(0)

        # crop out the potential barcode part
        #image = cv2.cvtColor(image[boxOrigY:boxOrigY+boxHeight, boxOrigX:boxOrigX+boxWidth], cv2.COLOR_BGR2RGB)
        rotImage = rotImage[boxOrigY:boxOrigY+boxHeight, boxOrigX:boxOrigX+boxWidth]

        # use zbar to read
        pil = Image.fromarray(rotImage).convert('L')
        width, height = pil.size
        raw = pil.tostring()
        del pil
        result.extend(zbar_engine.zbarScan(raw, width, height))

    return result
