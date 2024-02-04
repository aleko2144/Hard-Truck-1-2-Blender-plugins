import enum
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


from ..consts import (
    collisionTypeList,
    generatorTypeList,
    b24FlagList,
    vTypeList,
    BLOCK_TYPE,
    LEVEL_GROUP
)

from .common import (
    get_col_property_index,
    get_col_property_by_name,
    get_current_res_module,
    get_current_res_index,
    update_color_preview
)

# Dynamic block exmaple
# block_5 = type("block_5", (bpy.types.PropertyGroup,), {
#     '__annotations__': {
#         'name': StringProperty(
#                 name="Block name",
#                 default="",
#                 maxlen=30,
#             ),
#         'XYZ': FloatVectorProperty(
#                 name='Block border coord',
#                 description='',
#                 default=(0.0, 0.0, 0.0)
#             ),
#         'r': FloatProperty(
#                 name = "Block border rad",
#                 description = "",

#             )
#     }
# })

class FieldType(enum.Enum):
    IGNORE = 0
    STRING = 1
    COORD = 2
    RAD = 3
    INT = 4
    FLOAT = 5
    ENUM = 6
    LIST = 7
    ENUM_DYN = 8

    V_FORMAT = 21
    MATERIAL_IND = 22
    SPACE_NAME = 23
    REFERENCEABLE = 24
    ROOM = 25
    RES_MODULE = 26

    SPHERE_EDIT = 41


class BoolBlock(bpy.types.PropertyGroup):
    name: StringProperty()
    state : BoolProperty()


class FloatBlock(bpy.types.PropertyGroup):
    value: FloatProperty()


def update_palette_index(self, context):

    if not bpy.context.scene.my_tool.is_importing:
        index = get_col_property_index(self)
        res_module = get_current_res_module()
        if res_module is not None:
            update_color_preview(res_module, index)

def get_image_index_in_module(field, image_name, col_name='id_value'):

    res_module = get_current_res_module()
    if res_module is not None:
        for i, t in enumerate(getattr(res_module, field)): #maskfiles, textures, materials
            id_value = getattr(t, col_name)
            if id_value and id_value.name == image_name:
                return i
        return -1

def callback_only_maskfiles(self, context):

    ind = get_current_res_index()
    if(ind > -1):
        return (get_image_index_in_module('maskfiles', context.name, 'id_msk') > -1)


def callback_only_materials(self, context):

    ind = get_current_res_index()
    if(ind > -1):
        return (get_image_index_in_module('materials', context.name, 'id_mat') > -1)


def callback_only_textures(self, context):

    ind = get_current_res_index()
    if(ind > -1):
        return (get_image_index_in_module('textures', context.name, 'id_tex') > -1)


def callback_only_colors(self, context):
    mytool = bpy.context.scene.my_tool
    res_modules = mytool.res_modules

    res_module = get_current_res_module()
    if res_module is not None:
        common_res_module = get_col_property_by_name(res_modules, 'COMMON')

        name_split = context.name.split('_')
        if len(name_split) != 3:
            return False
        ind = -1
        module = "COMMON"
        try:
            ind = int(name_split[2])
        except:
            return False
        max_ind = len(common_res_module.palette_colors)
        if len(res_module.palette_colors) > 0:
            module = res_module.value
            max_ind = len(res_module.palette_colors)

        return name_split[0] == 'col' and name_split[1] == module and ind <= max_ind


def set_tex_ind(self, context):
    index = get_image_index_in_module("textures", self.id_tex.name, 'id_tex')
    if index:
        self.tex = index + 1

def set_msk_ind(self, context):
    index = get_image_index_in_module("maskfiles", self.id_msk.name, 'id_msk')
    if index:
        self.msk = index + 1

def set_mat_ind(self, context):
    index = get_image_index_in_module("materials", self.id_att.name, 'id_mat')
    if index:
        self.att = index + 1

def set_col_ind(self, context):
    if self.id_col is not None:
        name_split = self.id_col.name.split('_')
    ind = 0
    try:
        ind = int(name_split[2])
    except:
        pass
    self.col = ind


class PaletteColorBlock(bpy.types.PropertyGroup):
    value: FloatVectorProperty(
        name = 'Palette color',
        subtype = 'COLOR',
        default = (1, 1, 1, 1),
        size = 4,
        min = 0,
        max = 1,
        update = update_palette_index
    )


class MaskfileBlock(bpy.types.PropertyGroup):
    subpath: StringProperty(default = "")
    msk_name: StringProperty(default = "")
    id_msk: PointerProperty(
        name='Image',
        type=bpy.types.Image
    )

    is_noload: BoolProperty(default=False)
    is_someint: BoolProperty(default=False)
    someint: IntProperty(default=0)


class TextureBlock(bpy.types.PropertyGroup):
    subpath: StringProperty(default = "")
    tex_name: StringProperty(default = "")
    id_tex: PointerProperty(
        name='Image',
        type=bpy.types.Image
    )

    has_mipmap: BoolProperty(default=False)
    img_format: EnumProperty(
        name="Image color map",
        default = '0565',
        items=[
            ('0565', "ARGB(0565)", "Color without transparency"),
            ('4444', "ARGB(4444)", "Color with transparency(A)")
        ])

    img_type: EnumProperty(
        name="Image type",
        default='TRUECOLOR',
        items=[
            ('TRUECOLOR', "True-color image", "Store each pixel value"),
            ('COLORMAP', "Color mapped(palette) image", "Store indexes of palette")
        ]
    )

    is_memfix: BoolProperty(default=False)
    is_noload: BoolProperty(default=False)
    is_bumpcoord: BoolProperty(default=False)
    is_someint: BoolProperty(default=False)
    someint: IntProperty()


class MaterialBlock(bpy.types.PropertyGroup):
    mat_name: StringProperty(default = "")
    id_mat: PointerProperty(
        name='Material',
        type=bpy.types.Material
    )

    is_reflect: BoolProperty(default=False)
    reflect: FloatProperty(default=0.0)

    is_specular: BoolProperty(default=False)
    specular: FloatProperty(default=0.0)

    is_transp: BoolProperty(default=False)
    transp: FloatProperty(default=0.0)

    is_rot: BoolProperty(default=False)
    rot: FloatProperty(default=0.0)

    is_col: BoolProperty(default=False)
    col_switch: BoolProperty(
        name = 'Use dropdown',
        description = 'Dropdown selection',
        default = True
    )
    id_col: PointerProperty(
        name='Colors',
        type=bpy.types.Image,
        poll=callback_only_colors,
        update=set_col_ind
    )
    col: IntProperty(default=0)

    is_tex: BoolProperty(default=False)
    tex_type: EnumProperty(
        name="Texture type",
        items=[
            ('tex', "Tex", "Tex"),
            ('ttx', "Ttx", "Ttx"),
            ('itx', "Itx", "Itx"),
        ])
    tex_switch: BoolProperty(
        name = 'Use dropdown',
        description = 'Dropdown selection',
        default = True
    )
    id_tex: PointerProperty(
        name='Texture',
        type=bpy.types.Image,
        poll=callback_only_textures,
        update=set_tex_ind
    )
    tex: IntProperty(default=0)

    is_att: BoolProperty(default=False)
    att_switch: BoolProperty(
        name = 'Use dropdown',
        description = 'Dropdown selection',
        default = True
    )
    id_att: PointerProperty(
        name='Material',
        type=bpy.types.Material,
        poll=callback_only_materials,
        update=set_mat_ind
    )
    att: IntProperty(default=0)

    is_msk: BoolProperty(default=False)
    msk_switch: BoolProperty(
        name = 'Use dropdown',
        description = 'Dropdown selection',
        default = True
    )
    id_msk: PointerProperty(
        name='Maskfile',
        type=bpy.types.Image,
        poll=callback_only_maskfiles,
        update=set_msk_ind
    )
    msk: IntProperty(default=0)

    is_power: BoolProperty(default=False)
    power: IntProperty(default=0)

    is_coord: BoolProperty(default=False)
    coord: IntProperty(default=0)

    is_envId: BoolProperty(default=False)
    envId: IntProperty(default=0)

    is_env: BoolProperty(default=False)
    env: FloatVectorProperty(default=(0.0, 0.0), size=2)

    is_RotPoint: BoolProperty(default=False)
    RotPoint: FloatVectorProperty(default=(0.0, 0.0), size=2)

    is_move: BoolProperty(default=False)
    move: FloatVectorProperty(default=(0.0, 0.0), size=2)

    is_noz: BoolProperty(default=False)
    is_nof: BoolProperty(default=False)
    is_notile: BoolProperty(default=False)
    is_notileu: BoolProperty(default=False)
    is_notilev: BoolProperty(default=False)
    is_alphamirr: BoolProperty(default=False)
    is_bumpcoord: BoolProperty(default=False)
    is_usecol: BoolProperty(default=False)
    is_wave: BoolProperty(default=False)

class ResBlock(bpy.types.PropertyGroup):
    value: StringProperty()
    palette_subpath: StringProperty()
    palette_name: StringProperty()
    palette_colors: CollectionProperty(type=PaletteColorBlock)
    textures: CollectionProperty(type=TextureBlock)
    materials: CollectionProperty(type=MaterialBlock)
    maskfiles: CollectionProperty(type=MaskfileBlock)

# class_descr configuration:

# prop - Required - Key used to save property in Blenders custom properties.
# group - Optional - Used to determine what elements to group together.
# type - Required - Type of the field.
# Type specific configurations

# FieldType.STRING
    # 'name': 'name',
    # 'description': '',
    # 'default': ''

# FieldType.COORD
    # 'name': 'Name',
    # 'description': '',
    # 'default': (0.0, 0.0, 0.0)

# FieldType.INT
    # 'name': 'Name',
    # 'description': '',
    # 'default': 0

# FieldType.FLOAT
    # 'name': 'Name',
    # 'description': '',
    # 'default': 0.0

# FieldType.ENUM - static
    # 'subtype': FieldType.INT,
    # 'name': 'Name',
    # 'description': ''

# FieldType.LIST
    # 'name': 'Name',
    # 'description': ''

# FieldType.ENUM_DYN - dynamic
    # 'subtype': FieldType.STRING
    # 'callback': FieldType.SPACE_NAME,
    # 'name': 'Name',
    # 'description': ''

# FieldType.V_FORMAT

# Used as subtypes
# FieldType.MATERIAL_IND
# FieldType.SPACE_NAME
# FieldType.REFERENCEABLE
# FieldType.ROOM
# FieldType.RES_MODULE

# Custom operators
# FieldType.SPHERE_EDIT


class Pvb008():
    pass
    # disabled for now. Reason: 1) hard to edit
    # todo: analyze more
    # Normal_Switch = {
    #     'prop': 'normal_switch',
    #     'type': FieldType.FLOAT,
    #     'name': 'Normal switcher',
    #     'description': '',
    #     'default': 0.0
    # }
    # Custom_Normal = {
    #     'prop': 'custom_normal',
    #     'type': FieldType.COORD,
    #     'name': 'Custom normal',
    #     'description': '',
    #     'default': (0.0, 0.0, 0.0)
    # }


class Pvb035():
    pass
    # disabled for now. Reason: 1) hard to edit
    # todo: analyze more
    # Normal_Switch = {
    #     'prop': 'normal_switch',
    #     'type': FieldType.FLOAT,
    #     'name': 'Normal switcher',
    #     'description': '',
    #     'default': 0.0
    # }
    # Custom_Normal = {
    #     'prop': 'custom_normal',
    #     'type': FieldType.COORD,
    #     'name': 'Custom normal',
    #     'description': '',
    #     'default': (0.0, 0.0, 0.0)
    # }


class Pfb008():
    Format_Flags = {
        'prop': 'format_flags',
        'type': FieldType.V_FORMAT,
    }
    # disabled for now. Reason: 1) hard to edit 2) more or less static values
    # todo: analyze more
    # Unk_Float1 = {
    #     'prop': 'float1',
    #     'type': FieldType.FLOAT,
    #     'name': 'Unk. 1',
    #     'description': '',
    #     'default': 0.0
    # }
    # Unk_Int2 = {
    #     'prop': 'int2',
    #     'type': FieldType.INT,
    #     'name': 'Unk. 2',
    #     'description': '',
    #     'default': 0
    # }


class Pfb028():
    Format_Flags = {
        'prop': 'format_flags',
        'type': FieldType.V_FORMAT,
    }
    # disabled for now. Reason: 1) hard to edit 2) more or less static values
    # todo: analyze more
    # Unk_Float1 = {
    #     'prop': 'float1',
    #     'type': FieldType.FLOAT,
    #     'name': 'Unk. 1',
    #     'description': '',
    #     'default': 0.0
    # }
    # Unk_Int2 = {
    #     'prop': 'int2',
    #     'type': FieldType.INT,
    #     'name': 'Unk. 2',
    #     'description': '',
    #     'default': 0
    # }


class Pfb035():
    Format_Flags = {
        'prop': 'format_flags',
        'type': FieldType.V_FORMAT,
    }
    # disabled for now. Reason: 1) hard to edit 2) more or less static values
    # todo: analyze more
    # Unk_Float1 = {
    #     'prop': 'float1',
    #     'type': FieldType.FLOAT,
    #     'name': 'Unk. 1',
    #     'description': '',
    #     'default': 0.0
    # }
    # Unk_Int2 = {
    #     'prop': 'int2',
    #     'type': FieldType.INT,
    #     'name': 'Unk. 2',
    #     'description': '',
    #     'default': 0
    # }


class Blk001():
    Name1 = {
        'prop': 'name1',
        'type': FieldType.STRING,
        'name': 'Unk. name 1',
        'description': '',
        'default': ''
    }
    Name2 = {
        'prop': 'name2',
        'type': FieldType.STRING,
        'name': 'Unk. name 2',
        'description': '',
        'default': ''
    }


class Blk002():
    Unk_XYZ = {
        'prop': 'unk_XYZ',
        'type': FieldType.COORD,
        'name': 'Unk. coord',
        'description': '',
        'default': (0.0, 0.0, 0.0)
    }
    Unk_R = {
        'prop': 'unk_R',
        'type': FieldType.RAD,
        'name': 'Unk. rad',
        'description': '',
        'default': 0.0
    }


class Blk004():
    Name1 = {
        'prop': 'name1',
        'type': FieldType.ENUM_DYN,
        'subtype': FieldType.STRING,
        'callback': FieldType.SPACE_NAME,
        'name': 'Place',
        'description': ''
    }
    Name2 = {
        'prop': 'name2',
        'type': FieldType.STRING,
        'name': 'Name 2',
        'description': '',
        'default': ''
    }


class Blk005():
    Name1 = {
        'prop': 'name1',
        'type': FieldType.STRING,
        'name': 'Block name',
        'description': '',
        'default': ''
    }


class Blk006():
    Name1 = {
        'prop': 'name1',
        'type': FieldType.STRING,
        'name': 'Name 1',
        'description': '',
        'default': ''
    }
    Name2 = {
        'prop': 'name2',
        'type': FieldType.STRING,
        'name': 'Name 2',
        'description': '',
        'default': ''
    }


class Blk007():
    Name1 = {
        'prop': 'name1',
        'type': FieldType.STRING,
        'name': 'Group name',
        'description': '',
        'default': ''
    }


class Blk009():
    Unk_XYZ = {
        'prop': 'b3d_b9_center',
        'group': 'b9_group',
        'type': FieldType.COORD,
        'name': 'Unk. coord',
        'description': '',
        'default': (0.0, 0.0, 0.0)
    }
    Unk_R = {
        'prop': 'b3d_b9_rad',
        'group': 'b9_group',
        'type': FieldType.RAD,
        'name': 'Unk. rad',
        'description': '',
        'default': 0.0
    }
    Set_B9 = {
        'prop': 'b3d_b9',
        'group': 'b9_group',
        'type': FieldType.SPHERE_EDIT
    }


class Blk010():
    LOD_XYZ = {
        'prop': 'b3d_LOD_center',
        'group': 'LOD_group',
        'type': FieldType.COORD,
        'name': 'LOD coord',
        'description': '',
        'default': (0.0, 0.0, 0.0)
    }
    LOD_R = {
        'prop': 'b3d_LOD_rad',
        'group': 'LOD_group',
        'type': FieldType.RAD,
        'name': 'LOD rad',
        'description': '',
        'default': 0.0
    }
    Set_LOD = {
        'prop': 'b3d_LOD',
        'group': 'LOD_group',
        'type': FieldType.SPHERE_EDIT
    }


class Blk011():
    Unk_XYZ1 = {
        'prop': 'unk_XYZ1',
        'type': FieldType.COORD,
        'name': 'Unk. coord',
        'description': '',
        'default': (0.0, 0.0, 0.0)
    }
    Unk_XYZ2 = {
        'prop': 'unk_XYZ2',
        'type': FieldType.COORD,
        'name': 'Unk. coord',
        'description': '',
        'default': (0.0, 0.0, 0.0)
    }
    Unk_R1 = {
        'prop': 'unk_R1',
        'type': FieldType.RAD,
        'name': 'Unk. rad',
        'description': '',
        'default': 0.0
    }
    Unk_R2 = {
        'prop': 'unk_R1',
        'type': FieldType.RAD,
        'name': 'Unk. rad',
        'description': '',
        'default': 0.0
    }


class Blk012():
    Unk_XYZ = {
        'prop': 'unk_XYZ',
        'type': FieldType.COORD,
        'name': 'Unk. coord',
        'description': '',
        'default': (0.0, 0.0, 0.0)
    }
    Unk_R = {
        'prop': 'unk_R',
        'type': FieldType.RAD,
        'name': 'Unk. rad',
        'description': '',
        'default': 0.0
    }
    Unk_Int1 = {
        'prop': 'int1',
        'type': FieldType.INT,
        'name': 'Unk. 1',
        'description': '',
        'default': 0
    }
    Unk_Int2 = {
        'prop': 'int2',
        'type': FieldType.INT,
        'name': 'Unk. 2',
        'description': '',
        'default': 0
    }
    Unk_List = {
        'prop': 'list1',
        'type': FieldType.LIST,
        'name': 'Unk. params',
        'description': '',
    }


class Blk013():
    Unk_Int1 = {
        'prop': 'int1',
        'type': FieldType.INT,
        'name': 'Unk. 1',
        'description': '',
        'default': 0
    }
    Unk_Int2 = {
        'prop': 'int2',
        'type': FieldType.INT,
        'name': 'Unk. 2',
        'description': '',
        'default': 0
    }
    Unk_List = {
        'prop': 'list1',
        'type': FieldType.LIST,
        'name': 'Unk. params',
        'description': '',
    }


class Blk014():
    Unk_XYZ = {
        'prop': 'unk_XYZ',
        'type': FieldType.COORD,
        'name': 'Unk. coord',
        'description': '',
        'default': (0.0, 0.0, 0.0)
    }
    Unk_R = {
        'prop': 'unk_R',
        'type': FieldType.RAD,
        'name': 'Unk. rad',
        'description': '',
        'default': 0.0
    }
    Unk_Int1 = {
        'prop': 'int1',
        'type': FieldType.INT,
        'name': 'Unk. 1',
        'description': '',
        'default': 0
    }
    Unk_Int2 = {
        'prop': 'int2',
        'type': FieldType.INT,
        'name': 'Unk. 2',
        'description': '',
        'default': 0
    }
    Unk_List = {
        'prop': 'list1',
        'type': FieldType.LIST,
        'name': 'Unk. params',
        'description': '',
    }


class Blk015():
    Unk_Int1 = {
        'prop': 'int1',
        'type': FieldType.INT,
        'name': 'Unk. 1',
        'description': '',
        'default': 0
    }
    Unk_Int2 = {
        'prop': 'int2',
        'type': FieldType.INT,
        'name': 'Unk. 2',
        'description': '',
        'default': 0
    }
    Unk_List = {
        'prop': 'list1',
        'type': FieldType.LIST,
        'name': 'Unk. params',
        'description': '',
    }


class Blk016():
    Unk_XYZ1 = {
        'prop': 'unk_XYZ1',
        'type': FieldType.COORD,
        'name': 'Unk. coord 1',
        'description': '',
        'default': (0.0, 0.0, 0.0)
    }
    Unk_XYZ2 = {
        'prop': 'unk_XYZ2',
        'type': FieldType.COORD,
        'name': 'Unk. coord 2',
        'description': '',
        'default': (0.0, 0.0, 0.0)
    }
    Unk_Float1 = {
        'prop': 'float1',
        'type': FieldType.FLOAT,
        'name': 'Unk. 1',
        'description': '',
        'default': 0.0
    }
    Unk_Float2 = {
        'prop': 'float2',
        'type': FieldType.FLOAT,
        'name': 'Unk. 2',
        'description': '',
        'default': 0.0
    }
    Unk_Int1 = {
        'prop': 'int1',
        'type': FieldType.INT,
        'name': 'Unk. 3',
        'description': '',
        'default': 0
    }
    Unk_Int2 = {
        'prop': 'int2',
        'type': FieldType.INT,
        'name': 'Unk. 4',
        'description': '',
        'default': 0
    }
    Unk_List = {
        'prop': 'list1',
        'type': FieldType.LIST,
        'name': 'Unk. params',
        'description': '',
    }


class Blk017():
    Unk_XYZ1 = {
        'prop': 'unk_XYZ1',
        'type': FieldType.COORD,
        'name': 'Unk. coord 1',
        'description': '',
        'default': (0.0, 0.0, 0.0)
    }
    Unk_XYZ2 = {
        'prop': 'unk_XYZ2',
        'type': FieldType.COORD,
        'name': 'Unk. coord 2',
        'description': '',
        'default': (0.0, 0.0, 0.0)
    }
    Unk_Float1 = {
        'prop': 'float1',
        'type': FieldType.FLOAT,
        'name': 'Unk. 1',
        'description': '',
        'default': 0.0
    }
    Unk_Float2 = {
        'prop': 'float2',
        'type': FieldType.FLOAT,
        'name': 'Unk. 2',
        'description': '',
        'default': 0.0
    }
    Unk_Int1 = {
        'prop': 'int1',
        'type': FieldType.INT,
        'name': 'Unk. 3',
        'description': '',
        'default': 0
    }
    Unk_Int2 = {
        'prop': 'int2',
        'type': FieldType.INT,
        'name': 'Unk. 4',
        'description': '',
        'default': 0
    }
    Unk_List = {
        'prop': 'list1',
        'type': FieldType.LIST,
        'name': 'Unk. params',
        'description': '',
    }


class Blk018():
    Space_Name = {
        'prop': 'space_name',
        'type': FieldType.ENUM_DYN,
        'subtype': FieldType.STRING,
        'callback': FieldType.SPACE_NAME,
        'name': 'Place name (24)',
        'description': ''
    }
    Add_Name = {
        'prop': 'add_name',
        'type': FieldType.ENUM_DYN,
        'subtype': FieldType.STRING,
        'callback': FieldType.REFERENCEABLE,
        'name': 'Transfer block name',
        'description': ''
    }


class Blk020():
    Unk_Int1 = {
        'prop': 'int1',
        'type': FieldType.INT,
        'name': 'Unk. 1',
        'description': '',
        'default': 0
    }
    Unk_Int2 = {
        'prop': 'int2',
        'type': FieldType.INT,
        'name': 'Unk. 2',
        'description': '',
        'default': 0
    }
    Unk_List = {
        'prop': 'list1',
        'type': FieldType.LIST,
        'name': 'Unk. params',
        'description': '',
    }


class Blk021():
    GroupCnt = {
        'prop': 'group_cnt',
        'type': FieldType.INT,
        'name': 'Group count',
        'description': '',
        'default': 0
    }
    Unk_Int2 = {
        'prop': 'int2',
        'type': FieldType.INT,
        'name': 'Unk. 2',
        'description': '',
        'default': 0
    }


class Blk022():
    Unk_XYZ = {
        'prop': 'unk_XYZ',
        'type': FieldType.COORD,
        'name': 'Unk. coord',
        'description': '',
        'default': (0.0, 0.0, 0.0)
    }
    Unk_R = {
        'prop': 'unk_R',
        'type': FieldType.RAD,
        'name': 'Unk. rad',
        'description': '',
        'default': 0.0
    }


class Blk023():
    Unk_Int1 = {
        'prop': 'int1',
        'type': FieldType.INT,
        'name': 'Unk. 1',
        'description': '',
        'default': 0
    }
    Surface = {
        'prop': 'CType',
        'type': FieldType.ENUM,
        'subtype': FieldType.INT,
        'name': 'Surface type',
        'description': '',
        'default': 0,
        'items': collisionTypeList
    }
    Unk_List = {
        'prop': 'list1',
        'type': FieldType.LIST,
        'name': 'Unk. params',
        'description': '',
    }


class Blk024():
    Flag = {
        'prop': 'flag',
        'type': FieldType.ENUM,
        'subtype': FieldType.INT,
        'name': 'Show flag',
        'description': '',
        'default': 0,
        'items': b24FlagList
    }


class Blk025():
    XYZ = {
        'prop': 'XYZ',
        'type': FieldType.COORD,
        'name': 'Unk. coord',
        'description': '',
        'default': (0.0, 0.0, 0.0)
    }
    Name = {
        'prop': 'name',
        'type': FieldType.STRING,
        'name': 'Name 1',
        'description': '',
        'default': ''
    }
    Unk_XYZ1 = {
        'prop': 'unk_XYZ1',
        'type': FieldType.COORD,
        'name': 'Unk. coord 1',
        'description': '',
        'default': (0.0, 0.0, 0.0)
    }
    Unk_XYZ2 = {
        'prop': 'unk_XYZ2',
        'type': FieldType.COORD,
        'name': 'Unk. coord 2',
        'description': '',
        'default': (0.0, 0.0, 0.0)
    }
    Unk_Float1 = {
        'prop': 'float1',
        'type': FieldType.FLOAT,
        'name': 'Unk. 1',
        'description': '',
        'default': 0.0
    }
    Unk_Float2 = {
        'prop': 'float2',
        'type': FieldType.FLOAT,
        'name': 'Unk. 2',
        'description': '',
        'default': 0.0
    }
    Unk_Float3 = {
        'prop': 'float3',
        'type': FieldType.FLOAT,
        'name': 'Unk. 3',
        'description': '',
        'default': 0.0
    }
    Unk_Float4 = {
        'prop': 'float4',
        'type': FieldType.FLOAT,
        'name': 'Unk. 4',
        'description': '',
        'default': 0.0
    }
    Unk_Float5 = {
        'prop': 'float5',
        'type': FieldType.FLOAT,
        'name': 'Unk. 5',
        'description': '',
        'default': 0.0
    }


class Blk026():
    Unk_XYZ1 = {
        'prop': 'unk_XYZ1',
        'type': FieldType.COORD,
        'name': 'Unk. coord 1',
        'description': '',
        'default': (0.0, 0.0, 0.0)
    }
    Unk_XYZ2 = {
        'prop': 'unk_XYZ2',
        'type': FieldType.COORD,
        'name': 'Unk. coord 2',
        'description': '',
        'default': (0.0, 0.0, 0.0)
    }
    Unk_XYZ3 = {
        'prop': 'unk_XYZ3',
        'type': FieldType.COORD,
        'name': 'Unk. coord 3',
        'description': '',
        'default': (0.0, 0.0, 0.0)
    }


class Blk027():
    Flag = {
        'prop': 'flag',
        'type': FieldType.INT,
        'name': 'Flag',
        'description': '',
        'default': 0
    }
    Unk_XYZ = {
        'prop': 'unk_XYZ',
        'type': FieldType.COORD,
        'name': 'Unk. coord',
        'description': '',
        'default': (0.0, 0.0, 0.0)
    }
    Material = {
        'prop': 'material',
        'type': FieldType.INT,
        'name': 'Material',
        'description': '',
        'default': 0
    }


class Blk028():
    Sprite_Center = {
        'prop': 'unk_XYZ',
        'type': FieldType.COORD,
        'name': 'Sprite center coord',
        'description': '',
        'default': (0.0, 0.0, 0.0)
    }
     #todo: check


class Blk029():
    Unk_Int1 = {
        'prop': 'int1',
        'type': FieldType.INT,
        'name': 'Unk. 1',
        'description': '',
        'default': 0
    }
    Unk_Int2 = {
        'prop': 'int2',
        'type': FieldType.INT,
        'name': 'Unk. 2',
        'description': '',
        'default': 0
    }
    Unk_XYZ = {
        'prop': 'unk_XYZ',
        'type': FieldType.COORD,
        'name': 'Unk. coord',
        'description': '',
        'default': (0.0, 0.0, 0.0)
    }
    Unk_R = {
        'prop': 'unk_R',
        'type': FieldType.RAD,
        'name': 'Unk. rad',
        'description': '',
        'default': 0.0
    }


class Blk030():
    ResModule1 = {
        'prop': '1_roomName_res',
        'group': 'resModule1',
        'type': FieldType.ENUM_DYN,
        'subtype': FieldType.STRING,
        'callback': FieldType.RES_MODULE,
        'name': '1. module',
        'description': '',
        'default': ''
    }
    RoomName1 = {
        'prop': '1_roomName',
        'group': 'resModule1',
        'type': FieldType.ENUM_DYN,
        'subtype': FieldType.STRING,
        'callback': FieldType.ROOM,
        'name': '1. room',
        'description': '',
        'default': ''
    }
    ResModule2 = {
        'prop': '2_roomName_res',
        'group': 'resModule2',
        'type': FieldType.ENUM_DYN,
        'subtype': FieldType.STRING,
        'callback': FieldType.RES_MODULE,
        'name': '2. module',
        'description': '',
        'default': ''
    }
    RoomName2 = {
        'prop': '2_roomName',
        'group': 'resModule2',
        'type': FieldType.ENUM_DYN,
        'subtype': FieldType.STRING,
        'callback': FieldType.ROOM,
        'name': '2. room',
        'description': '',
        'default': ''
    }


class Blk031():
    Unk_Int1 = {
        'prop': 'int1',
        'type': FieldType.INT,
        'name': 'Unk. 1',
        'description': '',
        'default': 0
    }
    Unk_XYZ1 = {
        'prop': 'unk_XYZ1',
        'type': FieldType.COORD,
        'name': 'Unk. coord 1',
        'description': '',
        'default': (0.0, 0.0, 0.0)
    }
    Unk_R = {
        'prop': 'unk_R',
        'type': FieldType.RAD,
        'name': 'Unk. rad',
        'description': '',
        'default': 0.0
    }
    Unk_Int2 = {
        'prop': 'int2',
        'type': FieldType.INT,
        'name': 'Unk. 2',
        'description': '',
        'default': 0
    }
    Unk_XYZ2 = {
        'prop': 'unk_XYZ2',
        'type': FieldType.COORD,
        'name': 'Unk. coord 1',
        'description': '',
        'default': (0.0, 0.0, 0.0)
    }
    #todo: check


class Blk033():
    Use_Lights = {
        'prop': 'useLight',
        'type': FieldType.INT,
        'name': 'Use lights',
        'description': '',
        'default': 0
    }
    Light_Type = {
        'prop': 'lType',
        'type': FieldType.INT,
        'name': 'Light type',
        'description': '',
        'default': 0
    }
    Flag = {
        'prop': 'flag',
        'type': FieldType.INT,
        'name': 'Flag',
        'description': '',
        'default': 0
    }
    Unk_XYZ1 = {
        'prop': 'unk_XYZ1',
        'type': FieldType.COORD,
        'name': 'Unk. coord 1',
        'description': '',
        'default': (0.0, 0.0, 0.0)
    }
    Unk_XYZ2 = {
        'prop': 'unk_XYZ2',
        'type': FieldType.COORD,
        'name': 'Unk. coord 2',
        'description': '',
        'default': (0.0, 0.0, 0.0)
    }
    Unk_Float1 = {
        'prop': 'float1',
        'type': FieldType.FLOAT,
        'name': 'Unk. 1',
        'description': '',
        'default': 0.0
    }
    Unk_Float2 = {
        'prop': 'float2',
        'type': FieldType.FLOAT,
        'name': 'Unk. 2',
        'description': '',
        'default': 0.0
    }
    Light_R = {
        'prop': 'light_radius',
        'type': FieldType.FLOAT,
        'name': 'Light rad',
        'description': '',
        'default': 0.0
    }
    Intens = {
        'prop': 'intensity',
        'type': FieldType.FLOAT,
        'name': 'Light intensity',
        'description': '',
        'default': 0.0
    }
    Unk_Float3 = {
        'prop': 'float3',
        'type': FieldType.FLOAT,
        'name': 'Unk. 3',
        'description': '',
        'default': 0.0
    }
    Unk_Float4 = {
        'prop': 'float4',
        'type': FieldType.FLOAT,
        'name': 'Unk. 4',
        'description': '',
        'default': 0.0
    }
    RGB = {
        'prop': 'rgb',
        'type': FieldType.COORD,
        'name': 'RGB',
        'description': '',
        'default': (0.0, 0.0, 0.0)
    }


class Blk034():
    UnkInt = {
        'prop': 'int1',
        'type': FieldType.INT,
        'name': 'Unk. 1',
        'description': '',
        'default': 0
    }


class Blk035():
    MType = {
        'prop': 'm_type',
        'type': FieldType.INT,
        'name': 'Type',
        'description': '',
        'default': 0
    }
    TexNum = {
        'prop': 'texnum',
        'type': FieldType.ENUM_DYN,
        'subtype': FieldType.INT,
        'callback': FieldType.MATERIAL_IND,
        'name': 'Texture',
        'description': '',
    }


class Blk036():
    Name1 = {
        'prop': 'name1',
        'type': FieldType.STRING,
        'name': 'Name 1',
        'description': '',
        'default': ''
    }
    Name2 = {
        'prop': 'name2',
        'type': FieldType.STRING,
        'name': 'Name 2',
        'description': '',
        'default': ''
    }
    VType = {
        'prop': 'vType',
        'type': FieldType.ENUM,
        'subtype': FieldType.INT,
        'name': 'Vertex type',
        'description': '',
        'default': 2,
        'items': vTypeList
    }


class Blk037():
    Name1 = {
        'prop': 'name1',
        'type': FieldType.STRING,
        'name': 'Name 1',
        'description': '',
        'default': ''
    }
    VType = {
        'prop': 'vType',
        'type': FieldType.ENUM,
        'subtype': FieldType.INT,
        'name': 'Vertex type',
        'description': '',
        'default': 2,
        'items': vTypeList
    }


class Blk039():
    Color_R = {
        'prop': 'color_r',
        'type': FieldType.INT,
        'name': 'Color rad',
        'description': '',
        'default': 0
    }
    Unk_Float1 = {
        'prop': 'float1',
        'type': FieldType.FLOAT,
        'name': 'Unk. 1',
        'description': '',
        'default': 0.0
    }
    Fog_Start = {
        'prop': 'fog_start',
        'type': FieldType.FLOAT,
        'name': 'Unk. 3',
        'description': '',
        'default': 0.0
    }
    Fog_End = {
        'prop': 'fog_end',
        'type': FieldType.FLOAT,
        'name': 'Unk. 4',
        'description': '',
        'default': 0.0
    }
    Color_Id = {
        'prop': 'color_id',
        'type': FieldType.INT,
        'name': 'Color ID',
        'description': '',
        'default': 0
    }


class Blk040():
    Name1 = {
        'prop': 'name1',
        'type': FieldType.STRING,
        'name': 'Name 1',
        'description': '',
        'default': ''
    }
    Name2 = {
        'prop': 'name2',
        'type': FieldType.ENUM,
        'subtype': FieldType.STRING,
        'name': 'Generator type',
        'description': '',
        'default': '$$TreeGenerator',
        'items': generatorTypeList
    }
    Unk_Int1 = {
        'prop': 'int1',
        'type': FieldType.INT,
        'name': 'Unk. 1',
        'description': '',
        'default': 0
    }
    Unk_Int2 = {
        'prop': 'int2',
        'type': FieldType.INT,
        'name': 'Unk. 2',
        'description': '',
        'default': 0
    }
    Unk_List = {
        'prop': 'list1',
        'type': FieldType.LIST,
        'name': 'Unk. params',
        'description': '',
    }

# Blk050 - segment
# Blk051 - unoriented node
# Blk052 - oriented node

class Blk050():
    Attr1 = {
        'prop': 'attr1',
        'type': FieldType.INT,
        'name': 'Attr. 1',
        'description': '',
        'default': 0
    }
    Attr2 = {
        'prop': 'attr2',
        'type': FieldType.FLOAT,
        'name': 'Attr. 2',
        'description': '',
        'default': 0
    }
    Attr3 = {
        'prop': 'attr3',
        'type': FieldType.INT,
        'name': 'Attr. 3',
        'description': '',
        'default': 0
    }
    Rten = {
        'prop': 'rten',
        'type': FieldType.STRING,
        'name': 'Unk. name',
        'description': '',
        'default': ''
    }
    Width1 = {
        'prop': 'wdth1',
        'type': FieldType.FLOAT,
        'name': 'Width 1',
        'description': '',
        'default': 0
    }
    Width2 = {
        'prop': 'wdth2',
        'type': FieldType.FLOAT,
        'name': 'Width 2',
        'description': '',
        'default': 0
    }


class Blk051():
    Flag = {
        'prop': 'flag',
        'type': FieldType.INT,
        'name': 'Flag',
        'description': '',
        'default': 0
    }


class Blk052():
    Flag = {
        'prop': 'flag',
        'type': FieldType.INT,
        'name': 'Flag',
        'description': '',
        'default': 0
    }

block_classes = [
    None, Blk001, Blk002, None, Blk004, Blk005, Blk006, Blk007, None, Blk009,
    Blk010, Blk011, Blk012, Blk013, Blk014, Blk015, Blk016, Blk017, Blk018, None,
    Blk020, Blk021, Blk022, Blk023, Blk024, Blk025, Blk026, Blk027, Blk028, Blk029,
    Blk030, Blk031, None, Blk033, Blk034, Blk035, Blk036, Blk037, None, Blk039,
    Blk040, None, None, None, None, None, None, None, None, None,
    Blk050, Blk051, Blk052, None, None, None, None, None, None, None,
]

_classes = [
    BoolBlock,
    FloatBlock,
    PaletteColorBlock,
    TextureBlock,
    MaskfileBlock,
    MaterialBlock,
    ResBlock
]

def register():
    for cls in _classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in _classes[::-1]: #reversed
        bpy.utils.unregister_class(cls)
