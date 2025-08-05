
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

from ..compatibility import (
    is_before_2_80
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

        blocktool = context.scene.block_tool
        result = getattr(getattr(blocktool, bname), '{}_enum'.format(pname))
        if subtype == FieldType.INT:
            result = int(result)
        elif subtype == FieldType.FLOAT:
            result = float(result)
        elif subtype == FieldType.STRING:
            result = str(result)

        setattr(
            bpy.context.object,
            '["{}"]'.format(pname),
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
        zclass = BlockClassHandler.block_classes[block_num]
        return zclass

    @staticmethod
    def get_pfb_class_def_by_type(block_num):
        if block_num > 100:
            return None
        zclass = BlockClassHandler.per_face_block_classes[block_num]
        return zclass

    @staticmethod
    def get_pvb_class_def_by_type(block_num):
        if block_num > 100:
            return None
        zclass = BlockClassHandler.per_vertex_block_classes[block_num]
        return zclass

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
                    attributes['__annotations__']["show_{}".format(pname)] = lock_prop

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
                    attributes['__annotations__']["show_{}".format(pname)] = lock_prop

                enum_callback = None
                subtype = attr_class.get_subtype()

                if attr_class.get_callback() == FieldType.SPACE_NAME:
                    enum_callback = spaces_callback
                elif attr_class.get_callback() == FieldType.REFERENCEABLE:
                    enum_callback = referenceables_callback
                elif attr_class.get_callback() == FieldType.MATERIAL_IND:
                    enum_callback = res_materials_callback
                elif attr_class.get_callback() == FieldType.ROOM:
                    enum_callback = rooms_callback(bname, 'ResModule{}'.format(pname[-1:])) # room name number: 1 or 2
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

                    attributes['__annotations__']['{}_switch'.format(pname)] = prop_switch
                    attributes['__annotations__']['{}_enum'.format(pname)] = prop_enum

                    if multiple_edit:
                        attributes['__annotations__']['{}'.format(pname)] = prop

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

                    attributes['__annotations__']['{}_switch'.format(pname)] = prop_switch
                    attributes['__annotations__']['{}_enum'.format(pname)] = prop_enum

                    if multiple_edit:
                        attributes['__annotations__']['{}'.format(pname)] = prop

            elif attr_class.get_block_type() == FieldType.V_FORMAT: # currently only available in vertex edit

                attributes['__annotations__']["show_{}".format(pname)] = lock_prop

                prop0 = BoolProperty(
                    name = 'Raw edit',
                    description = 'Show raw integer',
                    default = False
                )
                attributes['__annotations__']['{}_show_int'.format(pname)] = prop0
                
                prop0 = IntProperty(
                    name = 'Format Raw',
                    description = 'Raw format integer',
                    default = 1
                )
                attributes['__annotations__']['{}_format_raw'.format(pname)] = prop0

                prop1 = BoolProperty(
                    name = 'Triangulation offset',
                    description = 'Order in which vertexes are read depends on that',
                    default = True
                )
                attributes['__annotations__']['{}_triang_offset'.format(pname)] = prop1

                prop2 = BoolProperty(
                    name = 'Use UV',
                    description = 'If active, writes UV during export.',
                    default = True
                )
                attributes['__annotations__']['{}_use_uvs'.format(pname)] = prop2

                prop3 = BoolProperty(
                    name = 'Use normals',
                    description = 'If active, writes normal during export.',
                    default = True
                )
                attributes['__annotations__']['{}_use_normals'.format(pname)] = prop3

                prop4 = BoolProperty(
                    name = 'Normal switch',
                    description = 'If active, use <float> for en(dis)abling normals. If not active use <float vector> for common normals. Is ignored if "Use normals" is inactive',
                    default = True
                )
                attributes['__annotations__']['{}_normal_flag'.format(pname)] = prop4

            elif attr_class.get_block_type() == FieldType.WAY_SEG_FLAGS: 

                if multiple_edit: # lock switches only for multiple edit
                    attributes['__annotations__']["show_{}".format(pname)] = lock_prop

                prop0 = BoolProperty(
                    name = 'Raw edit',
                    description = 'Show flags integer',
                    default = False
                )
                attributes['__annotations__']['{}_show_int'.format(pname)] = prop0

                prop0 = IntProperty(
                    name = 'Segment flags',
                    description = 'Segment flags as integer',
                    default = 1
                )
                attributes['__annotations__']['{}_segment_flags'.format(pname)] = prop0

                prop1 = BoolProperty(
                    name = 'Use curved path',
                    description = 'Path is built using a NURBS curve',
                    default = True
                )
                attributes['__annotations__']['{}_is_curve'.format(pname)] = prop1

                prop2 = BoolProperty(
                    name = 'Use straight path',
                    description = 'Path is built by passing points',
                    default = False
                )
                attributes['__annotations__']['{}_is_path'.format(pname)] = prop2
                
                prop3 = BoolProperty(
                    name = 'One-way right lane',
                    description = 'One-way right-lane path',
                    default = False
                )
                attributes['__annotations__']['{}_is_right_lane'.format(pname)] = prop3
                
                prop4 = BoolProperty(
                    name = 'One-way left lane',
                    description = 'One-way left-lane path',
                    default = False
                )
                attributes['__annotations__']['{}_is_left_lane'.format(pname)] = prop4

                prop5 = BoolProperty(
                    name = 'Fillable path',
                    description = 'Path on minimap is hidden, but filled once traversed',
                    default = False
                )
                attributes['__annotations__']['{}_is_fillable'.format(pname)] = prop5
                
                prop6 = BoolProperty(
                    name = 'Hidden path',
                    description = 'Path on minimap is always hidden',
                    default = False
                )
                attributes['__annotations__']['{}_is_hidden'.format(pname)] = prop6

                prop7 = BoolProperty(
                    name = 'No traffic?',
                    description = 'Traffic isn''t spawning at this path',
                    default = False
                )
                attributes['__annotations__']['{}_no_traffic'.format(pname)] = prop7


        if is_before_2_80():
            attributes = attributes['__annotations__']

        if multiple_edit:
            newclass = type("{}_gen".format(bclass.__name__), (bpy.types.PropertyGroup,), attributes)
        else:
            newclass = type("s_{}_gen".format(bclass.__name__), (bpy.types.PropertyGroup,), attributes)
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
            attributes['__annotations__']['{}_{}'.format(btype, bnum)] = PointerProperty(type=gen_class)
            BlockClassHandler.block_classes_gen.append(gen_class)

            gen_class = BlockClassHandler.create_type_class(bclass, False)
            attributes['__annotations__']['s_{}_{}'.format(btype, bnum)] = PointerProperty(type=gen_class)
            BlockClassHandler.block_classes_gen.append(gen_class)

        for bclass in [bc for bc in BlockClassHandler.per_face_block_classes if bc is not None]:
            bnum = BlockClassHandler.get_block_num_from_bclass(bclass)
            btype = BlockClassHandler.PER_FACE_BLOCK

            gen_class = BlockClassHandler.create_type_class(bclass)
            attributes['__annotations__']['{}_{}'.format(btype, bnum)] = PointerProperty(type=gen_class)
            BlockClassHandler.per_face_block_classes_gen.append(gen_class)

        for bclass in [bc for bc in BlockClassHandler.per_vertex_block_classes if bc is not None]:
            bnum = BlockClassHandler.get_block_num_from_bclass(bclass)
            btype = BlockClassHandler.PER_VERTEX_BLOCK

            gen_class = BlockClassHandler.create_type_class(bclass)
            attributes['__annotations__']['{}_{}'.format(btype, bnum)] = PointerProperty(type=gen_class)
            BlockClassHandler.per_vertex_block_classes_gen.append(gen_class)

        if is_before_2_80():
            attributes = attributes['__annotations__']

        return type("BlockSettings", (bpy.types.PropertyGroup,), attributes)

    @staticmethod
    def get_mytool_block_name_by_class(bclass, multiple_class = True):
        bname = ''
        btype = BlockClassHandler.get_block_type_from_bclass(bclass)
        bnum = BlockClassHandler.get_block_num_from_bclass(bclass)
        if btype == 'Blk':
            if multiple_class:
                bname = '{}_{}'.format(BlockClassHandler.BLOCK, bnum)
            else:
                bname = 's_{}_{}'.format(BlockClassHandler.BLOCK, bnum)
        elif btype == 'Pfb':
            bname = '{}_{}'.format(BlockClassHandler.PER_FACE_BLOCK, bnum)
        elif btype == 'Pvb':
            bname = '{}_{}'.format(BlockClassHandler.PER_VERTEX_BLOCK, bnum)

        return [bname, bnum]

    @staticmethod
    def get_mytool_block_name(btype, bnum, multiple_class = False):
        bname = ''
        if btype == 'Blk':
            if multiple_class:
                bname = '{}_{}'.format(BlockClassHandler.BLOCK, bnum)
            else:
                bname = 's_{}_{}'.format(BlockClassHandler.BLOCK, bnum)
        elif btype == 'Pfb':
            bname = '{}_{}'.format(BlockClassHandler.PER_FACE_BLOCK, bnum)
        elif btype == 'Pvb':
            bname = '{}_{}'.format(BlockClassHandler.PER_VERTEX_BLOCK, bnum)

        return bname

BlockSettings = BlockClassHandler.create_block_properties()

def register():
    for cls in BlockClassHandler.block_classes_gen:
        bpy.utils.register_class(cls)
    for cls in BlockClassHandler.per_face_block_classes_gen:
        bpy.utils.register_class(cls)
    for cls in BlockClassHandler.per_vertex_block_classes_gen:
        bpy.utils.register_class(cls)
    bpy.utils.register_class(BlockSettings)
    bpy.types.Scene.block_tool = bpy.props.PointerProperty(type=BlockSettings)

def unregister():
    del bpy.types.Scene.block_tool
    bpy.utils.unregister_class(BlockSettings)
    for cls in BlockClassHandler.per_vertex_block_classes_gen[::-1]: #reversed
        bpy.utils.unregister_class(cls)
    for cls in BlockClassHandler.per_face_block_classes_gen[::-1]: #reversed
        bpy.utils.unregister_class(cls)
    for cls in BlockClassHandler.block_classes_gen[::-1]: #reversed
        bpy.utils.unregister_class(cls)
