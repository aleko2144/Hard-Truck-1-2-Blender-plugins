# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>

if "bpy" in locals():
	print("Reimporting modules!!!")
	import importlib
	importlib.reload(common)
	importlib.reload(way)
	importlib.reload(tch)
	importlib.reload(b3d)
	# importlib.reload(exportb3d)
else:
	import bpy
	from . import (
		common,
		way,
		tch,
		b3d
	)




# from .b3d import b3d_register, b3d_unregister
from .b3d import b3d_register, b3d_unregister
from .tch import tch_unregister, tch_register
from .b3d.panel import b3dpanel_register, b3dpanel_unregister
from .way import way_register, way_unregister

# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>

bl_info = {
	"name": "King of The Road Tools",
	"description": "",
	"author": "Andrey Prozhoga",
	"version": (1, 2, 2),
	"blender": (2, 80, 0),
	"location": "3D View > Tools",
	"warning": "",
	"wiki_url": "",
	"tracker_url": "vk.com/rnr_mods",
	"category": "Development"
}


# ------------------------------------------------------------------------
# register and unregister
# ------------------------------------------------------------------------


def register():
	b3d_register()
	# tch_register()
	b3dpanel_register()

def unregister():
	b3dpanel_unregister()
	# tch_unregister()
	b3d_unregister()

if __name__ == "__main__":
	register()
