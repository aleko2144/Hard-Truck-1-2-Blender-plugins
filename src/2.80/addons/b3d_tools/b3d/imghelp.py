import os
import struct
import math
import bpy

from .common import (
    rgb_to_srgb,
    unmaskBits,
    unmaskTemplate,
    writeSize
)
from ..common import (
    createLogger
)

#Setup module logger
log = createLogger("imghelp")

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

            rgb_color = rgb_to_srgb(R, G, B)
            pal_color = resModule.palette_colors.add()
            pal_color.value = rgb_color


def paletteToColors(palette, indexes, trc):
    colors = []
    for index in indexes:
        R = palette[index*3]
        G = palette[index*3+1]
        B = palette[index*3+2]
        if (0 | (R << 16) | (G << 8) | B) != (0 | (trc[0] << 16) | (trc[1] << 8) | trc[2]):
            A = 255
        else:
            A = 0
        colors.extend([B, G, R, A])
    return colors



def compressRle(file, width, height, bytes_per_pixel):
    pc = 0
    compressed_data = bytearray(width * height * bytes_per_pixel)
    colors = file.read(width * height * 4)
    while pc < width * height:
        black_cnt = 0
        while (colors[pc*4] | colors[pc*4+1] | colors[pc*4+2]) == 0:
            black_cnt += 1


def decompressRle(file, width, height, bytes_per_pixel):
    try:
        # log.debug("BPP: {}".format(bytes_per_pixel))
        pixel_count = 0
        decompressed_data = bytearray(width * height * bytes_per_pixel)
        while pixel_count < width * height:
            curBit = struct.unpack("<B", file.read(1))[0]
            if(curBit > 127): #black pixels
                pixel_count += (curBit-128)
                # log.debug("black pixels {} {}".format(curBit-128, file.tell()))
            else: #raw data
                decompressed_data[pixel_count * bytes_per_pixel:(pixel_count + curBit) * bytes_per_pixel] = file.read(curBit*bytes_per_pixel)
                pixel_count += curBit
                # log.debug("Raw data {} {}".format(curBit, file.tell()))

        return decompressed_data
    except:
        log.error(file.tell())
        raise


def writeTGA8888(filepath, header, colorsBefore, bitMask, transpColor = (0,0,0), bytesPerPixel = 2):

    header[0] = 0
    header[5] = 32 #ColorMapEntrySize
    header[10] = 32 #PixelDepth

    width = header[8]
    height = header[9]
    colorsSize = height*width

    colorsAfter = []

    typeSize = (None,'<B','<H',None,'<I')[bytesPerPixel]

    Rmsk = bitMask[0]
    Gmsk = bitMask[1]
    Bmsk = bitMask[2]
    Amsk = bitMask[3]
    if Rmsk == 0 and Gmsk == 0 and Bmsk == 0 and Amsk == 0: #default 565
        Rmsk = 63488
        Gmsk = 2016
        Bmsk = 31

    Runmask = unmaskBits(Rmsk)
    Gunmask = unmaskBits(Gmsk)
    Bunmask = unmaskBits(Bmsk)
    Aunmask = unmaskBits(Amsk)

    for i in range(0, len(colorsBefore), bytesPerPixel):
        color = struct.unpack(typeSize, colorsBefore[i:i+bytesPerPixel])[0]

        R = ((color & Rmsk) >> Runmask[2])
        G = ((color & Gmsk) >> Gunmask[2])
        B = ((color & Bmsk) >> Bunmask[2])

        if Amsk == 0:
            if R == transpColor[0] >> (8 - Runmask[1]) \
            and G == transpColor[1] >> (8 - Gunmask[1]) \
            and B == transpColor[2] >> (8 - Bunmask[1]):
                A = 0
            else:
                A = 255
        else:
            A = ((color & Amsk) >> Aunmask[2])
            if A > 0:
                A = int("1" * 8, 2)

        R = R << (8-Runmask[1])
        G = G << (8-Gunmask[1])
        B = B << (8-Bunmask[1])

        colorsAfter.extend([B, G, R, A])
    with open(filepath, "wb") as tgaFile:
        headerPack = struct.pack("<3b2hb4h2b", *header)
        colorsPack = struct.pack("<"+str(colorsSize*4)+"B", *colorsAfter)
        tgaFile.write(headerPack)
        tgaFile.write(colorsPack)


def readLVMP(file, bytesPerPixel):
    mipmaps = []
    mipmap = {}
    mipmapCount = struct.unpack("<i", file.read(4))[0]
    width = struct.unpack("<i", file.read(4))[0] #width
    height = struct.unpack("<i", file.read(4))[0] #height
    mipmapSize = width * height
    l_bytesPerPixel = struct.unpack("<i", file.read(4))[0] # in HT2 is 2
    for i in range(mipmapCount):
        mipmap['width'] = width
        mipmap['height'] = height
        mipmap['colors'] = file.read(mipmapSize*bytesPerPixel)
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
        header = list(struct.unpack("<3b2hb4h2b", file.read(18)))
        identifier = file.read(4)
        sectionSize = struct.unpack("<i", file.read(4))[0]
        footerSize = struct.unpack("<i", file.read(4))[0]

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


def TRUEIMAGE_TXRtoTGA32(filepath, transpColor, bytesPerPixel):

    outpath = os.path.splitext(filepath)[0] + ".tga"
    with open(filepath, "rb") as txrFile:
        header = list(struct.unpack("<3b2hb4h2b", txrFile.read(18)))
        sectionIdentifier = txrFile.read(4) # LOFF
        sectionSize = struct.unpack("<i", txrFile.read(4))[0]
        footerSize = struct.unpack("<i", txrFile.read(4))[0]

        header[5] = 32 #ColorMapEntrySize
        header[10] = 32 #PixelDepth
        # header[11] = 0 #PixelDepth
        width = header[8]
        height = header[9]
        colorsSize = height*width
        colorsBefore = txrFile.read(colorsSize*bytesPerPixel)

        footerIdentifier = txrFile.read(4)
        footerSize = struct.unpack("<i", txrFile.read(4))[0]
        mipmaps = []
        if footerIdentifier == b"LVMP": #skip mipmap section
            mipmaps = readLVMP(txrFile, bytesPerPixel)
            footerIdentifier = txrFile.read(4)
            footerSize = struct.unpack("<i", txrFile.read(4))[0]

        pfrm = list(struct.unpack("<4i", txrFile.read(16)))
        txrFile.read(footerSize-16)

        mipmapHeader = header
        for mipmap in mipmaps:
            mipmapHeader[8] = mipmap['width']
            mipmapHeader[9] = mipmap['height']
            mipmapPath = "{}_{}_{}.tga".format(os.path.splitext(filepath)[0], mipmap['width'], mipmap['height'])
            writeTGA8888(mipmapPath, mipmapHeader, mipmap['colors'], pfrm, transpColor, bytesPerPixel)

        header[8] = width
        header[9] = height
        writeTGA8888(outpath, header, colorsBefore, pfrm, transpColor, bytesPerPixel)

    result = {}
    result['format'] = pfrm
    result['has_mipmap'] = True if len(mipmaps) > 0 else False

    return result


def COLORMAP_TXRtoTGA32(filepath, transpColor):

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

        colorsAfter = paletteToColors(palette, colorsBefore, transpColor)

        with open(outpath, "wb") as tgaFile:
            headerPack = struct.pack("<3b2hb4h2b", *header)
            colorsPack = struct.pack("<"+str(colorsSize*4)+"B", *colorsAfter)
            tgaFile.write(headerPack)
            tgaFile.write(colorsPack)

        result = {}
        result['format'] = [4,4,4,4] #probably
        result['has_mipmap'] = False

    return result

def generatePalette(colors, width, height, size = 256):
    num_pixels = width * height
    pixel_counts = {}

    # Loop through the image data, counting the occurrence of each pixel value
    indexes = [0] * num_pixels

    arrInd = 0

    for i in range(0, num_pixels):
        pixel_value = struct.unpack("<I", bytes([colors[i][0], colors[i][1], colors[i][2], 0]))[0]

        if pixel_value not in pixel_counts:
            pixel_counts[pixel_value] = arrInd
            indexes.append(arrInd)
            arrInd += 1
        else:
            indexes.append(pixel_counts[pixel_value])


    if len(pixel_counts) > size:
        log.error(f"Image doesn't fit {size} color palette.")
        return None

    palette = [0]*size
    for value, index in pixel_counts.items():
        palette[index] = ((value >> 24) & 255, (value >> 16) & 255, (value >> 8) & 255)

    # Return the palette
    return [palette, indexes]


def generateMipmaps(barray, width, height, tempFrom):
    # Load the original image into a 2D array of pixels
    original_image = [[0 for y in range(height)] for x in range(width)]

    for x in range(width):
        for y in range(height):
            color = struct.unpack('>I', barray[(x*width + y) * 4: (x*width + y + 1) * 4])[0]
            original_image[x][y] = (\
                (color >> 8) & 255, \
                (color >> 16) & 255, \
                (color >> 24) & 255, \
                (color >> 0) & 255\
            )

    # Create a list of mip-map levels, starting with the original image
    mipmaps = [original_image]

    # Generate the mip-map levels
    while width > 1 or height > 1:
        # Halve the dimensions of the image
        width = math.ceil(width / 2)
        height = math.ceil(height / 2)

        # Create a new 2D array for the mip-map level
        mip_level = [[0 for y in range(height)] for x in range(width)]

        # Compute the average color of each 2x2 block in the previous mip-map level
        for x in range(width):
            for y in range(height):
                r, g, b, a = 0, 0, 0, 0
                count = 0
                for dx in range(2):
                    for dy in range(2):
                        px = 2 * x + dx
                        py = 2 * y + dy
                        if px < len(mipmaps[-1]) and py < len(mipmaps[-1][0]):
                            pr, pg, pb, pa = mipmaps[-1][px][py]
                            r += pr
                            g += pg
                            b += pb
                            a += pa
                            count += 1
                if count > 0:
                    r /= count
                    g /= count
                    b /= count
                    a /= count
                mip_level[x][y] = (int(r), int(g), int(b), int(a))

        mipmaps.append(mip_level)

    return mipmaps


def convertTXRtoTGA32(filepath, transpColor):
    outpath = os.path.splitext(filepath)[0] + ".tga"
    log.info(f"Converting {outpath}")
    imageType = ""
    with open(filepath, "rb") as txrFile:
        txrFile.seek(2, 0)
        imageType = struct.unpack("<B", txrFile.read(1))[0]
    if imageType == 2:
        return TRUEIMAGE_TXRtoTGA32(filepath, transpColor, 2)
    if imageType == 1:
        return COLORMAP_TXRtoTGA32(filepath, transpColor)
    else:
        log.error("Unsupported Tga format")
    return None


def convertTGA32toTXR(filepath, bytesPerPixel, imageType, imageFormat, genMipmap, transpColor=(0,0,0)):
    outpath = os.path.splitext(filepath)[0] + ".txr"
    log.info(f"Converting {outpath}")

    if imageType == 'TRUECOLOR':
        TRUECOLOR_TGA32toTXR(filepath, 2, 2, imageFormat, genMipmap, transpColor)
        pass
    elif imageType == 'COLORMAP':
        pass


def colorsByterrayConvert(barray, tempFrom, tempTo, formFrom = 'ARGB', formTo = 'ARGB', transpColor = (0,0,0), replaceTransp = False):

    fofrAind, fofrRInd, fofrGInd, fofrBInd = (0, 0, 0, 0)

    for i in range(len(formFrom)):
        if formFrom[i] == 'A':
            ffAind = i
        elif formFrom[i] == 'G':
            ffGind = i
        elif formFrom[i] == 'B':
            ffBind = i
        elif formFrom[i] == 'R':
            ffRind = i

    for i in range(len(formTo)):
        if formTo[i] == 'A':
            ftAind = i
        elif formTo[i] == 'R':
            ftRind = i
        elif formTo[i] == 'G':
            ftGind = i
        elif formTo[i] == 'B':
            ftBind = i

    tfA = int(tempFrom[ffAind])
    tfR = int(tempFrom[ffRind])
    tfG = int(tempFrom[ffGind])
    tfB = int(tempFrom[ffBind])
    tfMask = getARGBBitMask(tempFrom)
    tfAMask = tfMask[ffAind]
    tfRMask = tfMask[ffRind]
    tfGMask = tfMask[ffGind]
    tfBMask = tfMask[ffBind]
    tfUnmask = unmaskTemplate(tempFrom)
    tfAUnmask = tfUnmask[ffAind]
    tfRUnmask = tfUnmask[ffRind]
    tfGUnmask = tfUnmask[ffGind]
    tfBUnmask = tfUnmask[ffBind]
    ttUnmask = unmaskTemplate(tempTo)
    ttAUnmask = ttUnmask[ftAind]
    ttRUnmask = ttUnmask[ftRind]
    ttGUnmask = ttUnmask[ftGind]
    ttBUnmask = ttUnmask[ftBind]

    ttA = int(tempTo[ftAind])
    ttR = int(tempTo[ftRind])
    ttG = int(tempTo[ftGind])
    ttB = int(tempTo[ftBind])
    tfBytesPerPixel = (tfR + tfG + tfB + tfA) >> 3
    pixelCnt = len(barray) // tfBytesPerPixel
    ttBytesPerPixel = (ttR + ttG + ttB + ttA) >> 3

    tfTypeSize = (None,'<B','<H',None,'<I')[tfBytesPerPixel]
    ttTypeSize = (None,'<B','<H',None,'<I')[ttBytesPerPixel]
    convertedBArray = bytearray(pixelCnt * ttBytesPerPixel)
    for i in range(0, pixelCnt):
        color = struct.unpack(tfTypeSize, barray[i*tfBytesPerPixel:(i+1)*tfBytesPerPixel])[0]

        if tfA == 0:
            A = 255 >> (8-ttA) << ttAUnmask[2]
        else:
            A = (color & tfAMask)
            # A
            if tfA > ttA:
                A = A >> (tfA-ttA)
            elif tfA < ttA:
                A = A << (ttA-tfA)

            A = A >> tfAUnmask[2] << ttAUnmask[2]


        tmpA = (color & tfAMask)
        if replaceTransp and (tmpA >> tfAUnmask[2]) == 0:

            A = 0
            R = transpColor[0] >> (8 - ttR) << ttRUnmask[2]
            G = transpColor[1] >> (8 - ttG) << ttGUnmask[2]
            B = transpColor[2] >> (8 - ttB) << ttBUnmask[2]

        else:

            R = (color & tfRMask)
            G = (color & tfGMask)
            B = (color & tfBMask)
            # R
            if tfR > ttR:
                R = R >> (tfR-ttR)
            elif tfR < ttR:
                R = R << (ttR-tfR)
            # G
            if tfG > ttG:
                G = G >> (tfG-ttG)
            elif tfR < ttR:
                G = G << (ttG-tfG)
            # B
            if tfB > ttB:
                B = B >> (tfB-ttB)
            elif tfR < ttB:
                B = B << (ttB-tfB)

            R = R >> tfRUnmask[2] << ttRUnmask[2]
            G = G >> tfGUnmask[2] << ttGUnmask[2]
            B = B >> tfBUnmask[2] << ttBUnmask[2]

        convColor = struct.pack(ttTypeSize, A|R|G|B)
        convertedBArray[i*ttBytesPerPixel:(i+1)*ttBytesPerPixel] = convColor

    return convertedBArray


def getARGBBitMask(imageFormat):
    offset = 0
    bitMasks = []
    for i in range(3, -1, -1):
        curInt = int(imageFormat[i])
        if curInt == 0:
            formatInt = 0
        else:
            formatInt = 1
            for j in range(curInt-1):
                formatInt = formatInt << 1
                formatInt += 1
        formatInt = formatInt << offset
        bitMasks.append(formatInt)
        offset += curInt

    return bitMasks[::-1] #reverse

def flipTgaVert(barray, width, height):
    colorsFlipped = bytearray()
    for y in range(height - 1, -1, -1):
        for x in range(width):
            # Get the pixel at (x, y)
            pixel_index = (y * width + x) * 4 #bytes_per_pixel in TGA32
            pixel = barray[pixel_index : pixel_index + 4]

            # Add the pixel to the flipped image
            colorsFlipped.extend(pixel)
    return colorsFlipped


def TRUECOLOR_TGA32toTXR(filepath, bytesPerPixel, imageType, imageFormat, genMipmap, transpColor):

    # genMipmap = False #Temporary
    outpath = os.path.splitext(filepath)[0] + ".txr"

    bitMasks = getARGBBitMask(imageFormat)

    Amsk = bitMasks[0]
    Rmsk = bitMasks[1]
    Gmsk = bitMasks[2]
    Bmsk = bitMasks[3]

    if genMipmap:
        imageFormat = '1555'

    with open(filepath, "rb") as tgaFile:
        colorsAfter = []
        header = list(struct.unpack("<3b2hb4h2b", tgaFile.read(18)))
        header[0] = 12 #LOFF declaration
        header[5] = 16 #ColorMapEntrySize
        header[10] = 16 #PixelDepth
        header[11] = 32 #Image Descriptor
        width = header[8]
        height = header[9]
        colorsSize = height*width
        colorsBefore = struct.unpack("<"+str(colorsSize*4)+"B", tgaFile.read(colorsSize*4))

        colorsBefore = flipTgaVert(bytearray(colorsBefore), width, height)

        colorsAfter = colorsByterrayConvert(bytearray(colorsBefore), '8888', imageFormat, 'ARGB', 'ARGB', transpColor, True)
        if genMipmap:
            mipmaps = generateMipmaps(bytearray(colorsBefore), width, height, '0565')

        footer = tgaFile.read()
    with open(outpath, "wb") as txrFile:
        headerPack = struct.pack("<3b2hb4h2b", *header)
        colorsPack = struct.pack("<"+str(colorsSize*bytesPerPixel)+"B", *colorsAfter)

        LOFF_ms = txrFile.tell()
        txrFile.write(headerPack)
        txrFile.write('LOFF'.encode('cp1251'))
        txrFile.write(struct.pack("<i",4))
        LOFF_write_ms = txrFile.tell()
        txrFile.write(struct.pack("<i",0)) #LOFF reserved
        txrFile.write(colorsPack)
        writeSize(txrFile, LOFF_ms, LOFF_write_ms)
        if genMipmap and len(mipmaps) > 1:
            txrFile.write('LVMP'.encode('cp1251'))
            LVMP_ms = txrFile.tell()
            txrFile.write(struct.pack("<i",0)) #LVMP reserved
            txrFile.write(struct.pack("<i", len(mipmaps)-1))
            txrFile.write(struct.pack("<i", len(mipmaps[1][0])))
            txrFile.write(struct.pack("<i", len(mipmaps[1])))
            txrFile.write(struct.pack("<i", 2))

            for m in range(1, len(mipmaps)):
                mipmap = mipmaps[m]
                m_width = len(mipmap)
                m_height = len(mipmap[0])
                mipmapBytearray = bytearray(m_height * m_width * 4)
                for x in range(m_width):
                    for y in range(m_height): #BGRA
                        mipmapBytearray[(x*m_width+y)*4:(x*m_width+y+1)*4] = struct.pack('>I', \
                            ((mipmap[x][y][0]) << 8) | \
                            ((mipmap[x][y][1]) << 16) | \
                            ((mipmap[x][y][2]) << 24) | \
                            ((mipmap[x][y][3]) << 0)  \
                        )

                mipmapHeader = header
                mipmapHeader[8] = m_width
                mipmapHeader[9] = m_height
                mipmapPath = "{}_{}-{}.tga".format(os.path.splitext(filepath)[0], m_width, m_height)
                writeTGA8888(mipmapPath, mipmapHeader, mipmapBytearray, [\
                    0b00000000111111110000000000000000,\
                    0b00000000000000001111111100000000,\
                    0b00000000000000000000000011111111,\
                    0b11111111000000000000000000000000\
                ], transpColor, 4)

                convertedMipmap = colorsByterrayConvert(mipmapBytearray, '8888', '1555', 'ARGB', 'ARGB', transpColor)

                txrFile.write(convertedMipmap)
            writeSize(txrFile, LVMP_ms)
            txrFile.write(struct.pack("<H", 0))

        # txrFile.write(footer)
        txrFile.write('PFRM'.encode('cp1251'))
        txrFile.write(struct.pack('<i', 16))
        txrFile.write(struct.pack('<i', Rmsk))
        txrFile.write(struct.pack('<i', Gmsk))
        txrFile.write(struct.pack('<i', Bmsk))
        txrFile.write(struct.pack('<i', Amsk))
        txrFile.write('ENDR'.encode('cp1251'))


    return


def MSKtoTGA32(filepath):
    outpath = os.path.splitext(filepath)[0] + ".tga"
    log.info(f"Converting {outpath}")
    indexes = []
    colorsAfter = []
    with open(filepath, "rb") as mskFile:
        magic = mskFile.read(4).decode('cp1251')
        width = struct.unpack("<H", mskFile.read(2))[0]
        height = struct.unpack("<H", mskFile.read(2))[0]
        paletteSize = 256
        palette = list(struct.unpack("<"+str(paletteSize*3)+"B", mskFile.read(paletteSize*3)))
        colorsSize = width*height

        if magic == 'MS16':
            bytesPerPixel = 2
        else: #MSKR, MSK8, MASK
            bytesPerPixel = 1

        colors = decompressRle(mskFile, width, height, bytesPerPixel)

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

        pfrm = [5,6,5,0]

        while True:
            footerIdentifier = mskFile.read(4).decode('cp1251')
            if footerIdentifier == 'PFRM':
                footerSize = struct.unpack("<i", mskFile.read(4))[0]
                pfrm = list(struct.unpack("<4i", mskFile.read(16)))
                continue

            elif footerIdentifier == 'ENDR':
                mskFile.read(4) # alwas int 0
                continue

            mskFile.seek(-4, 1)
            break

        writeTGA8888(outpath, header, colors, pfrm, (0,0,0), bytesPerPixel)
