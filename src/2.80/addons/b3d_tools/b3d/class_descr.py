from email.policy import default
import bpy
import enum

from bpy.props import (StringProperty,
						BoolProperty,
						IntProperty,
						FloatProperty,
						EnumProperty,
						PointerProperty,
                        FloatVectorProperty,
						CollectionProperty
						)

from bpy.types import (Panel,
						Operator,
						PropertyGroup,
						)

from ..common import log

from ..consts import (
	collisionTypeList,
	generatorTypeList,
	b24FlagList,
	BLOCK_TYPE,
	LEVEL_GROUP
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


class ActiveBlock(bpy.types.PropertyGroup):
    name: StringProperty()
    state : BoolProperty()

class FloatBlock(bpy.types.PropertyGroup):
    value: FloatProperty()

class MaskfileBlock(bpy.types.PropertyGroup):
	value: StringProperty()

	is_noload: BoolProperty(default=False)
	is_someint: BoolProperty(default=False)
	someint: IntProperty(default=0)

class TextureBlock(bpy.types.PropertyGroup):
	value: StringProperty()

	is_memfix: BoolProperty(default=False)
	is_noload: BoolProperty(default=False)
	is_bumpcoord: BoolProperty(default=False)
	is_someint: BoolProperty(default=False)
	someint: IntProperty()

class MaterialBlock(bpy.types.PropertyGroup):
	value: StringProperty()

	is_reflect: BoolProperty(default=False)
	reflect: FloatProperty(default=0.0)

	is_specular: BoolProperty(default=False)
	specular: FloatProperty(default=0.0)

	is_transp: BoolProperty(default=False)
	transp: FloatProperty(default=0.0)

	is_rot: BoolProperty(default=False)
	rot: FloatProperty(default=0.0)

	is_col: BoolProperty(default=False)
	col: IntProperty(default=0)

	is_tex: BoolProperty(default=False)
	tex: IntProperty(default=0)

	is_ttx: BoolProperty(default=False)
	ttx: IntProperty(default=0)

	is_itx: BoolProperty(default=False)
	itx: IntProperty(default=0)

	is_att: BoolProperty(default=False)
	att: IntProperty(default=0)

	is_msk: BoolProperty(default=False)
	msk: IntProperty(default=0)

	is_power: BoolProperty(default=False)
	power: IntProperty(default=0)

	is_coord: BoolProperty(default=False)
	coord: IntProperty(default=0)

	is_env: BoolProperty(default=False)
	envId: IntProperty(default=0)
	env: FloatVectorProperty(default=(0.0, 0.0), size=2)

	is_rotPoint: BoolProperty(default=False)
	rotPoint: FloatVectorProperty(default=(0.0, 0.0), size=2)

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
	Normal_Switch = {
		'prop': 'normal_switch',
		'type': fieldType.FLOAT,
		'name': 'Normal switcher',
		'description': '',
		'default': 0.0
	}
	Custom_Normal = {
		'prop': 'custom_normal',
		'type': fieldType.COORD,
		'name': 'Custom normal',
		'description': '',
		'default': (0.0, 0.0, 0.0)
	}


class pvb_35():
	Normal_Switch = {
		'prop': 'normal_switch',
		'type': fieldType.FLOAT,
		'name': 'Normal switcher',
		'description': '',
		'default': 0.0
	}
	Custom_Normal = {
		'prop': 'custom_normal',
		'type': fieldType.COORD,
		'name': 'Custom normal',
		'description': '',
		'default': (0.0, 0.0, 0.0)
	}

class pfb_8():
	Format_Flags = {
		'prop': 'format_flags',
		'type': fieldType.V_FORMAT,
	}
	Unk_Float1 = {
		'prop': 'float1',
		'type': fieldType.FLOAT,
		'name': 'Unk. 1',
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

class pfb_28():
	Format_Flags = {
		'prop': 'format_flags',
		'type': fieldType.V_FORMAT,
	}
	Unk_Float1 = {
		'prop': 'float1',
		'type': fieldType.FLOAT,
		'name': 'Unk. 1',
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


class pfb_35():
	Format_Flags = {
		'prop': 'format_flags',
		'type': fieldType.V_FORMAT,
	}
	Unk_Float1 = {
		'prop': 'float1',
		'type': fieldType.FLOAT,
		'name': 'Unk. 1',
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


class b_common():
	LevelGroup = {
		'prop': LEVEL_GROUP,
		'type': fieldType.INT,
		'name': 'Block group',
		'description': '',
		'default': 0
	}

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
	XYZ = {
		'prop': 'b3d_border_center',
		'group': borderSphereGroup,
		'type': fieldType.COORD,
		'name': 'Block border coord',
		'description': '',
		'default': (0.0, 0.0, 0.0)
	}
	R = {
		'prop': 'b3d_border_rad',
		'group': borderSphereGroup,
		'type': fieldType.RAD,
		'name': 'Block border rad',
		'description': '',
		'default': 0.0
	}
	Set_Bound = {
		'prop': 'b3d_border',
		'group': borderSphereGroup,
		'type': fieldType.SPHERE_EDIT
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

class b_3():
	XYZ = {
		'prop': 'b3d_border_center',
		'group': borderSphereGroup,
		'type': fieldType.COORD,
		'name': 'Block border coord',
		'description': '',
		'default': (0.0, 0.0, 0.0)
	}
	R = {
		'prop': 'b3d_border_rad',
		'group': borderSphereGroup,
		'type': fieldType.RAD,
		'name': 'Block border rad',
		'description': '',
		'default': 0.0
	}
	Set_Bound = {
		'prop': 'b3d_border',
		'group': borderSphereGroup,
		'type': fieldType.SPHERE_EDIT
	}

class b_4():
	XYZ = {
		'prop': 'b3d_border_center',
		'group': borderSphereGroup,
		'type': fieldType.COORD,
		'name': 'Block border coord',
		'description': '',
		'default': (0.0, 0.0, 0.0)
	}
	R = {
		'prop': 'b3d_border_rad',
		'group': borderSphereGroup,
		'type': fieldType.RAD,
		'name': 'Block border rad',
		'description': '',
		'default': 0.0
	}
	Set_Bound = {
		'prop': 'b3d_border',
		'group': borderSphereGroup,
		'type': fieldType.SPHERE_EDIT
	}
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
	XYZ = {
		'prop': 'b3d_border_center',
		'group': borderSphereGroup,
		'type': fieldType.COORD,
		'name': 'Block border coord',
		'description': '',
		'default': (0.0, 0.0, 0.0)
	}
	R = {
		'prop': 'b3d_border_rad',
		'group': borderSphereGroup,
		'type': fieldType.RAD,
		'name': 'Block border rad',
		'description': '',
		'default': 0.0
	}
	Set_Bound = {
		'prop': 'b3d_border',
		'group': borderSphereGroup,
		'type': fieldType.SPHERE_EDIT
	}


class b_6():
	XYZ = {
		'prop': 'b3d_border_center',
		'group': borderSphereGroup,
		'type': fieldType.COORD,
		'name': 'Block border coord',
		'description': '',
		'default': (0.0, 0.0, 0.0)
	}
	R = {
		'prop': 'b3d_border_rad',
		'group': borderSphereGroup,
		'type': fieldType.RAD,
		'name': 'Block border rad',
		'description': '',
		'default': 0.0
	}
	Set_Bound = {
		'prop': 'b3d_border',
		'group': borderSphereGroup,
		'type': fieldType.SPHERE_EDIT
	}
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
	XYZ = {
		'prop': 'b3d_border_center',
		'group': borderSphereGroup,
		'type': fieldType.COORD,
		'name': 'Block border coord',
		'description': '',
		'default': (0.0, 0.0, 0.0)
	}
	R = {
		'prop': 'b3d_border_rad',
		'group': borderSphereGroup,
		'type': fieldType.RAD,
		'name': 'Block border rad',
		'description': '',
		'default': 0.0
	}
	Set_Bound = {
		'prop': 'b3d_border',
		'group': borderSphereGroup,
		'type': fieldType.SPHERE_EDIT
	}
	Name1 = {
		'prop': 'name1',
		'type': fieldType.STRING,
		'name': 'Group name',
		'description': '',
		'default': ''
	}

class b_8():
	XYZ = {
		'prop': 'b3d_border_center',
		'group': borderSphereGroup,
		'type': fieldType.COORD,
		'name': 'Block border coord',
		'description': '',
		'default': (0.0, 0.0, 0.0)
	}
	R = {
		'prop': 'b3d_border_rad',
		'group': borderSphereGroup,
		'type': fieldType.RAD,
		'name': 'Block border rad',
		'description': '',
		'default': 0.0
	}
	Set_Bound = {
		'prop': 'b3d_border',
		'group': borderSphereGroup,
		'type': fieldType.SPHERE_EDIT
	}

class b_9():
	XYZ = {
		'prop': 'b3d_border_center',
		'group': borderSphereGroup,
		'type': fieldType.COORD,
		'name': 'Block border coord',
		'description': '',
		'default': (0.0, 0.0, 0.0)
	}
	R = {
		'prop': 'b3d_border_rad',
		'group': borderSphereGroup,
		'type': fieldType.RAD,
		'name': 'Block border rad',
		'description': '',
		'default': 0.0
	}
	Set_Bound = {
		'prop': 'b3d_border',
		'group': borderSphereGroup,
		'type': fieldType.SPHERE_EDIT
	}
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
	XYZ = {
		'prop': 'b3d_border_center',
		'group': borderSphereGroup,
		'type': fieldType.COORD,
		'name': 'Block border coord',
		'description': '',
		'default': (0.0, 0.0, 0.0)
	}
	R = {
		'prop': 'b3d_border_rad',
		'group': borderSphereGroup,
		'type': fieldType.RAD,
		'name': 'Block border rad',
		'description': '',
		'default': 0.0
	}
	Set_Bound = {
		'prop': 'b3d_border',
		'group': borderSphereGroup,
		'type': fieldType.SPHERE_EDIT
	}
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
	XYZ = {
		'prop': 'b3d_border_center',
		'group': borderSphereGroup,
		'type': fieldType.COORD,
		'name': 'Block border coord',
		'description': '',
		'default': (0.0, 0.0, 0.0)
	}
	R = {
		'prop': 'b3d_border_rad',
		'group': borderSphereGroup,
		'type': fieldType.RAD,
		'name': 'Block border rad',
		'description': '',
		'default': 0.0
	}
	Set_Bound = {
		'prop': 'b3d_border',
		'group': borderSphereGroup,
		'type': fieldType.SPHERE_EDIT
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

class b_12():
	XYZ = {
		'prop': 'b3d_border_center',
		'group': borderSphereGroup,
		'type': fieldType.COORD,
		'name': 'Block border coord',
		'description': '',
		'default': (0.0, 0.0, 0.0)
	}
	R = {
		'prop': 'b3d_border_rad',
		'group': borderSphereGroup,
		'type': fieldType.RAD,
		'name': 'Block border rad',
		'description': '',
		'default': 0.0
	}
	Set_Bound = {
		'prop': 'b3d_border',
		'group': borderSphereGroup,
		'type': fieldType.SPHERE_EDIT
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
	XYZ = {
		'prop': 'b3d_border_center',
		'group': borderSphereGroup,
		'type': fieldType.COORD,
		'name': 'Block border coord',
		'description': '',
		'default': (0.0, 0.0, 0.0)
	}
	R = {
		'prop': 'b3d_border_rad',
		'group': borderSphereGroup,
		'type': fieldType.RAD,
		'name': 'Block border rad',
		'description': '',
		'default': 0.0
	}
	Set_Bound = {
		'prop': 'b3d_border',
		'group': borderSphereGroup,
		'type': fieldType.SPHERE_EDIT
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

class b_14():
	XYZ = {
		'prop': 'b3d_border_center',
		'group': borderSphereGroup,
		'type': fieldType.COORD,
		'name': 'Block border coord',
		'description': '',
		'default': (0.0, 0.0, 0.0)
	}
	R = {
		'prop': 'b3d_border_rad',
		'group': borderSphereGroup,
		'type': fieldType.RAD,
		'name': 'Block border rad',
		'description': '',
		'default': 0.0
	}
	Set_Bound = {
		'prop': 'b3d_border',
		'group': borderSphereGroup,
		'type': fieldType.SPHERE_EDIT
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
	XYZ = {
		'prop': 'b3d_border_center',
		'group': borderSphereGroup,
		'type': fieldType.COORD,
		'name': 'Block border coord',
		'description': '',
		'default': (0.0, 0.0, 0.0)
	}
	R = {
		'prop': 'b3d_border_rad',
		'group': borderSphereGroup,
		'type': fieldType.RAD,
		'name': 'Block border rad',
		'description': '',
		'default': 0.0
	}
	Set_Bound = {
		'prop': 'b3d_border',
		'group': borderSphereGroup,
		'type': fieldType.SPHERE_EDIT
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

class b_16():
	XYZ = {
		'prop': 'b3d_border_center',
		'group': borderSphereGroup,
		'type': fieldType.COORD,
		'name': 'Block border coord',
		'description': '',
		'default': (0.0, 0.0, 0.0)
	}
	R = {
		'prop': 'b3d_border_rad',
		'group': borderSphereGroup,
		'type': fieldType.RAD,
		'name': 'Block border rad',
		'description': '',
		'default': 0.0
	}
	Set_Bound = {
		'prop': 'b3d_border',
		'group': borderSphereGroup,
		'type': fieldType.SPHERE_EDIT
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
	XYZ = {
		'prop': 'b3d_border_center',
		'group': borderSphereGroup,
		'type': fieldType.COORD,
		'name': 'Block border coord',
		'description': '',
		'default': (0.0, 0.0, 0.0)
	}
	R = {
		'prop': 'b3d_border_rad',
		'group': borderSphereGroup,
		'type': fieldType.RAD,
		'name': 'Block border rad',
		'description': '',
		'default': 0.0
	}
	Set_Bound = {
		'prop': 'b3d_border',
		'group': borderSphereGroup,
		'type': fieldType.SPHERE_EDIT
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
	XYZ = {
		'prop': 'b3d_border_center',
		'group': borderSphereGroup,
		'type': fieldType.COORD,
		'name': 'Block border coord',
		'description': '',
		'default': (0.0, 0.0, 0.0)
	}
	R = {
		'prop': 'b3d_border_rad',
		'group': borderSphereGroup,
		'type': fieldType.RAD,
		'name': 'Block border rad',
		'description': '',
		'default': 0.0
	}
	Set_Bound = {
		'prop': 'b3d_border',
		'group': borderSphereGroup,
		'type': fieldType.SPHERE_EDIT
	}
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
	XYZ = {
		'prop': 'b3d_border_center',
		'group': borderSphereGroup,
		'type': fieldType.COORD,
		'name': 'Block border coord',
		'description': '',
		'default': (0.0, 0.0, 0.0)
	}
	R = {
		'prop': 'b3d_border_rad',
		'group': borderSphereGroup,
		'type': fieldType.RAD,
		'name': 'Block border rad',
		'description': '',
		'default': 0.0
	}
	Set_Bound = {
		'prop': 'b3d_border',
		'group': borderSphereGroup,
		'type': fieldType.SPHERE_EDIT
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

class b_21():
	XYZ = {
		'prop': 'b3d_border_center',
		'group': borderSphereGroup,
		'type': fieldType.COORD,
		'name': 'Block border coord',
		'description': '',
		'default': (0.0, 0.0, 0.0)
	}
	R = {
		'prop': 'b3d_border_rad',
		'group': borderSphereGroup,
		'type': fieldType.RAD,
		'name': 'Block border rad',
		'description': '',
		'default': 0.0
	}
	Set_Bound = {
		'prop': 'b3d_border',
		'group': borderSphereGroup,
		'type': fieldType.SPHERE_EDIT
	}
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
	XYZ = {
		'prop': 'b3d_border_center',
		'group': borderSphereGroup,
		'type': fieldType.COORD,
		'name': 'Block border coord',
		'description': '',
		'default': (0.0, 0.0, 0.0)
	}
	R = {
		'prop': 'b3d_border_rad',
		'group': borderSphereGroup,
		'type': fieldType.RAD,
		'name': 'Block border rad',
		'description': '',
		'default': 0.0
	}
	Set_Bound = {
		'prop': 'b3d_border',
		'group': borderSphereGroup,
		'type': fieldType.SPHERE_EDIT
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
	XYZ = {
		'prop': 'b3d_border_center',
		'group': borderSphereGroup,
		'type': fieldType.COORD,
		'name': 'Block border coord',
		'description': '',
		'default': (0.0, 0.0, 0.0)
	}
	R = {
		'prop': 'b3d_border_rad',
		'group': borderSphereGroup,
		'type': fieldType.RAD,
		'name': 'Block border rad',
		'description': '',
		'default': 0.0
	}
	Set_Bound = {
		'prop': 'b3d_border',
		'group': borderSphereGroup,
		'type': fieldType.SPHERE_EDIT
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
	Unk_XYZ3 = {
		'prop': 'unk_XYZ3',
		'type': fieldType.COORD,
		'name': 'Unk. coord 3',
		'description': '',
		'default': (0.0, 0.0, 0.0)
	}

class b_27():
	XYZ = {
		'prop': 'b3d_border_center',
		'group': borderSphereGroup,
		'type': fieldType.COORD,
		'name': 'Block border coord',
		'description': '',
		'default': (0.0, 0.0, 0.0)
	}
	R = {
		'prop': 'b3d_border_rad',
		'group': borderSphereGroup,
		'type': fieldType.RAD,
		'name': 'Block border rad',
		'description': '',
		'default': 0.0
	}
	Set_Bound = {
		'prop': 'b3d_border',
		'group': borderSphereGroup,
		'type': fieldType.SPHERE_EDIT
	}
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
	XYZ = {
		'prop': 'b3d_border_center',
		'group': borderSphereGroup,
		'type': fieldType.COORD,
		'name': 'Block border coord',
		'description': '',
		'default': (0.0, 0.0, 0.0)
	}
	R = {
		'prop': 'b3d_border_rad',
		'group': borderSphereGroup,
		'type': fieldType.RAD,
		'name': 'Block border rad',
		'description': '',
		'default': 0.0
	}
	Set_Bound = {
		'prop': 'b3d_border',
		'group': borderSphereGroup,
		'type': fieldType.SPHERE_EDIT
	}
	Unk_XYZ = {
		'prop': 'unk_XYZ',
		'type': fieldType.COORD,
		'name': 'Sprite center coord',
		'description': '',
		'default': (0.0, 0.0, 0.0)
	}
 	#todo: check

class b_29():
	XYZ = {
		'prop': 'b3d_border_center',
		'group': borderSphereGroup,
		'type': fieldType.COORD,
		'name': 'Block border coord',
		'description': '',
		'default': (0.0, 0.0, 0.0)
	}
	R = {
		'prop': 'b3d_border_rad',
		'group': borderSphereGroup,
		'type': fieldType.RAD,
		'name': 'Block border rad',
		'description': '',
		'default': 0.0
	}
	Set_Bound = {
		'prop': 'b3d_border',
		'group': borderSphereGroup,
		'type': fieldType.SPHERE_EDIT
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
	XYZ = {
		'prop': 'b3d_border_center',
		'group': borderSphereGroup,
		'type': fieldType.COORD,
		'name': 'Block border coord',
		'description': '',
		'default': (0.0, 0.0, 0.0)
	}
	R = {
		'prop': 'b3d_border_rad',
		'group': borderSphereGroup,
		'type': fieldType.RAD,
		'name': 'Block border rad',
		'description': '',
		'default': 0.0
	}
	Set_Bound = {
		'prop': 'b3d_border',
		'group': borderSphereGroup,
		'type': fieldType.SPHERE_EDIT
	}
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
	XYZ = {
		'prop': 'b3d_border_center',
		'group': borderSphereGroup,
		'type': fieldType.COORD,
		'name': 'Block border coord',
		'description': '',
		'default': (0.0, 0.0, 0.0)
	}
	R = {
		'prop': 'b3d_border_rad',
		'group': borderSphereGroup,
		'type': fieldType.RAD,
		'name': 'Block border rad',
		'description': '',
		'default': 0.0
	}
	Set_Bound = {
		'prop': 'b3d_border',
		'group': borderSphereGroup,
		'type': fieldType.SPHERE_EDIT
	}
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
	XYZ = {
		'prop': 'b3d_border_center',
		'group': borderSphereGroup,
		'type': fieldType.COORD,
		'name': 'Block border coord',
		'description': '',
		'default': (0.0, 0.0, 0.0)
	}
	R = {
		'prop': 'b3d_border_rad',
		'group': borderSphereGroup,
		'type': fieldType.RAD,
		'name': 'Block border rad',
		'description': '',
		'default': 0.0
	}
	Set_Bound = {
		'prop': 'b3d_border',
		'group': borderSphereGroup,
		'type': fieldType.SPHERE_EDIT
	}
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
	XYZ = {
		'prop': 'b3d_border_center',
		'group': borderSphereGroup,
		'type': fieldType.COORD,
		'name': 'Block border coord',
		'description': '',
		'default': (0.0, 0.0, 0.0)
	}
	R = {
		'prop': 'b3d_border_rad',
		'group': borderSphereGroup,
		'type': fieldType.RAD,
		'name': 'Block border rad',
		'description': '',
		'default': 0.0
	}
	Set_Bound = {
		'prop': 'b3d_border',
		'group': borderSphereGroup,
		'type': fieldType.SPHERE_EDIT
	}
	UnkInt = {
		'prop': 'int1',
		'type': fieldType.INT,
		'name': 'Unk. 1',
		'description': '',
		'default': 0
	}

class b_35():
	XYZ = {
		'prop': 'b3d_border_center',
		'group': borderSphereGroup,
		'type': fieldType.COORD,
		'name': 'Block border coord',
		'description': '',
		'default': (0.0, 0.0, 0.0)
	}
	R = {
		'prop': 'b3d_border_rad',
		'group': borderSphereGroup,
		'type': fieldType.RAD,
		'name': 'Block border rad',
		'description': '',
		'default': 0.0
	}
	Set_Bound = {
		'prop': 'b3d_border',
		'group': borderSphereGroup,
		'type': fieldType.SPHERE_EDIT
	}
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
	XYZ = {
		'prop': 'b3d_border_center',
		'group': borderSphereGroup,
		'type': fieldType.COORD,
		'name': 'Block border coord',
		'description': '',
		'default': (0.0, 0.0, 0.0)
	}
	R = {
		'prop': 'b3d_border_rad',
		'group': borderSphereGroup,
		'type': fieldType.RAD,
		'name': 'Block border rad',
		'description': '',
		'default': 0.0
	}
	Set_Bound = {
		'prop': 'b3d_border',
		'group': borderSphereGroup,
		'type': fieldType.SPHERE_EDIT
	}
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
	MType = {
		'prop': 'MType',
		'type': fieldType.INT,
		'name': 'Type',
		'description': '',
		'default': 0
	}

class b_37():
	XYZ = {
		'prop': 'b3d_border_center',
		'group': borderSphereGroup,
		'type': fieldType.COORD,
		'name': 'Block border coord',
		'description': '',
		'default': (0.0, 0.0, 0.0)
	}
	R = {
		'prop': 'b3d_border_rad',
		'group': borderSphereGroup,
		'type': fieldType.RAD,
		'name': 'Block border rad',
		'description': '',
		'default': 0.0
	}
	Set_Bound = {
		'prop': 'b3d_border',
		'group': borderSphereGroup,
		'type': fieldType.SPHERE_EDIT
	}
	Name1 = {
		'prop': 'name1',
		'type': fieldType.STRING,
		'name': 'Name 1',
		'description': '',
		'default': ''
	}
	SType = {
		'prop': 'SType',
		'type': fieldType.INT,
		'name': 'Type',
		'description': '',
		'default': 0
	}

class b_39():
	XYZ = {
		'prop': 'b3d_border_center',
		'group': borderSphereGroup,
		'type': fieldType.COORD,
		'name': 'Block border coord',
		'description': '',
		'default': (0.0, 0.0, 0.0)
	}
	R = {
		'prop': 'b3d_border_rad',
		'group': borderSphereGroup,
		'type': fieldType.RAD,
		'name': 'Block border rad',
		'description': '',
		'default': 0.0
	}
	Set_Bound = {
		'prop': 'b3d_border',
		'group': borderSphereGroup,
		'type': fieldType.SPHERE_EDIT
	}
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
	XYZ = {
		'prop': 'b3d_border_center',
		'group': borderSphereGroup,
		'type': fieldType.COORD,
		'name': 'Block border coord',
		'description': '',
		'default': (0.0, 0.0, 0.0)
	}
	R = {
		'prop': 'b3d_border_rad',
		'group': borderSphereGroup,
		'type': fieldType.RAD,
		'name': 'Block border rad',
		'description': '',
		'default': 0.0
	}
	Set_Bound = {
		'prop': 'b3d_border',
		'group': borderSphereGroup,
		'type': fieldType.SPHERE_EDIT
	}
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

def getClassDefByType(blockNum):
	zclass = None
	if blockNum == 1:
		zclass = b_1
	elif blockNum == 2:
		zclass = b_2
	elif blockNum == 3:
		zclass = b_3
	elif blockNum == 4:
		zclass = b_4
	elif blockNum == 5:
		zclass = b_5
	elif blockNum == 6:
		zclass = b_6
	elif blockNum == 7:
		zclass = b_7
	elif blockNum == 8:
		zclass = b_8
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
	return zclass

_classes = (
	ActiveBlock,
	FloatBlock,
	TextureBlock,
	MaskfileBlock,
	MaterialBlock,
	ResBlock
)

def register():
	for cls in _classes:
		bpy.utils.register_class(cls)

def unregister():
	for cls in _classes[::-1]: #reversed
		bpy.utils.unregister_class(cls)
