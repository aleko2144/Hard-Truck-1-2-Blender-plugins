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
    'name': 'King of the Road B3D importer/exporter',
    'author': 'Yuriy Gladishenko, Andrey Prozhoga',
    'version': (0, 1, 17),
    'blender': (2, 80, 0),
    'api': 34893,
    'description': 'This script imports and exports the King of the Road b3d',
    'warning': '',
    'wiki_url': 'http://wiki.blender.org/index.php/Extensions:2.5/Py/Scripts/'\
        'Import-Export/M3_Import',
    'tracker_url': 'vk.com/rnr_mods',
    'category': 'Import-Export'}

# To support reload properly, try to access a package var, if it's there,
# reload everything
if "bpy" in locals():
    print("Reimporting modules!!!")
    import importlib
    importlib.reload(common)
    importlib.reload(importb3d)
    # importlib.reload(exportb3d)
    importlib.reload(imghelp)
else:
    import bpy
    from . import (
        common,
        importb3d,
        # exportb3d,
        imghelp,
    )

from threading import Lock, Thread
import time
import datetime
import os
import bpy
from bpy.props import StringProperty, BoolProperty, CollectionProperty
from bpy_extras.io_utils import ImportHelper, ExportHelper
# from . import common, exportb3d, imghelp, importb3d

def thread_import_b3d(self, files, context):
    for b3dfile in files:
        filepath = os.path.join(self.directory, b3dfile.name)

        print('Importing file', filepath)
        t = time.mktime(datetime.datetime.now().timetuple())
        with open(filepath, 'rb') as file:
            importb3d.read(file, context, self, filepath)
        t = time.mktime(datetime.datetime.now().timetuple()) - t
        print('Finished importing in', t, 'seconds')

class HTImportPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    COMMON_RES_Path: bpy.props.StringProperty(
        name="Common.res path",
        default="",
        subtype='FILE_PATH')

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.prop(self, 'COMMON_RES_Path', expand=True)


class ImportB3D(bpy.types.Operator, ImportHelper):
    '''Import from B3D file format (.b3d)'''
    bl_idname = 'import_scene.kotr_b3d'
    bl_label = 'Import B3D'

    filename_ext = '.b3d'

    files: CollectionProperty(
        type=bpy.types.OperatorFileListElement,
        options={'HIDDEN', 'SKIP_SAVE'},
    )

    directory: StringProperty(maxlen=1024, subtype='FILE_PATH', options={'HIDDEN', 'SKIP_SAVE'})

    filter_glob : StringProperty(default='*.b3d', options={'HIDDEN'})

    to_unpack_res : BoolProperty(name='Unpack .res archive',
                    description='Unpack associated with .b3d fie .res archive. \n'\
                                'NOTE: .res archive must be located in the same folder as .b3d file', default=False)

    to_import_textures : BoolProperty(name='Import Textures',
                    description='Import textures from unpacked .res archive. \n'\
                                'NOTE: if importing for the first time select previous option too', default=False)


    textures_format : StringProperty(
        name="Images format",
        description="Loaded images format",
        default="tga",
    )

    def thread_import_b3d(self, files, context):
        for b3dfile in files:
            filepath = os.path.join(self.directory, b3dfile.name)

            print('Importing file', filepath)
            t = time.mktime(datetime.datetime.now().timetuple())
            with open(filepath, 'rb') as file:
                importb3d.read(file, context, self, filepath)
            t = time.mktime(datetime.datetime.now().timetuple()) - t
            print('Finished importing in', t, 'seconds')

    lock = Lock()

    def execute(self, context):
        # from . import importb3d
        # t1 = None
        # t2 = None

        evens = [cn for i,cn in enumerate(self.files) if i%2==0]
        odds = [cn for i,cn in enumerate(self.files) if i%2==1]


        t1 = Thread(target=thread_import_b3d, args=(self, evens, context))
        t2 = Thread(target=thread_import_b3d, args=(self, odds, context))

        tt = time.mktime(datetime.datetime.now().timetuple())

        t1.start()
        t2.start()

        t1.join()
        t2.join()

        # for b3dfile in self.files:
        #     filepath = os.path.join(self.directory, b3dfile.name)

        #     print('Importing file', filepath)
        #     t = time.mktime(datetime.datetime.now().timetuple())
        #     with open(filepath, 'rb') as file:
        #         importb3d.read(file, context, self, filepath)
        #     t = time.mktime(datetime.datetime.now().timetuple()) - t
        #     print('Finished importing in', t, 'seconds')


        tt = time.mktime(datetime.datetime.now().timetuple()) - tt
        print('All imported in', tt, 'seconds')

        return {'FINISHED'}



class ImportWayTxt(bpy.types.Operator, ImportHelper):
    '''Import from txt file format (.txt)'''
    bl_idname = 'import_scene.kotr_way_txt'
    bl_label = 'Import way_txt'

    filename_ext = '.txt'
    filter_glob = StringProperty(default='*.txt', options={'HIDDEN'})

    use_image_search = BoolProperty(name='Image Search',
                        description='Search subdirectories for any associated'\
                                    'images', default=True)

    def execute(self, context):
        from . import importb3d
        print('Importing file', self.filepath)
        t = time.mktime(datetime.datetime.now().timetuple())
        with open(self.filepath, 'r') as file:
            importb3d.readWayTxt(file, context, self, self.filepath)
        t = time.mktime(datetime.datetime.now().timetuple()) - t
        print('Finished importing in', t, 'seconds')
        return {'FINISHED'}


class ExportB3D(bpy.types.Operator, ImportHelper):
    '''Export to B3D file format (.b3d)'''
    bl_idname = 'export_scene.kotr_b3d'
    bl_label = 'Export B3D'

    filename_ext = '.b3d'
    filter_glob = StringProperty(default='*.b3d', options={'HIDDEN'})

    generate_pro_file = BoolProperty(name='Generate .pro file',
                        description='Generate .pro file, which can used'\
                                    'to assembly the resources file', default=False)

    textures_path = StringProperty(
        name="Textures directory",
        default="txr\\",
        )

    def execute(self, context):
        from . import exportb3d
        print('Exporting file', self.filepath)
        t = time.mktime(datetime.datetime.now().timetuple())
        exportb3d.write(self.filepath+'.b3d', context, self, self.filepath, self.generate_pro_file, self.textures_path)
        t = time.mktime(datetime.datetime.now().timetuple()) - t
        print('Finished exporting in', t, 'seconds')
        return {'FINISHED'}


def menu_func_import(self, context):
    self.layout.operator(ImportB3D.bl_idname, text='KOTR B3D (.b3d)')
    self.layout.operator(ImportWayTxt.bl_idname, text='KOTR WAY (.txt)')


def menu_func_export(self, context):
   self.layout.operator(ExportB3D.bl_idname, text='KOTR B3D (.b3d)')

classes = (
    HTImportPreferences,
    ImportB3D,
    ImportWayTxt,
    ExportB3D
)



def register():
    print("registering addon")
    # import importlib
    # for cls in classes:
    #     importlib.reload(cls)
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
    print("unregistering addon")
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)
    for cls in classes:
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
