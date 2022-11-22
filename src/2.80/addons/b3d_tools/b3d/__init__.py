

# To support reload properly, try to access a package var, if it's there,
# reload everything
if "bpy" in locals():
    print("Reimporting modules!!!")
    import importlib

    importlib.reload(common)
    importlib.reload(classes)
    importlib.reload(importb3d)
    # importlib.reload(exportb3d)
    importlib.reload(imghelp)
    importlib.reload(panel)
else:
    import bpy
    from . import (
        common,
        classes,
        importb3d,
        # exportb3d,
        imghelp,
        panel
    )

import math
from threading import Lock, Thread
import time
import datetime
import os
import bpy
from bpy.props import StringProperty, EnumProperty, BoolProperty, CollectionProperty, FloatProperty
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


class ActiveBlock(bpy.types.PropertyGroup):
    name: StringProperty()
    state : BoolProperty()


class HTImportPreferences(bpy.types.AddonPreferences):
    bl_idname = "b3d_tools"

    COMMON_RES_Path: bpy.props.StringProperty(
        name="Common.res path",
        default="",
        subtype='FILE_PATH')

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.prop(self, 'COMMON_RES_Path', expand=True)

class ImportRAW(bpy.types.Operator, ImportHelper):
    '''Import from RAW file format (.raw)'''
    bl_idname = 'import_scene.kotr_raw'
    bl_label = 'Import RAW'

    filename_ext = '.raw'

    files: CollectionProperty(
        type=bpy.types.OperatorFileListElement,
        options={'HIDDEN', 'SKIP_SAVE'},
    )
    filter_glob : StringProperty(default='*.raw', options={'HIDDEN'})

    directory: StringProperty(maxlen=1024, subtype='FILE_PATH', options={'HIDDEN', 'SKIP_SAVE'})

    def execute(self, context):
        for rawfile in self.files:
            filepath = os.path.join(self.directory, rawfile.name)

            print('Importing file', filepath)
            t = time.mktime(datetime.datetime.now().timetuple())
            with open(filepath, 'rb') as file:
                importb3d.parseRAW(file, context, self, filepath)
            t = time.mktime(datetime.datetime.now().timetuple()) - t
            print('Finished importing in', t, 'seconds')

        return {'FINISHED'}

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

    to_convert_txr : BoolProperty(name='Convert .txr to .tga',
                    description='Convert .txr from unpacked .res to .tga', default=False)

    to_import_textures : BoolProperty(name='Import Textures',
                    description='Import textures from unpacked .res archive. \n'\
                                'NOTE: if importing for the first time select previous option too', default=False)

    textures_format : StringProperty(
        name="Images format",
        description="Loaded images format",
        default="tga",
    )

    res_location : StringProperty(
        name=".res path",
        description="Path to .res file location. Default: .res file with name and location of imported .b3d",
        default=""
    )

    show_all_blocks : EnumProperty(
		name="Block",
		items=[
            ('0', 'Custom select', 'Custom select'),
            ('1', 'Select all', 'Select all'),
            ('2', 'Select none', 'Select none'),
        ]
    )

    blocks_to_import: CollectionProperty(type=ActiveBlock)

    def invoke(self, context, event):
        wm = context.window_manager

        self.blocks_to_import.clear()

        blocks = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,
        # 32,
        33,34,35,36,37,
        # 38,
        39,40]

        for i, block in enumerate(blocks):
            item = self.blocks_to_import.add()
            item.name = str(block)
            item.state = False

        wm.fileselect_add(self)
        return {"RUNNING_MODAL"}


    def thread_import_b3d(self, files, context):
        for b3dfile in files:
            filepath = os.path.join(self.directory, b3dfile.name)

            print('Importing file', filepath)
            t = time.mktime(datetime.datetime.now().timetuple())
            with open(filepath, 'rb') as file:
                importb3d.read(file, context, self, filepath)
            t = time.mktime(datetime.datetime.now().timetuple()) - t
            print('Finished importing in', t, 'seconds')

    def execute(self, context):
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

    def draw(self, context):

        layout = self.layout

        layout.label(text="Main settings:")
        box1 = layout.box()
        row = box1.row()
        row.prop(self, 'to_unpack_res')
        row = box1.row()
        row.prop(self, 'to_convert_txr')
        row = box1.row()
        row.prop(self, 'to_import_textures')
        row = box1.row()
        row.prop(self, 'textures_format')

        layout.label(text="Optional settings:")
        box1 = layout.box()
        row = box1.row()
        row.prop(self, 'res_location')

        layout.label(text="Blocks to import:")
        box1 = layout.box()
        row = box1.row()
        row.prop(self, 'show_all_blocks')
        # props = row.operator(SelectAllBlocksBtn.bl_idname)
        # props.blocks_to_import = self.blocks_to_import
        # props.test = PointerProperty(type=self.blocks_to_import)
        row = box1.row()

        if self.show_all_blocks == '1':
            for block in self.blocks_to_import:
                block.state = True
        elif self.show_all_blocks == '2':
            for block in self.blocks_to_import:
                block.state = False

        i = 0
        perRow = 8
        rowcnt = math.floor(len(self.blocks_to_import)/perRow)
        for j in range(rowcnt):
            row = box1.row()
            for block in self.blocks_to_import[i:i+perRow]:
                row.prop(block, 'state', text=block['name'], toggle=True)
            i+=perRow
        row = box1.row()
        for block in self.blocks_to_import[i:]:
            row.prop(block, 'state', text=block['name'], toggle=True)

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
    self.layout.operator(ImportRAW.bl_idname, text='KOTR RAW (.raw)')
    self.layout.operator(ImportB3D.bl_idname, text='KOTR B3D (.b3d)')
    self.layout.operator(ImportWayTxt.bl_idname, text='KOTR WAY (.txt)')


def menu_func_export(self, context):
   self.layout.operator(ExportB3D.bl_idname, text='KOTR B3D (.b3d)')

_classes = (
    common.SCENE_UL_list,
    HTImportPreferences,
    ImportB3D,
    ImportRAW,
    ImportWayTxt,
    ExportB3D
)



def b3d_register():
    print("registering addon")
    # import importlib
    # for cls in classes:
    #     importlib.reload(cls)
    bpy.utils.register_class(ActiveBlock)
    bpy.utils.register_class(common.FloatBlock)
    for cls in _classes:
        bpy.utils.register_class(cls)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def b3d_unregister():
    print("unregistering addon")
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)
    for cls in _classes:
        bpy.utils.unregister_class(cls)
    bpy.utils.unregister_class(common.FloatBlock)
    bpy.utils.unregister_class(ActiveBlock)
