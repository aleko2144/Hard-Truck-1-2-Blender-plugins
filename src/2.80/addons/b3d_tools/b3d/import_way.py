import bpy
import struct
import os
import sys
import logging

from ..common import (
    recalcToLocalCoord,
    importway_logger
)

from ..consts import (
    BLOCK_TYPE,
    EMPTY_NAME
)

from .scripts import (
    prop
)

from .class_descr import (
    b_50,b_51,b_52
)

#Setup module logger
log = importway_logger

globalInd = None

def readBlockType(file):
    return file.read(4).decode("cp1251").rstrip('\0')

def readName(file, text_len):
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

def getNumberedName(name):
    global globalInd
    name = f"{globalInd:04d}|{name}"
    globalInd += 1
    return name

def importWay(file, context, filepath):
    # file_path = file
    # file = open(file, 'rb')

    global globalInd
    globalInd = 0

    ex = 0
    rootName = os.path.basename(filepath)
    # rootObject = None

    readingHeader = True
    moduleName = rootName

    while ex!=1:
        ex = openclose(file, filepath)
        if ex == 1:
            file.close()
            break

        elif ex == 2:

            global curRoom

            while readingHeader:
                subtype = readBlockType(file)

                if subtype == "WTWR":
                    log.debug("Reading type WTWR")
                    subtypeSize = struct.unpack("<i",file.read(4))[0]

                elif subtype == "MNAM":
                    log.debug("Reading type MNAM")
                    subtypeSize = struct.unpack("<i",file.read(4))[0]
                    moduleName = readName(file, subtypeSize)

                elif subtype == "GDAT":
                    log.debug("Reading type GDAT")
                    subtypeSize = struct.unpack("<i",file.read(4))[0]
                else:
                    readingHeader = False

                    rootName = f'{moduleName}.b3d'

                    rootObject = bpy.data.objects.get(rootName)
                    if rootObject is None:
                        rootObject = bpy.data.objects.new(rootName, None)
                        rootObject[BLOCK_TYPE] = 111 # 111
                        rootObject.name = rootName
                        rootObject.location=(0,0,0)
                        context.collection.objects.link(rootObject)

                    file.seek(-4, 1)

            type = readBlockType(file)

            if type == "GROM": #GROM
                log.debug("Reading type GROM")
                grom_size = struct.unpack("<i",file.read(4))[0]

                objName = ''
                subtype = readBlockType(file)
                if subtype == "RNAM":
                    log.debug("Reading subtype RNAM")
                    nameLen = struct.unpack("<i",file.read(4))[0]
                    objName = readName(file, nameLen)

                curObj = bpy.data.objects.get(objName)
                # for test
                # objName = getNumberedName(objName)
                if curObj is None:
                    curObj = bpy.data.objects.new(objName, None)
                    curObj.location=(0,0,0)
                    curObj[BLOCK_TYPE] = 19
                    curObj.parent = rootObject
                    context.collection.objects.link(curObj)

                curRoom = bpy.data.objects[curObj.name]

            elif type == "RSEG": #RSEG
                log.debug("Reading type RSEG")
                rseg_size = struct.unpack("<i",file.read(4))[0]
                rseg_size_cur = rseg_size

                points = []
                attr1 = None
                attr2 = None
                attr3 = None
                wdth1 = None
                wdth2 = None
                unkName = ''

                while rseg_size_cur > 0:
                    subtype = readBlockType(file)
                    subtypeSize = struct.unpack("<i",file.read(4))[0]

                    if subtype == "ATTR":
                        log.debug("Reading subtype ATTR")
                        attr1 = struct.unpack("<i",file.read(4))[0]
                        attr2 = struct.unpack("<d",file.read(8))[0]
                        attr3 = struct.unpack("<i",file.read(4))[0]

                        rseg_size_cur -= (subtypeSize+8) #subtype+subtypeSize

                    elif subtype == "WDTH":
                        log.debug("Reading subtype WDTH")
                        wdth1 = struct.unpack("<d",file.read(8))[0]
                        wdth2 = struct.unpack("<d",file.read(8))[0]

                        log.debug(f"WDTH: {str(wdth1)} {str(wdth2)}")

                        rseg_size_cur -= (subtypeSize+8) #subtype+subtypeSize

                    elif subtype == "VDAT":
                        log.debug("Reading subtype VDAT")
                        len_points = struct.unpack("<i",file.read(4))[0]
                        for i in range (len_points):
                            points.append(struct.unpack("ddd",file.read(24)))

                        rseg_size_cur -= (subtypeSize+8) #subtype+subtypeSize

                    elif subtype == "RTEN":
                        log.debug("Reading subtype RTEN")
                        unkName = readName(file, subtypeSize)

                        subtypeSize = ((subtypeSize >> 2) + 1) * 4

                        rseg_size_cur -= (subtypeSize+8) #subtype+subtypeSize

                if len(points):

                    curveData = bpy.data.curves.new('curve', type='CURVE')

                    curveData.dimensions = '3D'
                    curveData.resolution_u = 2

                    newPoints = recalcToLocalCoord(points[0], points)

                    polyline = curveData.splines.new('POLY')
                    polyline.points.add(len(newPoints)-1)
                    for i, coord in enumerate(newPoints):
                        x,y,z = coord
                        polyline.points[i].co = (x, y, z, 1)


                    curveData.bevel_depth = 0.3
                    curveData.bevel_mode = 'ROUND'
                    objName = EMPTY_NAME
                    # objName = getNumberedName(EMPTY_NAME)
                    curObj = bpy.data.objects.new(objName, curveData)
                    # curveData.bevel_mode = ''

                    curObj.location = (points[0])
                    curObj[BLOCK_TYPE] = 50
                    curObj[prop(b_50.Attr1)] = attr1
                    curObj[prop(b_50.Attr2)] = attr2
                    curObj[prop(b_50.Attr3)] = attr3
                    curObj[prop(b_50.Width1)] = wdth1
                    curObj[prop(b_50.Width2)] = wdth2
                    curObj[prop(b_50.Rten)] = unkName
                    curObj.parent = curRoom
                    context.collection.objects.link(curObj)

            elif type == "RNOD": #RNOD
                log.debug("Reading type RNOD")
                rnod_size = struct.unpack("<i",file.read(4))[0]
                rnod_size_cur = rnod_size

                objName = ''
                object_matrix = None
                pos = None
                flag = None

                cur_pos = (0.0,0.0,0.0)

                while rnod_size_cur > 0:
                    subtype = readBlockType(file)
                    subtypeSize = struct.unpack("<i",file.read(4))[0]
                    if subtype == "NNAM":
                        log.debug("Reading subtype NNAM")
                        objName = readName(file, subtypeSize)

                        realSize = ((subtypeSize >> 2) + 1) * 4
                        rnod_size_cur -= (realSize+8) #subtype+subtypeSize
                    elif subtype == "POSN":
                        log.debug("Reading subtype POSN")
                        pos = struct.unpack("ddd",file.read(24))

                        rnod_size_cur -= (subtypeSize+8) #subtype+subtypeSize
                    elif subtype == "ORTN":
                        log.debug("Reading subtype ORTN")
                        object_matrix = []
                        for i in range(4):
                            object_matrix.append(struct.unpack("<ddd",file.read(24)))

                        rnod_size_cur -= (subtypeSize+8) #subtype+subtypeSize
                    elif subtype == "FLAG":
                        log.debug("Reading subtype FLAG")
                        flag = struct.unpack("<i",file.read(4))[0]

                        rnod_size_cur -= (subtypeSize+8) #subtype+subtypeSize

                    if object_matrix is not None:
                        cur_pos = object_matrix[3]
                    elif pos is not None:
                        cur_pos = pos

                # objName = getNumberedName(objName)
                curObj = bpy.data.objects.new(objName, None)
                if object_matrix is not None:
                    curObj[BLOCK_TYPE] = 52
                    curObj[prop(b_52.Flag)] = flag
                    curObj.empty_display_type = 'ARROWS'
                    for i in range(3):
                        for j in range(3):
                            curObj.matrix_world[i][j] = object_matrix[j][i]
                else:
                    curObj[BLOCK_TYPE] = 51
                    curObj[prop(b_51.Flag)] = flag
                    curObj.empty_display_type = 'PLAIN_AXES'
                curObj.empty_display_size = 5
                curObj.location = cur_pos
                curObj.parent = curRoom
                context.collection.objects.link(curObj)
            else:
                log.error(f"Unknown type: {type} on position {str(file.tell())}")

