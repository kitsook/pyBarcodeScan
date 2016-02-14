# pyBarcodeScan

A Python program to scan barcodes from images with zbar and OpenCV.
By default, it processes all images in the `srcDir` folder. For each barcode
found in an image, the file is copied to the `dstDir` folder and named as
*barcode.count*.

For example, if these are the image files and corresponding barcodes in them:
```
srcDir/image01.jpg: 00400439, 00730655
srcDir/image02.jpg: 00400439, 4890008330249
```

After processing, the above images will be copied to folder `dstDir` as:

```
dstDir/00400439.1.jpg
dstDir/00400439.2.jpg
dstDir/00730655.1.jpg
dstDir/4890008330249.1.jpg
```

## Mechanism

There are two engines defined.  First the program will try to use zbar directly
to process the image.

If no barcode is found, it will use OpenCV to scan for possible barcode patterns
in the image and rotate them properly before passing to zbar again.


## Prerequisite

First you need to have zbar (http://zbar.sourceforge.net/) installed on your
system.  Remember to install the development header and library too.

Then download and compile the source code of zbar python
(https://pypi.python.org/pypi/zbar).  Modify `setup.py` and add the `include`
and `libaray` folder of zbar library.  Run `setup.py build` to build it (use
`setup.py build --compiler=mingw32` if you are building it on Windows and
has MinGW installed).  Finally run `setup.py install` to install it.

This program also uses Python Image Libaray (PIL) which can be installed with
`pip install PIL`.

## Parameters

The program can be executed as `python barcode_scan.py`.  Possible parameters:
* `-s` or `--srcDir` - source directory of images
* `-d`, `--dstDir` - destination directory of the images named as barcode found
* `-l`, `--lostDir` - images copied here if no barcode found within
