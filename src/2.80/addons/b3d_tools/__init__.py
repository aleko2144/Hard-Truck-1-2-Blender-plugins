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
	# importlib.reload(object_UIList)
	# importlib.reload(material_UIList)
	importlib.reload(custom_UIList)
	importlib.reload(common)
	importlib.reload(consts)
	importlib.reload(way)
	importlib.reload(tch)
	importlib.reload(b3d)
else:
	import bpy
	from . import (
		# object_UIList,
		# material_UIList,
		custom_UIList,
		common,
		consts,
		way,
		tch,
		b3d
	)




from .tch import tch_unregister, tch_register



bl_info = {
	"name": "King of The Road Tools",
	"description": "",
	"author": "Andrey Prozhoga, LabVaKars",
	"version": (2, 3, 1),
	"blender": (2, 93, 0),
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
	custom_UIList.register()
	way.register()
	b3d.register()
	# tch_register()

def unregister():
	b3d.unregister()
	way.unregister()
	custom_UIList.unregister()
	# tch_unregister()

if __name__ == "__main__":
	register()
