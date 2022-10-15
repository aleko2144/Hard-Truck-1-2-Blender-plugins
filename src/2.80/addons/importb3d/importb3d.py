import enum
from hashlib import new
import struct
import sys
import time
import timeit
import threading
import pdb
import logging
from pathlib import Path
from .imghelp import TXRtoTGA32
from .imghelp import parsePLM
from .common import ShowMessageBox, Vector3F, createMaterial, getUsedFaces, getUsedFace, getUsedVerticesAndTransform, getUserVertices, parseMaterials, readCString, RESUnpack, transformVertices

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

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
log = logging.getLogger("importb3d")
log.setLevel(logging.DEBUG)

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
                # log.debug('Triangle')
                faces1.append((counter, counter+1, counter+width+1))
            else:
                # log.debug('Quad')
                faces1.append((counter, counter+1, counter+width+1, counter+width))

    log.debug(faces1)

    for i in range(width-1):
        for j in range(i,width-1):
            counter = j*width+i
            if i == j:
                # log.debug('Triangle')
                faces2.append((counter, counter+width, counter+width+1))
            else:
                # log.debug('Quad')
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

    commonResPath = bpy.context.preferences.addons['importb3d'].preferences.COMMON_RES_Path


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
    resPath = os.path.join(noextPath + ".res")
    # commonPath = os.path.join(bpy.context.preferences.addons['importb3d'].preferences.COMMON_RES_Path, r"COMMON")

    blocksToImport = op.blocks_to_import

    usedBlocks = {}
    for block in blocksToImport:
        usedBlocks[block.name] = block.state

    RESUnpacked = None
    if op.to_import_textures:
        if op.to_unpack_res:
            RESUnpacked = unpackRES(resPath, basename, True)
        else:
            RESUnpacked = unpackRES(resPath, basename, False)

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
        unpackPath = os.path.join(basepath, basename + r"_unpack")
        materialsPath = os.path.join(unpackPath, r"MATERIALS", "MATERIALS.txt")
        colorsPath = os.path.join(unpackPath, r"COLORS", "COLORS.txt")
        texturePath = os.path.join(unpackPath, r"TEXTUREFILES")
        maskfiles = os.path.join(unpackPath, r"MASKFILES")

        #1. Получить общую для большинства палитру Common.plm
        if os.path.exists(commonResPath):
            unpackRES(commonResPath, "common")
            commonPalette = parsePLM(palettePath)
        else:
            log.warning("Failed to unpack COMMON.RES")

    # RESUnpacked = unpackRES(resPath, basename)

        #2. Распаковка .RES и конвертация .txr и .msk в .tga 32bit
        # txrFolder = os.path.join(texturePath, "txr")
        folder_content = os.listdir(texturePath)
        reTXR = re.compile(r'\.txr')
        for path in folder_content:
            fullpath = os.path.join(texturePath, path)
            if reTXR.search(path):
                TXRtoTGA32(fullpath)

        #3. Парсинг и добавление материалов
        materials = parseMaterials(materialsPath, basename)
        for material in materials:
            createMaterial(commonPalette, RESUnpacked.textures, texturePath, material, op.textures_format)

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
    uv = []

    b3dName = os.path.basename(filepath)

    b3dObj = bpy.data.objects.new(b3dName,None)
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
            # log.info("Importing block #{}: {}".format(type, objName))
            # log.info("type: {}, active: {}".format(type, usedBlocks[str(type)]))
            if (type == 0): # Empty Block
                bounding_sphere = struct.unpack("<4f",file.read(16))
                ff = file.seek(28,1)

                if not usedBlocks[str(type)]:
                    continue
                objString[len(objString)-1] = b3dName

            elif (type == 1):
                name1 = readName(file) #?
                name2 = readName(file) #?

                if not usedBlocks[str(type)]:
                    continue

                b3dObj = bpy.data.objects.new(objName, None)
                b3dObj['block_type'] = type
                b3dObj['level_group'] = levelGroups[lvl-1]
                b3dObj['pos'] = str(pos)

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
                b3dObj['level_group'] = levelGroups[lvl-1]
                b3dObj['pos'] = str(pos)

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
                b3dObj['level_group'] = levelGroups[lvl-1]
                b3dObj['pos'] = str(pos)

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
                b3dObj['level_group'] = levelGroups[lvl-1]
                b3dObj['pos'] = str(pos)

                b3dObj.parent = context.scene.objects[objString[-2]]
                context.collection.objects.link(b3dObj)
                realName = b3dObj.name
                objString[len(objString)-1] = b3dObj.name

            elif (type==5): #общий контейнер

                bounding_sphere = struct.unpack("<4f",file.read(16))
                name = readName(file)
                childCnt = struct.unpack("<i",file.read(4))[0]

                if not usedBlocks[str(type)]:
                    continue
                b3dObj = bpy.data.objects.new(objName, None) #create empty
                b3dObj['block_type'] = type
                b3dObj['level_group'] = levelGroups[lvl-1]
                b3dObj['pos'] = pos

                b3dObj.parent = context.scene.objects[objString[-2]]
                context.collection.objects.link(b3dObj)
                realName = b3dObj.name
                objString[len(objString)-1] = b3dObj.name

            elif (type == 6):
                vertexes = []
                uv = []

                bounding_sphere = struct.unpack("<4f",file.read(16))
                name1 = readName(file)
                name2 = readName(file)
                vertexCount = struct.unpack("<i",file.read(4))[0]
                for i in range (vertexCount):
                    vertexes.append(struct.unpack("<3f",file.read(12)))
                    uv.append(struct.unpack("<2f",file.read(8)))

                childCnt = struct.unpack("<i",file.read(4))[0]

                if not usedBlocks[str(type)]:
                    continue

                b3dObj = bpy.data.objects.new(objName, None)
                b3dObj['block_type'] = type
                b3dObj['level_group'] = levelGroups[lvl-1]
                b3dObj['pos'] = str(pos)

                b3dObj.parent = context.scene.objects[objString[-2]]
                context.collection.objects.link(b3dObj)
                realName = b3dObj.name
                objString[len(objString)-1] = b3dObj.name

            elif (type == 7):	#25? xyzuv TailLight? похоже на "хвост" движения	mesh
                format = 0
                coords25 = []
                vertexes = []
                normals = []
                uv = []

                bounding_sphere = struct.unpack("<4f",file.read(16))
                groupName = readName(file) #0-0

                vertexCount = struct.unpack("<i",file.read(4))[0]
                for i in range(vertexCount):
                    vertexes.append(struct.unpack("<3f",file.read(12)))
                    uv.append(struct.unpack("<2f",file.read(8)))

                childCnt = struct.unpack("<i",file.read(4))[0]

                if not usedBlocks[str(type)]:
                    continue

                b3dObj = bpy.data.objects.new(objName, None)
                b3dObj['block_type'] = type
                b3dObj['level_group'] = levelGroups[lvl-1]
                b3dObj['pos'] = pos

                b3dObj.parent = context.scene.objects[objString[-2]]
                context.collection.objects.link(b3dObj)
                realName = b3dObj.name
                objString[len(objString)-1] = b3dObj.name

            elif (type == 8):	#тоже фейсы		face
                faces = []
                faces_all = []
                uvs = []
                # normals = []
                intencities = []
                texnums = {}
                b3dMesh = bpy.data.meshes.new(objName)
                l_uv = uv.copy()
                vert_uvs = []

                bounding_sphere = struct.unpack("<4f",file.read(16)) # skip bounding sphere
                polygonCount = struct.unpack("<i",file.read(4))[0]

                for i in range(polygonCount):
                    faces = []
                    faces_new = []

                    formatRaw = struct.unpack("<i",file.read(4))[0]
                    format = formatRaw ^ 1
                    coordsPerVertex = (format & 0xFF00) >> 8 #ah
                    triangulateOffset = format & 0b10000000

                    if format & 0b10:
                        coordsPerVertex += 1

                    uunknown = struct.unpack("<fi",file.read(8))
                    texnum = str(struct.unpack("i",file.read(4))[0])

                    vertexCount = struct.unpack("<i",file.read(4))[0]

                    for j in range(vertexCount):
                        face = struct.unpack("<i",file.read(4))[0]
                        faces.append(face)
                        if format & 0b10:
                            for k in range(coordsPerVertex):
                                vert_uvs.append(struct.unpack("<2f",file.read(8)))
                            # uv override
                            if len(vert_uvs) > 0:
                                l_uv[face] = vert_uvs[len(vert_uvs)-1]
                        if format & 0b10000:
                            if format & 0b1:
                                if format & 0b100000:
                                    intens = struct.unpack("<3f",file.read(12))
                                    intencities.append(intens)
                            elif format & 0b100000:
                                intencity = struct.unpack("<f",file.read(4))
                                intens = intencity + (0.0,0.0)
                                # intens = (0.0,) + intencity + (0.0,)
                                # intens = (0.0,0.0) + intencity
                                intencities.append(intens)

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

                        uvs.append((l_uv[faces_new[t][0]],l_uv[faces_new[t][1]],l_uv[faces_new[t][2]]))

                    faces_all.extend(faces_new)

                if not usedBlocks[str(type)]:
                    continue

                curVertexes, curFaces, indices, oldNewTransf, newOldTransf = getUsedVerticesAndTransform(vertexes, faces_all)

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
                customUV = b3dMesh.uv_layers.new()
                customUV.name = "UVmap"

                for k, texpoly in enumerate(b3dMesh.polygons):
                    for j,loop in enumerate(texpoly.loop_indices):
                        uvsMesh = (uvs[k][j][0], 1-uvs[k][j][1])
                        customUV.data[loop].uv = uvsMesh

                #Create Object

                b3dObj = bpy.data.objects.new(objName, b3dMesh)
                b3dObj['block_type'] = type
                b3dObj['level_group'] = levelGroups[lvl-1]
                b3dObj['pos'] = pos
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
                            mat = bpy.data.materials[RESUnpacked.getPrefixedMaterial(int(texnum))]
                            b3dMesh.materials.append(mat)
                            lastIndex = len(b3dMesh.materials)-1

                            for vertArr in texnums[texnum]:
                                newVertArr = getUsedFace(vertArr, oldNewTransf)
                                # op.lock.acquire()
                                assignMaterialByVertices(b3dObj, newVertArr, lastIndex)
                                # op.lock.release()
                    else:
                        for texnum in texnums:
                            mat = bpy.data.materials[RESUnpacked.getPrefixedMaterial(int(texnum))]
                            b3dMesh.materials.append(mat)



            elif (type == 9 or type == 22):

                bounding_sphere = struct.unpack("<4f",file.read(16))
                unknown_sphere = struct.unpack("<4f",file.read(16))
                childCnt = struct.unpack("<i",file.read(4))[0]

                if not usedBlocks[str(type)]:
                    continue

                b3dObj = bpy.data.objects.new(objName, None)
                b3dObj['block_type'] = type
                b3dObj['level_group'] = levelGroups[lvl-1]
                b3dObj['pos'] = str(pos)

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
                b3dObj['level_group'] = levelGroups[lvl-1]
                b3dObj['pos'] = str(pos)

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
                b3dObj['level_group'] = levelGroups[lvl-1]
                b3dObj['pos'] = str(pos)

                b3dObj.parent = context.scene.objects[objString[-2]]
                context.collection.objects.link(b3dObj)
                realName = b3dObj.name
                objString[len(objString)-1] = b3dObj.name

            elif (type == 12):

                bounding_sphere = struct.unpack("<4f",file.read(16))
                unknown_sphere = struct.unpack("<4f",file.read(16))
                unknown1 = struct.unpack("<i",file.read(4))[0]
                unknown2 = struct.unpack("<i",file.read(4))[0]
                cnt = struct.unpack("<i",file.read(4))[0]
                for i in range(cnt):
                    coords.append(struct.unpack("f",file.read(4))[0])

                if not usedBlocks[str(type)]:
                    continue

                b3dObj = bpy.data.objects.new(objName, None)
                b3dObj['block_type'] = type
                b3dObj['level_group'] = levelGroups[lvl-1]
                b3dObj['pos'] = str(pos)

                b3dObj.parent = context.scene.objects[objString[-2]]
                context.collection.objects.link(b3dObj)
                realName = b3dObj.name
                objString[len(objString)-1] = b3dObj.name

            elif (type == 13):

                bounding_sphere = struct.unpack("<4f",file.read(16))
                num = []
                coords = []
                unknown1 = struct.unpack("<i",file.read(4))[0]
                unknown2 = struct.unpack("<i",file.read(4))[0]
                cnt = struct.unpack("<i",file.read(4))[0]
                for i in range(cnt):
                    coords.append(struct.unpack("f",file.read(4))[0])
                if cnt>0:
                    pass

                if not usedBlocks[str(type)]:
                    continue

                b3dObj = bpy.data.objects.new(objName, None)
                b3dObj['block_type'] = type
                b3dObj['level_group'] = levelGroups[lvl-1]
                b3dObj['pos'] = str(pos)

                b3dObj.parent = context.scene.objects[objString[-2]]
                context.collection.objects.link(b3dObj)
                realName = b3dObj.name
                objString[len(objString)-1] = b3dObj.name

            elif (type == 14): #sell_ ?

                bounding_sphere = struct.unpack("<4f",file.read(16))
                unknown_sphere = struct.unpack("<4f",file.read(16))

                some_var = struct.unpack("<i",file.read(4))[0]
                unknown = struct.unpack("<i",file.read(4))[0]
                cnt = struct.unpack("<i",file.read(4))[0]

                for i in range(cnt):
                    coords.append(struct.unpack("f",file.read(4))[0])

                if not usedBlocks[str(type)]:
                    continue

                b3dObj = bpy.data.objects.new(objName, None)
                b3dObj['block_type'] = type
                b3dObj['level_group'] = levelGroups[lvl-1]
                b3dObj['pos'] = str(pos)

                b3dObj.parent = context.scene.objects[objString[-2]]
                context.collection.objects.link(b3dObj)
                realName = b3dObj.name
                objString[len(objString)-1] = b3dObj.name

            elif (type == 15):

                bounding_sphere = struct.unpack("<4f",file.read(16))
                num = []
                coords = []
                unknown1 = struct.unpack("<i",file.read(4))[0]
                unknown2 = struct.unpack("<i",file.read(4))[0]
                cnt = struct.unpack("<i",file.read(4))[0]
                for i in range(cnt):
                    coords.append(struct.unpack("f",file.read(4))[0])
                if cnt>0:
                    pass

                if not usedBlocks[str(type)]:
                    continue

                b3dObj = bpy.data.objects.new(objName, None)
                b3dObj['block_type'] = type
                b3dObj['level_group'] = levelGroups[lvl-1]
                b3dObj['pos'] = str(pos)

                b3dObj.parent = context.scene.objects[objString[-2]]
                context.collection.objects.link(b3dObj)
                realName = b3dObj.name
                objString[len(objString)-1] = b3dObj.name

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
                    coords.append(struct.unpack("f",file.read(4))[0])

                if not usedBlocks[str(type)]:
                    continue

                b3dObj = bpy.data.objects.new(objName, None)
                b3dObj['block_type'] = type
                b3dObj['level_group'] = levelGroups[lvl-1]
                b3dObj['pos'] = str(pos)

                b3dObj.parent = context.scene.objects[objString[-2]]
                context.collection.objects.link(b3dObj)
                realName = b3dObj.name
                objString[len(objString)-1] = b3dObj.name

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
                    coords.append(struct.unpack("f",file.read(4))[0])

                if not usedBlocks[str(type)]:
                    continue

                b3dObj = bpy.data.objects.new(objName, None)
                b3dObj['block_type'] = type
                b3dObj['level_group'] = levelGroups[lvl-1]
                b3dObj['pos'] = str(pos)

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
                b3dObj['level_group'] = levelGroups[lvl-1]
                b3dObj['pos'] = str(pos)
                b3dObj['add_name'] = add_name
                b3dObj['space_name'] = space_name

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
                b3dObj['level_group'] = levelGroups[lvl-1]
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

                cnt = struct.unpack("i",file.read(4))[0]
                for i in range(cnt):
                    struct.unpack("f",file.read(4))
                coords = []
                for i in range (verts_count):
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
                b3dObj['level_group'] = levelGroups[lvl-1]
                b3dObj['pos'] = str(pos)

                b3dObj.parent = context.scene.objects[objString[-2]]
                context.collection.objects.link(b3dObj)
                realName = b3dObj.name
                objString[len(objString)-1] = b3dObj.name

            elif (type == 21): #testkey???
                bounding_sphere = struct.unpack("<4f",file.read(16))


                unknown1 = struct.unpack("<i",file.read(4))[0]
                unknown2 = struct.unpack("<i",file.read(4))[0]
                childCnt = struct.unpack("<i",file.read(4))[0]

                if not usedBlocks[str(type)]:
                    continue

                b3dObj = bpy.data.objects.new(objName, None)
                b3dObj['block_type'] = type
                b3dObj['level_group'] = levelGroups[lvl-1]
                b3dObj['pos'] = str(pos)

                b3dObj.parent = context.scene.objects[objString[-2]]
                context.collection.objects.link(b3dObj)
                realName = b3dObj.name
                objString[len(objString)-1] = b3dObj.name

            elif (type == 23): #colision mesh


                var1 = struct.unpack("<i",file.read(4))[0]
                ctype = struct.unpack("<i",file.read(4))[0]
                var4 = struct.unpack("<i",file.read(4))[0]
                for i in range(var4):
                    struct.unpack("<i",file.read(4))[0]

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
                b3dObj['level_group'] = levelGroups[lvl-1]
                b3dObj['pos'] = str(pos)
                b3dObj['CType'] = ctype

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
                else:
                    z_d = atan2(- m21, m11)
                    x_d = atan2(- m32, var_cy)
                    y_d = 0

                rot_x = ((x_d * 180) / PI)
                rot_y = ((y_d * 180) / PI)
                rot_z = ((z_d * 180) / PI)



                b3dObj = bpy.data.objects.new(objName, None)
                b3dObj['block_type'] = type
                b3dObj.rotation_euler[0] = x_d
                b3dObj.rotation_euler[1] = y_d
                b3dObj.rotation_euler[2] = z_d
                b3dObj.location = sp_pos
                b3dObj['flag'] = flag
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
                b3dObj['level_group'] = levelGroups[lvl-1]
                b3dObj['pos'] = str(pos)

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
                b3dObj['level_group'] = levelGroups[lvl-1]
                b3dObj['pos'] = str(pos)

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
                b3dObj['level_group'] = levelGroups[lvl-1]
                b3dObj['pos'] = str(pos)

                b3dObj.parent = context.scene.objects[objString[-2]]
                context.collection.objects.link(b3dObj)
                realName = b3dObj.name
                objString[len(objString)-1] = b3dObj.name

            elif (type == 28): #face

                coords = []

                bounding_sphere = struct.unpack("<4f",file.read(16))
                unknown_sphere = struct.unpack("<3f",file.read(12))

                num = struct.unpack("<i",file.read(4))[0]

                for i in range(num):

                    formatRaw = struct.unpack("<i",file.read(4))[0]
                    unknown1 = formatRaw & 0xFFFF
                    unknown2 = ((formatRaw & 0xFF00) >> 8) + 1 #ah
                    file.seek(4,1)

                    unknown3 = struct.unpack("<i",file.read(4))[0]
                    materialId = struct.unpack("<i",file.read(4))[0]

                    vert_num = struct.unpack("<i", file.read(4))[0]
                    for k in range(vert_num):
                        l_x = struct.unpack("<f", file.read(4))[0]
                        l_y = struct.unpack("<f", file.read(4))[0]
                        if unknown1 & 0b10:
                            for j in range(unknown2):
                                l_u = struct.unpack("<f", file.read(4))[0]
                                l_v = struct.unpack("<f", file.read(4))[0]

                if not usedBlocks[str(type)]:
                    continue

                b3dMesh = (bpy.data.meshes.new(objName))
                b3dObj = bpy.data.objects.new(objName, b3dMesh)
                b3dObj['block_type'] = type
                b3dObj['level_group'] = levelGroups[lvl-1]
                b3dObj['pos'] = str(pos)

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
                b3dObj['level_group'] = levelGroups[lvl-1]
                b3dObj['pos'] = str(pos)

                b3dObj.parent = context.scene.objects[objString[-2]]
                context.collection.objects.link(b3dObj)
                realName = b3dObj.name
                objString[len(objString)-1] = b3dObj.name

            elif (type == 30):

                b3dMesh = (bpy.data.meshes.new(objName))

                bounding_sphere = struct.unpack("<4f",file.read(16))

                connectedRoomName = readName(file)

                p1 = Vector3F(file)
                p2 = Vector3F(file)

                if not usedBlocks[str(type)]:
                    continue

                l_vertexes = [
                    (p1.x, p1.y, p1.z),
                    (p1.x, p1.y, p2.z),
                    (p2.x, p2.y, p2.z),
                    (p2.x, p2.y, p1.z),
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
                b3dObj['level_group'] = levelGroups[lvl-1]
                b3dObj['pos'] = pos

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
                b3dObj['level_group'] = levelGroups[lvl-1]
                b3dObj['pos'] = str(pos)

                b3dObj.parent = context.scene.objects[objString[-2]]
                context.collection.objects.link(b3dObj)
                realName = b3dObj.name
                objString[len(objString)-1] = b3dObj.name

            elif (type == 33): #lamp

                bounding_sphere = struct.unpack("<4f",file.read(16))

                useLights = struct.unpack("<i",file.read(4))[0]
                b3dObj['light_type'] = struct.unpack("<i",file.read(4))[0]
                flag1 = struct.unpack("<i",file.read(4))[0]

                unknown_vector1 = struct.unpack("<3f",file.read(12))
                unknown_vector2 = struct.unpack("<3f",file.read(12))
                unknown1 = struct.unpack("<f",file.read(4))[0]#global_light_state
                unknown2 = struct.unpack("<f",file.read(4))[0]
                b3dObj['light_radius'] = struct.unpack("<f",file.read(4))[0]
                b3dObj['intensity'] = struct.unpack("<f",file.read(4))[0]
                unknown3 = struct.unpack("<f",file.read(4))[0]
                unknown4 = struct.unpack("<f",file.read(4))[0]
                b3dObj['R'] = struct.unpack("<f",file.read(4))[0]
                b3dObj['G'] = struct.unpack("<f",file.read(4))[0]
                b3dObj['B'] = struct.unpack("<f",file.read(4))[0]
                childCnt = struct.unpack("<i",file.read(4))[0]

                if not usedBlocks[str(type)]:
                    continue

                b3dObj = bpy.data.objects.new(objName, None)
                b3dObj['block_type'] = type
                b3dObj['level_group'] = levelGroups[lvl-1]
                b3dObj['pos'] = str(pos)

                b3dObj.parent = context.scene.objects[objString[-2]]
                context.collection.objects.link(b3dObj)
                realName = b3dObj.name
                objString[len(objString)-1] = b3dObj.name

            elif (type == 34): #lamp
                num = 0

                bounding_sphere = struct.unpack("<4f",file.read(16))
                ff = file.read(4)
                num = struct.unpack("<i",file.read(4))[0]
                for i in range(num):
                    unknown_vector1 = struct.unpack("<3f",file.read(12))
                    unknown1 = struct.unpack("<f",file.read(4))

                if not usedBlocks[str(type)]:
                    continue

                b3dObj = bpy.data.objects.new(objName, None)
                b3dObj['block_type'] = type
                b3dObj['level_group'] = levelGroups[lvl-1]
                b3dObj['pos'] = str(pos)

                b3dObj.parent = context.scene.objects[objString[-2]]
                context.collection.objects.link(b3dObj)
                realName = b3dObj.name
                objString[len(objString)-1] = b3dObj.name

            elif (type == 35): #mesh

                bounding_sphere = struct.unpack("<4f",file.read(16))
                faces_all = []
                faces = []
                formats = []

                mType = struct.unpack("<i",file.read(4))[0]
                texNum = struct.unpack("<i",file.read(4))[0]
                polygonCount = struct.unpack("<i",file.read(4))[0]
                uvs = []
                intencities = []
                vert_uvs = []
                l_uv = uv.copy()

                for i in range(polygonCount):
                    faces = []
                    formatRaw = struct.unpack("<i",file.read(4))[0]
                    format = formatRaw ^ 1
                    formats.append(format)
                    coordsPerVertex = (format >> 8) & 0xF0 #ah
                    triangulateOffset = format & 0b10000000

                    if format & 0b10:
                        coordsPerVertex += 1

                    uunknown = struct.unpack("<fi",file.read(8))
                    texnum = str(struct.unpack("i",file.read(4))[0])

                    vertexCount = struct.unpack("<i",file.read(4))[0]

                    for j in range(vertexCount):
                        face = struct.unpack("<i",file.read(4))[0]
                        faces.append(face)
                        if format & 0b10:
                            for k in range(coordsPerVertex):
                                vert_uvs.append(struct.unpack("<2f",file.read(8)))
                            # uv override
                            if len(vert_uvs) > 0:
                                l_uv[face] = vert_uvs[len(vert_uvs)-1]
                        if format & 0b10000:
                            if format & 0b1:
                                if format & 0b100000:
                                    intens = struct.unpack("<3f",file.read(12))
                                    intencities.append(intens)
                            elif format & 0b100000:
                                intencity = struct.unpack("<f",file.read(4))
                                intens = intencity + (0.0,0.0)
                                # intens = (0.0,) + intencity + (0.0,)
                                # intens = (0.0,0.0) + intencity
                                intencities.append(intens)

                    faces_all.append(faces)
                    uvs.append((l_uv[faces[0]],l_uv[faces[1]],l_uv[faces[2]]))

                if not usedBlocks[str(type)]:
                    continue

                b3dMesh = (bpy.data.meshes.new(objName))
                curVertexes, curFaces, indices, oldNewTransf, newOldTransf = getUsedVerticesAndTransform(vertexes, faces_all)

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
                    # log.debug(normalList)
                    b3dMesh.normals_split_custom_set_from_vertices(normalList)

                # if len(normals) > 0:
                #     for i,idx in enumerate(newIndices):
                #         b3dMesh.vertices[idx].normal = normals[idx]

                customUV = b3dMesh.uv_layers.new()
                customUV.name = "UVmap"
                uvsMesh = []

                for i, texpoly in enumerate(b3dMesh.polygons):
                    for j,loop in enumerate(texpoly.loop_indices):
                        uvsMesh = [uvs[i][j][0],1 - uvs[i][j][1]]
                        customUV.data[loop].uv = uvsMesh

                if op.to_import_textures:
                    mat = bpy.data.materials[RESUnpacked.getPrefixedMaterial(texNum)]
                    b3dMesh.materials.append(mat)


                b3dObj = bpy.data.objects.new(objName, b3dMesh)
                b3dObj.parent = context.scene.objects[objString[-2]]
                b3dObj['MType'] = mType
                b3dObj['texNum'] = texNum
                b3dObj['FType'] = 0
                try:
                    b3dObj['SType'] = b3dObj.parent['SType']
                except:
                    b3dObj['SType'] = 2
                b3dObj['BType'] = 35
                b3dObj['pos'] = str(pos)
                b3dObj['block_type'] = type
                b3dObj['level_group'] = levelGroups[lvl-1]
                realName = b3dObj.name
                # for face in b3dMesh.polygons:
                #     face.use_smooth = True
                context.collection.objects.link(b3dObj) #добавляем в сцену обьект
                objString[len(objString)-1] = b3dObj.name

            elif (type == 36):

                coords25 = []
                vertexes = []
                normals =[]
                uv = []

                bounding_sphere = struct.unpack("<4f",file.read(16))
                name1 = readName(file)
                name2 = readName(file)

                formatRaw = struct.unpack("<i",file.read(4))[0]
                uvCount = formatRaw >> 8
                format = formatRaw & 0xFF

                vertexCount = struct.unpack("<i",file.read(4))[0]
                if format == 0:
                    objString[len(objString)-1] = objString[-2]
                    pass
                else:
                    for i in range(vertexCount):
                        vertexes.append(struct.unpack("<3f",file.read(12)))
                        uv.append(struct.unpack("<2f",file.read(8)))
                        for j in range(uvCount):
                            u = struct.unpack("<f",file.read(4))
                            v = struct.unpack("<f",file.read(4))
                        if format == 1 or format == 2:	#Vertex with normals
                            normals.append(struct.unpack("<3f",file.read(12)))
                        elif format == 3: #отличается от шаблона 010Editor
                            normal = struct.unpack("<f",file.read(4))[0]
                            normal1 = (normal,0.0,0.0)
                            # normal1 = (0.0,normal,0.0)
                            # normal1 = (0.0,0.0,normal)
                            # normal1 = (normal,normal,normal)
                            normals.append(normal1)

                childCnt = struct.unpack("<i",file.read(4))[0]#01 00 00 00 subblocks count

                if not usedBlocks[str(type)]:
                    continue

                b3dObj = bpy.data.objects.new(objName, None)
                b3dObj['block_type'] = type
                b3dObj['level_group'] = levelGroups[lvl-1]
                b3dObj['pos'] = pos

                b3dObj.parent = context.scene.objects[objString[-2]]
                context.collection.objects.link(b3dObj)
                realName = b3dObj.name
                objString[len(objString)-1] = b3dObj.name

            elif (type == 37):

                coords25 = []
                vertexes = []
                normals = []
                uv = []


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
                            vertexes.append(struct.unpack("<3f",file.read(12)))
                            uv.append(struct.unpack("<2f",file.read(8)))
                            for j in range(uvCount):
                                u = struct.unpack("<f",file.read(4))
                                v = struct.unpack("<f",file.read(4))
                            if format == 1 or format == 2:	#Vertex with normals
                                normals.append(struct.unpack("<3f",file.read(12)))
                            elif format == 3: #отличается от шаблона 010Editor
                                normal = struct.unpack("<f",file.read(4))[0]
                                normal1 = (normal,0.0,0.0)
                                # normal1 = (0.0,normal,0.0)
                                # normal1 = (0.0,0.0,normal)
                                # normal1 = (normal,normal,normal)
                                normals.append(normal1)

                childCnt = struct.unpack("<i",file.read(4))[0]#01 00 00 00 subblocks count

                if not usedBlocks[str(type)]:
                    continue

                b3dObj = bpy.data.objects.new(objName, None) #create empty
                b3dObj['block_type'] = type
                b3dObj['level_group'] = levelGroups[lvl-1]
                b3dObj['pos'] = pos
                b3dObj['SType'] = format

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
                b3dObj['level_group'] = levelGroups[lvl-1]
                b3dObj['pos'] = str(pos)

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
                b3dObj['level_group'] = levelGroups[lvl-1]
                b3dObj['pos'] = str(pos)
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
    selectedPolygons = getPolygonsBySelectedVertices()
    for poly in selectedPolygons:
        poly.material_index = matIndex

def getPolygonsBySelectedVertices():
    data = bpy.context.view_layer.objects.active.data
    selectedPolygons = []
    for f in data.polygons:
        s = True
        for v in f.vertices:
            if not data.vertices[v].select:
                s = False
                break
        if s:
            selectedPolygons.append(f)
    return selectedPolygons

def getRESFolder(filepath):
    basename = os.path.basename(filepath)
    basepath = os.path.dirname(filepath)
    return os.path.join(basepath, "{}_unpack".format(basename[:-4]))

def unpackRES(filepath, prefix, saveOnDisk = True):
    log.info("Unpacking {}:".format(filepath))
    # filename, resExtension = os.path.splitext(filepath)
    # basename = os.path.basename(filepath)[:-4]
    # basepath = os.path.dirname(filepath)
    resdir = getRESFolder(filepath)
    curfolder = resdir
    if not os.path.exists(resdir):
        os.mkdir(resdir)

    unpacked = RESUnpack()
    unpacked.prefix = prefix

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
                        names = []
                        for i in range(cnt):
                            name = readCString(resFile)
                            names.append(name)
                        if id == "MATERIALS":
                            if saveOnDisk:
                                with open(binfilePath, "wb") as outFile:
                                    for n in names:
                                        nameSplit = n.split(" ")
                                        name = nameSplit[0]
                                        params = " ".join(nameSplit[1:])
                                        unpacked.materials.append(name)
                                        unpacked.materialParams.append(params)
                                        outFile.write((n+"\n").encode("UTF-8"))
                            else:
                                for n in names:
                                    nameSplit = n.split(" ")
                                    name = nameSplit[0]
                                    params = " ".join(nameSplit[1:])
                                    unpacked.materials.append(name)
                                    unpacked.materialParams.append(params)
                        elif id == "COLORS":
                            if saveOnDisk:
                                with open(binfilePath, "wb") as outFile:
                                    for name in names:
                                        unpacked.colors.append(name)
                                        outFile.write((name+"\n").encode("UTF-8"))
                            else:
                                for name in names:
                                    unpacked.colors.append(name)
                        else:
                            if saveOnDisk:
                                with open(binfilePath, "wb") as outFile:
                                    for name in names:
                                        outFile.write((name+"\n").encode("UTF-8"))
                    else:
                        names = []
                        for i in range(cnt):
                            fullname = readCString(resFile).split(" ")[0]
                            lastpath = fullname.split("\\")
                            name = "\\".join(lastpath[len(lastpath)-1:])
                            names.append(name)
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
                            for name in names:
                                unpacked.textures.append(name)
                        if id == "MASKFILES":
                            for name in names:
                                unpacked.maskfiles.append(name)
                else:
                    log.info("Skip category")
            else:
                break

    return unpacked