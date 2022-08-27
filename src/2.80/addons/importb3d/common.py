from asyncio.windows_events import NULL
import os
import struct
import bpy
import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
log = logging.getLogger("common")
log.setLevel(logging.DEBUG)

def ShowMessageBox(message = "", title = "Message Box", icon = 'INFO'):

    def draw(self, context):
        self.layout.label(text=message)

    bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)


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
        self.reflect = 0.0 #HT1
        self.specular = 0.0 #HT1
        self.col = 0
        self.transp = 1.0
        self.tex = 0
        self.ttx = 0
        self.rot = 0.0
        self.rotPoint = [0, 0]
        self.power = 0.0
        self.noz = False
        self.nof = False
        self.notile = False
        self.move = None
        self.att = 0
        self.itx = 0
        self.coord = 2
        self.env = [0, 0] #scale x,y
        self.notilev = False
        self.notileu = False
        self.bumpcoord = 0
        self.alphamirr = 0

class Vector3F():

    def __init__(self, file=NULL, tuple=NULL):
        if file != NULL:
            tpl = struct.unpack("<3f", file.read(12))
            self.x = tpl[0]
            self.y = tpl[1]
            self.z = tpl[2]
        elif tuple != NULL:
            self.x = tuple[0]
            self.y = tuple[1]
            self.z = tuple[2]
        else:
            self.x = 0
            self.y = 0
            self.z = 0



class RESUnpack():

    def __init__(self):
        self.prefix = ""
        self.textures = []
        self.maskfiles = []
        self.materials = []
        self.materialParams = []
        self.colors = []

    def getPrefixedMaterial(self, ind):
        return "{}_{}".format(self.prefix, self.materials[ind])

def parseMaterial(matString, prefix):
    params = matString.split(" ")
    i = 1
    mat = HTMaterial()
    mat.prefix = prefix
    mat.path = params[0]
    while i < len(params):
        if params[i] == "col":
            i+=1
            mat.col = int(params[i])
        elif params[i] == "tex":
            i+=1
            mat.tex = int(params[i])
        elif params[i] == "ttx":
            i+=1
            mat.ttx = int(params[i])
        elif params[i] == "itx":
            i+=1
            mat.itx = int(params[i])
        i+=1
    return mat


def parseMaterials(filepath, prefix):
    content = ""
    with open(filepath, "rb") as matFile:
        content = matFile.read().decode("UTF-8")

    matStrings = content.split("\n")
    materials = []
    for matStr in matStrings:
        material = parseMaterial(matStr, prefix)
        materials.append(material)
    return materials

#https://blender.stackexchange.com/questions/118646/add-a-texture-to-an-object-using-python-and-blender-2-8
def createMaterial(palette, texturelist, texturepath, mat, imageFormat):
    newMat = bpy.data.materials.new(name="{}_{}".format(mat.prefix, mat.path))
    newMat.use_nodes = True
    bsdf = newMat.node_tree.nodes["Principled BSDF"]
    if int(mat.col) > 0:
        R = palette[mat.col-1][0]
        G = palette[mat.col-1][1]
        B = palette[mat.col-1][2]
        texColor = newMat.node_tree.nodes.new("ShaderNodeRGB")
        texColor.outputs[0].default_value = hex_to_rgb(R,G,B)
        newMat.node_tree.links.new(bsdf.inputs['Base Color'], texColor.outputs['Color'])
    if int(mat.tex) > 0 or int(mat.ttx) > 0 or int(mat.itx) > 0:
        texidx = mat.tex | mat.ttx | mat.itx
        path = texturelist[texidx-1][:-4]
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

