#!/usr/bin/env python
import sys
import tempfile
from optparse import OptionParser
import subprocess

from path import path

FULL_SIZE = 1024
THUMB_SIZE = 120
QUALITY = 75

gDryRun = False

def createTempImage(src):
    fs, name = tempfile.mkstemp()
    src.copy(name)
    subprocess.call(["jhead", "-autorot", name])
    return name


def resizeImage(src, size, dst):
    if not dst.dirname().exists():
        dst.dirname().makedirs()
    subprocess.call(["convert",
        "-resize", "%dx%d" % (size, size),
        "-quality", str(QUALITY),
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

    if not gDryRun:
        tempImage = createTempImage(src)

    if updateFull:
        print "Updating full image", src
        if not gDryRun:
            resizeImage(tempImage, FULL_SIZE, full)

    if updateThumb:
        print "Updating thumbnail", src
        if not gDryRun:
            resizeImage(tempImage, THUMB_SIZE, thumb)


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
