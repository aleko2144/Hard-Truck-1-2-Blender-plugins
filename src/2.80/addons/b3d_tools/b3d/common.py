import struct
import bpy
import re
from mathutils import Vector
import math

from ..common import log
from ..consts import (
    BLOCK_TYPE,
    EMPTY_NAME
)

def writeSize(file, ms, writeMs=None):
    if writeMs is None:
        writeMs = ms
    endMs = file.tell()
    size = endMs - ms
    file.seek(writeMs, 0)
    file.write(struct.pack("<i", size))
    file.seek(endMs, 0)

def getNotNumericName(name):
    reIsCopy = re.compile(r'\|')
    matchInd = reIsCopy.search(name)
    result = name
    if matchInd:
        result = name[matchInd.span()[0]+1:]
    return result

def getNonCopyName(name):
    reIsCopy = re.compile(r'\.[0-9]*$')
    matchInd = reIsCopy.search(name)
    result = name
    if matchInd:
        result = name[:matchInd.span()[0]]
    return result

def isRootObj(obj):
    return obj.parent is None and obj.name[-4:] == '.b3d'

def getRootObj(obj):
    result = obj
    while not isRootObj(result):
        result = result.parent
    return result

def isEmptyName(name):
    reIsEmpty = re.compile(r'.*{}.*'.format(EMPTY_NAME))
    return reIsEmpty.search(name)

def isMeshBlock(obj):
    # 18 - for correct transform apply
    return obj.get("block_type") is not None \
        and (obj["block_type"]==8 or obj["block_type"]==35\
        or obj["block_type"]==28 \
        # or obj["block_type"]==18
        )

def isRefBlock(obj):
    return obj.get("block_type") is not None and obj["block_type"]==18

def unmaskTemplate(templ):
    offset = 0
    unmasks = []
    tA = int(templ[0])
    tR = int(templ[1])
    tG = int(templ[2])
    tB = int(templ[3])
    totalBytes = tR + tG + tB + tA
    for i in range(4):
        curInt = int(templ[i])
        lzeros = offset
        bits = curInt
        rzeros = totalBytes - lzeros - bits
        unmasks.append([lzeros, bits, rzeros])
        offset += curInt
    return unmasks

def unmaskBits(num, bytes=2):
    bits = [int(digit) for digit in bin(num)[2:]]
    lzeros = 0
    rzeros = 0
    ones = 0
    if num == 0:
        return [0, 0, 0]
    for bit in bits:
        if bit:
            ones+=1
        else:
            rzeros+=1
        lzeros = bytes*8 - len(bits)
    return [lzeros, ones, rzeros]


def readCString(file):
    try:
        chrs = []
        i = 0
        chrs.append(file.read(1).decode("utf-8"))
        while ord(chrs[i]) != 0:
            chrs.append(file.read(1).decode("utf-8"))
            i += 1
        return "".join(chrs[:-1])
    except TypeError as e:
        log.error("Error in readCString. Nothing to read")
        return ""


def readRESSections(filepath):
	sections = []
	with open(filepath, "rb") as file:
		k = 0
		while 1:
			category = readCString(file)
			if(len(category) > 0):
				resSplit = category.split(" ")
				id = resSplit[0]
				cnt = int(resSplit[1])

				sections.append({})

				sections[k]["name"] = id
				sections[k]["cnt"] = cnt
				sections[k]["data"] = []

				log.info("Reading category {}".format(id))
				log.info("Element count in category is {}.".format(cnt))
				if cnt > 0:
					log.info("Start processing...")
					resData = []
					if id in ["COLORS", "MATERIALS", "SOUNDS"]: # save only .txt
						for i in range(cnt):
							data = {}
							data['row'] = readCString(file)
							resData.append(data)

					else: #PALETTEFILES, SOUNDFILES, BACKFILES, MASKFILES, TEXTUREFILES
						for i in range(cnt):

							data = {}
							data['row'] = readCString(file)
							data['size'] = struct.unpack("<i",file.read(4))[0]
							data['bytes'] = file.read(data['size'])
							resData.append(data)

					sections[k]['data'] = resData

				else:
					log.info("Skip category")
				k += 1
			else:
				break
	return sections


class HTMaterial():

    def __init__(self):
        self.prefix = ""
        self.path = ""
        self.reflect = None #HT1 float
        self.specular = None #HT1 float
        self.transp = None # float
        self.rot = None # float
        self.col = None # int
        self.tex = None # int
        self.ttx = None # int
        self.itx = None # int
        self.att = None # int
        self.msk = None # int
        self.power = None # int
        self.coord = None # int
        self.envId = None # int
        self.env = None #scale x,y  2 floats
        self.rotPoint = None # 2 floats
        self.move = None # 2 floats
        self.noz = False # bool
        self.nof = False # bool
        self.notile = False # bool
        self.notileu = False # bool
        self.notilev = False # bool
        self.alphamirr = False # bool
        self.bumpcoord = False # bool
        self.usecol = False # bool
        self.wave = False # bool

def getColPropertyByName(colProperty, value):
    result = None
    for item in colProperty:
        if item.value == value:
            result = item
            break
    return result

def getColPropertyIndexByName(colProperty, value):
    result = -1
    for idx, item in enumerate(colProperty):
        if item.value == value:
            result = idx
            break
    return result

def existsColPropertyByName(colProperty, value):
    for item in colProperty:
        if item.value == value:
            return True
    return False

def getMaterialIndexInRES(matName):
    resModules = bpy.context.scene.my_tool.resModules
    delimiterInd = matName.find("_")
    resModuleName = matName[:delimiterInd]
    materialName = matName[delimiterInd+1:]
    curModule = getColPropertyByName(resModules, resModuleName)
    curMaterialInd = getColPropertyIndexByName(curModule.materials, materialName)
    return curMaterialInd

def getColorImgName(moduleName, index):
    return "col_{}_{:03d}".format(moduleName, index)

# https://blenderartists.org/t/index-lookup-in-a-collection/512818/2
def getColPropertyIndex(prop):
    txt = prop.path_from_id()
    pos = txt.rfind('[')
    colIndex = txt[pos+1: len(txt)-1]
    return int(colIndex)

def getCurrentRESIndex():
    mytool = bpy.context.scene.my_tool
    return int(mytool.selectedResModule)

def getCurrentRESModule():
    mytool = bpy.context.scene.my_tool
    resModule = None
    ind = getCurrentRESIndex()
    if ind > -1:
        resModule = mytool.resModules[ind]
    return resModule

def getActivePaletteModule(resModule):
    mytool = bpy.context.scene.my_tool
    if resModule:
        if len(resModule.palette_colors) > 0:
            return resModule
        commonResModule = getColPropertyByName(mytool.resModules, 'COMMON')
        if len(commonResModule.palette_colors) > 0:
            return commonResModule
    return None

def updateColorPreview(resModule, ind):
    moduleName = resModule.value
    bpyImage = bpy.data.images.get(getColorImgName(moduleName, ind+1))
    if bpyImage is None:
        bpyImage = bpy.data.images.new(getColorImgName(moduleName, ind+1), width=1, height=1, alpha=1)
    bpyImage.pixels[0] = resModule.palette_colors[ind].value[0]
    bpyImage.pixels[1] = resModule.palette_colors[ind].value[1]
    bpyImage.pixels[2] = resModule.palette_colors[ind].value[2]
    bpyImage.pixels[3] = resModule.palette_colors[ind].value[3]
    bpyImage.preview_ensure()
    bpyImage.preview.reload()


def getMatTextureRefDict(resModule):
    matToTexture = {}
    textureToMat = {}
    for i, mat in enumerate(resModule.materials):
        if mat.is_tex:
            matToTexture[i] = mat.tex-1
            textureToMat[mat.tex-1] = i

    return [matToTexture, textureToMat]


def rgb_to_srgb(r, g, b, alpha = 1):
    # convert from RGB to sRGB
    r_linear = r / 255.0
    g_linear = g / 255.0
    b_linear = b / 255.0

    def srgb_transform(value):
        if value <= 0.04045:
            return value / 12.92
        else:
            return math.pow(((value + 0.055) / 1.055), 2.4)

    r_srgb = srgb_transform(r_linear)
    g_srgb = srgb_transform(g_linear)
    b_srgb = srgb_transform(b_linear)

    return (r_srgb, g_srgb, b_srgb, alpha)


def srgb_to_rgb(r, g, b):
    # convert from sRGB to RGB

    def srgb_inverse_transform(value):
        if value <= 0.04045 / 12.92:
            return value * 12.92
        else:
            return math.pow(value, 1 / 2.4) * 1.055 - 0.055

    r_rgb = srgb_inverse_transform(r)
    g_rgb = srgb_inverse_transform(g)
    b_rgb = srgb_inverse_transform(b)

    return (round(r_rgb * 255), round(g_rgb * 255), round(b_rgb * 255))

# https://blender.stackexchange.com/questions/234388/how-to-convert-rgb-to-hex-almost-there-1-error-colors
# def linear_to_srgb8(c):
#     if c < 0.0031308:
#         srgb = 0.0 if c < 0.0 else c * 12.92
#     else:
#         srgb = 1.055 * math.pow(c, 1.0 / 2.4) - 0.055
#     if srgb > 1: srgb = 1

#     return round(255*srgb)

#https://blender.stackexchange.com/questions/158896/how-set-hex-in-rgb-node-python
# def srgb_to_linearrgb(c):
#     if   c < 0:       return 0
#     elif c < 0.04045: return c/12.92
#     else:             return ((c+0.055)/1.055)**2.4

# def hex_to_rgb(r,g,b,alpha=1):
#     return tuple([srgb_to_linearrgb(c/0xff) for c in (r,g,b)] + [alpha])


def getUsedVerticesAndTransform(vertices, faces):
    indices = set()
    oldNewTransf = {}
    newOldTransf = {}
    newVertexes = []
    newFaces = []
    for face in faces:
        for idx in face:
            indices.add(idx)
    indices = sorted(indices)
    for idx in indices:
        oldNewTransf[idx] = len(newVertexes)
        newOldTransf[len(newVertexes)] = idx
        newVertexes.append(vertices[idx])
    newFaces = getUsedFaces(faces, oldNewTransf)

    return [newVertexes, newFaces, indices, oldNewTransf, newOldTransf]

def transformVertices(vertices, idxTransf):
    newVertices = []
    for idx in vertices:
        newVertices.append(idxTransf[idx])
    return newVertices

def getUsedFaces(faces, idxTransf):
    newFaces = []
    for face in faces:
        newFace = getUsedFace(face, idxTransf)
        newFaces.append(tuple(newFace))
    return newFaces

def getUserVertices(faces):
    indices = set()
    for face in faces:
        for idx in face:
            indices.add(idx)
    return list(indices)


def getUsedFace(face, idxTransf):
    newFace = []
    for idx in face:
        newFace.append(idxTransf[idx])
    return newFace


def getPolygonsBySelectedVertices(obj):
    data = obj.data
    # data = bpy.context.object.data
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

def getSelectedVertices(obj):
    data = obj.data
    # data = bpy.context.object.data
    selectedVertices = []
    for v in data.vertices:
        if v.select:
            selectedVertices.append(v)

    return selectedVertices


def getAllChildren(obj):
    allChildren = []
    currentObjs = [obj]
    while(1):
        nextChildren = []
        if len(currentObjs) > 0:
            for obj in currentObjs:
                nextChildren.extend(obj.children)
            currentObjs = nextChildren
            allChildren.extend(currentObjs)
        else:
            break
    return allChildren

def getMytoolBlockNameByClass(zclass, multipleClass = True):
    bname = ''
    btype, bnum = zclass.__name__.split('_')
    if btype == 'b':
        if multipleClass:
            bname = 'block{}'.format(bnum)
        else:
            bname = 'sBlock{}'.format(bnum)
    elif btype == 'pfb':
        bname = 'perFaceBlock{}'.format(bnum)
    elif btype == 'pvb':
        bname = 'perVertBlock{}'.format(bnum)

    return [bname, bnum]


def getMytoolBlockName(btype, bnum, multipleClass = False):
    bname = ''
    if btype == 'b':
        if multipleClass:
            bname = 'block{}'.format(bnum)
        else:
            bname = 'sBlock{}'.format(bnum)
    elif btype == 'pfb':
        bname = 'perFaceBlock{}'.format(bnum)
    elif btype == 'pvb':
        bname = 'perVertBlock{}'.format(bnum)

    return bname

def getPythagorLength(p1, p2):
    return (sum(map(lambda xx,yy : (xx-yy)**2,p1,p2)))**0.5

# https://b3d.interplanety.org/en/how-to-calculate-the-bounding-sphere-for-selected-objects/
def getMultObjBoundingSphere(objnTransfs, mode='BBOX'):
    # return the bounding sphere center and radius for objects (in global coordinates)
    # if not isinstance(objects, list):
    #     objects = [objects]
    points_co_global = []
    # if mode == 'GEOMETRY':
    #     # GEOMETRY - by all vertices/points - more precis, more slow
    #     for obj in objects:
    #         points_co_global.extend([obj.matrix_world @ vertex.co for vertex in obj.data.vertices])
    if mode == 'BBOX':
        # BBOX - by object bounding boxes - less precis, quick
        for objnTransf in objnTransfs:
            obj = bpy.data.objects[objnTransf['obj']]
            transf = bpy.data.objects[objnTransf['transf']]
            points_co_global.extend([transf.matrix_world @ Vector(bbox) for bbox in obj.bound_box])

    def get_center(l):
        return (max(l) + min(l)) / 2 if l else 0.0

    x, y, z = [[point_co[i] for point_co in points_co_global] for i in range(3)]
    b_sphere_center = Vector([get_center(axis) for axis in [x, y, z]]) if (x and y and z) else None
    b_sphere_radius = max(((point - b_sphere_center) for point in points_co_global)) if b_sphere_center else None
    return [b_sphere_center, b_sphere_radius.length]

# https://blender.stackexchange.com/questions/62040/get-center-of-geometry-of-an-object
def getSingleCoundingSphere(obj, local = False):
    center = 0.125 * sum((Vector(b) for b in obj.bound_box), Vector())
    p1 = obj.bound_box[0]
    if not local:
        center = obj.matrix_world @ center
        p1 = obj.matrix_world @ Vector(obj.bound_box[0])
    rad = getPythagorLength(center, p1)
    return [center, rad]

def getCenterCoord(vertices):
    if len(vertices) == 0:
        return (0.0, 0.0, 0.0)
    x = [p[0] for p in vertices]
    y = [p[1] for p in vertices]
    z = [p[2] for p in vertices]
    centroid = (sum(x) / len(vertices), sum(y) / len(vertices), sum(z) / len(vertices))

    return centroid

def getLevelGroup(obj):
    parent = obj.parent
    if parent is None:
        return 0
    if parent.get(BLOCK_TYPE) == 444:
        return int(parent.name[6]) #GROUP_n
    return 0

def referenceablesCallback(self, context):

    mytool = context.scene.my_tool
    rootObj = getRootObj(context.object)

    referenceables = [cn for cn in rootObj.children if cn.get(BLOCK_TYPE) != 24]

    enumProperties = [(cn.name, cn.name, "") for i, cn in enumerate(referenceables)]

    return enumProperties

def spacesCallback(self, context):

    mytool = context.scene.my_tool
    rootObj = getRootObj(context.object)

    spaces = [cn for cn in bpy.data.objects if cn.get(BLOCK_TYPE) == 24 and getRootObj(cn) == rootObj]

    enumProperties = [(cn.name, cn.name, "") for i, cn in enumerate(spaces)]

    return enumProperties

def resMaterialsCallback(self, context):

	mytool = context.scene.my_tool
	rootObj = getRootObj(context.object)
	moduleName = rootObj.name[:-4]

	resModules = mytool.resModules
	curModule = getColPropertyByName(resModules, moduleName)

	enumProperties = [(str(i), cn.value, "") for i, cn in enumerate(curModule.materials)]

	return enumProperties

def roomsCallback(bname, pname):
    def callback_func(self, context):

        enumProperties = []

        mytool = context.scene.my_tool
        resModule = context.object.path_resolve('["{}"]'.format(pname))

        rootObj = bpy.data.objects.get('{}.b3d'.format(resModule))
        if rootObj:
            rooms = [cn for cn in rootObj.children if cn.get(BLOCK_TYPE) == 19]

            enumProperties = [(cn.name, cn.name, "") for i, cn in enumerate(rooms)]

        return enumProperties
    return callback_func


def modulesCallback(self, context):

    mytool = context.scene.my_tool

    modules = [cn for cn in bpy.data.objects if isRootObj(cn)]

    enumProperties = [(cn.name, cn.name, "") for i, cn in enumerate(modules)]

    return enumProperties


def resModulesCallback(self, context):

    mytool = bpy.context.scene.my_tool

    modules = [cn for cn in mytool.resModules if cn.value != "-1"]

    enumProperties = [(cn.value, cn.value, "") for i, cn in enumerate(modules)]

    return enumProperties