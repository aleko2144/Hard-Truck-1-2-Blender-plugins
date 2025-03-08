import bpy
import struct
import os

from .common import (
    is_root_obj,
    get_non_copy_name,
    get_not_numeric_name,
    BLOCK_TYPE,
    write_size
)

from ..common import (
    exportway_logger
)

from .class_descr import (
    Blk050, Blk051, Blk052
)

from ..compatibility import (
    matrix_multiply
)

#Setup module logger
log = exportway_logger


def write_name(file, name):
    name = name.rstrip('\0') + '\0'
    name_len = len(name)
    fill_len = 0
    if name_len % 4:
        fill_len = ((name_len >> 2) + 1) * 4 - name_len
    file.write(name.encode('cp1251'))
    file.write(b"\x00" * fill_len)


def write_type(file, type_abbr):
    file.write(type_abbr.encode('cp1251'))


def write_nam(file, type_abbr, name):
    write_type(file, type_abbr)
    name = get_not_numeric_name(name)
    file.write(struct.pack('<i', len(name)+1))
    write_name(file, name)


def write_attr(file, block):
    write_type(file, "ATTR")
    file.write(struct.pack('<i', 16))
    file.write(struct.pack('<i', block.get(Blk050.Attr1.get_prop())))
    file.write(struct.pack('<d', block.get(Blk050.Attr2.get_prop())))
    file.write(struct.pack('<i', block.get(Blk050.Attr3.get_prop())))


def write_rten(file, block):
    rten_name = block.get(Blk050.Rten.get_prop())
    if rten_name is not None and len(rten_name) > 0:
        write_nam(file, "RTEN", rten_name)


def write_wdth(file, block):
    write_type(file, "WDTH")
    file.write(struct.pack('<i', 16))
    file.write(struct.pack('<d', block.get(Blk050.Width1.get_prop())))
    file.write(struct.pack('<d', block.get(Blk050.Width2.get_prop())))

def write_vdat(file, block):
    write_type(file, "VDAT")
    points = block.data.splines[0].points
    file.write(struct.pack("<i", 4+len(points)*24))
    file.write(struct.pack("<i", len(points)))
    for point in points:
        file.write(struct.pack("<ddd", *(matrix_multiply(block.matrix_world, point.co.xyz))))


def write_ortn(file, block):
    write_type(file, "ORTN")
    file.write(struct.pack('<i', 96))
    for i in range(3): #ortn
        for j in range(3):
            file.write(struct.pack("<d", block.matrix_world[j][i]))
    file.write(struct.pack("<ddd", *block.location))


def write_posn(file, block):
    write_type(file, "POSN")
    file.write(struct.pack('<i', 24))
    file.write(struct.pack("<ddd", *block.location))


def export_way(context, op, export_dir):

    exported_modules = [sn.name for sn in op.res_modules if sn.state == True]
    if not os.path.isdir(export_dir):
        export_dir = os.path.dirname(export_dir)

    for obj_name in exported_modules:

        filepath = os.path.join(export_dir, "{}.way".format(obj_name))

        file = open(filepath, 'wb')

        root_obj = bpy.data.objects["{}.b3d".format(obj_name)]

        #Header
        write_type(file, "WTWR")
        wtwr_write_ms = file.tell()
        file.write(struct.pack("<i", 0))
        wtwr_ms = file.tell()
        write_nam(file, "MNAM", obj_name)
        write_type(file, "GDAT")
        gdat_write_ms = file.tell()
        file.write(struct.pack("<i", 0))
        gdat_ms = file.tell()

        rooms = [cn for cn in root_obj.children if cn.get(BLOCK_TYPE) == 19]

        for room in rooms:
            segs = [cn for cn in room.children if cn.get(BLOCK_TYPE) in [50]]
            nodes = [cn for cn in room.children if cn.get(BLOCK_TYPE) in [51,52]]
            ways = []
            ways.extend(nodes)
            ways.extend(segs)

            if len(ways) > 0:
                write_type(file, "GROM")
                grom_write_ms = file.tell()
                file.write(struct.pack("<i", 0))
                grom_ms = file.tell()
                write_nam(file, "RNAM", room.name)
                for way_obj in ways:
                    way_name = get_non_copy_name(way_obj.name)
                    obj_type = way_obj.get(BLOCK_TYPE)
                    if obj_type == 50:
                        write_type(file, "RSEG")
                        rseg_write_ms = file.tell()
                        file.write(struct.pack("<i", 0))
                        rseg_ms = file.tell()
                        write_attr(file, way_obj)
                        write_wdth(file, way_obj)
                        write_rten(file, way_obj)
                        write_vdat(file, way_obj)
                        write_size(file, rseg_ms, rseg_write_ms)
                    elif obj_type == 51:
                        write_type(file, "RNOD")
                        rnod_write_ms = file.tell()
                        file.write(struct.pack("<i", 0))
                        rnod_ms = file.tell()
                        write_nam(file, "NNAM", way_name)
                        write_posn(file, way_obj)
                        # flag
                        write_type(file, "FLAG")
                        file.write(struct.pack("<i", 4))
                        file.write(struct.pack("<i", way_obj[Blk051.Flag.get_prop()]))
                        write_size(file, rnod_ms, rnod_write_ms)
                    elif obj_type == 52:
                        write_type(file, "RNOD")
                        rnod_write_ms = file.tell()
                        file.write(struct.pack("<i", 0))
                        rnod_ms = file.tell()
                        write_nam(file, "NNAM", way_name)
                        write_posn(file, way_obj)
                        write_ortn(file, way_obj)
                        # flag
                        write_type(file, "FLAG")
                        file.write(struct.pack("<i", 4))
                        file.write(struct.pack("<i", way_obj[Blk052.Flag.get_prop()]))
                        write_size(file, rnod_ms, rnod_write_ms)

                write_size(file, grom_ms, grom_write_ms)

        write_size(file, gdat_ms, gdat_write_ms)
        write_size(file, wtwr_ms, wtwr_write_ms)

        file.close()

    return {'FINISHED'}
