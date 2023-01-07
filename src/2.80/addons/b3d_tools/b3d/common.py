import os
import struct
import bpy
import logging
import sys
import re

from ..common import log

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
    reIsEmpty = re.compile(r'.*empty name.*')
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