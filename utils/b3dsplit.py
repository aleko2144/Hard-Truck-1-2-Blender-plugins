import logging
import struct
import sys
import enum
import json
import os

filename = ''
outdir = ''

args = sys.argv

rootsFile = None
rootsFromFile = False

EMPTY_NAME = '~'

if len(args) == 2:
    filename = args[1]
    outdir = os.path.dirname(filename)
elif len(args) == 3:
    filename = args[1]
    outdir = os.path.dirname(filename)
    rootsFromFile = True
    rootsFile = args[2]
else:
    print("Wrong number of parameters")
    print("")
    print('Usage: python b3dsplit.py <path to b3d> <path to .txt>')
    print('<path to .b3d> - (obligatory) Path to .b3d file to export meshes')
    print('<path to .txt> - (optional) Path to .txt file with mesh root names. 1 line = 1 name')
    print('if <path to .txt> not defined or file is empty, script search for roots automatically')
    print('Tested with Python v.3.9.13')
    sys.exit()

blocksToExtract = []

if rootsFromFile:
    if os.path.exists(rootsFile):
        with open(rootsFile) as f:
            for line in f:
                l = line.rstrip()
                if len(l) > 0:
                    blocksToExtract.append(l)


logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
log = logging.getLogger("splitb3d")
log.setLevel(logging.DEBUG)

def getHierarchyRoots(refObjs):

    graph = {}

    for key in refObjs.keys():
        graph[key] = [cn['add_name'] for cn in refObjs[key]]

    zgraph = Graph(graph)

    visited = zgraph.DFS()

    roots = [cn for cn in visited.keys() if (visited[cn]["in"] == 0) and (visited[cn]["out"] > 0)]

    return roots

def readName(file):
    objName = file.read(32)
    if (objName[0] == 0):
        objName = EMPTY_NAME
        #objname = "Untitled_0x" + str(hex(pos-36))
    else:
        objName = (objName.decode("cp1251").rstrip('\0'))
    return objName

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
        # log.debug(file.tell())
        raise Exception()

class Graph:

    def __init__(self, graph):
        self.graph = graph

    def DFSUtil(self, val, visited):

        visited[val]["in"] += 1
        for v in self.graph[val]:
            if self.graph.get(v) is not None:
                visited[val]["out"] += 1
                self.DFSUtil(v, visited)

    def DFS(self, start=None):
        V = len(self.graph)  #total vertices

        visited = {}
        for val in self.graph.keys():
            visited[val] = {
                "in": 0,
                "out": 0
            }

        searchIn = []
        if start is not None:
            searchIn.append(start.name)
        else:
            searchIn = self.graph.keys()

        for val in searchIn:
            for v in self.graph[val]:
                if self.graph.get(v) is not None:
                    visited[val]["out"] += 1
                    self.DFSUtil(v, visited)

        return visited

def read(file):
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

    level = 0

    rootObjects = {}

    objName = ''
    start_pos = 0
    end_pos = 0

    blocks18 = {}

    while ex!=ChunkType.END_CHUNKS:

        ex = openclose(file)
        if ex == ChunkType.END_CHUNK:
            level -= 1
            if level == 0:
                end_pos = file.tell()
                rootObjects[objName] = {
                    "start": start_pos,
                    "size": end_pos - start_pos
                }
                # log.debug("name:{}, start:{}, end:{}".format(objName, start_pos, end_pos))

        elif ex == ChunkType.END_CHUNKS:
            # file.close()
            break
        elif ex == ChunkType.GROUP_CHUNK: #skip
            continue
        elif ex == ChunkType.BEGIN_CHUNK:

            if level == 0:
                start_pos = file.tell()-4

            curObjName = readName(file)
            type = struct.unpack("<i",file.read(4))[0]

            if level == 0:
                objName = curObjName
                blocks18[objName] = []

            level += 1

            if (type == 0):
                ff = file.seek(44,1)

            elif (type == 1):
                name1 = readName(file)
                name2 = readName(file)

            elif (type == 2):
                bounding_sphere = struct.unpack("<4f",file.read(16))
                unknown_sphere = struct.unpack("<4f",file.read(16))
                childCnt = struct.unpack("<i",file.read(4))

            elif (type == 3):
                bounding_sphere = struct.unpack("<4f",file.read(16))
                childCnt = struct.unpack("<i",file.read(4))

            elif (type == 4):
                bounding_sphere = struct.unpack("<4f",file.read(16))
                name1 = readName(file)
                name2 = readName(file)
                childCnt = struct.unpack("<i",file.read(4))[0]

            elif (type == 5):
                bounding_sphere = struct.unpack("<4f",file.read(16))
                name = readName(file)
                childCnt = struct.unpack("<i",file.read(4))[0]

            elif (type == 6):

                bounding_sphere = struct.unpack("<4f",file.read(16))
                name1 = readName(file)
                name2 = readName(file)
                vertexCount = struct.unpack("<i",file.read(4))[0]
                for i in range (vertexCount):
                    vertex = struct.unpack("<3f",file.read(12))
                    uv = struct.unpack("<2f",file.read(8))

                childCnt = struct.unpack("<i",file.read(4))[0]

            elif (type == 7):

                bounding_sphere = struct.unpack("<4f",file.read(16))
                groupName = readName(file) #0-0

                vertexCount = struct.unpack("<i",file.read(4))[0]
                for i in range(vertexCount):
                    vertex = struct.unpack("<3f",file.read(12))
                    uv = struct.unpack("<2f",file.read(8))

                childCnt = struct.unpack("<i",file.read(4))[0]

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


            elif (type == 9 or type == 22):

                bounding_sphere = struct.unpack("<4f",file.read(16))
                unknown_sphere = struct.unpack("<4f",file.read(16))
                childCnt = struct.unpack("<i",file.read(4))[0]

            elif (type == 10):

                bounding_sphere = struct.unpack("<4f",file.read(16))
                unknown_sphere = struct.unpack("<4f",file.read(16))
                childCnt = struct.unpack("<i",file.read(4))[0]

            elif (type == 11):
                bounding_sphere = struct.unpack("<4f",file.read(16))
                unknown_sphere = struct.unpack("<4f",file.read(16))
                childCnt = struct.unpack("<i",file.read(4))[0]

            elif (type == 12):

                bounding_sphere = struct.unpack("<4f",file.read(16))
                unknown_sphere = struct.unpack("<4f",file.read(16))
                unknown1 = struct.unpack("<i",file.read(4))[0]
                unknown2 = struct.unpack("<i",file.read(4))[0]
                cnt = struct.unpack("<i",file.read(4))[0]
                for i in range(cnt):
                    coord = struct.unpack("f",file.read(4))[0]

            elif (type == 13):

                bounding_sphere = struct.unpack("<4f",file.read(16))
                unknown1 = struct.unpack("<i",file.read(4))[0]
                unknown2 = struct.unpack("<i",file.read(4))[0]
                cnt = struct.unpack("<i",file.read(4))[0]
                for i in range(cnt):
                    coord = struct.unpack("f",file.read(4))[0]

            elif (type == 14):

                bounding_sphere = struct.unpack("<4f",file.read(16))
                unknown_sphere = struct.unpack("<4f",file.read(16))
                unknown1 = struct.unpack("<i",file.read(4))[0]
                unknown2 = struct.unpack("<i",file.read(4))[0]
                cnt = struct.unpack("<i",file.read(4))[0]

                for i in range(cnt):
                    coord = struct.unpack("f",file.read(4))[0]

            elif (type == 15):

                bounding_sphere = struct.unpack("<4f",file.read(16))
                unknown1 = struct.unpack("<i",file.read(4))[0]
                unknown2 = struct.unpack("<i",file.read(4))[0]
                cnt = struct.unpack("<i",file.read(4))[0]

                for i in range(cnt):
                    coord = struct.unpack("f",file.read(4))[0]

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

            elif (type == 18):

                bounding_sphere = struct.unpack("<4f",file.read(16))
                space_name = readName(file)
                add_name = readName(file)

                blocks18[objName].append({
                    "space_name" : space_name,
                    "add_name" : add_name,
                })

            elif (type == 19):

                childCnt = struct.unpack("i",file.read(4))[0]

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


            elif (type == 21):

                bounding_sphere = struct.unpack("<4f",file.read(16))
                unknown1 = struct.unpack("<i",file.read(4))[0]
                unknown2 = struct.unpack("<i",file.read(4))[0]
                childCnt = struct.unpack("<i",file.read(4))[0]

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

            elif (type == 24):

                m11 = struct.unpack("<f",file.read(4))[0]
                m12 = struct.unpack("<f",file.read(4))[0]
                m13 = struct.unpack("<f",file.read(4))[0]

                m21 = struct.unpack("<f",file.read(4))[0]
                m22 = struct.unpack("<f",file.read(4))[0]
                m23 = struct.unpack("<f",file.read(4))[0]

                m31 = struct.unpack("<f",file.read(4))[0]
                m32 = struct.unpack("<f",file.read(4))[0]
                m33 = struct.unpack("<f",file.read(4))[0]

                sp_pos = struct.unpack("<fff",file.read(12))

                flag = struct.unpack("<i",file.read(4))[0]
                childCnt = struct.unpack("<i", file.read(4))[0]

            elif (type == 25):

                unknown1 = struct.unpack("<3i",file.read(12))
                name = readName(file)
                unknown_sphere1 = struct.unpack("<3f",file.read(12))
                unknown_sphere2 = struct.unpack("<3f",file.read(12))
                unknown2 = struct.unpack("<5f",file.read(20))

            elif (type == 26):

                bounding_sphere = struct.unpack("<4f",file.read(16))
                unknown_sphere1 = struct.unpack("<3f",file.read(12))
                unknown_sphere2 = struct.unpack("<3f",file.read(12))
                unknown_sphere3 = struct.unpack("<3f",file.read(12))

                childCnt = struct.unpack("<i",file.read(4))

            elif (type == 27):

                bounding_sphere = struct.unpack("<4f",file.read(16))
                flag1 = struct.unpack("<i",file.read(4))
                unknown_sphere = struct.unpack("<3f",file.read(12))
                materialId = struct.unpack("<i",file.read(4))

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

            elif (type == 29):

                bounding_sphere = struct.unpack("<4f",file.read(16))
                num0 = struct.unpack("<i",file.read(4))[0]
                num1 = struct.unpack("<i",file.read(4))[0]
                unknown_sphere = struct.unpack("<4f",file.read(16))
                if num0 > 0:
                    f = struct.unpack("<"+str(num0)+"f",file.read(4*num0))

                childCnt = struct.unpack("<i",file.read(4))[0]

            elif (type == 30):

                bounding_sphere = struct.unpack("<4f",file.read(16))
                connectedRoomName = readName(file)

                p1 = struct.unpack("<3f",file.read(12))
                p2 = struct.unpack("<3f",file.read(12))


            elif (type == 31):

                bounding_sphere = struct.unpack("<4f",file.read(16))

                num = struct.unpack("<i",file.read(4))[0]
                unknown_sphere = struct.unpack("<4f",file.read(16))
                num2 = struct.unpack("<i",file.read(4))[0]
                unknown = struct.unpack("<3f",file.read(12))
                for i in range(num):
                    unknown = struct.unpack("<fi",file.read(8))

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

            elif (type == 34):

                bounding_sphere = struct.unpack("<4f",file.read(16))
                file.read(4) #skipped Int
                num = struct.unpack("<i",file.read(4))[0]
                for i in range(num):
                    unknown_vector1 = struct.unpack("<3f",file.read(12))
                    unknown1 = struct.unpack("<f",file.read(4))

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

            elif (type == 39):

                bounding_sphere = struct.unpack("<4f",file.read(16))
                color_r = struct.unpack("<i",file.read(4))
                unknown = struct.unpack("<f",file.read(4))
                fog_start = struct.unpack("<f",file.read(4))
                fog_end = struct.unpack("<f",file.read(4))
                colorId = struct.unpack("<i",file.read(4))
                childCnt = struct.unpack("<i",file.read(4))

            elif (type == 40):

                bounding_sphere = struct.unpack("<4f",file.read(16))
                name1 = readName(file)
                name2 = readName(file)
                unknown1 = struct.unpack("<i",file.read(4))[0]
                unknown2 = struct.unpack("<i",file.read(4))[0]
                num = struct.unpack("<i",file.read(4))[0]
                for i in range(num):
                    data1 = struct.unpack("f", file.read(4))[0]

            else:
                log.warning('smthng wrng')
                return

    roots = getHierarchyRoots(blocks18)

    global blocksToExtract

    if not rootsFromFile:
        blocksToExtract = roots

    log.info(blocksToExtract)

    for extBlock in blocksToExtract:
        g_spaces = set()
        g_objs = set()
        g_objs.add(extBlock)
        curLevel = [extBlock]
        # curLevel.append(extBlock)
        objs = set()
        while len(curLevel) > 0:
            for add in curLevel:
                for block in blocks18[add]:
                    # log.debug(block)
                    g_spaces.add(block['space_name'])
                    g_objs.add(block['add_name'])
                    objs.add(block['add_name'])
            curLevel = list(objs)
            objs = set()

        spaces = [cn for cn in list(g_spaces) if cn != EMPTY_NAME]
        objs = list(g_objs)

        spaces.sort()
        objs.sort(reverse=True)


        outfilename = os.path.join(outdir, '{}.b3d'.format(extBlock))
        with open(outfilename, 'wb') as outFile:
            outFile.write(b'b3d\x00')
            outFile.write(struct.pack("<i", 0))
            outFile.write(struct.pack("<i", 0))
            outFile.write(struct.pack("<i", 0))
            outFile.write(struct.pack("<i", 0))
            outFile.write(struct.pack("<i", 0))
            outFile.write(struct.pack("<i", 0)) #Materials list
            outFile.write(b'\x4D\x01\x00\x00') #BeginChunks

            for space in spaces:
                rootObj = rootObjects[space]
                file.seek(rootObj['start'], 0)
                temp = file.read(rootObj['size'])

                outFile.write(temp)

            for obj in objs:
                rootObj = rootObjects[obj]
                file.seek(rootObj['start'], 0)
                temp = file.read(rootObj['size'])

                outFile.write(temp)

            outFile.write(b'\xde\x00\00\00') #EndChunks


with open(filename, 'rb') as file:
    read(file)
