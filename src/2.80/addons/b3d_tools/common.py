import bpy

import logging
import sys


# https://blenderartists.org/t/solved-adding-a-tab-in-blender-2-8/1133119/3
def getRegion():
    if bpy.app.version < (2,80,0):
        return "TOOLS"
    else:
        return "UI"

def recalcToLocalCoord(center, vertexes):
    newVertexes = []
    for vert in vertexes:
        newVert = [0.0,0.0,0.0]
        newVert[0] = vert[0] - center[0]
        newVert[1] = vert[1] - center[1]
        newVert[2] = vert[2] - center[2]
        newVertexes.append(newVert)

    return newVertexes


logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
log = logging.getLogger("common")