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
    importlib.reload(compatibility)
    importlib.reload(common)
    importlib.reload(consts)
    importlib.reload(b3d)
else:
    import bpy
    from . import (
        compatibility,
        common,
        consts,
        b3d
    )


bl_info = {
    "name": "King of The Road Tools",
    "description": "",
    "author": "Andrey Prozhoga, LabVaKars",
    "version": (2, 3, 3),
    "blender": (2, 79, 0),
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
    b3d.register()
    common.updateLoggers(None, None)

def unregister():
    b3d.unregister()

if __name__ == "__main__":
    register()
