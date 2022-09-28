import os
import struct
from .common import unmaskShort
import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
log = logging.getLogger("imghelp")
log.setLevel(logging.DEBUG)

def parsePLM(filepath):
    colors = []
    with open(filepath, "rb") as plmFile:
        magic = plmFile.read(4).decode("UTF-8")
        palSize = struct.unpack("<I", plmFile.read(4))[0]
        cat1 = plmFile.read(4).decode("UTF-8")
        cat1Size = struct.unpack("<I", plmFile.read(4))[0]
        for i in range(cat1Size // 3):
            R = struct.unpack("<B",plmFile.read(1))[0]
            G = struct.unpack("<B",plmFile.read(1))[0]
            B = struct.unpack("<B",plmFile.read(1))[0]
            colors.append([R, G, B])
    return colors

def paletteToColors(palette, indexes):
    colors = []
    for index in indexes:
            R = palette[index*3]
            G = palette[index*3+1]
            B = palette[index*3+2]
            if (R | B | G) > 0:
                A = 0b11111111
            else:
                A = 0
            colors.extend([B, G, R, A])
    return colors


def MSKtoTGA32(filepath):
    outpath = os.path.splitext(filepath)[0] + ".tga"
    log.info("Converting " + outpath)
    indexes = []
    colorsAfter = []
    with open(filepath, "rb") as mskFile:
        magic = struct.unpack("<4s", mskFile.read(4))
        width = struct.unpack("<H", mskFile.read(2))[0]
        height = struct.unpack("<H", mskFile.read(2))[0]
        paletteSize = 256
        palette = list(struct.unpack("<"+str(paletteSize*3)+"B", mskFile.read(paletteSize*3)))
        curBit = mskFile.read(1)
        colorsSize = width*width

        while(curBit != b''):
            curBit = struct.unpack("<B", curBit)[0]
            if(curBit > 127):
                for i in range(curBit-128):
                    indexes.append(0)
            else:
                indexes.extend(list(struct.unpack("<"+str(curBit)+"B", mskFile.read(curBit))))
            curBit = mskFile.read(1)
        colorsAfter = paletteToColors(palette, indexes)
        header = [None]*12
        header[0] = 0 #IDLength
        header[1] = 0 #ColorMapType
        header[2] = 2 #ImageType
        header[3] = 0 #FirstIndexEntry
        header[4] = 0 #ColorMapLength
        header[5] = 32 #ColorMapEntrySize
        header[6] = 0 #XOrigin
        header[7] = 0 #YOrigin
        header[8] = width #Width
        header[9] = height #Height
        header[10] = 32 #PixelDepth
        header[11] = 32 #ImageDescriptor

        with open(outpath, "wb") as tgaFile:
            headerPack = struct.pack("<3b2hb4h2b", *header)
            colorsPack = struct.pack("<"+str(colorsSize*4)+"B", *colorsAfter)
            tgaFile.write(headerPack)
            tgaFile.write(colorsPack)


def TXR565toTGA8888(filepath):

    outpath = os.path.splitext(filepath)[0] + ".tga"
    with open(filepath, "rb") as txrFile:
        colorsAfter = []
        header = list(struct.unpack("<3b2hb4h2b"+"4s2i", txrFile.read(30)))
        header[5] = 32 #ColorMapEntrySize
        header[10] = 32 #PixelDepth
        width = header[8]
        height = header[9]
        colorsSize = height*width
        colorsBefore = list(struct.unpack("<"+str(colorsSize)+"H", txrFile.read(colorsSize*2)))

        footerIdentifier = txrFile.read(4)
        footerSize = struct.unpack("<i", txrFile.read(4))[0]
        if footerIdentifier == b"LVMP": #skip mipmap section
            txrFile.seek(footerSize+2, 1) # 2 extra bytes
            footerIdentifier = txrFile.read(4)
            footerSize = struct.unpack("<i", txrFile.read(4))[0]

        footer = list(struct.unpack("<4i"+str(footerSize-16)+"B", txrFile.read(footerSize)))
        Rmsk = footer[0]
        Gmsk = footer[1]
        Bmsk = footer[2]
        Amsk = footer[3]
        Runmask = unmaskShort(Rmsk)
        Gunmask = unmaskShort(Gmsk)
        Bunmask = unmaskShort(Bmsk)
        Aunmask = unmaskShort(Amsk)
        if Aunmask[1] != 0:
            for color in colorsBefore:
                R = ((color & Rmsk) >> Runmask[2]) << (8-Runmask[1])
                G = ((color & Gmsk) >> Gunmask[2]) << (8-Gunmask[1])
                B = ((color & Bmsk) >> Bunmask[2]) << (8-Bunmask[1])
                A = ((color & Amsk) >> Aunmask[2]) << (8-Aunmask[1])
                colorsAfter.extend([B, G, R, A])
        else:
            for color in colorsBefore:
                R = ((color & Rmsk) >> Runmask[2]) << (8-Runmask[1])
                G = ((color & Gmsk) >> Gunmask[2]) << (8-Gunmask[1])
                B = ((color & Bmsk) >> Bunmask[2]) << (8-Bunmask[1])
                if (R | B | G) > 0:
                    A = 0b11111111
                else:
                    A = 0
                colorsAfter.extend([B, G, R, A])
        footer[0] = 0xFF000000
        footer[1] = 0x00FF0000
        footer[2] = 0x0000FF00
        footer[3] = 0x000000FF
        with open(outpath, "wb") as tgaFile:
            headerPack = struct.pack("<3b2hb4h2b"+"4s2i", *header)
            colorsPack = struct.pack("<"+str(colorsSize*4)+"B", *colorsAfter)
            footerPack = struct.pack("<4I"+str(footerSize-16)+"B", *footer)
            tgaFile.write(headerPack)
            tgaFile.write(colorsPack)
            tgaFile.write(footerIdentifier)
            tgaFile.write(struct.pack("<i",footerSize))
            tgaFile.write(footerPack)

    return

def TXRwPAL888toTGA8888(filepath):

    outpath = os.path.splitext(filepath)[0] + ".tga"
    with open(filepath, "rb") as txrFile:
        colorsAfter = []
        header = list(struct.unpack("<3b2hb4h2b", txrFile.read(18)))
        colorMapLength = header[4]
        width = header[8]
        height = header[9]
        header[1] = 0 #ColorMapType
        header[2] = 2 #ImageType
        header[4] = 0 #ColorMapLength
        header[5] = 32 #ColorMapEntrySize
        header[10] = 32 #PixelDepth
        paletteSize = colorMapLength*3
        palette = struct.unpack("<"+str(paletteSize)+"B", txrFile.read(paletteSize))
        colorsSize = height*width
        colorsBefore = list(struct.unpack("<"+str(colorsSize)+"B", txrFile.read(colorsSize)))

        for color in colorsBefore:
            R = palette[color*3]
            G = palette[color*3+1]
            B = palette[color*3+2]
            if (R | B | G) > 0:
                A = 0b11111111
            else:
                A = 0
            colorsAfter.extend([B, G, R, A])

        with open(outpath, "wb") as tgaFile:
            headerPack = struct.pack("<3b2hb4h2b", *header)
            colorsPack = struct.pack("<"+str(colorsSize*4)+"B", *colorsAfter)
            tgaFile.write(headerPack)
            tgaFile.write(colorsPack)

    return

def TXRtoTGA32(filepath):
    outpath = os.path.splitext(filepath)[0] + ".tga"
    log.info("Converting " + outpath)
    imageType = ""
    with open(filepath, "rb") as txrFile:
        txrFile.seek(2, 0)
        imageType = struct.unpack("<B", txrFile.read(1))[0]
    if imageType == 2:
        TXR565toTGA8888(filepath)
    elif imageType == 1:
        TXRwPAL888toTGA8888(filepath)
    return

def TGA32toTXR(filepath):
    outpath = os.path.splitext(filepath)[0] + ".txr"
    with open(filepath, "rb") as tgaFile:
        colorsAfter = []
        header = list(struct.unpack("<3b2hb4h2b"+"4s2i", tgaFile.read(30)))
        header[5] = 16 #ColorMapEntrySize
        header[10] = 16 #PixelDepth
        width = header[8]
        height = header[9]
        colorsSize = height*width
        colorsBefore = list(struct.unpack("<"+str(colorsSize*4)+"B", tgaFile.read(colorsSize*4)))
        for i in range(0, colorsSize):
            pos = i*4
            R = colorsBefore[pos]
            G = colorsBefore[pos+1]
            B = colorsBefore[pos+2]
            # A = colorsBefore[pos+3]
            color = ((R >> 3) << 11) | ((G >> 2) << 5) | (B >> 3)
            colorsAfter.append(color)
        footer = tgaFile.read()
        with open(outpath, "wb") as tgaFile:
            headerPack = struct.pack("<3b2hb4h2b"+"4s2i", *header)
            colorsPack = struct.pack("<"+str(colorsSize)+"H", *colorsAfter)
            tgaFile.write(headerPack)
            tgaFile.write(colorsPack)
            tgaFile.write(footer)

    return