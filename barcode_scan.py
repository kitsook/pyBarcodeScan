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

import argparse
import os
import sys
import shutil
from engine import opencv_engine
from engine import zbar_engine

# display the image
#(imgH,imgW) = image.shape[:2]
#while imgW > 1024 or imgH > 1024:
#    image = cv2.pyrDown(image)
#    (imgH,imgW) = image.shape[:2]

#cv2.imshow("Image", image)
#cv2.waitKey(0)

# construct a unique filename in dir based on name.nextval
def nextFilename(dir, name):
    nextVal = 1
    for file in [d for d in os.listdir(dir) if d.startswith(name)]:
        fileWithVal =  os.path.splitext(file)[0]

        fileValSplit = fileWithVal.split('.')
        if len(fileValSplit) > 1:
            nextVal = int(fileValSplit[1]) + 1

    return name + '.' + str(nextVal)
######

# parse arguments
ap = argparse.ArgumentParser()
ap.add_argument("-s", "--srcDir", required = False, default = "srcDir", help = "path to the image files")
ap.add_argument("-d", "--dstDir", required = False, default = "dstDir", help = "path to the destination")
ap.add_argument("-l", "--lostDir", required= False, default = "lostDir", help = "path to store unidentified files")
args = vars(ap.parse_args())

for root, dirs, files in os.walk(args['srcDir']):
    for f in files:
        try:
            fileName = os.path.join(args['srcDir'], f)
            ext = os.path.splitext(fileName)[1]
            symbols = zbar_engine.processFile(fileName)

            # if zbar can't find anything, use opencv
            if len(symbols) == 0:
                symbols = opencv_engine.processFile(fileName)

            print f, ': ', list(set(symbols))

            for symbol in list(set(symbols)):
                newName = nextFilename(args['dstDir'], symbol) + ext
                shutil.copy2(fileName, os.path.join(args['dstDir'], newName))

            if len(symbols) == 0:
                shutil.copy2(fileName, os.path.join(args['lostDir'], f))

        except:
            print "Problem handling file ", f, ': ', sys.exc_info()
            #pass
