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
from .common import ShowMessageBox, Vector3F, createMaterial, parseMaterials, readCString, RESUnpack

import bpy
import mathutils
import os.path
import os
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
        #objname = "Untitled_0x" + str(hex(file.tell()-36))
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

    RESUnpacked = None
    if op.to_unpack_res:
        RESUnpacked = unpackRES(resPath, basename, True)
    else:
        RESUnpacked = unpackRES(resPath, basename, False)

    if op.to_import_textures and not os.path.exists(commonResPath):
        ShowMessageBox("Common.res path is wrong or is not set. Textures weren't imported! Please, set path to Common.res in addon preferences.",
        "COMMON.res wrong path",
        "ERROR")
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
        txrFolder = os.path.join(texturePath, "txr")
        folder_content = os.listdir(txrFolder)
        reTXR = re.compile(r'\.txr')
        for path in folder_content:
            fullpath = os.path.join(txrFolder, path)
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

        # if (search_tex_names == True):
        #     if (material_textures[i][0] == "("):
        #         PImg = (material_textures[i])
        #     elif (material_textures[i][0] == "["):
        #         PImg = ("(255, 255, 255)")
        #     else:
        #         PImg = (filepath.rsplit('\\',1)[0] + "\\" + material_textures[i] + "." + textures_format)
        # else:
        #     PImg = (filepath.rsplit('\\',1)[0] +'\\txr\\' +SNImg + "." + textures_format)


        # if (search_tex_names == True):
        #     if os.path.isfile(PImg):
        #         img = bpy.data.images.load(PImg)
        #     else:
        #         img = bpy.data.images.new(SNImg,1,1)
        #         if (material_textures[i][0] == "("):
        #             PImg = (material_textures[i])
        #             R = (float((PImg[1:-1].split(", "))[0])) / 255
        #             G = (float((PImg[1:-1].split(", "))[1])) / 255
        #             B = (float((PImg[1:-1].split(", "))[2])) / 255
        #             img.pixels = (B, G, R, 1.0)
        #             img.filepath_raw = (filepath.rsplit('\\',1)[0] + tex_path + "\\" + SNImg + "." + textures_format)
        #             img.file_format = textures_format.upper()
        #             img.save()
        # else:
        #     if os.path.isfile(PImg):
        #         img = bpy.data.images.load(PImg)
        #     else:
        #         PImg = (filepath.rsplit('\\',1)[0] +'\\txr\\' +SNImg[4:]+'.tga') #полный путь
        #         if os.path.isfile(PImg):
        #             img = bpy.data.images.load(PImg)
        #         else:
        #             img = bpy.data.images.new(SNImg,1,1)

            #if (search_tex_names == False):
            #	PImg = (filepath.rsplit('\\',1)[0] +'\\txr\\' +SNImg+'.tga') #полный путь #####################################################################
            #PImg = (filepath.rsplit('\\',1)[0] +'\\txr\\' +SNImg[4:]+'.tga')
            #?
            #if os.path.isfile(PImg):
            #	img = bpy.data.images.load(PImg)
            #else:
            #	img = bpy.data.images.new(SNImg,1,1)#bpy.data.images.new(SNImg,1,1)
        # Imgs.append(img)


    #     tex = bpy.data.textures.new(SNImg,'IMAGE')
    #     tex.use_preview_alpha = True
    #     tex.image = img #bpy.data.images[i]
    #     # todo: replace with solution:
    #     # https://blender.stackexchange.com/questions/118646/add-a-texture-to-an-object-using-python-and-blender-2-8
    #     # mat = bpy.data.materials.new(SNImg)
    #     # mat.texture_slots.add()
    #     # mat.texture_slots[0].uv_layer = 'UVmap'
    #     # mat.texture_slots[0].texture = tex
    #     # mat.texture_slots[0].use_map_alpha = True
    #     # math.append(mat)

    file.seek(4,1) #Skip Begin_Chunks(111)

    # Processing vertices

    ex = 0
    i = 0
    lvl = 0
    cnt = 0
    coords25 = []
    coords23 = []
    vertexes = []
    normals = []
    format = 0
    #
    b3dObj = 0
    uv = []

    b3dName = os.path.basename(op.properties.filepath)

    b3dObj = bpy.data.objects.new(b3dName,None)
    b3dObj['block_type'] = 0
    context.collection.objects.link(b3dObj) # root object

    objString = [b3dName]

    while ex!=ChunkType.END_CHUNKS:

        ex = openclose(file)
        if ex == ChunkType.END_CHUNK:
            del objString[-1]
            lvl-=1
        elif ex == ChunkType.END_CHUNKS:
            file.close()
            break
        elif ex == ChunkType.GROUP_CHUNK:
            continue
        elif ex == ChunkType.BEGIN_CHUNK:
            lvl+=1
            onlyName = readName(file)
            type = 	struct.unpack("<i",file.read(4))[0]
            # objName = "{}_{}".format(str(type).zfill(2), onlyName)
            objName = onlyName
            realName = onlyName
            # log.info("Importing block #{}: {}".format(type, objName))
            if (type == 0): # Empty Block
                bounding_sphere = struct.unpack("<4f",file.read(16))
                objString.append(b3dName)
                ff = file.seek(28,1)

            elif (type == 1):
                b3dObj = bpy.data.objects.new(objName, None)
                b3dObj['block_type'] = type

                b3dObj.parent = context.scene.objects[objString[-1]]
                context.collection.objects.link(b3dObj)
                realName = b3dObj.name
                objString.append(b3dObj.name)

                b3dObj['2 name'] = file.read(32).decode("cp1251").rstrip('\0') #?
                b3dObj['3 name'] = file.read(32).decode("cp1251").rstrip('\0') #?
                b3dObj['pos'] = str(file.tell())

            elif (type == 2):	#контейнер хз
                b3dObj = bpy.data.objects.new(objName, None)
                b3dObj['block_type'] = type
                b3dObj['pos'] = str(file.tell())

                b3dObj.parent = context.scene.objects[objString[-1]]
                context.collection.objects.link(b3dObj)
                realName = b3dObj.name
                objString.append(b3dObj.name)

                bounding_sphere = struct.unpack("<4f",file.read(16))

                unknown_sphere = struct.unpack("<4f",file.read(16))

                childCnt = struct.unpack("<i",file.read(4))

            elif (type == 3):	#
                b3dObj = bpy.data.objects.new(objName, None)
                b3dObj['block_type'] = type
                b3dObj['pos'] = str(file.tell())

                b3dObj.parent = context.scene.objects[objString[-1]]
                context.collection.objects.link(b3dObj)
                realName = b3dObj.name
                objString.append(b3dObj.name)

                bounding_sphere = struct.unpack("<4f",file.read(16))
                childCnt = struct.unpack("<i",file.read(4))

            elif (type == 4):	#похоже на контейнер 05 совмещенный с 12
                cnt+=1
                b3dObj = bpy.data.objects.new(objName, None)
                b3dObj['block_type'] = type
                b3dObj['pos'] = str(file.tell())

                b3dObj.parent = context.scene.objects[objString[-1]]
                context.collection.objects.link(b3dObj)
                realName = b3dObj.name

                objString.append(b3dObj.name)

                bounding_sphere = struct.unpack("<4f",file.read(16))

                name1 = readName(file)
                name2 = readName(file)

                childCnt = struct.unpack("<i",file.read(4))[0]

            elif (type==5): #общий контейнер

                pos = file.tell()

                b3dObj = bpy.data.objects.new(objName, None) #create empty

                b3dObj['block_type'] = type
                b3dObj['pos'] = pos

                bounding_sphere = struct.unpack("<4f",file.read(16))

                name = readName(file)

                b3dObj.parent = context.scene.objects[objString[-1]]
                context.collection.objects.link(b3dObj)
                realName = b3dObj.name
                objString.append(b3dObj.name)
                b3dObj['child_count'] = struct.unpack("<i",file.read(4))[0]

            elif (type == 6):
                vertexes = []
                uv = []

                cnt+=1
                b3dObj = bpy.data.objects.new(objName, None)
                b3dObj['block_type'] = type
                b3dObj['pos'] = str(file.tell())

                b3dObj.parent = context.scene.objects[objString[-1]]
                context.collection.objects.link(b3dObj)
                realName = b3dObj.name

                objString.append(b3dObj.name)

                bounding_sphere = struct.unpack("<4f",file.read(16))
                name1 = readName(file)
                name2 = readName(file)
                vertexCount = struct.unpack("<i",file.read(4))[0]
                for i in range (vertexCount):
                    vertexes.append(struct.unpack("<3f",file.read(12)))
                    uv.append(struct.unpack("<2f",file.read(8)))

                childCnt = struct.unpack("<i",file.read(4))[0]

            elif (type == 7):	#25? xyzuv TailLight? похоже на "хвост" движения	mesh
                format = 0
                coords25 = []
                vertexes = []
                uv = []
                cnt+=1
                b3dObj = bpy.data.objects.new(objName, None)
                b3dObj['block_type'] = type

                b3dObj.parent = context.scene.objects[objString[-1]]

                bounding_sphere = struct.unpack("<4f",file.read(16))
                groupName = str(file.read(32)) #0-0

                vertexCount = struct.unpack("<i",file.read(4))[0]
                for i in range(vertexCount):
                    vertexes.append(struct.unpack("<3f",file.read(12)))
                    uv.append(struct.unpack("<2f",file.read(8)))

                childCnt = struct.unpack("<i",file.read(4))[0]

                context.collection.objects.link(b3dObj)
                realName = b3dObj.name
                objString.append(b3dObj.name)

            elif (type == 8):	#тоже фейсы		face
                faces = []
                faces_all = []
                uvs = []
                texnums = {}
                cnt+=1
                b3dObj
                b3dMesh = bpy.data.meshes.new(objName)

                pos = str(file.tell())

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
                        faces.append(struct.unpack("<i",file.read(4))[0])
                        if format & 0b10:
                            for k in range(coordsPerVertex):
                                u = struct.unpack("<f",file.read(4))[0]
                                v = struct.unpack("<f",file.read(4))[0]
                        if format & 0b10000:
                            if format & 0b1:
                                if format & 0b100000:
                                    normals1 = struct.unpack("<3f",file.read(12))
                            elif format & 0b100000:
                                intencity = struct.unpack("<f",file.read(4))[0]

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
                            faces_new.append([faces[t],faces[t+1],faces[t+2]])

                        uvs.append((uv[faces_new[t][0]],uv[faces_new[t][1]],uv[faces_new[t][2]]))

                    faces_all.extend(faces_new)

                Ev = threading.Event()
                Tr = threading.Thread(target=b3dMesh.from_pydata, args = (vertexes,[],faces_all))
                Tr.start()
                Ev.set()
                Tr.join()

                #Setup UV
                customUV = b3dMesh.uv_layers.new()
                customUV.name = "UVmap"

                for k, texpoly in enumerate(b3dMesh.polygons):
                    for j,loop in enumerate(texpoly.loop_indices):
                        uvsMesh = [uvs[k][j][0],1 - uvs[k][j][1]]
                        customUV.data[loop].uv = uvsMesh

                #Create Object
                b3dObj = bpy.data.objects.new(objName, b3dMesh)
                b3dObj['block_type'] = type
                b3dObj['pos'] = pos
                b3dObj.parent = context.scene.objects[objString[-1]]
                context.collection.objects.link(b3dObj)
                realName = b3dObj.name

                if op.to_import_textures:
                    #For assignMaterialByVertices just-in-case
                    bpy.ops.object.mode_set(mode = 'OBJECT')
                    #Set appropriate meaterials
                    if len(texnums.keys()) > 1:
                        for texnum in texnums:
                            mat = bpy.data.materials[RESUnpacked.getPrefixedMaterial(int(texnum))]
                            b3dMesh.materials.append(mat)
                            lastIndex = len(b3dMesh.materials)-1

                            for vertArr in texnums[texnum]:
                                assignMaterialByVertices(b3dObj, vertArr, lastIndex)
                    else:
                        for texnum in texnums:
                            mat = bpy.data.materials[RESUnpacked.getPrefixedMaterial(int(texnum))]
                            b3dMesh.materials.append(mat)

                objString.append(b3dObj.name)

            elif (type == 9 or type == 22):
                cnt+=1
                b3dObj = bpy.data.objects.new(objName, None)
                b3dObj['block_type'] = type
                b3dObj['pos'] = str(file.tell())

                b3dObj.parent = context.scene.objects[objString[-1]]
                context.collection.objects.link(b3dObj)
                realName = b3dObj.name
                objString.append(b3dObj.name)

                bounding_sphere = struct.unpack("<4f",file.read(16))
                unknown_sphere = struct.unpack("<4f",file.read(16))
                childCnt = struct.unpack("<i",file.read(4))[0]

            elif (type == 10): #контейнер, хз о чем LOD

                b3dObj = bpy.data.objects.new(objName, None)
                b3dObj['block_type'] = type
                b3dObj['pos'] = str(file.tell())

                b3dObj.parent = context.scene.objects[objString[-1]]
                context.collection.objects.link(b3dObj)
                realName = b3dObj.name
                objString.append(b3dObj.name)

                bounding_sphere = struct.unpack("<4f",file.read(16))
                unknown_sphere = struct.unpack("<4f",file.read(16))
                childCnt = struct.unpack("<i",file.read(4))[0]

            elif (type == 11):
                cnt+=1
                b3dObj = bpy.data.objects.new(objName, None)
                b3dObj['block_type'] = type
                b3dObj['pos'] = str(file.tell())

                b3dObj.parent = context.scene.objects[objString[-1]]
                context.collection.objects.link(b3dObj)
                realName = b3dObj.name
                objString.append(b3dObj.name)

                bounding_sphere = struct.unpack("<4f",file.read(16))
                unknown_sphere = struct.unpack("<4f",file.read(16))
                childCnt = struct.unpack("<i",file.read(4))[0]

            elif (type == 12):
                cnt+=1
                b3dObj = bpy.data.objects.new(objName, None)
                b3dObj['block_type'] = type
                b3dObj['pos'] = str(file.tell())

                b3dObj.parent = context.scene.objects[objString[-1]]
                context.collection.objects.link(b3dObj)
                realName = b3dObj.name
                objString.append(b3dObj.name)

                bounding_sphere = struct.unpack("<4f",file.read(16))
                unknown_sphere = struct.unpack("<4f",file.read(16))
                unknown1 = struct.unpack("<i",file.read(4))[0]
                unknown2 = struct.unpack("<i",file.read(4))[0]
                cnt = struct.unpack("<i",file.read(4))[0]
                for i in range(cnt):
                    coords.append(struct.unpack("f",file.read(4))[0])

            elif (type == 13):
                cnt+=1
                b3dObj = bpy.data.objects.new(objName, None)
                b3dObj['block_type'] = type
                b3dObj['pos'] = str(file.tell())

                b3dObj.parent = context.scene.objects[objString[-1]]
                context.collection.objects.link(b3dObj)
                realName = b3dObj.name
                objString.append(b3dObj.name)


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

            elif (type == 14): #sell_ ?

                b3dObj = bpy.data.objects.new(objName, None)
                b3dObj['block_type'] = type
                b3dObj['pos'] = str(file.tell())

                b3dObj.parent = context.scene.objects[objString[-1]]
                context.collection.objects.link(b3dObj)
                realName = b3dObj.name
                objString.append(b3dObj.name)

                bounding_sphere = struct.unpack("<4f",file.read(16))
                unknown_sphere = struct.unpack("<4f",file.read(16))

                some_var = struct.unpack("<i",file.read(4))[0]
                unknown = struct.unpack("<i",file.read(4))[0]
                cnt = struct.unpack("<i",file.read(4))[0]

                for i in range(cnt):
                    coords.append(struct.unpack("f",file.read(4))[0])

            elif (type == 15):

                b3dObj = bpy.data.objects.new(objName, None)
                b3dObj['block_type'] = type
                b3dObj['pos'] = str(file.tell())

                b3dObj.parent = context.scene.objects[objString[-1]]
                context.collection.objects.link(b3dObj)
                realName = b3dObj.name
                objString.append(b3dObj.name)


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

            elif (type == 16):
                cnt+=1
                b3dObj = bpy.data.objects.new(objName, None)
                b3dObj['block_type'] = type
                b3dObj['pos'] = str(file.tell())

                b3dObj.parent = context.scene.objects[objString[-1]]
                context.collection.objects.link(b3dObj)
                realName = b3dObj.name
                objString.append(b3dObj.name)

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

            elif (type == 17):
                cnt+=1
                b3dObj = bpy.data.objects.new(objName, None)
                b3dObj['block_type'] = type
                b3dObj['pos'] = str(file.tell())

                b3dObj.parent = context.scene.objects[objString[-1]]
                context.collection.objects.link(b3dObj)
                realName = b3dObj.name
                objString.append(b3dObj.name)

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

            elif (type == 18):	#контейнер "применить к"

                bounding_sphere = struct.unpack("<4f",file.read(16))

                b3dObj = bpy.data.objects.new(objName, None)
                b3dObj['block_type'] = type
                b3dObj['pos'] = str(file.tell())
                b3dObj['space_name'] = file.read(32).decode("utf-8").rstrip('\0')
                b3dObj['add_name'] = file.read(32).decode("utf-8").rstrip('\0')

                b3dObj.parent = context.scene.objects[objString[-1]]
                context.collection.objects.link(b3dObj)
                realName = b3dObj.name
                objString.append(b3dObj.name)


            elif (type == 19):
                b3dObj = bpy.data.objects.new(objName, None)
                b3dObj['block_type'] = type
                b3dObj['pos'] = str(file.tell())

                b3dObj.parent = context.scene.objects[objString[-1]]
                context.collection.objects.link(b3dObj)
                realName = b3dObj.name
                objString.append(b3dObj.name)

                childCnt = struct.unpack("i",file.read(4))[0]

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
                curveData = bpy.data.curves.new('curve', type='CURVE')

                curveData.dimensions = '3D'
                curveData.resolution_u = 2

                # map coords to spline
                polyline = curveData.splines.new('POLY')
                polyline.points.add(len(coords)-1)
                for i, coord in enumerate(coords):
                    x,y,z = coord
                    polyline.points[i].co = (x, y, z, 1)

                # create Object
                b3dObj = bpy.data.objects.new(objName, curveData)
                curveData.bevel_depth = 0.01

                b3dObj.location = (0,0,0)
                b3dObj['block_type'] = type
                b3dObj['pos'] = str(file.tell())

                b3dObj.parent = context.scene.objects[objString[-1]]
                context.collection.objects.link(b3dObj)
                realName = b3dObj.name
                objString.append(b3dObj.name)

            elif (type == 21): #testkey???
                bounding_sphere = struct.unpack("<4f",file.read(16))

                b3dObj = bpy.data.objects.new(objName, None)
                b3dObj['block_type'] = type
                b3dObj['pos'] = str(file.tell())

                b3dObj.parent = context.scene.objects[objString[-1]]
                context.collection.objects.link(b3dObj)
                realName = b3dObj.name
                objString.append(b3dObj.name)

                unknown1 = struct.unpack("<i",file.read(4))[0]
                unknown2 = struct.unpack("<i",file.read(4))[0]
                childCnt = struct.unpack("<i",file.read(4))[0]


            elif (type == 23): #colision mesh

                cnt+=1
                b3dMesh = (bpy.data.meshes.new(objName))
                b3dObj = bpy.data.objects.new(objName, b3dMesh)
                b3dObj['block_type'] = type
                b3dObj['pos'] = str(file.tell())

                b3dObj.parent = context.scene.objects[objString[-1]]
                context.collection.objects.link(b3dObj)
                realName = b3dObj.name
                objString.append(b3dObj.name)


                var1 = struct.unpack("<i",file.read(4))[0]
                b3dObj['CType'] = struct.unpack("<i",file.read(4))[0]
                var4 = struct.unpack("<i",file.read(4))[0]
                for i in range(var4):
                    struct.unpack("<i",file.read(4))[0]

                vertsBlockNum = struct.unpack("<i",file.read(4))[0]
                num = 0
                faces = []
                vertexes = []
                for i in range(vertsBlockNum):
                    vertsInBlock = struct.unpack("<i",file.read(4))[0]

                    if (vertsInBlock == 3):
                        faces.append([num+1,num+2,num+0])
                        num+=3
                    elif(vertsInBlock ==4):
                        faces.append([num+1,num+2,num+0,num+2,num+3,num+1])
                        num+=4

                    for j in range(vertsInBlock):
                        vertexes.append(struct.unpack("<3f",file.read(12)))

                b3dMesh.from_pydata(vertexes,[],faces)

            elif (type == 24): #настройки положения обьекта
                cnt+=1

                #qu = quat(file).v
                #objString.append(context.scene.objects[0].name)
                #file.seek(20,1)

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



                #bpy.ops.mesh.primitive_ico_sphere_add(size=0.05, calc_uvs=True, location=sp_pos)
                b3dObj = bpy.data.objects.new(objName, None)
                #b3dObj = bpy.context.selected_objects[0]
                #b3dObj.name = objName
                b3dObj['block_type'] = type
                b3dObj.rotation_euler[0] = x_d
                b3dObj.rotation_euler[1] = y_d
                b3dObj.rotation_euler[2] = z_d
                b3dObj.location = sp_pos

                #b3dObj['rotation_euler0'] = rot_x
                #b3dObj['rotation_euler1'] = rot_y
                #b3dObj['rotation_euler2'] = rot_z

                #bpy.ops.object.select_all(action='DESELECT')
                flag = struct.unpack("<i",file.read(4))[0]
                b3dObj['flag'] = flag

                childCnt = struct.unpack("<i", file.read(4))[0]

                b3dObj.parent = context.scene.objects[objString[-1]]
                context.collection.objects.link(b3dObj)
                realName = b3dObj.name
                # objString.append(context.scene.objects[0].name)
                objString.append(b3dObj.name)

            elif (type == 25): #copSiren????/ контейнер

                b3dObj = bpy.data.objects.new(objName, None)
                b3dObj['block_type'] = type
                b3dObj['pos'] = str(file.tell())

                b3dObj.parent = context.scene.objects[objString[-1]]
                context.collection.objects.link(b3dObj)
                realName = b3dObj.name
                # objString.append(context.scene.objects[0].name)
                objString.append(b3dObj.name)

                unknown1 = struct.unpack("<3i",file.read(12))

                name = readName(file)
                unknown_sphere1 = struct.unpack("<3f",file.read(12))
                unknown_sphere2 = struct.unpack("<3f",file.read(12))
                unknown2 = struct.unpack("<5f",file.read(20))

            elif (type == 26):

                b3dObj = bpy.data.objects.new(objName, None)
                b3dObj['block_type'] = type
                b3dObj['pos'] = str(file.tell())

                b3dObj.parent = context.scene.objects[objString[-1]]
                context.collection.objects.link(b3dObj)
                realName = b3dObj.name
                # objString.append(context.scene.objects[0].name)
                objString.append(b3dObj.name)

                bounding_sphere = struct.unpack("<4f",file.read(16))

                unknown_sphere1 = struct.unpack("<3f",file.read(12))
                unknown_sphere2 = struct.unpack("<3f",file.read(12))
                unknown_sphere3 = struct.unpack("<3f",file.read(12))

                childCnt = struct.unpack("<i",file.read(4))

            elif (type == 27):

                b3dObj = bpy.data.objects.new(objName, None)
                b3dObj['block_type'] = type
                b3dObj['pos'] = str(file.tell())

                b3dObj.parent = context.scene.objects[objString[-1]]
                context.collection.objects.link(b3dObj)
                realName = b3dObj.name
                # objString.append(context.scene.objects[0].name)
                objString.append(b3dObj.name)

                bounding_sphere = struct.unpack("<4f",file.read(16))
                flag1 = struct.unpack("<i",file.read(4))
                unknown_sphere = struct.unpack("<3f",file.read(12))

                materialId = struct.unpack("<i",file.read(4))

            elif (type == 28): #face

                cnt+=1
                b3dMesh = (bpy.data.meshes.new(objName))
                b3dObj = bpy.data.objects.new(objName, b3dMesh)
                b3dObj['block_type'] = type
                b3dObj['pos'] = str(file.tell())


                b3dObj.parent = context.scene.objects[objString[-1]]

                #b3dObj.hide_viewport = True
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

                        # if (type == 0) :
                        #     file.seek(8, 1) #x,y
                        # if type==256 or type == 1 or type == 2:
                        #     file.seek(16,1) #x,y,u,v
                        # if type == -256:
                        #     file.seek(8, 1) #x,y

                #for i in range(num):
                #	num1 = struct.unpack("i",file.read(4))[0]
                #	coords.extend(struct.unpack("f3i",file.read(16)))
                #	if (num1 == 2):
                #		coords.extend(struct.unpack('{}f'.format(coords[-1]*4),file.read(4*4*coords[-1])))

                # if num == 1:
                    # coords.extend(struct.unpack("if3i",file.read(20)))
                    # if (coords[0]>1):
                        # for i in range(coords[4]):
                            # coords.extend(struct.unpack("<4f",file.read(16)))
                    # else:
                        # coords.extend(struct.unpack("<8f",file.read(32)))

                # elif num ==2:
                    # coords.extend(struct.unpack("if3i",file.read(20)))
                    # for i in range(num*2):
                        # coords.extend(struct.unpack("<7f",file.read(28)))
                    # coords.extend(struct.unpack("<f",file.read(4)))

                # elif ((num == 10) or(num == 6)) : #db1
                    # for i in range(num):
                        # coords.extend(struct.unpack("if3i",file.read(20)))
                        # num1 = coords[-1]
                        # for i in range (num1):
                            # coords.append(struct.unpack("<2f",file.read(8)))
                # #b3dMesh.from_pydata(vertexes,[],faces)

                context.collection.objects.link(b3dObj) #добавляем в сцену обьект
                realName = b3dObj.name
                # objString.append(context.scene.objects[0].name)
                objString.append(b3dObj.name)

            elif (type == 29):
                #cnt+=1
                #b3dObj = bpy.data.objects.new(objName, None)
                #b3dObj['block_type'] = 29
                #b3dObj['pos'] = str(file.tell())
                #b3dObj.parent = context.scene.objects[objString[-1]]
                ##b3dObj.hide_viewport = True
                #context.collection.objects.link(b3dObj)
                #objString.append(context.scene.objects[0].name)

                #qu = quat(file).v
                ##num0 = struct.unpack("<i",file.read(4))[0]
                ##struct.unpack("<i",file.read(4))[0]
                ##struct.unpack("<7f",file.read(28))
                ##if num0 == 4:
                ##	struct.unpack("<f",file.read(4))[0]
                ##elif num0 == 3:
                ##	pass
                ##struct.unpack("<i",file.read(4))[0]

                ##дб1


                ##дб2
                ##struct.unpack("<i",file.read(4))[0]
                ##struct.unpack("<i",file.read(4))[0]
                ##struct.unpack("<fff",file.read(12))
                ##struct.unpack("<fff",file.read(12))
                ##struct.unpack("<i",file.read(4))[0]

                ##struct.unpack("<i",file.read(4))[0]

                #num0 = struct.unpack("<i",file.read(4))[0]
                #num1 = struct.unpack("<i",file.read(4))[0]
                #struct.unpack("<fff",file.read(12))
                #struct.unpack("<fff",file.read(12))

                #struct.unpack("<f",file.read(4))[0]

                #if (num0 != 3):
                #	struct.unpack("<f",file.read(4))[0]

                #struct.unpack("<i",file.read(4))[0]

                b3dObj = bpy.data.objects.new(objName, None)
                b3dObj['block_type'] = type
                b3dObj['pos'] = str(file.tell())

                b3dObj.parent = context.scene.objects[objString[-1]]
                context.collection.objects.link(b3dObj)
                realName = b3dObj.name
                # objString.append(context.scene.objects[0].name)
                objString.append(b3dObj.name)

                bounding_sphere = struct.unpack("<4f",file.read(16))
                num0 = struct.unpack("<i",file.read(4))[0]
                num1 = struct.unpack("<i",file.read(4))[0]

                unknown_sphere = struct.unpack("<4f",file.read(16))

                if num0 > 0:
                    f = struct.unpack("<"+num0+"f",file.read(4*num0))

                childCnt = struct.unpack("<i",file.read(4))[0]


            elif (type == 30):
                cnt+=1
                pos = str(file.tell())

                b3dMesh = (bpy.data.meshes.new(objName))

                bounding_sphere = struct.unpack("<4f",file.read(16))

                connectedRoomName = readName(file)

                p1 = Vector3F(file)
                p2 = Vector3F(file)

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
                b3dObj['pos'] = pos

                b3dObj.parent = context.scene.objects[objString[-1]]
                context.collection.objects.link(b3dObj)
                realName = b3dObj.name
                objString.append(b3dObj.name)

            elif (type == 31):
                b3dObj = bpy.data.objects.new(objName, None)
                b3dObj['block_type'] = type
                b3dObj['pos'] = str(file.tell())

                b3dObj.parent = context.scene.objects[objString[-1]]
                context.collection.objects.link(b3dObj)
                realName = b3dObj.name
                objString.append(b3dObj.name)

                bounding_sphere = struct.unpack("<4f",file.read(16))

                num = struct.unpack("<i",file.read(4))[0]
                unknown_sphere = struct.unpack("<4f",file.read(16))
                num2 = struct.unpack("<i",file.read(4))[0]
                unknown = struct.unpack("<3f",file.read(12))
                for i in range(num):
                    struct.unpack("<fi",file.read(8))


            elif (type == 33): #lamp

                b3dObj = bpy.data.objects.new(objName, None)
                b3dObj['block_type'] = type
                b3dObj['pos'] = str(file.tell())

                b3dObj.parent = context.scene.objects[objString[-1]]
                context.collection.objects.link(b3dObj)
                realName = b3dObj.name
                objString.append(b3dObj.name)
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

            elif (type == 34): #lamp
                num = 0
                b3dObj = bpy.data.objects.new(objName, None)
                b3dObj['block_type'] = type
                b3dObj['pos'] = str(file.tell())

                b3dObj.parent = context.scene.objects[objString[-1]]
                #b3dObj.hide_viewport = True
                context.collection.objects.link(b3dObj)
                realName = b3dObj.name
                # objString.append(context.scene.objects[0].name)
                objString.append(b3dObj.name)

                bounding_sphere = struct.unpack("<4f",file.read(16))
                ff = file.read(4)
                num = struct.unpack("<i",file.read(4))[0]
                for i in range(num):
                    unknown_vector1 = struct.unpack("<3f",file.read(12))
                    unknown1 = struct.unpack("<f",file.read(4))

            elif (type == 35): #mesh

                b3dMesh = (bpy.data.meshes.new(objName))
                b3dObj = bpy.data.objects.new(objName, b3dMesh)
                #b3dObj['block_type'] = 35


                b3dObj.parent = context.scene.objects[objString[-1]]

                #b3dObj.hide_viewport = True

                bounding_sphere = struct.unpack("<4f",file.read(16))
                # qu = quat(file).v
                faces_all = []
                faces = []

                mType = struct.unpack("<i",file.read(4))[0]
                texNum = struct.unpack("<i",file.read(4))[0]
                polygonCount = struct.unpack("<i",file.read(4))[0]
                uvs = []

                for i in range(polygonCount):
                    faces = []
                    formatRaw = struct.unpack("<i",file.read(4))[0]
                    format = formatRaw ^ 1
                    coordsPerVertex = (format >> 8) & 0xF0 #ah
                    triangulateOffset = format & 0b10000000

                    if format & 0b10:
                        coordsPerVertex += 1

                    uunknown = struct.unpack("<fi",file.read(8))
                    texnum = str(struct.unpack("i",file.read(4))[0])

                    vertexCount = struct.unpack("<i",file.read(4))[0]

                    for j in range(vertexCount):
                        faces.append(struct.unpack("<i",file.read(4))[0])
                        if format & 0b10:
                            for k in range(coordsPerVertex):
                                u = struct.unpack("<f",file.read(4))[0]
                                v = struct.unpack("<f",file.read(4))[0]
                        if format & 0b10000:
                            if format & 0b1:
                                if format & 0b100000:
                                    normals1 = struct.unpack("<3f",file.read(12))
                            elif format & 0b100000:
                                intencity = struct.unpack("<f",file.read(4))[0]

                    faces_all.append(faces)
                    uvs.append((uv[faces[0]],uv[faces[1]],uv[faces[2]]))


                ########

                ########
                # faces1 = []

                # if mType<3:
                #     for i in range(polygonCount):
                #         faces1 = []
                #         num1=[]
                #         #coords23.append(struct.unpack("<i",file.read(4)))
                #         num1.append(struct.unpack("<i",file.read(4))[0])
                #         if (num1[0] == 50):
                #             num1.extend(struct.unpack("<f4i5fi5fi5f",file.read(88)))
                #             coords23.append(num1)
                #             faces1 = (coords23[i][5],coords23[i][11],coords23[i][17])

                #         elif (num1[0] == 49):
                #             num1.extend(struct.unpack("<f3iififif",file.read(40)))
                #             coords23.append(num1)
                #             faces1 = (coords23[i][5],coords23[i][7],coords23[i][9])
                #         elif((num1[0] == 1) or (num1[0] == 0)):

                #             num1.extend(struct.unpack("<f6i",file.read(28)))
                #             coords23.append(num1)
                #             faces1 = coords23[i][5:8]
                #             # faces1 = coords23[i][4:7]
                #             # faces.append(faces1)
                #         elif ((num1[0] == 2) or (num1[0] == 3)):
                #             num1.extend(struct.unpack("<fiiiiffiffiff",file.read(52)))
                #             coords23.append(num1)
                #             faces1=(coords23[i][5],coords23[i][8],coords23[i][11])
                #         else:
                #             num1.extend(struct.unpack("<f3iifffifffifff",file.read(64)))
                #             coords23.append(num1)
                #             faces1 = (coords23[i][5],coords23[i][9],coords23[i][13])
                #         #faces1 = faces1[0]
                #         faces.append(faces1)
                #         #faces1 = faces1[0]
                #         #uvs.append((coords25[faces1[0]][3:5] , coords25[faces1[1]][3:5] , coords25[faces1[2]][3:5]))
                #         uvs.append((uv[faces1[0]],uv[faces1[1]],uv[faces1[2]]))

                # elif mType == 3:
                #     for i in range(polygonCount):
                #         #coords23.append([struct.unpack("<i",file.read(4))[0]])
                #         #file.read(4)
                #         coords23.append(struct.unpack("<if6i",file.read(32)))
                #         faces1 = coords23[i][5:8]
                #         faces.append(faces1)
                #         uvs.append((uv[faces1[0]],uv[faces1[1]],uv[faces1[2]]))

                Ev = threading.Event()
                Tr = threading.Thread(target=b3dMesh.from_pydata, args = (vertexes,[],faces_all))
                Tr.start()
                Ev.set()
                Tr.join()

                #if ((format == 2) or (format == 515) or (format == 514) or (format == 258)):
                    #i = 0
                    #for i,vert in enumerate(b3dMesh.vertices):
                        #vert.normal = normals[i]

                customUV = b3dMesh.uv_layers.new()
                customUV.name = "UVmap"
                uvsMesh = []

                #uvMain = createTextureLayer("default", b3dMesh, uvs)

                for i, texpoly in enumerate(b3dMesh.polygons):
                    for j,loop in enumerate(texpoly.loop_indices):
                        uvsMesh = [uvs[i][j][0],1 - uvs[i][j][1]]
                        customUV.data[loop].uv = uvsMesh

                if op.to_import_textures:
                    mat = bpy.data.materials[RESUnpacked.getPrefixedMaterial(texNum)]
                    b3dMesh.materials.append(mat)

                context.collection.objects.link(b3dObj) #добавляем в сцену обьект
                realName = b3dObj.name
                b3dObj['MType'] = mType
                b3dObj['texNum'] = texNum
                b3dObj['FType'] = 0
                try:
                    b3dObj['SType'] = b3dObj.parent['SType']
                except:
                    b3dObj['SType'] = 2
                b3dObj['BType'] = 35
                b3dObj['pos'] = str(file.tell())
                b3dObj['block_type'] = type
                for face in b3dMesh.polygons:
                    face.use_smooth = True
                objString.append(b3dObj.name)

            elif (type == 36):

                coords25 = []
                vertexes = []
                normals =[]
                uv = []

                pos = file.tell()

                b3dObj = bpy.data.objects.new(objName, None)
                b3dObj['block_type'] = type
                b3dObj['pos'] = pos

                b3dObj.parent = context.scene.objects[objString[-1]]
                context.collection.objects.link(b3dObj)
                realName = b3dObj.name
                objString.append(b3dObj.name)

                bounding_sphere = struct.unpack("<4f",file.read(16))
                name1 = readName(file)
                name2 = readName(file)

                formatRaw = struct.unpack("<i",file.read(4))[0]
                uvCount = formatRaw >> 8
                format = formatRaw & 0xFF

                vertexCount = struct.unpack("<i",file.read(4))[0]
                if format == 0:
                    objString.append(objString[-1])
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
                                normal = struct.unpack("<f",file.read(4))

                    # if format == 2:
                    #     for i in range(vertexCount):
                    #         vertexes.append(struct.unpack("<3f",file.read(12)))
                    #         uv.append(struct.unpack("<2f",file.read(8)))
                    #         normals.append(struct.unpack("<3f",file.read(12)))
                    #         #file.seek(12,1)
                    # elif format ==3:

                    #     for i in range(vertexCount):
                    #         vertexes.append(struct.unpack("<3f",file.read(12)))
                    #         uv.append(struct.unpack("<2f",file.read(8)))
                    #         file.seek(4,1)

                    # elif ((format ==258) or (format ==515)):

                    #     for i in range(vertexCount):
                    #         vertexes.append(struct.unpack("<3f",file.read(12)))
                    #         uv.append(struct.unpack("<2f",file.read(8)))
                    #         normals.append(struct.unpack("<3f",file.read(12)))
                    #         file.seek(8,1)
                    # elif format ==514:
                    #     for i in range(vertexCount):
                    #         vertexes.append(struct.unpack("<3f",file.read(12)))
                    #         uv.append(struct.unpack("<2f",file.read(8)))
                    #         normals.append(struct.unpack("<3f",file.read(12)))
                    #         struct.unpack("<4f",file.read(16))

                childCnt = struct.unpack("<i",file.read(4))[0]#01 00 00 00 subblocks count

            elif (type == 37):

                coords25 = []
                vertexes = []
                normals = []
                uv = []

                b3dObj = bpy.data.objects.new(objName, None) #create empty

                pos = file.tell()
                b3dObj['block_type'] = type
                b3dObj['pos'] = pos

                bounding_sphere = struct.unpack("<4f",file.read(16))

                groupName = readName(file)

                formatRaw = struct.unpack("<i",file.read(4))[0]
                uvCount = formatRaw >> 8
                format = formatRaw & 0xFF


                vertexCount = struct.unpack("<i",file.read(4))[0]
                b3dObj['SType'] = format

                b3dObj.parent = context.scene.objects[objString[-1]]
                context.collection.objects.link(b3dObj)
                realName = b3dObj.name
                # objString.append(context.scene.objects[0].name)
                objString.append(b3dObj.name)

                if vertexCount > 0:

                    if format == 0:
                        objString.append(objString[-1])
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
                                normal = struct.unpack("<f",file.read(4))

                            # elif ((format ==258) or (format ==515)): #258 - стекло

                            #     for i in range(vertexCount):
                            #         vertexes.append(struct.unpack("<3f",file.read(12)))
                            #         uv.append(struct.unpack("<2f",file.read(8)))
                            #         normals.append(struct.unpack("<3f",file.read(12)))
                            #         file.seek(8,1)
                            # elif format ==514:
                            #     for i in range(vertexCount):
                            #         vertexes.append(struct.unpack("<3f",file.read(12)))
                            #         uv.append(struct.unpack("<2f",file.read(8)))
                            #         normals.append(struct.unpack("<3f",file.read(12)))
                            #         file.seek(16,1)
                                    # struct.unpack("<4f",file.read(16))

                childCnt = struct.unpack("<i",file.read(4))[0]#01 00 00 00 subblocks count

            elif (type == 39):
                cnt+=1
                b3dObj = bpy.data.objects.new(objName, None)
                b3dObj['block_type'] = type
                b3dObj['pos'] = str(file.tell())

                b3dObj.parent = context.scene.objects[objString[-1]]
                context.collection.objects.link(b3dObj)
                realName = b3dObj.name
                # objString.append(context.scene.objects[0].name)
                objString.append(b3dObj.name)
                ##b3dObj.hide_viewport = True

                bounding_sphere = struct.unpack("<4f",file.read(16))
                color_r = struct.unpack("<i",file.read(4))
                unknown = struct.unpack("<f",file.read(4))
                fog_start = struct.unpack("<f",file.read(4))
                fog_end = struct.unpack("<f",file.read(4))
                colorId = struct.unpack("<i",file.read(4))
                childCnt = struct.unpack("<i",file.read(4))

            elif (type == 40):
                data = []
                data1 = []
                cnt+=1

                bounding_sphere = struct.unpack("<4f",file.read(16))
                #bpy.ops.mesh.primitive_ico_sphere_add(size=0.05, calc_uvs=True, location=sp_pos)
                #b3dObj = bpy.context.selected_objects[0]
                b3dObj = bpy.data.objects.new(objName, None)
                b3dObj.location = bounding_sphere[:3]

                context.collection.objects.link(b3dObj)
                realName = b3dObj.name
                #b3dObj.name = objName
                b3dObj['block_type'] = type
                b3dObj['pos'] = str(file.tell())

                b3dObj.parent = context.scene.objects[objString[-1]]
                # objString.append(context.scene.objects[0].name)
                objString.append(b3dObj.name)
                #bpy.ops.object.select_all(action='DESELECT')
                #b3dObj.hide_viewport = True

                name1 = readName(file)
                name2 = readName(file)
                #file.read(52)

                unknown1 = struct.unpack("<i",file.read(4))[0]
                unknown2 = struct.unpack("<i",file.read(4))[0]
                num = struct.unpack("<i",file.read(4))[0]
                for i in range(num):
                    data1.append(struct.unpack("f", file.read(4))[0])

            #elif (type == 40):
            #	data = []
            #	data1 = []
            #	cnt+=1
            #	b3dObj = bpy.data.objects.new(objName, None)
            #	b3dObj['block_type'] = 40
            #	b3dObj.parent = context.scene.objects[objString[-1]]
            #	context.collection.objects.link(b3dObj)
            #	objString.append(context.scene.objects[0].name)
                #b3dObj.hide_viewport = True

            #	qu = quat(file).v
            #	file.read(32)
            #	file.read(32)
                #file.read(52)
            #	data = struct.unpack("<3i",file.read(12))
            #	for i in range (data[-1]):
            #		data1.append(struct.unpack("f", file.read(4))[0])

            else:
                log.warning('smthng wrng')
                return

            log.info("Importing block #{}: {}".format(type, realName))

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
    vert = bpy.context.object.data.vertices
    face = bpy.context.object.data.polygons
    edge = bpy.context.object.data.edges
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
    data = bpy.context.object.data
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
                            name = readCString(resFile).split(" ")[0]
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