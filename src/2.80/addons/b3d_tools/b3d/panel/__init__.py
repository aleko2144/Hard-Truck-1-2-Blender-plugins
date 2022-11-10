if "bpy" in locals():
    print("Reimporting modules!!!")
    import importlib
    importlib.reload(common)
else:
    import bpy
    from . import (
        common
    )


from b3d_tools.common import getRegion
from .common import (
	applyRemoveTransforms,
	applyTransforms,
	hideConditionals,
	showConditionals,
	hideLOD,
	showLOD,
	showConditionals,
	hideConditionals,
	showHideObjByType,
	showHideObjTreeByType,
	prop,
	drawCommon,
	drawAllFieldsByType,
	drawFieldByType,
	getAllObjsByType,
	setAllObjsByType
)


from b3d_tools.b3d.classes import (
	block_1,block_2,block_3,block_4,block_5,block_6,block_7,block_8,block_9,block_10,\
	block_11,block_12,block_13,block_14,block_15,block_16,block_17,block_18,block_20,\
	block_21,block_22,block_23,block_24,block_25,block_26,block_27,block_28,block_29,block_30,\
	block_31,block_33,block_34,block_35,block_36,block_37,block_39,block_40,block_common
)
from b3d_tools.b3d.classes import (
	b_1,b_2,b_3,b_4,b_5,b_6,b_7,b_8,b_9,b_10,\
	b_11,b_12,b_13,b_14,b_15,b_16,b_17,b_18,b_20,\
	b_21,b_22,b_23,b_24,b_25,b_26,b_27,b_28,b_29,b_30,\
	b_31,b_33,b_34,b_35,b_36,b_37,b_39,b_40,b_common
)


from bpy.props import (StringProperty,
						BoolProperty,
						IntProperty,
						FloatProperty,
						EnumProperty,
						PointerProperty,
						FloatVectorProperty
						)

from bpy.types import (Panel,
						Operator,
						PropertyGroup,
						)





# ------------------------------------------------------------------------
#	store properties in the active scene
# ------------------------------------------------------------------------

class PanelSettings(bpy.types.PropertyGroup):

	#my_bool = bpy.props.BoolProperty(
	#	name="Enable or Disable",
	#	description="A bool property",
	#	default = False
	#	)

	#my_int : bpy.props.IntProperty(
	#	name = "Int Value",
	#	description="A integer property",
	#	default = 23,
	#	min = 10,
	#	max = 100
	#	)

	#my_float : bpy.props.FloatProperty(
	#	name = "Float Value",
	#	description = "A float property",
	#	default = 23.7,
	#	min = 0.01,
	#	max = 30.0
	#	)

	block1: PointerProperty(type=block_1)
	block2: PointerProperty(type=block_2)
	block3: PointerProperty(type=block_3)
	block4: PointerProperty(type=block_4)
	block5: PointerProperty(type=block_5)
	block6: PointerProperty(type=block_6)
	block7: PointerProperty(type=block_7)
	block8: PointerProperty(type=block_8)
	block9: PointerProperty(type=block_9)
	block10: PointerProperty(type=block_10)
	block11: PointerProperty(type=block_11)
	block12: PointerProperty(type=block_12)
	block13: PointerProperty(type=block_13)
	block14: PointerProperty(type=block_14)
	block15: PointerProperty(type=block_15)
	block16: PointerProperty(type=block_16)
	block17: PointerProperty(type=block_17)
	block18: PointerProperty(type=block_18)
	block20: PointerProperty(type=block_20)
	block21: PointerProperty(type=block_21)
	block22: PointerProperty(type=block_22)
	block23: PointerProperty(type=block_23)
	block24: PointerProperty(type=block_24)
	block25: PointerProperty(type=block_25)
	block26: PointerProperty(type=block_26)
	block27: PointerProperty(type=block_27)
	block28: PointerProperty(type=block_28)
	block29: PointerProperty(type=block_29)
	block30: PointerProperty(type=block_30)
	block31: PointerProperty(type=block_31)
	block33: PointerProperty(type=block_33)
	block34: PointerProperty(type=block_34)
	block35: PointerProperty(type=block_35)
	block36: PointerProperty(type=block_36)
	block37: PointerProperty(type=block_37)
	block39: PointerProperty(type=block_39)
	block40: PointerProperty(type=block_40)
	blockcommon: PointerProperty(type=block_common)

	list_index: IntProperty(name = "Index for my_list", default = 0)

	conditionGroup : bpy.props.IntProperty(
		name='Номер условия',
		description='Номер условия(группа обьекта), который надо скрыть/отобразить. Если -1, то берутся все доступные номера. При слишком большом числе берётся ближайшее подходящее.',
		default=-1,
		min=-1
	)

	coordinates : bpy.props.FloatVectorProperty(
		name='Координаты блока',
		description='',
		default=(0.0, 0.0, 0.0)
	)

	BlockName_string : bpy.props.StringProperty(
		name="Имя блока",
		default="",
		maxlen=30,
		)

	addBlockType_enum : bpy.props.EnumProperty(
		name="Тип блока",
		items=[ ('6566754', "b3d", "b3d"),
				('00', "00", "2D фон"),
				('01', "01", "Камера"),
				('02', "02", "Неизв. блок"),
				('03', "03", "Контейнер"),
				('04', "04", "Контейнер с возможностью привязки к нему других блоков"),
				('05', "05", "Контейнер с возможностью привязки к нему другого блока"),
				('06', "06", "Блок вершин"),
				('07', "07", "Блок вершин"),
				('08', "08", "Блок полигонов"),
				('09', "09", "Триггер"),
				('10', "10", "LOD"),
				('11', "11", "Неизв. блок"),
				('12', "12", "Плоскость коллизии"),
				('13', "13", "Триггер (загрузчик карты)"),
				('14', "14", "Блок, связанный с автомобилями"),
				('15', "15", "Неизв. блок"),
				('16', "16", "Неизв. блок"),
				('17', "17", "Неизв. блок"),
				('18', "18", "Связка локатора и 3D-модели, например: FiatWheel0Space и Single0Wheel14"),
				('19', "19", "Контейнер, в отличие от блока типа 05, не имеет возможности привязки"),
				('20', "20", "Плоская коллизия"),
				('21', "21", "Контейнер с обработкой событий"),
				('22', "22", "Блок-локатор"),
				('23', "23", "Объёмная коллизия"),
				('24', "24", "Локатор"),
				('25', "25", "Звуковой объект"),
				('26', "26", "Блок-локатор"),
				('27', "27", "Блок-локатор"),
				('28', "28", "Блок-локатор"),
				('29', "29", "Неизв. блок"),
				('30', "30", "Триггер для загрузки участков карты"),
				('31', "31", "Неизв. блок"),
				('33', "33", "Источник света"),
				('34', "34", "Неизв. блок"),
				('35', "35", "Блок полигонов"),
				('36', "36", "Блок вершин"),
				('37', "37", "Блок вершин"),
				('39', "39", "Блок-локатор"),
				('40', "40", "Генератор объектов"),
				# ('444', "Разделитель", "Разделитель"),
			   ]
		)


	CollisionType_enum : bpy.props.EnumProperty(
		name="Тип коллизии",
		items=(('0', "стандарт", ""),
			   ('1', "асфальт", ""),
			   ('2', "земля", ""),
			   ('3', "вязкое болото", ""),
			   ('4', "легкопроходимое болото", ""),
			   ('5', "мокрый асфальт", ""),
			   ('7', "лёд", ""),
			   ('8', "вода (уничтожает автомобиль)", ""),
			   ('10', "песок", ""),
			   ('11', "пустыня", ""),
			   ('13', "шипы", ""),
			   ('16', "лёд (следы от шин не остаются)", ""),
			   ),
		)

	Radius : bpy.props.FloatProperty(
		name = "Радиус блока",
		description = "Дальность прорисовки блока",
		default = 1.0,
		)

	Radius1 : bpy.props.FloatProperty(
		name = "Радиус блока",
		description = "Дальность прорисовки блока",
		default = 1.0,
		)

	LOD_Distance : bpy.props.FloatProperty(
		name = "Дальность отображения LOD",
		description = "Маскимальная дальность отображения LOD",
		default = 10.0,
		)

	LOD_Distance1 : bpy.props.FloatProperty(
		name = "Дальность отображения LOD",
		description = "Маскимальная дальность отображения LOD",
		default = 10.0,
		)

	Intensity : bpy.props.FloatProperty(
		name = "Интенсивность освещения",
		description = "Яркость источника света",
		default = 1.0,
		min = 0.0,
		)

	Intensity1 : bpy.props.FloatProperty(
		name = "Интенсивность освещения",
		description = "Яркость источника света",
		default = 1.0,
		min = 0.0,
		)

	R : bpy.props.FloatProperty(
		name = "R",
		description = "",
		default = 255,
		min = 0.0,
		max = 255,
		)

	G : bpy.props.FloatProperty(
		name = "G",
		description = "",
		default = 255,
		min = 0.0,
		max = 255,
		)

	B : bpy.props.FloatProperty(
		name = "B",
		description = "",
		default = 255,
		min = 0.0,
		max = 255,
		)

	R1 : bpy.props.FloatProperty(
		name = "R",
		description = "",
		default = 255,
		min = 0.0,
		max = 255,
		)

	G1 : bpy.props.FloatProperty(
		name = "G",
		description = "",
		default = 255,
		min = 0.0,
		max = 255,
		)

	B1 : bpy.props.FloatProperty(
		name = "B",
		description = "",
		default = 255,
		min = 0.0,
		max = 255,
		)

	RadiusLight : bpy.props.FloatProperty(
		name = "Радиус освещения",
		description = "",
		default = 1,
		min = 0.0,
		)

	RadiusLight1 : bpy.props.FloatProperty(
		name = "Радиус освещения",
		description = "",
		default = 1,
		min = 0.0,
		)

	LType_enum : bpy.props.EnumProperty(
		name="Тип источника света",
		items=(('0', 'Тип 0', ""),
			   ('1', 'Тип 1', ""),
			   ('2', 'Тип 2', ""),
			   ('3', 'Тип 3', ""),
			   ),
		)

	SType_enum : bpy.props.EnumProperty(
		name="Тип записи вершин",
		items=(#('1', "Тип 1, координаты + UV + нормали", ""),
			   ('2', "Тип 2, координаты + UV + нормали", "Данный тип используется на обычных моделях"),
			   ('3', "Тип 3, координаты + UV", "Данный тип используется на моделях света фар"),
			   ('258', "Тип 258, координаты + UV + нормали + 2 float", "Данный тип используется для моделей асфальтированных дорог"),
			   ('514', "Тип 514, координаты + UV + нормали + 4 float", "Данный тип используется на моделях поверхности воды"),
			   ('515', "Тип 515, координаты + UV + нормали + 2 float", "Тоже самое, что и 258. Данный тип используется для моделей асфальтированных дорог"),
			   ),
		)

	MType_enum : bpy.props.EnumProperty(
		name="Тип записи полигонов (35)",
		items=(('1', "Тип 1, с разрывной UV", "Каждый трис модели записывается вместе со собственной UV."),
			   ('3', "Тип 3, без разрывной UV", "Этот тип можно использовать для моделей, которые используют текстуру отражений."),
			   ),
		)

	texNum_int : bpy.props.IntProperty(
		name = "Номер текстуры",
		description="Номер используемой текстуры.",
		)

	addBlockName_string : bpy.props.StringProperty(
		name="Присоединённый блок",
		description="Имя блока, который будет приписан к текущему блоку, например: hit_BmwM5 приписан к BmwM5 (05)",
		default="",
		maxlen=30,
		)

	addBlockName1_string : bpy.props.StringProperty(
		name="Присоединённый блок",
		description="Имя блока, который будет приписан к текущему блоку, например: hit_BmwM5 приписан к BmwM5 (05)",
		default="",
		maxlen=30,
		)

	addSpaceName_string : bpy.props.StringProperty(
		name="Используемый локатор",
		description="Имя блока, который будет использоваться в качестве локатора для привязанного блока, например: AirportSpace и Airport",
		default="",
		maxlen=30,
		)

	addSpaceName1_string : bpy.props.StringProperty(
		name="Используемый локатор",
		description="Имя блока, который будет использоваться в качестве локатора для привязанного блока, например: AirportSpace и Airport",
		default="",
		maxlen=30,
		)

	add24Flag_enum : bpy.props.EnumProperty(
		name="Флаг",
		items=[ ('0', "0", "Присоединённый объект не будет отображаться"),
				('1', "1", "Присоединённый объект будет отображаться"),
				]
		)

	add24Flag_enum1 : bpy.props.EnumProperty(
		name="Флаг",
		items=[ ('0', "0", "Присоединённый объект не будет отображаться"),
				('1', "1", "Присоединённый объект будет отображаться"),
				]
		)

	TGType_int : bpy.props.IntProperty(
		name = "Тип модели дерева",
		description="",
		)

	Scale : bpy.props.FloatProperty(
		name = "Масштаб генератора",
		description="",
		min=0.0,
		default=9.5,
		)

	generatorType_enum : bpy.props.EnumProperty(
		name="Тип генератора",
		items=[ ('$SeaGenerator', "$SeaGenerator", ""),
				('$$TreeGenerator1', "$$TreeGenerator1", ""),
				('$$TreeGenerator', "$$TreeGenerator", ""),
				('$$CollisionOfTerrain', "$$CollisionOfTerrain", ""),
				('$$GeneratorOfTerrain', "$$GeneratorOfTerrain", ""),
				('$$People', "$$People", ""),
				('$$WeldingSparkles', "$$WeldingSparkles", ""),
				('$$DynamicGlow', "$$DynamicGlow", ""),
				('$$StaticGlow', "$$StaticGlow", ""),
				]
		)

	groupsNum_int : bpy.props.IntProperty(
		name = "Кол-во групп",
		description="Кол-во переключаемых групп.",
		)

	groupsNum1_int : bpy.props.IntProperty(
		name = "Кол-во групп",
		description="Кол-во переключаемых групп.",
		)

	Refer_bool = bpy.props.BoolProperty(
		name="refer",
		description="",
		default = False
		)

	Type21_enum : bpy.props.EnumProperty(
		name="Имя 21 блока",
		items=[ ('GeometryKey', "GeometryKey", ""),
				('CollisionKey', "CollisionKey", ""),
				('GlassKey', "GlassKey", ""),
				('RD_LampKey', "RD_LampKey", ""),
				('RD_Key', "RD_Key", ""),
				('RedSvetKey', "RedSvetKey", ""),
				('GreenSvetKey', "GreenSvetKey", ""),
				('TrafficLightKey0', "TrafficLightKey0", ""),
				('TrafficLightKey1', "TrafficLightKey1", ""),
				('ILLUM_LEVEL_00', "ILLUM_LEVEL_00", ""),
				('ILLUM_LEVEL_01', "ILLUM_LEVEL_01", ""),
				('ILLUM_LEVEL_02', "ILLUM_LEVEL_02", ""),
				('ILLUM_LEVEL_03', "ILLUM_LEVEL_03", ""),
				('ILLUM_LEVEL_04', "ILLUM_LEVEL_04", ""),
				('ILLUM_LEVEL_05', "ILLUM_LEVEL_05", ""),
				('ILLUM_LEVEL_06', "ILLUM_LEVEL_06", ""),
				('ILLUM_LEVEL_07', "ILLUM_LEVEL_07", ""),
				('ILLUM_LEVEL_08', "ILLUM_LEVEL_08", ""),
				('ILLUM_LEVEL_09', "ILLUM_LEVEL_09", ""),
				('ILLUM_LEVEL_10', "ILLUM_LEVEL_10", ""),
				('ILLUM_LEVEL_11', "ILLUM_LEVEL_11", ""),
				('ILLUM_LEVEL_12', "ILLUM_LEVEL_12", ""),
				('ILLUM_LEVEL_13', "ILLUM_LEVEL_13", ""),
				('ILLUM_LEVEL_14', "ILLUM_LEVEL_14", ""),
				('ILLUM_LEVEL_15', "ILLUM_LEVEL_15", ""),
				('Damage1Key', "Damage1Key", ""),
				('DamageFRKey', "DamageFRKey", ""),
				('DamageFCKey', "DamageFCKey", ""),
				('DamageFLKey', "DamageFLKey", ""),
				('DamageRKey', "DamageRKey", ""),
				('DamageLKey', "DamageLKey", ""),
				('DamageBRKey', "DamageBRKey", ""),
				('DamageBCKey', "DamageBCKey", ""),
				('DamageBLKey', "DamageBLKey", ""),
				('DamageWheel0Key', "DamageWheel0Key", ""),
				('DamageWheel1Key', "DamageWheel1Key", ""),
				('DamageWheel2Key', "DamageWheel2Key", ""),
				('DamageWheel3Key', "DamageWheel3Key", ""),
				('DamageWheel4Key', "DamageWheel4Key", ""),
				('DamageWheel5Key', "DamageWheel5Key", ""),
				('DamageWheel6Key', "DamageWheel6Key", ""),
				('DamageWheel7Key', "DamageWheel7Key", ""),
				('HeadLightKey', "HeadLightKey", ""),
				('BackFaraKeyR', "BackFaraKeyR", ""),
				('StopFaraKeyR', "StopFaraKeyR", ""),
				('BackFaraKeyL', "BackFaraKeyL", ""),
				('StopFaraKeyL', "StopFaraKeyL", ""),
				('IconKey', "IconKey", ""),
				('SizeLightKey', "SizeLightKey", ""),
				('HornKey', "HornKey", ""),
				('SupportKey', "SupportKey", ""),
				('CopSirenKey', "CopSirenKey", ""),
				('CopLightKey', "CopLightKey", ""),
				('GunRightKey', "GunRightKey", ""),
				('GunLeftKey', "GunLeftKey", ""),
				('StaticLightKey', "StaticLightKey", ""),
				('BlinkLightKey', "BlinkLightKey", ""),
				('SearchLightKey', "SearchLightKey", ""),
				]
		)

	addGroupName_string : bpy.props.StringProperty(
		name="Имя группы",
		description="Имя переключаемой группы",
		default="",
		maxlen=30,
		)

	T14_enum : bpy.props.EnumProperty(
		name="Преднастройки",
		items=[ ('car', "Для транспорта", ""),
				('trl', "Для полуприцепа", ""),
				('trl_cyc', "Для полуприцепа-цистерны", ""),
				('clk', "Для коллизии", ""),
				]
		)

	T28_radius : bpy.props.FloatProperty(
		name = "Радиус спрайта",
		description = "Радиус плоскости спрайта",
		default = 1.0,
		min = 0.01,
		)

	T28_radius1 : bpy.props.FloatProperty(
		name = "Радиус спрайта",
		description = "Радиус плоскости спрайта",
		default = 1.0,
		min = 0.01,
		)

	CH : bpy.props.FloatProperty(
		name = "Высота коллизии",
		description = "Высота плоскости коллизии",
		)

	CH1 : bpy.props.FloatProperty(
		name = "Высота коллизии",
		description = "Высота плоскости коллизии",
		)

	RSound : bpy.props.FloatProperty(
		name = "Радиус звука",
		description = "Радиус звука",
		default = 10.0,
		min = 0.0,
		)

	RSound1 : bpy.props.FloatProperty(
		name = "Радиус звука",
		description = "Радиус звука",
		default = 10.0,
		min = 0.0,
		)

	addSoundName_string : bpy.props.StringProperty(
		name="Присоединённый звуковой файл",
		description="Имя звукового файла, который будет использоваться данным блоком",
		default="",
		maxlen=30,
		)

	addSoundName1_string : bpy.props.StringProperty(
		name="Присоединённый звуковой файл",
		description="Имя звукового файла, который будет использоваться данным блоком",
		default="",
		maxlen=30,
		)

	SLevel : bpy.props.FloatProperty(
		name = "Уровень громкости звука",
		description = "Уровень громкости звука",
		default = 1.0,
		min = 0.0,
		max = 1.0,
		)

	SLevel1 : bpy.props.FloatProperty(
		name = "Уровень громкости звука",
		description = "Уровень громкости звука",
		default = 1.0,
		min = 0.0,
		max = 1.0,
		)

	addRoomName_string : bpy.props.StringProperty(
		name="Присоединённая комната",
		description="Имя комнаты, которая будет загружена",
		default="",
		maxlen=30,
		)

	FType_enum : bpy.props.EnumProperty(
		name="Тип записи полигонов (08)",
		items=(('0', "Тип 0", "С нормалями"),
			   ('1', "Тип 1", "Без нормалей"),
			   ('2', "Тип 2", "С нормалями, UV разрывная"),
			   ('128', "Тип 128", ""),
			   ('144', "Тип 144", ""),
			   ),
		)

	Faces_enum : bpy.props.EnumProperty(
		name="Тип блока полигонов",
		items=(('8', "8", ""),
			   ('35', "35", ""),
			   ),
		)

	addBlockMeshType_enum : bpy.props.EnumProperty(
		name="Тип записи модели",
		items=[ ('auto', "Автоматический", "Экспортер сам определит, какой блок использовать (8, 35 или оба)"),
				('manual', "Ручной", "Будет записан блок, который выбран в настройках"),
			   ]
		)

	addMeshType_enum : bpy.props.EnumProperty(
		name="Тип записи полигонов",
		items=[ ('uv0', "Обычный", ""),
				('uv1', "С разрывной UV", ""),
			   ]
		)

	materialName_string : bpy.props.StringProperty(
		name="Имя материала",
		description="Имя материала, который будет использоваться генератором",
		default="",
		maxlen=10,
		)

	routeName_string : bpy.props.StringProperty(
		name="Имя участка карты",
		description="Имя участка карты, который будет загружен",
		default="",
		maxlen=2,
		)

	triggerType_enum : bpy.props.EnumProperty(
		name="Тип триггера",
		items=(('loader', "Загрузчик", "Загрузчик участков карты"),
			   ('radar0', "Радар 0", "Event 0"),
			   ('radar1', "Радар 1", "Event 1"),
			   ),
		)

	addBlockName4_string : bpy.props.StringProperty(
		name="Родительский блок",
		description="",
		default="",
		maxlen=30,
		)

	speed_limit : bpy.props.FloatProperty(
		name = "Ограничение скорости",
		description = "",
		default = 60.0,
		min = 0.0,
		)

	addBlocks_enum : bpy.props.EnumProperty(
		name="Тип сборки",
		items=[ ('room', "Комната", "Комната с коллизией"),
				#('07', "07", "Меш (ДБ1)"),
				#('10', "10", "LOD"),
				#('12', "12", "Плоскость коллизии"),
				#('14', "14", "Блок, связанный с автомобилями"),
				#('18', "18", "Связка локатора и 3D-модели, например: FiatWheel0Space и Single0Wheel14"),
				#('19', "19", "Контейнер, в отличие от блока типа 05, не имеет возможности привязки"),
				#('20', "20", "Плоская коллизия"),
				#('21', "21", "Контейнер с обработкой событий"),
				#('23', "23", "Объёмная коллизия"),
				#('24', "24", "Локатор"),
				#('28', "28", "3D-спрайт"),
				#('33', "33", "Источник света"),
				#('37', "37", "Меш"),
				#('40', "40", "Генератор объектов"),
			   ]
		)

	addRoomNameIndex_string : bpy.props.StringProperty(
		name="Имя комнаты",
		description="",
		default="aa_000",
		maxlen=30,
		)

	mirrorType_enum : bpy.props.EnumProperty(
		name="Тип блока",
		items=[ ('x', "x", ""),
				('y', "y", ""),
				('z', "z", ""),
			   ]
		)

# ------------------------------------------------------------------------
#	menus
# ------------------------------------------------------------------------

# class BasicMenu(bpy.types.Menu):
# 	bl_idname = "OBJECT_MT_select_test"
# 	bl_label = "Select"

# 	def draw(self, context):
# 		layout = self.layout

# 		# built-in example operators
# 		layout.operator("object.select_all", text="Select/Deselect All").action = 'TOGGLE'
# 		layout.operator("object.select_all", text="Inverse").action = 'INVERT'
# 		layout.operator("object.select_random", text="Random")

# ------------------------------------------------------------------------
#	operators / buttons
# ------------------------------------------------------------------------

class AddOperator(bpy.types.Operator):
	bl_idname = "wm.add_operator"
	bl_label = "Добавить блок на сцену"

	def execute(self, context):
		scene = context.scene
		mytool = scene.my_tool

		global block_type

		block_type = int(mytool.addBlockType_enum)

		global cursor_pos
		cursor_pos = bpy.context.scene.cursor_location

		object_name = mytool.BlockName_string

		if block_type == 6566754:
			object_name = "b3d"
			object = bpy.data.objects.new(object_name, None)
			object.location=(0.0,0.0,0.0)
			bpy.context.scene.objects.link(object)

		elif block_type == 0:
			object = bpy.data.objects.new(object_name, None)
			object.location=cursor_pos
			object['block_type'] = block_type
			# setAllObjsByType(context, object, b_1)
			# object['block_type'] = block_type
			# object['add_space'] = mytool.addSpaceName_string
			bpy.context.scene.objects.link(object)

		elif block_type == 1:
			object = bpy.data.objects.new(object_name, None)
			object.location=cursor_pos
			object['block_type'] = block_type
			setAllObjsByType(context, object, b_1)
			# object['block_type'] = block_type
			# object['add_space'] = mytool.addSpaceName_string
			# object['route_name'] = mytool.routeName_string
			bpy.context.scene.objects.link(object)

		elif block_type == 2:
			object = bpy.data.objects.new(object_name, None)
			object.location=cursor_pos
			object['block_type'] = block_type
			setAllObjsByType(context, object, b_2)
			# object['block_type'] = block_type
			# object['add_space'] = mytool.addSpaceName_string
			# object['route_name'] = mytool.routeName_string
			bpy.context.scene.objects.link(object)

		elif block_type == 3:
			object = bpy.data.objects.new(object_name, None)
			object.location=cursor_pos
			object['block_type'] = block_type
			setAllObjsByType(context, object, b_3)
			# object['block_type'] = block_type
			# object['node_radius'] = mytool.Radius
			bpy.context.scene.objects.link(object)

		elif block_type == 4:
			object = bpy.data.objects.new(object_name, None)
			object.location=cursor_pos #(0.0,0.0,0.0)
			object['block_type'] = block_type
			setAllObjsByType(context, object, b_4)
			# object['block_type'] = block_type
			# object['node_radius'] = mytool.Radius
			# object['add_name'] = mytool.addBlockName4_string
			# object['add_name1'] = mytool.addBlockName_string
			bpy.context.scene.objects.link(object)

		elif block_type == 5:
			object = bpy.data.objects.new(object_name, None)
			object.location=cursor_pos #(0.0,0.0,0.0)
			object['block_type'] = block_type
			setAllObjsByType(context, object, b_5)
			# object['block_type'] = block_type
			# object['node_radius'] = mytool.Radius
			# object['add_name'] = mytool.addBlockName_string
			bpy.context.scene.objects.link(object)

		elif block_type == 6:
			object = bpy.data.objects.new(object_name, None)
			object.location=cursor_pos #(0.0,0.0,0.0)
			object['block_type'] = block_type
			setAllObjsByType(context, object, b_6)
			bpy.context.scene.objects.link(object)

		elif block_type == 7:
			object = bpy.data.objects.new(object_name, None)
			object.location=cursor_pos #(0.0,0.0,0.0)
			object['block_type'] = block_type
			setAllObjsByType(context, object, b_7)
			bpy.context.scene.objects.link(object)

		elif block_type == 8:
			object = bpy.data.objects.new(object_name, None)
			object.location=cursor_pos #(0.0,0.0,0.0)
			object['block_type'] = block_type
			setAllObjsByType(context, object, b_8)
			bpy.context.scene.objects.link(object)

		elif block_type == 9:
			object = bpy.data.objects.new(object_name, None)
			object.location=cursor_pos #(0.0,0.0,0.0)
			object['block_type'] = block_type
			setAllObjsByType(context, object, b_9)
			bpy.context.scene.objects.link(object)

		elif block_type == 10:
			object = bpy.data.objects.new(object_name, None)
			object.location=cursor_pos
			object['block_type'] = block_type
			setAllObjsByType(context, object, b_10)
			# object['block_type'] = block_type
			# object['node_radius'] = mytool.Radius
			# object['lod_distance'] = mytool.LOD_Distance
			bpy.context.scene.objects.link(object)

		elif block_type == 11:
			object = bpy.data.objects.new(object_name, None)
			object.location=cursor_pos
			object['block_type'] = block_type
			setAllObjsByType(context, object, b_11)
			bpy.context.scene.objects.link(object)

		elif block_type == 12:
			object = bpy.data.objects.new(object_name, None)
			object.location=cursor_pos
			object['block_type'] = block_type
			setAllObjsByType(context, object, b_12)
			# object['block_type'] = block_type
			# object['pos'] = 1
			# object['height'] = mytool.CH
			# object['CType'] = int(mytool.CollisionType_enum)
			bpy.context.scene.objects.link(object)

		elif block_type == 13:
			object = bpy.data.objects.new(object_name, None)
			object.location=cursor_pos
			object['block_type'] = block_type
			setAllObjsByType(context, object, b_13)
			# object['block_type'] = block_type
			# if mytool.triggerType_enum == "loader":
			# 	object['type'] = "loader"
			# 	object['route_name'] = mytool.routeName_string
			# if mytool.triggerType_enum == "radar0":
			# 	object['type'] = "radar0"
			# 	object['var0'] = 30
			# 	object['var1'] = 3005
			# 	object['var2'] = 4
			# 	object['speed_limit'] = mytool.speed_limit
			# if mytool.triggerType_enum == "radar1":
			# 	object['type'] = "radar1"
			# 	object['var0'] = 30
			# 	object['var1'] = -1
			# 	object['var2'] = 4
			# 	object['speed_limit'] = mytool.speed_limit
			bpy.context.scene.objects.link(object)

		elif block_type == 14:
			object = bpy.data.objects.new(object_name, None)
			object.location=cursor_pos
			object['block_type'] = block_type
			setAllObjsByType(context, object, b_14)
			# if mytool.T14_enum == "car":
			# 	object['var0'] = 0
			# 	object['var1'] = mytool.Radius
			# 	object['var2'] = mytool.Radius/2
			# 	object['var3'] = 10
			# 	object['var4'] = 18
			# elif mytool.T14_enum == "trl":
			# 	object['var0'] = 0
			# 	object['var1'] = mytool.Radius
			# 	object['var2'] = mytool.Radius/2
			# 	object['var3'] = 16
			# 	object['var4'] = 25

			# elif mytool.T14_enum == "trl_cyc":
			# 	object['var0'] = 0
			# 	object['var1'] = mytool.Radius
			# 	object['var2'] = mytool.Radius/2
			# 	object['var3'] = 18
			# 	object['var4'] = 25

			# elif mytool.T14_enum == "clk":
			# 	object['var0'] = 0
			# 	object['var1'] = mytool.Radius * 0.08
			# 	object['var2'] = mytool.Radius * 0.51
			# 	object['var3'] = mytool.Radius
			# 	object['var4'] = 0
			# bpy.context.scene.objects.link(object)

		elif block_type == 15:
			object = bpy.data.objects.new(object_name, None)
			object.location=cursor_pos
			object['block_type'] = block_type
			setAllObjsByType(context, object, b_15)
			bpy.context.scene.objects.link(object)

		elif block_type == 16:
			object = bpy.data.objects.new(object_name, None)
			object.location=cursor_pos
			object['block_type'] = block_type
			setAllObjsByType(context, object, b_16)
			bpy.context.scene.objects.link(object)

		elif block_type == 17:
			object = bpy.data.objects.new(object_name, None)
			object.location=cursor_pos
			object['block_type'] = block_type
			setAllObjsByType(context, object, b_17)
			bpy.context.scene.objects.link(object)

		elif block_type == 18:
			object = bpy.data.objects.new(object_name, None)
			object['block_type'] = block_type
			object.location=cursor_pos
			setAllObjsByType(context, object, b_18)
			# object['node_radius'] = mytool.Radius
			# object['add_name'] = mytool.addBlockName_string
			# object['space_name'] = mytool.addSpaceName_string
			bpy.context.scene.objects.link(object)

		elif block_type == 19:
			object = bpy.data.objects.new(object_name, None)
			object['block_type'] = block_type
			object.location=cursor_pos
			bpy.context.scene.objects.link(object)

		elif block_type == 20:
			points = [(0,0,0), (0,1,0)]
			curveData = bpy.data.curves.new('curve', type='CURVE')

			curveData.dimensions = '3D'
			curveData.resolution_u = 2

			polyline = curveData.splines.new('POLY')
			polyline.points.add(len(points)-1)
			for i, coord in enumerate(points):
				x,y,z = coord
				polyline.points[i].co = (x, y, z, 1)

			curveData.bevel_depth = 0.01
			object = bpy.data.objects.new(object_name, curveData)
			object.location = (0,0,0)
			object['block_type'] = block_type
			setAllObjsByType(context, object, b_20)
			#object = bpy.context.selected_objects[0]
			context.scene.objects.link(object)
			# object.name = mytool.BlockName_string

		elif block_type == 21:
			# if mytool.Refer_bool is False:
			# 	object_name = mytool.Type21_enum
			# else:
			# 	object_name = 'refer_' + mytool.Type21_enum
			# object = bpy.data.objects.new(object_name, None)
			# object['node_radius'] = mytool.Radius
			# object['groups_num'] = mytool.groupsNum_int
			object['block_type'] = block_type
			object.location=cursor_pos
			setAllObjsByType(context, object, b_20)
			bpy.context.scene.objects.link(object)
			# for i in range(mytool.groupsNum_int):
			# 	group = bpy.data.objects.new((mytool.addGroupName_string + str(i)), None)
			# 	group['block_type'] = 5
			# 	group['node_radius'] = mytool.Radius
			# 	group['add_name'] = ""
			# 	bpy.context.scene.objects.link(group)
			# 	group.parent = object
			# 	if (i < mytool.groupsNum_int - 1):
			# 		separator = bpy.data.objects.new((mytool.addGroupName_string + str(i) + "_444"), None)
			# 		separator['block_type'] = 444
			# 		bpy.context.scene.objects.link(separator)
			# 		separator.parent = object

		elif block_type == 22:
			object = bpy.data.objects.new(object_name, None)
			object.location=cursor_pos
			object['block_type'] = block_type
			setAllObjsByType(context, object, b_22)
			bpy.context.scene.objects.link(object)

		elif block_type == 23:
			object = bpy.data.objects.new(object_name, None)
			object.location=cursor_pos
			object['block_type'] = block_type
			setAllObjsByType(context, object, b_23)
			bpy.context.scene.objects.link(object)

		elif block_type == 24:
			# object = bpy.ops.mesh.primitive_ico_sphere_add(size=0.05, calc_uvs=True, location=(0.0,0.0,0.0))
			# object = bpy.context.selected_objects[0]
			object = bpy.data.objects.new(object_name, None)
			object.location=cursor_pos
			object['block_type'] = block_type
			setAllObjsByType(context, object, b_24)
			bpy.context.scene.objects.link(object)
			# object['flag'] = int(mytool.add24Flag_enum)
			# object.name = mytool.BlockName_string

		elif block_type == 25:
			object = bpy.data.objects.new(object_name, None)
			object.location=cursor_pos
			object['block_type'] = block_type
			setAllObjsByType(context, object, b_25)
			# object['sound_name'] = mytool.addSoundName_string
			# object['RSound'] = mytool.RSound
			# object['SLevel'] = mytool.SLevel
			bpy.context.scene.objects.link(object)

		elif block_type == 26:
			object = bpy.data.objects.new(object_name, None)
			object.location=cursor_pos
			object['block_type'] = block_type
			setAllObjsByType(context, object, b_26)
			bpy.context.scene.objects.link(object)

		elif block_type == 27:
			object = bpy.data.objects.new(object_name, None)
			object.location=cursor_pos
			object['block_type'] = block_type
			setAllObjsByType(context, object, b_27)
			bpy.context.scene.objects.link(object)

		elif block_type == 28:
			object = bpy.data.objects.new(object_name, None)
			object.location=cursor_pos
			object['block_type'] = block_type
			setAllObjsByType(context, object, b_28)
			# object['node_radius'] = mytool.Radius
			# object['sprite_radius'] = mytool.T28_radius
			# object['texNum'] = mytool.texNum_int
			bpy.context.scene.objects.link(object)

		elif block_type == 29:
			object = bpy.data.objects.new(object_name, None)
			object.location=cursor_pos
			object['block_type'] = block_type
			setAllObjsByType(context, object, b_29)
			bpy.context.scene.objects.link(object)

		elif block_type == 30:
			# object_name = mytool.BlockName_string

			# myvertex = []
			# myfaces = []

			# mypoint = [(0, -20, 0)]
			# myvertex.extend(mypoint)

			# mypoint = [(0, -20, 100)]
			# myvertex.extend(mypoint)

			# mypoint = [(0, 20, 100)]
			# myvertex.extend(mypoint)

			# mypoint = [(0, 20, 0)]
			# myvertex.extend(mypoint)

			# myface = [(0, 1, 2, 3)]
			# myfaces.extend(myface)


			# mymesh = bpy.data.meshes.new(object_name)

			# bpy.context.scene.objects.link(object)


			# mymesh.from_pydata(myvertex, [], myfaces)

			# mymesh.update(calc_edges=True)

			object = bpy.data.objects.new(object_name, None)

			object.location=cursor_pos
			object['block_type'] = block_type
			setAllObjsByType(context, object, b_30)
			# object['radius'] = mytool.Radius
			# object['room_name'] = mytool.addRoomName_string
			bpy.context.scene.objects.link(object)

		elif block_type == 31:
			object = bpy.data.objects.new(object_name, None)
			object.location=cursor_pos
			object['block_type'] = block_type
			setAllObjsByType(context, object, b_31)
			bpy.context.scene.objects.link(object)


		elif block_type == 33:
			object = bpy.data.objects.new(object_name, None)
			object.location=cursor_pos
			setAllObjsByType(context, object, b_33)
			# object['block_type'] = block_type
			# object['node_radius'] = mytool.Radius
			# object['light_radius'] = mytool.RadiusLight
			# object['light_type'] = int(mytool.LType_enum)
			# object['intensity'] = mytool.Intensity
			# object['R'] = mytool.R / 255
			# object['G'] = mytool.G / 255
			# object['B'] = mytool.B / 255
			bpy.context.scene.objects.link(object)

		elif block_type == 34:
			object = bpy.data.objects.new(object_name, None)
			object.location=cursor_pos
			object['block_type'] = block_type
			setAllObjsByType(context, object, b_34)
			bpy.context.scene.objects.link(object)

		elif block_type == 35:
			object = bpy.data.objects.new(object_name, None)
			object.location=cursor_pos
			object['block_type'] = block_type
			setAllObjsByType(context, object, b_35)
			bpy.context.scene.objects.link(object)

		elif block_type == 36:
			object = bpy.data.objects.new(object_name, None)
			object.location=cursor_pos
			object['block_type'] = block_type
			setAllObjsByType(context, object, b_36)
			bpy.context.scene.objects.link(object)

		elif block_type == 37:
			object = bpy.data.objects.new(object_name, None)
			object.location=cursor_pos
			object['block_type'] = block_type
			setAllObjsByType(context, object, b_37)
			bpy.context.scene.objects.link(object)

		elif block_type == 39:
			object = bpy.data.objects.new(object_name, None)
			object.location=cursor_pos
			object['block_type'] = block_type
			setAllObjsByType(context, object, b_39)
			bpy.context.scene.objects.link(object)

		elif block_type == 40:
			object = bpy.data.objects.new(object_name, None)
			object.location=cursor_pos
			object['block_type'] = block_type
			setAllObjsByType(context, object, b_40)
			bpy.context.scene.objects.link(object)
			# if mytool.generatorType_enum == "$$TreeGenerator1":
			# 	point = bpy.ops.mesh.primitive_ico_sphere_add(size=0.05, calc_uvs=True, enter_editmode=True, location=(0.0,0.0,0.0))
			# 	mesh0 = bpy.ops.mesh.primitive_cone_add(vertices=12, radius1=0.5, radius2=0.0, depth=1.0, end_fill_type='NGON', calc_uvs=True, enter_editmode=True, location=(0.0, 0.0, 1.0))
			# 	mesh1 = bpy.ops.mesh.primitive_cone_add(vertices=12, radius1=0.3, radius2=0.0, depth=0.6, end_fill_type='NGON', calc_uvs=True, enter_editmode=True, location=(0.0, 0.0, 1.4))
			# 	tree = bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.05, depth=0.5, end_fill_type='NGON', calc_uvs=True, enter_editmode=True, location=(0.0, 0.0, 0.25))
			# 	object = bpy.context.selected_objects[0]
			# 	object['block_type'] = block_type
			# 	object['scale'] = mytool.Scale
			# 	object['TGType'] = mytool.TGType_int
			# 	object['GType'] = mytool.generatorType_enum
			# 	object.name = mytool.BlockName_string
			# 	bpy.ops.object.mode_set(mode = 'OBJECT')
			# 	object.location = bpy.context.scene.cursor_location

			# if mytool.generatorType_enum == "$$DynamicGlow":
			# 	object = bpy.data.objects.new(object_name, None)
			# 	object.location=cursor_pos

			# 	object['block_type'] = block_type
			# 	object['node_radius'] = mytool.Radius
			# 	object['scale'] = mytool.Scale
			# 	object['mat_name'] = mytool.materialName_string
			# 	object['GType'] = mytool.generatorType_enum
			# 	object.name = mytool.BlockName_string
			# 	bpy.context.scene.objects.link(object)

		# if block_type == 444:
		# 	object = bpy.data.objects.new(object_name, None)
		# 	object['block_type'] = 444
		# 	object.location=(0.0,0.0,0.0)
		# 	bpy.context.scene.objects.link(object)
		return {'FINISHED'}

class GetValuesOperator(bpy.types.Operator):
	bl_idname = "wm.get_values_operator"
	bl_label = "Получить настройки блока"

	def execute(self, context):
		scene = context.scene
		mytool = scene.my_tool

		global block_type
		global lenStr
		object = bpy.context.selected_objects[0]
		block_type = object['block_type']

		if block_type == 1:
			getAllObjsByType(context, object, b_1)

		elif block_type == 2:
			getAllObjsByType(context, object, b_2)

		elif block_type == 3:
			getAllObjsByType(context, object, b_3)

		elif block_type == 4:
			getAllObjsByType(context, object, b_4)

		elif block_type == 5:
			# for f in block_5.__dict__['__annotations__'].keys():
			# 	mytool.block_5[f] = object[f]
			getAllObjsByType(context, object, b_5)
			# mytool.block_5[prop(b_5.Name1)] = object[prop(b_5.Name1)]
			# mytool.block_5[prop(b_5.XYZ)] = object[prop(b_5.XYZ)]
			# mytool.block_5[prop(b_5.R)] = object[prop(b_5.R)]

		elif block_type == 6:
			getAllObjsByType(context, object, b_6)

		elif block_type == 7:
			getAllObjsByType(context, object, b_7)
			# if 'BType' in object:
			# 	mytool.Faces_enum = str(object['BType'])
			# else:
			# 	mytool.Faces_enum = str(35)
			# 	object['BType'] = 35
			# if "type1" in object:
			# 	mytool.addBlockMeshType_enum = str(object['type1'])
			# else:
			# 	object['type1'] = "manual"
			# 	mytool.addBlockMeshType_enum = str(object['type1'])
			# mytool.MType_enum = str(object['MType'])
			# mytool.FType_enum = str(object['FType'])
			# mytool.texNum_int = object['texNum']

		elif block_type == 8:
			getAllObjsByType(context, object, b_8)

		elif block_type == 9:
			getAllObjsByType(context, object, b_9)

		elif block_type == 10:
			getAllObjsByType(context, object, b_10)
			# mytool.Radius1 = object['node_radius']
			# mytool.LOD_Distance1 = object['lod_distance']

		elif block_type == 11:
			getAllObjsByType(context, object, b_11)

		elif block_type == 12:
			getAllObjsByType(context, object, b_12)
			# mytool.CH1 = object['height']
			# mytool.CollisionType_enum = object['CType']

		elif block_type == 13:
			getAllObjsByType(context, object, b_13)

		elif block_type == 14:
			getAllObjsByType(context, object, b_14)

		elif block_type == 15:
			getAllObjsByType(context, object, b_15)

		elif block_type == 16:
			getAllObjsByType(context, object, b_16)

		elif block_type == 17:
			getAllObjsByType(context, object, b_17)

		elif block_type == 18:
			getAllObjsByType(context, object, b_18)
			# mytool.Radius1 = object['node_radius']
			# mytool.addBlockName1_string = object['add_name']
			# mytool.addSpaceName1_string = object['space_name']

		elif block_type == 20:
			getAllObjsByType(context, object, b_20)

		elif block_type == 21:
			getAllObjsByType(context, object, b_21)
			# mytool.groupsNum1_int = object['groups_num']
			# mytool.Radius1 = object['node_radius']

		elif block_type == 22:
			getAllObjsByType(context, object, b_22)

		elif block_type == 23:
			getAllObjsByType(context, object, b_23)
			# mytool.CollisionType_enum = str(object['CType'])

		elif block_type == 24:
			getAllObjsByType(context, object, b_24)
			# mytool.add24Flag_enum1 = str(object['flag'])

		elif block_type == 25:
			getAllObjsByType(context, object, b_25)
			# mytool.RSound1 = (object['RSound'])
			# mytool.addSoundName1_string = object['sound_name']
			# mytool.SLevel1 = (object['SLevel'])

		elif block_type == 26:
			getAllObjsByType(context, object, b_26)

		elif block_type == 27:
			getAllObjsByType(context, object, b_27)

		elif block_type == 28:
			getAllObjsByType(context, object, b_28)
			# mytool.texNum_int = object['texNum']
			# mytool.T28_radius1 = object['sprite_radius']

		elif block_type == 29:
			getAllObjsByType(context, object, b_29)

		elif block_type == 30:
			getAllObjsByType(context, object, b_30)

		elif block_type == 31:
			getAllObjsByType(context, object, b_31)

		elif block_type == 33:
			getAllObjsByType(context, object, b_33)
			# mytool.Radius1 = object['node_radius']
			# mytool.LType_enum = str(object['light_type'])
			# mytool.RadiusLight1 = object['light_radius']
			# mytool.Intensity1 = object['intensity']
			# mytool.R1 = object['R'] * 255
			# mytool.G1 = object['G'] * 255
			# mytool.B1 = object['B'] * 255

		elif block_type == 34:
			getAllObjsByType(context, object, b_34)

		elif block_type == 35:
			getAllObjsByType(context, object, b_35)

		elif block_type == 36:
			getAllObjsByType(context, object, b_36)

		elif block_type == 37:
			getAllObjsByType(context, object, b_37)
			# if 'BType' in object:
			# 	mytool.Faces_enum = str(object['BType'])
			# else:
			# 	mytool.Faces_enum = str(35)
			# 	object['BType'] = 35
			# if "type1" in object:
			# 	mytool.addBlockMeshType_enum = str(object['type1'])
			# else:
			# 	object['type1'] = "manual"
			# 	mytool.addBlockMeshType_enum = str(object['type1'])
			# #mytool.addMeshType_enum = str(object['type2'])
			# mytool.SType_enum = str(object['SType'])
			# mytool.MType_enum = str(object['MType'])
			# mytool.FType_enum = str(object['FType'])
			# mytool.texNum_int = object['texNum']

		elif block_type == 39:
			getAllObjsByType(context, object, b_39)

		elif block_type == 40:
			getAllObjsByType(context, object, b_40)

		return {'FINISHED'}

class SetValuesOperator(bpy.types.Operator):
	bl_idname = "wm.set_values_operator"
	bl_label = "Сохранить настройки блока"

	def execute(self, context):
		scene = context.scene
		mytool = scene.my_tool

		global block_type
		global lenStr
		#object = bpy.context.selected_objects[0]

		for i in range(len(bpy.context.selected_objects)):

			object = bpy.context.selected_objects[i]

			if 'block_type' in object:
				block_type = object['block_type']
			else:
				block_type = 0

			object['block_type'] = block_type

			if block_type == 1:
				setAllObjsByType(context, object, b_1)

			elif block_type == 2:
				setAllObjsByType(context, object, b_2)

			elif block_type == 3:
				setAllObjsByType(context, object, b_3)

			elif block_type == 4:
				setAllObjsByType(context, object, b_4)

			elif block_type == 5:
				setAllObjsByType(context, object, b_5)
				# object['add_name'] = mytool.addBlockName1_string
				# object['node_radius'] = mytool.Radius1

			elif block_type == 6:
				setAllObjsByType(context, object, b_6)


			elif block_type == 7:
				setAllObjsByType(context, object, b_7)
				# object['type1'] = str(mytool.addBlockMeshType_enum)
				# object['BType'] = int(mytool.Faces_enum)
				# object['FType'] = int(mytool.FType_enum)
				# object['MType'] = int(mytool.MType_enum)
				# object['texNum'] = int(mytool.texNum_int)

			elif block_type == 8:
				setAllObjsByType(context, object, b_8)

			elif block_type == 9:
				setAllObjsByType(context, object, b_9)

			elif block_type == 10:
				setAllObjsByType(context, object, b_10)
				# object['node_radius'] = mytool.Radius1
				# object['lod_distance'] = mytool.LOD_Distance1

			elif block_type == 11:
				setAllObjsByType(context, object, b_11)

			elif block_type == 12:
				setAllObjsByType(context, object, b_12)
				# object['height'] = mytool.CH1
				# object['CType'] = int(mytool.CollisionType_enum)

			elif block_type == 13:
				setAllObjsByType(context, object, b_13)

			elif block_type == 14:
				setAllObjsByType(context, object, b_14)

			elif block_type == 15:
				setAllObjsByType(context, object, b_15)

			elif block_type == 16:
				setAllObjsByType(context, object, b_16)

			elif block_type == 17:
				setAllObjsByType(context, object, b_17)

			elif block_type == 18:
				setAllObjsByType(context, object, b_18)
				# object['node_radius'] = mytool.Radius1
				# object['add_name'] = mytool.addBlockName1_string
				# object['space_name'] = mytool.addSpaceName1_string

			elif block_type == 20:
				setAllObjsByType(context, object, b_20)

			elif block_type == 21:
				setAllObjsByType(context, object, b_21)
				# object['groups_num'] = mytool.groupsNum1_int
				# object['node_radius'] = mytool.Radius1

			elif block_type == 22:
				setAllObjsByType(context, object, b_22)

			elif block_type == 23:
				setAllObjsByType(context, object, b_23)
				# object['CType'] = int(mytool.CollisionType_enum)

			elif block_type == 24:
				setAllObjsByType(context, object, b_24)
				# object['flag'] = int(mytool.add24Flag_enum1)

			elif block_type == 25:
				setAllObjsByType(context, object, b_25)
				# object['RSound'] = mytool.RSound1
				# object['sound_name'] = mytool.addSoundName1_string
				# object['SLevel'] = mytool.SLevel1

			elif block_type == 26:
				setAllObjsByType(context, object, b_26)

			elif block_type == 27:
				setAllObjsByType(context, object, b_27)

			elif block_type == 28:
				setAllObjsByType(context, object, b_28)
				# object['texNum'] = mytool.texNum_int
				# object['node_radius'] = mytool.Radius1
				# object['sprite_radius'] = mytool.T28_radius1

			elif block_type == 29:
				setAllObjsByType(context, object, b_29)

			elif block_type == 30:
				setAllObjsByType(context, object, b_30)

			elif block_type == 31:
				setAllObjsByType(context, object, b_31)

			elif block_type == 33:
				setAllObjsByType(context, object, b_33)
				# object['node_radius'] = mytool.Radius1
				# object['light_type'] = int(mytool.LType_enum)
				# object['light_radius'] = mytool.RadiusLight1
				# object['intensity'] = mytool.Intensity1
				object['R'] = mytool.R1 / 255
				object['G'] = mytool.G1 / 255
				object['B'] = mytool.B1 / 255

			elif block_type == 34:
				setAllObjsByType(context, object, b_34)

			elif block_type == 35:
				setAllObjsByType(context, object, b_35)

			elif block_type == 36:
				setAllObjsByType(context, object, b_36)

			elif block_type == 37:
				setAllObjsByType(context, object, b_37)
				# object['type1'] = str(mytool.addBlockMeshType_enum)
				# # object['type2'] = str(mytool.addMeshType_enum)
				# object['BType'] = int(mytool.Faces_enum)
				# object['SType'] = int(mytool.SType_enum)
				# object['MType'] = int(mytool.MType_enum)
				# object['FType'] = int(mytool.FType_enum)
				# object['texNum'] = int(mytool.texNum_int)

			elif block_type == 39:
				setAllObjsByType(context, object, b_39)

			elif block_type == 40:
				setAllObjsByType(context, object, b_40)

		return {'FINISHED'}

class DelValuesOperator(bpy.types.Operator):
	bl_idname = "wm.del_values_operator"
	bl_label = "Удалить настройки блока"

	def execute(self, context):
		scene = context.scene
		mytool = scene.my_tool

		global block_type
		global lenStr
		#object = bpy.context.selected_objects[0]

		for i in range(len(bpy.context.selected_objects)):

			object = bpy.context.selected_objects[i]

			if 'block_type' in object:
				del object['block_type']

		return {'FINISHED'}

class FixUVOperator(bpy.types.Operator):
	bl_idname = "wm.fix_uv_operator"
	bl_label = "Исправить UV для экспорта"

	def execute(self, context):

		for i in range(len(bpy.context.selected_objects)):

			object = bpy.context.selected_objects[i]

			bpy.ops.object.mode_set(mode = 'EDIT')

			context = bpy.context
			obj = context.edit_object
			me = obj.data
			bm = bmesh.from_edit_mesh(me)
			# old seams
			old_seams = [e for e in bm.edges if e.seam]
			# unmark
			for e in old_seams:
				e.seam = False
			# mark seams from uv islands
			bpy.ops.uv.seams_from_islands()
			seams = [e for e in bm.edges if e.seam]
			# split on seams
			print(seams)
			print("salo 111")
			bmesh.ops.split_edges(bm, edges=seams)
			# re instate old seams.. could clear new seams.
			for e in old_seams:
				e.seam = True
			bmesh.update_edit_mesh(me)

			boundary_seams = [e for e in bm.edges if e.seam and e.is_boundary]

			bpy.ops.object.mode_set(mode = 'OBJECT')

		return {'FINISHED'}

class FixVertsOperator(bpy.types.Operator):
	bl_idname = "wm.fix_verts_operator"
	bl_label = "Исправить меш для экспорта"

	def execute(self, context):

		for i in range(len(bpy.context.selected_objects)):

			object = bpy.context.selected_objects[i]

			bpy.ops.object.mode_set(mode = 'EDIT')
			bpy.ops.mesh.select_mode(type="FACE")
			bpy.ops.mesh.select_all(action='DESELECT')
			bpy.ops.mesh.select_all(action='INVERT')
			bpy.ops.mesh.select_mode(type="VERT")
			bpy.ops.mesh.select_all(action='INVERT')
			bpy.ops.mesh.delete(type='VERT')

			bpy.ops.object.mode_set(mode = 'OBJECT')

		return {'FINISHED'}

class MirrorAndFlipObjectsOperator(bpy.types.Operator):
	bl_idname = "wm.mirror_objects_operator"
	bl_label = "Отзеркалить объекты"

	def execute(self, context):
		scene = context.scene
		mytool = scene.my_tool

		x = False
		y = False
		z = False

		if (mytool.mirrorType_enum) == "x":
			x = True
		else:
			x = False

		if (mytool.mirrorType_enum) == "y":
			y = True
		else:
			y = False

		if (mytool.mirrorType_enum) == "z":
			z = True
		else:
			z = False

		for object in context.selected_objects:
			if object.type == 'MESH':
				#object = bpy.context.selected_objects[i]
				bpy.ops.transform.mirror(constraint_axis=(x, y, z), constraint_orientation='GLOBAL')
				bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

				#if object.type == 'MESH':
				bpy.ops.object.mode_set(mode = 'EDIT')
				bpy.ops.mesh.select_mode(type="FACE")
				bpy.ops.mesh.select_all(action='DESELECT')
				bpy.ops.mesh.select_all(action='INVERT')
				bpy.ops.mesh.flip_normals()
				bpy.ops.mesh.select_all(action='DESELECT')
				bpy.ops.object.mode_set(mode = 'OBJECT')




		#bpy.ops.object.mode_set(mode = 'OBJECT')

		return {'FINISHED'}

class ApplyTransformsOperator(bpy.types.Operator):
	bl_idname = "wm.apply_transforms_operator"
	bl_label = "Расположить/Убрать обьекты"

	def execute(self, context):
		scene = context.scene
		mytool = scene.my_tool

		applyRemoveTransforms()

		return {'FINISHED'}

class ShowHideCollisionsOperator(bpy.types.Operator):
	bl_idname = "wm.show_hide_collisions_operator"
	bl_label = "Отобразить/Скрыть коллизии"

	def execute(self, context):
		scene = context.scene
		mytool = scene.my_tool

		showHideObjByType(23)

		return {'FINISHED'}

class ShowHideRoomBordersOperator(bpy.types.Operator):
	bl_idname = "wm.show_hide_room_borders_operator"
	bl_label = "Отобразить/Скрыть границы комнат"

	def execute(self, context):
		scene = context.scene
		mytool = scene.my_tool

		showHideObjByType(30)

		return {'FINISHED'}

class ShowLODOperator(bpy.types.Operator):
	bl_idname = "wm.show_lod_operator"
	bl_label = "Отобразить LOD модели"

	def execute(self, context):
		scene = context.scene
		mytool = scene.my_tool

		objs = context.selected_objects
		if not len(objs):
			objs = [cn for cn in bpy.data.objects if cn.parent is None]

		for obj in objs:
			showLOD(obj)

		return {'FINISHED'}

class HideLODOperator(bpy.types.Operator):
	bl_idname = "wm.hide_lod_operator"
	bl_label = "Скрыть LOD модели"

	def execute(self, context):
		scene = context.scene
		mytool = scene.my_tool

		objs = context.selected_objects
		if not len(objs):
			objs = [cn for cn in bpy.data.objects if cn.parent is None]

		for obj in objs:
			hideLOD(obj)

		return {'FINISHED'}

class ShowHideGeneratorsOperator(bpy.types.Operator):
	bl_idname = "wm.show_hide_generator_operator"
	bl_label = "Отобразить/Скрыть генераторы обьектов"

	def execute(self, context):
		scene = context.scene
		mytool = scene.my_tool

		showHideObjByType(40)

		return {'FINISHED'}

class ShowConditionalsOperator(bpy.types.Operator):
	bl_idname = "wm.show_conditional_operator"
	bl_label = "Отобразить обьекты с условием"

	group : bpy.props.IntProperty()

	def execute(self, context):
		scene = context.scene
		mytool = scene.my_tool

		objs = context.selected_objects
		if not len(objs):
			objs = [cn for cn in bpy.data.objects if cn.parent is None]

		for obj in objs:
			showConditionals(obj, self.group)

		return {'FINISHED'}

class HideConditionalsOperator(bpy.types.Operator):
	bl_idname = "wm.hide_conditional_operator"
	bl_label = "Скрыть обьекты с условием"

	group : bpy.props.IntProperty()

	def execute(self, context):
		scene = context.scene
		mytool = scene.my_tool

		objs = context.selected_objects
		if not len(objs):
			objs = [cn for cn in bpy.data.objects if cn.parent is None]

		print(objs)

		for obj in objs:
			hideConditionals(obj, self.group)
		# showHideObjByType(40)

		return {'FINISHED'}

class AddBlocksOperator(bpy.types.Operator):
	bl_idname = "wm.add1_operator"
	bl_label = "Добавить сборку блоков на сцену"

	def execute(self, context):
		scene = context.scene
		mytool = scene.my_tool

		global type

		type = mytool.addBlocks_enum

		global cursor_pos
		cursor_pos = bpy.context.scene.cursor_location

		def type05(name, radius, add_name):
			object_name = name
			object = bpy.data.objects.new(object_name, None)
			object['block_type'] = 5
			object.location=cursor_pos
			object['node_radius'] = radius
			object['add_name'] = add_name
			bpy.context.scene.objects.link(object)
			object.select = True

		def type19(name):
			object_name = name
			object = bpy.data.objects.new(object_name, None)
			object['block_type'] = 19
			object.location=cursor_pos
			bpy.context.scene.objects.link(object)
			object.select = True

		if type == "room":
			type19("room_" + mytool.addRoomNameIndex_string)
			room = bpy.context.selected_objects[0]

			type05(("road_" + mytool.addRoomNameIndex_string), mytool.Radius, ("hit_road_" + mytool.addRoomNameIndex_string))
			road = bpy.context.selected_objects[0]

			type05(("obj_" + mytool.addRoomNameIndex_string), mytool.Radius, ("hit_obj_" + mytool.addRoomNameIndex_string))
			obj = bpy.context.selected_objects[0]

			hit_road = type05(("hit_road_" + mytool.addRoomNameIndex_string), 0, "")
			hit_obj = type05(("hit_obj_" + mytool.addRoomNameIndex_string), 0, "")

			bpy.ops.object.select_all(action='DESELECT')

			room.select = True
			road.select = True
			obj.select = True

			bpy.context.scene.objects.active = room

			bpy.ops.object.parent_set()

			bpy.ops.object.select_all(action='DESELECT')

		return {'FINISHED'}

# ------------------------------------------------------------------------
# panels
# ------------------------------------------------------------------------


# ------------------------------------------------------------------------
# panels
# ------------------------------------------------------------------------

class OBJECT_PT_b3d_add_panel(bpy.types.Panel):
	bl_idname = "OBJECT_PT_b3d_add_panel"
	bl_label = "Добавление блоков"
	bl_space_type = "VIEW_3D"
	bl_region_type = getRegion()
	bl_category = "b3d Tools"
	#bl_context = "objectmode"

	@classmethod
	def poll(self,context):
		return context.object is not None

	def draw(self, context):
		layout = self.layout
		scene = context.scene
		mytool = scene.my_tool
		# print(type(mytool))
		# print(bpy.types.Scene.my_tool)
		# print(dir(bpy.types.Scene.my_tool))
		# print(dir(context.scene.my_tool))
		global block_type
		block_type = int(mytool.addBlockType_enum)

		self.layout.label(text="Тип блока:")
		layout.prop(mytool, "addBlockType_enum", text="")
		layout.prop(mytool, "BlockName_string")

		# if block_type == 6566754:
		# 	self.layout.label(text="Тип блока:")
		# 	layout.prop(mytool, "addBlockType_enum", text="")

		# if block_type == 0:
		# 	layout.prop(mytool, "BlockName_string")
		# 	self.layout.label(text="Тип блока:")
		# 	layout.prop(mytool, "addBlockType_enum", text="")
		# 	layout.prop(mytool, "addSpaceName_string")


		if block_type == 1:
			drawAllFieldsByType(self, context, b_1)
			# layout.prop(mytool, "BlockName_string")
			# self.layout.label(text="Тип блока:")
			# layout.prop(mytool, "addBlockType_enum", text="")
			# layout.prop(mytool, "addSpaceName_string")
			# layout.prop(mytool, "routeName_string")

		elif block_type == 2:
			drawAllFieldsByType(self, context, b_2)

		elif block_type == 3:
			drawAllFieldsByType(self, context, b_3)
			# layout.prop(mytool, "BlockName_string")
			# self.layout.label(text="Тип блока:")
			# layout.prop(mytool, "addBlockType_enum", text="")
			# layout.prop(mytool, "Radius")

		elif block_type == 4:
			drawAllFieldsByType(self, context, b_4)
			# layout.prop(mytool, "BlockName_string")
			# self.layout.label(text="Тип блока:")
			# layout.prop(mytool, "addBlockType_enum", text="")
			# layout.prop(mytool, "Radius")
			# layout.prop(mytool, "addBlockName4_string")
			# layout.prop(mytool, "addBlockName_string")

		elif block_type == 5:
			drawAllFieldsByType(self, context, b_5)
			# layout.prop(mytool, "BlockName_string")
			# self.layout.label(text="Тип блока:")
			# layout.prop(mytool, "addBlockType_enum", text="")
			# layout.prop(mytool, "addBlockName_string")
			# layout.prop(mytool, "Radius")

		elif block_type == 6:
			drawAllFieldsByType(self, context, b_6)

		elif block_type == 7:
			drawAllFieldsByType(self, context, b_7)

		elif block_type == 8:
			drawAllFieldsByType(self, context, b_8)

		elif block_type == 9:
			drawAllFieldsByType(self, context, b_9)

		elif block_type == 10:
			drawAllFieldsByType(self, context, b_10)
			# layout.prop(mytool, "BlockName_string")
			# self.layout.label(text="Тип блока:")
			# layout.prop(mytool, "addBlockType_enum", text="")
			# layout.prop(mytool, "Radius")
			# layout.prop(mytool, "LOD_Distance")

		elif block_type == 11:
			drawAllFieldsByType(self, context, b_11)

		elif block_type == 12:
			drawAllFieldsByType(self, context, b_12)
			# layout.prop(mytool, "BlockName_string")
			# self.layout.label(text="Тип блока:")
			# layout.prop(mytool, "addBlockType_enum", text="")
			# layout.prop(mytool, "CH")
			# layout.prop(mytool, "CollisionType_enum")

		elif block_type == 13:
			drawAllFieldsByType(self, context, b_13)
			# layout.prop(mytool, "BlockName_string")
			# self.layout.label(text="Тип блока:")
			# layout.prop(mytool, "addBlockType_enum", text="")
			# layout.prop(mytool, "triggerType_enum", text="")
			# if mytool.triggerType_enum == "loader":
			# 	layout.prop(mytool, "routeName_string")
			# elif mytool.triggerType_enum == "radar0" or "radar1":
			# 	layout.prop(mytool, "speed_limit")

		elif block_type == 14:
			drawAllFieldsByType(self, context, b_14)
			# layout.prop(mytool, "BlockName_string")
			# self.layout.label(text="Тип блока:")
			# layout.prop(mytool, "addBlockType_enum", text="")
			# self.layout.label(text="Вариант преднастроек:")
			# layout.prop(mytool, "T14_enum", text="")
			# layout.prop(mytool, "Radius")

		elif block_type == 15:
			drawAllFieldsByType(self, context, b_15)

		elif block_type == 16:
			drawAllFieldsByType(self, context, b_16)

		elif block_type == 17:
			drawAllFieldsByType(self, context, b_17)

		elif block_type == 18:
			drawAllFieldsByType(self, context, b_18)
			# layout.prop(mytool, "BlockName_string")
			# self.layout.label(text="Тип блока:")
			# layout.prop(mytool, "addBlockType_enum", text="")
			# layout.prop(mytool, "Radius")
			# layout.prop(mytool, "addBlockName_string")
			# layout.prop(mytool, "addSpaceName_string")

		elif block_type == 19:
			pass
			# layout.prop(mytool, "BlockName_string")
			# self.layout.label(text="Тип блока:")
			# layout.prop(mytool, "addBlockType_enum", text="")

		elif block_type == 20:
			drawAllFieldsByType(self, context, b_20)
			# layout.prop(mytool, "BlockName_string")
			# self.layout.label(text="Тип блока:")
			# layout.prop(mytool, "addBlockType_enum", text="")

		elif block_type == 21:
			drawAllFieldsByType(self, context, b_21)
			# self.layout.label(text="Имя блока:")
			# layout.prop(mytool, "Type21_enum", text="")
			# layout.prop(mytool, "Refer_bool")
			# self.layout.label(text="Тип блока:")
			# layout.prop(mytool, "addBlockType_enum", text="")
			# layout.prop(mytool, "Radius")
			# layout.prop(mytool, "groupsNum_int")
			# layout.prop(mytool, "addGroupName_string")

		elif block_type == 22:
			drawAllFieldsByType(self, context, b_22)

		elif block_type == 23:
			drawAllFieldsByType(self, context, b_23)

		elif block_type == 24:
			drawAllFieldsByType(self, context, b_24)
			# layout.prop(mytool, "BlockName_string")
			# self.layout.label(text="Тип блока:")
			# layout.prop(mytool, "addBlockType_enum", text="")
			# self.layout.label(text="Флаг:")
			# layout.prop(mytool, "add24Flag_enum", text="")

		elif block_type == 25:
			drawAllFieldsByType(self, context, b_25)
			# layout.prop(mytool, "BlockName_string")
			# self.layout.label(text="Тип блока:")
			# layout.prop(mytool, "addBlockType_enum", text="")
			# layout.prop(mytool, "addSoundName_string")
			# layout.prop(mytool, "RSound")
			# layout.prop(mytool, "SLevel")

		elif block_type == 26:
			drawAllFieldsByType(self, context, b_26)

		elif block_type == 27:
			drawAllFieldsByType(self, context, b_27)

		elif block_type == 28:
			drawAllFieldsByType(self, context, b_28)
			# layout.prop(mytool, "BlockName_string")
			# self.layout.label(text="Тип блока:")
			# layout.prop(mytool, "addBlockType_enum", text="")
			# layout.prop(mytool, "Radius")
			# layout.prop(mytool, "T28_radius")
			# layout.prop(mytool, "texNum_int")

		elif block_type == 29:
			drawAllFieldsByType(self, context, b_29)

		elif block_type == 30:
			drawAllFieldsByType(self, context, b_30)
			# layout.prop(mytool, "BlockName_string")
			# self.layout.label(text="Тип блока:")
			# layout.prop(mytool, "addBlockType_enum", text="")
			# layout.prop(mytool, "Radius")
			# layout.prop(mytool, "addRoomName_string")

		elif block_type == 31:
			drawAllFieldsByType(self, context, b_31)

		elif block_type == 33:
			drawAllFieldsByType(self, context, b_33)
			# layout.prop(mytool, "BlockName_string")
			# self.layout.label(text="Тип блока:")
			# layout.prop(mytool, "addBlockType_enum", text="")
			# layout.prop(mytool, "LType_enum")
			# layout.prop(mytool, "Radius")
			# layout.prop(mytool, "RadiusLight")
			# layout.prop(mytool, "Intensity")
			# layout.prop(mytool, "R")
			# layout.prop(mytool, "G")
			# layout.prop(mytool, "B")

		elif block_type == 34:
			drawAllFieldsByType(self, context, b_34)

		elif block_type == 35:
			drawAllFieldsByType(self, context, b_35)

		elif block_type == 36:
			drawAllFieldsByType(self, context, b_36)

		elif block_type == 37:
			drawAllFieldsByType(self, context, b_37)

		elif block_type == 39:
			drawAllFieldsByType(self, context, b_39)

		elif block_type == 40:
			drawAllFieldsByType(self, context, b_40)
			# layout.prop(mytool, "BlockName_string")
			# layout.prop(mytool, "Radius")
			# self.layout.label(text="Тип блока:")
			# layout.prop(mytool, "addBlockType_enum", text="")
			# self.layout.label(text="Тип генератора:")
			# layout.prop(mytool, "generatorType_enum", text="")
			# if mytool.generatorType_enum == "$$TreeGenerator1":
			# 	layout.prop(mytool, "TGType_int")
			# 	layout.prop(mytool, "Scale")
			# if mytool.generatorType_enum == "$$DynamicGlow":
			# 	layout.prop(mytool, "materialName_string")
			# 	layout.prop(mytool, "Scale")
			# else:
			# 	self.layout.label(text="Данный тип генератора не поддерживается.")

		# elif block_type == 444:
		# 	self.layout.label(text="Тип блока:")
		# 	layout.prop(mytool, "addBlockType_enum", text="")

		layout.operator("wm.add_operator")

class OBJECT_PT_b3d_edit_panel(bpy.types.Panel):
	bl_idname = "OBJECT_PT_b3d_edit_panel"
	bl_label = "Редактирование блоков"
	bl_space_type = "VIEW_3D"
	bl_region_type = getRegion()
	bl_category = "b3d Tools"
	#bl_context = "objectmode"

	@classmethod
	def poll(self,context):
		return context.object is not None

	def draw(self, context):
		layout = self.layout
		mytool = context.scene.my_tool

		type(context)
		#for i in range(len(bpy.context.selected_objects)):

		if len(bpy.context.selected_objects):
			for i in range(1):

				object = bpy.context.selected_objects[i]

				level_group = None

				if 'block_type' in object:
					block_type = object['block_type']
				else:
					block_type = None

				if 'level_group' in object:
					level_group = object['level_group']
				else:
					level_group = None

				lenStr = str(len(object.children))

				if block_type == 0:
					drawCommon(self, object)

				elif block_type == 1:
					drawCommon(self, object)
					drawAllFieldsByType(self, context, b_1)

				elif block_type == 2:
					drawCommon(self, object)
					drawAllFieldsByType(self, context, b_2)

				elif block_type == 3:
					drawCommon(self, object)
					drawAllFieldsByType(self, context, b_3)

				elif block_type == 4:
					drawCommon(self, object)
					drawAllFieldsByType(self, context, b_4)

				elif block_type == 5:
					drawCommon(self, object)
					drawAllFieldsByType(self, context, b_5)
					# layout.prop(getattr(mytool, 'block5'), "name1")
					# layout.prop(mytool.block5, "XYZ")
					# layout.prop(mytool.block5, "R")
					# if 'add_name' in object:
					# 	pass
					# else:
					# 	self.layout.label(text="Имя присоединённого блока не указано. Сохраните настройки,")
					# 	self.layout.label(text="а затем попробуйте выделить блок заново.")

				elif block_type == 6:
					drawCommon(self, object)
					drawAllFieldsByType(self, context, b_6)

				elif block_type == 7:
					drawCommon(self, object)
					drawAllFieldsByType(self, context, b_7)
					# if 'texNum' in object:
					# 	layout.prop(mytool, "addBlockMeshType_enum")

					# 	if (mytool.addBlockMeshType_enum) == "auto":
					# 		layout.prop(mytool, "FType_enum")
					# 		layout.prop(mytool, "MType_enum")
					# 	else:
					# 		layout.prop(mytool, "Faces_enum")
					# 		if int(mytool.Faces_enum) == 35:
					# 			layout.prop(mytool, "MType_enum")
					# 		else:
					# 			layout.prop(mytool, "FType_enum")

					# 	layout.prop(mytool, "texNum_int")
					# else:
					# 	self.layout.label(text="Указаны не все атрибуты объекта.")
					# 	self.layout.label(text="Сохраните настройки, а затем попробуйте выделить блок заново.")

				elif block_type == 8:
					drawCommon(self, object)
					drawAllFieldsByType(self, context, b_8)

				elif block_type == 9:
					drawCommon(self, object)
					drawAllFieldsByType(self, context, b_9)

				elif block_type == 10:
					drawCommon(self, object)
					drawAllFieldsByType(self, context, b_10)
					# if 'node_radius' in object:
					# 	layout.prop(mytool, "Radius1")
					# 	layout.prop(mytool, "LOD_Distance1")
					# else:
					# 	self.layout.label(text="Указаны не все атрибуты объекта.")
					# 	self.layout.label(text="Сохраните настройки, а затем попробуйте выделить блок заново.")

				elif block_type == 11:
					drawCommon(self, object)
					drawAllFieldsByType(self, context, b_11)

				elif block_type == 12:
					drawCommon(self, object)
					drawAllFieldsByType(self, context, b_12)
					# if 'CType' in object:
					# 	self.layout.label(text="Тип коллизии:")
					# 	layout.prop(mytool, "CollisionType_enum", text="")
					# 	layout.prop(mytool, "CH1")
					# else:
					# 	self.layout.label(text="Тип коллизии не указан. Сохраните настройки,")
					# 	self.layout.label(text="а затем попробуйте выделить блок заново.")

				elif block_type == 13:
					drawCommon(self, object)
					drawAllFieldsByType(self, context, b_13)

				elif block_type == 14:
					drawCommon(self, object)
					drawAllFieldsByType(self, context, b_14)

				elif block_type == 15:
					drawCommon(self, object)
					drawAllFieldsByType(self, context, b_15)

				elif block_type == 16:
					drawCommon(self, object)
					drawAllFieldsByType(self, context, b_16)

				elif block_type == 17:
					drawCommon(self, object)
					drawAllFieldsByType(self, context, b_17)

				elif block_type == 18:
					drawCommon(self, object)
					drawAllFieldsByType(self, context, b_18)
					# if 'add_name' in object:
					# 	layout.prop(mytool, "Radius1")
					# 	layout.prop(mytool, "addBlockName1_string")
					# 	layout.prop(mytool, "addSpaceName1_string")
					# else:
					# 	self.layout.label(text="Указаны не все атрибуты объекта.")
					# 	self.layout.label(text="Сохраните настройки, а затем попробуйте выделить блок заново.")

				elif block_type == 19:
					drawCommon(self, object)

				elif block_type == 20:
					drawCommon(self, object)
					drawAllFieldsByType(self, context, b_20)

				elif block_type == 21:
					drawCommon(self, object)
					drawAllFieldsByType(self, context, b_21)
					# if 'groups_num' in object:
					# 	layout.prop(mytool, "groupsNum1_int")
					# 	layout.prop(mytool, "Radius1")
					# else:
					# 	self.layout.label(text="Кол-во групп не указано. Сохраните настройки,")
					# 	self.layout.label(text="а затем попробуйте выделить блок заново.")

				elif block_type == 23:
					drawCommon(self, object)
					drawAllFieldsByType(self, context, b_23)
					# if 'CType' in object:
					# 	self.layout.label(text="Тип коллизии:")
					# 	layout.prop(mytool, "CollisionType_enum", text="")
					# else:
					# 	self.layout.label(text="Тип коллизии не указан. Сохраните настройки,")
					# 	self.layout.label(text="а затем попробуйте выделить блок заново.")

				elif block_type == 24:
					drawCommon(self, object)
					drawAllFieldsByType(self, context, b_24)
					# if 'flag' in object:
					# 	layout.prop(mytool, "add24Flag_enum1", text="")
					# else:
					# 	self.layout.label(text="Флаг блока не указан. Сохраните настройки,")
					# 	self.layout.label(text="а затем попробуйте выделить блок заново.")

				elif block_type == 25:
					drawCommon(self, object)
					drawAllFieldsByType(self, context, b_25)
					# if 'RSound' in object:
					# 	layout.prop(mytool, "addSoundName1_string")
					# 	layout.prop(mytool, "RSound1")
					# 	layout.prop(mytool, "SLevel1")
					# else:
					# 	self.layout.label(text="Указаны не все атрибуты объекта.")
					# 	self.layout.label(text="Сохраните настройки, а затем попробуйте выделить блок заново.")

				elif block_type == 26:
					drawCommon(self, object)
					drawAllFieldsByType(self, context, b_26)

				elif block_type == 27:
					drawCommon(self, object)
					drawAllFieldsByType(self, context, b_27)

				elif block_type == 28:
					drawCommon(self, object)
					drawAllFieldsByType(self, context, b_28)
					# if 'sprite_radius' in object:
					# 	layout.prop(mytool, "Radius1")
					# 	layout.prop(mytool, "T28_radius1")
					# 	layout.prop(mytool, "texNum_int")
					# else:
					# 	self.layout.label(text="Указаны не все атрибуты объекта.")
					# 	self.layout.label(text="Сохраните настройки, а затем попробуйте выделить блок заново.")

				elif block_type == 29:
					drawCommon(self, object)
					drawAllFieldsByType(self, context, b_29)

				elif block_type == 30:
					drawCommon(self, object)
					drawAllFieldsByType(self, context, b_30)

				elif block_type == 31:
					drawCommon(self, object)
					drawAllFieldsByType(self, context, b_31)

				# elif block_type == 32:
				# 	drawCommon(self, object)

				elif block_type == 33:
					drawCommon(self, object)
					drawAllFieldsByType(self, context, b_33)
					# layout.prop(mytool, "Radius1")
					# layout.prop(mytool, "LType_enum")
					# layout.prop(mytool, "RadiusLight1")
					# layout.prop(mytool, "Intensity1")
					# layout.prop(mytool, "R1")
					# layout.prop(mytool, "G1")
					# layout.prop(mytool, "B1")

				elif block_type == 34:
					drawCommon(self, object)
					drawAllFieldsByType(self, context, b_34)

				elif block_type == 35:
					drawCommon(self, object)
					drawAllFieldsByType(self, context, b_35)

				elif block_type == 36:
					drawCommon(self, object)
					drawAllFieldsByType(self, context, b_36)

				elif block_type == 37:
					drawCommon(self, object)
					drawAllFieldsByType(self, context, b_37)
					# if 'texNum' in object:
					# 	layout.prop(mytool, "addBlockMeshType_enum")

					# 	if (mytool.addBlockMeshType_enum) == "auto":
					# 		layout.prop(mytool, "SType_enum")
					# 		#layout.prop(mytool, "FType_enum")
					# 		#layout.prop(mytool, "addMeshType_enum")
					# 		layout.prop(mytool, "FType_enum")
					# 		layout.prop(mytool, "MType_enum")
					# 	else:
					# 		layout.prop(mytool, "Faces_enum")
					# 		if int(mytool.Faces_enum) == 35:
					# 			layout.prop(mytool, "MType_enum")
					# 			layout.prop(mytool, "SType_enum")
					# 		else:
					# 			layout.prop(mytool, "SType_enum")
					# 			layout.prop(mytool, "FType_enum")

					# 	layout.prop(mytool, "texNum_int")
					# else:
					# 	self.layout.label(text="Указаны не все атрибуты объекта.")
					# 	self.layout.label(text="Сохраните настройки, а затем попробуйте выделить блок заново.")

				# elif block_type == 38:
				# 	drawCommon(self, object)

				elif block_type == 39:
					drawCommon(self, object)
					drawAllFieldsByType(self, context, b_39)

				elif block_type == 40:
					drawCommon(self, object)
					drawAllFieldsByType(self, context, b_40)
					# self.layout.label(text="Тип генератора: " + object['GType'])

				# elif block_type == 444:
				# 	self.layout.label(text="Тип объекта - разделитель")

				else:
					self.layout.label(text="Выбранный объект не имеет типа.")
					self.layout.label(text="Чтобы указать его, нажмите на кнопку сохранения настроек.")

			layout.operator("wm.get_values_operator")
			layout.operator("wm.set_values_operator")
			layout.operator("wm.del_values_operator")
			layout.operator("wm.fix_uv_operator")
			layout.operator("wm.fix_verts_operator")

class OBJECT_PT_b3d_blocks_panel(bpy.types.Panel):
	bl_idname = "OBJECT_PT_b3d_blocks_panel"
	bl_label = "Сборки блоков"
	bl_space_type = "VIEW_3D"
	bl_region_type = getRegion()
	bl_category = "b3d Tools"
	#bl_context = "objectmode"

	@classmethod
	def poll(self,context):
		return context.object is not None

	def draw(self, context):
		layout = self.layout
		# print(dir(context))
		mytool = context.scene.my_tool

		type = mytool.addBlocks_enum

		# print(dir(mytool))

		layout.prop(mytool, "addBlocks_enum")

		if type == "room":
			layout.prop(mytool, "addRoomNameIndex_string")
			layout.prop(mytool, "Radius")

		layout.operator("wm.add1_operator")

class OBJECT_PT_b3d_func_panel(bpy.types.Panel):
	bl_idname = "OBJECT_PT_b3d_func_panel"
	bl_label = "Дополнительные функции"
	bl_space_type = "VIEW_3D"
	bl_region_type = getRegion()
	bl_category = "b3d Tools"
	#bl_context = "objectmode"

	@classmethod
	def poll(self,context):
		return context.object is not None

	def draw(self, context):
		layout = self.layout
		scene = context.scene
		mytool = scene.my_tool


		layout.prop(mytool, "mirrorType_enum")

		layout.operator("wm.mirror_objects_operator")
		layout.operator("wm.apply_transforms_operator")
		layout.operator("wm.show_hide_collisions_operator")
		layout.operator("wm.show_hide_room_borders_operator")
		layout.operator("wm.show_hide_generator_operator")

		box = layout.box()
		box.operator("wm.show_lod_operator")
		box.operator("wm.hide_lod_operator")

		box = layout.box()
		box.prop(mytool, "conditionGroup")
		oper = box.operator("wm.show_conditional_operator")
		oper.group = getattr(mytool, 'conditionGroup')
		oper = box.operator("wm.hide_conditional_operator")
		oper.group = getattr(mytool, 'conditionGroup')

class OBJECT_PT_b3d_misc_panel(bpy.types.Panel):
	bl_idname = "OBJECT_PT_b3d_misc_panel"
	bl_label = "О плагине"
	bl_space_type = "VIEW_3D"
	bl_region_type = getRegion()
	bl_category = "b3d Tools"
	#bl_context = "objectmode"

	@classmethod
	def poll(self,context):
		return context.object is not None

	def draw(self, context):
		layout = self.layout
		scene = context.scene
		mytool = scene.my_tool

		self.layout.label(text="Автор плагина: aleko2144")
		self.layout.label(text="vk.com/rnr_mods")
# ------------------------------------------------------------------------
# register and unregister
# ------------------------------------------------------------------------

_classes = (
	# 'b_1_gen',
	# 'b_2_gen',
	# 'b_3_gen',
	# 'b_4_gen',
	# 'b_5_gen',
	# 'b_6_gen',
	# 'b_7_gen',
	# 'b_8_gen',
	# 'b_9_gen',
	# 'b_10_gen',
	# 'b_11_gen',
	# 'b_12_gen',
	# 'b_13_gen',
	# 'b_14_gen',
	# 'b_15_gen',
	# 'b_16_gen',
	# 'b_17_gen',
	# 'b_18_gen',
	# 'b_20_gen',
	# 'b_21_gen',
	# 'b_22_gen',
	# 'b_23_gen',
	# 'b_24_gen',
	# 'b_25_gen',
	# 'b_26_gen',
	# 'b_27_gen',
	# 'b_28_gen',
	# 'b_29_gen',
	# 'b_30_gen',
	# 'b_31_gen',
	# 'b_33_gen',
	# 'b_34_gen',
	# 'b_35_gen',
	# 'b_36_gen',
	# 'b_37_gen',
	# 'b_39_gen',
	# 'b_40_gen',
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
	PanelSettings,
	AddOperator,
	OBJECT_PT_b3d_add_panel,
	GetValuesOperator,
	SetValuesOperator,
	DelValuesOperator,
	FixUVOperator,
	FixVertsOperator,
	MirrorAndFlipObjectsOperator,
	ApplyTransformsOperator,
	ShowHideCollisionsOperator,
	ShowHideRoomBordersOperator,
	ShowLODOperator,
	HideLODOperator,
	ShowHideGeneratorsOperator,
	ShowConditionalsOperator,
	HideConditionalsOperator,
	OBJECT_PT_b3d_edit_panel,
	AddBlocksOperator,
	OBJECT_PT_b3d_blocks_panel,
	OBJECT_PT_b3d_func_panel,
	OBJECT_PT_b3d_misc_panel,
)

def b3dpanel_register():
	for cls in _classes:
		bpy.utils.register_class(cls)
	bpy.types.Scene.my_tool = bpy.props.PointerProperty(type=PanelSettings)

def b3dpanel_unregister():
	del bpy.types.Scene.my_tool
	for cls in _classes:
		bpy.utils.unregister_class(cls)

