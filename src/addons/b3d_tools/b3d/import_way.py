import bpy
import struct
import os
import sys
import logging

from ..common import (
    recalc_to_local_coord,
    importway_logger
)

from ..consts import (
    BLOCK_TYPE,
    EMPTY_NAME
)

from .class_descr import (
    Blk050,Blk051,Blk052
)

from ..compatibility import (
    get_context_collection_objects,
    get_or_create_collection,
    is_before_2_80,
    set_empty_type,
    set_empty_size
)

#Setup module logger
log = importway_logger

global_ind = None

def read_block_type(file):
    return file.read(4).decode("cp1251").rstrip('\0')

def read_name(file, text_len):
    # text_len = 0
    str_len = 0
    fill_len = 0
    if text_len % 4:
        fill_len = ((text_len >> 2) + 1) * 4 - text_len

    string = file.read(text_len).decode("cp1251").rstrip('\0')
    if fill_len > 0:
        file.seek(fill_len, 1)
    return string

def openclose(file, path):
    if file.tell() == os.path.getsize(path):
        log.debug ('EOF')
        return 1
    else:
        return 2

def get_numbered_name(name):
    global global_ind
    name = "{:04d}|{}".format(global_ind, name)
    global_ind += 1
    return name

def import_way(file, context, filepath):
    # file_path = file
    # file = open(file, 'rb')

    global global_ind
    global_ind = 0

    ex = 0
    root_name = os.path.basename(filepath)
    # root_object = None

    reading_header = True
    module_name = root_name

    while ex!=1:
        ex = openclose(file, filepath)
        if ex == 1:
            file.close()
            break

        elif ex == 2:

            global curRoom

            while reading_header:
                subtype = read_block_type(file)

                if subtype == "WTWR":
                    log.debug("Reading type WTWR")
                    subtype_size = struct.unpack("<i",file.read(4))[0]

                elif subtype == "MNAM":
                    log.debug("Reading type MNAM")
                    subtype_size = struct.unpack("<i",file.read(4))[0]
                    module_name = read_name(file, subtype_size)

                elif subtype == "GDAT":
                    log.debug("Reading type GDAT")
                    subtype_size = struct.unpack("<i",file.read(4))[0]
                else:
                    reading_header = False

                    root_name = '{}.b3d'.format(module_name)

                    root_object = bpy.data.objects.get(root_name)
                    if root_object is None:
                        root_object = bpy.data.objects.new(root_name, None)
                        root_object[BLOCK_TYPE] = 111 # 111
                        root_object.name = root_name
                        root_object.location=(0,0,0)
                        get_context_collection_objects(context).link(root_object)

                    file.seek(-4, 1)

            block_type = read_block_type(file)

            if block_type == "GROM": #GROM
                log.debug("Reading type GROM")
                grom_size = struct.unpack("<i",file.read(4))[0]

                obj_name = ''
                subtype = read_block_type(file)
                if subtype == "RNAM":
                    log.debug("Reading subtype RNAM")
                    name_len = struct.unpack("<i",file.read(4))[0]
                    obj_name = read_name(file, name_len)

                cur_obj = bpy.data.objects.get(obj_name)
                # for test
                # obj_name = get_numbered_name(obj_name)
                if cur_obj is None:
                    cur_obj = bpy.data.objects.new(obj_name, None)
                    cur_obj.location=(0,0,0)
                    cur_obj[BLOCK_TYPE] = 19
                    cur_obj.parent = root_object
                    get_context_collection_objects(context).link(cur_obj)

                curRoom = bpy.data.objects[cur_obj.name]

            elif block_type == "RSEG": #RSEG
                log.debug("Reading type RSEG")
                rseg_size = struct.unpack("<i",file.read(4))[0]
                rseg_size_cur = rseg_size

                points = []
                attr1 = None
                attr2 = None
                attr3 = None
                wdth1 = None
                wdth2 = None
                unk_name = ''

                while rseg_size_cur > 0:
                    subtype = read_block_type(file)
                    subtype_size = struct.unpack("<i",file.read(4))[0]

                    if subtype == "ATTR":
                        log.debug("Reading subtype ATTR")
                        attr1 = struct.unpack("<i",file.read(4))[0]
                        attr2 = struct.unpack("<d",file.read(8))[0]
                        attr3 = struct.unpack("<i",file.read(4))[0]

                        rseg_size_cur -= (subtype_size+8) #subtype+subtype_size

                    elif subtype == "WDTH":
                        log.debug("Reading subtype WDTH")
                        wdth1 = struct.unpack("<d",file.read(8))[0]
                        wdth2 = struct.unpack("<d",file.read(8))[0]

                        log.debug("WDTH: {} {}".format(str(wdth1), str(wdth2)))

                        rseg_size_cur -= (subtype_size+8) #subtype+subtype_size

                    elif subtype == "VDAT":
                        log.debug("Reading subtype VDAT")
                        len_points = struct.unpack("<i",file.read(4))[0]
                        for i in range (len_points):
                            points.append(struct.unpack("ddd",file.read(24)))

                        rseg_size_cur -= (subtype_size+8) #subtype+subtype_size

                    elif subtype == "RTEN":
                        log.debug("Reading subtype RTEN")
                        unk_name = read_name(file, subtype_size)

                        subtype_size = ((subtype_size >> 2) + 1) * 4

                        rseg_size_cur -= (subtype_size+8) #subtype+subtype_size

                if len(points):

                    curve_data = bpy.data.curves.new('curve', type='CURVE')

                    curve_data.dimensions = '3D'
                    curve_data.resolution_u = 2

                    new_points = recalc_to_local_coord(points[0], points)

                    polyline = curve_data.splines.new(type='NURBS')
                    polyline.points.add(len(new_points)-1)
                    for i, coord in enumerate(new_points):
                        x,y,z = coord
                        polyline.points[i].co = (x, y, z, 1)

                    polyline.order_u = 4
                    polyline.use_endpoint_u = True
                    obj_name = EMPTY_NAME
                    # obj_name = get_numbered_name(EMPTY_NAME)
                    cur_obj = bpy.data.objects.new(obj_name, curve_data)
                    
                    cur_obj.location = (points[0])
                    cur_obj[BLOCK_TYPE] = 50
                    cur_obj[Blk050.Attr1.get_prop()] = attr1
                    cur_obj[Blk050.Attr2.get_prop()] = attr2
                    cur_obj[Blk050.Attr3.get_prop()] = attr3
                    cur_obj[Blk050.Width1.get_prop()] = wdth1
                    cur_obj[Blk050.Width2.get_prop()] = wdth2
                    cur_obj[Blk050.Rten.get_prop()] = unk_name
                    cur_obj.parent = curRoom
                    get_context_collection_objects(context).link(cur_obj)

            elif block_type == "RNOD": #RNOD
                log.debug("Reading type RNOD")
                rnod_size = struct.unpack("<i",file.read(4))[0]
                rnod_size_cur = rnod_size

                obj_name = ''
                object_matrix = None
                pos = None
                flag = None

                cur_pos = (0.0,0.0,0.0)

                while rnod_size_cur > 0:
                    subtype = read_block_type(file)
                    subtype_size = struct.unpack("<i",file.read(4))[0]
                    if subtype == "NNAM":
                        log.debug("Reading subtype NNAM")
                        obj_name = read_name(file, subtype_size)

                        real_size = ((subtype_size >> 2) + 1) * 4
                        rnod_size_cur -= (real_size+8) #subtype+subtype_size
                    elif subtype == "POSN":
                        log.debug("Reading subtype POSN")
                        pos = struct.unpack("ddd",file.read(24))

                        rnod_size_cur -= (subtype_size+8) #subtype+subtype_size
                    elif subtype == "ORTN":
                        log.debug("Reading subtype ORTN")
                        object_matrix = []
                        for i in range(4):
                            object_matrix.append(struct.unpack("<ddd",file.read(24)))

                        rnod_size_cur -= (subtype_size+8) #subtype+subtype_size
                    elif subtype == "FLAG":
                        log.debug("Reading subtype FLAG")
                        flag = struct.unpack("<i",file.read(4))[0]

                        rnod_size_cur -= (subtype_size+8) #subtype+subtype_size

                    if object_matrix is not None:
                        cur_pos = object_matrix[3]
                    elif pos is not None:
                        cur_pos = pos

                # obj_name = get_numbered_name(obj_name)
                cur_obj = bpy.data.objects.new(obj_name, None)
                if object_matrix is not None:
                    cur_obj[BLOCK_TYPE] = 52
                    cur_obj[Blk052.Flag.get_prop()] = flag
                    set_empty_type(cur_obj, 'ARROWS')
                    for i in range(3):
                        for j in range(3):
                            cur_obj.matrix_world[i][j] = object_matrix[j][i]
                else:
                    cur_obj[BLOCK_TYPE] = 51
                    cur_obj[Blk051.Flag.get_prop()] = flag
                    set_empty_type(cur_obj, 'PLAIN_AXES')
                set_empty_size(cur_obj, 5)
                cur_obj.location = cur_pos
                cur_obj.parent = curRoom
                get_context_collection_objects(context).link(cur_obj)
            else:
                log.error("Unknown type: {} on position {}".format(block_type, str(file.tell())))

