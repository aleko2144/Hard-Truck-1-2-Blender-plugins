import os
import struct
import math
import bpy

from .common import (
    rgb_to_srgb,
    unmask_bits,
    unmask_template,
    write_size
)
from ..common import (
    imghelp_logger
)

#Setup module logger
log = imghelp_logger

def parse_plm(res_module, filepath):
    # colors = []
    with open(filepath, "rb") as plm_file:
        magic = plm_file.read(4).decode("UTF-8")
        pal_size = struct.unpack("<I", plm_file.read(4))[0]
        cat1 = plm_file.read(4).decode("UTF-8")
        cat1_size = struct.unpack("<I", plm_file.read(4))[0]
        for i in range(cat1_size // 3):
            r = struct.unpack("<B",plm_file.read(1))[0]
            g = struct.unpack("<B",plm_file.read(1))[0]
            b = struct.unpack("<B",plm_file.read(1))[0]

            rgb_color = rgb_to_srgb(r, g, b)
            pal_color = res_module.palette_colors.add()
            pal_color.value = rgb_color


def palette_to_colors(palette, indexes, trc):
    colors = []
    for index in indexes:
        r = palette[index*3]
        g = palette[index*3+1]
        b = palette[index*3+2]
        if (0 | (r << 16) | (g << 8) | b) != (0 | (trc[0] << 16) | (trc[1] << 8) | trc[2]):
            a = 255
        else:
            a = 0
        colors.extend([b, g, r, a])
    return colors



def compress_rle(file, width, height, bytes_per_pixel):
    pc = 0
    compressed_data = bytearray(width * height * bytes_per_pixel)
    colors = file.read(width * height * 4)
    while pc < width * height:
        black_cnt = 0
        while (colors[pc*4] | colors[pc*4+1] | colors[pc*4+2]) == 0:
            black_cnt += 1


def decompress_rle(file, width, height, bytes_per_pixel):
    try:
        # log.debug("BPP: {}".format(bytes_per_pixel))
        pixel_count = 0
        decompressed_data = bytearray(width * height * bytes_per_pixel)
        while pixel_count < width * height:
            curbit = struct.unpack("<B", file.read(1))[0]
            if(curbit > 127): #black pixels
                pixel_count += (curbit-128)
                # log.debug("black pixels {} {}".format(curbit-128, file.tell()))
            else: #raw data
                decompressed_data[pixel_count * bytes_per_pixel:(pixel_count + curbit) * bytes_per_pixel] = file.read(curbit*bytes_per_pixel)
                pixel_count += curbit
                # log.debug("Raw data {} {}".format(curbit, file.tell()))

        return decompressed_data
    except:
        log.error(file.tell())
        raise


def write_tga8888(filepath, header, colors_before, bit_mask, transp_color = (0,0,0), bytes_per_pixel = 2):

    header[0] = 0
    header[5] = 32 #ColorMapEntrySize
    header[10] = 32 #PixelDepth

    width = header[8]
    height = header[9]
    colors_size = height*width

    colors_after = []

    type_size = (None,'<B','<H',None,'<I')[bytes_per_pixel]

    r_msk = bit_mask[0]
    g_msk = bit_mask[1]
    b_msk = bit_mask[2]
    a_msk = bit_mask[3]
    if r_msk == 0 and g_msk == 0 and b_msk == 0 and a_msk == 0: #default 565
        r_msk = 63488
        g_msk = 2016
        b_msk = 31

    r_unmask = unmask_bits(r_msk)
    g_unmask = unmask_bits(g_msk)
    b_unmask = unmask_bits(b_msk)
    a_unmask = unmask_bits(a_msk)

    for i in range(0, len(colors_before), bytes_per_pixel):
        color = struct.unpack(type_size, colors_before[i:i+bytes_per_pixel])[0]

        r = ((color & r_msk) >> r_unmask.rzeros)
        g = ((color & g_msk) >> g_unmask.rzeros)
        b = ((color & b_msk) >> b_unmask.rzeros)

        a = 255
        if a_msk == 0:
            if r == transp_color[0] >> (8 - r_unmask.ones) \
            and g == transp_color[1] >> (8 - g_unmask.ones) \
            and b == transp_color[2] >> (8 - b_unmask.ones):
                a = 0
            else:
                a = 255
        else:
            a = ((color & a_msk) >> a_unmask.rzeros)
            if a > 0:
                a = int("1" * 8, 2)

        r = r << (8-r_unmask.ones)
        g = g << (8-g_unmask.ones)
        b = b << (8-b_unmask.ones)

        colors_after.extend([b, g, r, a])
        # colors_after.extend([a, r, g, b])
    with open(filepath, "wb") as tga_file:
        header_pack = struct.pack("<3b2hb4h2b", *header)
        colors_pack = struct.pack("<"+str(colors_size*4)+"B", *colors_after)
        tga_file.write(header_pack)
        tga_file.write(colors_pack)


def read_lvmp(file, bytes_per_pixel):
    mipmaps = []
    mipmap = {}
    mipmap_count = struct.unpack("<i", file.read(4))[0]
    width = struct.unpack("<i", file.read(4))[0] #width
    height = struct.unpack("<i", file.read(4))[0] #height
    mipmap_size = width * height
    l_bytes_per_pixel = struct.unpack("<i", file.read(4))[0] # in HT2 is 2
    for i in range(mipmap_count):
        mipmap['width'] = width
        mipmap['height'] = height
        mipmap['colors'] = file.read(mipmap_size*bytes_per_pixel)
        width = width >> 1
        height = height >> 1
        mipmap_size = width * height
        mipmaps.append(mipmap)
        mipmap = {}

    file.read(2) # 2 extra bytes
    return mipmaps


def get_txr_params(filepath):

    result = {}
    result['has_mipmap'] = False
    with open(filepath, "rb") as file:
        header = list(struct.unpack("<3b2hb4h2b", file.read(18)))
        identifier = file.read(4)
        section_size = struct.unpack("<i", file.read(4))[0]
        footer_size = struct.unpack("<i", file.read(4))[0]

        width = header[8]
        height = header[9]
        colors_size = height*width
        file.seek(colors_size*2, 1)
        identifier = file.read(4)
        section_size = struct.unpack("<i", file.read(4))[0]
        if identifier == b"LVMP": #skip mipmap section
            result['has_mipmap'] = True
            file.seek(section_size+2, 1) #skip 2 bytes
            identifier = file.read(4)
            section_size = struct.unpack("<i", file.read(4))[0]
        pfrm = list(struct.unpack("<4i", file.read(16)))
        result['format'] = pfrm

    return result


def trueimage_txr_to_tga32(filepath, transp_color, bytes_per_pixel):

    outpath = os.path.splitext(filepath)[0] + ".tga"
    with open(filepath, "rb") as txr_file:
        header = list(struct.unpack("<3b2hb4h2b", txr_file.read(18)))
        section_identifier = txr_file.read(4) # LOFF
        section_size = struct.unpack("<i", txr_file.read(4))[0]
        footer_size = struct.unpack("<i", txr_file.read(4))[0]

        header[5] = 32 #ColorMapEntrySize
        header[10] = 32 #PixelDepth
        # header[11] = 0 #PixelDepth
        width = header[8]
        height = header[9]
        colors_size = height*width
        colors_before = txr_file.read(colors_size*bytes_per_pixel)

        footer_identifier = txr_file.read(4)
        footer_size = struct.unpack("<i", txr_file.read(4))[0]
        mipmaps = []
        if footer_identifier == b"LVMP": #skip mipmap section
            mipmaps = read_lvmp(txr_file, bytes_per_pixel)
            footer_identifier = txr_file.read(4)
            footer_size = struct.unpack("<i", txr_file.read(4))[0]

        pfrm = list(struct.unpack("<4i", txr_file.read(16)))
        txr_file.read(footer_size-16)

        mipmap_header = header
        for mipmap in mipmaps:
            mipmap_header[8] = mipmap['width']
            mipmap_header[9] = mipmap['height']
            filepath_no_ext = os.path.splitext(filepath)[0]
            mipmap_path = '{}_{}_{}.tga'.format(filepath_no_ext, mipmap["width"], mipmap["height"])
            write_tga8888(mipmap_path, mipmap_header, mipmap['colors'], pfrm, transp_color, bytes_per_pixel)

        header[8] = width
        header[9] = height
        write_tga8888(outpath, header, colors_before, pfrm, transp_color, bytes_per_pixel)

    result = {}
    result['format'] = pfrm
    result['has_mipmap'] = True if len(mipmaps) > 0 else False

    return result


def colormap_txr_to_tga32(filepath, transp_color):

    outpath = os.path.splitext(filepath)[0] + ".tga"
    with open(filepath, "rb") as txr_file:
        colors_after = []
        header = list(struct.unpack("<3b2hb4h2b", txr_file.read(18)))
        color_map_length = header[4]
        width = header[8]
        height = header[9]
        header[1] = 0 #ColorMapType
        header[2] = 2 #ImageType
        header[4] = 0 #ColorMapLength
        header[5] = 32 #ColorMapEntrySize
        header[10] = 32 #PixelDepth
        palette_size = color_map_length*3
        palette = struct.unpack("<"+str(palette_size)+"B", txr_file.read(palette_size))
        colors_size = height*width
        colors_before = list(struct.unpack("<"+str(colors_size)+"B", txr_file.read(colors_size)))

        colors_after = palette_to_colors(palette, colors_before, transp_color)

        with open(outpath, "wb") as tga_file:
            header_pack = struct.pack("<3b2hb4h2b", *header)
            colors_pack = struct.pack("<"+str(colors_size*4)+"B", *colors_after)
            tga_file.write(header_pack)
            tga_file.write(colors_pack)

        result = {}
        result['format'] = [4,4,4,4] #probably
        result['has_mipmap'] = False

    return result

def generate_palette(colors, width, height, size = 256):
    num_pixels = width * height
    pixel_counts = {}

    # Loop through the image data, counting the occurrence of each pixel value
    indexes = [0] * num_pixels

    arr_ind = 0

    for i in range(0, num_pixels):
        pixel_value = struct.unpack("<I", bytes([colors[i][0], colors[i][1], colors[i][2], 0]))[0]

        if pixel_value not in pixel_counts:
            pixel_counts[pixel_value] = arr_ind
            indexes.append(arr_ind)
            arr_ind += 1
        else:
            indexes.append(pixel_counts[pixel_value])


    if len(pixel_counts) > size:
        log.error("Image doesn't fit {} color palette.".format(size))
        return None

    palette = [0]*size
    for value, index in pixel_counts.items():
        palette[index] = ((value >> 24) & 255, (value >> 16) & 255, (value >> 8) & 255)

    # Return the palette
    return [palette, indexes]


def generate_mipmaps(barray, width, height, temp_from):
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


def convert_txr_to_tga32(filepath, transp_color):
    outpath = os.path.splitext(filepath)[0] + ".tga"
    log.info("Converting {}".format(outpath))
    image_type = ""
    with open(filepath, "rb") as txr_file:
        txr_file.seek(2, 0)
        image_type = struct.unpack("<B", txr_file.read(1))[0]
        log.debug("Image type: {}".format(image_type))
    if image_type == 2:
        return trueimage_txr_to_tga32(filepath, transp_color, 2)
    if image_type == 1:
        return colormap_txr_to_tga32(filepath, transp_color)
    else:
        log.error("Unsupported Tga format")
    return None


def convert_tga32_to_txr(filepath, bytes_per_pixel, image_type, image_format, gen_mipmap, transp_color=(0,0,0)):
    outpath = os.path.splitext(filepath)[0] + ".txr"
    log.info("Converting {}".format(outpath))

    if image_type == 'TRUECOLOR':
        truecolor_tga_32_to_txr(filepath, 2, 2, image_format, gen_mipmap, transp_color)
        pass
    elif image_type == 'COLORMAP':
        pass


def colors_byterray_convert(barray, temp_from, temp_to, form_from = 'ARGB', form_to = 'ARGB', transp_color = (0,0,0), replace_transp = False):

    fofr_a_ind, fofr_r_ind, fofr_g_ind, fofr_b_ind = (0, 0, 0, 0)

    for i in range(len(form_from)):
        if form_from[i] == 'A':
            ff_a_ind = i
        elif form_from[i] == 'G':
            ff_g_ind = i
        elif form_from[i] == 'B':
            ff_b_ind = i
        elif form_from[i] == 'R':
            ff_r_ind = i

    for i in range(len(form_to)):
        if form_to[i] == 'A':
            ft_a_ind = i
        elif form_to[i] == 'R':
            ft_r_ind = i
        elif form_to[i] == 'G':
            ft_g_ind = i
        elif form_to[i] == 'B':
            ft_b_ind = i

    tf_a = int(temp_from[ff_a_ind])
    tf_r = int(temp_from[ff_r_ind])
    tf_g = int(temp_from[ff_g_ind])
    tf_b = int(temp_from[ff_b_ind])
    tf_mask = get_argb_bit_mask(temp_from)
    tf_a_mask = tf_mask[ff_a_ind]
    tf_r_mask = tf_mask[ff_r_ind]
    tf_g_mask = tf_mask[ff_g_ind]
    tf_b_mask = tf_mask[ff_b_ind]
    tf_unmask = unmask_template(temp_from)
    tf_a_unmask = tf_unmask[ff_a_ind]
    tf_r_unmask = tf_unmask[ff_r_ind]
    tf_g_unmask = tf_unmask[ff_g_ind]
    tf_b_unmask = tf_unmask[ff_b_ind]
    tt_unmask = unmask_template(temp_to)
    tt_a_unmask = tt_unmask[ft_a_ind]
    tt_r_unmask = tt_unmask[ft_r_ind]
    tt_g_unmask = tt_unmask[ft_g_ind]
    tt_b_unmask = tt_unmask[ft_b_ind]

    tt_a = int(temp_to[ft_a_ind])
    tt_r = int(temp_to[ft_r_ind])
    tt_g = int(temp_to[ft_g_ind])
    tt_b = int(temp_to[ft_b_ind])
    tf_bytes_per_pixel = (tf_r + tf_g + tf_b + tf_a) >> 3
    pixel_cnt = len(barray) // tf_bytes_per_pixel
    tt_bytes_per_pixel = (tt_r + tt_g + tt_b + tt_a) >> 3

    tf_type_size = (None,'<B','<H',None,'<I')[tf_bytes_per_pixel]
    tt_type_size = (None,'<B','<H',None,'<I')[tt_bytes_per_pixel]
    converted_byte_array = bytearray(pixel_cnt * tt_bytes_per_pixel)
    for i in range(0, pixel_cnt):
        color = struct.unpack(tf_type_size, barray[i*tf_bytes_per_pixel:(i+1)*tf_bytes_per_pixel])[0]

        if tf_a == 0:
            a = 255 >> (8-tt_a) << tt_a_unmask[2]
        else:
            a = (color & tf_a_mask)
            # a
            if tf_a > tt_a:
                a = a >> (tf_a-tt_a)
            elif tf_a < tt_a:
                a = a << (tt_a-tf_a)

            a = a >> tf_a_unmask[2] << tt_a_unmask[2]


        tmp_a = (color & tf_a_mask)
        if replace_transp and (tmp_a >> tf_a_unmask[2]) == 0:

            a = 0
            r = transp_color[0] >> (8 - tt_r) << tt_r_unmask[2]
            g = transp_color[1] >> (8 - tt_g) << tt_g_unmask[2]
            b = transp_color[2] >> (8 - tt_b) << tt_b_unmask[2]

        else:

            r = (color & tf_r_mask)
            g = (color & tf_g_mask)
            b = (color & tf_b_mask)
            # r
            if tf_r > tt_r:
                r = r >> (tf_r-tt_r)
            elif tf_r < tt_r:
                r = r << (tt_r-tf_r)
            # g
            if tf_g > tt_g:
                g = g >> (tf_g-tt_g)
            elif tf_r < tt_r:
                g = g << (tt_g-tf_g)
            # b
            if tf_b > tt_b:
                b = b >> (tf_b-tt_b)
            elif tf_r < tt_b:
                b = b << (tt_b-tf_b)

            r = r >> tf_r_unmask[2] << tt_r_unmask[2]
            g = g >> tf_g_unmask[2] << tt_g_unmask[2]
            b = b >> tf_b_unmask[2] << tt_b_unmask[2]

        conv_color = struct.pack(tt_type_size, a|r|g|b)
        converted_byte_array[i*tt_bytes_per_pixel:(i+1)*tt_bytes_per_pixel] = conv_color

    return converted_byte_array


def get_argb_bit_mask(image_format):
    offset = 0
    bit_masks = []
    for i in range(3, -1, -1):
        cur_int = int(image_format[i])
        if cur_int == 0:
            format_int = 0
        else:
            format_int = 1
            for j in range(cur_int-1):
                format_int = format_int << 1
                format_int += 1
        format_int = format_int << offset
        bit_masks.append(format_int)
        offset += cur_int

    return bit_masks[::-1] #reverse

def flip_tga_vert(barray, width, height):
    colors_flipped = bytearray()
    for y in range(height - 1, -1, -1):
        for x in range(width):
            # Get the pixel at (x, y)
            pixel_index = (y * width + x) * 4 #bytes_per_pixel in TGA32
            pixel = barray[pixel_index : pixel_index + 4]

            # Add the pixel to the flipped image
            colors_flipped.extend(pixel)
    return colors_flipped


def truecolor_tga_32_to_txr(filepath, bytes_per_pixel, image_type, image_format, gen_mipmap, transp_color):

    # gen_mipmap = False #Temporary
    outpath = os.path.splitext(filepath)[0] + ".txr"

    bit_masks = get_argb_bit_mask(image_format)

    a_msk = bit_masks[0]
    r_msk = bit_masks[1]
    g_msk = bit_masks[2]
    b_msk = bit_masks[3]

    if gen_mipmap:
        image_format = '1555'

    with open(filepath, "rb") as tga_file:
        colors_after = []
        header = list(struct.unpack("<3b2hb4h2b", tga_file.read(18)))
        header[0] = 12 #LOFF declaration
        header[5] = 16 #ColorMapEntrySize
        header[10] = 16 #PixelDepth
        header[11] = 32 #Image Descriptor
        width = header[8]
        height = header[9]
        colors_size = height*width
        colors_before = struct.unpack("<"+str(colors_size*4)+"B", tga_file.read(colors_size*4))

        colors_before = flip_tga_vert(bytearray(colors_before), width, height)

        colors_after = colors_byterray_convert(bytearray(colors_before), '8888', image_format, 'ARGB', 'ARGB', transp_color, True)
        if gen_mipmap:
            mipmaps = generate_mipmaps(bytearray(colors_before), width, height, '0565')

        footer = tga_file.read()
    with open(outpath, "wb") as txr_file:
        header_pack = struct.pack("<3b2hb4h2b", *header)
        colors_pack = struct.pack("<"+str(colors_size*bytes_per_pixel)+"B", *colors_after)

        loff_ms = txr_file.tell()
        txr_file.write(header_pack)
        txr_file.write('LOFF'.encode('cp1251'))
        txr_file.write(struct.pack("<i",4))
        loff_write_ms = txr_file.tell()
        txr_file.write(struct.pack("<i",0)) #LOFF reserved
        txr_file.write(colors_pack)
        write_size(txr_file, loff_ms, loff_write_ms)
        if gen_mipmap and len(mipmaps) > 1:
            txr_file.write('LVMP'.encode('cp1251'))
            lvmp_ms = txr_file.tell()
            txr_file.write(struct.pack("<i",0)) #LVMP reserved
            txr_file.write(struct.pack("<i", len(mipmaps)-1))
            txr_file.write(struct.pack("<i", len(mipmaps[1][0])))
            txr_file.write(struct.pack("<i", len(mipmaps[1])))
            txr_file.write(struct.pack("<i", 2))

            for m in range(1, len(mipmaps)):
                mipmap = mipmaps[m]
                m_width = len(mipmap)
                m_height = len(mipmap[0])
                mipmap_bytearray = bytearray(m_height * m_width * 4)
                for x in range(m_width):
                    for y in range(m_height): #BGRA
                        mipmap_bytearray[(x*m_width+y)*4:(x*m_width+y+1)*4] = struct.pack('>I', \
                            ((mipmap[x][y][0]) << 8) | \
                            ((mipmap[x][y][1]) << 16) | \
                            ((mipmap[x][y][2]) << 24) | \
                            ((mipmap[x][y][3]) << 0)  \
                        )

                mipmap_header = header
                mipmap_header[8] = m_width
                mipmap_header[9] = m_height
                filepath_no_ext = os.path.splitext(filepath)[0]
                #todo: check
                mipmap_path = "{}_{}-{}.tga".format(filepath_no_ext, m_width, m_height)
                write_tga8888(mipmap_path, mipmap_header, mipmap_bytearray, [\
                    0b00000000111111110000000000000000,\
                    0b00000000000000001111111100000000,\
                    0b00000000000000000000000011111111,\
                    0b11111111000000000000000000000000\
                ], transp_color, 4)

                converted_mipmap = colors_byterray_convert(mipmap_bytearray, '8888', '1555', 'ARGB', 'ARGB', transp_color)

                txr_file.write(converted_mipmap)
            write_size(txr_file, lvmp_ms)
            txr_file.write(struct.pack("<H", 0))

        # txr_file.write(footer)
        txr_file.write('PFRM'.encode('cp1251'))
        txr_file.write(struct.pack('<i', 16))
        txr_file.write(struct.pack('<i', r_msk))
        txr_file.write(struct.pack('<i', g_msk))
        txr_file.write(struct.pack('<i', b_msk))
        txr_file.write(struct.pack('<i', a_msk))
        txr_file.write('ENDR'.encode('cp1251'))


    return


def msk_to_tga32(filepath):
    outpath = os.path.splitext(filepath)[0] + ".tga"
    log.info("Converting {}".format(outpath))
    indexes = []
    colors_after = []
    with open(filepath, "rb") as msk_file:
        magic = msk_file.read(4).decode('cp1251')
        width = struct.unpack("<H", msk_file.read(2))[0]
        height = struct.unpack("<H", msk_file.read(2))[0]
        palette_size = 256
        palette = list(struct.unpack("<"+str(palette_size*3)+"B", msk_file.read(palette_size*3)))
        colors_size = width*height

        if magic == 'MS16':
            bytes_per_pixel = 2
        else: #MSKR, MSK8, MASK
            bytes_per_pixel = 1

        colors = decompress_rle(msk_file, width, height, bytes_per_pixel)

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
            footer_identifier = msk_file.read(4).decode('cp1251')
            if footer_identifier == 'PFRM':
                footer_size = struct.unpack("<i", msk_file.read(4))[0]
                pfrm = list(struct.unpack("<4i", msk_file.read(16)))
                continue

            elif footer_identifier == 'ENDR':
                msk_file.read(4) # alwas int 0
                continue

            msk_file.seek(-4, 1)
            break

        write_tga8888(outpath, header, colors, pfrm, (0,0,0), bytes_per_pixel)
