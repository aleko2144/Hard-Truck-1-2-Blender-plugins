import bpy

import logging
import sys


# https://blenderartists.org/t/solved-adding-a-tab-in-blender-2-8/1133119/3

from .compatibility import (
    get_user_preferences
)

def recalc_to_local_coord(center, vertexes):
    new_vertexes = []
    for vert in vertexes:
        newVert = [0.0,0.0,0.0]
        newVert[0] = vert[0] - center[0]
        newVert[1] = vert[1] - center[1]
        newVert[2] = vert[2] - center[2]
        new_vertexes.append(newVert)

    return new_vertexes

def createLogger(module_name):
    log_level = 40 #ERROR
    log = logging.getLogger(module_name)
    log.setLevel(log_level)
    if not log.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s - %(message)s','%H:%M:%S'))
        log.addHandler(handler)
    return log

common_logger = createLogger("b3d_tools.common")
exportb3d_logger = createLogger("b3d_tools.export_b3d")
exportres_logger = createLogger("b3d_tools.export_res")
exportway_logger = createLogger("b3d_tools.export_way")
imghelp_logger = createLogger("b3d_tools.imghelp")
importb3d_logger = createLogger("b3d_tools.import_b3d")
importres_logger = createLogger("b3d_tools.import_res")
importway_logger = createLogger("b3d_tools.import_way")
panel_logger = createLogger("b3d_tools.panel")
menus_logger = createLogger("b3d_tools.menus")
scripts_logger = createLogger("b3d_tools.scripts")
classes_logger = createLogger("b3d_tools.classes")
custom_ui_list_logger = createLogger("b3d_tools.ui_list")

loggers = [common_logger, exportb3d_logger, importres_logger, exportway_logger, imghelp_logger, importb3d_logger, importway_logger, panel_logger, menus_logger, scripts_logger, classes_logger, custom_ui_list_logger]

def updateLoggers(self, context):
    user_prefs = get_user_preferences()
    log_level = int(user_prefs.addons['b3d_tools'].preferences.logger_level)
    for logger in loggers:
        logger.setLevel(log_level)



