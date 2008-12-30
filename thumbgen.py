#!/usr/bin/env python
import os
import sys
import tempfile
from optparse import OptionParser
import subprocess

from path import path

import config

gDryRun = False

def createTempImage(src, name):
    src.copy(name)
    subprocess.call(["jhead", "-autorot", name])


def resizeImage(src, size, dst):
    if not dst.dirname().exists():
        dst.dirname().makedirs()
    subprocess.call(["convert",
        "-resize", "%dx%d" % (size, size),
        "-quality", str(config.QUALITY),
        src, dst])


def generateThumbnail(src, dstDir):
    def needUpdate(dst):
        if not dst.exists():
            return True
        return src.getmtime() > dst.getmtime()

    full = dstDir / "full" / src.basename()
    thumb = dstDir / "thumb" / src.basename()
    updateThumb = needUpdate(thumb)
    updateFull = needUpdate(full)

    if not updateThumb and not updateFull:
        return

    fd, tempImage = tempfile.mkstemp()
    tempImage = path(tempImage)
    if not gDryRun:
        createTempImage(src, tempImage)

    try:
        if updateFull:
            print "Updating full image", src
            if not gDryRun:
                resizeImage(tempImage, config.FULL_SIZE, full)

        if updateThumb:
            print "Updating thumbnail", src
            if not gDryRun:
                resizeImage(full, config.THUMB_SIZE, thumb)
    finally:
        os.close(fd)
        tempImage.unlink()


def main():
    parser = OptionParser()

    # Add a boolean option stored in options.verbose.
    parser.add_option("--dry-run",
                      action="store_true", dest="dryRun", default=False,
                      help="Just print what should be done")

    (options, args) = parser.parse_args()

    if len(args) != 2:
        parser.show_help()

    gDryRun = options.dryRun

    srcBaseDir = path(args[0])
    dstBaseDir = path(args[1])

    for src in srcBaseDir.walk():
        ext = src.splitext()[1]
        if ext.lower() == ".jpg":
            relativePath = srcBaseDir.relpathto(src)
            dst = dstBaseDir / relativePath
            generateThumbnail(src, dst.dirname())

    return 0


if __name__=="__main__":
    sys.exit(main())
# vi: ts=4 sw=4 et
