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
    getColPropertyIndex,
    getColPropertyByName,
    getCurrentRESModule,
    getCurrentRESIndex,
    updateColorPreview
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
#         'R': FloatProperty(
#                 name = "Block border rad",
#                 description = "",

#             )
#     }
# })

class fieldType(enum.Enum):
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

    if not bpy.context.scene.my_tool.isImporting:
        index = getColPropertyIndex(self)
        resModule = getCurrentRESModule()
        if resModule is not None:
            updateColorPreview(resModule, index)

def getImageIndexInModule(field, imageName, colName='id_value'):
    mytool = bpy.context.scene.my_tool

    resModule = getCurrentRESModule()
    if resModule is not None:
        for i, t in enumerate(getattr(resModule, field)): #maskfiles, textures, materials
            id_value = getattr(t, colName)
            if id_value and id_value.name == imageName:
                return i
        return -1

def callback_only_maskfiles(self, context):
    mytool = bpy.context.scene.my_tool

    ind = getCurrentRESIndex()
    if(ind > -1):
        return (getImageIndexInModule('maskfiles', context.name, 'id_msk') > -1)


def callback_only_materials(self, context):
    mytool = bpy.context.scene.my_tool

    ind = getCurrentRESIndex()
    if(ind > -1):
        return (getImageIndexInModule('materials', context.name, 'id_mat') > -1)


def callback_only_textures(self, context):
    mytool = bpy.context.scene.my_tool

    ind = getCurrentRESIndex()
    if(ind > -1):
        return (getImageIndexInModule('textures', context.name, 'id_tex') > -1)


def callback_only_colors(self, context):
    mytool = bpy.context.scene.my_tool
    resModules = mytool.resModules

    resModule = getCurrentRESModule()
    if resModule is not None:
        commonResModule = getColPropertyByName(resModules, 'COMMON')

        nameSplit = context.name.split('_')
        if len(nameSplit) != 3:
            return False
        ind = -1
        module = "COMMON"
        try:
            ind = int(nameSplit[2])
        except:
            return False
        maxInd = len(commonResModule.palette_colors)
        if len(resModule.palette_colors) > 0:
            module = resModule.value
            maxInd = len(resModule.palette_colors)

        return nameSplit[0] == 'col' and nameSplit[1] == module and ind <= maxInd


def setTexInd(self, context):
    index = getImageIndexInModule("textures", self.id_tex.name, 'id_tex')
    if index:
        self.tex = index + 1

def setMskInd(self, context):
    index = getImageIndexInModule("maskfiles", self.id_msk.name, 'id_msk')
    if index:
        self.msk = index + 1

def setMatInd(self, context):
    index = getImageIndexInModule("materials", self.id_att.name, 'id_mat')
    if index:
        self.att = index + 1

def setColInd(self, context):
    if self.id_col is not None:
        nameSplit = self.id_col.name.split('_')
    ind = 0
    try:
        ind = int(nameSplit[2])
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
        update=setColInd
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
        update=setTexInd
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
        update=setMatInd
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
        update=setMskInd
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

borderSphereGroup = 'border_sphere'

# class_descr configuration:

# prop - Required - Key used to save property in Blenders custom properties.
# group - Optional - Used to determine what elements to group together.
# type - Required - Type of the field.
# Type specific configurations

# fieldType.STRING
    # 'name': 'name',
    # 'description': '',
    # 'default': ''

# fieldType.COORD
    # 'name': 'Name',
    # 'description': '',
    # 'default': (0.0, 0.0, 0.0)

# fieldType.INT
    # 'name': 'Name',
    # 'description': '',
    # 'default': 0

# fieldType.FLOAT
    # 'name': 'Name',
    # 'description': '',
    # 'default': 0.0

# fieldType.ENUM - static
    # 'subtype': fieldType.INT,
    # 'name': 'Name',
    # 'description': ''

# fieldType.LIST
    # 'name': 'Name',
    # 'description': ''

# fieldType.ENUM_DYN - dynamic
    # 'subtype': fieldType.STRING
    # 'callback': fieldType.SPACE_NAME,
    # 'name': 'Name',
    # 'description': ''

# fieldType.V_FORMAT

# Used as subtypes
# fieldType.MATERIAL_IND
# fieldType.SPACE_NAME
# fieldType.REFERENCEABLE
# fieldType.ROOM
# fieldType.RES_MODULE

# Custom operators
# fieldType.SPHERE_EDIT


class pvb_8():
    pass
    # disabled for now. Reason: 1) hard to edit
    # todo: analyze more
    # Normal_Switch = {
    #     'prop': 'normal_switch',
    #     'type': fieldType.FLOAT,
    #     'name': 'Normal switcher',
    #     'description': '',
    #     'default': 0.0
    # }
    # Custom_Normal = {
    #     'prop': 'custom_normal',
    #     'type': fieldType.COORD,
    #     'name': 'Custom normal',
    #     'description': '',
    #     'default': (0.0, 0.0, 0.0)
    # }


class pvb_35():
    pass
    # disabled for now. Reason: 1) hard to edit
    # todo: analyze more
    # Normal_Switch = {
    #     'prop': 'normal_switch',
    #     'type': fieldType.FLOAT,
    #     'name': 'Normal switcher',
    #     'description': '',
    #     'default': 0.0
    # }
    # Custom_Normal = {
    #     'prop': 'custom_normal',
    #     'type': fieldType.COORD,
    #     'name': 'Custom normal',
    #     'description': '',
    #     'default': (0.0, 0.0, 0.0)
    # }


class pfb_8():
    Format_Flags = {
        'prop': 'format_flags',
        'type': fieldType.V_FORMAT,
    }
    # disabled for now. Reason: 1) hard to edit 2) more or less static values
    # todo: analyze more
    # Unk_Float1 = {
    #     'prop': 'float1',
    #     'type': fieldType.FLOAT,
    #     'name': 'Unk. 1',
    #     'description': '',
    #     'default': 0.0
    # }
    # Unk_Int2 = {
    #     'prop': 'int2',
    #     'type': fieldType.INT,
    #     'name': 'Unk. 2',
    #     'description': '',
    #     'default': 0
    # }


class pfb_28():
    Format_Flags = {
        'prop': 'format_flags',
        'type': fieldType.V_FORMAT,
    }
    # disabled for now. Reason: 1) hard to edit 2) more or less static values
    # todo: analyze more
    # Unk_Float1 = {
    #     'prop': 'float1',
    #     'type': fieldType.FLOAT,
    #     'name': 'Unk. 1',
    #     'description': '',
    #     'default': 0.0
    # }
    # Unk_Int2 = {
    #     'prop': 'int2',
    #     'type': fieldType.INT,
    #     'name': 'Unk. 2',
    #     'description': '',
    #     'default': 0
    # }


class pfb_35():
    Format_Flags = {
        'prop': 'format_flags',
        'type': fieldType.V_FORMAT,
    }
    # disabled for now. Reason: 1) hard to edit 2) more or less static values
    # todo: analyze more
    # Unk_Float1 = {
    #     'prop': 'float1',
    #     'type': fieldType.FLOAT,
    #     'name': 'Unk. 1',
    #     'description': '',
    #     'default': 0.0
    # }
    # Unk_Int2 = {
    #     'prop': 'int2',
    #     'type': fieldType.INT,
    #     'name': 'Unk. 2',
    #     'description': '',
    #     'default': 0
    # }


class b_1():
    Name1 = {
        'prop': 'name1',
        'type': fieldType.STRING,
        'name': 'Unk. name 1',
        'description': '',
        'default': ''
    }
    Name2 = {
        'prop': 'name2',
        'type': fieldType.STRING,
        'name': 'Unk. name 2',
        'description': '',
        'default': ''
    }


class b_2():
    Unk_XYZ = {
        'prop': 'unk_XYZ',
        'type': fieldType.COORD,
        'name': 'Unk. coord',
        'description': '',
        'default': (0.0, 0.0, 0.0)
    }
    Unk_R = {
        'prop': 'unk_R',
        'type': fieldType.RAD,
        'name': 'Unk. rad',
        'description': '',
        'default': 0.0
    }


class b_4():
    Name1 = {
        'prop': 'name1',
        'type': fieldType.ENUM_DYN,
        'subtype': fieldType.STRING,
        'callback': fieldType.SPACE_NAME,
        'name': 'Place',
        'description': ''
    }
    Name2 = {
        'prop': 'name2',
        'type': fieldType.STRING,
        'name': 'Name 2',
        'description': '',
        'default': ''
    }


class b_5():
    Name1 = {
        'prop': 'name1',
        'type': fieldType.STRING,
        'name': 'Block name',
        'description': '',
        'default': ''
    }


class b_6():
    Name1 = {
        'prop': 'name1',
        'type': fieldType.STRING,
        'name': 'Name 1',
        'description': '',
        'default': ''
    }
    Name2 = {
        'prop': 'name2',
        'type': fieldType.STRING,
        'name': 'Name 2',
        'description': '',
        'default': ''
    }


class b_7():
    Name1 = {
        'prop': 'name1',
        'type': fieldType.STRING,
        'name': 'Group name',
        'description': '',
        'default': ''
    }


class b_9():
    Unk_XYZ = {
        'prop': 'b3d_b9_center',
        'group': 'b9_group',
        'type': fieldType.COORD,
        'name': 'Unk. coord',
        'description': '',
        'default': (0.0, 0.0, 0.0)
    }
    Unk_R = {
        'prop': 'b3d_b9_rad',
        'group': 'b9_group',
        'type': fieldType.RAD,
        'name': 'Unk. rad',
        'description': '',
        'default': 0.0
    }
    Set_B9 = {
        'prop': 'b3d_b9',
        'group': 'b9_group',
        'type': fieldType.SPHERE_EDIT
    }


class b_10():
    LOD_XYZ = {
        'prop': 'b3d_LOD_center',
        'group': 'LOD_group',
        'type': fieldType.COORD,
        'name': 'LOD coord',
        'description': '',
        'default': (0.0, 0.0, 0.0)
    }
    LOD_R = {
        'prop': 'b3d_LOD_rad',
        'group': 'LOD_group',
        'type': fieldType.RAD,
        'name': 'LOD rad',
        'description': '',
        'default': 0.0
    }
    Set_LOD = {
        'prop': 'b3d_LOD',
        'group': 'LOD_group',
        'type': fieldType.SPHERE_EDIT
    }


class b_11():
    Unk_XYZ1 = {
        'prop': 'unk_XYZ1',
        'type': fieldType.COORD,
        'name': 'Unk. coord',
        'description': '',
        'default': (0.0, 0.0, 0.0)
    }
    Unk_XYZ2 = {
        'prop': 'unk_XYZ2',
        'type': fieldType.COORD,
        'name': 'Unk. coord',
        'description': '',
        'default': (0.0, 0.0, 0.0)
    }
    Unk_R1 = {
        'prop': 'unk_R1',
        'type': fieldType.RAD,
        'name': 'Unk. rad',
        'description': '',
        'default': 0.0
    }
    Unk_R2 = {
        'prop': 'unk_R1',
        'type': fieldType.RAD,
        'name': 'Unk. rad',
        'description': '',
        'default': 0.0
    }


class b_12():
    Unk_XYZ = {
        'prop': 'unk_XYZ',
        'type': fieldType.COORD,
        'name': 'Unk. coord',
        'description': '',
        'default': (0.0, 0.0, 0.0)
    }
    Unk_R = {
        'prop': 'unk_R',
        'type': fieldType.RAD,
        'name': 'Unk. rad',
        'description': '',
        'default': 0.0
    }
    Unk_Int1 = {
        'prop': 'int1',
        'type': fieldType.INT,
        'name': 'Unk. 1',
        'description': '',
        'default': 0
    }
    Unk_Int2 = {
        'prop': 'int2',
        'type': fieldType.INT,
        'name': 'Unk. 2',
        'description': '',
        'default': 0
    }
    Unk_List = {
        'prop': 'list1',
        'type': fieldType.LIST,
        'name': 'Unk. params',
        'description': '',
    }


class b_13():
    Unk_Int1 = {
        'prop': 'int1',
        'type': fieldType.INT,
        'name': 'Unk. 1',
        'description': '',
        'default': 0
    }
    Unk_Int2 = {
        'prop': 'int2',
        'type': fieldType.INT,
        'name': 'Unk. 2',
        'description': '',
        'default': 0
    }
    Unk_List = {
        'prop': 'list1',
        'type': fieldType.LIST,
        'name': 'Unk. params',
        'description': '',
    }


class b_14():
    Unk_XYZ = {
        'prop': 'unk_XYZ',
        'type': fieldType.COORD,
        'name': 'Unk. coord',
        'description': '',
        'default': (0.0, 0.0, 0.0)
    }
    Unk_R = {
        'prop': 'unk_R',
        'type': fieldType.RAD,
        'name': 'Unk. rad',
        'description': '',
        'default': 0.0
    }
    Unk_Int1 = {
        'prop': 'int1',
        'type': fieldType.INT,
        'name': 'Unk. 1',
        'description': '',
        'default': 0
    }
    Unk_Int2 = {
        'prop': 'int2',
        'type': fieldType.INT,
        'name': 'Unk. 2',
        'description': '',
        'default': 0
    }
    Unk_List = {
        'prop': 'list1',
        'type': fieldType.LIST,
        'name': 'Unk. params',
        'description': '',
    }


class b_15():
    Unk_Int1 = {
        'prop': 'int1',
        'type': fieldType.INT,
        'name': 'Unk. 1',
        'description': '',
        'default': 0
    }
    Unk_Int2 = {
        'prop': 'int2',
        'type': fieldType.INT,
        'name': 'Unk. 2',
        'description': '',
        'default': 0
    }
    Unk_List = {
        'prop': 'list1',
        'type': fieldType.LIST,
        'name': 'Unk. params',
        'description': '',
    }


class b_16():
    Unk_XYZ1 = {
        'prop': 'unk_XYZ1',
        'type': fieldType.COORD,
        'name': 'Unk. coord 1',
        'description': '',
        'default': (0.0, 0.0, 0.0)
    }
    Unk_XYZ2 = {
        'prop': 'unk_XYZ2',
        'type': fieldType.COORD,
        'name': 'Unk. coord 2',
        'description': '',
        'default': (0.0, 0.0, 0.0)
    }
    Unk_Float1 = {
        'prop': 'float1',
        'type': fieldType.FLOAT,
        'name': 'Unk. 1',
        'description': '',
        'default': 0.0
    }
    Unk_Float2 = {
        'prop': 'float2',
        'type': fieldType.FLOAT,
        'name': 'Unk. 2',
        'description': '',
        'default': 0.0
    }
    Unk_Int1 = {
        'prop': 'int1',
        'type': fieldType.INT,
        'name': 'Unk. 3',
        'description': '',
        'default': 0
    }
    Unk_Int2 = {
        'prop': 'int2',
        'type': fieldType.INT,
        'name': 'Unk. 4',
        'description': '',
        'default': 0
    }
    Unk_List = {
        'prop': 'list1',
        'type': fieldType.LIST,
        'name': 'Unk. params',
        'description': '',
    }


class b_17():
    Unk_XYZ1 = {
        'prop': 'unk_XYZ1',
        'type': fieldType.COORD,
        'name': 'Unk. coord 1',
        'description': '',
        'default': (0.0, 0.0, 0.0)
    }
    Unk_XYZ2 = {
        'prop': 'unk_XYZ2',
        'type': fieldType.COORD,
        'name': 'Unk. coord 2',
        'description': '',
        'default': (0.0, 0.0, 0.0)
    }
    Unk_Float1 = {
        'prop': 'float1',
        'type': fieldType.FLOAT,
        'name': 'Unk. 1',
        'description': '',
        'default': 0.0
    }
    Unk_Float2 = {
        'prop': 'float2',
        'type': fieldType.FLOAT,
        'name': 'Unk. 2',
        'description': '',
        'default': 0.0
    }
    Unk_Int1 = {
        'prop': 'int1',
        'type': fieldType.INT,
        'name': 'Unk. 3',
        'description': '',
        'default': 0
    }
    Unk_Int2 = {
        'prop': 'int2',
        'type': fieldType.INT,
        'name': 'Unk. 4',
        'description': '',
        'default': 0
    }
    Unk_List = {
        'prop': 'list1',
        'type': fieldType.LIST,
        'name': 'Unk. params',
        'description': '',
    }


class b_18():
    Space_Name = {
        'prop': 'space_name',
        'type': fieldType.ENUM_DYN,
        'subtype': fieldType.STRING,
        'callback': fieldType.SPACE_NAME,
        'name': 'Place name (24)',
        'description': ''
    }
    Add_Name = {
        'prop': 'add_name',
        'type': fieldType.ENUM_DYN,
        'subtype': fieldType.STRING,
        'callback': fieldType.REFERENCEABLE,
        'name': 'Transfer block name',
        'description': ''
    }


class b_20():
    Unk_Int1 = {
        'prop': 'int1',
        'type': fieldType.INT,
        'name': 'Unk. 1',
        'description': '',
        'default': 0
    }
    Unk_Int2 = {
        'prop': 'int2',
        'type': fieldType.INT,
        'name': 'Unk. 2',
        'description': '',
        'default': 0
    }
    Unk_List = {
        'prop': 'list1',
        'type': fieldType.LIST,
        'name': 'Unk. params',
        'description': '',
    }


class b_21():
    GroupCnt = {
        'prop': 'group_cnt',
        'type': fieldType.INT,
        'name': 'Group count',
        'description': '',
        'default': 0
    }
    Unk_Int2 = {
        'prop': 'int2',
        'type': fieldType.INT,
        'name': 'Unk. 2',
        'description': '',
        'default': 0
    }


class b_22():
    Unk_XYZ = {
        'prop': 'unk_XYZ',
        'type': fieldType.COORD,
        'name': 'Unk. coord',
        'description': '',
        'default': (0.0, 0.0, 0.0)
    }
    Unk_R = {
        'prop': 'unk_R',
        'type': fieldType.RAD,
        'name': 'Unk. rad',
        'description': '',
        'default': 0.0
    }


class b_23():
    Unk_Int1 = {
        'prop': 'int1',
        'type': fieldType.INT,
        'name': 'Unk. 1',
        'description': '',
        'default': 0
    }
    Surface = {
        'prop': 'CType',
        'type': fieldType.ENUM,
        'subtype': fieldType.INT,
        'name': 'Surface type',
        'description': '',
        'default': 0,
        'items': collisionTypeList
    }
    Unk_List = {
        'prop': 'list1',
        'type': fieldType.LIST,
        'name': 'Unk. params',
        'description': '',
    }


class b_24():
    Flag = {
        'prop': 'flag',
        'type': fieldType.ENUM,
        'subtype': fieldType.INT,
        'name': 'Show flag',
        'description': '',
        'default': 0,
        'items': b24FlagList
    }


class b_25():
    XYZ = {
        'prop': 'XYZ',
        'type': fieldType.COORD,
        'name': 'Unk. coord',
        'description': '',
        'default': (0.0, 0.0, 0.0)
    }
    Name = {
        'prop': 'name',
        'type': fieldType.STRING,
        'name': 'Name 1',
        'description': '',
        'default': ''
    }
    Unk_XYZ1 = {
        'prop': 'unk_XYZ1',
        'type': fieldType.COORD,
        'name': 'Unk. coord 1',
        'description': '',
        'default': (0.0, 0.0, 0.0)
    }
    Unk_XYZ2 = {
        'prop': 'unk_XYZ2',
        'type': fieldType.COORD,
        'name': 'Unk. coord 2',
        'description': '',
        'default': (0.0, 0.0, 0.0)
    }
    Unk_Float1 = {
        'prop': 'float1',
        'type': fieldType.FLOAT,
        'name': 'Unk. 1',
        'description': '',
        'default': 0.0
    }
    Unk_Float2 = {
        'prop': 'float2',
        'type': fieldType.FLOAT,
        'name': 'Unk. 2',
        'description': '',
        'default': 0.0
    }
    Unk_Float3 = {
        'prop': 'float3',
        'type': fieldType.FLOAT,
        'name': 'Unk. 3',
        'description': '',
        'default': 0.0
    }
    Unk_Float4 = {
        'prop': 'float4',
        'type': fieldType.FLOAT,
        'name': 'Unk. 4',
        'description': '',
        'default': 0.0
    }
    Unk_Float5 = {
        'prop': 'float5',
        'type': fieldType.FLOAT,
        'name': 'Unk. 5',
        'description': '',
        'default': 0.0
    }


class b_26():
    Unk_XYZ1 = {
        'prop': 'unk_XYZ1',
        'type': fieldType.COORD,
        'name': 'Unk. coord 1',
        'description': '',
        'default': (0.0, 0.0, 0.0)
    }
    Unk_XYZ2 = {
        'prop': 'unk_XYZ2',
        'type': fieldType.COORD,
        'name': 'Unk. coord 2',
        'description': '',
        'default': (0.0, 0.0, 0.0)
    }
    Unk_XYZ3 = {
        'prop': 'unk_XYZ3',
        'type': fieldType.COORD,
        'name': 'Unk. coord 3',
        'description': '',
        'default': (0.0, 0.0, 0.0)
    }


class b_27():
    Flag = {
        'prop': 'flag',
        'type': fieldType.INT,
        'name': 'Flag',
        'description': '',
        'default': 0
    }
    Unk_XYZ = {
        'prop': 'unk_XYZ',
        'type': fieldType.COORD,
        'name': 'Unk. coord',
        'description': '',
        'default': (0.0, 0.0, 0.0)
    }
    Material = {
        'prop': 'material',
        'type': fieldType.INT,
        'name': 'Material',
        'description': '',
        'default': 0
    }


class b_28():
    Sprite_Center = {
        'prop': 'unk_XYZ',
        'type': fieldType.COORD,
        'name': 'Sprite center coord',
        'description': '',
        'default': (0.0, 0.0, 0.0)
    }
     #todo: check


class b_29():
    Unk_Int1 = {
        'prop': 'int1',
        'type': fieldType.INT,
        'name': 'Unk. 1',
        'description': '',
        'default': 0
    }
    Unk_Int2 = {
        'prop': 'int2',
        'type': fieldType.INT,
        'name': 'Unk. 2',
        'description': '',
        'default': 0
    }
    Unk_XYZ = {
        'prop': 'unk_XYZ',
        'type': fieldType.COORD,
        'name': 'Unk. coord',
        'description': '',
        'default': (0.0, 0.0, 0.0)
    }
    Unk_R = {
        'prop': 'unk_R',
        'type': fieldType.RAD,
        'name': 'Unk. rad',
        'description': '',
        'default': 0.0
    }


class b_30():
    ResModule1 = {
        'prop': '1_roomName_res',
        'group': 'resModule1',
        'type': fieldType.ENUM_DYN,
        'subtype': fieldType.STRING,
        'callback': fieldType.RES_MODULE,
        'name': '1. module',
        'description': '',
        'default': ''
    }
    RoomName1 = {
        'prop': '1_roomName',
        'group': 'resModule1',
        'type': fieldType.ENUM_DYN,
        'subtype': fieldType.STRING,
        'callback': fieldType.ROOM,
        'name': '1. room',
        'description': '',
        'default': ''
    }
    ResModule2 = {
        'prop': '2_roomName_res',
        'group': 'resModule2',
        'type': fieldType.ENUM_DYN,
        'subtype': fieldType.STRING,
        'callback': fieldType.RES_MODULE,
        'name': '2. module',
        'description': '',
        'default': ''
    }
    RoomName2 = {
        'prop': '2_roomName',
        'group': 'resModule2',
        'type': fieldType.ENUM_DYN,
        'subtype': fieldType.STRING,
        'callback': fieldType.ROOM,
        'name': '2. room',
        'description': '',
        'default': ''
    }


class b_31():
    Unk_Int1 = {
        'prop': 'int1',
        'type': fieldType.INT,
        'name': 'Unk. 1',
        'description': '',
        'default': 0
    }
    Unk_XYZ1 = {
        'prop': 'unk_XYZ1',
        'type': fieldType.COORD,
        'name': 'Unk. coord 1',
        'description': '',
        'default': (0.0, 0.0, 0.0)
    }
    Unk_R = {
        'prop': 'unk_R',
        'type': fieldType.RAD,
        'name': 'Unk. rad',
        'description': '',
        'default': 0.0
    }
    Unk_Int2 = {
        'prop': 'int2',
        'type': fieldType.INT,
        'name': 'Unk. 2',
        'description': '',
        'default': 0
    }
    Unk_XYZ2 = {
        'prop': 'unk_XYZ2',
        'type': fieldType.COORD,
        'name': 'Unk. coord 1',
        'description': '',
        'default': (0.0, 0.0, 0.0)
    }
    #todo: check


class b_33():
    Use_Lights = {
        'prop': 'useLight',
        'type': fieldType.INT,
        'name': 'Use lights',
        'description': '',
        'default': 0
    }
    Light_Type = {
        'prop': 'lType',
        'type': fieldType.INT,
        'name': 'Light type',
        'description': '',
        'default': 0
    }
    Flag = {
        'prop': 'flag',
        'type': fieldType.INT,
        'name': 'Flag',
        'description': '',
        'default': 0
    }
    Unk_XYZ1 = {
        'prop': 'unk_XYZ1',
        'type': fieldType.COORD,
        'name': 'Unk. coord 1',
        'description': '',
        'default': (0.0, 0.0, 0.0)
    }
    Unk_XYZ2 = {
        'prop': 'unk_XYZ2',
        'type': fieldType.COORD,
        'name': 'Unk. coord 2',
        'description': '',
        'default': (0.0, 0.0, 0.0)
    }
    Unk_Float1 = {
        'prop': 'float1',
        'type': fieldType.FLOAT,
        'name': 'Unk. 1',
        'description': '',
        'default': 0.0
    }
    Unk_Float2 = {
        'prop': 'float2',
        'type': fieldType.FLOAT,
        'name': 'Unk. 2',
        'description': '',
        'default': 0.0
    }
    Light_R = {
        'prop': 'light_radius',
        'type': fieldType.FLOAT,
        'name': 'Light rad',
        'description': '',
        'default': 0.0
    }
    Intens = {
        'prop': 'intensity',
        'type': fieldType.FLOAT,
        'name': 'Light intensity',
        'description': '',
        'default': 0.0
    }
    Unk_Float3 = {
        'prop': 'float3',
        'type': fieldType.FLOAT,
        'name': 'Unk. 3',
        'description': '',
        'default': 0.0
    }
    Unk_Float4 = {
        'prop': 'float4',
        'type': fieldType.FLOAT,
        'name': 'Unk. 4',
        'description': '',
        'default': 0.0
    }
    RGB = {
        'prop': 'rgb',
        'type': fieldType.COORD,
        'name': 'RGB',
        'description': '',
        'default': (0.0, 0.0, 0.0)
    }


class b_34():
    UnkInt = {
        'prop': 'int1',
        'type': fieldType.INT,
        'name': 'Unk. 1',
        'description': '',
        'default': 0
    }


class b_35():
    MType = {
        'prop': 'mType',
        'type': fieldType.INT,
        'name': 'Type',
        'description': '',
        'default': 0
    }
    TexNum = {
        'prop': 'texnum',
        'type': fieldType.ENUM_DYN,
        'subtype': fieldType.INT,
        'callback': fieldType.MATERIAL_IND,
        'name': 'Texture',
        'description': '',
    }


class b_36():
    Name1 = {
        'prop': 'name1',
        'type': fieldType.STRING,
        'name': 'Name 1',
        'description': '',
        'default': ''
    }
    Name2 = {
        'prop': 'name2',
        'type': fieldType.STRING,
        'name': 'Name 2',
        'description': '',
        'default': ''
    }
    VType = {
        'prop': 'vType',
        'type': fieldType.ENUM,
        'subtype': fieldType.INT,
        'name': 'Vertex type',
        'description': '',
        'default': 2,
        'items': vTypeList
    }


class b_37():
    Name1 = {
        'prop': 'name1',
        'type': fieldType.STRING,
        'name': 'Name 1',
        'description': '',
        'default': ''
    }
    VType = {
        'prop': 'vType',
        'type': fieldType.ENUM,
        'subtype': fieldType.INT,
        'name': 'Vertex type',
        'description': '',
        'default': 2,
        'items': vTypeList
    }


class b_39():
    Color_R = {
        'prop': 'color_r',
        'type': fieldType.INT,
        'name': 'Color rad',
        'description': '',
        'default': 0
    }
    Unk_Float1 = {
        'prop': 'float1',
        'type': fieldType.FLOAT,
        'name': 'Unk. 1',
        'description': '',
        'default': 0.0
    }
    Fog_Start = {
        'prop': 'fog_start',
        'type': fieldType.FLOAT,
        'name': 'Unk. 3',
        'description': '',
        'default': 0.0
    }
    Fog_End = {
        'prop': 'fog_end',
        'type': fieldType.FLOAT,
        'name': 'Unk. 4',
        'description': '',
        'default': 0.0
    }
    Color_Id = {
        'prop': 'color_id',
        'type': fieldType.INT,
        'name': 'Color ID',
        'description': '',
        'default': 0
    }


class b_40():
    Name1 = {
        'prop': 'name1',
        'type': fieldType.STRING,
        'name': 'Name 1',
        'description': '',
        'default': ''
    }
    Name2 = {
        'prop': 'name2',
        'type': fieldType.ENUM,
        'subtype': fieldType.STRING,
        'name': 'Generator type',
        'description': '',
        'default': '$$TreeGenerator',
        'items': generatorTypeList
    }
    Unk_Int1 = {
        'prop': 'int1',
        'type': fieldType.INT,
        'name': 'Unk. 1',
        'description': '',
        'default': 0
    }
    Unk_Int2 = {
        'prop': 'int2',
        'type': fieldType.INT,
        'name': 'Unk. 2',
        'description': '',
        'default': 0
    }
    Unk_List = {
        'prop': 'list1',
        'type': fieldType.LIST,
        'name': 'Unk. params',
        'description': '',
    }

# b_50 - segment
# b_51 - unoriented node
# b_52 - oriented node

class b_50():
    Attr1 = {
        'prop': 'attr1',
        'type': fieldType.INT,
        'name': 'Attr. 1',
        'description': '',
        'default': 0
    }
    Attr2 = {
        'prop': 'attr2',
        'type': fieldType.FLOAT,
        'name': 'Attr. 2',
        'description': '',
        'default': 0
    }
    Attr3 = {
        'prop': 'attr3',
        'type': fieldType.INT,
        'name': 'Attr. 3',
        'description': '',
        'default': 0
    }
    Rten = {
        'prop': 'rten',
        'type': fieldType.STRING,
        'name': 'Unk. name',
        'description': '',
        'default': ''
    }
    Width1 = {
        'prop': 'wdth1',
        'type': fieldType.FLOAT,
        'name': 'Width 1',
        'description': '',
        'default': 0
    }
    Width2 = {
        'prop': 'wdth2',
        'type': fieldType.FLOAT,
        'name': 'Width 2',
        'description': '',
        'default': 0
    }


class b_51():
    Flag = {
        'prop': 'flag',
        'type': fieldType.INT,
        'name': 'Flag',
        'description': '',
        'default': 0
    }


class b_52():
    Flag = {
        'prop': 'flag',
        'type': fieldType.INT,
        'name': 'Flag',
        'description': '',
        'default': 0
    }


def getClassDefByType(blockNum):
    zclass = None
    if blockNum == 1:
        zclass = b_1
    elif blockNum == 2:
        zclass = b_2
    # elif blockNum == 3:
    #     zclass = b_3
    elif blockNum == 4:
        zclass = b_4
    elif blockNum == 5:
        zclass = b_5
    elif blockNum == 6:
        zclass = b_6
    elif blockNum == 7:
        zclass = b_7
    # elif blockNum == 8:
    #     zclass = b_8
    elif blockNum == 9:
        zclass = b_9
    elif blockNum == 10:
        zclass = b_10
    elif blockNum == 11:
        zclass = b_11
    elif blockNum == 12:
        zclass = b_12
    elif blockNum == 13:
        zclass = b_13
    elif blockNum == 14:
        zclass = b_14
    elif blockNum == 15:
        zclass = b_15
    elif blockNum == 16:
        zclass = b_16
    elif blockNum == 17:
        zclass = b_17
    elif blockNum == 18:
        zclass = b_18
    elif blockNum == 20:
        zclass = b_20
    elif blockNum == 21:
        zclass = b_21
    elif blockNum == 22:
        zclass = b_22
    elif blockNum == 23:
        zclass = b_23
    elif blockNum == 24:
        zclass = b_24
    elif blockNum == 25:
        zclass = b_25
    elif blockNum == 26:
        zclass = b_26
    elif blockNum == 27:
        zclass = b_27
    elif blockNum == 28:
        zclass = b_28
    elif blockNum == 29:
        zclass = b_29
    elif blockNum == 30:
        zclass = b_30
    elif blockNum == 31:
        zclass = b_31
    elif blockNum == 33:
        zclass = b_33
    elif blockNum == 34:
        zclass = b_34
    elif blockNum == 35:
        zclass = b_35
    elif blockNum == 36:
        zclass = b_36
    elif blockNum == 37:
        zclass = b_37
    elif blockNum == 39:
        zclass = b_39
    elif blockNum == 40:
        zclass = b_40

    elif blockNum == 50:
        zclass = b_50
    elif blockNum == 51:
        zclass = b_51
    elif blockNum == 52:
        zclass = b_52
    return zclass

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
