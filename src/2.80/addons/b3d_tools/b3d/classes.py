
import bpy

from bpy.props import (StringProperty,
                        BoolProperty,
                        IntProperty,
                        FloatProperty,
                        EnumProperty,
                        PointerProperty,
                        FloatVectorProperty,
                        CollectionProperty
                        )

from .class_descr import (
    FieldType,
    FloatBlock
)

from ..common import (
    classes_logger
)

log = classes_logger

from .class_descr import (
    Blk001,
    Blk002,
    # Blk003,
    Blk004,
    Blk005,
    Blk006,
    Blk007,
    # Blk008,
    Blk009,
    Blk010,
    Blk011,
    Blk012,
    Blk013,
    Blk014,
    Blk015,
    Blk016,
    Blk017,
    Blk018,
    Blk020,
    Blk021,
    Blk022,
    Blk023,
    Blk024,
    Blk025,
    Blk026,
    Blk027,
    Blk028,
    Blk029,
    Blk030,
    Blk031,
    Blk033,
    Blk034,
    Blk035,
    Blk036,
    Blk037,
    Blk039,
    Blk040,

    Pfb008,
    Pfb028,
    Pfb035,
    Pvb008,
    Pvb035,
    # way objs
    Blk050,
    Blk051,
    Blk052
)

from .common import (
    res_materials_callback,
    spaces_callback,
    referenceables_callback,
    rooms_callback,
    modules_callback
)


def set_cust_obj_value(subtype, bname, pname):
    def callback_func(self, context):

        mytool = context.scene.my_tool
        result = getattr(getattr(mytool, bname), f'{pname}_enum')
        if subtype == FieldType.INT:
            result = int(result)
        elif subtype == FieldType.FLOAT:
            result = float(result)
        elif subtype == FieldType.STRING:
            result = str(result)

        setattr(
            bpy.context.object,
            f'["{pname}"]',
            result
        )

    return callback_func

class BlockClassHandler():

    PER_FACE_BLOCK = 'per_face_block'
    PER_VERTEX_BLOCK = 'per_vertex_block'
    BLOCK = 'block'

    block_classes = [
        None, Blk001, Blk002, None, Blk004, Blk005, Blk006, Blk007, None, Blk009,
        Blk010, Blk011, Blk012, Blk013, Blk014, Blk015, Blk016, Blk017, Blk018, None,
        Blk020, Blk021, Blk022, Blk023, Blk024, Blk025, Blk026, Blk027, Blk028, Blk029,
        Blk030, Blk031, None, Blk033, Blk034, Blk035, Blk036, Blk037, None, Blk039,
        Blk040, None, None, None, None, None, None, None, None, None,
        Blk050, Blk051, Blk052, None, None, None, None, None, None, None,
    ]

    per_face_block_classes = [
        None, None, None, None, None, None, None, None, Pfb008, None,
        None, None, None, None, None, None, None, None, None, None,
        None, None, None, None, None, None, None, None, Pfb028, None,
        None, None, None, None, None, Pfb035, None, None, None, None
    ]

    per_vertex_block_classes = [
        None, None, None, None, None, None, None, None, Pvb008, None,
        None, None, None, None, None, None, None, None, None, None,
        None, None, None, None, None, None, None, None, None, None,
        None, None, None, None, None, Pvb035, None, None, None, None
    ]

    block_classes_gen = []
    per_face_block_classes_gen = []
    per_vertex_block_classes_gen = []

    @staticmethod
    def get_block_type_from_bclass(bclass):
        return bclass.__name__[:3]

    @staticmethod
    def get_block_num_from_bclass(bclass):
        return int(bclass.__name__[3:])

    @staticmethod
    def get_class_def_by_type(block_num):
        if block_num > 100:
            return None
        return BlockClassHandler.block_classes[block_num]

    @staticmethod
    def create_type_class(bclass, multiple_edit = True):
        attrs_cls = [obj for obj in bclass.__dict__.keys() if not obj.startswith('__')]

        bname, bnum = BlockClassHandler.get_mytool_block_name_by_class(bclass, multiple_edit)

        attributes = {
            '__annotations__' : {}
        }
        for attr_class_name in attrs_cls:
            attr_class = bclass.__dict__[attr_class_name]

            pname = attr_class.get_prop()
            prop = None

            if multiple_edit: # lock switches only for multiple edit
                lock_prop = BoolProperty(
                    name = "On./Off.",
                    description = "Enable/Disable param for editing",
                    default = True
                )

            if attr_class.get_block_type() == FieldType.STRING \
            or attr_class.get_block_type() == FieldType.COORD \
            or attr_class.get_block_type() == FieldType.RAD \
            or attr_class.get_block_type() == FieldType.FLOAT \
            or attr_class.get_block_type() == FieldType.INT \
            or attr_class.get_block_type() == FieldType.LIST:

                if multiple_edit: # lock switches only for multiple edit
                    attributes['__annotations__']["show_"+pname] = lock_prop

                if attr_class.get_block_type() == FieldType.STRING and multiple_edit:
                    prop = StringProperty(
                        name = attr_class.get_name(),
                        description = attr_class.get_description(),
                        default = attr_class.get_default(),
                        maxlen = 32
                    )

                elif attr_class.get_block_type() == FieldType.COORD and multiple_edit:
                    prop = FloatVectorProperty(
                        name = attr_class.get_name(),
                        description = attr_class.get_description(),
                        default = attr_class.get_default()
                    )

                elif (attr_class.get_block_type() == FieldType.RAD or attr_class.get_block_type() == FieldType.FLOAT) and multiple_edit:
                    prop = FloatProperty(
                        name = attr_class.get_name(),
                        description = attr_class.get_description(),
                        default = attr_class.get_default()
                    )

                elif attr_class.get_block_type() == FieldType.INT and multiple_edit:
                    prop = IntProperty(
                        name = attr_class.get_name(),
                        description = attr_class.get_description(),
                        default = attr_class.get_default()
                    )

                elif attr_class.get_block_type() == FieldType.LIST:
                    prop = CollectionProperty(
                        name = attr_class.get_name(),
                        description = attr_class.get_description(),
                        type = FloatBlock
                    )

                attributes['__annotations__'][pname] = prop

            elif attr_class.get_block_type() == FieldType.ENUM \
            or attr_class.get_block_type() == FieldType.ENUM_DYN:


                if multiple_edit: # lock switches only for multiple edit
                    attributes['__annotations__']["show_"+pname] = lock_prop

                enum_callback = None
                subtype = attr_class.get_subtype()

                if attr_class.get_callback() == FieldType.SPACE_NAME:
                    enum_callback = spaces_callback
                elif attr_class.get_callback() == FieldType.REFERENCEABLE:
                    enum_callback = referenceables_callback
                elif attr_class.get_callback() == FieldType.MATERIAL_IND:
                    enum_callback = res_materials_callback
                elif attr_class.get_callback() == FieldType.ROOM:
                    enum_callback = rooms_callback(bname, f'{pname}_res')
                elif attr_class.get_callback() == FieldType.RES_MODULE:
                    enum_callback = modules_callback

                if attr_class.get_block_type() == FieldType.ENUM:
                    prop = None
                    prop_enum = None
                    prop_switch = None

                    prop_switch = BoolProperty(
                        name = 'Use dropdown',
                        description = 'Dropdown selection',
                        default = False
                    )

                    prop_enum = EnumProperty(
                        name = attr_class.get_name(),
                        description = attr_class.get_description(),
                        items = attr_class.get_items(),
                        default = attr_class.get_default(),
                        update = set_cust_obj_value(subtype, bname, pname)
                    )

                    if multiple_edit:
                        if subtype == FieldType.STRING:
                            prop = StringProperty(
                                name = attr_class.get_name(),
                                description = attr_class.get_description(),
                                default = attr_class.get_default(),
                                maxlen = 32
                            )
                        elif subtype == FieldType.INT:
                            prop = IntProperty(
                                name = attr_class.get_name(),
                                description = attr_class.get_description(),
                                default = attr_class.get_default()
                            )

                    attributes['__annotations__'][f'{pname}_switch'] = prop_switch
                    attributes['__annotations__'][f'{pname}_enum'] = prop_enum

                    if multiple_edit:
                        attributes['__annotations__'][f'{pname}'] = prop

                elif attr_class.get_block_type() == FieldType.ENUM_DYN:
                    # prop = None
                    prop_enum = None
                    prop_switch = None

                    prop_switch = BoolProperty(
                        name = 'Use dropdown',
                        description = 'Dropdown selection',
                        default = False
                    )

                    prop_enum = EnumProperty(
                        name = attr_class.get_name(),
                        description = attr_class.get_description(),
                        items = enum_callback,
                        update = set_cust_obj_value(subtype, bname, pname)
                    )


                    if multiple_edit:
                        if subtype == FieldType.STRING:
                            prop = StringProperty(
                                name = attr_class.get_name(),
                                description = attr_class.get_description(),
                                maxlen = 32
                            )
                        elif subtype == FieldType.INT:
                            prop = IntProperty(
                                name = attr_class.get_name(),
                                description = attr_class.get_description()
                            )

                    attributes['__annotations__'][f'{pname}_switch'] = prop_switch
                    attributes['__annotations__'][f'{pname}_enum'] = prop_enum

                    if multiple_edit:
                        attributes['__annotations__'][f'{pname}'] = prop

            elif attr_class.get_block_type() == FieldType.V_FORMAT: # currently only available in vertex edit

                attributes['__annotations__'][f"show_{pname}"] = lock_prop

                prop1 = BoolProperty(
                    name = 'Triangulation offset',
                    description = 'Order in which vertexes are read depends on that',
                    default = True
                )
                attributes['__annotations__'][f'{pname}_triang_offset'] = prop1

                prop2 = BoolProperty(
                    name = 'Use UV',
                    description = 'If active, writes UV during export.',
                    default = True
                )
                attributes['__annotations__'][f'{pname}_use_uvs'] = prop2

                prop3 = BoolProperty(
                    name = 'Use normals',
                    description = 'If active, writes normal during export.',
                    default = True
                )
                attributes['__annotations__'][f'{pname}_use_normals'] = prop3

                prop4 = BoolProperty(
                    name = 'Normal switch',
                    description = 'If active, use <float> for en(dis)abling normals. If not active use <float vector> for common normals. Is ignored if "Use normals" is inactive',
                    default = True
                )
                attributes['__annotations__'][f'{pname}_normal_flag'] = prop4

        if multiple_edit:
            newclass = type(f"{bclass.__name__}_gen", (bpy.types.PropertyGroup,), attributes)
        else:
            newclass = type(f"s_{bclass.__name__}_gen", (bpy.types.PropertyGroup,), attributes)
        return newclass

    @staticmethod
    def create_block_properties():

        BlockClassHandler.block_classes_gen = []
        BlockClassHandler.per_face_block_classes_gen = []
        BlockClassHandler.per_vertex_block_classes_gen = []

        attributes = {
            '__annotations__' : {}
        }

        for bclass in [bc for bc in BlockClassHandler.block_classes if bc is not None]:
            bnum = BlockClassHandler.get_block_num_from_bclass(bclass)
            btype = BlockClassHandler.BLOCK

            gen_class = BlockClassHandler.create_type_class(bclass)
            attributes['__annotations__'][f'{btype}_{bnum}'] = PointerProperty(type=gen_class)
            BlockClassHandler.block_classes_gen.append(gen_class)

            gen_class = BlockClassHandler.create_type_class(bclass, False)
            attributes['__annotations__'][f's_{btype}_{bnum}'] = PointerProperty(type=gen_class)
            BlockClassHandler.block_classes_gen.append(gen_class)

        for bclass in [bc for bc in BlockClassHandler.per_face_block_classes if bc is not None]:
            bnum = BlockClassHandler.get_block_num_from_bclass(bclass)
            btype = BlockClassHandler.PER_FACE_BLOCK

            gen_class = BlockClassHandler.create_type_class(bclass)
            attributes['__annotations__'][f'{btype}_{bnum}'] = PointerProperty(type=gen_class)
            BlockClassHandler.per_face_block_classes_gen.append(gen_class)

        for bclass in [bc for bc in BlockClassHandler.per_vertex_block_classes if bc is not None]:
            bnum = BlockClassHandler.get_block_num_from_bclass(bclass)
            btype = BlockClassHandler.PER_VERTEX_BLOCK

            gen_class = BlockClassHandler.create_type_class(bclass)
            attributes['__annotations__'][f'{btype}_{bnum}'] = PointerProperty(type=gen_class)
            BlockClassHandler.per_vertex_block_classes_gen.append(gen_class)


        return type("BlockSettings", (bpy.types.PropertyGroup,), attributes)

    @staticmethod
    def get_mytool_block_name_by_class(bclass, multiple_class = True):
        bname = ''
        btype = BlockClassHandler.get_block_type_from_bclass(bclass)
        bnum = BlockClassHandler.get_block_num_from_bclass(bclass)
        if btype == 'Blk':
            if multiple_class:
                bname = f'{BlockClassHandler.BLOCK}_{bnum}'
            else:
                bname = f's_{BlockClassHandler.BLOCK}_{bnum}'
        elif btype == 'Pfb':
            bname = f'{BlockClassHandler.PER_FACE_BLOCK}_{bnum}'
        elif btype == 'Pvb':
            bname = f'{BlockClassHandler.PER_VERTEX_BLOCK}_{bnum}'

        return [bname, bnum]

    @staticmethod
    def get_mytool_block_name(btype, bnum, multiple_class = False):
        bname = ''
        if btype == 'Blk':
            if multiple_class:
                bname = f'{BlockClassHandler.BLOCK}_{bnum}'
            else:
                bname = f's_{BlockClassHandler.BLOCK}_{bnum}'
        elif btype == 'Pfb':
            bname = f'{BlockClassHandler.PER_FACE_BLOCK}_{bnum}'
        elif btype == 'Pvb':
            bname = f'{BlockClassHandler.PER_VERTEX_BLOCK}_{bnum}'

        return bname

BlockSettings = BlockClassHandler.create_block_properties()

_classes = [BlockSettings]

def register():
    for cls in BlockClassHandler.block_classes_gen:
        bpy.utils.register_class(cls)
    for cls in BlockClassHandler.per_face_block_classes_gen:
        bpy.utils.register_class(cls)
    for cls in BlockClassHandler.per_vertex_block_classes_gen:
        bpy.utils.register_class(cls)
    for cls in _classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.block_tool = bpy.props.PointerProperty(type=BlockSettings)

def unregister():
    del bpy.types.Scene.block_tool
    for cls in _classes[::-1]:
        bpy.utils.unregister_class(cls)
    for cls in BlockClassHandler.per_vertex_block_classes_gen[::-1]: #reversed
        bpy.utils.unregister_class(cls)
    for cls in BlockClassHandler.per_face_block_classes_gen[::-1]: #reversed
        bpy.utils.unregister_class(cls)
    for cls in BlockClassHandler.block_classes_gen[::-1]: #reversed
        bpy.utils.unregister_class(cls)
