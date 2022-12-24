import enum
from hashlib import new
import struct
import sys
import time
import timeit
import datetime
import threading
import pdb
import logging
from pathlib import Path

from .classes import (
	b_1,
	b_2,
	b_3,
	b_4,
	b_5,
	b_6,
	b_7,
	b_8,
	b_9,
	b_10,
	b_11,
	b_12,
	b_13,
	b_14,
	b_15,
	b_16,
	b_17,
	b_18,
	b_20,
	b_21,
	b_22,
	b_23,
	b_24,
	b_25,
	b_26,
	b_27,
	b_28,
	b_29,
	b_30,
	b_31,
	b_33,
	b_34,
	b_35,
	b_36,
	b_37,
	b_39,
	b_40,
	pfb_8,
	pfb_28,
	pfb_35,
	pvb_8,
	pvb_35
)

from .scripts import (
    prop,
    createCustomAttribute
)


from .imghelp import TXRtoTGA32
from .imghelp import parsePLM
from .common import (
    ShowMessageBox,
    Vector3F,
    createMaterials,
    getUsedFaces,
    getUsedFace,
    getUsedVerticesAndTransform,
    getUserVertices,
    readCString,
    transformVertices,
    getPolygonsBySelectedVertices
)

import bpy
import mathutils
import os.path
import os
from threading import Lock
from bpy.props import *
from bpy_extras.image_utils import load_image
from ast import literal_eval as make_tuple

from math import sqrt
from math import atan2

import re

import bmesh

from ..common import log

# logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
# log = logging.getLogger("import_b3d")
# log.setLevel(logging.DEBUG)

def thread_import_b3d(self, files, context):
    for b3dfile in files:
        filepath = os.path.join(self.directory, b3dfile.name)

        print('Importing file', filepath)
        t = time.mktime(datetime.datetime.now().timetuple())
        with open(filepath, 'rb') as file:
            read(file, context, self, filepath)
        t = time.mktime(datetime.datetime.now().timetuple()) - t
        print('Finished importing in', t, 'seconds')

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
        raise Exception()

def onebyte(file):
    return (file.read(1))

def readName(file):
    objName = file.read(32)
    if (objName[0] == 0):
        objName = "empty name"
        #objname = "Untitled_0x" + str(hex(pos-36))
    else:
        objName = (objName.decode("cp1251").rstrip('\0'))
    return objName


def Triangulate(faces):
    faces_new = []
    for t in range(len(faces)-2):
        faces_new.extend([faces[t],faces[t+1],faces[t+2]])
        # if t%2 ==0:
            # faces_new.extend([faces[t],faces[t+1],faces[t+2]])
        # else:
            # faces_new.extend([faces[t+2],faces[t+1],faces[t]])


            # if ((format == 0) or (format == 16) or (format == 1)):
                # faces_new.extend([faces[t+2],faces[t+1],faces[0]])
            # else:
                # faces_new.extend([faces[t+2],faces[t+1],faces[t]])
    return faces_new


def MakePolyOk(faces):
    faces1 = []
    face = []
    for j in range(len(faces)):
        if (j%2 == 0):
            faces1.append(faces[j])
        else:
            face.append(faces[j])

    faces = face
    faces1.reverse()
    faces.extend(faces1)
    return faces

def parse_plm(input_file, color_format):
    with open (input_file,'r+b') as file:
        struct.unpack('<i',file.read(4))[0] #== 5065808:
        data_len = struct.unpack('<i',file.read(4))[0]


        ##### PALT #####
        PALT = struct.unpack('<i',file.read(4))[0]

        PALT_len = struct.unpack('<i',file.read(4))[0]

        colors_list = []

        for i in range(PALT_len):
            R = 0
            G = 0
            B = 0

            R_dat = struct.unpack('<b',file.read(1))[0]
            if (R_dat <= 1):
                R = 255 + R_dat
            else:
                R = R_dat
            G_dat = struct.unpack('<b',file.read(1))[0]
            if (G_dat <= -1):
                G = 255 + G_dat
            else:
                G = G_dat
            B_dat = struct.unpack('<b',file.read(1))[0]
            if (B_dat <= -1):
                B = 255 + B_dat
            else:
                B = B_dat

            col_1 = 0
            col_2 = 0
            col_3 = 0

            if (color_format[0] == "R"):
                col_1 = R
            elif (color_format[0] == "G"):
                col_1 = G
            elif (color_format[0] == "B"):
                col_1 = B

            if (color_format[1] == "R"):
                col_2 = R
            elif (color_format[1] == "G"):
                col_2 = G
            elif (color_format[1] == "B"):
                col_2 = B

            if (color_format[2] == "R"):
                col_3 = R
            elif (color_format[2] == "G"):
                col_3 = G
            elif (color_format[2] == "B"):
                col_3 = B

            colors_list.append( (col_1, col_2, col_3) )

        return colors_list

def parse_pro(input_file, colors_list):
    with open (input_file,'r') as file:
        #read all lines first
        pro = file.readlines()
        file.close()
        # you may also want to remove whitespace characters like `\n` at the end of each line
        pro = [x.strip() for x in pro]

        ##### TEXTUREFILES #####
        texturefiles_index = pro.index([i for i in pro if "TEXTUREFILES" in i][0])
        texturefiles_num = int(re.search(r'\d+', pro[texturefiles_index]).group())
        texturefiles = []
        for i in range(texturefiles_num):
            texturefiles.append(pro[texturefiles_index + 1 + i].split(".")[0]) # так как texturefiles_index = номер строки, где написано "TEXTUREFILES", сами текстуры на одну строку ниже
                                                                               # split нужен для того, чтобы убрать всё, что после точки - например, ".txr noload"
        ##### MATERIALS #####
        materials_index = pro.index([i for i in pro if "MATERIALS" in i][0])
        materials_num = int(re.search(r'\d+', pro[materials_index]).group())
        materials = []
        for i in range(materials_num):
            materials.append(pro[materials_index + 1 + i]) # тоже самое, так как materials_index = номер строки, где написано "MATERIALS", сами материалы на одну строку ниже

        ##### Параметры материалов (col %d) #####
        material_colors = []

        for i in range(materials_num):
            colNum_str = str(re.findall(r'col\s+\d+', materials[i]))
            colNum = 0
            if (colNum_str != "[]"):
                colNum_final = str(re.findall(r'\d+', colNum_str[2:-2]))[2:-2]
                colNum = int(colNum_final) #[5:-2] нужно чтобы убрать ['tex и '], например: ['tex 10'] -> 10
                material_colors.append(str(colors_list[colNum]))
            else:
                material_colors.append("[]")


        ##### Параметры материалов (tex %d) #####
        material_textures = []

        for i in range(materials_num):
            texNum_str = str(re.findall(r't\wx\s+\d+', materials[i])) # t\wx - так как помимо tex, ещё бывает ttx
            texNum = 0
            if (texNum_str != "[]"):
                texNum_final = str(re.findall(r'\d+', texNum_str[2:-2]))[2:-2]
                texNum = int(texNum_final) #[5:-2] нужно чтобы убрать ['tex и '], например: ['tex 10'] -> 10
                material_textures.append(texturefiles[texNum-1])
            else:
                material_textures.append(material_colors[i])

        #for k in range(materials_num):

        return material_textures

def parseRAW(file, context, op, filepath):

    basename1 = os.path.basename(filepath)[:-4]
    basename2 = basename1+"_2"
    basename1 = basename1+"_1"

    vertexes = []
    faces1 = []
    faces2 = []

    counter = 0

    width = 257

    for i in range(width):
        for j in range(width):
            vertexes.append((i*10,j*10,struct.unpack('<B',file.read(1))[0]))
            file.read(1)

    for i in range(width-1):
        for j in range(i,width-1):
            counter = i*width+j
            if i == j:
                faces1.append((counter, counter+1, counter+width+1))
            else:
                faces1.append((counter, counter+1, counter+width+1, counter+width))

    for i in range(width-1):
        for j in range(i,width-1):
            counter = j*width+i
            if i == j:
                faces2.append((counter, counter+width, counter+width+1))
            else:
                faces2.append((counter, counter+1, counter+width+1, counter+width))


    b3dMesh1 = bpy.data.meshes.new(basename1)
    b3dMesh2 = bpy.data.meshes.new(basename2)

    Ev = threading.Event()
    Tr = threading.Thread(target=b3dMesh1.from_pydata, args = (vertexes,[],faces1))
    Tr.start()
    Ev.set()
    Tr.join()

    Ev = threading.Event()
    Tr = threading.Thread(target=b3dMesh2.from_pydata, args = (vertexes,[],faces2))
    Tr.start()
    Ev.set()
    Tr.join()


    b3dObj1 = bpy.data.objects.new(basename1, b3dMesh1)
    context.collection.objects.link(b3dObj1)

    b3dObj2 = bpy.data.objects.new(basename2, b3dMesh2)
    context.collection.objects.link(b3dObj2)


def read(file, context, op, filepath):
    if file.read(3) == b'b3d':
        log.info("correct file")
    else:
        log.error("b3d error")

    commonResPath = bpy.context.preferences.addons['b3d_tools'].preferences.COMMON_RES_Path

    scene = context.scene
    mytool = scene.my_tool

    #skip to materials list
    file.seek(21,1)
    Imgs = []
    math = []
    commonPalette = []
    materials = []

    noextPath, ext = os.path.splitext(filepath)
    basepath = os.path.dirname(filepath)
    basename = os.path.basename(filepath)[:-4] #cut extension


    #Пути
    resPath = ''
    if len(op.res_location) > 0 and os.path.exists(op.res_location):
        resPath = op.res_location
    else:
        resPath = os.path.join(noextPath + ".res")

    res_basepath = os.path.dirname(resPath)
    res_basename = os.path.basename(resPath)[:-4] #cut extension

    # commonPath = os.path.join(bpy.context.preferences.addons['import_b3d'].preferences.COMMON_RES_Path, r"COMMON")

    blocksToImport = op.blocks_to_import

    resModules = getattr(mytool, "resModules")
    resModule = resModules.add()
    resModule.name = res_basename

    usedBlocks = {}
    for block in blocksToImport:
        usedBlocks[block.name] = block.state

    if op.to_import_textures:
        if op.to_unpack_res:
            unpackRES(resModule, resPath, True)
        else:
            unpackRES(resModule, resPath, False)

    if op.to_import_textures and not os.path.exists(commonResPath):
        # ShowMessageBox("Common.res path is wrong or is not set. Textures weren't imported! Please, set path to Common.res in addon preferences.",
        # "COMMON.res wrong path",
        # "ERROR")
        op.to_import_textures = False

    if op.to_import_textures and os.path.exists(commonResPath):
        # commonPath = os.path.join(r"D:\_PROJECTS\DB2\Hard Truck 2", r"COMMON")
        # commonResPath = os.path.join(commonPath, r"COMMON.RES")
        commonPath = os.path.join(os.path.dirname(commonResPath))
        palettePath = os.path.join(commonPath, r"COMMON_unpack/PALETTEFILES/common.plm")
        unpackPath = os.path.join(res_basepath, res_basename + r"_unpack")
        materialsPath = os.path.join(unpackPath, r"MATERIALS", "MATERIALS.txt")
        colorsPath = os.path.join(unpackPath, r"COLORS", "COLORS.txt")
        texturePath = os.path.join(unpackPath, r"TEXTUREFILES")
        maskfiles = os.path.join(unpackPath, r"MASKFILES")

        #1. Получить общую для большинства палитру Common.plm
        if os.path.exists(commonResPath):
            commonResModule = resModules.add()
            commonResModule.name = "common"
            unpackRES(commonResModule, commonResPath)
            commonPalette = parsePLM(palettePath)
        else:
            log.warning("Failed to unpack COMMON.RES")

        #2. Распаковка .RES и конвертация .txr и .msk в .tga 32bit
        # txrFolder = os.path.join(texturePath, "txr")
        if op.to_convert_txr:
            folder_content = os.listdir(texturePath)
            reTXR = re.compile(r'\.txr')
            for path in folder_content:
                fullpath = os.path.join(texturePath, path)
                if reTXR.search(path):
                    TXRtoTGA32(fullpath)


        #3. Парсинг и добавление материалов
        createMaterials(resModule, commonPalette, texturePath, op.textures_format)

    # Parsing b3d
    material_textures = []
    materials_count = struct.unpack('<i',file.read(4))[0]
    material_list = []
    # Adding Materials
    for i in range(materials_count):

        SNImg = file.read(32).decode("utf-8").rstrip('\0') #читаю имя
        material_list.append(SNImg)

    file.seek(4,1) #Skip Begin_Chunks(111)

    # Processing vertices

    ex = 0
    i = 0
    lvl = 0
    cnt = 0
    levelGroups = []
    vertexes = []
    normals = []
    formats = []
    format = 0
    #
    vertex_block_uvs = []
    poly_block_uvs = []

    uv = []

    b3dName = os.path.basename(filepath)

    b3dObj = bpy.data.objects.new(b3dName, None)
    b3dObj['block_type'] = 0
    context.collection.objects.link(b3dObj) # root object

    objString = [b3dName]

    while ex!=ChunkType.END_CHUNKS:

        ex = openclose(file)
        if ex == ChunkType.END_CHUNK:
            del objString[-1]
            levelGroups[lvl] = 0
            lvl-=1
        elif ex == ChunkType.END_CHUNKS:
            file.close()
            break
        elif ex == ChunkType.GROUP_CHUNK:
            if len(levelGroups) <= lvl:
                for i in range(lvl+1-len(levelGroups)):
                    levelGroups.append(0)
            if lvl > 0:
                levelGroups[lvl] +=1
            continue
        elif ex == ChunkType.BEGIN_CHUNK:
            lvl+=1
            if len(levelGroups) <= lvl:
                for i in range(lvl+1-len(levelGroups)):
                    levelGroups.append(0)

            t1 = time.perf_counter()
            objString.append(objString[-1])
            onlyName = readName(file)
            type = struct.unpack("<i",file.read(4))[0]
            pos = file.tell()
            # objName = "{}_{}".format(str(type).zfill(2), onlyName)
            objName = onlyName
            realName = onlyName

            # log.debug("{}_{}".format(type, objName))
            # log.debug("{}_{}".format(lvl - 1, levelGroups))
            # log.info("Importing block #{}: {}".format(type, objName))
            # log.info("type: {}, active: {}".format(type, usedBlocks[str(type)]))
            if (type == 0): # Empty Block

                # bounding_sphere = struct.unpack("<4f",file.read(16))
                ff = file.seek(44,1)

                if not usedBlocks[str(type)]:
                    continue

                b3dObj = bpy.data.objects.new(objName, None)
                b3dObj['block_type'] = type
                b3dObj['level_group'] = levelGroups[lvl - 1]
                b3dObj['pos'] = str(pos)

                b3dObj.parent = context.scene.objects[objString[-2]]
                context.collection.objects.link(b3dObj)
                realName = b3dObj.name
                objString[len(objString)-1] = b3dName

            elif (type == 1):
                name1 = readName(file) #?
                name2 = readName(file) #?

                if not usedBlocks[str(type)]:
                    continue

                b3dObj = bpy.data.objects.new(objName, None)
                b3dObj['block_type'] = type
                b3dObj['level_group'] = levelGroups[lvl - 1]
                b3dObj['pos'] = str(pos)
                b3dObj[prop(b_1.Name1)] = name1
                b3dObj[prop(b_1.Name2)] = name2

                b3dObj.parent = context.scene.objects[objString[-2]]
                context.collection.objects.link(b3dObj)
                realName = b3dObj.name
                objString[len(objString)-1] = b3dObj.name


            elif (type == 2):	#контейнер хз
                bounding_sphere = struct.unpack("<4f",file.read(16))
                unknown_sphere = struct.unpack("<4f",file.read(16))
                childCnt = struct.unpack("<i",file.read(4))

                if not usedBlocks[str(type)]:
                    continue

                b3dObj = bpy.data.objects.new(objName, None)
                b3dObj['block_type'] = type
                b3dObj['level_group'] = levelGroups[lvl - 1]
                b3dObj['pos'] = str(pos)
                b3dObj[prop(b_2.XYZ)] = bounding_sphere[0:3]
                b3dObj[prop(b_2.R)] = bounding_sphere[3]
                b3dObj[prop(b_2.Unk_XYZ)] = unknown_sphere[0:3]
                b3dObj[prop(b_2.Unk_R)] = unknown_sphere[3]

                b3dObj.parent = context.scene.objects[objString[-2]]
                context.collection.objects.link(b3dObj)
                realName = b3dObj.name
                objString[len(objString)-1] = b3dObj.name


            elif (type == 3):	#
                bounding_sphere = struct.unpack("<4f",file.read(16))
                childCnt = struct.unpack("<i",file.read(4))

                if not usedBlocks[str(type)]:
                    continue

                b3dObj = bpy.data.objects.new(objName, None)
                b3dObj['block_type'] = type
                b3dObj['level_group'] = levelGroups[lvl - 1]
                b3dObj['pos'] = str(pos)
                b3dObj[prop(b_3.XYZ)] = bounding_sphere[0:3]
                b3dObj[prop(b_3.R)] = bounding_sphere[3]

                b3dObj.parent = context.scene.objects[objString[-2]]
                context.collection.objects.link(b3dObj)
                realName = b3dObj.name
                objString[len(objString)-1] = b3dObj.name


            elif (type == 4):	#похоже на контейнер 05 совмещенный с 12
                bounding_sphere = struct.unpack("<4f",file.read(16))
                name1 = readName(file)
                name2 = readName(file)
                childCnt = struct.unpack("<i",file.read(4))[0]

                if not usedBlocks[str(type)]:
                    continue

                b3dObj = bpy.data.objects.new(objName, None)
                b3dObj['block_type'] = type
                b3dObj['level_group'] = levelGroups[lvl - 1]
                b3dObj['pos'] = str(pos)
                b3dObj[prop(b_4.XYZ)] = bounding_sphere[0:3]
                b3dObj[prop(b_4.R)] = bounding_sphere[3]
                b3dObj[prop(b_4.Name1)] = name1
                b3dObj[prop(b_4.Name2)] = name2

                b3dObj.parent = context.scene.objects[objString[-2]]
                context.collection.objects.link(b3dObj)
                realName = b3dObj.name
                objString[len(objString)-1] = b3dObj.name

            elif (type == 5): #общий контейнер

                # bounding_sphere
                bounding_sphere = struct.unpack("<4f",file.read(16))
                name = readName(file)
                childCnt = struct.unpack("<i",file.read(4))[0]

                if not usedBlocks[str(type)]:
                    continue
                b3dObj = bpy.data.objects.new(objName, None) #create empty
                b3dObj['block_type'] = type
                b3dObj['level_group'] = levelGroups[lvl - 1]
                b3dObj['pos'] = pos
                b3dObj[prop(b_5.XYZ)] = (bounding_sphere[0:3])
                b3dObj[prop(b_5.R)] = (bounding_sphere[3])
                b3dObj[prop(b_5.Name1)] = name

                b3dObj.parent = context.scene.objects[objString[-2]]
                context.collection.objects.link(b3dObj)
                realName = b3dObj.name
                objString[len(objString)-1] = b3dObj.name

            elif (type == 6):
                vertexes = []
                uv = []
                normals = []
                normals_off = []

                bounding_sphere = struct.unpack("<4f",file.read(16))
                name1 = readName(file)
                name2 = readName(file)
                vertexCount = struct.unpack("<i",file.read(4))[0]
                for i in range (vertexCount):
                    vertexes.append(struct.unpack("<3f",file.read(12)))
                    uv.append(struct.unpack("<2f",file.read(8)))
                    normals.append((0.0, 0.0, 0.0))
                    normals_off.append(1.0)

                childCnt = struct.unpack("<i",file.read(4))[0]

                if not usedBlocks[str(type)]:
                    continue

                b3dObj = bpy.data.objects.new(objName, None)
                b3dObj['block_type'] = type
                b3dObj['level_group'] = levelGroups[lvl - 1]
                b3dObj['pos'] = str(pos)
                b3dObj[prop(b_6.XYZ)] = bounding_sphere[0:3]
                b3dObj[prop(b_6.R)] = bounding_sphere[3]
                b3dObj[prop(b_6.Name1)] = name1
                b3dObj[prop(b_6.Name2)] = name2

                b3dObj.parent = context.scene.objects[objString[-2]]
                context.collection.objects.link(b3dObj)
                realName = b3dObj.name
                objString[len(objString)-1] = b3dObj.name

            elif (type == 7):	#25? xyzuv TailLight? похоже на "хвост" движения	mesh
                format = 0
                vertexes = []
                normals = []
                normals_off = []
                # uv = []
                vertex_block_uvs = []

                vertex_block_uvs.append([])

                bounding_sphere = struct.unpack("<4f",file.read(16))
                groupName = readName(file) #0-0

                vertexCount = struct.unpack("<i",file.read(4))[0]
                for i in range(vertexCount):
                    vertexes.append(struct.unpack("<3f",file.read(12)))
                    vertex_block_uvs[0].append(struct.unpack("<2f",file.read(8)))
                    normals.append((0.0, 0.0, 0.0))
                    normals_off.append(1.0)
                    # uv.append(struct.unpack("<2f",file.read(8)))


                childCnt = struct.unpack("<i",file.read(4))[0]

                if not usedBlocks[str(type)]:
                    continue

                b3dObj = bpy.data.objects.new(objName, None)
                b3dObj['block_type'] = type
                b3dObj['level_group'] = levelGroups[lvl - 1]
                b3dObj['pos'] = pos
                b3dObj[prop(b_7.XYZ)] = bounding_sphere[0:3]
                b3dObj[prop(b_7.R)] = bounding_sphere[3]
                b3dObj[prop(b_7.Name1)] = groupName

                b3dObj.parent = context.scene.objects[objString[-2]]
                context.collection.objects.link(b3dObj)
                realName = b3dObj.name
                objString[len(objString)-1] = b3dObj.name

            elif (type == 8):	#тоже фейсы		face
                faces = []
                faces_all = []
                overriden_uvs = []
                texnums = {}
                uv_indexes = []
                formats = []
                unkFs = []
                unkInts = []
                l_normals = normals
                l_normals_off = normals_off


                bounding_sphere = struct.unpack("<4f",file.read(16)) # skip bounding sphere
                polygonCount = struct.unpack("<i",file.read(4))[0]

                for i in range(polygonCount):
                    faces = []
                    faces_new = []

                    formatRaw = struct.unpack("<i",file.read(4))[0]
                    format = formatRaw ^ 1
                    uvCount = ((format & 0xFF00) >> 8) #ah
                    triangulateOffset = format & 0b10000000

                    if format & 0b10:
                        uvCount += 1

                    if format & 0b100000 and format & 0b10000:
                        if format & 0b1:
                            log.debug("intencities 3f")
                        else:
                            log.debug("intencities f")

                    poly_block_uvs = [{}]

                    poly_block_len = len(poly_block_uvs)

                    for i in range(uvCount - poly_block_len):
                        poly_block_uvs.append({})

                    unkF = struct.unpack("<f",file.read(4))[0]
                    unkInt = struct.unpack("<i",file.read(4))[0]
                    texnum = str(struct.unpack("<i",file.read(4))[0])

                    vertexCount = struct.unpack("<i",file.read(4))[0]

                    for j in range(vertexCount):
                        face = struct.unpack("<i",file.read(4))[0]
                        faces.append(face)
                        if format & 0b10:
                            log.debug("uv override 8")
                            # uv override
                            for k in range(uvCount):
                                poly_block_uvs[k][face] = struct.unpack("<2f",file.read(8))
                        else:
                            poly_block_uvs[0][face] = vertex_block_uvs[0][face]
                        # if used with no-normals vertex blocks(6,7) use this normals
                        if format & 0b100000 and format & 0b10000:
                            if format & 0b1:
                                l_normals[face] = struct.unpack("<3f",file.read(12))
                            else:
                                l_normals_off[face] = struct.unpack("<f",file.read(4))

                    #Save materials for faces
                    if texnum in texnums:
                        texnums[texnum].append(faces)
                    else:
                        texnums[texnum] = []
                        texnums[texnum].append(faces)


                    #Without triangulation
                    # uv_new = ()
                    # for t in range(len(faces)):
                    #     uv_new = uv_new + (uv[faces[t]],)
                    # uvs.append(uv_new)
                    # faces_all.append(faces)

                    if len(poly_block_uvs) > len(overriden_uvs):
                        for i in range(len(poly_block_uvs)-len(overriden_uvs)):
                            overriden_uvs.append([])

                    #Triangulating faces
                    for t in range(len(faces)-2):
                        if not triangulateOffset:
                            if t%2 == 0:
                                faces_new.append([faces[t-1],faces[t],faces[t+1]])
                            else:
                                faces_new.append([faces[t],faces[t+1],faces[t+2]])
                        else:
                            if t%2 == 0:
                                faces_new.append([faces[t],faces[t+1],faces[t+2]])
                            else:
                                faces_new.append([faces[t],faces[t+2],faces[t+1]])

                        for u, over_uv in enumerate(poly_block_uvs):
                            if over_uv:
                                overriden_uvs[u].append((over_uv[faces_new[t][0]], over_uv[faces_new[t][1]], over_uv[faces_new[t][2]]))

                        uv_indexes.append(faces_new[t])
                        formats.append(formatRaw)
                        unkFs.append(unkF)
                        unkInts.append(unkInt)

                    faces_all.extend(faces_new)

                if not usedBlocks[str(type)]:
                    continue

                b3dMesh = (bpy.data.meshes.new(objName))

                curVertexes, curFaces, indices, oldNewTransf, newOldTransf = getUsedVerticesAndTransform(vertexes, faces_all)

                curNormals = []
                curNormalsOff = []
                for i in range(len(curVertexes)):
                    curNormals.append(l_normals[newOldTransf[i]])
                    curNormalsOff.append(l_normals_off[newOldTransf[i]])

                Ev = threading.Event()
                Tr = threading.Thread(target=b3dMesh.from_pydata, args = (curVertexes,[],curFaces))
                Tr.start()
                Ev.set()
                Tr.join()

                # newIndices = getUserVertices(curFaces)

                if len(normals) > 0:
                    b3dMesh.use_auto_smooth = True
                    normalList = []
                    for i,vert in enumerate(b3dMesh.vertices):
                        normalList.append(normals[newOldTransf[i]])
                        # b3dMesh.vertices[idx].normal = normals[idx]
                    b3dMesh.normals_split_custom_set_from_vertices(normalList)

                #Setup UV
                # customUV = b3dMesh.uv_layers.new()
                # customUV.name = "UVmap"

                # for k, texpoly in enumerate(b3dMesh.polygons):
                #     for j,loop in enumerate(texpoly.loop_indices):
                #         uvsMesh = (uvs[k][j][0], 1-uvs[k][j][1])
                #         customUV.data[loop].uv = uvsMesh


                for u, uvMap in enumerate(vertex_block_uvs):

                    customUV = b3dMesh.uv_layers.new()
                    customUV.name = "UVmapVert{}".format(u)
                    uvsMesh = []

                    for i, texpoly in enumerate(b3dMesh.polygons):
                        for j,loop in enumerate(texpoly.loop_indices):
                            uvsMesh = (uvMap[uv_indexes[i][j]][0],1 - uvMap[uv_indexes[i][j]][1])
                            customUV.data[loop].uv = uvsMesh

                for u, uvOver in enumerate(overriden_uvs):

                    customUV = b3dMesh.uv_layers.new()
                    customUV.name = "UVmapPoly{}".format(u)
                    uvsMesh = []

                    for i, texpoly in enumerate(b3dMesh.polygons):
                        for j,loop in enumerate(texpoly.loop_indices):
                            uvsMesh = [uvOver[i][j][0],1 - uvOver[i][j][1]]
                            customUV.data[loop].uv = uvsMesh

                createCustomAttribute(b3dMesh, formats, pfb_8, pfb_8.Format_Flags)
                createCustomAttribute(b3dMesh, unkFs, pfb_8, pfb_8.Unk_Float1)
                createCustomAttribute(b3dMesh, unkInts, pfb_8, pfb_8.Unk_Int2)

                createCustomAttribute(b3dMesh, curNormalsOff, pvb_8, pvb_8.Normal_Switch)
                createCustomAttribute(b3dMesh, curNormals, pvb_8, pvb_8.Custom_Normal)

                #Create Object

                b3dObj = bpy.data.objects.new(objName, b3dMesh)
                b3dObj['block_type'] = type
                b3dObj['level_group'] = levelGroups[lvl - 1]
                b3dObj['pos'] = pos
                b3dObj[prop(b_8.XYZ)] = bounding_sphere[0:3]
                b3dObj[prop(b_8.R)] = bounding_sphere[3]
                b3dObj.parent = context.scene.objects[objString[-2]]
                context.collection.objects.link(b3dObj)
                realName = b3dObj.name
                objString[len(objString)-1] = b3dObj.name

                if op.to_import_textures:
                    #For assignMaterialByVertices just-in-case
                    # bpy.ops.object.mode_set(mode = 'OBJECT')
                    #Set appropriate meaterials
                    if len(texnums.keys()) > 1:
                        for texnum in texnums:
                            mat = bpy.data.materials["{}_{}".format(resModule.name, resModule.materials[int(texnum)].name)]
                            b3dMesh.materials.append(mat)
                            lastIndex = len(b3dMesh.materials)-1

                            for vertArr in texnums[texnum]:
                                newVertArr = getUsedFace(vertArr, oldNewTransf)
                                # op.lock.acquire()
                                assignMaterialByVertices(b3dObj, newVertArr, lastIndex)
                                # op.lock.release()
                    else:
                        for texnum in texnums:
                            mat = bpy.data.materials["{}_{}".format(resModule.name, resModule.materials[int(texnum)].name)]
                            b3dMesh.materials.append(mat)



            elif (type == 9 or type == 22):

                bounding_sphere = struct.unpack("<4f",file.read(16))
                unknown_sphere = struct.unpack("<4f",file.read(16))
                childCnt = struct.unpack("<i",file.read(4))[0]

                if not usedBlocks[str(type)]:
                    continue

                b3dObj = bpy.data.objects.new(objName, None)
                b3dObj['block_type'] = type
                b3dObj['level_group'] = levelGroups[lvl - 1]
                b3dObj['pos'] = str(pos)
                b3dObj[prop(b_9.XYZ)] = bounding_sphere[0:3]
                b3dObj[prop(b_9.R)] = bounding_sphere[3]
                b3dObj[prop(b_9.Unk_XYZ)] = unknown_sphere[0:3]
                b3dObj[prop(b_9.Unk_R)] = unknown_sphere[3]

                b3dObj.parent = context.scene.objects[objString[-2]]
                context.collection.objects.link(b3dObj)
                realName = b3dObj.name
                objString[len(objString)-1] = b3dObj.name

            elif (type == 10): #контейнер, хз о чем LOD

                bounding_sphere = struct.unpack("<4f",file.read(16))
                unknown_sphere = struct.unpack("<4f",file.read(16))
                childCnt = struct.unpack("<i",file.read(4))[0]

                if not usedBlocks[str(type)]:
                    continue

                b3dObj = bpy.data.objects.new(objName, None)
                b3dObj['block_type'] = type
                b3dObj['level_group'] = levelGroups[lvl - 1]
                b3dObj['pos'] = str(pos)
                b3dObj[prop(b_10.XYZ)] = bounding_sphere[0:3]
                b3dObj[prop(b_10.R)] = bounding_sphere[3]
                b3dObj[prop(b_10.LOD_XYZ)] = unknown_sphere[0:3]
                b3dObj[prop(b_10.LOD_R)] = unknown_sphere[3]

                b3dObj.parent = context.scene.objects[objString[-2]]
                context.collection.objects.link(b3dObj)
                realName = b3dObj.name
                objString[len(objString)-1] = b3dObj.name


            elif (type == 11):
                bounding_sphere = struct.unpack("<4f",file.read(16))
                unknown_sphere = struct.unpack("<4f",file.read(16))
                childCnt = struct.unpack("<i",file.read(4))[0]

                if not usedBlocks[str(type)]:
                    continue

                b3dObj = bpy.data.objects.new(objName, None)
                b3dObj['block_type'] = type
                b3dObj['level_group'] = levelGroups[lvl - 1]
                b3dObj['pos'] = str(pos)
                b3dObj[prop(b_11.XYZ)] = bounding_sphere[0:3]
                b3dObj[prop(b_11.R)] = bounding_sphere[3]
                b3dObj[prop(b_11.Unk_XYZ)] = unknown_sphere[0:3]
                b3dObj[prop(b_11.Unk_R)] = unknown_sphere[3]

                b3dObj.parent = context.scene.objects[objString[-2]]
                context.collection.objects.link(b3dObj)
                realName = b3dObj.name
                objString[len(objString)-1] = b3dObj.name

            elif (type == 12):

                l_params = []
                bounding_sphere = struct.unpack("<4f",file.read(16))
                unknown_sphere = struct.unpack("<4f",file.read(16))
                unknown1 = struct.unpack("<i",file.read(4))[0]
                unknown2 = struct.unpack("<i",file.read(4))[0]
                cnt = struct.unpack("<i",file.read(4))[0]
                for i in range(cnt):
                    l_params.append(struct.unpack("f",file.read(4))[0])

                if not usedBlocks[str(type)]:
                    continue

                b3dObj = bpy.data.objects.new(objName, None)
                b3dObj['block_type'] = type
                b3dObj['level_group'] = levelGroups[lvl - 1]
                b3dObj['pos'] = str(pos)
                b3dObj[prop(b_12.XYZ)] = bounding_sphere[0:3]
                b3dObj[prop(b_12.R)] = bounding_sphere[3]
                b3dObj[prop(b_12.Unk_XYZ)] = unknown_sphere[0:3]
                b3dObj[prop(b_12.Unk_R)] = unknown_sphere[3]
                b3dObj[prop(b_12.Unk_Int1)] = unknown1
                b3dObj[prop(b_12.Unk_Int2)] = unknown2
                b3dObj[prop(b_12.Unk_List)] = l_params

                b3dObj.parent = context.scene.objects[objString[-2]]
                context.collection.objects.link(b3dObj)
                realName = b3dObj.name
                objString[len(objString)-1] = b3dObj.name

            elif (type == 13):

                l_params = []
                bounding_sphere = struct.unpack("<4f",file.read(16))
                unknown1 = struct.unpack("<i",file.read(4))[0]
                unknown2 = struct.unpack("<i",file.read(4))[0]
                cnt = struct.unpack("<i",file.read(4))[0]
                for i in range(cnt):
                    l_params.append(struct.unpack("f",file.read(4))[0])

                if not usedBlocks[str(type)]:
                    continue

                b3dObj = bpy.data.objects.new(objName, None)
                b3dObj['block_type'] = type
                b3dObj['level_group'] = levelGroups[lvl - 1]
                b3dObj['pos'] = str(pos)
                b3dObj[prop(b_13.XYZ)] = bounding_sphere[0:3]
                b3dObj[prop(b_13.R)] = bounding_sphere[3]
                b3dObj[prop(b_13.Unk_Int1)] = unknown1
                b3dObj[prop(b_13.Unk_Int2)] = unknown2
                b3dObj[prop(b_13.Unk_List)] = l_params

                b3dObj.parent = context.scene.objects[objString[-2]]
                context.collection.objects.link(b3dObj)
                realName = b3dObj.name
                objString[len(objString)-1] = b3dObj.name

            elif (type == 14): #sell_ ?

                l_params = []

                bounding_sphere = struct.unpack("<4f",file.read(16))
                unknown_sphere = struct.unpack("<4f",file.read(16))

                unknown1 = struct.unpack("<i",file.read(4))[0]
                unknown2 = struct.unpack("<i",file.read(4))[0]
                cnt = struct.unpack("<i",file.read(4))[0]

                for i in range(cnt):
                    l_params.append(struct.unpack("f",file.read(4))[0])

                if not usedBlocks[str(type)]:
                    continue

                b3dObj = bpy.data.objects.new(objName, None)
                b3dObj['block_type'] = type
                b3dObj['level_group'] = levelGroups[lvl - 1]
                b3dObj['pos'] = str(pos)
                b3dObj[prop(b_14.XYZ)] = bounding_sphere[0:3]
                b3dObj[prop(b_14.R)] = bounding_sphere[3]
                b3dObj[prop(b_14.Unk_XYZ)] = unknown_sphere[0:3]
                b3dObj[prop(b_14.Unk_R)] = unknown_sphere[3]
                b3dObj[prop(b_14.Unk_Int1)] = unknown1
                b3dObj[prop(b_14.Unk_Int2)] = unknown2
                b3dObj[prop(b_14.Unk_List)] = l_params

                b3dObj.parent = context.scene.objects[objString[-2]]
                context.collection.objects.link(b3dObj)
                realName = b3dObj.name
                objString[len(objString)-1] = b3dObj.name

            elif (type == 15):

                l_params = []
                bounding_sphere = struct.unpack("<4f",file.read(16))
                unknown1 = struct.unpack("<i",file.read(4))[0]
                unknown2 = struct.unpack("<i",file.read(4))[0]
                cnt = struct.unpack("<i",file.read(4))[0]
                for i in range(cnt):
                    l_params.append(struct.unpack("f",file.read(4))[0])

                if not usedBlocks[str(type)]:
                    continue

                b3dObj = bpy.data.objects.new(objName, None)
                b3dObj['block_type'] = type
                b3dObj['level_group'] = levelGroups[lvl - 1]
                b3dObj['pos'] = str(pos)
                b3dObj[prop(b_15.XYZ)] = bounding_sphere[0:3]
                b3dObj[prop(b_15.R)] = bounding_sphere[3]
                b3dObj[prop(b_15.Unk_Int1)] = unknown1
                b3dObj[prop(b_15.Unk_Int2)] = unknown2
                b3dObj[prop(b_15.Unk_List)] = l_params

                b3dObj.parent = context.scene.objects[objString[-2]]
                context.collection.objects.link(b3dObj)
                realName = b3dObj.name
                objString[len(objString)-1] = b3dObj.name

            elif (type == 16):

                l_params = []

                bounding_sphere = struct.unpack("<4f",file.read(16))
                vector1 = struct.unpack("<3f",file.read(12))
                vector2 = struct.unpack("<3f",file.read(12))
                unk1 = struct.unpack("<f",file.read(4))[0]
                unk2 = struct.unpack("<f",file.read(4))[0]

                unknown1 = struct.unpack("<i",file.read(4))[0]
                unknown2 = struct.unpack("<i",file.read(4))[0]
                cnt = struct.unpack("<i",file.read(4))[0]
                for i in range(cnt):
                    l_params.append(struct.unpack("f",file.read(4))[0])

                if not usedBlocks[str(type)]:
                    continue

                b3dObj = bpy.data.objects.new(objName, None)
                b3dObj['block_type'] = type
                b3dObj['level_group'] = levelGroups[lvl - 1]
                b3dObj['pos'] = str(pos)
                b3dObj[prop(b_16.XYZ)] = bounding_sphere[0:3]
                b3dObj[prop(b_16.R)] = bounding_sphere[3]
                b3dObj[prop(b_16.Unk_XYZ1)] = vector1
                b3dObj[prop(b_16.Unk_XYZ2)] = vector2
                b3dObj[prop(b_16.Unk_Float1)] = unk1
                b3dObj[prop(b_16.Unk_Float2)] = unk2
                b3dObj[prop(b_16.Unk_Int1)] = unknown1
                b3dObj[prop(b_16.Unk_Int2)] = unknown2
                b3dObj[prop(b_13.Unk_List)] = l_params


                b3dObj.parent = context.scene.objects[objString[-2]]
                context.collection.objects.link(b3dObj)
                realName = b3dObj.name
                objString[len(objString)-1] = b3dObj.name

            elif (type == 17):

                l_params = []

                bounding_sphere = struct.unpack("<4f",file.read(16))
                vector1 = struct.unpack("<3f",file.read(12))
                vector2 = struct.unpack("<3f",file.read(12))
                unk1 = struct.unpack("<f",file.read(4))[0]
                unk2 = struct.unpack("<f",file.read(4))[0]

                unknown1 = struct.unpack("<i",file.read(4))[0]
                unknown2 = struct.unpack("<i",file.read(4))[0]
                cnt = struct.unpack("<i",file.read(4))[0]
                for i in range(cnt):
                    l_params.append(struct.unpack("f",file.read(4))[0])

                if not usedBlocks[str(type)]:
                    continue

                b3dObj = bpy.data.objects.new(objName, None)
                b3dObj['block_type'] = type
                b3dObj['level_group'] = levelGroups[lvl - 1]
                b3dObj['pos'] = str(pos)
                b3dObj[prop(b_17.XYZ)] = bounding_sphere[0:3]
                b3dObj[prop(b_17.R)] = bounding_sphere[3]
                b3dObj[prop(b_17.Unk_XYZ1)] = vector1
                b3dObj[prop(b_17.Unk_XYZ2)] = vector2
                b3dObj[prop(b_17.Unk_Float1)] = unk1
                b3dObj[prop(b_17.Unk_Float2)] = unk2
                b3dObj[prop(b_17.Unk_Int1)] = unknown1
                b3dObj[prop(b_17.Unk_Int2)] = unknown2
                b3dObj[prop(b_17.Unk_List)] = l_params

                b3dObj.parent = context.scene.objects[objString[-2]]
                context.collection.objects.link(b3dObj)
                realName = b3dObj.name
                objString[len(objString)-1] = b3dObj.name

            elif (type == 18):	#контейнер "применить к"

                bounding_sphere = struct.unpack("<4f",file.read(16))
                space_name = readName(file)
                add_name = readName(file)
                # b3dObj['space_name'] = file.read(32).decode("utf-8").rstrip('\0')
                # b3dObj['add_name'] = file.read(32).decode("utf-8").rstrip('\0')

                if not usedBlocks[str(type)]:
                    continue

                b3dObj = bpy.data.objects.new(objName, None)
                b3dObj['block_type'] = type
                b3dObj['level_group'] = levelGroups[lvl - 1]
                b3dObj['pos'] = str(pos)
                b3dObj[prop(b_18.XYZ)] = bounding_sphere[0:3]
                b3dObj[prop(b_18.R)] = bounding_sphere[3]
                b3dObj[prop(b_18.Add_Name)] = add_name
                b3dObj[prop(b_18.Space_Name)] = space_name

                b3dObj.parent = context.scene.objects[objString[-2]]
                context.collection.objects.link(b3dObj)
                realName = b3dObj.name
                objString[len(objString)-1] = b3dObj.name


            elif (type == 19):

                childCnt = struct.unpack("i",file.read(4))[0]

                if not usedBlocks[str(type)]:
                    continue

                b3dObj = bpy.data.objects.new(objName, None)
                b3dObj['block_type'] = type
                b3dObj['level_group'] = levelGroups[lvl - 1]
                b3dObj['pos'] = str(pos)

                b3dObj.parent = context.scene.objects[objString[-2]]
                context.collection.objects.link(b3dObj)
                realName = b3dObj.name
                objString[len(objString)-1] = b3dObj.name


            elif (type == 20):
                bounding_sphere = struct.unpack("<4f",file.read(16))

                verts_count = struct.unpack("i",file.read(4))[0]

                unknown1 = struct.unpack("<i",file.read(4))[0]
                unknown2 = struct.unpack("<i",file.read(4))[0]

                unknowns = []
                cnt = struct.unpack("i",file.read(4))[0]
                for i in range(cnt):
                    unknowns.append(struct.unpack("f",file.read(4))[0])

                coords = []
                for i in range(verts_count):
                    coords.append(struct.unpack("fff",file.read(12)))

                if not usedBlocks[str(type)]:
                    continue

                curveData = bpy.data.curves.new('curve', type='CURVE')

                curveData.dimensions = '3D'
                curveData.resolution_u = 2

                # map coords to spline
                polyline = curveData.splines.new('POLY')
                polyline.points.add(len(coords)-1)
                for i, coord in enumerate(coords):
                    x,y,z = coord
                    polyline.points[i].co = (x, y, z, 1)

                curveData.bevel_depth = 0.01

                # create Object
                b3dObj = bpy.data.objects.new(objName, curveData)
                b3dObj.location = (0,0,0)
                b3dObj['block_type'] = type
                b3dObj['level_group'] = levelGroups[lvl - 1]
                b3dObj['pos'] = str(pos)
                b3dObj[prop(b_20.XYZ)] = bounding_sphere[0:3]
                b3dObj[prop(b_20.R)] = bounding_sphere[3]
                b3dObj[prop(b_20.Unk_Int1)] = unknown1
                b3dObj[prop(b_20.Unk_Int2)] = unknown2
                b3dObj[prop(b_20.Unk_List)] = unknowns

                b3dObj.parent = context.scene.objects[objString[-2]]
                context.collection.objects.link(b3dObj)
                realName = b3dObj.name
                objString[len(objString)-1] = b3dObj.name

            elif (type == 21): #testkey???

                bounding_sphere = struct.unpack("<4f",file.read(16))
                groupCnt = struct.unpack("<i",file.read(4))[0]
                unknown2 = struct.unpack("<i",file.read(4))[0]
                childCnt = struct.unpack("<i",file.read(4))[0]

                if not usedBlocks[str(type)]:
                    continue

                b3dObj = bpy.data.objects.new(objName, None)
                b3dObj['block_type'] = type
                b3dObj['level_group'] = levelGroups[lvl - 1]
                b3dObj['pos'] = str(pos)
                b3dObj[prop(b_21.XYZ)] = bounding_sphere[0:3]
                b3dObj[prop(b_21.R)] = bounding_sphere[3]
                b3dObj[prop(b_21.GroupCnt)] = groupCnt
                b3dObj[prop(b_21.Unk_Int2)] = unknown2
                b3dObj.parent = context.scene.objects[objString[-2]]
                context.collection.objects.link(b3dObj)
                realName = b3dObj.name
                objString[len(objString)-1] = b3dObj.name

            elif (type == 23): #colision mesh

                var1 = struct.unpack("<i",file.read(4))[0]
                ctype = struct.unpack("<i",file.read(4))[0]
                cnt = struct.unpack("<i",file.read(4))[0]
                unknowns = []
                for i in range(cnt):
                    unknowns.append(struct.unpack("<i",file.read(4))[0])

                vertsBlockNum = struct.unpack("<i",file.read(4))[0]
                num = 0
                faces = []
                l_vertexes = []
                for i in range(vertsBlockNum):
                    vertsInBlock = struct.unpack("<i",file.read(4))[0]

                    if (vertsInBlock == 3):
                        faces.append([num+1,num+2,num+0])
                        num+=3
                    elif(vertsInBlock ==4):
                        # faces.append([num+1,num+2,num+0,num+2,num+3,num+1])
                        faces.append([num+0,num+1,num+2,num+3])
                        num+=4

                    for j in range(vertsInBlock):
                        l_vertexes.append(struct.unpack("<3f",file.read(12)))

                if not usedBlocks[str(type)]:
                    continue

                b3dMesh = (bpy.data.meshes.new(objName))
                b3dMesh.from_pydata(l_vertexes,[],faces)

                b3dObj = bpy.data.objects.new(objName, b3dMesh)
                b3dObj['block_type'] = type
                b3dObj['level_group'] = levelGroups[lvl - 1]
                b3dObj['pos'] = str(pos)
                b3dObj[prop(b_23.Unk_Int1)] = unknown1
                b3dObj[prop(b_23.Surface)] = ctype
                b3dObj[prop(b_23.Unk_List)] = unknowns

                b3dObj.parent = context.scene.objects[objString[-2]]
                context.collection.objects.link(b3dObj)
                realName = b3dObj.name
                objString[len(objString)-1] = b3dObj.name

            elif (type == 24): #настройки положения обьекта

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

                if not usedBlocks[str(type)]:
                    continue

                x_d = 0.0
                y_d = 0.0
                z_d = 0.0

                PI = 3.14159265358979
                test_var = 0.0
                test_var = ((m33*m33) + (m31*m31))
                var_cy = sqrt(test_var)

                if (var_cy > 16*sys.float_info.epsilon):
                    z_d = atan2(m12, m22)
                    x_d = atan2(- m32, var_cy)
                    y_d = atan2(m31, m33)
                    # log.debug("MORE than 16")
                else:
                    z_d = atan2(- m21, m11)
                    x_d = atan2(- m32, var_cy)
                    y_d = 0
                    # log.debug("LESS than 16")

                rot_x = ((x_d * 180) / PI)
                rot_y = ((y_d * 180) / PI)
                rot_z = ((z_d * 180) / PI)



                b3dObj = bpy.data.objects.new(objName, None)
                b3dObj['block_type'] = type
                b3dObj['level_group'] = levelGroups[lvl - 1]
                b3dObj['pos'] = str(pos)
                b3dObj.rotation_euler[0] = x_d
                b3dObj.rotation_euler[1] = y_d
                b3dObj.rotation_euler[2] = z_d
                b3dObj.location = sp_pos
                b3dObj[prop(b_24.Flag)] = flag
                b3dObj.parent = context.scene.objects[objString[-2]]
                context.collection.objects.link(b3dObj)
                realName = b3dObj.name
                objString[len(objString)-1] = b3dObj.name

            elif (type == 25): #copSiren????/ контейнер

                unknown1 = struct.unpack("<3i",file.read(12))

                name = readName(file)
                unknown_sphere1 = struct.unpack("<3f",file.read(12))
                unknown_sphere2 = struct.unpack("<3f",file.read(12))
                unknown2 = struct.unpack("<5f",file.read(20))

                if not usedBlocks[str(type)]:
                    continue

                b3dObj = bpy.data.objects.new(objName, None)
                b3dObj['block_type'] = type
                b3dObj['level_group'] = levelGroups[lvl - 1]
                b3dObj['pos'] = str(pos)
                b3dObj[prop(b_25.XYZ)] = unknown1
                b3dObj[prop(b_25.Name)] = name
                b3dObj[prop(b_25.Unk_XYZ1)] = unknown_sphere1
                b3dObj[prop(b_25.Unk_XYZ2)] = unknown_sphere2
                b3dObj[prop(b_25.Unk_Float1)] = unknown2[0]
                b3dObj[prop(b_25.Unk_Float2)] = unknown2[1]
                b3dObj[prop(b_25.Unk_Float3)] = unknown2[2]
                b3dObj[prop(b_25.Unk_Float4)] = unknown2[3]
                b3dObj[prop(b_25.Unk_Float5)] = unknown2[4]

                b3dObj.parent = context.scene.objects[objString[-2]]
                context.collection.objects.link(b3dObj)
                realName = b3dObj.name
                objString[len(objString)-1] = b3dObj.name

            elif (type == 26):

                bounding_sphere = struct.unpack("<4f",file.read(16))

                unknown_sphere1 = struct.unpack("<3f",file.read(12))
                unknown_sphere2 = struct.unpack("<3f",file.read(12))
                unknown_sphere3 = struct.unpack("<3f",file.read(12))

                childCnt = struct.unpack("<i",file.read(4))

                if not usedBlocks[str(type)]:
                    continue

                b3dObj = bpy.data.objects.new(objName, None)
                b3dObj['block_type'] = type
                b3dObj['level_group'] = levelGroups[lvl - 1]
                b3dObj['pos'] = str(pos)
                b3dObj[prop(b_26.XYZ)] = bounding_sphere[0:3]
                b3dObj[prop(b_26.R)] = bounding_sphere[3]
                b3dObj[prop(b_26.Unk_XYZ1)] = unknown_sphere1
                b3dObj[prop(b_26.Unk_XYZ2)] = unknown_sphere2
                b3dObj[prop(b_26.Unk_XYZ3)] = unknown_sphere3

                b3dObj.parent = context.scene.objects[objString[-2]]
                context.collection.objects.link(b3dObj)
                realName = b3dObj.name
                objString[len(objString)-1] = b3dObj.name

            elif (type == 27):

                bounding_sphere = struct.unpack("<4f",file.read(16))
                flag1 = struct.unpack("<i",file.read(4))
                unknown_sphere = struct.unpack("<3f",file.read(12))

                materialId = struct.unpack("<i",file.read(4))

                if not usedBlocks[str(type)]:
                    continue

                b3dObj = bpy.data.objects.new(objName, None)
                b3dObj['block_type'] = type
                b3dObj['level_group'] = levelGroups[lvl - 1]
                b3dObj['pos'] = str(pos)
                b3dObj[prop(b_27.XYZ)] = bounding_sphere[0:3]
                b3dObj[prop(b_27.R)] = bounding_sphere[3]
                b3dObj[prop(b_27.Flag)] = flag1
                b3dObj[prop(b_27.Unk_XYZ)] = unknown_sphere
                b3dObj[prop(b_27.Material)] = materialId

                b3dObj.parent = context.scene.objects[objString[-2]]
                context.collection.objects.link(b3dObj)
                realName = b3dObj.name
                objString[len(objString)-1] = b3dObj.name

            elif (type == 28): #face

                l_vertexes = []
                l_faces = []
                faces_new = []
                l_faces_all = []
                l_uvs = []
                scale_base = 1
                curface = 0
                texnums = {}
                vertex_block_uvs = []
                vertex_block_uvs.append([])
                overriden_uvs = []
                uv_indexes = []
                formats = []
                unkFs = []
                unkInts = []

                bounding_sphere = struct.unpack("<4f",file.read(16))
                sprite_center = struct.unpack("<3f",file.read(12))

                cnt = struct.unpack("<i",file.read(4))[0]

                for i in range(cnt):

                    formatRaw = struct.unpack("<i",file.read(4))[0]
                    format = formatRaw & 0xFFFF
                    uvCount = ((formatRaw & 0xFF00) >> 8) + 1 #ah
                    triangulateOffset = format & 0b10000000

                    unkF = struct.unpack("<f",file.read(4))[0]
                    unkInt = struct.unpack("<i",file.read(4))[0]
                    texnum = struct.unpack("<i",file.read(4))[0]

                    vert_num = struct.unpack("<i", file.read(4))[0]

                    poly_block_uvs = [{}]

                    poly_block_len = len(poly_block_uvs)

                    for i in range(uvCount - poly_block_len):
                        poly_block_uvs.append({})

                    l_faces = []
                    faces_new = []

                    for k in range(vert_num):
                        scale_u = struct.unpack("<f", file.read(4))[0]
                        scale_v = struct.unpack("<f", file.read(4))[0]
                        l_vertexes.append((sprite_center[0], sprite_center[1]-scale_u*scale_base, sprite_center[2]+scale_v*scale_base))
                        l_faces.append(curface)
                        curface += 1
                        if format & 0b10:
                            vertex_block_uvs[0].append(struct.unpack("<2f",file.read(8)))
                            for j in range(uvCount-1):
                                poly_block_uvs[j][face] = struct.unpack("<2f",file.read(8))


                    #Save materials for faces
                    if texnum in texnums:
                        texnums[texnum].append(l_faces)
                    else:
                        texnums[texnum] = []
                        texnums[texnum].append(l_faces)

                    # store uv coords for each face
                    if len(poly_block_uvs) > len(overriden_uvs):
                        for i in range(len(poly_block_uvs)-len(overriden_uvs)):
                            overriden_uvs.append([])

                    #Triangulating faces
                    for t in range(len(l_faces)-2):
                        if not triangulateOffset:
                            if t%2 == 0:
                                faces_new.append([l_faces[t-1],l_faces[t],l_faces[t+1]])
                            else:
                                faces_new.append([l_faces[t],l_faces[t+1],l_faces[t+2]])
                        else:
                            if t%2 == 0:
                                faces_new.append([l_faces[t],l_faces[t+1],l_faces[t+2]])
                            else:
                                faces_new.append([l_faces[t],l_faces[t+2],l_faces[t+1]])

                        for u, over_uv in enumerate(poly_block_uvs):
                            if over_uv: #not empty
                                overriden_uvs[u].append((over_uv[faces_new[t][0]], over_uv[faces_new[t][1]], over_uv[faces_new[t][2]]))

                        # store face indexes for setting uv coords later
                        uv_indexes.append(faces_new[t])
                        formats.append(formatRaw)
                        unkFs.append(unkF)
                        unkInts.append(unkInt)

                    l_faces_all.extend(faces_new)


                if not usedBlocks[str(type)]:
                    continue

                b3dMesh = (bpy.data.meshes.new(objName))

                Ev = threading.Event()
                Tr = threading.Thread(target=b3dMesh.from_pydata, args = (l_vertexes,[],l_faces_all))
                Tr.start()
                Ev.set()
                Tr.join()

                for u, uvMap in enumerate(vertex_block_uvs):
                    if len(uvMap):
                        customUV = b3dMesh.uv_layers.new()
                        customUV.name = "UVmapVert{}".format(u)
                        uvsMesh = []

                        for i, texpoly in enumerate(b3dMesh.polygons):
                            for j,loop in enumerate(texpoly.loop_indices):
                                uvsMesh = (uvMap[uv_indexes[i][j]][0],1 - uvMap[uv_indexes[i][j]][1])
                                customUV.data[loop].uv = uvsMesh

                for u, uvOver in enumerate(overriden_uvs):
                    if len(uvOver):
                        customUV = b3dMesh.uv_layers.new()
                        customUV.name = "UVmapPoly{}".format(u)
                        uvsMesh = []

                        for i, texpoly in enumerate(b3dMesh.polygons):
                            for j,loop in enumerate(texpoly.loop_indices):
                                uvsMesh = [uvOver[i][j][0],1 - uvOver[i][j][1]]
                                customUV.data[loop].uv = uvsMesh

                if op.to_import_textures:
                    #For assignMaterialByVertices just-in-case
                    # bpy.ops.object.mode_set(mode = 'OBJECT')
                    #Set appropriate meaterials
                    if len(texnums.keys()) > 1:
                        for texnum in texnums:
                            mat = bpy.data.materials["{}_{}".format(resModule.name, resModule.materials[int(texnum)].name)]
                            b3dMesh.materials.append(mat)
                            lastIndex = len(b3dMesh.materials)-1

                            for vertArr in texnums[texnum]:
                                # op.lock.acquire()
                                assignMaterialByVertices(b3dObj, vertArr, lastIndex)
                                # op.lock.release()
                    else:
                        for texnum in texnums:
                            mat = bpy.data.materials["{}_{}".format(resModule.name, resModule.materials[int(texnum)].name)]
                            b3dMesh.materials.append(mat)

                createCustomAttribute(b3dMesh, formats, pfb_28, pfb_28.Format_Flags)
                createCustomAttribute(b3dMesh, unkFs, pfb_28, pfb_28.Unk_Float1)
                createCustomAttribute(b3dMesh, unkInts, pfb_28, pfb_28.Unk_Int2)

                b3dObj = bpy.data.objects.new(objName, b3dMesh)
                b3dObj['block_type'] = type
                b3dObj['level_group'] = levelGroups[lvl - 1]
                b3dObj['pos'] = str(pos)
                b3dObj[prop(b_28.XYZ)] = bounding_sphere[0:3]
                b3dObj[prop(b_28.R)] = bounding_sphere[3]
                b3dObj[prop(b_28.Unk_XYZ)] = sprite_center

                b3dObj.parent = context.scene.objects[objString[-2]]
                context.collection.objects.link(b3dObj) #добавляем в сцену обьект
                realName = b3dObj.name
                objString[len(objString)-1] = b3dObj.name

            elif (type == 29):

                bounding_sphere = struct.unpack("<4f",file.read(16))
                num0 = struct.unpack("<i",file.read(4))[0]
                num1 = struct.unpack("<i",file.read(4))[0]

                unknown_sphere = struct.unpack("<4f",file.read(16))

                if num0 > 0:
                    f = struct.unpack("<"+str(num0)+"f",file.read(4*num0))

                childCnt = struct.unpack("<i",file.read(4))[0]

                if not usedBlocks[str(type)]:
                    continue

                b3dObj = bpy.data.objects.new(objName, None)
                b3dObj['block_type'] = type
                b3dObj['level_group'] = levelGroups[lvl - 1]
                b3dObj['pos'] = str(pos)
                b3dObj[prop(b_29.XYZ)] = bounding_sphere[0:3]
                b3dObj[prop(b_29.R)] = bounding_sphere[3]
                b3dObj[prop(b_29.Unk_Int1)] = num0
                b3dObj[prop(b_29.Unk_Int2)] = num1
                b3dObj[prop(b_29.Unk_XYZ)] = unknown_sphere[0:3]
                b3dObj[prop(b_29.Unk_R)] = unknown_sphere[3]

                b3dObj.parent = context.scene.objects[objString[-2]]
                context.collection.objects.link(b3dObj)
                realName = b3dObj.name
                objString[len(objString)-1] = b3dObj.name

            elif (type == 30):

                bounding_sphere = struct.unpack("<4f",file.read(16))
                connectedRoomName = readName(file)

                p1 = struct.unpack("<3f",file.read(12))
                p2 = struct.unpack("<3f",file.read(12))

                if not usedBlocks[str(type)]:
                    continue

                b3dMesh = (bpy.data.meshes.new(objName))
                #0-x
                #1-y
                #2-z

                l_vertexes = [
                    (p1[0], p1[1], p1[2]),
                    (p1[0], p1[1], p2[2]),
                    (p2[0], p2[1], p2[2]),
                    (p2[0], p2[1], p1[2]),
                ]

                l_faces = [
                    (0,1,2),
                    (2,3,0)
                ]

                Ev = threading.Event()
                Tr = threading.Thread(target=b3dMesh.from_pydata, args = (l_vertexes,[],l_faces))
                Tr.start()
                Ev.set()
                Tr.join()


                b3dObj = bpy.data.objects.new(objName, b3dMesh)
                b3dObj['block_type'] = type
                b3dObj['level_group'] = levelGroups[lvl - 1]
                b3dObj['pos'] = pos
                b3dObj[prop(b_30.XYZ)] = bounding_sphere[0:3]
                b3dObj[prop(b_30.R)] = bounding_sphere[3]
                b3dObj[prop(b_30.Name)] = connectedRoomName
                b3dObj[prop(b_30.XYZ1)] = p1
                b3dObj[prop(b_30.XYZ2)] = p2

                b3dObj.parent = context.scene.objects[objString[-2]]
                context.collection.objects.link(b3dObj)
                realName = b3dObj.name
                objString[len(objString)-1] = b3dObj.name

            elif (type == 31):

                bounding_sphere = struct.unpack("<4f",file.read(16))

                num = struct.unpack("<i",file.read(4))[0]
                unknown_sphere = struct.unpack("<4f",file.read(16))
                num2 = struct.unpack("<i",file.read(4))[0]
                unknown = struct.unpack("<3f",file.read(12))
                for i in range(num):
                    struct.unpack("<fi",file.read(8))

                if not usedBlocks[str(type)]:
                    continue

                b3dObj = bpy.data.objects.new(objName, None)
                b3dObj['block_type'] = type
                b3dObj['level_group'] = levelGroups[lvl - 1]
                b3dObj['pos'] = str(pos)
                b3dObj[prop(b_31.XYZ)] = bounding_sphere[0:3]
                b3dObj[prop(b_31.R)] = bounding_sphere[3]
                b3dObj[prop(b_31.Unk_Int1)] = num
                b3dObj[prop(b_31.Unk_XYZ1)] = unknown_sphere[0:3]
                b3dObj[prop(b_31.Unk_R)] = unknown_sphere[3]
                b3dObj[prop(b_31.Unk_Int2)] = num2
                b3dObj[prop(b_31.Unk_XYZ2)] = unknown

                b3dObj.parent = context.scene.objects[objString[-2]]
                context.collection.objects.link(b3dObj)
                realName = b3dObj.name
                objString[len(objString)-1] = b3dObj.name

            elif (type == 33): #lamp

                bounding_sphere = struct.unpack("<4f",file.read(16))

                useLights = struct.unpack("<i",file.read(4))[0]
                light_type = struct.unpack("<i",file.read(4))[0]
                flag1 = struct.unpack("<i",file.read(4))[0]

                unknown_vector1 = struct.unpack("<3f",file.read(12))
                unknown_vector2 = struct.unpack("<3f",file.read(12))
                unknown1 = struct.unpack("<f",file.read(4))[0]#global_light_state
                unknown2 = struct.unpack("<f",file.read(4))[0]
                light_radius = struct.unpack("<f",file.read(4))[0]
                intensity = struct.unpack("<f",file.read(4))[0]
                unknown3 = struct.unpack("<f",file.read(4))[0]
                unknown4 = struct.unpack("<f",file.read(4))[0]
                RGB = struct.unpack("<3f",file.read(12))

                childCnt = struct.unpack("<i",file.read(4))[0]

                if not usedBlocks[str(type)]:
                    continue

                b3dObj = bpy.data.objects.new(objName, None)
                b3dObj['block_type'] = type
                b3dObj['level_group'] = levelGroups[lvl - 1]
                b3dObj['pos'] = str(pos)
                b3dObj[prop(b_33.XYZ)] = bounding_sphere[0:3]
                b3dObj[prop(b_33.R)] = bounding_sphere[3]
                b3dObj[prop(b_33.Use_Lights)] = useLights
                b3dObj[prop(b_33.Light_Type)] = light_type
                b3dObj[prop(b_33.Flag)] = flag1
                b3dObj[prop(b_33.Unk_XYZ1)] = unknown_vector1
                b3dObj[prop(b_33.Unk_XYZ2)] = unknown_vector2
                b3dObj[prop(b_33.Unk_Float1)] = unknown1
                b3dObj[prop(b_33.Unk_Float2)] = unknown2
                b3dObj[prop(b_33.Light_R)] = light_radius
                b3dObj[prop(b_33.Intens)] = intensity
                b3dObj[prop(b_33.Unk_Float3)] = unknown3
                b3dObj[prop(b_33.Unk_Float4)] = unknown4
                b3dObj[prop(b_33.RGB)] = RGB


                b3dObj.parent = context.scene.objects[objString[-2]]
                context.collection.objects.link(b3dObj)
                realName = b3dObj.name
                objString[len(objString)-1] = b3dObj.name

            elif (type == 34): #lamp
                num = 0

                bounding_sphere = struct.unpack("<4f",file.read(16))
                file.read(4) #skipped Int
                num = struct.unpack("<i",file.read(4))[0]
                l_coords = []
                for i in range(num):
                    l_coords.append(struct.unpack("<3f",file.read(12)))
                    unknown1 = struct.unpack("<f",file.read(4))

                if not usedBlocks[str(type)]:
                    continue

                curveData = bpy.data.curves.new('curve', type='CURVE')

                curveData.dimensions = '3D'
                curveData.resolution_u = 2

                # map coords to spline
                polyline = curveData.splines.new('POLY')
                polyline.points.add(len(l_coords)-1)
                for i, coord in enumerate(l_coords):
                    x,y,z = coord
                    polyline.points[i].co = (x, y, z, 1)

                curveData.bevel_depth = 0.01

                b3dObj = bpy.data.objects.new(objName, curveData)
                b3dObj['block_type'] = type
                b3dObj['level_group'] = levelGroups[lvl - 1]
                b3dObj['pos'] = str(pos)
                b3dObj[prop(b_34.XYZ)] = bounding_sphere[0:3]
                b3dObj[prop(b_34.R)] = bounding_sphere[3]

                b3dObj.parent = context.scene.objects[objString[-2]]
                context.collection.objects.link(b3dObj)
                realName = b3dObj.name
                objString[len(objString)-1] = b3dObj.name

            elif (type == 35): #mesh

                bounding_sphere = struct.unpack("<4f",file.read(16))
                faces_all = []
                faces = []
                poly_block_uvs = []

                mType = struct.unpack("<i",file.read(4))[0]
                texNum = struct.unpack("<i",file.read(4))[0]
                polygonCount = struct.unpack("<i",file.read(4))[0]
                overriden_uvs = []
                uv_indexes = []
                l_normals = normals
                l_normals_off = normals_off

                formats = []
                unkFs = []
                unkInts = []

                for i in range(polygonCount):
                    faces = []
                    formatRaw = struct.unpack("<i",file.read(4))[0]
                    format = formatRaw ^ 1
                    uvCount = ((format & 0xFF00) >> 8) #ah
                    triangulateOffset = format & 0b10000000

                    if format & 0b10:
                        uvCount += 1

                    if format & 0b100000 and format & 0b10000:
                        if format & 0b1:
                            log.debug("intencities 3f")
                        else:
                            log.debug("intencities f")

                    poly_block_uvs = [{}]

                    poly_block_len = len(poly_block_uvs)

                    for i in range(uvCount - poly_block_len):
                        poly_block_uvs.append({})

                    unkF = struct.unpack("<f",file.read(4))[0]
                    unkInt = struct.unpack("<i",file.read(4))[0]
                    texnum = str(struct.unpack("<i",file.read(4))[0])

                    vertexCount = struct.unpack("<i",file.read(4))[0]

                    for j in range(vertexCount):
                        face = struct.unpack("<i",file.read(4))[0]
                        faces.append(face)
                        if format & 0b10:
                            log.debug("uv override 35")
                            # uv override
                            for k in range(uvCount):
                                poly_block_uvs[k][face] = struct.unpack("<2f",file.read(8))
                        else:
                            poly_block_uvs[0][face] = vertex_block_uvs[0][face]
                        if format & 0b100000 and format & 0b10000:
                            if format & 0b1:
                                l_normals[face] = struct.unpack("<3f",file.read(12))
                            else:
                                l_normals_off[face] = struct.unpack("<f",file.read(4))


                    faces_all.append(faces)

                    formats.append(formatRaw)
                    unkFs.append(unkF)
                    unkInts.append(unkInt)

                    # store uv coords for each face
                    if len(poly_block_uvs) > len(overriden_uvs):
                        for i in range(len(poly_block_uvs)-len(overriden_uvs)):
                            overriden_uvs.append([])

                    for u, over_uv in enumerate(poly_block_uvs):
                        if over_uv:
                            overriden_uvs[u].append((over_uv[faces[0]], over_uv[faces[1]], over_uv[faces[2]]))

                    # store face indexes for setting uv coords later
                    uv_indexes.append((faces[0], faces[1], faces[2]))

                    #https://docs.blender.org/api/current/bpy.types.bpy_prop_collection.html#bpy.types.bpy_prop_collection
                    #seq must be uni-dimensional
                    # normals_set.extend([normals[faces[0]], normals[faces[1]], normals[faces[2]]])
                    # normals_set.extend(list(normals[faces[0]]))
                    # normals_set.extend(list(normals[faces[1]]))
                    # normals_set.extend(list(normals[faces[2]]))
                    # intens_set.extend(list(intencities[faces[0]]))
                    # intens_set.extend(list(intencities[faces[1]]))
                    # intens_set.extend(list(intencities[faces[2]]))
                    # intens_set.extend([intencities[faces[0]], intencities[faces[1]], intencities[faces[2]]])

                if not usedBlocks[str(type)]:
                    continue

                # log.debug(vertex_block_uvs)
                # log.debug(overriden_uvs)

                b3dMesh = (bpy.data.meshes.new(objName))
                curVertexes, curFaces, indices, oldNewTransf, newOldTransf = getUsedVerticesAndTransform(vertexes, faces_all)

                curNormals = []
                curNormalsOff = []
                for i in range(len(curVertexes)):
                    curNormals.append(l_normals[newOldTransf[i]])
                    curNormalsOff.append(l_normals_off[newOldTransf[i]])

                Ev = threading.Event()
                Tr = threading.Thread(target=b3dMesh.from_pydata, args = (curVertexes,[],curFaces))
                Tr.start()
                Ev.set()
                Tr.join()

                # newIndices = getUserVertices(curFaces)

                # blender generates his own normals, so imported vertex normals doesn't affect
                # them too much.
                if len(normals) > 0:
                    b3dMesh.use_auto_smooth = True
                    normalList = []
                    for i,vert in enumerate(b3dMesh.vertices):
                        normalList.append(normals[newOldTransf[i]])
                        # b3dMesh.vertices[idx].normal = normals[idx]
                    # log.debug(normalList)
                    b3dMesh.normals_split_custom_set_from_vertices(normalList)

                # if len(normals) > 0:
                #     for i,idx in enumerate(newIndices):
                #         b3dMesh.vertices[idx].normal = normals[idx]



                for u, uvMap in enumerate(vertex_block_uvs):

                    customUV = b3dMesh.uv_layers.new()
                    customUV.name = "UVmapVert{}".format(u)
                    uvsMesh = []

                    for i, texpoly in enumerate(b3dMesh.polygons):
                        for j,loop in enumerate(texpoly.loop_indices):
                            uvsMesh = (uvMap[uv_indexes[i][j]][0],1 - uvMap[uv_indexes[i][j]][1])
                            customUV.data[loop].uv = uvsMesh

                for u, uvOver in enumerate(overriden_uvs):

                    customUV = b3dMesh.uv_layers.new()
                    customUV.name = "UVmapPoly{}".format(u)
                    uvsMesh = []

                    for i, texpoly in enumerate(b3dMesh.polygons):
                        for j,loop in enumerate(texpoly.loop_indices):
                            uvsMesh = [uvOver[i][j][0],1 - uvOver[i][j][1]]
                            customUV.data[loop].uv = uvsMesh


                # b3dMesh.attributes["my_normal"].data.foreach_set("vector", normals_set)

                createCustomAttribute(b3dMesh, formats, pfb_35, pfb_35.Format_Flags)
                createCustomAttribute(b3dMesh, unkFs, pfb_35, pfb_35.Unk_Float1)
                createCustomAttribute(b3dMesh, unkInts, pfb_35, pfb_35.Unk_Int2)

                createCustomAttribute(b3dMesh, curNormalsOff, pvb_35, pvb_35.Normal_Switch)
                createCustomAttribute(b3dMesh, curNormals, pvb_35, pvb_35.Custom_Normal)

                if op.to_import_textures:
                    mat = bpy.data.materials["{}_{}".format(resModule.name, resModule.materials[int(texNum)].name)]
                    b3dMesh.materials.append(mat)


                b3dObj = bpy.data.objects.new(objName, b3dMesh)
                b3dObj.parent = context.scene.objects[objString[-2]]
                b3dObj['block_type'] = type
                b3dObj['level_group'] = levelGroups[lvl - 1]
                b3dObj['pos'] = str(pos)
                b3dObj[prop(b_35.XYZ)] = bounding_sphere[0:3]
                b3dObj[prop(b_35.R)] = bounding_sphere[3]
                b3dObj[prop(b_35.MType)] = mType
                b3dObj[prop(b_35.TexNum)] = texNum
                b3dObj['FType'] = 0
                try:
                    b3dObj['SType'] = b3dObj.parent['SType']
                except:
                    b3dObj['SType'] = 2
                b3dObj['BType'] = 35
                realName = b3dObj.name
                # for face in b3dMesh.polygons:
                #     face.use_smooth = True
                context.collection.objects.link(b3dObj) #добавляем в сцену обьект
                objString[len(objString)-1] = b3dObj.name

            elif (type == 36):

                vertexes = []
                normals = []
                normals_off = []
                uv = []
                vertex_block_uvs = []

                bounding_sphere = struct.unpack("<4f",file.read(16))
                name1 = readName(file)
                name2 = readName(file)

                formatRaw = struct.unpack("<i",file.read(4))[0]
                uvCount = formatRaw >> 8
                format = formatRaw & 0xFF

                if format == 1 or format == 2:
                    log.debug("normals 3f")
                elif format == 3:
                    log.debug("normals f")

                vertex_block_uvs.append([])
                for i in range(uvCount):
                    vertex_block_uvs.append([])

                vertexCount = struct.unpack("<i",file.read(4))[0]
                if format == 0:
                    # objString[len(objString)-1] = objString[-2]
                    pass
                else:
                    for i in range(vertexCount):
                        vertexes.append(struct.unpack("<3f",file.read(12)))
                        vertex_block_uvs[0].append(struct.unpack("<2f",file.read(8)))
                        for j in range(uvCount):
                            vertex_block_uvs[j+1].append(struct.unpack("<2f",file.read(8)))
                        if format == 1 or format == 2:	#Vertex with normals
                            normals.append(struct.unpack("<3f",file.read(12)))
                            normals_off.append(1.0)
                        elif format == 3: #отличается от шаблона 010Editor
                            normals.append((0.0, 0.0, 0.0))
                            normals_off.append(struct.unpack("<f",file.read(4))[0])
                        else:
                            normals.append((0.0, 0.0, 0.0))
                            normals_off.append(1.0)

                childCnt = struct.unpack("<i",file.read(4))[0]#01 00 00 00 subblocks count

                if not usedBlocks[str(type)]:
                    continue

                b3dObj = bpy.data.objects.new(objName, None)
                b3dObj['block_type'] = type
                b3dObj['level_group'] = levelGroups[lvl - 1]
                b3dObj['pos'] = pos
                b3dObj[prop(b_36.XYZ)] = bounding_sphere[0:3]
                b3dObj[prop(b_36.R)] = bounding_sphere[3]
                b3dObj[prop(b_36.Name1)] = name1
                b3dObj[prop(b_36.Name2)] = name2
                b3dObj[prop(b_36.MType)] = format

                b3dObj.parent = context.scene.objects[objString[-2]]
                context.collection.objects.link(b3dObj)
                realName = b3dObj.name
                objString[len(objString)-1] = b3dObj.name

            elif (type == 37):

                vertexes = []
                normals = []
                normals_off = []
                vertex_block_uvs = []
                uv = []

                bounding_sphere = struct.unpack("<4f",file.read(16))

                groupName = readName(file)

                formatRaw = struct.unpack("<i",file.read(4))[0]
                uvCount = formatRaw >> 8
                format = formatRaw & 0xFF

                if format == 1 or format == 2:
                    log.debug("normals 3f")
                elif format == 3:
                    log.debug("normals f")

                vertex_block_uvs.append([])
                for i in range(uvCount):
                    vertex_block_uvs.append([])


                vertexCount = struct.unpack("<i",file.read(4))[0]

                if vertexCount > 0:

                    if format == 0:
                        # objString[len(objString)-1] = objString[-2]
                        pass
                    else:
                        for i in range(vertexCount):
                            vertexes.append(struct.unpack("<3f",file.read(12)))
                            vertex_block_uvs[0].append(struct.unpack("<2f",file.read(8)))
                            for j in range(uvCount):
                                vertex_block_uvs[j+1].append(struct.unpack("<2f",file.read(8)))
                            if format == 1 or format == 2:	#Vertex with normals
                                normals.append(struct.unpack("<3f",file.read(12)))
                                normals_off.append(1.0)
                            elif format == 3: #отличается от шаблона 010Editor
                                normals.append((0.0, 0.0, 0.0))
                                normals_off.append(struct.unpack("<f",file.read(4))[0])
                            else:
                                normals.append((0.0, 0.0, 0.0))
                                normals_off.append(1.0)

                childCnt = struct.unpack("<i",file.read(4))[0]#01 00 00 00 subblocks count

                # if len(vertex_block_uvs) == 2:
                #     vertex_block_uvs = [vertex_block_uvs[1], vertex_block_uvs[0]]


                if not usedBlocks[str(type)]:
                    continue

                b3dObj = bpy.data.objects.new(objName, None) #create empty
                b3dObj['block_type'] = type
                b3dObj['level_group'] = levelGroups[lvl - 1]
                b3dObj['pos'] = pos
                b3dObj[prop(b_37.XYZ)] = bounding_sphere[0:3]
                b3dObj[prop(b_37.R)] = bounding_sphere[3]
                b3dObj[prop(b_37.Name1)] = groupName
                b3dObj[prop(b_37.SType)] = format

                b3dObj.parent = context.scene.objects[objString[-2]]
                context.collection.objects.link(b3dObj)
                realName = b3dObj.name
                objString[len(objString)-1] = b3dObj.name

            elif (type == 39):

                bounding_sphere = struct.unpack("<4f",file.read(16))
                color_r = struct.unpack("<i",file.read(4))
                unknown = struct.unpack("<f",file.read(4))
                fog_start = struct.unpack("<f",file.read(4))
                fog_end = struct.unpack("<f",file.read(4))
                colorId = struct.unpack("<i",file.read(4))
                childCnt = struct.unpack("<i",file.read(4))

                if not usedBlocks[str(type)]:
                    continue

                b3dObj = bpy.data.objects.new(objName, None)
                b3dObj['block_type'] = type
                b3dObj['level_group'] = levelGroups[lvl - 1]
                b3dObj['pos'] = str(pos)
                b3dObj[prop(b_39.XYZ)] = bounding_sphere[0:3]
                b3dObj[prop(b_39.R)] = bounding_sphere[3]
                b3dObj[prop(b_39.Color_R)] = color_r
                b3dObj[prop(b_39.Unk_Float1)] = unknown
                b3dObj[prop(b_39.Fog_Start)] = fog_start
                b3dObj[prop(b_39.Fog_End)] = fog_end
                b3dObj[prop(b_39.Color_Id)] = colorId

                b3dObj.parent = context.scene.objects[objString[-2]]
                context.collection.objects.link(b3dObj)
                realName = b3dObj.name
                objString[len(objString)-1] = b3dObj.name

            elif (type == 40):
                data = []
                data1 = []

                bounding_sphere = struct.unpack("<4f",file.read(16))

                name1 = readName(file)
                name2 = readName(file)

                unknown1 = struct.unpack("<i",file.read(4))[0]
                unknown2 = struct.unpack("<i",file.read(4))[0]
                num = struct.unpack("<i",file.read(4))[0]
                for i in range(num):
                    data1.append(struct.unpack("f", file.read(4))[0])

                if not usedBlocks[str(type)]:
                    continue

                b3dObj = bpy.data.objects.new(objName, None)
                b3dObj['block_type'] = type
                b3dObj['level_group'] = levelGroups[lvl - 1]
                b3dObj['pos'] = str(pos)
                b3dObj[prop(b_40.XYZ)] = bounding_sphere[0:3]
                b3dObj[prop(b_40.R)] = bounding_sphere[3]
                b3dObj[prop(b_40.Name1)] = name1
                b3dObj[prop(b_40.Name2)] = name2
                b3dObj[prop(b_40.Unk_Int1)] = unknown1
                b3dObj[prop(b_40.Unk_Int2)] = unknown2

                b3dObj.location = bounding_sphere[:3]
                context.collection.objects.link(b3dObj)
                realName = b3dObj.name

                b3dObj.parent = context.scene.objects[objString[-2]]
                objString[len(objString)-1] = b3dObj.name

            else:
                log.warning('smthng wrng')
                return

            t2 = time.perf_counter()

            log.info("Time: {} | Block #{}: {}".format(t2-t1, type, realName))

def readWayTxt(file, context, op, filepath):
    b3dObj = 0
    # b3dObj = bpy.data.objects.new(os.path.basename(op.properties.filepath),None)
    # context.collection.objects.link(b3dObj)

    # objString = [os.path.basename(op.properties.filepath)]

    type = None
    mnam_c = 0

    grom = 0
    rnod = 1
    rseg = 2
    mnam = 3
    mnam2nd = 4

    lineNum = 0

    for line in file:
        if (type == grom):
            lineNum+=1
            if (lineNum == 2): #GROM ROOM
                b3dObj = bpy.data.objects.new(line.strip(),None)
                b3dObj.parent = context.scene.objects[objString[-1]]
                context.collection.objects.link(b3dObj)
                objString.append(line.strip())
            elif (lineNum == 3):
                type = None			#GROM RESET
                lineNum = 0
        elif(type == rnod):
            lineNum+=1
            if (lineNum == 2): #RNOD ROOM
                bpy.ops.mesh.primitive_ico_sphere_add(size=10, location=(0,0,0))
                b3dObj = bpy.context.object
                b3dObj.name = line.strip()
                b3dObj.parent = context.scene.objects[objString[-1]]
                objString.append(line.strip())
            elif (lineNum == 4): #RNOD POS

                b3dObj.location = make_tuple(line.strip())#loc
            elif (lineNum == 5):
                type = None			#RNOD RESET
                lineNum = 0
                del objString[-1]
        elif(type == rseg):
            massline = 0
            lineNum+=1
            if (line[2:6]=='RTEN'):
                massline = 6
            else:
                massline = 4
            if (lineNum == massline): #RSEG MASS

                b3dObj = bpy.data.objects.new('RSEG',None)				#
                b3dObj.parent = context.scene.objects[objString[-1]]	#
                objString.append(b3dObj.name)
                context.collection.objects.link(b3dObj)


                mass = make_tuple(line.strip())
                for pos in mass:
                    bpy.ops.mesh.primitive_cylinder_add(radius = 1,location = pos)
                    b3dObj = bpy.context.object
                    b3dObj.name = 'location'
                    b3dObj.parent = context.scene.objects[objString[-1]]
                    #objString.append('RSEG')
                bpy.ops.curve.primitive_bezier_curve_add()
                b3dObj = bpy.context.object

                b3dObj.parent = context.scene.objects[objString[-1]]
                b3dObj.name = 'RSEGBezier'
                b3dObj.data.dimensions = '3D'
                b3dObj.data.fill_mode = 'FULL'
                b3dObj.data.bevel_depth = 0.1
                b3dObj.data.bevel_resolution = 4

                flatten = lambda mass: [item for sublist in mass for item in sublist]
                b3dObj.data.splines[0].bezier_points.add(len(mass)-2)
                b3dObj.data.splines[0].bezier_points.foreach_set("co",flatten(mass))

                points = b3dObj.data.splines[0].bezier_points

                for i,point in enumerate(points):
                    point.handle_left_type = point.handle_right_type = "AUTO"

                type = None 	#reset
                lineNum = 0
                del objString[-1]
        elif(type == mnam):
            b3dObj = bpy.data.objects.new(line[1:mnam_c],None)
            b3dObj['root'] = True
            context.collection.objects.link(b3dObj)

            objString = [b3dObj.name]
            type = None

        elif(type == None):
            if (line[0:2] == '  '):
                if (line[2:6] == 'RNOD'):
                    type = rnod
                elif (line[2:6] == 'RSEG'):
                    type = rseg
            else:
                if (line[0:4] == 'GROM'):
                    if (len(objString)>1):
                        del objString[-1]
                    type = grom
                elif(line[0:4] == 'MNAM'):
                    mnam_c = int(line[5])
                    type = mnam








def assignMaterialByVertices(obj, vertIndexes, matIndex):
    bpy.context.view_layer.objects.active = obj
    # bpy.ops is slow https://blender.stackexchange.com/questions/2848/why-avoid-bpy-ops#comment11187_2848
    # bpy.ops.object.mode_set(mode = 'EDIT')
    # bpy.ops.mesh.select_mode(type= 'VERT')
    # bpy.ops.mesh.select_all(action = 'DESELECT')
    # bpy.ops.object.mode_set(mode = 'OBJECT')
    vert = obj.data.vertices
    face = obj.data.polygons
    edge = obj.data.edges
    for i in face:
        i.select=False
    for i in edge:
        i.select=False
    for i in vert:
        i.select=False

    for idx in vertIndexes:
        obj.data.vertices[idx].select = True
    selectedPolygons = getPolygonsBySelectedVertices(bpy.context.view_layer.objects.active)
    for poly in selectedPolygons:
        poly.material_index = matIndex

def getRESFolder(filepath):
    basename = os.path.basename(filepath)
    basepath = os.path.dirname(filepath)
    return os.path.join(basepath, "{}_unpack".format(basename[:-4]))

def saveMaterial(resModule, materialStr):
    nameSplit = materialStr.split(" ")
    name = nameSplit[0]
    params = nameSplit[1:]

    material = resModule.materials.add()
    material.name = name
    i = 0
    while i < len(params):
        paramName = params[i].replace('"', '')
        if paramName in ["tex", "ttx", "itx"]:
            setattr(material, "is_tex", True)
            setattr(material, paramName, int(params[i+1]))
            i+=1
        elif paramName in ["col", "att", "msk", "power", "coord"]:
            setattr(material, "is_" + paramName, True)
            setattr(material, paramName, int(params[i+1]))
            i+=1
        elif paramName in ["reflect", "specular", "transp", "rot"]:
            setattr(material, paramName, float(params[i+1]))
            i+=1
        elif paramName in ["noz", "nof", "notile", "notiveu", "notilev", \
                            "alphamirr", "bumpcoord", "usecol", "wave"]:
            setattr(material, "is_" + paramName, True)
            i+=1
        elif paramName in ["RotPoint", "move"]:
            setattr(material, "is_" + paramName, True)
            setattr(material, paramName, [float(params[i+1]), float(params[i+2])])
            i+=2
        elif paramName[0:3] == "env":
            setattr(material, "is_env", True)
            envid = paramName[3:]
            setattr(material, "env", [float(params[i+1]), float(params[i+2])])
            i+=2
            if len(envid) > 0:
                setattr(material, "envId", int(envid))
        i+=1

def saveMaskfile(resModule, maskfileStr):
    nameSplit = maskfileStr.split(" ")
    rawName = nameSplit[0]
    params = nameSplit[1:]

    name = rawName.split("\\")[-1][:-4]

    maskfile = resModule.maskfiles.add()
    maskfile.name = name
    i = 0
    while i < len(params):
        paramName = params[i].replace('"', '')
        if paramName == "noload":
            setattr(maskfile, "is_noload", True)
        else:
            someInt = None
            try:
                someInt = int(someInt)
            except:
                pass
            if someInt:
                setattr(maskfile, "is_someint", True)
                setattr(maskfile, "someint", someInt)
        i+=1

def saveTexture(resModule, textueStr):
    nameSplit = textueStr.split(" ")
    rawName = nameSplit[0]
    params = nameSplit[1:]

    name = rawName.split("\\")[-1][:-4]
    log.debug(name)

    texture = resModule.textures.add()
    texture.name = name
    i = 0
    while i < len(params):
        paramName = params[i].replace('"', '')
        if paramName in ["noload", "bumpcoord", "memfix"]:
            setattr(texture, "is_" + paramName, True)
        else:
            someInt = None
            try:
                someInt = int(someInt)
            except:
                pass
            if someInt:
                setattr(texture, "is_someint", True)
                setattr(texture, "someint", someInt)
        i+=1


def unpackRES(resModule, filepath, saveOnDisk = True):
    log.info("Unpacking {}:".format(filepath))

    # filename, resExtension = os.path.splitext(filepath)
    # basename = os.path.basename(filepath)[:-4]
    # basepath = os.path.dirname(filepath)
    resdir = getRESFolder(filepath)
    curfolder = resdir
    if not os.path.exists(resdir):
        os.mkdir(resdir)

    with open(filepath, "rb") as resFile:
        while 1:
            category = readCString(resFile)
            if(len(category) > 0):
                log.info(category)
                resSplit = category.split(" ")
                id = resSplit[0]
                cnt = int(resSplit[1])
                log.info("Reading category {}".format(id))
                log.info("Element count in category is {}.".format(cnt))
                binfilePath = None
                if cnt > 0:
                    elements = []
                    log.info("Start processing...")
                    curfolder = os.path.join(resdir,id)
                    if id == "COLORS" or id == "MATERIALS" or id == "SOUNDS":
                        if saveOnDisk:
                            binfilePath = os.path.join(curfolder, "{}.txt".format(id))
                            binfileBase = os.path.dirname(binfilePath)
                            binfileBase = Path(binfileBase)
                            binfileBase.mkdir(exist_ok=True, parents=True)
                        rawStrings = []
                        for i in range(cnt):
                            rawString = readCString(resFile)
                            rawStrings.append(rawString)
                        if id == "MATERIALS":
                            if saveOnDisk:
                                with open(binfilePath, "wb") as outFile:
                                    for rawString in rawStrings:
                                        saveMaterial(resModule, rawString)
                                        # nameSplit = rawString.split(" ")
                                        # name = nameSplit[0]
                                        # params = " ".join(nameSplit[1:])
                                        # unpacked.materials.append(name)
                                        # unpacked.materialParams.append(params)
                                        outFile.write((rawString+"\n").encode("UTF-8"))
                            else:
                                for rawString in rawStrings:
                                    saveMaterial(resModule, rawString)
                                    # nameSplit = rawString.split(" ")
                                    # name = nameSplit[0]
                                    # params = " ".join(nameSplit[1:])
                                    # unpacked.materials.append(name)
                                    # unpacked.materialParams.append(params)
                        elif id == "COLORS":
                            if saveOnDisk:
                                with open(binfilePath, "wb") as outFile:
                                    for rawString in rawStrings:
                                        # unpacked.colors.append(rawString)
                                        outFile.write((rawString+"\n").encode("UTF-8"))
                            else:
                                for rawString in rawStrings:
                                    pass
                                    # unpacked.colors.append(rawString)
                        else:
                            if saveOnDisk:
                                with open(binfilePath, "wb") as outFile:
                                    for rawString in rawStrings:
                                        outFile.write((rawString+"\n").encode("UTF-8"))
                    else: #TEXTUREFILES and MASKFILES
                        rawStrings = []
                        for i in range(cnt):
                            rawString = readCString(resFile)
                            rawStrings.append(rawString)

                            nameSplit = rawString.split(" ")
                            fullname = nameSplit[0]
                            lastpath = fullname.split("\\")
                            name = "\\".join(lastpath[len(lastpath)-1:])
                            sectionSize = struct.unpack("<i	",resFile.read(4))[0]
                            bytes = resFile.read(sectionSize)
                            if saveOnDisk:
                                binfilePath = os.path.join(curfolder, "{}".format(name))
                                binfileBase = os.path.dirname(binfilePath)
                                binfileBase = Path(binfileBase)
                                binfileBase.mkdir(exist_ok=True, parents=True)
                                with open(binfilePath, "wb") as binfile:
                                    log.info("Saving file {}".format(binfile.name))
                                    binfile.write(bytes)
                        if id == "TEXTUREFILES":
                            for rawString in rawStrings:
                                saveTexture(resModule, rawString)
                                # unpacked.textures.append(name)
                        if id == "MASKFILES":
                            for rawString in rawStrings:
                                saveMaskfile(resModule, rawString)
                                # unpacked.maskfiles.append(name)
                else:
                    log.info("Skip category")
            else:
                break

    return