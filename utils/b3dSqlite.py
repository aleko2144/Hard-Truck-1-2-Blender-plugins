import sqlite3
import struct
import logging
import sys
import os
import enum

filename = ''
outdir = ''


# dbName = r'.\testHT1.db'
dbName = r'.\testHT2.db'

# reloadTables = True
reloadTables = False

args = sys.argv

if len(args) == 2:
    filename = args[1]
    outdir = os.path.dirname(filename)
else:
    print(args)
    print("Wrong number of parameters")
    print("")
    print('Usage: python b3dSqlite.py <path to b3d>')
    print('<path to .b3d> - (obligatory) Path to .b3d file to fill SQLite')
    print('Tested with Python v.3.9.13')
    sys.exit()


logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
log = logging.getLogger("sqliteb3d")
log.setLevel(logging.DEBUG)

b3dBlocks = [
    1,2,3,4,5,6,7,8,9,10,
    11,12,13,14,15,16,17,18,19,20,
    21,22,23,24,25,26,27,28,29,30,
    31,33,34,35,36,37,39,40
]

class ChunkType(enum.Enum):
    END_CHUNK = 0
    END_CHUNKS = 1
    BEGIN_CHUNK = 2
    GROUP_CHUNK = 3

def openclose(file):
    oc = file.read(4)
    if (oc == (b'\x4D\x01\x00\x00')): # Begin_Chunk(111)
        return ChunkType.BEGIN_CHUNK
    elif oc == (b'\x2B\x02\x00\x00'): # End_Chunk(555)
        return ChunkType.END_CHUNK
    elif oc == (b'\xbc\x01\x00\x00'): # Group_Chunk(444)
        return ChunkType.GROUP_CHUNK
    elif oc == (b'\xde\x00\00\00'): # End_Chunks(222)
        return ChunkType.END_CHUNKS
    else:
        log.debug(oc)
        log.debug(file.tell())
        raise Exception()

def readName(file):
    objName = file.read(32)
    if (objName[0] == 0):
        objName = ''
        #objname = "Untitled_0x" + str(hex(pos-36))
    else:
        objName = (objName.decode("cp1251").rstrip('\0'))
    return objName

def tabSphere(name, isInt = False):
    ctype = "INT" if isInt else "FLOAT"
    return """
        {name}_x {ctype},
        {name}_y {ctype},
        {name}_z {ctype},
        {name}_r {ctype}""".format(name=name, ctype=ctype)

def tabPoint(name, isInt = False):
    ctype = "INT" if isInt else "FLOAT"
    return """
        {name}_x {ctype},
        {name}_y {ctype},
        {name}_z {ctype}""".format(name=name, ctype=ctype)

def getBlockColumnByType(blockType, noTypes = False):
    blockColumns = ""
    if blockType == 1:
        blockColumns = """
            name1 VARCHAR(32),
            name2 VARCHAR(32)
        """
    elif blockType == 2:
        blockColumns = """
            {},
            {},
            child_cnt INT
        """.format(
            tabSphere("bound_sphere"),
            tabSphere("unk_sphere")
        )
    elif blockType == 3:
        blockColumns = """
            {},
            child_cnt INT
        """.format(
            tabSphere("bound_sphere")
        )
    elif blockType == 4:
        blockColumns = """
            {},
            name1 VARCHAR(32),
            name2 VARCHAR(32),
            child_cnt INT
        """.format(
            tabSphere("bound_sphere")
        )
    elif blockType == 5:
        blockColumns = """
            {},
            name1 VARCHAR(32),
            child_cnt INT
        """.format(
            tabSphere("bound_sphere")
        )
    elif blockType == 6:
        blockColumns = """
            {},
            name1 VARCHAR(32),
            name2 VARCHAR(32),
            vertex_cnt INT,
            child_cnt INT
        """.format(
            tabSphere("bound_sphere")
        )
    elif blockType == 7:
        blockColumns = """
            {},
            name1 VARCHAR(32),
            vertex_cnt INT,
            child_cnt INT
        """.format(
            tabSphere("bound_sphere")
        )
    elif blockType == 8:
        blockColumns = """
            {},
            poly_cnt INT
        """.format(
            tabSphere("bound_sphere")
        )
    elif blockType in [9,10,22]:
        blockColumns = """
            {},
            {},
            child_cnt INT
        """.format(
            tabSphere("bound_sphere"),
            tabSphere("unk_sphere")
        )
    elif blockType == 11:
        blockColumns = """
            {},
            {},
            {},
            float1 FLOAT,
            float2 FLOAT,
            child_cnt INT
        """.format(
            tabSphere("bound_sphere"),
            tabPoint("unk_point1"),
            tabPoint("unk_point2")
        )
    elif blockType in [12, 14]:
        blockColumns = """
            {},
            {},
            int1 INT,
            int2 INT,
            unk_cnt INT
        """.format(
            tabSphere("bound_sphere"),
            tabSphere("unk_sphere")
        )
    elif blockType in [13, 15]:
        blockColumns = """
            {},
            int1 INT,
            int2 INT,
            unk_cnt INT
        """.format(
            tabSphere("bound_sphere"),
            tabSphere("unk_sphere")
        )
    elif blockType in [16, 17]:
        blockColumns = """
            {},
            {},
            {},
            float1 FLOAT,
            float2 FLOAT,
            int1 INT,
            int2 INT,
            poly_cnt INT
        """.format(
            tabSphere("bound_sphere"),
            tabPoint("point1"),
            tabPoint("point2"),
        )
    elif blockType == 18:
        blockColumns = """
            {},
            space_name VARCHAR(32),
            add_name VARCHAR(32)
        """.format(
            tabSphere("bound_sphere")
        )
    elif blockType == 19:
        blockColumns = """
            child_cnt INT
        """
    elif blockType == 20:
        blockColumns = """
            {},
            vertex_cnt INT,
            int1 INT,
            int2 INT,
            unk_cnt INT
        """.format(
            tabSphere("bound_sphere")
        )
    elif blockType == 21:
        blockColumns = """
            {},
            int1 INT,
            int2 INT,
            child_cnt INT
        """.format(
            tabSphere("bound_sphere")
        )
    elif blockType == 23:
        blockColumns = """
            int1 INT,
            surface INT,
            unk_cnt INT,
            poly_cnt INT
        """
    elif blockType == 24:
        blockColumns = """
            {},
            {},
            {},
            {},
            flag INT,
            child_cnt INT
        """.format(
            tabPoint("transf1"),
            tabPoint("transf2"),
            tabPoint("transf3"),
            tabPoint("pos")
        )
    elif blockType == 25:
        blockColumns = """
            {},
            name1 VARCHAR(32),
            {},
            {},
            float1 FLOAT,
            float2 FLOAT,
            float3 FLOAT,
            float4 FLOAT,
            float5 FLOAT
        """.format(
            tabPoint("point1", True),
            tabPoint("point2"),
            tabPoint("point3")
        )
    elif blockType == 26:
        blockColumns = """
            {},
            {},
            {},
            {},
            child_cnt INT
        """.format(
            tabSphere("bound_sphere"),
            tabSphere("point1"),
            tabSphere("point2"),
            tabSphere("point3")
        )
    elif blockType == 27:
        blockColumns = """
            {},
            flag1 INT,
            {},
            material INT
        """.format(
            tabSphere("bound_sphere"),
            tabPoint("unk_point"),
        )
    elif blockType == 28:
        blockColumns = """
            {},
            {},
            vertex_cnt INT
        """.format(
            tabSphere("bound_sphere"),
            tabPoint("sprite_center"),
        )
    elif blockType == 29:
        blockColumns = """
            {},
            unk_cnt INT,
            int2 INT,
            {},
            child_cnt INT
        """.format(
            tabSphere("bound_sphere"),
            tabSphere("unk_sphere"),
        )
    elif blockType == 30:
        blockColumns = """
            {},
            room_name VARCHAR(32),
            {},
            {}
        """.format(
            tabSphere("bound_sphere"),
            tabPoint("point1"),
            tabPoint("point2"),
        )
    elif blockType == 31:
        blockColumns = """
            {},
            unk_cnt INT,
            {},
            int1 INT,
            {}
        """.format(
            tabSphere("bound_sphere"),
            tabSphere("unk_sphere"),
            tabPoint("unk_point"),
        )
    elif blockType == 33:
        blockColumns = """
            {},
            use_lights INT,
            light_type INT,
            flag1 INT,
            {},
            {},
            float1 FLOAT,
            float2 FLOAT,
            light_r FLOAT,
            intensity FLOAT,
            float3 FLOAT,
            float4 FLOAT,
            {},
            child_cnt INT
        """.format(
            tabSphere("bound_sphere"),
            tabPoint("unk_sphere1"),
            tabPoint("unk_sphere2"),
            tabPoint("rgb"),
        )
    elif blockType == 34:
        blockColumns = """
            {},
            int1 INT,
            unk_cnt INT
        """.format(
            tabSphere("bound_sphere")
        )
    elif blockType == 35:
        blockColumns = """
            {},
            mtype INT,
            texnum INT,
            poly_cnt INT
        """.format(
            tabSphere("bound_sphere")
        )
    elif blockType == 36:
        blockColumns = """
            {},
            name1 VARCHAR(32),
            name2 VARCHAR(32),
            format INT,
            vertex_cnt INT,
            child_cnt INT
        """.format(
            tabSphere("bound_sphere")
        )
    elif blockType == 37:
        blockColumns = """
            {},
            name1 VARCHAR(32),
            format INT,
            vertex_cnt INT,
            child_cnt INT
        """.format(
            tabSphere("bound_sphere")
        )
    elif blockType == 39:
        blockColumns = """
            {},
            color_r INT,
            float1 FLOAT,
            fog_start FLOAT,
            fog_end FLOAT,
            color_id INT,
            child_cnt INT
        """.format(
            tabSphere("bound_sphere")
        )
    elif blockType == 40:
        blockColumns = """
            {},
            name1 VARCHAR(32),
            name2 VARCHAR(32),
            int1 INT,
            int2 INT,
            unk_cnt INT
        """.format(
            tabSphere("bound_sphere")
        )

    if noTypes:
        blockColumns = blockColumns.replace(" INT", "")
        blockColumns = blockColumns.replace(" FLOAT", "")
        blockColumns = blockColumns.replace(" VARCHAR(32)", "")

    return blockColumns

insertColumns = {}
for blockType in b3dBlocks:
    insertColumns[blockType] = getBlockColumnByType(blockType, True)

def createTableByType(con, blockType):

    cur = con.cursor()

    sqlStatement = """
        CREATE TABLE IF NOT EXISTS b_{}(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            b3dmodule VARCHAR(32),
            b3dname VARCHAR(32),
            {}
        )
    """
    blockColumns = getBlockColumnByType(blockType)

    cur.execute(sqlStatement.format(blockType, blockColumns))

def getPlaceholders(cnt):
    if cnt > 0:
        arr = ['?'] * cnt
        return ",".join(arr)
    return ""

def insertByType(con, blockType, row):

    # log.debug("inserting {}".format(blockType))

    cur = con.cursor()

    count = (insertColumns[blockType]).count(",")+1+2

    sqlStatement = """
        INSERT INTO b_{}(b3dmodule, b3dname, {})
        VALUES ({})
    """.format(blockType, insertColumns[blockType], getPlaceholders(count))

    cur.execute(sqlStatement, row)
    con.commit()

def readb3d(con, file):

    resBasename = os.path.basename(file.name)[:-4] #cut extension

    if file.read(3) == b'b3d':
        log.info("correct file")
    else:
        log.error("b3d error")

    file.seek(1,1)
    filesize = struct.unpack("<i", file.read(4))[0]
    matOff = struct.unpack("<i", file.read(4))[0]
    matSize = struct.unpack("<i", file.read(4))[0]
    chunkOff = struct.unpack("<i", file.read(4))[0]
    chunkSize = struct.unpack("<i", file.read(4))[0]

    file.seek(chunkOff*4, 0)

    # log.debug(file.tell())

    # log.debug(struct.unpack("<i", file.read(4))[0])
    file.read(4)
    ex = 0
    while ex!=ChunkType.END_CHUNKS:

        ex = openclose(file)
        if ex == ChunkType.END_CHUNK:
            continue
        elif ex == ChunkType.END_CHUNKS:
            # file.close()
            break
        elif ex == ChunkType.GROUP_CHUNK: #skip
            continue
        elif ex == ChunkType.BEGIN_CHUNK:

            curObjName = readName(file)
            type = struct.unpack("<i",file.read(4))[0]

            row = [resBasename, curObjName]

            if (type == 0):
                ff = file.seek(44,1)

            elif (type == 1):
                name1 = readName(file)
                name2 = readName(file)

                row.extend([name1, name2])
                insertByType(con, type, row)

            elif (type == 2):
                bounding_sphere = struct.unpack("<4f",file.read(16))
                unknown_sphere = struct.unpack("<4f",file.read(16))
                childCnt = struct.unpack("<i",file.read(4))[0]

                row.extend([*bounding_sphere, *unknown_sphere, childCnt])
                insertByType(con, type, row)

            elif (type == 3):
                bounding_sphere = struct.unpack("<4f",file.read(16))
                childCnt = struct.unpack("<i",file.read(4))[0]

                row.extend([*bounding_sphere, childCnt])
                insertByType(con, type, row)

            elif (type == 4):
                bounding_sphere = struct.unpack("<4f",file.read(16))
                name1 = readName(file)
                name2 = readName(file)
                childCnt = struct.unpack("<i",file.read(4))[0]

                row.extend([*bounding_sphere, name1, name2, childCnt])
                insertByType(con, type, row)

            elif (type == 5):
                bounding_sphere = struct.unpack("<4f",file.read(16))
                name = readName(file)
                childCnt = struct.unpack("<i",file.read(4))[0]

                row.extend([*bounding_sphere, name, childCnt])
                insertByType(con, type, row)

            elif (type == 6):

                bounding_sphere = struct.unpack("<4f",file.read(16))
                name1 = readName(file)
                name2 = readName(file)
                vertexCount = struct.unpack("<i",file.read(4))[0]
                for i in range (vertexCount):
                    vertex = struct.unpack("<3f",file.read(12))
                    uv = struct.unpack("<2f",file.read(8))

                childCnt = struct.unpack("<i",file.read(4))[0]

                row.extend([*bounding_sphere, name1, name2, vertexCount, childCnt])
                insertByType(con, type, row)

            elif (type == 7):

                bounding_sphere = struct.unpack("<4f",file.read(16))
                groupName = readName(file) #0-0

                vertexCount = struct.unpack("<i",file.read(4))[0]
                for i in range(vertexCount):
                    vertex = struct.unpack("<3f",file.read(12))
                    uv = struct.unpack("<2f",file.read(8))

                childCnt = struct.unpack("<i",file.read(4))[0]

                row.extend([*bounding_sphere, groupName, vertexCount, childCnt])
                insertByType(con, type, row)

            elif (type == 8):

                bounding_sphere = struct.unpack("<4f",file.read(16))
                polygonCount = struct.unpack("<i",file.read(4))[0]

                for i in range(polygonCount):

                    formatRaw = struct.unpack("<i",file.read(4))[0]
                    format = formatRaw ^ 1
                    uvCount = (format & 0xFF00) >> 8 #ah

                    if format & 0b10:
                        uvCount += 1

                    unkF = struct.unpack("<f",file.read(4))[0]
                    unkInt = struct.unpack("<i",file.read(4))[0]
                    texnum = str(struct.unpack("i",file.read(4))[0])
                    vertexCount = struct.unpack("<i",file.read(4))[0]

                    for j in range(vertexCount):
                        face = struct.unpack("<i",file.read(4))[0]
                        if format & 0b10:
                            for k in range(uvCount):
                                uv = struct.unpack("<2f",file.read(8))
                        if format & 0b100000 and format & 0b10000:
                            if format & 0b1:
                                normal = struct.unpack("<3f",file.read(12))
                            else:
                                normal_off = struct.unpack("<f",file.read(4))

                row.extend([*bounding_sphere, polygonCount])
                insertByType(con, type, row)

            elif (type == 9 or type == 22):

                bounding_sphere = struct.unpack("<4f",file.read(16))
                unknown_sphere = struct.unpack("<4f",file.read(16))
                childCnt = struct.unpack("<i",file.read(4))[0]

                row.extend([*bounding_sphere, *unknown_sphere, childCnt])
                insertByType(con, type, row)

            elif (type == 10):

                bounding_sphere = struct.unpack("<4f",file.read(16))
                unknown_sphere = struct.unpack("<4f",file.read(16))
                childCnt = struct.unpack("<i",file.read(4))[0]

                row.extend([*bounding_sphere, *unknown_sphere, childCnt])
                insertByType(con, type, row)

            elif (type == 11):
                bounding_sphere = struct.unpack("<4f",file.read(16))
                unknown_point = struct.unpack("<3f",file.read(12))
                unknown_point2 = struct.unpack("<3f",file.read(12))
                unk1 = struct.unpack("<f",file.read(4))[0]
                unk2 = struct.unpack("<f",file.read(4))[0]
                childCnt = struct.unpack("<i",file.read(4))[0]

                row.extend([*bounding_sphere, *unknown_point, *unknown_point2, unk1, unk2, childCnt])
                insertByType(con, type, row)

            elif (type == 12):

                bounding_sphere = struct.unpack("<4f",file.read(16))
                unknown_sphere = struct.unpack("<4f",file.read(16))
                unknown1 = struct.unpack("<i",file.read(4))[0]
                unknown2 = struct.unpack("<i",file.read(4))[0]
                cnt = struct.unpack("<i",file.read(4))[0]
                for i in range(cnt):
                    coord = struct.unpack("f",file.read(4))[0]

                row.extend([*bounding_sphere, *unknown_sphere, unknown1, unknown2, cnt])
                insertByType(con, type, row)

            elif (type == 13):

                bounding_sphere = struct.unpack("<4f",file.read(16))
                unknown1 = struct.unpack("<i",file.read(4))[0]
                unknown2 = struct.unpack("<i",file.read(4))[0]
                cnt = struct.unpack("<i",file.read(4))[0]
                for i in range(cnt):
                    coord = struct.unpack("f",file.read(4))[0]

                row.extend([*bounding_sphere, unknown1, unknown2, cnt])
                insertByType(con, type, row)

            elif (type == 14):

                bounding_sphere = struct.unpack("<4f",file.read(16))
                unknown_sphere = struct.unpack("<4f",file.read(16))
                unknown1 = struct.unpack("<i",file.read(4))[0]
                unknown2 = struct.unpack("<i",file.read(4))[0]
                cnt = struct.unpack("<i",file.read(4))[0]

                for i in range(cnt):
                    coord = struct.unpack("f",file.read(4))[0]

                row.extend([*bounding_sphere, *unknown_sphere, unknown1, unknown2, cnt])
                insertByType(con, type, row)

            elif (type == 15):

                bounding_sphere = struct.unpack("<4f",file.read(16))
                unknown1 = struct.unpack("<i",file.read(4))[0]
                unknown2 = struct.unpack("<i",file.read(4))[0]
                cnt = struct.unpack("<i",file.read(4))[0]

                for i in range(cnt):
                    coord = struct.unpack("f",file.read(4))[0]

                row.extend([*bounding_sphere, unknown1, unknown2, cnt])
                insertByType(con, type, row)

            elif (type == 16):

                bounding_sphere = struct.unpack("<4f",file.read(16))
                vector1 = struct.unpack("<3f",file.read(12))
                vector2 = struct.unpack("<3f",file.read(12))
                unk1 = struct.unpack("<f",file.read(4))[0]
                unk2 = struct.unpack("<f",file.read(4))[0]

                unknown1 = struct.unpack("<i",file.read(4))[0]
                unknown2 = struct.unpack("<i",file.read(4))[0]
                cnt = struct.unpack("<i",file.read(4))[0]
                for i in range(cnt):
                    coord = struct.unpack("f",file.read(4))[0]

                row.extend([*bounding_sphere, *vector1, *vector2, unk1, unk2, unknown1, unknown2, cnt])
                insertByType(con, type, row)

            elif (type == 17):

                bounding_sphere = struct.unpack("<4f",file.read(16))
                vector1 = struct.unpack("<3f",file.read(12))
                vector2 = struct.unpack("<3f",file.read(12))
                unk1 = struct.unpack("<f",file.read(4))[0]
                unk2 = struct.unpack("<f",file.read(4))[0]

                unknown1 = struct.unpack("<i",file.read(4))[0]
                unknown2 = struct.unpack("<i",file.read(4))[0]
                cnt = struct.unpack("<i",file.read(4))[0]
                for i in range(cnt):
                    coord = struct.unpack("f",file.read(4))[0]

                row.extend([*bounding_sphere, *vector1, *vector2, unk1, unk2, unknown1, unknown2, cnt])
                insertByType(con, type, row)

            elif (type == 18):

                bounding_sphere = struct.unpack("<4f",file.read(16))
                space_name = readName(file)
                add_name = readName(file)

                row.extend([*bounding_sphere, space_name, add_name])
                insertByType(con, type, row)

            elif (type == 19):

                childCnt = struct.unpack("i",file.read(4))[0]

                row.extend([childCnt])
                insertByType(con, type, row)

            elif (type == 20):

                bounding_sphere = struct.unpack("<4f",file.read(16))
                verts_count = struct.unpack("i",file.read(4))[0]
                unknown1 = struct.unpack("<i",file.read(4))[0]
                unknown2 = struct.unpack("<i",file.read(4))[0]

                cnt = struct.unpack("i",file.read(4))[0]
                for i in range(cnt):
                    unknown = struct.unpack("f",file.read(4))[0]

                for i in range(verts_count):
                    coord = struct.unpack("fff",file.read(12))

                row.extend([*bounding_sphere, verts_count, unknown1, unknown2, cnt])
                insertByType(con, type, row)

            elif (type == 21):

                bounding_sphere = struct.unpack("<4f",file.read(16))
                unknown1 = struct.unpack("<i",file.read(4))[0]
                unknown2 = struct.unpack("<i",file.read(4))[0]
                childCnt = struct.unpack("<i",file.read(4))[0]

                row.extend([*bounding_sphere, unknown1, unknown2, childCnt])
                insertByType(con, type, row)

            elif (type == 23):

                var1 = struct.unpack("<i",file.read(4))[0]
                ctype = struct.unpack("<i",file.read(4))[0]
                cnt = struct.unpack("<i",file.read(4))[0]
                for i in range(cnt):
                    unknown = struct.unpack("<i",file.read(4))[0]

                vertsBlockNum = struct.unpack("<i",file.read(4))[0]
                for i in range(vertsBlockNum):
                    vertsInBlock = struct.unpack("<i",file.read(4))[0]
                    for j in range(vertsInBlock):
                        vertex = struct.unpack("<3f",file.read(12))

                row.extend([var1, ctype, cnt, vertsBlockNum])
                insertByType(con, type, row)

            elif (type == 24):

                m1 = struct.unpack("<3f",file.read(12))
                m2 = struct.unpack("<3f",file.read(12))
                m3 = struct.unpack("<3f",file.read(12))
                sp_pos = struct.unpack("<3f",file.read(12))

                flag = struct.unpack("<i",file.read(4))[0]
                childCnt = struct.unpack("<i", file.read(4))[0]

                row.extend([*m1, *m2, *m3, *sp_pos, flag, childCnt])
                insertByType(con, type, row)

            elif (type == 25):

                unknown1 = struct.unpack("<3i",file.read(12))
                name = readName(file)
                unknown_sphere1 = struct.unpack("<3f",file.read(12))
                unknown_sphere2 = struct.unpack("<3f",file.read(12))
                unknown2 = struct.unpack("<5f",file.read(20))

                row.extend([*unknown1, name, *unknown_sphere1, *unknown_sphere2, *unknown2])
                insertByType(con, type, row)

            elif (type == 26):

                bounding_sphere = struct.unpack("<4f",file.read(16))
                unknown_sphere1 = struct.unpack("<3f",file.read(12))
                unknown_sphere2 = struct.unpack("<3f",file.read(12))
                unknown_sphere3 = struct.unpack("<3f",file.read(12))

                childCnt = struct.unpack("<i",file.read(4))[0]

                row.extend([*bounding_sphere, *unknown_sphere1, *unknown_sphere2, *unknown_sphere3, childCnt])
                insertByType(con, type, row)

            elif (type == 27):

                bounding_sphere = struct.unpack("<4f",file.read(16))
                flag1 = struct.unpack("<i",file.read(4))[0]
                unknown_sphere = struct.unpack("<3f",file.read(12))
                materialId = struct.unpack("<i",file.read(4))[0]

                row.extend([*bounding_sphere, flag1, *unknown_sphere, materialId])
                insertByType(con, type, row)

            elif (type == 28):

                bounding_sphere = struct.unpack("<4f",file.read(16))
                sprite_center = struct.unpack("<3f",file.read(12))
                cnt = struct.unpack("<i",file.read(4))[0]

                for i in range(cnt):
                    formatRaw = struct.unpack("<i",file.read(4))[0]
                    format = formatRaw & 0xFFFF
                    uvCount = ((formatRaw & 0xFF00) >> 8) + 1 #ah
                    unknown3 = struct.unpack("<fi",file.read(8))[0]
                    texnum = struct.unpack("<i",file.read(4))[0]
                    vert_num = struct.unpack("<i", file.read(4))[0]
                    for k in range(vert_num):
                        scale_u = struct.unpack("<f", file.read(4))[0]
                        scale_v = struct.unpack("<f", file.read(4))[0]
                        if format & 0b10:
                            uv = struct.unpack("<2f",file.read(8))
                            for j in range(uvCount-1):
                                uv = struct.unpack("<2f",file.read(8))

                row.extend([*bounding_sphere, *sprite_center, cnt])
                insertByType(con, type, row)

            elif (type == 29):

                bounding_sphere = struct.unpack("<4f",file.read(16))
                num0 = struct.unpack("<i",file.read(4))[0]
                num1 = struct.unpack("<i",file.read(4))[0]
                unknown_sphere = struct.unpack("<4f",file.read(16))
                if num0 > 0:
                    f = struct.unpack("<"+str(num0)+"f",file.read(4*num0))

                childCnt = struct.unpack("<i",file.read(4))[0]

                row.extend([*bounding_sphere, num0, num1, *unknown_sphere, childCnt])
                insertByType(con, type, row)

            elif (type == 30):

                bounding_sphere = struct.unpack("<4f",file.read(16))
                connectedRoomName = readName(file)

                p1 = struct.unpack("<3f",file.read(12))
                p2 = struct.unpack("<3f",file.read(12))

                row.extend([*bounding_sphere, connectedRoomName, *p1, *p2])
                insertByType(con, type, row)

            elif (type == 31):

                bounding_sphere = struct.unpack("<4f",file.read(16))

                num = struct.unpack("<i",file.read(4))[0]
                unknown_sphere = struct.unpack("<4f",file.read(16))
                num2 = struct.unpack("<i",file.read(4))[0]
                unknown = struct.unpack("<3f",file.read(12))
                for i in range(num):
                    unknowns = struct.unpack("<fi",file.read(8))

                row.extend([*bounding_sphere, num, *unknown_sphere, num2, *unknown])
                insertByType(con, type, row)

            elif (type == 33):

                bounding_sphere = struct.unpack("<4f",file.read(16))

                useLights = struct.unpack("<i",file.read(4))[0]
                light_type = struct.unpack("<i",file.read(4))[0]
                flag1 = struct.unpack("<i",file.read(4))[0]

                unknown_vector1 = struct.unpack("<3f",file.read(12))
                unknown_vector2 = struct.unpack("<3f",file.read(12))
                unknown1 = struct.unpack("<f",file.read(4))[0]
                unknown2 = struct.unpack("<f",file.read(4))[0]
                light_radius = struct.unpack("<f",file.read(4))[0]
                intensity = struct.unpack("<f",file.read(4))[0]
                unknown3 = struct.unpack("<f",file.read(4))[0]
                unknown4 = struct.unpack("<f",file.read(4))[0]
                RGB = struct.unpack("<3f",file.read(12))

                childCnt = struct.unpack("<i",file.read(4))[0]

                row.extend([
                    *bounding_sphere, useLights, light_type, flag1,
                    *unknown_vector1, *unknown_vector2, unknown1, unknown2,
                    light_radius, intensity, unknown3, unknown4,
                    *RGB, childCnt
                ])
                insertByType(con, type, row)

            elif (type == 34):

                bounding_sphere = struct.unpack("<4f",file.read(16))
                someInt = struct.unpack("<i",file.read(4))[0] #skipped Int
                num = struct.unpack("<i",file.read(4))[0]
                for i in range(num):
                    unknown_vector1 = struct.unpack("<3f",file.read(12))
                    unknown1 = struct.unpack("<f",file.read(4))

                row.extend([*bounding_sphere, someInt, num])
                insertByType(con, type, row)

            elif (type == 35):

                bounding_sphere = struct.unpack("<4f",file.read(16))
                mType = struct.unpack("<i",file.read(4))[0]
                texNum = struct.unpack("<i",file.read(4))[0]
                polygonCount = struct.unpack("<i",file.read(4))[0]

                for i in range(polygonCount):

                    formatRaw = struct.unpack("<i",file.read(4))[0]
                    format = formatRaw ^ 1
                    uvCount = (format & 0xFF00) >> 8 #ah

                    if format & 0b10:
                        uvCount += 1

                    unkF = struct.unpack("<f",file.read(4))[0]
                    unkInt = struct.unpack("<i",file.read(4))[0]
                    texnum = str(struct.unpack("<i",file.read(4))[0])
                    vertexCount = struct.unpack("<i",file.read(4))[0]

                    for j in range(vertexCount):
                        face = struct.unpack("<i",file.read(4))[0]
                        if format & 0b10:
                            for k in range(uvCount):
                                uv = struct.unpack("<2f",file.read(8))
                        if format & 0b100000 and format & 0b10000:
                            if format & 0b1:
                                l_normal = struct.unpack("<3f",file.read(12))
                            else:
                                l_normal_off = struct.unpack("<f",file.read(4))

                row.extend([*bounding_sphere, mType, texNum, polygonCount])
                insertByType(con, type, row)

            elif (type == 36):

                bounding_sphere = struct.unpack("<4f",file.read(16))
                name1 = readName(file)
                name2 = readName(file)
                formatRaw = struct.unpack("<i",file.read(4))[0]
                uvCount = formatRaw >> 8
                format = formatRaw & 0xFF

                vertexCount = struct.unpack("<i",file.read(4))[0]
                if format == 0:
                    # objString[len(objString)-1] = objString[-2]
                    pass
                else:
                    for i in range(vertexCount):
                        vertex = struct.unpack("<3f",file.read(12))
                        uv = struct.unpack("<2f",file.read(8))
                        for j in range(uvCount):
                            uv = struct.unpack("<2f",file.read(8))
                        if format == 1 or format == 2:
                            normal = struct.unpack("<3f",file.read(12))
                        elif format == 3:
                            normal_off = struct.unpack("<f",file.read(4))[0]

                childCnt = struct.unpack("<i",file.read(4))[0]

                row.extend([*bounding_sphere, name1, name2, formatRaw, vertexCount, childCnt])
                insertByType(con, type, row)

            elif (type == 37):

                bounding_sphere = struct.unpack("<4f",file.read(16))
                groupName = readName(file)
                formatRaw = struct.unpack("<i",file.read(4))[0]
                uvCount = formatRaw >> 8
                format = formatRaw & 0xFF
                vertexCount = struct.unpack("<i",file.read(4))[0]

                if vertexCount > 0:
                    if format == 0:
                        # objString[len(objString)-1] = objString[-2]
                        pass
                    else:
                        for i in range(vertexCount):
                            vertex = struct.unpack("<3f",file.read(12))
                            uv = struct.unpack("<2f",file.read(8))
                            for j in range(uvCount):
                                uv = struct.unpack("<2f",file.read(8))
                            if format == 1 or format == 2:
                                normal = struct.unpack("<3f",file.read(12))
                            elif format == 3:
                                normal_off = struct.unpack("<f",file.read(4))[0]

                childCnt = struct.unpack("<i",file.read(4))[0]

                row.extend([*bounding_sphere, groupName, formatRaw, vertexCount, childCnt])
                insertByType(con, type, row)

            elif (type == 39):

                bounding_sphere = struct.unpack("<4f",file.read(16))
                color_r = struct.unpack("<i",file.read(4))[0]
                unknown = struct.unpack("<f",file.read(4))[0]
                fog_start = struct.unpack("<f",file.read(4))[0]
                fog_end = struct.unpack("<f",file.read(4))[0]
                colorId = struct.unpack("<i",file.read(4))[0]
                childCnt = struct.unpack("<i",file.read(4))[0]

                row.extend([
                    *bounding_sphere, color_r, unknown,
                    fog_start, fog_end, colorId, childCnt
                ])
                insertByType(con, type, row)

            elif (type == 40):

                bounding_sphere = struct.unpack("<4f",file.read(16))
                name1 = readName(file)
                name2 = readName(file)
                unknown1 = struct.unpack("<i",file.read(4))[0]
                unknown2 = struct.unpack("<i",file.read(4))[0]
                num = struct.unpack("<i",file.read(4))[0]
                for i in range(num):
                    data1 = struct.unpack("f", file.read(4))[0]

                row.extend([
                    *bounding_sphere, name1, name2,
                    unknown1, unknown2, num
                ])
                insertByType(con, type, row)

            else:
                print('smthng wrng')

def dropDbStruct(con):

    cur = con.cursor()

    for blockType in b3dBlocks:
        cur.execute("""
            DROP TABLE IF EXISTS b_{}
        """.format(blockType))

    con.commit()

def createDbStruct(con):

    for blockType in b3dBlocks:
        createTableByType(con, blockType)

    con.commit()

con = sqlite3.connect(dbName)

res_basename = os.path.basename(filename)[:-4] #cut extension

if reloadTables:
    dropDbStruct(con)
createDbStruct(con)


with open(filename, 'rb') as file:
    readb3d(con, file)


