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
	generatorTypeList
)

# Dynamic block exmaple
# block_5 = type("block_5", (bpy.types.PropertyGroup,), {
#     '__annotations__': {
#         'name': StringProperty(
#                 name="Имя блока",
#                 default="",
#                 maxlen=30,
#             ),
#         'XYZ': FloatVectorProperty(
#                 name='Координаты блока',
#                 description='',
#                 default=(0.0, 0.0, 0.0)
#             ),
#         'R': FloatProperty(
#                 name = "Радиус",
#                 description = "",

#             )
#     }
# })



class fieldType(enum.Enum):
	STRING = 1
	COORD = 2
	RAD = 3
	INT = 4
	FLOAT = 5
	ENUM = 6
	LIST = 7
	V_FORMAT = 8
	MATERIAL_IND = 9
	SPACE_NAME = 10
	REFERENCEABLE = 11


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


class pvb_8():
	Normal_Switch = {
		'prop': 'normal_switch',
		'type': fieldType.FLOAT,
		'name': 'Выключатель нормали',
		'description': '',
		'default': 0.0
	}
	Custom_Normal = {
		'prop': 'custom_normal',
		'type': fieldType.COORD,
		'name': 'Кастомная нормаль',
		'description': '',
		'default': (0.0, 0.0, 0.0)
	}


class pvb_35():
	Normal_Switch = {
		'prop': 'normal_switch',
		'type': fieldType.FLOAT,
		'name': 'Выключатель нормали',
		'description': '',
		'default': 0.0
	}
	Custom_Normal = {
		'prop': 'custom_normal',
		'type': fieldType.COORD,
		'name': 'Кастомная нормаль',
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
		'name': 'Неизвестная 1',
		'description': '',
		'default': 0.0
	}
	Unk_Int2 = {
		'prop': 'int2',
		'type': fieldType.INT,
		'name': 'Неизвестная 2',
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
		'name': 'Неизвестная 1',
		'description': '',
		'default': 0.0
	}
	Unk_Int2 = {
		'prop': 'int2',
		'type': fieldType.INT,
		'name': 'Неизвестная 2',
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
		'name': 'Неизвестная 1',
		'description': '',
		'default': 0.0
	}
	Unk_Int2 = {
		'prop': 'int2',
		'type': fieldType.INT,
		'name': 'Неизвестная 2',
		'description': '',
		'default': 0
	}


class b_common():
	LevelGroup = {
		'prop': 'level_group',
		'type': fieldType.INT,
		'name': 'Группа блока',
		'description': '',
		'default': 0
	}

class b_1():
	Name1 = {
		'prop': 'name1',
		'type': fieldType.STRING,
		'name': 'Неизв. название 1',
		'description': '',
		'default': ''
	}
	Name2 = {
		'prop': 'name2',
		'type': fieldType.STRING,
		'name': 'Неизв. название 2',
		'description': '',
		'default': ''
	}

class b_2():
	XYZ = {
		'prop': 'XYZ',
		'type': fieldType.COORD,
		'name': 'Координаты блока',
		'description': '',
		'default': (0.0, 0.0, 0.0)
	}
	R = {
		'prop': 'R',
		'type': fieldType.RAD,
		'name': 'Радиус',
		'description': '',
		'default': 0.0
	}
	Unk_XYZ = {
		'prop': 'unk_XYZ',
		'type': fieldType.COORD,
		'name': 'Неизв. координаты',
		'description': '',
		'default': (0.0, 0.0, 0.0)
	}
	Unk_R = {
		'prop': 'unk_R',
		'type': fieldType.RAD,
		'name': 'Неизв. радиус',
		'description': '',
		'default': 0.0
	}

class b_3():
	XYZ = {
		'prop': 'XYZ',
		'type': fieldType.COORD,
		'name': 'Координаты блока',
		'description': '',
		'default': (0.0, 0.0, 0.0)
	}
	R = {
		'prop': 'R',
		'type': fieldType.RAD,
		'name': 'Радиус',
		'description': '',
		'default': 0.0
	}

class b_4():
	XYZ = {
		'prop': 'XYZ',
		'type': fieldType.COORD,
		'name': 'Координаты блока',
		'description': '',
		'default': (0.0, 0.0, 0.0)
	}
	R = {
		'prop': 'R',
		'type': fieldType.RAD,
		'name': 'Радиус',
		'description': '',
		'default': 0.0
	}
	Name1 = {
		'prop': 'name1',
		'type': fieldType.SPACE_NAME,
		'name': 'Трансформация',
		'description': ''
	}
	Name2 = {
		'prop': 'name2',
		'type': fieldType.STRING,
		'name': 'Название 2',
		'description': '',
		'default': ''
	}

class b_5():
    Name1 = {
        'prop': 'name1',
        'type': fieldType.STRING,
        'name': 'Имя блока',
        'description': '',
        'default': ''
    }
    XYZ = {
        'prop': 'XYZ',
        'type': fieldType.COORD,
        'name': 'Координаты блока',
        'description': '',
        'default': (0.0, 0.0, 0.0)
    }
    R = {
        'prop': 'R',
        'type': fieldType.RAD,
        'name': 'Радиус',
        'description': '',
        'default': 0.0
    }


class b_6():
	XYZ = {
		'prop': 'XYZ',
		'type': fieldType.COORD,
		'name': 'Координаты блока',
		'description': '',
		'default': (0.0, 0.0, 0.0)
	}
	R = {
		'prop': 'R',
		'type': fieldType.RAD,
		'name': 'Радиус',
		'description': '',
		'default': 0.0
	}
	Name1 = {
		'prop': 'name1',
		'type': fieldType.STRING,
		'name': 'Название 1',
		'description': '',
		'default': ''
	}
	Name2 = {
		'prop': 'name2',
		'type': fieldType.STRING,
		'name': 'Название 2',
		'description': '',
		'default': ''
	}

class b_7():
    XYZ = {
        'prop': 'XYZ',
        'type': fieldType.COORD,
        'name': 'Координаты блока',
        'description': '',
        'default': (0.0, 0.0, 0.0)
    }
    R = {
        'prop': 'R',
        'type': fieldType.RAD,
        'name': 'Радиус',
        'description': '',
        'default': 0.0
    }
    Name1 = {
        'prop': 'name1',
        'type': fieldType.STRING,
        'name': 'Название группы',
        'description': '',
        'default': ''
    }

class b_8():
	XYZ = {
		'prop': 'XYZ',
		'type': fieldType.COORD,
		'name': 'Координаты блока',
		'description': '',
		'default': (0.0, 0.0, 0.0)
	}
	R = {
		'prop': 'R',
		'type': fieldType.RAD,
		'name': 'Радиус',
		'description': '',
		'default': 0.0
	}

class b_9():
	XYZ = {
		'prop': 'XYZ',
		'type': fieldType.COORD,
		'name': 'Координаты блока',
		'description': '',
		'default': (0.0, 0.0, 0.0)
	}
	R = {
		'prop': 'R',
		'type': fieldType.RAD,
		'name': 'Радиус',
		'description': '',
		'default': 0.0
	}
	Unk_XYZ = {
		'prop': 'unk_XYZ',
		'type': fieldType.COORD,
		'name': 'Неизв. координаты',
		'description': '',
		'default': (0.0, 0.0, 0.0)
	}
	Unk_R = {
		'prop': 'unk_R',
		'type': fieldType.RAD,
		'name': 'Неизв. радиус',
		'description': '',
		'default': 0.0
	}

class b_10():
	XYZ = {
		'prop': 'XYZ',
		'type': fieldType.COORD,
		'name': 'Координаты блока',
		'description': '',
		'default': (0.0, 0.0, 0.0)
	}
	R = {
		'prop': 'R',
		'type': fieldType.RAD,
		'name': 'Радиус',
		'description': '',
		'default': 0.0
	}
	LOD_XYZ = {
		'prop': 'LOD_XYZ',
		'type': fieldType.COORD,
		'name': 'Центр LOD',
		'description': '',
		'default': (0.0, 0.0, 0.0)
	}
	LOD_R = {
		'prop': 'LOD_R',
		'type': fieldType.RAD,
		'name': 'Радиус LOD',
		'description': '',
		'default': 0.0
	}

class b_11():
	XYZ = {
		'prop': 'XYZ',
		'type': fieldType.COORD,
		'name': 'Координаты блока',
		'description': '',
		'default': (0.0, 0.0, 0.0)
	}
	R = {
		'prop': 'R',
		'type': fieldType.RAD,
		'name': 'Радиус',
		'description': '',
		'default': 0.0
	}
	Unk_XYZ = {
		'prop': 'unk_XYZ',
		'type': fieldType.COORD,
		'name': 'Неизв. координаты',
		'description': '',
		'default': (0.0, 0.0, 0.0)
	}
	Unk_R = {
		'prop': 'unk_R',
		'type': fieldType.RAD,
		'name': 'Неизв. радиус',
		'description': '',
		'default': 0.0
	}

class b_12():
	XYZ = {
		'prop': 'XYZ',
		'type': fieldType.COORD,
		'name': 'Координаты блока',
		'description': '',
		'default': (0.0, 0.0, 0.0)
	}
	R = {
		'prop': 'R',
		'type': fieldType.RAD,
		'name': 'Радиус',
		'description': '',
		'default': 0.0
	}
	Unk_XYZ = {
		'prop': 'unk_XYZ',
		'type': fieldType.COORD,
		'name': 'Неизв. координаты',
		'description': '',
		'default': (0.0, 0.0, 0.0)
	}
	Unk_R = {
		'prop': 'unk_R',
		'type': fieldType.RAD,
		'name': 'Неизв. радиус',
		'description': '',
		'default': 0.0
	}
	Unk_Int1 = {
		'prop': 'int1',
		'type': fieldType.INT,
		'name': 'Неизвестная 1',
		'description': '',
		'default': 0
	}
	Unk_Int2 = {
		'prop': 'int2',
		'type': fieldType.INT,
		'name': 'Неизвестная 2',
		'description': '',
		'default': 0
	}
	Unk_List = {
		'prop': 'list1',
		'type': fieldType.LIST,
		'name': 'Неизв. параметры',
		'description': '',
	}

class b_13():
	XYZ = {
		'prop': 'XYZ',
		'type': fieldType.COORD,
		'name': 'Координаты блока',
		'description': '',
		'default': (0.0, 0.0, 0.0)
	}
	R = {
		'prop': 'R',
		'type': fieldType.RAD,
		'name': 'Радиус',
		'description': '',
		'default': 0.0
	}
	Unk_Int1 = {
		'prop': 'int1',
		'type': fieldType.INT,
		'name': 'Неизвестная 1',
		'description': '',
		'default': 0
	}
	Unk_Int2 = {
		'prop': 'int2',
		'type': fieldType.INT,
		'name': 'Неизвестная 2',
		'description': '',
		'default': 0
	}
	Unk_List = {
		'prop': 'list1',
		'type': fieldType.LIST,
		'name': 'Неизв. параметры',
		'description': '',
	}

class b_14():
	XYZ = {
		'prop': 'XYZ',
		'type': fieldType.COORD,
		'name': 'Координаты блока',
		'description': '',
		'default': (0.0, 0.0, 0.0)
	}
	R = {
		'prop': 'R',
		'type': fieldType.RAD,
		'name': 'Радиус',
		'description': '',
		'default': 0.0
	}
	Unk_XYZ = {
		'prop': 'unk_XYZ',
		'type': fieldType.COORD,
		'name': 'Неизв. координаты',
		'description': '',
		'default': (0.0, 0.0, 0.0)
	}
	Unk_R = {
		'prop': 'unk_R',
		'type': fieldType.RAD,
		'name': 'Неизв. радиус',
		'description': '',
		'default': 0.0
	}
	Unk_Int1 = {
		'prop': 'int1',
		'type': fieldType.INT,
		'name': 'Неизвестная 1',
		'description': '',
		'default': 0
	}
	Unk_Int2 = {
		'prop': 'int2',
		'type': fieldType.INT,
		'name': 'Неизвестная 2',
		'description': '',
		'default': 0
	}
	Unk_List = {
		'prop': 'list1',
		'type': fieldType.LIST,
		'name': 'Неизв. параметры',
		'description': '',
	}

class b_15():
	XYZ = {
		'prop': 'XYZ',
		'type': fieldType.COORD,
		'name': 'Координаты блока',
		'description': '',
		'default': (0.0, 0.0, 0.0)
	}
	R = {
		'prop': 'R',
		'type': fieldType.RAD,
		'name': 'Радиус',
		'description': '',
		'default': 0.0
	}
	Unk_Int1 = {
		'prop': 'int1',
		'type': fieldType.INT,
		'name': 'Неизвестная 1',
		'description': '',
		'default': 0
	}
	Unk_Int2 = {
		'prop': 'int2',
		'type': fieldType.INT,
		'name': 'Неизвестная 2',
		'description': '',
		'default': 0
	}
	Unk_List = {
		'prop': 'list1',
		'type': fieldType.LIST,
		'name': 'Неизв. параметры',
		'description': '',
	}

class b_16():
	XYZ = {
		'prop': 'XYZ',
		'type': fieldType.COORD,
		'name': 'Координаты блока',
		'description': '',
		'default': (0.0, 0.0, 0.0)
	}
	R = {
		'prop': 'R',
		'type': fieldType.RAD,
		'name': 'Радиус',
		'description': '',
		'default': 0.0
	}
	Unk_XYZ1 = {
		'prop': 'unk_XYZ1',
		'type': fieldType.COORD,
		'name': 'Неизв. координаты 1',
		'description': '',
		'default': (0.0, 0.0, 0.0)
	}
	Unk_XYZ2 = {
		'prop': 'unk_XYZ2',
		'type': fieldType.COORD,
		'name': 'Неизв. координаты 2',
		'description': '',
		'default': (0.0, 0.0, 0.0)
	}
	Unk_Float1 = {
		'prop': 'float1',
		'type': fieldType.FLOAT,
		'name': 'Неизвестная 1',
		'description': '',
		'default': 0.0
	}
	Unk_Float2 = {
		'prop': 'float2',
		'type': fieldType.FLOAT,
		'name': 'Неизвестная 2',
		'description': '',
		'default': 0.0
	}
	Unk_Int1 = {
		'prop': 'int1',
		'type': fieldType.INT,
		'name': 'Неизвестная 3',
		'description': '',
		'default': 0
	}
	Unk_Int2 = {
		'prop': 'int2',
		'type': fieldType.INT,
		'name': 'Неизвестная 4',
		'description': '',
		'default': 0
	}
	Unk_List = {
		'prop': 'list1',
		'type': fieldType.LIST,
		'name': 'Неизв. параметры',
		'description': '',
	}

class b_17():
	XYZ = {
		'prop': 'XYZ',
		'type': fieldType.COORD,
		'name': 'Координаты блока',
		'description': '',
		'default': (0.0, 0.0, 0.0)
	}
	R = {
		'prop': 'R',
		'type': fieldType.RAD,
		'name': 'Радиус',
		'description': '',
		'default': 0.0
	}
	Unk_XYZ1 = {
		'prop': 'unk_XYZ1',
		'type': fieldType.COORD,
		'name': 'Неизв. координаты 1',
		'description': '',
		'default': (0.0, 0.0, 0.0)
	}
	Unk_XYZ2 = {
		'prop': 'unk_XYZ2',
		'type': fieldType.COORD,
		'name': 'Неизв. координаты 2',
		'description': '',
		'default': (0.0, 0.0, 0.0)
	}
	Unk_Float1 = {
		'prop': 'float1',
		'type': fieldType.FLOAT,
		'name': 'Неизвестная 1',
		'description': '',
		'default': 0.0
	}
	Unk_Float2 = {
		'prop': 'float2',
		'type': fieldType.FLOAT,
		'name': 'Неизвестная 2',
		'description': '',
		'default': 0.0
	}
	Unk_Int1 = {
		'prop': 'int1',
		'type': fieldType.INT,
		'name': 'Неизвестная 3',
		'description': '',
		'default': 0
	}
	Unk_Int2 = {
		'prop': 'int2',
		'type': fieldType.INT,
		'name': 'Неизвестная 4',
		'description': '',
		'default': 0
	}
	Unk_List = {
		'prop': 'list1',
		'type': fieldType.LIST,
		'name': 'Неизв. параметры',
		'description': '',
	}

class b_18():
	XYZ = {
		'prop': 'XYZ',
		'type': fieldType.COORD,
		'name': 'Координаты блока',
		'description': '',
		'default': (0.0, 0.0, 0.0)
	}
	R = {
		'prop': 'R',
		'type': fieldType.RAD,
		'name': 'Радиус',
		'description': '',
		'default': 0.0
	}
	Space_Name = {
        'prop': 'space_name',
        'type': fieldType.SPACE_NAME,
        'name': 'Название трансформации (24)',
        'description': ''
    }
	Add_Name = {
        'prop': 'add_name',
        'type': fieldType.REFERENCEABLE,
        'name': 'Название переносимого блока',
        'description': ''
    }

class b_20():
	XYZ = {
		'prop': 'XYZ',
		'type': fieldType.COORD,
		'name': 'Координаты блока',
		'description': '',
		'default': (0.0, 0.0, 0.0)
	}
	R = {
		'prop': 'R',
		'type': fieldType.RAD,
		'name': 'Радиус',
		'description': '',
		'default': 0.0
	}
	Unk_Int1 = {
		'prop': 'int1',
		'type': fieldType.INT,
		'name': 'Неизвестная 1',
		'description': '',
		'default': 0
	}
	Unk_Int2 = {
		'prop': 'int2',
		'type': fieldType.INT,
		'name': 'Неизвестная 2',
		'description': '',
		'default': 0
	}
	Unk_List = {
		'prop': 'list1',
		'type': fieldType.LIST,
		'name': 'Неизв. параметры',
		'description': '',
	}

class b_21():
	XYZ = {
		'prop': 'XYZ',
		'type': fieldType.COORD,
		'name': 'Координаты блока',
		'description': '',
		'default': (0.0, 0.0, 0.0)
	}
	R = {
		'prop': 'R',
		'type': fieldType.RAD,
		'name': 'Радиус',
		'description': '',
		'default': 0.0
	}
	GroupCnt = {
		'prop': 'group_cnt',
		'type': fieldType.INT,
		'name': 'Количество групп',
		'description': '',
		'default': 0
	}
	Unk_Int2 = {
		'prop': 'int2',
		'type': fieldType.INT,
		'name': 'Неизвестная 2',
		'description': '',
		'default': 0
	}

class b_22():
	XYZ = {
		'prop': 'XYZ',
		'type': fieldType.COORD,
		'name': 'Координаты блока',
		'description': '',
		'default': (0.0, 0.0, 0.0)
	}
	R = {
		'prop': 'R',
		'type': fieldType.RAD,
		'name': 'Радиус',
		'description': '',
		'default': 0.0
	}
	Unk_XYZ = {
		'prop': 'unk_XYZ',
		'type': fieldType.COORD,
		'name': 'Неизв. координаты',
		'description': '',
		'default': (0.0, 0.0, 0.0)
	}
	Unk_R = {
		'prop': 'unk_R',
		'type': fieldType.RAD,
		'name': 'Неизв. радиус',
		'description': '',
		'default': 0.0
	}

class b_23():
	Unk_Int1 = {
		'prop': 'int1',
		'type': fieldType.INT,
		'name': 'Неизвестная 1',
		'description': '',
		'default': 0
	}
	Surface = {
		'prop': 'CType',
		'type': fieldType.ENUM,
		'subtype': fieldType.INT,
		'name': 'Тип поверхности',
		'description': '',
		'default': 0,
		'items': collisionTypeList
	}
	Unk_List = {
		'prop': 'list1',
		'type': fieldType.LIST,
		'name': 'Неизв. параметры',
		'description': '',
	}

class b_24():
	Flag = {
		'prop': 'flag',
		'type': fieldType.INT,
		'name': 'Неизвестная 1',
		'description': '',
		'default': 0
	}

class b_25():
	XYZ = {
		'prop': 'XYZ',
		'type': fieldType.COORD,
		'name': 'Координаты блока',
		'description': '',
		'default': (0.0, 0.0, 0.0)
	}
	Name = {
		'prop': 'name',
		'type': fieldType.STRING,
		'name': 'Название 1',
		'description': '',
		'default': ''
	}
	Unk_XYZ1 = {
		'prop': 'unk_XYZ1',
		'type': fieldType.COORD,
		'name': 'Неизв. координаты 1',
		'description': '',
		'default': (0.0, 0.0, 0.0)
	}
	Unk_XYZ2 = {
		'prop': 'unk_XYZ2',
		'type': fieldType.COORD,
		'name': 'Неизв. координаты 2',
		'description': '',
		'default': (0.0, 0.0, 0.0)
	}
	Unk_Float1 = {
		'prop': 'float1',
		'type': fieldType.FLOAT,
		'name': 'Неизвестная 1',
		'description': '',
		'default': 0.0
	}
	Unk_Float2 = {
		'prop': 'float2',
		'type': fieldType.FLOAT,
		'name': 'Неизвестная 2',
		'description': '',
		'default': 0.0
	}
	Unk_Float3 = {
		'prop': 'float3',
		'type': fieldType.FLOAT,
		'name': 'Неизвестная 3',
		'description': '',
		'default': 0.0
	}
	Unk_Float4 = {
		'prop': 'float4',
		'type': fieldType.FLOAT,
		'name': 'Неизвестная 4',
		'description': '',
		'default': 0.0
	}
	Unk_Float5 = {
		'prop': 'float5',
		'type': fieldType.FLOAT,
		'name': 'Неизвестная 5',
		'description': '',
		'default': 0.0
	}

class b_26():
	XYZ = {
		'prop': 'XYZ',
		'type': fieldType.COORD,
		'name': 'Координаты блока',
		'description': '',
		'default': (0.0, 0.0, 0.0)
	}
	R = {
		'prop': 'R',
		'type': fieldType.RAD,
		'name': 'Радиус',
		'description': '',
		'default': 0.0
	}
	Unk_XYZ1 = {
		'prop': 'unk_XYZ1',
		'type': fieldType.COORD,
		'name': 'Неизв. координаты 1',
		'description': '',
		'default': (0.0, 0.0, 0.0)
	}
	Unk_XYZ2 = {
		'prop': 'unk_XYZ2',
		'type': fieldType.COORD,
		'name': 'Неизв. координаты 2',
		'description': '',
		'default': (0.0, 0.0, 0.0)
	}
	Unk_XYZ3 = {
		'prop': 'unk_XYZ3',
		'type': fieldType.COORD,
		'name': 'Неизв. координаты 3',
		'description': '',
		'default': (0.0, 0.0, 0.0)
	}

class b_27():
	XYZ = {
		'prop': 'XYZ',
		'type': fieldType.COORD,
		'name': 'Координаты блока',
		'description': '',
		'default': (0.0, 0.0, 0.0)
	}
	R = {
		'prop': 'R',
		'type': fieldType.RAD,
		'name': 'Радиус',
		'description': '',
		'default': 0.0
	}
	Flag = {
		'prop': 'flag',
		'type': fieldType.INT,
		'name': 'Флаг',
		'description': '',
		'default': 0
	}
	Unk_XYZ = {
		'prop': 'unk_XYZ',
		'type': fieldType.COORD,
		'name': 'Неизв. координаты',
		'description': '',
		'default': (0.0, 0.0, 0.0)
	}
	Material = {
		'prop': 'material',
		'type': fieldType.INT,
		'name': 'Материал',
		'description': '',
		'default': 0
	}

class b_28():
	XYZ = {
		'prop': 'XYZ',
		'type': fieldType.COORD,
		'name': 'Координаты блока',
		'description': '',
		'default': (0.0, 0.0, 0.0)
	}
	R = {
		'prop': 'R',
		'type': fieldType.RAD,
		'name': 'Радиус',
		'description': '',
		'default': 0.0
	}
	Unk_XYZ = {
		'prop': 'unk_XYZ',
		'type': fieldType.COORD,
		'name': 'Координаты блока',
		'description': '',
		'default': (0.0, 0.0, 0.0)
	}
 	#todo: check

class b_29():
	XYZ = {
		'prop': 'XYZ',
		'type': fieldType.COORD,
		'name': 'Координаты блока',
		'description': '',
		'default': (0.0, 0.0, 0.0)
	}
	R = {
		'prop': 'R',
		'type': fieldType.RAD,
		'name': 'Радиус',
		'description': '',
		'default': 0.0
	}
	Unk_Int1 = {
		'prop': 'int1',
		'type': fieldType.INT,
		'name': 'Неизвестная 1',
		'description': '',
		'default': 0
	}
	Unk_Int2 = {
		'prop': 'int2',
		'type': fieldType.INT,
		'name': 'Неизвестная 2',
		'description': '',
		'default': 0
	}
	Unk_XYZ = {
		'prop': 'unk_XYZ',
		'type': fieldType.COORD,
		'name': 'Неизв. координаты',
		'description': '',
		'default': (0.0, 0.0, 0.0)
	}
	Unk_R = {
		'prop': 'unk_R',
		'type': fieldType.RAD,
		'name': 'Неизв. радиус',
		'description': '',
		'default': 0.0
	}

class b_30():
	XYZ = {
		'prop': 'XYZ',
		'type': fieldType.COORD,
		'name': 'Координаты блока',
		'description': '',
		'default': (0.0, 0.0, 0.0)
	}
	R = {
		'prop': 'R',
		'type': fieldType.RAD,
		'name': 'Радиус',
		'description': '',
		'default': 0.0
	}
	Name = {
		'prop': 'name',
		'type': fieldType.STRING,
		'name': 'Название комнаты',
		'description': '',
		'default': ''
	}
	XYZ1 = {
		'prop': 'XYZ1',
		'type': fieldType.COORD,
		'name': 'Координаты 1. точки',
		'description': '',
		'default': (0.0, 0.0, 0.0)
	}
	XYZ2 = {
		'prop': 'XYZ2',
		'type': fieldType.COORD,
		'name': 'Координаты 2. точки',
		'description': '',
		'default': (0.0, 0.0, 0.0)
	}

class b_31():
	XYZ = {
		'prop': 'XYZ',
		'type': fieldType.COORD,
		'name': 'Координаты блока',
		'description': '',
		'default': (0.0, 0.0, 0.0)
	}
	R = {
		'prop': 'R',
		'type': fieldType.RAD,
		'name': 'Радиус',
		'description': '',
		'default': 0.0
	}
	Unk_Int1 = {
		'prop': 'int1',
		'type': fieldType.INT,
		'name': 'Неизвестная 1',
		'description': '',
		'default': 0
	}
	Unk_XYZ1 = {
		'prop': 'unk_XYZ1',
		'type': fieldType.COORD,
		'name': 'Неизв. координаты 1',
		'description': '',
		'default': (0.0, 0.0, 0.0)
	}
	Unk_R = {
		'prop': 'unk_R',
		'type': fieldType.RAD,
		'name': 'Радиус',
		'description': '',
		'default': 0.0
	}
	Unk_Int2 = {
		'prop': 'int2',
		'type': fieldType.INT,
		'name': 'Неизвестная 2',
		'description': '',
		'default': 0
	}
	Unk_XYZ2 = {
		'prop': 'unk_XYZ2',
		'type': fieldType.COORD,
		'name': 'Неизв. координаты 1',
		'description': '',
		'default': (0.0, 0.0, 0.0)
	}
	#todo: check

class b_33():
	XYZ = {
		'prop': 'XYZ',
		'type': fieldType.COORD,
		'name': 'Координаты блока',
		'description': '',
		'default': (0.0, 0.0, 0.0)
	}
	R = {
		'prop': 'R',
		'type': fieldType.RAD,
		'name': 'Радиус',
		'description': '',
		'default': 0.0
	}
	Use_Lights = {
		'prop': 'useLight',
		'type': fieldType.INT,
		'name': 'Исп. свет',
		'description': '',
		'default': 0
	}
	Light_Type = {
		'prop': 'lType',
		'type': fieldType.INT,
		'name': 'Тип света',
		'description': '',
		'default': 0
	}
	Flag = {
		'prop': 'flag',
		'type': fieldType.INT,
		'name': 'Флаг',
		'description': '',
		'default': 0
	}
	Unk_XYZ1 = {
		'prop': 'unk_XYZ1',
		'type': fieldType.COORD,
		'name': 'Неизв. координаты 1',
		'description': '',
		'default': (0.0, 0.0, 0.0)
	}
	Unk_XYZ2 = {
		'prop': 'unk_XYZ2',
		'type': fieldType.COORD,
		'name': 'Неизв. координаты 2',
		'description': '',
		'default': (0.0, 0.0, 0.0)
	}
	Unk_Float1 = {
		'prop': 'float1',
		'type': fieldType.FLOAT,
		'name': 'Неизв. 1',
		'description': '',
		'default': 0.0
	}
	Unk_Float2 = {
		'prop': 'float2',
		'type': fieldType.FLOAT,
		'name': 'Неизв. 2',
		'description': '',
		'default': 0.0
	}
	Light_R = {
		'prop': 'light_radius',
		'type': fieldType.FLOAT,
		'name': 'Радиус света',
		'description': '',
		'default': 0.0
	}
	Intens = {
		'prop': 'intensity',
		'type': fieldType.FLOAT,
		'name': 'Интенсивность',
		'description': '',
		'default': 0.0
	}
	Unk_Float3 = {
		'prop': 'float3',
		'type': fieldType.FLOAT,
		'name': 'Неизв. 3',
		'description': '',
		'default': 0.0
	}
	Unk_Float4 = {
		'prop': 'float4',
		'type': fieldType.FLOAT,
		'name': 'Неизв. 4',
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
		'prop': 'XYZ',
		'type': fieldType.COORD,
		'name': 'Координаты блока',
		'description': '',
		'default': (0.0, 0.0, 0.0)
	}
	R = {
		'prop': 'R',
		'type': fieldType.RAD,
		'name': 'Радиус',
		'description': '',
		'default': 0.0
	}
	UnkInt = {
		'prop': 'int1',
		'type': fieldType.INT,
		'name': 'Неизв.',
		'description': '',
		'default': 0
	}

class b_35():
	XYZ = {
		'prop': 'XYZ',
		'type': fieldType.COORD,
		'name': 'Координаты блока',
		'description': '',
		'default': (0.0, 0.0, 0.0)
	}
	R = {
		'prop': 'R',
		'type': fieldType.RAD,
		'name': 'Радиус',
		'description': '',
		'default': 0.0
	}
	MType = {
		'prop': 'mType',
		'type': fieldType.INT,
		'name': 'Переменная 1',
		'description': '',
		'default': 0
	}
	TexNum = {
		'prop': 'texnum',
		'type': fieldType.MATERIAL_IND,
		'name': 'Номер текстуры',
		'description': '',
	}

class b_36():
	XYZ = {
		'prop': 'XYZ',
		'type': fieldType.COORD,
		'name': 'Координаты блока',
		'description': '',
		'default': (0.0, 0.0, 0.0)
	}
	R = {
		'prop': 'R',
		'type': fieldType.RAD,
		'name': 'Радиус',
		'description': '',
		'default': 0.0
	}
	Name1 = {
		'prop': 'name1',
		'type': fieldType.STRING,
		'name': 'Название 1',
		'description': '',
		'default': ''
	}
	Name2 = {
		'prop': 'name2',
		'type': fieldType.STRING,
		'name': 'Название 2',
		'description': '',
		'default': ''
	}
	MType = {
		'prop': 'MType',
		'type': fieldType.INT,
		'name': 'Переменная 1',
		'description': '',
		'default': 0
	}

class b_37():
	XYZ = {
		'prop': 'XYZ',
		'type': fieldType.COORD,
		'name': 'Координаты блока',
		'description': '',
		'default': (0.0, 0.0, 0.0)
	}
	R = {
		'prop': 'R',
		'type': fieldType.RAD,
		'name': 'Радиус',
		'description': '',
		'default': 0.0
	}
	Name1 = {
		'prop': 'name1',
		'type': fieldType.STRING,
		'name': 'Название 1',
		'description': '',
		'default': ''
	}
	SType = {
		'prop': 'SType',
		'type': fieldType.INT,
		'name': 'Переменная 1',
		'description': '',
		'default': 0
	}

class b_39():
	XYZ = {
		'prop': 'XYZ',
		'type': fieldType.COORD,
		'name': 'Координаты блока',
		'description': '',
		'default': (0.0, 0.0, 0.0)
	}
	R = {
		'prop': 'R',
		'type': fieldType.RAD,
		'name': 'Радиус',
		'description': '',
		'default': 0.0
	}
	Color_R = {
		'prop': 'color_r',
		'type': fieldType.INT,
		'name': 'Радиус цвета',
		'description': '',
		'default': 0
	}
	Unk_Float1 = {
		'prop': 'float1',
		'type': fieldType.FLOAT,
		'name': 'Неизвестная 1',
		'description': '',
		'default': 0.0
	}
	Fog_Start = {
		'prop': 'fog_start',
		'type': fieldType.FLOAT,
		'name': 'Неизвестная 3',
		'description': '',
		'default': 0.0
	}
	Fog_End = {
		'prop': 'fog_end',
		'type': fieldType.FLOAT,
		'name': 'Неизвестная 4',
		'description': '',
		'default': 0.0
	}
	Color_Id = {
		'prop': 'color_id',
		'type': fieldType.INT,
		'name': 'ID цвета',
		'description': '',
		'default': 0
	}

class b_40():
	XYZ = {
		'prop': 'XYZ',
		'type': fieldType.COORD,
		'name': 'Координаты блока',
		'description': '',
		'default': (0.0, 0.0, 0.0)
	}
	R = {
		'prop': 'R',
		'type': fieldType.RAD,
		'name': 'Радиус',
		'description': '',
		'default': 0.0
	}
	Name1 = {
		'prop': 'name1',
		'type': fieldType.STRING,
		'name': 'Название 1',
		'description': '',
		'default': ''
	}
	Name2 = {
		'prop': 'name2',
		'type': fieldType.ENUM,
		'subtype': fieldType.STRING,
		'name': 'Тип генератора',
		'description': '',
		'default': '$$TreeGenerator',
		'items': generatorTypeList
	}
	Unk_Int1 = {
		'prop': 'int1',
		'type': fieldType.INT,
		'name': 'Неизвестная 1',
		'description': '',
		'default': 0
	}
	Unk_Int2 = {
		'prop': 'int2',
		'type': fieldType.INT,
		'name': 'Неизвестная 2',
		'description': '',
		'default': 0
	}
	Unk_List = {
		'prop': 'list1',
		'type': fieldType.LIST,
		'name': 'Неизв. параметры',
		'description': '',
	}

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
