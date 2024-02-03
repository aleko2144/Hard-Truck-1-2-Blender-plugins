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

def createLogger(module_name):
    log_level = 40 #ERROR
    log = logging.getLogger(module_name)
    log.setLevel(log_level)
    log.addHandler(logging.StreamHandler(sys.stdout))
    return log

common_logger = createLogger("common")
exportb3d_logger = createLogger("export_b3d")
exportway_logger = createLogger("export_way")
imghelp_logger = createLogger("imghelp")
importb3d_logger = createLogger("import_b3d")
importway_logger = createLogger("import_way")
menus_logger = createLogger("menus")
scripts_logger = createLogger("scripts")

loggers = [common_logger, exportb3d_logger, exportway_logger, imghelp_logger, importb3d_logger, importway_logger, menus_logger, scripts_logger]


