import os
import struct
import logging
import sys

from ..common import log

from .common import (
    hex_to_rgb,
    unmaskShort
)

def parsePLM(resModule, filepath):
    # colors = []
    with open(filepath, "rb") as plmFile:
        magic = plmFile.read(4).decode("UTF-8")
        palSize = struct.unpack("<I", plmFile.read(4))[0]
        cat1 = plmFile.read(4).decode("UTF-8")
        cat1Size = struct.unpack("<I", plmFile.read(4))[0]
        for i in range(cat1Size // 3):
            R = struct.unpack("<B",plmFile.read(1))[0]
            G = struct.unpack("<B",plmFile.read(1))[0]
            B = struct.unpack("<B",plmFile.read(1))[0]

            rgb_color = hex_to_rgb(R, G, B)
            pal_color = resModule.palette_colors.add()
            pal_color.value = rgb_color

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


def writeTGA8888(filepath, header, colorsBefore, format):

    header[5] = 32 #ColorMapEntrySize
    header[10] = 32 #PixelDepth

    width = header[8]
    height = header[9]
    colorsSize = height*width

    colorsAfter = []

    Rmsk = format[0]
    Gmsk = format[1]
    Bmsk = format[2]
    Amsk = format[3]
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
    with open(filepath, "wb") as tgaFile:
        headerPack = struct.pack("<3b2hb4h2b"+"4s2i", *header)
        colorsPack = struct.pack("<"+str(colorsSize*4)+"B", *colorsAfter)
        tgaFile.write(headerPack)
        tgaFile.write(colorsPack)


def readLVMP(file):
    mipmaps = []
    mipmap = {}
    mipmapCount = struct.unpack("<i", file.read(4))[0]
    width = struct.unpack("<i", file.read(4))[0] #width
    height = struct.unpack("<i", file.read(4))[0] #height
    mipmapSize = width * height
    skipInt = struct.unpack("<i", file.read(4))[0]
    for i in range(mipmapCount):
        mipmap['width'] = width
        mipmap['height'] = height
        mipmap['colors'] = list(struct.unpack("<"+str(mipmapSize)+"H", file.read(mipmapSize*2)))
        width = width >> 1
        height = height >> 1
        mipmapSize = width * height
        mipmaps.append(mipmap)
        mipmap = {}

    file.read(2) # 2 extra bytes
    return mipmaps


def getTXRParams(filepath):

    result = {}
    result['has_mipmap'] = False
    with open(filepath, "rb") as file:
        header = list(struct.unpack("<3b2hb4h2b"+"4s2i", file.read(30)))
        width = header[8]
        height = header[9]
        colorsSize = height*width
        file.seek(colorsSize*2, 1)
        identifier = file.read(4)
        sectionSize = struct.unpack("<i", file.read(4))[0]
        if identifier == b"LVMP": #skip mipmap section
            result['has_mipmap'] = True
            file.seek(sectionSize+2, 1) #skip 2 bytes
        identifier = file.read(4)
        sectionSize = struct.unpack("<i", file.read(4))[0]
        pfrm = list(struct.unpack("<4i", file.read(16)))
        result['format'] = pfrm

    return result


def TXR565toTGA8888(filepath):

    outpath = os.path.splitext(filepath)[0] + ".tga"
    with open(filepath, "rb") as txrFile:
        header = list(struct.unpack("<3b2hb4h2b"+"4s2i", txrFile.read(30)))
        header[5] = 32 #ColorMapEntrySize
        header[10] = 32 #PixelDepth
        width = header[8]
        height = header[9]
        colorsSize = height*width
        colorsBefore = list(struct.unpack("<"+str(colorsSize)+"H", txrFile.read(colorsSize*2)))

        footerIdentifier = txrFile.read(4)
        footerSize = struct.unpack("<i", txrFile.read(4))[0]
        mipmaps = []
        if footerIdentifier == b"LVMP": #skip mipmap section
            mipmaps = readLVMP(txrFile)
            footerIdentifier = txrFile.read(4)
            footerSize = struct.unpack("<i", txrFile.read(4))[0]

        pfrm = list(struct.unpack("<4i", txrFile.read(16)))
        txrFile.read(footerSize-16)

        mipmapHeader = header
        for mipmap in mipmaps:
            mipmapHeader[8] = mipmap['width']
            mipmapHeader[9] = mipmap['height']
            mipmapPath = "{}_{}_{}.tga".format(os.path.splitext(filepath)[0], mipmap['width'], mipmap['height'])
            writeTGA8888(mipmapPath, mipmapHeader, mipmap['colors'], pfrm)

        header[8] = width
        header[9] = height
        writeTGA8888(outpath, header, colorsBefore, pfrm)

    result = {}
    result['format'] = pfrm
    result['has_mipmap'] = True if len(mipmaps) > 0 else False

    return result


def TXRtoTGA32(filepath):
    outpath = os.path.splitext(filepath)[0] + ".tga"
    log.info("Converting " + outpath)
    imageType = ""
    with open(filepath, "rb") as txrFile:
        txrFile.seek(2, 0)
        imageType = struct.unpack("<B", txrFile.read(1))[0]
    if imageType == 2:
        return TXR565toTGA8888(filepath)
    else:
        log.error("Unsupported Tga format")
    return None

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