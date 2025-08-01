
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

from .class_descr import (
    BoolBlock
)
from . import (
    import_b3d, export_b3d, import_res, export_res
)
from .common import (
    res_modules_callback,
    modules_callback,
    get_col_property_by_name
)
from .ui_utils import (
    draw_multi_select_list
)
from ..common import (
    menus_logger,
    updateLoggers
)
from ..compatibility import (
    make_annotations,
    get_ui_menu,
    get_user_preferences,
    is_before_2_80
)

log = menus_logger

@make_annotations
class HTImportPreferences(AddonPreferences):
    bl_idname = "b3d_tools"

    COMMON_RES_Path = StringProperty(
        name="Common.res path",
        default="",
        subtype='FILE_PATH')

    logger_level = EnumProperty(
        name = "Logger level",
        default = "40", # "ERROR"
        items = [
            ( "10", "DEBUG", "DEBUG"),
            ( "20", "INFO", "INFO"),
            ( "30", "WARNING", "WARNING"),
            ( "40", "ERROR", "ERROR")
        ],
        update=updateLoggers
    )

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.prop(self, 'COMMON_RES_Path', expand=True)
        row = layout.row()
        row.prop(self, 'logger_level', expand=False)



@make_annotations
class ImportRES(Operator, ImportHelper):
    '''Import from RES file format (.res)'''
    bl_idname = 'kotr_b3d.import_res'
    bl_label = 'Import RES'

    filename_ext = ['.res', '.rmp']

    files = CollectionProperty(
        type=OperatorFileListElement,
        options={'HIDDEN', 'SKIP_SAVE'},
    )

    directory = StringProperty(maxlen=1024, subtype='FILE_PATH', options={'HIDDEN', 'SKIP_SAVE'})

    filter_glob = StringProperty(default='*.res;*.rmp', options={'HIDDEN'})

    to_import_textures = BoolProperty(name='Import textures',
                    description='Import textures', default=True, options={'HIDDEN'})

    to_unpack_res = BoolProperty(name='Unpack .res archive',
                    description='Unpack seleted .res archive.', default=True)

    to_convert_txr = BoolProperty(name='Convert .txr to .tga',
                    description='Convert .txr|.msk from unpacked .res to .tga', default=True)

    to_reload_common_res = BoolProperty(name='Reload common.res(HT2)',
                    description='Imports/Reloads resources from common.res', default=False)

    res_extension = EnumProperty(
        name="Extension",
        items=[
            ('res', '.RES', '.RES'),
            ('rmp', '.RMP', '.RMP'),
        ],
        default='res'
    )

    textures_format = StringProperty(
        name="Images format",
        description="Loaded images format",
        default="tga",
    )

    def execute(self, context):

        # importing Res
        mytool = bpy.context.scene.my_tool
        res_modules = mytool.res_modules

        #importing COMMON.RES(Hard Truck 2)
        user_prefs = get_user_preferences()
        common_res_path = user_prefs.addons['b3d_tools'].preferences.COMMON_RES_Path
        common_res_module = get_col_property_by_name(res_modules, 'COMMON')

        tt1 = time.mktime(datetime.datetime.now().timetuple())
        if (common_res_module is None or self.to_reload_common_res) and os.path.exists(common_res_path):
            import_res.import_common_dot_res(self, context, common_res_path)
        else:
            self.report({'ERROR'}, "Common.res path is wrong or is not set. Textures weren't imported! Please, set path to Common.res in addon preferences.")

        if self.to_import_textures:
            if is_before_2_80():
                bpy.context.scene.render.engine = 'CYCLES' #Blender render doesnt render in Material and Texture View

            t0 = Thread(target=import_res.import_multiple_res, args=(self, self.files, context))

            t0.start()
            t0.join()

        tt1 = time.mktime(datetime.datetime.now().timetuple()) - tt1
        log.info('All RES imported in {} seconds'.format(tt1))

        return {'FINISHED'}

@make_annotations
class ExportRES(Operator, ExportHelper):
    '''Export into RES file format (.res)'''
    bl_idname = 'kotr_b3d.export_res'
    bl_label = 'Export RES'

    filename_ext = '.res'
    use_filter_folder = True

    directory = StringProperty(maxlen=1024, subtype='DIR_PATH', options={'HIDDEN', 'SKIP_SAVE'})

    filter_glob = StringProperty(default='', options={'HIDDEN'})

    to_merge = BoolProperty(name='Merge into existing .res ',
                    description='Merge selected sections into existing .res file', default=False)

    export_images = BoolProperty(name='Export images',
                    description='To export images from Blender', default=True)

    tmp_folder = StringProperty(
        name="Temp folder",
        description=".tga images will be exported to this folder",
        default="res_export"
    )

    res_sections = CollectionProperty(type=BoolBlock)

    res_modules = CollectionProperty(type=BoolBlock)

    def invoke(self, context, event):
        wm = context.window_manager

        #RES sections
        self.res_sections.clear()
        sections = [
            "PALETTEFILES",
            "MASKFILES",
            "TEXTUREFILES",
            "MATERIALS"
        ]

        for i, section in enumerate(sections):
            item = self.res_sections.add()
            item.name = str(section)
            item.state = False

        # RES modules
        self.res_modules.clear()
        for module in res_modules_callback(self, None):
            item = self.res_modules.add()
            item.name = str(module[0])
            item.state = False

        wm.fileselect_add(self)
        return {"RUNNING_MODAL"}


    def execute(self, context):

        log.info('Importing to folder {}'.format(self.directory))
        t = time.mktime(datetime.datetime.now().timetuple())
        export_res.export_res(context, self, self.directory)
        t = time.mktime(datetime.datetime.now().timetuple()) - t
        log.info('Finished importing in {} seconds'.format(t))

        return {'FINISHED'}


    def draw(self, context):

        layout = self.layout

        layout.label(text="Modules to export:")
        box1 = layout.box()
        # RES modules
        draw_multi_select_list(self, box1, 'res_modules', 1)

        layout.label(text="RES Settings:")
        box2 = layout.box()

        box2.prop(self, "export_images")
        box2.prop(self, "to_merge")
        # box2.prop(self, 'res_extension')

        box2.label(text="Sections to merge:")
        box3 = box2.box()
        col = box3.column()

        # RES sections
        draw_multi_select_list(self, col, 'res_sections', 1)

        if self.to_merge:
            col.enabled = True
        else:
            col.enabled = False

@make_annotations
class ImportB3D(Operator, ImportHelper):
    '''Import from B3D file format (.b3d)'''
    bl_idname = 'kotr_b3d.import_b3d'
    bl_label = 'Import B3D'

    filename_ext = '.b3d'

    files = CollectionProperty(
        type=OperatorFileListElement,
        options={'HIDDEN', 'SKIP_SAVE'},
    )

    directory = StringProperty(maxlen=1024, subtype='FILE_PATH', options={'HIDDEN', 'SKIP_SAVE'})

    filter_glob = StringProperty(default='*.b3d', options={'HIDDEN'})

    to_unpack_res = BoolProperty(name='Unpack .res archive',
                    description='Unpack associated with .b3d fie .res archive. \n'\
                                'NOTE: .res archive must be located in the same folder as .b3d file', default=False)

    to_convert_txr = BoolProperty(name='Convert .txr to .tga',
                    description='Convert .txr|.msk from unpacked .res to .tga', default=False)

    to_import_textures = BoolProperty(name='Import Textures',
                    description='Import textures from unpacked .res archive. \n'\
                                'NOTE: if importing for the first time select previous option too', default=False)

    to_reload_common_res = BoolProperty(name='Reload common.res(HT2)',
                    description='Imports/Reloads resources from common.res', default=False)

    res_extension = EnumProperty(
        name="Extension",
        items=[
            ('res', '.RES', '.RES'),
            ('rmp', '.RMP', '.RMP'),
        ],
        default='res'
    )

    textures_format = StringProperty(
        name="Images format",
        description="Loaded images format",
        default="tga",
    )

    res_location = StringProperty(
        name=".res path",
        description="Path to .res file location. Default: .res file with name and location of imported .b3d",
        default=""
    )

    show_all_blocks = EnumProperty(
        name="Block",
        items=[
            ('0', 'Custom select', 'Custom select'),
            ('1', 'Select all', 'Select all'),
            ('2', 'Select none', 'Select none'),
        ],
        default='1'
    )

    blocks_to_import = CollectionProperty(type=BoolBlock)

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

    def execute(self, context):
        # importing Res

        mytool = bpy.context.scene.my_tool
        res_modules = mytool.res_modules

        #importing COMMON.RES(Hard Truck 2)
        user_prefs = get_user_preferences()
        common_res_path = user_prefs.addons['b3d_tools'].preferences.COMMON_RES_Path
        common_res_module = get_col_property_by_name(res_modules, 'COMMON')

        if (common_res_module is None or self.to_reload_common_res) and self.to_import_textures and os.path.exists(common_res_path):
            import_res.import_common_dot_res(self, context, common_res_path)
        else:
            self.report({'ERROR'}, "Common.res path is wrong or is not set. There might be problems with imported textures! Please, set path to Common.res in addon preferences.")

        # importing other RES modules
        if self.to_import_textures:

            if is_before_2_80():
                bpy.context.scene.render.engine = 'CYCLES' #Blender render doesnt render in Material and Texture View

            t0 = Thread(target=import_res.import_multiple_res, args=(self, self.files, context))

            tt = time.mktime(datetime.datetime.now().timetuple())

            t0.start()
            t0.join()

            tt = time.mktime(datetime.datetime.now().timetuple()) - tt
            log.info('All RES imported in {} seconds'.format(tt))

        # importing B3d
        evens = [cn for i,cn in enumerate(self.files) if i%2==0]
        odds = [cn for i,cn in enumerate(self.files) if i%2==1]


        t1 = Thread(target=import_b3d.thread_import_b3d, args=(self, evens, context))
        t2 = Thread(target=import_b3d.thread_import_b3d, args=(self, odds, context))

        tt = time.mktime(datetime.datetime.now().timetuple())

        t1.start()
        t2.start()

        t1.join()
        t2.join()

        tt = time.mktime(datetime.datetime.now().timetuple()) - tt
        log.info('All B3D imported in {} seconds'.format(tt))
        self.report({'INFO'}, 'B3D imported')

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
        row.prop(self, 'to_reload_common_res')
        row = box1.row()
        row.prop(self, 'res_extension')
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

        draw_multi_select_list(self, box1, 'blocks_to_import', 8)

@make_annotations
class ExportB3D(Operator, ExportHelper):
    '''Export to B3D file format (.b3d)'''
    bl_idname = 'kotr_b3d.export_b3d'
    bl_label = 'Export B3D'

    filename_ext = '.b3d'
    use_filter_folder = True

    directory = StringProperty(maxlen=1024, subtype='DIR_PATH', options={'HIDDEN', 'SKIP_SAVE'})

    filter_glob = StringProperty(default='', options={'HIDDEN'})

    res_modules = CollectionProperty(type=BoolBlock)

    # B3D settings
    partial_export = BoolProperty(name='Partial export',
                    description='Exports node, that is currently selected in outliner', default=False)

    to_export_res = BoolProperty(name='Export associated .res',
                    description='Exports associated .res in the same folder', default=True)


    # RES settings
    to_merge = BoolProperty(name='Merge into existing .res ',
                    description='Merge selected sections into existing .res file', default=False)

    export_images = BoolProperty(name='Export images',
                    description='To export images from Blender', default=True)

    tmp_folder = StringProperty(
        name="Temp folder",
        description=".tga images will be exported to this folder",
        default="res_export"
    )

    res_sections = CollectionProperty(type=BoolBlock)

    def invoke(self, context, event):
        wm = context.window_manager

        # RES sections
        self.res_sections.clear()
        sections = [
            "PALETTEFILES",
            "MASKFILES",
            "TEXTUREFILES",
            "MATERIALS"
        ]

        for i, section in enumerate(sections):
            item = self.res_sections.add()
            item.name = str(section)
            item.state = False

        # RES modules
        self.res_modules.clear()
        for module in modules_callback(self, None):
            item = self.res_modules.add()
            item.name = str(module[0])
            item.state = False

        wm.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        log.info('Exporting to folder {}'.format(self.filepath))
        if self.to_export_res:
            t = time.mktime(datetime.datetime.now().timetuple())
            export_res.export_res(context, self, self.filepath)
            t = time.mktime(datetime.datetime.now().timetuple()) - t
            log.info('Finished exporting RES in {} seconds'.format(t))

        t = time.mktime(datetime.datetime.now().timetuple())
        export_b3d.export_b3d(context, self, self.filepath)
        t = time.mktime(datetime.datetime.now().timetuple()) - t
        log.info('Finished exporting B3D in {} seconds'.format(t))
        self.report({'INFO'}, 'B3D exported')
        return {'FINISHED'}

    def draw(self, context):

        layout = self.layout

        layout.label(text="Modules to export:")
        box1 = layout.box()
        draw_multi_select_list(self, box1, 'res_modules', 1)

        layout.label(text="B3D Settings:")

        box2 = layout.box()

        box2.prop(self, "partial_export")
        box2.prop(self, "to_export_res")

        layout.label(text="RES Settings:")
        box3 = layout.box()

        box3.prop(self, "export_images")
        box3.prop(self, "to_merge")

        box3.label(text="Sections to merge:")
        box4 = box3.box()
        col = box4.column()

        # RES sections
        draw_multi_select_list(self, col, 'res_sections', 1)

        if self.to_merge:
            col.enabled = True
        else:
            col.enabled = False


@make_annotations
class ImportRAW(Operator, ImportHelper):
    '''Import from RAW file format (.raw)'''
    bl_idname = 'kotr_b3d.import_raw'
    bl_label = 'Import RAW'

    filename_ext = '.raw'

    files = CollectionProperty(
        type=OperatorFileListElement,
        options={'HIDDEN', 'SKIP_SAVE'},
    )

    directory = StringProperty(maxlen=1024, subtype='FILE_PATH', options={'HIDDEN', 'SKIP_SAVE'})

    filter_glob = StringProperty(default='*.raw', options={'HIDDEN'})

    def execute(self, context):
        for rawfile in self.files:
            filepath = os.path.join(self.directory, rawfile.name)

            log.info('Importing file {}'.format(filepath))
            t = time.mktime(datetime.datetime.now().timetuple())
            with open(filepath, 'rb') as file:
                import_b3d.import_raw(file, context, self, filepath)
            t = time.mktime(datetime.datetime.now().timetuple()) - t
            log.info('Finished importing in {} seconds'.format(t))

        return {'FINISHED'}

@make_annotations
class ImportWAY(Operator, ImportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "kotr_b3d.import_way"
    bl_label = "Import WAY"

    filename_ext = '.way'

    files = CollectionProperty(
        type=OperatorFileListElement,
        options={'HIDDEN', 'SKIP_SAVE'},
    )

    directory = StringProperty(maxlen=1024, subtype='FILE_PATH', options={'HIDDEN', 'SKIP_SAVE'})

    filter_glob = StringProperty(default='*.way',options={'HIDDEN'})

    def execute(self, context):
        from . import import_way

        tt = time.mktime(datetime.datetime.now().timetuple())
        for wayfile in self.files:
            filepath = os.path.join(self.directory, wayfile.name)
            log.info('Importing file {}'.format(filepath))
            t = time.mktime(datetime.datetime.now().timetuple())
            with open(filepath, 'rb') as file:
                import_way.import_way(file, context, filepath)
            t = time.mktime(datetime.datetime.now().timetuple()) - t
            log.info('Finished importing in {} seconds'.format(t))

        tt = time.mktime(datetime.datetime.now().timetuple()) - tt
        log.info('Finished all importing in {} seconds'.format(t))

        return {'FINISHED'}

@make_annotations
class ExportWAY(Operator, ExportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "kotr_b3d.export_way"
    bl_label = "Export WAY"

    filename_ext = '.way'
    use_filter_folder = True

    directory = StringProperty(maxlen=1024, subtype='DIR_PATH', options={'HIDDEN', 'SKIP_SAVE'})

    filter_glob = StringProperty(default='', options={'HIDDEN'})

    res_modules = CollectionProperty(type=BoolBlock)

    def invoke(self, context, event):
        wm = context.window_manager

        self.res_modules.clear()
        for module in modules_callback(self, None):
            item = self.res_modules.add()
            item.name = str(module[0])
            item.state = False

        wm.fileselect_add(self)
        return {"RUNNING_MODAL"}


    def execute(self, context):
        from . import export_way

        log.info('Exporting to folder {}'.format(self.filepath))
        t = time.mktime(datetime.datetime.now().timetuple())
        export_way.export_way(context, self, self.filepath)
        t = time.mktime(datetime.datetime.now().timetuple()) - t
        log.info('Finished exporting in {} seconds'.format(t))
        self.report({'INFO'}, 'WAY exported')
        return {'FINISHED'}


    def draw(self, context):

        layout = self.layout

        layout.label(text="Modules to export:")
        box1 = layout.box()

        draw_multi_select_list(self, box1, 'res_modules', 1)


class KOTRImportMenu(bpy.types.Menu):
    bl_label = 'KOTR formats'
    bl_idname = 'kotr_b3d.import_menu'

    def draw(self, context):
        layout = self.layout
        layout.operator(ImportRES.bl_idname, text='KOTR RES (.res)')
        layout.operator(ImportRAW.bl_idname, text='KOTR RAW (.raw)')
        layout.operator(ImportWAY.bl_idname, text='KOTR WAY (.way)')
        layout.operator(ImportB3D.bl_idname, text='KOTR B3D (.b3d)')


class KOTRExportMenu(bpy.types.Menu):
    bl_label = 'KOTR formats'
    bl_idname = 'kotr_b3d.export_menu'

    def draw(self, context):
        layout = self.layout
        layout.operator(ExportRES.bl_idname, text='KOTR RES (.res)')
        layout.operator(ExportWAY.bl_idname, text='KOTR WAY (.way)')
        layout.operator(ExportB3D.bl_idname, text='KOTR B3D (.b3d)')
        
def menu_func_import(self, context):
    self.layout.menu(KOTRImportMenu.bl_idname)


def menu_func_export(self, context):
    self.layout.menu(KOTRExportMenu.bl_idname)


_classes = [
    HTImportPreferences,
    KOTRImportMenu,
    KOTRExportMenu,
    ImportRES,
    ExportRES,
    ImportB3D,
    ImportWAY,
    ImportRAW,
    ExportB3D,
    ExportWAY
]


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)
    menu_prefix = get_ui_menu()
    getattr(bpy.types, "{}_file_import".format(menu_prefix)).append(menu_func_import)
    getattr(bpy.types, "{}_file_export".format(menu_prefix)).append(menu_func_export)


def unregister():
    menu_prefix = get_ui_menu()
    getattr(bpy.types, "{}_file_import".format(menu_prefix)).remove(menu_func_import)
    getattr(bpy.types, "{}_file_export".format(menu_prefix)).remove(menu_func_export)
    for cls in _classes[::-1]: #reversed
        bpy.utils.unregister_class(cls)