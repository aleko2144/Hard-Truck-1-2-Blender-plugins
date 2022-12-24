
import time
import datetime
from threading import Lock, Thread
import os
import math
import bpy

from bpy.props import (
    StringProperty,
    EnumProperty,
    BoolProperty,
    CollectionProperty,
    FloatProperty
)
from bpy_extras.io_utils import (
    ImportHelper,
    ExportHelper
)
from bpy.types import (
    OperatorFileListElement,
    Operator,
    AddonPreferences
)




class ImportWayTxt(Operator, ImportHelper):
    '''Import from txt file format (.txt)'''
    bl_idname = 'import_scene.kotr_way_txt'
    bl_label = 'Import way_txt'

    filename_ext = '.txt'
    filter_glob = StringProperty(default='*.txt', options={'HIDDEN'})

    use_image_search = BoolProperty(name='Image Search',
                        description='Search subdirectories for any associated'\
                                    'images', default=True)

    def execute(self, context):
        from . import import_b3d
        print('Importing file', self.filepath)
        t = time.mktime(datetime.datetime.now().timetuple())
        with open(self.filepath, 'r') as file:
            import_b3d.readWayTxt(file, context, self, self.filepath)
        t = time.mktime(datetime.datetime.now().timetuple()) - t
        print('Finished importing in', t, 'seconds')
        return {'FINISHED'}


def menu_func_import(self, context):
    self.layout.operator(ImportWayTxt.bl_idname, text='KOTR WAY (.txt)')


def menu_func_export(self, context):
    pass


_classes = (
    ImportWayTxt
)


def register():
    print("registering addon")
    for cls in _classes:
        bpy.utils.register_class(cls)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
    print("unregistering addon")
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)
    for cls in _classes[::-1]: #reversed
        bpy.utils.unregister_class(cls)