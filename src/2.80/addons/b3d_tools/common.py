import bpy

import logging
import sys


# https://blenderartists.org/t/solved-adding-a-tab-in-blender-2-8/1133119/3
def getRegion():
	if bpy.app.version < (2,80,0):
		return "TOOLS"
	else:
		return "UI"


logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
log = logging.getLogger("common")