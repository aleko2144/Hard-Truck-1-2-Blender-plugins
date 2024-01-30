import bpy
import struct
import os

from ..common import (
    log
)

from .common import (
    isRootObj,
    getNonCopyName,
    getNotNumericName,
    BLOCK_TYPE,
    writeSize
)

from .scripts import (
    prop
)

from .class_descr import (
    b_50, b_51, b_52
)


def writeName(file, name):
    name = name.rstrip('\0') + '\0'
    nameLen = len(name)
    fillLen = 0
    if nameLen % 4:
        fillLen = ((nameLen >> 2) + 1) * 4 - nameLen
    file.write(name.encode('cp1251'))
    file.write(b"\x00" * fillLen)


def writeType(file, type):
    file.write(type.encode('cp1251'))


def write_NAM(file, type, name):
    writeType(file, type)
    name = getNotNumericName(name)
    file.write(struct.pack('<i', len(name)+1))
    writeName(file, name)


def writeATTR(file, block):
    writeType(file, "ATTR")
    file.write(struct.pack('<i', 16))
    file.write(struct.pack('<i', block.get(prop(b_50.Attr1))))
    file.write(struct.pack('<d', block.get(prop(b_50.Attr2))))
    file.write(struct.pack('<i', block.get(prop(b_50.Attr3))))


def writeRTEN(file, block):
    rten_name = block.get(prop(b_50.Rten))
    if rten_name is not None and len(rten_name) > 0:
        write_NAM(file, type, "RTEN")


def writeWDTH(file, block):
    writeType(file, "WDTH")
    file.write(struct.pack('<i', 16))
    file.write(struct.pack('<d', block.get(prop(b_50.Width1))))
    file.write(struct.pack('<d', block.get(prop(b_50.Width2))))

def writeVDAT(file, block):
    writeType(file, "VDAT")
    points = block.data.splines[0].points
    file.write(struct.pack("<i", 4+len(points)*24))
    file.write(struct.pack("<i", len(points)))
    for point in points:
        file.write(struct.pack("<ddd", *(block.matrix_world @ point.co.xyz)))


def writeORTN(file, block):
    writeType(file, "ORTN")
    file.write(struct.pack('<i', 96))
    for i in range(3): #ortn
        for j in range(3):
            file.write(struct.pack("<d", block.matrix_world[j][i]))
    file.write(struct.pack("<ddd", *block.location))


def writePOSN(file, block):
    writeType(file, "POSN")
    file.write(struct.pack('<i', 24))
    file.write(struct.pack("<ddd", *block.location))


def exportWay(context, op, exportDir):

    exportedModules = [sn.name for sn in op.res_modules if sn.state == True]
    if not os.path.isdir(exportDir):
        exportDir = os.path.dirname(exportDir)

    for objName in exportedModules:

        filepath = os.path.join(exportDir, "{}.way".format(objName))

        file = open(filepath, 'wb')

        rootObj = bpy.data.objects["{}.b3d".format(objName)]

        #Header
        writeType(file, "WTWR")
        WTWR_write_ms = file.tell()
        file.write(struct.pack("<i", 0))
        WTWR_ms = file.tell()
        write_NAM(file, "MNAM", objName)
        writeType(file, "GDAT")
        GDAT_write_ms = file.tell()
        file.write(struct.pack("<i", 0))
        GDAT_ms = file.tell()

        rooms = [cn for cn in rootObj.children if cn.get(BLOCK_TYPE) == 19]

        for room in rooms:
            segs = [cn for cn in room.children if cn.get(BLOCK_TYPE) in [50]]
            nodes = [cn for cn in room.children if cn.get(BLOCK_TYPE) in [51,52]]
            ways = []
            ways.extend(nodes)
            ways.extend(segs)

            if len(ways) > 0:
                writeType(file, "GROM")
                GROM_write_ms = file.tell()
                file.write(struct.pack("<i", 0))
                GROM_ms = file.tell()
                write_NAM(file, "RNAM", room.name)
                for wayObj in ways:
                    wayName = getNonCopyName(wayObj.name)
                    type = wayObj.get(BLOCK_TYPE)
                    if type == 50:
                        writeType(file, "RSEG")
                        RSEG_write_ms = file.tell()
                        file.write(struct.pack("<i", 0))
                        RSEG_ms = file.tell()
                        writeATTR(file, wayObj)
                        writeWDTH(file, wayObj)
                        writeRTEN(file, wayObj)
                        writeVDAT(file, wayObj)
                        writeSize(file, RSEG_ms, RSEG_write_ms)
                    elif type == 51:
                        writeType(file, "RNOD")
                        RNOD_write_ms = file.tell()
                        file.write(struct.pack("<i", 0))
                        RNOD_ms = file.tell()
                        write_NAM(file, "NNAM", wayName)
                        writePOSN(file, wayObj)
                        # flag
                        writeType(file, "FLAG")
                        file.write(struct.pack("<i", 4))
                        file.write(struct.pack("<i", wayObj[prop(b_51.Flag)]))
                        writeSize(file, RNOD_ms, RNOD_write_ms)
                    elif type == 52:
                        writeType(file, "RNOD")
                        RNOD_write_ms = file.tell()
                        file.write(struct.pack("<i", 0))
                        RNOD_ms = file.tell()
                        write_NAM(file, "NNAM", wayName)
                        writePOSN(file, wayObj)
                        writeORTN(file, wayObj)
                        # flag
                        writeType(file, "FLAG")
                        file.write(struct.pack("<i", 4))
                        file.write(struct.pack("<i", wayObj[prop(b_52.Flag)]))
                        writeSize(file, RNOD_ms, RNOD_write_ms)

                writeSize(file, GROM_ms, GROM_write_ms)

        writeSize(file, GDAT_ms, GDAT_write_ms)
        writeSize(file, WTWR_ms, WTWR_write_ms)

        file.close()

    return {'FINISHED'}


def SetBytesLength(object, root):
    if (not root):
        if object.name[0:4] == 'VDAT':
            for subcurve in object.data.splines:
                bytes_len = (len(subcurve.points) * 24) + 4 + 4 + 4
            object['bytes_len'] = bytes_len
            object['c_bytes_len'] = 0

        if object.name[0:4] == 'ATTR':
            bytes_len = 24
            object['bytes_len'] = bytes_len
            object['c_bytes_len'] = 0

        elif object.name[0:4] == 'WDTH':
            bytes_len = 24
            object['bytes_len'] = bytes_len
            object['c_bytes_len'] = 0

        elif object.name[0:4] == 'ORTN':
            bytes_len = 96
            object['bytes_len'] = bytes_len
            object['c_bytes_len'] = 0

        elif object.name[0:4] == 'POSN':
            bytes_len = 32
            object['bytes_len'] = bytes_len
            object['c_bytes_len'] = 0

        elif object.name[0:4] == 'RSEG':
            bytes_len = 8
            object['bytes_len'] = bytes_len
            object['c_bytes_len'] = 0

        elif object.name[0:4] == 'RNAM':

            text_len = 0

            if (len(str(object['str'])) > 15):
                text_len = 20

            elif (11 < len(str(object['str'])) < 15 or len(str(object['str'])) == 15):
                text_len = 16

            elif (7 < len(str(object['str'])) < 11 or len(str(object['str'])) == 11):
                text_len = 12

            elif (3 < len(str(object['str'])) < 7 or len(str(object['str'])) == 7):
                text_len = 8

            elif (len(str(object['str'])) < 3 or len(str(object['str'])) == 3):
                text_len = 4

            bytes_len = 8 + text_len

            object['bytes_len'] = bytes_len
            object['c_bytes_len'] = 0

        elif object.name[0:4] == 'RNOD':
            bytes_len = 8
            object['bytes_len'] = bytes_len
            object['c_bytes_len'] = 0

        elif object.name[0:4] == 'NNAM':
            text_len = 0

            if (len(str(object['str'])) > 15):
                text_len = 20

            elif (11 < len(str(object['str'])) < 15 or len(str(object['str'])) == 15):
                text_len = 16

            elif (7 < len(str(object['str'])) < 11 or len(str(object['str'])) == 11):
                text_len = 12

            elif (3 < len(str(object['str'])) < 7 or len(str(object['str'])) == 7):
                text_len = 8

            elif (len(str(object['str'])) < 3 or len(str(object['str'])) == 3):
                text_len = 4

            bytes_len = 8 + text_len
            object['bytes_len'] = bytes_len
            object['c_bytes_len'] = 0

        elif object.name[0:4] == 'GROM':
            bytes_len = 8
            object['bytes_len'] = bytes_len
            object['c_bytes_len'] = 0

        elif object.name[0:4] == 'GDAT':
            bytes_len = 8
            object['bytes_len'] = bytes_len
            object['c_bytes_len'] = 0

        elif object.name[0:4] == 'MNAM':
            text_len = 0

            if (len(str(object['str'])) > 15):
                text_len = 20

            elif (11 < len(str(object['str'])) < 15 or len(str(object['str'])) == 15):
                text_len = 16

            elif (7 < len(str(object['str'])) < 11 or len(str(object['str'])) == 11):
                text_len = 12

            elif (3 < len(str(object['str'])) < 7 or len(str(object['str'])) == 7):
                text_len = 8

            elif (len(str(object['str'])) < 3 or len(str(object['str'])) == 3):
                text_len = 4

            bytes_len = 8 + text_len
            object['bytes_len'] = bytes_len
            object['c_bytes_len'] = 0

        elif object.name[0:4] == 'WTWR':
            bytes_len = 8
            object['bytes_len'] = bytes_len
            object['c_bytes_len'] = 0

        elif object.name[0:4] == 'FLAG':
            bytes_len = 12
            object['bytes_len'] = bytes_len
            object['c_bytes_len'] = 0
            #object['flag'] = 1

    for child in object.children:
        SetBytesLength(child,False)


def SetCBytesLength(object, root):
    varCB = 0
    if (not root):
        if object.name[0:4] == 'RSEG':
            bytes_len = 8

        elif object.name[0:4] == 'RNOD':
            for x in range (len(object.children)):
                varCB += object.children[x]['bytes_len']

            object['c_bytes_len'] = varCB

    for child in object.children:
        SetCBytesLength(child,False)

def SetRS(object, root):
    varRS = 0
    if (not root):
        if object.name[0:4] == 'RSEG':
            for r in range (len(object.children)):
                varRS += object.children[r]['bytes_len'] + object.children[r]['c_bytes_len']

            object['c_bytes_len'] = varRS

    for child in object.children:
        SetRS(child, False)

def SetGR(object, root):
    varGR = 0
    if (not root):
        if object.name[0:4] == 'GROM':
            for j in range (len(object.children)):
                varGR += object.children[j]['bytes_len'] + object.children[j]['c_bytes_len']

            object['c_bytes_len'] = varGR

    for child in object.children:
        SetGR(child, False)

def SetGD(object, root):
    variable = 0
    if (not root):
        if object.name[0:4] == 'GDAT':
            for n in range (len(object.children)):
                variable += object.children[n]['bytes_len'] + object.children[n]['c_bytes_len']

            object['c_bytes_len'] = variable

    for child in object.children:
        SetGD(child, False)

def SetMN(object, root):
    varMN = 0
    if (not root):
        if object.name[0:4] == 'MNAM':
            for i in range (len(object.children)):
                varMN = object.children[i]['bytes_len'] + object.children[i]['c_bytes_len']

            object['c_bytes_len'] = varMN

    for child in object.children:
        SetMN(child, False)

def SetWT(object, root):
    varWT = 0
    if (not root):
        if object.name[0:4] == 'WTWR':
            for i in range (len(object.children)):
                varWT = object.children[i]['bytes_len'] + object.children[i]['c_bytes_len']

            object['c_bytes_len'] = varWT

    for child in object.children:
        SetWT(child, False)


def GetCBytesLength(object, root):
    var1 = 0
    if (not root):
        #for object in bpy.data.objects:
        if (object.children):
            for i in range (len(object.children)):
                var1 = object.children[i]['bytes_len'] + object['bytes_len']
                #object['c_bytes_len'] = var1
                object['c_bytes_len'] = var1 + object['c_bytes_len']
            print(str(var1))

    for child in object.children:
        GetCBytesLength(child,False)

def SetRSEGBytes(object, root):
    if (not root):
        if object['type'] == 'rseg':
            for subcurve in object.data.splines:
                object['bytes_len'] = 68 + len(subcurve.points) * 24

            room = object.parent
            room['c_bytes_len'] += object['bytes_len']

    for child in object.children:
        SetRSEGBytes(child, False)

def SetNodeBytes(object, root):
    var_node = 0
    print("SetNodeBytes")
    try:
        if object['type'] == 'rnod' or object['type'] == 'ortn':
            object_name = object.name.split(".")[0]
            text_len1 = 0
            if (len(str(object_name)) > 15):
                text_len1 = 20

            elif (11 < len(str(object_name)) < 15 or len(str(object_name)) == 15):
                text_len1 = 16

            elif (7 < len(str(object_name)) < 11 or len(str(object_name)) == 11):
                text_len1 = 12

            elif (3 < len(str(object_name)) < 7 or len(str(object_name)) == 7):
                text_len1 = 8

            elif (len(str(object_name)) < 3 or len(str(object_name)) == 3):
                text_len1 = 4

            var_node = text_len1 + 16 + 32 + 12
            if object['type'] == "ortn":
                var_node += 104
            object['bytes_len'] = var_node

            #object.parent['c_bytes_len'] += var_node
            room = object.parent
            room['c_bytes_len'] += var_node

        for child in object.children:
            SetNodeBytes(child, False)
    except:
        pass

def SetRoomBytes(object, root):
    var_r = 0
    if object['type'] == 'room':
        object_name = object.name.split(".")[0]
        text_len1 = 0
        if (len(str(object_name)) > 15):
            text_len1 = 20

        elif (11 < len(str(object_name)) < 15 or len(str(object_name)) == 15):
            text_len1 = 16

        elif (7 < len(str(object_name)) < 11 or len(str(object_name)) == 11):
            text_len1 = 12

        elif (3 < len(str(object_name)) < 7 or len(str(object_name)) == 7):
            text_len1 = 8

        elif (len(str(object_name)) < 3 or len(str(object_name)) == 3):
            text_len1 = 4

        var_r = text_len1 + 16

        object['bytes_len'] = var_r #+ 8

        #way = object.parent
        #way['c_bytes_len'] += object['bytes_len']

    for child in object.children:
        SetRoomBytes(child, False)

def SetWayBytes(object, root):
    if object['type'] == 'room':
        way = object.parent
        print(object['bytes_len'])
        way['c_bytes_len'] = way['c_bytes_len'] + object['c_bytes_len'] + object['bytes_len']

    for child in object.children:
        SetWayBytes(child, False)

def SetWayBytes1(object, root):
    if object['type'] == 'way':
        object['bytes_len'] = 20 + object['c_bytes_len']

    for child in object.children:
        SetWayBytes1(child, False)


def ClearBytes(object, root):
    if object['type'] == 'room':
        object['bytes_len'] = 0
        object['c_bytes_len'] = 0

    if object['type'] == 'way':
        object['bytes_len'] = 0
        object['c_bytes_len'] = 0

    for child in object.children:
        ClearBytes(child, False)

def writeWTWR(object, file):
    file.write(str.encode('WTWR'))
    file.write(struct.pack("<i", object['bytes_len']))

    file.write(str.encode('MNAM'))
    file.write(struct.pack("<i", len(str(object['mnam'])) + 1))
    file.write(str.encode(str(object['mnam']))+bytearray(b'\x00'*2))

    file.write(str.encode('GDAT'))
    file.write(struct.pack("<i", object['c_bytes_len']))

def forChild(object, root, file):
    if (not root):
        #for object in bpy.data.objects:
        bytes_len = 0
        obj_len = len(object.children)
        if object['type'] == 'rseg':
            file.write(str.encode('RSEG'))

            for subcurve in object.data.splines:
                object['bytes_len'] = 68 + len(subcurve.points) * 24
                object['c_bytes_len'] = 60 + len(subcurve.points) * 24
                file.write(struct.pack("<i", object['c_bytes_len']))

            file.write(str.encode('ATTR'))
            file.write(struct.pack("<i", 16))
            file.write(struct.pack("<i", object['attr1']))
            file.write(struct.pack("<d", object['attr2']))
            file.write(struct.pack("<i", object['attr3']))

            file.write(str.encode('WDTH'))
            file.write(struct.pack("<i", 16))
            file.write(struct.pack("<d", object['wdth']))
            file.write(struct.pack("<d", object['wdth']))

            for subcurve in object.data.splines:
                file.write(str.encode('VDAT'))
                bytes_len = (len(subcurve.points) * 24) + 4
                file.write(struct.pack("<i",bytes_len))
                file.write(struct.pack("<i",len(subcurve.points)))
            for point in subcurve.points:
                file.write(struct.pack("<d",point.co.x))
                file.write(struct.pack("<d",point.co.y))
                file.write(struct.pack("<d",point.co.z))

        elif object['type'] == 'rnod' or object['type'] == "ortn":
            file.write(str.encode('RNOD'))
            object_name = object.name.split(".")[0]
            text_len1 = 0
            if (len(str(object_name)) > 15):
                text_len1 = 20

            elif (11 < len(str(object_name)) < 15 or len(str(object_name)) == 15):
                text_len1 = 16

            elif (7 < len(str(object_name)) < 11 or len(str(object_name)) == 11):
                text_len1 = 12

            elif (3 < len(str(object_name)) < 7 or len(str(object_name)) == 7):
                text_len1 = 8

            elif (len(str(object_name)) < 3 or len(str(object_name)) == 3):
                text_len1 = 4

            object['c_bytes_len'] = text_len1 + 8 + 32 + 12

            if object['type'] == "ortn":
                object['c_bytes_len'] += 104

            file.write(struct.pack("<i", object['c_bytes_len']))

            file.write(str.encode('NNAM'))
            file.write(struct.pack("<i", len(str(object_name)) + 1))
            text_len = 0

            if (len(str(object_name)) > 15):
                file.write(str.encode(object_name)+bytearray(b'\x00'*(20-len(str(object_name)))))
                text_len = 20

            elif (11 < len(str(object_name)) < 15 or len(str(object_name)) == 15):
                file.write(str.encode(object_name)+bytearray(b'\x00'*(16-len(str(object_name)))))
                text_len = 16

            elif (7 < len(str(object_name)) < 11 or len(str(object_name)) == 11):
                file.write(str.encode(object_name)+bytearray(b'\x00'*(12-len(str(object_name)))))
                text_len = 12

            elif (3 < len(str(object_name)) < 7 or len(str(object_name)) == 7):
                file.write(str.encode(object_name)+bytearray(b'\x00'*(8-len(str(object_name)))))
                text_len = 8

            elif (len(str(object_name)) < 3 or len(str(object_name)) == 3):
                file.write(str.encode(object_name)+bytearray(b'\x00'*(4-len(str(object_name)))))
                text_len = 4

            #bytes_len = 8 + text_len

            file.write(str.encode('POSN'))
            file.write(struct.pack("<i", 24))
            file.write(struct.pack("<d", object.location.x))
            file.write(struct.pack("<d", object.location.y))
            file.write(struct.pack("<d", object.location.z))

            if object['type'] == "ortn":
                object_matrix = object.matrix_world.to_3x3()

                file.write(str.encode('ORTN'))
                file.write(struct.pack("<i", 96))

                file.write(struct.pack("<d",object_matrix[0][0]))
                file.write(struct.pack("<d",object_matrix[0][1]))
                file.write(struct.pack("<d",object_matrix[0][2]))

                file.write(struct.pack("<d",object_matrix[1][0]))
                file.write(struct.pack("<d",object_matrix[1][1]))
                file.write(struct.pack("<d",object_matrix[1][2]))

                file.write(struct.pack("<d",object_matrix[2][0]))
                file.write(struct.pack("<d",object_matrix[2][1]))
                file.write(struct.pack("<d",object_matrix[2][2]))

                file.write(struct.pack("<d", object.location.x))
                file.write(struct.pack("<d", object.location.y))
                file.write(struct.pack("<d", object.location.z))

            file.write(str.encode('FLAG'))
            file.write(struct.pack("<ii", 4, object['flag']))

        elif object['type'] == "room":
            file.write(str.encode('GROM'))

            object_name = object.name.split(".")[0]
            text_len1 = 0
            if (len(str(object_name)) > 15):
                text_len1 = 20

            elif (11 < len(str(object_name)) < 15 or len(str(object_name)) == 15):
                text_len1 = 16

            elif (7 < len(str(object_name)) < 11 or len(str(object_name)) == 11):
                text_len1 = 12

            elif (3 < len(str(object_name)) < 7 or len(str(object_name)) == 7):
                text_len1 = 8

            elif (len(str(object_name)) < 3 or len(str(object_name)) == 3):
                text_len1 = 4

            object['bytes_len'] = 8 + text_len1 + object['c_bytes_len']
            object['c_bytes_len'] = object['c_bytes_len'] + 20

            file.write(struct.pack("<i", object['c_bytes_len']))

            file.write(str.encode('RNAM'))
            file.write(struct.pack("<i", len(str(object_name)) + 1))
            text_len = 0

            if (len(str(object_name)) > 15):
                file.write(str.encode(object_name)+bytearray(b'\x00'*(20-len(str(object_name)))))
                text_len = 20

            elif (11 < len(str(object_name)) < 15 or len(str(object_name)) == 15):
                file.write(str.encode(object_name)+bytearray(b'\x00'*(16-len(str(object_name)))))
                text_len = 16

            elif (7 < len(str(object_name)) < 11 or len(str(object_name)) == 11):
                file.write(str.encode(object_name)+bytearray(b'\x00'*(12-len(str(object_name)))))
                text_len = 12

            elif (3 < len(str(object_name)) < 7 or len(str(object_name)) == 7):
                file.write(str.encode(object_name)+bytearray(b'\x00'*(8-len(str(object_name)))))
                text_len = 8

            elif (len(str(object_name)) < 3 or len(str(object_name)) == 3):
                file.write(str.encode(object_name)+bytearray(b'\x00'*(4-len(str(object_name)))))
                text_len = 4

    for child in object.children:
        forChild(child,False,file)







