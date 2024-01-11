import os
import struct
import bpy
import logging
import sys
import re
import time
from mathutils import Vector

from ..common import log
from ..consts import (
    BLOCK_TYPE,
    EMPTY_NAME
)

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

def unmaskShort(num):
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
        lzeros = 16 - len(bits)
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


def createMaterials(resModule, palette, texturePath, imageFormat):
    materialList = resModule.materials

    for material in materialList:
        createMaterial(resModule, palette, texturePath, material, imageFormat)

#https://blender.stackexchange.com/questions/118646/add-a-texture-to-an-object-using-python-and-blender-2-8
def createMaterial(resModule, palette, texturepath, mat, imageFormat):

    textureList = resModule.textures

    newMat = bpy.data.materials.new(name="{}_{}".format(resModule.value, mat.value))
    newMat.use_nodes = True
    bsdf = newMat.node_tree.nodes["Principled BSDF"]

    if mat.is_col and int(mat.col) > 0:
        R = palette[mat.col-1][0]
        G = palette[mat.col-1][1]
        B = palette[mat.col-1][2]
        texColor = newMat.node_tree.nodes.new("ShaderNodeRGB")
        texColor.outputs[0].default_value = hex_to_rgb(R,G,B)
        newMat.node_tree.links.new(bsdf.inputs['Base Color'], texColor.outputs['Color'])

    if (mat.is_tex and int(mat.tex) > 0) \
    or (mat.is_ttx and int(mat.ttx) > 0) \
    or (mat.is_itx and int(mat.itx) > 0):
        texidx = mat.tex | mat.ttx | mat.itx
        path = textureList[texidx-1].value
        texImage = newMat.node_tree.nodes.new("ShaderNodeTexImage")
        texImage.image = bpy.data.images.load(os.path.join(texturepath, "{}.{}".format(path, imageFormat)))
        newMat.node_tree.links.new(bsdf.inputs['Base Color'], texImage.outputs['Color'])


#https://blender.stackexchange.com/questions/158896/how-set-hex-in-rgb-node-python
def srgb_to_linearrgb(c):
    if   c < 0:       return 0
    elif c < 0.04045: return c/12.92
    else:             return ((c+0.055)/1.055)**2.4

def hex_to_rgb(r,g,b,alpha=1):
    return tuple([srgb_to_linearrgb(c/0xff) for c in (r,g,b)] + [alpha])


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


def recalcToLocalCoord(center, vertexes):
    newVertexes = []
    for vert in vertexes:
        newVert = [0.0,0.0,0.0]
        newVert[0] = vert[0] - center[0]
        newVert[1] = vert[1] - center[1]
        newVert[2] = vert[2] - center[2]
        newVertexes.append(newVert)

    return newVertexes

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
    # log.debug(parent)
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