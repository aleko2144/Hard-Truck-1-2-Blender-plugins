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


class fieldType(enum.Enum):
	STRING = 1
	COORD = 2
	RAD = 3
	INT = 4
	FLOAT = 5
	ENUM = 6
	LIST = 7
	V_FORMAT = 8


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


def createTypeClass(zclass):
	attrs = [obj for obj in zclass.__dict__.keys() if not obj.startswith('__')]
	attributes = {
		'__annotations__' : {

		}
	}
	for attr in attrs:
		obj = zclass.__dict__[attr]
		propName = obj['prop']
		prop = None

		lockProp = BoolProperty(
			name = "Вкл./Выкл.",
			description = "Включить/выключить параметр для редактирования",
			default = True
		)

		if obj['type'] == fieldType.STRING \
		or obj['type'] == fieldType.COORD \
		or obj['type'] == fieldType.RAD \
		or obj['type'] == fieldType.FLOAT \
		or obj['type'] == fieldType.INT \
		or obj['type'] == fieldType.ENUM \
		or obj['type'] == fieldType.LIST:


			attributes['__annotations__']["show_"+propName] = lockProp

			if obj['type'] == fieldType.STRING:
				prop = StringProperty(
					name = obj['name'],
					description = obj['description'],
					default = obj['default'],
					maxlen = 30
				)

			elif obj['type'] == fieldType.COORD:
				prop = FloatVectorProperty(
					name = obj['name'],
					description = obj['description'],
					default = obj['default']
				)

			elif obj['type'] == fieldType.RAD or obj['type'] == fieldType.FLOAT:
				prop = FloatProperty(
					name = obj['name'],
					description = obj['description'],
					default = obj['default']
				)

			elif obj['type'] == fieldType.INT:
				prop = IntProperty(
					name = obj['name'],
					description = obj['description'],
					default = obj['default']
				)

			elif obj['type'] == fieldType.ENUM:
				prop = EnumProperty(
					name = obj['name'],
					description = obj['description'],
					default = obj['default'],
					items = obj['items']
				)

			elif obj['type'] == fieldType.LIST:
				prop = CollectionProperty(
					name = obj['name'],
					description = obj['description'],
					type = FloatBlock
				)

			attributes['__annotations__'][propName] = prop

		elif obj['type'] == fieldType.V_FORMAT:

			attributes['__annotations__']["show_{}".format(propName)] = lockProp

			prop1 = BoolProperty(
				name = 'Смещенная триангуляция',
				description = 'Порядок в котором считываются вертексы, зависит от этой переменной',
				default = True
			)
			attributes['__annotations__']['{}_{}'.format(propName, 'triang_offset')] = prop1

			prop2 = BoolProperty(
				name = 'Использовать UV',
				description = 'Когда активен, при экспорте записывает UV.',
				default = True
			)
			attributes['__annotations__']['{}_{}'.format(propName, 'use_uvs')] = prop2

			prop3 = BoolProperty(
				name = 'Использовать нормали',
				description = 'Когда активен, при экспорте записывает нормали.',
				default = True
			)
			attributes['__annotations__']['{}_{}'.format(propName, 'use_normals')] = prop3

			prop4 = BoolProperty(
				name = 'Выключатель нормалей',
				description = 'Когда активен, использует float для вкл./выкл. нормалей. Когда неактивен использует float vector для обычных нормалей. Игнорируется если пункт "Использовать нормали" неактивен',
				default = True
			)
			attributes['__annotations__']['{}_{}'.format(propName, 'normal_flag')] = prop4

	newclass = type("{}_gen".format(zclass.__name__), (bpy.types.PropertyGroup,), attributes)
	return newclass

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
        'type': fieldType.STRING,
        'name': 'Название трансформации (24)',
        'description': '',
        'default': ''
    }
	Add_Name = {
        'prop': 'add_name',
        'type': fieldType.STRING,
        'name': 'Название переносимого блока',
        'description': '',
        'default': ''
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
		'type': fieldType.INT,
		'name': 'Тип поверхности',
		'description': '',
		'default': 0
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
		'prop': 'int1',
		'type': fieldType.INT,
		'name': 'Исп. свет',
		'description': '',
		'default': 0
	}
	Light_Type = {
		'prop': 'int2',
		'type': fieldType.INT,
		'name': 'Тип света',
		'description': '',
		'default': 0
	}
	Flag = {
		'prop': 'int2',
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
	#todo check

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
		'type': fieldType.INT,
		'name': 'Номер текстуры',
		'description': '',
		'default': 0
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
		'type': fieldType.STRING,
		'name': 'Название 2',
		'description': '',
		'default': ''
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


perFaceBlock_8 = createTypeClass(pfb_8)
perFaceBlock_28 = createTypeClass(pfb_28)
perFaceBlock_35 = createTypeClass(pfb_35)

perVertBlock_8 = createTypeClass(pvb_8)
perVertBlock_35 = createTypeClass(pvb_35)

block_common = createTypeClass(b_common)
block_1 = createTypeClass(b_1)
block_2 = createTypeClass(b_2)
block_3 = createTypeClass(b_3)
block_4 = createTypeClass(b_4)
block_5 = createTypeClass(b_5)
block_6 = createTypeClass(b_6)
block_7 = createTypeClass(b_7)
block_8 = createTypeClass(b_8)
block_9 = createTypeClass(b_9)
block_10 = createTypeClass(b_10)
block_11 = createTypeClass(b_11)
block_12 = createTypeClass(b_12)
block_13 = createTypeClass(b_13)
block_14 = createTypeClass(b_14)
block_15 = createTypeClass(b_15)
block_16 = createTypeClass(b_16)
block_17 = createTypeClass(b_17)
block_18 = createTypeClass(b_18)
block_20 = createTypeClass(b_20)
block_21 = createTypeClass(b_21)
block_22 = createTypeClass(b_22)
block_23 = createTypeClass(b_23)
block_24 = createTypeClass(b_24)
block_25 = createTypeClass(b_25)
block_26 = createTypeClass(b_26)
block_27 = createTypeClass(b_27)
block_28 = createTypeClass(b_28)
block_29 = createTypeClass(b_29)
block_30 = createTypeClass(b_30)
block_31 = createTypeClass(b_31)
block_33 = createTypeClass(b_33)
block_34 = createTypeClass(b_34)
block_35 = createTypeClass(b_35)
block_36 = createTypeClass(b_36)
block_37 = createTypeClass(b_37)
block_39 = createTypeClass(b_39)
block_40 = createTypeClass(b_40)

_classes = (
	ActiveBlock,
	FloatBlock,
	TextureBlock,
	MaskfileBlock,
	MaterialBlock,
	ResBlock,
	block_1,
	block_2,
	block_3,
	block_4,
	block_5,
	block_6,
	block_7,
	block_8,
	block_9,
	block_10,
	block_11,
	block_12,
	block_13,
	block_14,
	block_15,
	block_16,
	block_17,
	block_18,
	block_20,
	block_21,
	block_22,
	block_23,
	block_24,
	block_25,
	block_26,
	block_27,
	block_28,
	block_29,
	block_30,
	block_31,
	block_33,
	block_34,
	block_35,
	block_36,
	block_37,
	block_39,
	block_40,
	block_common,
	perFaceBlock_8,
	perFaceBlock_28,
	perFaceBlock_35,
	perVertBlock_8,
	perVertBlock_35
)

def register():
	for cls in _classes:
		bpy.utils.register_class(cls)

def unregister():
	for cls in _classes[::-1]: #reversed
		bpy.utils.unregister_class(cls)
