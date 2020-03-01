bl_info = {
	"name": "King of The Road Tools Panel for b3d exporter",
	"description": "",
	"author": "Andrey Prozhoga",
	"version": (0, 0, 5),
	"blender": (2, 79, 0),
	"location": "3D View > Tools",
	"warning": "",
	"wiki_url": "",
	"tracker_url": "vk.com/rnr_mods",
	"category": "Development"
}

import bpy

from bpy.props import (StringProperty,
						BoolProperty,
						IntProperty,
						FloatProperty,
						EnumProperty,
						PointerProperty,
						)

from bpy.types import (Panel,
						Operator,
						PropertyGroup,
						)

import bmesh
						
# ------------------------------------------------------------------------
#	store properties in the active scene
# ------------------------------------------------------------------------

class PanelSettings(PropertyGroup):

	#my_bool = BoolProperty(
	#	name="Enable or Disable",
	#	description="A bool property",
	#	default = False
	#	)

	#my_int = IntProperty(
	#	name = "Int Value",
	#	description="A integer property",
	#	default = 23,
	#	min = 10,
	#	max = 100
	#	)

	#my_float = FloatProperty(
	#	name = "Float Value",
	#	description = "A float property",
	#	default = 23.7,
	#	min = 0.01,
	#	max = 30.0
	#	)

	BlockName_string = StringProperty(
		name="Имя блока",
		default="",
		maxlen=30,
		)
		
	addBlockType_enum = EnumProperty(
		name="Тип блока",
		items=[ ('6566754', "b3d", "b3d"),
				('00', "00", "2D фон"),
				('01', "01", "Камера"),
				('03', "03", "Контейнер"),
				('04', "04", "Контейнер с возможностью привязки к нему других блоков"),
				('05', "05", "Контейнер с возможностью привязки к нему другого блока"),
				('10', "10", "LOD"),
				('12', "12", "Плоскость коллизии"),
				('13', "13", "Триггер (загрузчик карты)"),
				('14', "14", "Блок, связанный с автомобилями"),
				('18', "18", "Связка локатора и 3D-модели, например: FiatWheel0Space и Single0Wheel14"),
				('19', "19", "Контейнер, в отличие от блока типа 05, не имеет возможности привязки"),
				('20', "20", "Плоская коллизия"),
				('21', "21", "Контейнер с обработкой событий"),
				#('22', "22", "Блок-локатор"),
				#('23', "23", "Объёмная коллизия"),
				('24', "24", "Локатор"),
				('25', "25", "Звуковой объект"),
				('28', "28", "3D-спрайт"),
				#('25', "25", "Блок-локатор"),
				#('26', "26", "Блок-локатор"),
				#('27', "27", "Блок-локатор"),
				#('29', "29", "Блок-локатор"),
				('30', "30", "Триггер для загрузки участков карты"),
				#('31', "31", "Блок-локатор"),
				#('32', "32", "Блок-локатор"),
				('33', "33", "Источник света"),
				#('34', "34", "Блок-локатор"),
				#('35', "35", "Трисы модели"),
				#('36', "36", "Блок-локатор"),
				#('37', "37", "Вершины модели"),
				#('38', "38", "Блок-локатор"),
				#('39', "39", "Блок-локатор"),
				('40', "40", "Генератор объектов"),
				('444', "Разделитель", "Разделитель"),
			   ]
		)
		
	addBlockType_enum1 = EnumProperty(
		name="Тип блока",
		items=[ ('05', "05", "Контейнер с возможностью привязки к нему другого блока"),
				('07', "07", "Меш (ДБ1)"),
				('10', "10", "LOD"),
				('12', "12", "Плоскость коллизии"),
				('14', "14", "Блок, связанный с автомобилями"),
				('18', "18", "Связка локатора и 3D-модели, например: FiatWheel0Space и Single0Wheel14"),
				('19', "19", "Контейнер, в отличие от блока типа 05, не имеет возможности привязки"),
				('20', "20", "Плоская коллизия"),
				('21', "21", "Контейнер с обработкой событий"),
				('23', "23", "Объёмная коллизия"),
				('24', "24", "Локатор"),
				('28', "28", "3D-спрайт"),
				('33', "33", "Источник света"),
				('37', "37", "Меш"),
				('40', "40", "Генератор объектов"),
			   ]
		)
		
	CollisionType_enum = bpy.props.EnumProperty(
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
		
	Radius = FloatProperty(
		name = "Радиус блока",
		description = "Дальность прорисовки блока",
		default = 1.0,
		)
		
	Radius1 = FloatProperty(
		name = "Радиус блока",
		description = "Дальность прорисовки блока",
		default = 1.0,
		)
		
	LOD_Distance = FloatProperty(
		name = "Дальность отображения LOD",
		description = "Маскимальная дальность отображения LOD",
		default = 10.0,
		)
		
	LOD_Distance1 = FloatProperty(
		name = "Дальность отображения LOD",
		description = "Маскимальная дальность отображения LOD",
		default = 10.0,
		)
		
	Intensity = FloatProperty(
		name = "Интенсивность освещения",
		description = "Яркость источника света",
		default = 1.0,
		min = 0.0,
		)
		
	Intensity1 = FloatProperty(
		name = "Интенсивность освещения",
		description = "Яркость источника света",
		default = 1.0,
		min = 0.0,
		)
		
	R = FloatProperty(
		name = "R",
		description = "",
		default = 255,
		min = 0.0,
		max = 255,
		)
		
	G = FloatProperty(
		name = "G",
		description = "",
		default = 255,
		min = 0.0,
		max = 255,
		)
		
	B = FloatProperty(
		name = "B",
		description = "",
		default = 255,
		min = 0.0,
		max = 255,
		)
		
	R1 = FloatProperty(
		name = "R",
		description = "",
		default = 255,
		min = 0.0,
		max = 255,
		)
		
	G1 = FloatProperty(
		name = "G",
		description = "",
		default = 255,
		min = 0.0,
		max = 255,
		)
		
	B1 = FloatProperty(
		name = "B",
		description = "",
		default = 255,
		min = 0.0,
		max = 255,
		)
		
	RadiusLight = FloatProperty(
		name = "Радиус освещения",
		description = "",
		default = 1,
		min = 0.0,
		)
		
	RadiusLight1 = FloatProperty(
		name = "Радиус освещения",
		description = "",
		default = 1,
		min = 0.0,
		)
		
	SType_enum = bpy.props.EnumProperty(
		name="Тип записи вершин",
		items=(('1', "Тип 1, координаты + UV + нормали", ""),
			   ('2', "Тип 2, координаты + UV + нормали", "Данный тип используется на обычных моделях"),
			   ('3', "Тип 3, координаты + UV", "Данный тип используется на моделях света фар"),
			   ('258', "Тип 258, координаты + UV + нормали + 2 float", "Данный тип используется для моделей асфальтированных дорог"),
			   ('514', "Тип 514, координаты + UV + нормали + 4 float", "Данный тип используется на моделях поверхности воды"),
			   ('515', "Тип 515, координаты + UV + нормали + 2 float", "Тоже самое, что и 258. Данный тип используется для моделей асфальтированных дорог"),
			   ),
		)
	
	MType_enum = bpy.props.EnumProperty(
		name="Тип записи полигонов (35)",
		items=(('1', "Тип 1, с разрывной UV", "Каждый трис модели записывается вместе со собственной UV."),
			   ('3', "Тип 3, без разрывной UV", "Этот тип можно использовать для моделей, которые используют текстуру отражений."),
			   ),
		)
		
	texNum_int = IntProperty(
		name = "Номер текстуры",
		description="Номер используемой текстуры.",
		)
		
	addBlockName_string = StringProperty(
		name="Присоединённый блок",
		description="Имя блока, который будет приписан к текущему блоку, например: hit_BmwM5 приписан к BmwM5 (05)",
		default="",
		maxlen=30,
		)
		
	addBlockName1_string = StringProperty(
		name="Присоединённый блок",
		description="Имя блока, который будет приписан к текущему блоку, например: hit_BmwM5 приписан к BmwM5 (05)",
		default="",
		maxlen=30,
		)
		
	addSpaceName_string = StringProperty(
		name="Используемый локатор",
		description="Имя блока, который будет использоваться в качестве локатора для привязанного блока, например: AirportSpace и Airport",
		default="",
		maxlen=30,
		)

	addSpaceName1_string = StringProperty(
		name="Используемый локатор",
		description="Имя блока, который будет использоваться в качестве локатора для привязанного блока, например: AirportSpace и Airport",
		default="",
		maxlen=30,
		)
		
	add24Flag_enum = EnumProperty(
		name="Флаг",
		items=[ ('0', "0", "Присоединённый объект не будет отображаться"),
				('1', "1", "Присоединённый объект будет отображаться"),
				]
		)
		
	add24Flag_enum1 = EnumProperty(
		name="Флаг",
		items=[ ('0', "0", "Присоединённый объект не будет отображаться"),
				('1', "1", "Присоединённый объект будет отображаться"),
				]
		)
		
	TGType_int = IntProperty(
		name = "Тип модели дерева",
		description="",
		)
		
	Scale = FloatProperty(
		name = "Масштаб генератора",
		description="",
		min=0.0,
		default=9.5,
		)
		
	generatorType_enum = EnumProperty(
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
		
	groupsNum_int = IntProperty(
		name = "Количество групп",
		description="Количество переключаемых групп.",
		)
		
	groupsNum1_int = IntProperty(
		name = "Количество групп",
		description="Количество переключаемых групп.",
		)
		
	Refer_bool = BoolProperty(
		name="refer",
		description="",
		default = False
		)
		
	Type21_enum = EnumProperty(
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
		
	T14_enum = EnumProperty(
		name="Преднастройки",
		items=[ ('car', "Для транспорта", ""),
				('trl', "Для полуприцепа", ""),
				('trl_cyc', "Для полуприцепа-цистерны", ""),
				('clk', "Для коллизии", ""),
				]
		)
		
	T28_radius = FloatProperty(
		name = "Радиус спрайта",
		description = "Радиус плоскости спрайта",
		default = 1.0,
		min = 0.01,
		)
		
	T28_radius1 = FloatProperty(
		name = "Радиус спрайта",
		description = "Радиус плоскости спрайта",
		default = 1.0,
		min = 0.01,
		)
		
	CH = FloatProperty(
		name = "Высота коллизии",
		description = "Высота плоскости коллизии",
		)
		
	CH1 = FloatProperty(
		name = "Высота коллизии",
		description = "Высота плоскости коллизии",
		)
	
	RSound = FloatProperty(
		name = "Радиус звука",
		description = "Радиус звука",
		default = 10.0,
		min = 0.0,
		)
		
	RSound1 = FloatProperty(
		name = "Радиус звука",
		description = "Радиус звука",
		default = 10.0,
		min = 0.0,
		)
		
	addSoundName_string = StringProperty(
		name="Присоединённый звуковой файл",
		description="Имя звукового файла, который будет использоваться данным блоком",
		default="",
		maxlen=30,
		)
		
	addSoundName1_string = StringProperty(
		name="Присоединённый звуковой файл",
		description="Имя звукового файла, который будет использоваться данным блоком",
		default="",
		maxlen=30,
		)
		
	SLevel = FloatProperty(
		name = "Уровень громкости звука",
		description = "Уровень громкости звука",
		default = 1.0,
		min = 0.0,
		max = 1.0,
		)
		
	SLevel1 = FloatProperty(
		name = "Уровень громкости звука",
		description = "Уровень громкости звука",
		default = 1.0,
		min = 0.0,
		max = 1.0,
		)
		
	addRoomName_string = StringProperty(
		name="Присоединённая комната",
		description="Имя комнаты, которая будет загружена",
		default="",
		maxlen=30,
		)
		
	FType_enum = bpy.props.EnumProperty(
		name="Тип записи полигонов (08)",
		items=(('0', "Тип 0", "С нормалями"),
			   ('1', "Тип 1", "Без нормалей"),
			   ('2', "Тип 2", "С нормалями, UV разрывная"),
			   ('128', "Тип 128", ""),
			   ('144', "Тип 144", ""),
			   ),
		)
		
	Faces_enum = bpy.props.EnumProperty(
		name="Тип блока полигонов",
		items=(('8', "8", ""),
			   ('35', "35", ""),
			   ),
		)
		
	addBlockMeshType_enum = EnumProperty(
		name="Тип записи модели",
		items=[ ('auto', "Автоматический", "Экспортер сам определит, какой блок использовать (8, 35 или оба)"),
				('manual', "Ручной", "Будет записан блок, который выбран в настройках"),
			   ]
		)
		
	addMeshType_enum = EnumProperty(
		name="Тип записи полигонов",
		items=[ ('uv0', "Обычный", ""),
				('uv1', "С разрывной UV", ""),
			   ]
		)
		
	materialName_string = StringProperty(
		name="Имя материала",
		description="Имя материала, который будет использоваться генератором",
		default="",
		maxlen=10,
		)
		
	routeName_string = StringProperty(
		name="Имя участка карты",
		description="Имя участка карты, который будет загружен",
		default="",
		maxlen=2,
		)
		
	triggerType_enum = bpy.props.EnumProperty(
		name="Тип триггера",
		items=(('loader', "Загрузчик", "Загрузчик участков карты"),
			   ('radar0', "Радар 0", "Event 0"),
			   ('radar1', "Радар 1", "Event 1"),
			   ),
		)
		
	addBlockName4_string = StringProperty(
		name="Родительский блок",
		description="",
		default="",
		maxlen=30,
		)
		
	speed_limit = FloatProperty(
		name = "Ограничение скорости",
		description = "",
		default = 60.0,
		min = 0.0,
		)
		
	addBlocks_enum = EnumProperty(
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
		
	addRoomNameIndex_string = StringProperty(
		name="Имя комнаты",
		description="",
		default="aa_000",
		maxlen=30,
		)

# ------------------------------------------------------------------------
#	operators
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
		
		if block_type == 6566754:
			object_name = "b3d"
			object = bpy.data.objects.new(object_name, None) 
			object.location=(0.0,0.0,0.0)
			bpy.context.scene.objects.link(object)
		
		if block_type == 0:
			object_name = mytool.BlockName_string
			object = bpy.data.objects.new(object_name, None) 
			object['block_type'] = block_type
			object.location=cursor_pos
			object['add_space'] = mytool.addSpaceName_string
			bpy.context.scene.objects.link(object)
		
		if block_type == 1:
			object_name = mytool.BlockName_string
			object = bpy.data.objects.new(object_name, None) 
			object['block_type'] = block_type
			object.location=cursor_pos
			object['add_space'] = mytool.addSpaceName_string
			object['route_name'] = mytool.routeName_string
			bpy.context.scene.objects.link(object)
			
		if block_type == 3:
			object_name = mytool.BlockName_string
			object = bpy.data.objects.new(object_name, None) 
			object['block_type'] = block_type
			object.location=cursor_pos
			object['node_radius'] = mytool.Radius
			bpy.context.scene.objects.link(object)
			
		if block_type == 4:
			object_name = mytool.BlockName_string
			object = bpy.data.objects.new(object_name, None) 
			object['block_type'] = block_type
			object.location=cursor_pos #(0.0,0.0,0.0)
			object['node_radius'] = mytool.Radius
			object['add_name'] = mytool.addBlockName4_string
			object['add_name1'] = mytool.addBlockName_string
			bpy.context.scene.objects.link(object)
		
		if block_type == 5:
			object_name = mytool.BlockName_string
			object = bpy.data.objects.new(object_name, None) 
			object['block_type'] = block_type
			object.location=cursor_pos #(0.0,0.0,0.0)
			object['node_radius'] = mytool.Radius
			object['add_name'] = mytool.addBlockName_string
			bpy.context.scene.objects.link(object)
			
		if block_type == 10:
			object_name = mytool.BlockName_string
			object = bpy.data.objects.new(object_name, None) 
			object['block_type'] = block_type
			object.location=cursor_pos
			object['node_radius'] = mytool.Radius
			object['lod_distance'] = mytool.LOD_Distance
			bpy.context.scene.objects.link(object)
		
		if block_type == 12:
			object_name = mytool.BlockName_string
			object = bpy.data.objects.new(object_name, None)
			object.location=cursor_pos
			object['block_type'] = block_type
			object['pos'] = 1
			object['height'] = mytool.CH
			object['CType'] = int(mytool.CollisionType_enum)
			bpy.context.scene.objects.link(object)
			
		if block_type == 13:
			object_name = mytool.BlockName_string
			object = bpy.data.objects.new(object_name, None)
			object.location=cursor_pos
			object['block_type'] = block_type
			if mytool.triggerType_enum == "loader":
				object['type'] = "loader"
				object['route_name'] = mytool.routeName_string
			if mytool.triggerType_enum == "radar0":
				object['type'] = "radar0"
				object['var0'] = 30
				object['var1'] = 3005
				object['var2'] = 4
				object['speed_limit'] = mytool.speed_limit
			if mytool.triggerType_enum == "radar1":
				object['type'] = "radar1"
				object['var0'] = 30
				object['var1'] = -1
				object['var2'] = 4
				object['speed_limit'] = mytool.speed_limit
			bpy.context.scene.objects.link(object)
		
		if block_type == 14:
			object_name = mytool.BlockName_string
			object = bpy.data.objects.new(object_name, None)
			object['block_type'] = block_type
			object.location=cursor_pos
			if mytool.T14_enum == "car":
				object['var0'] = 0 
				object['var1'] = mytool.Radius
				object['var2'] = mytool.Radius/2
				object['var3'] = 10
				object['var4'] = 18
			elif mytool.T14_enum == "trl":
				object['var0'] = 0
				object['var1'] = mytool.Radius
				object['var2'] = mytool.Radius/2
				object['var3'] = 16
				object['var4'] = 25
				
			elif mytool.T14_enum == "trl_cyc":
				object['var0'] = 0
				object['var1'] = mytool.Radius
				object['var2'] = mytool.Radius/2
				object['var3'] = 18
				object['var4'] = 25
				
			elif mytool.T14_enum == "clk":
				object['var0'] = 0
				object['var1'] = mytool.Radius * 0.08
				object['var2'] = mytool.Radius * 0.51
				object['var3'] = mytool.Radius
				object['var4'] = 0
			bpy.context.scene.objects.link(object)
		
		if block_type == 18:
			object_name = mytool.BlockName_string
			object = bpy.data.objects.new(object_name, None) 
			object['block_type'] = block_type
			object.location=cursor_pos
			object['node_radius'] = mytool.Radius
			object['add_name'] = mytool.addBlockName_string
			object['space_name'] = mytool.addSpaceName_string
			bpy.context.scene.objects.link(object)
		
		if block_type == 19:
			object_name = mytool.BlockName_string	
			object = bpy.data.objects.new(object_name, None) 
			object['block_type'] = block_type
			object.location=cursor_pos
			bpy.context.scene.objects.link(object)
			
		if block_type == 20:
			points = [(0,0,0), (0,1,0)]
			curveData = bpy.data.curves.new('curve', type='CURVE')
					
			curveData.dimensions = '3D'
			curveData.resolution_u = 2

			polyline = curveData.splines.new('POLY')
			polyline.points.add(len(points)-1)
			for i, coord in enumerate(points):
				x,y,z = coord
				polyline.points[i].co = (x, y, z, 1)

			object = bpy.data.objects.new("VDAT", curveData)
			curveData.bevel_depth = 0.01
					
			object.location = (0,0,0)
			#object = bpy.context.selected_objects[0]
			context.scene.objects.link(object)
			object.name = mytool.BlockName_string
			object['block_type'] = block_type
			
		if block_type == 21:
			if mytool.Refer_bool is False:
				object_name = mytool.Type21_enum
			else:
				object_name = 'refer_' + mytool.Type21_enum
			object = bpy.data.objects.new(object_name, None) 
			object['block_type'] = block_type
			object['node_radius'] = mytool.Radius
			object['groups_num'] = mytool.groupsNum_int
			object.location=cursor_pos
			bpy.context.scene.objects.link(object)

		if block_type == 24:
			object = bpy.ops.mesh.primitive_ico_sphere_add(size=0.05, calc_uvs=True, location=(0.0,0.0,0.0))	
			object = bpy.context.selected_objects[0]
			object['block_type'] = block_type
			object['flag'] = int(mytool.add24Flag_enum)
			object.name = mytool.BlockName_string
			object.location=cursor_pos
			
		if block_type == 25:
			object_name = mytool.BlockName_string
			object = bpy.data.objects.new(object_name, None)
			object.location=cursor_pos
			object['block_type'] = block_type
			object['sound_name'] = mytool.addSoundName_string
			object['RSound'] = mytool.RSound
			object['SLevel'] = mytool.SLevel
			bpy.context.scene.objects.link(object)
			
		if block_type == 28:
			object_name = mytool.BlockName_string
			object = bpy.data.objects.new(object_name, None)
			object.location=cursor_pos
			object['block_type'] = block_type
			object['node_radius'] = mytool.Radius
			object['sprite_radius'] = mytool.T28_radius
			object['texNum'] = mytool.texNum_int
			object_name = mytool.BlockName_string
			bpy.context.scene.objects.link(object)
			
		if block_type == 30:
			object_name = mytool.BlockName_string
			
			myvertex = []
			myfaces = []

			mypoint = [(0, -20, 0)]
			myvertex.extend(mypoint)

			mypoint = [(0, -20, 100)]
			myvertex.extend(mypoint)
			
			mypoint = [(0, 20, 100)]
			myvertex.extend(mypoint)

			mypoint = [(0, 20, 0)]
			myvertex.extend(mypoint)

			myface = [(0, 1, 2, 3)]
			myfaces.extend(myface)


			mymesh = bpy.data.meshes.new(object_name)

			object = bpy.data.objects.new(object_name, mymesh)

			bpy.context.scene.objects.link(object)

			mymesh.from_pydata(myvertex, [], myfaces)

			mymesh.update(calc_edges=True)
	
			object.location = cursor_pos
			
			object['block_type'] = block_type
			object.location=cursor_pos
			object['radius'] = mytool.Radius
			object['room_name'] = mytool.addRoomName_string
			#bpy.context.scene.objects.link(object)
			
		if block_type == 33:
			object_name = mytool.BlockName_string
			object = bpy.data.objects.new(object_name, None)
			object.location=cursor_pos
			object['block_type'] = block_type
			object['node_radius'] = mytool.Radius
			object['radius_light'] = mytool.RadiusLight
			object['intensity'] = mytool.Intensity
			object['R'] = mytool.R / 255
			object['G'] = mytool.G / 255
			object['B'] = mytool.B / 255
			object_name = mytool.BlockName_string
			bpy.context.scene.objects.link(object)
				
		if block_type == 40:
			if mytool.generatorType_enum == "$$TreeGenerator1":
				point = bpy.ops.mesh.primitive_ico_sphere_add(size=0.05, calc_uvs=True, enter_editmode=True, location=(0.0,0.0,0.0))
				mesh0 = bpy.ops.mesh.primitive_cone_add(vertices=12, radius1=0.5, radius2=0.0, depth=1.0, end_fill_type='NGON', calc_uvs=True, enter_editmode=True, location=(0.0, 0.0, 1.0))
				mesh1 = bpy.ops.mesh.primitive_cone_add(vertices=12, radius1=0.3, radius2=0.0, depth=0.6, end_fill_type='NGON', calc_uvs=True, enter_editmode=True, location=(0.0, 0.0, 1.4))
				tree = bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.05, depth=0.5, end_fill_type='NGON', calc_uvs=True, enter_editmode=True, location=(0.0, 0.0, 0.25))
				object = bpy.context.selected_objects[0]
				object['block_type'] = block_type
				object['scale'] = mytool.Scale
				object['TGType'] = mytool.TGType_int
				object['GType'] = mytool.generatorType_enum
				object.name = mytool.BlockName_string
				bpy.ops.object.mode_set(mode = 'OBJECT')
				object.location = bpy.context.scene.cursor_location
				
			if mytool.generatorType_enum == "$$DynamicGlow":
				object_name = mytool.BlockName_string
				object = bpy.data.objects.new(object_name, None)
				object.location=cursor_pos
			
				object['block_type'] = block_type
				object['scale'] = mytool.Scale
				object['mat_name'] = mytool.materialName_string
				object['GType'] = mytool.generatorType_enum
				object.name = mytool.BlockName_string
				bpy.context.scene.objects.link(object)
				
		if block_type == 444:
			object_name = mytool.BlockName_string
			object = bpy.data.objects.new(object_name, None) 
			object['block_type'] = 444
			object.location=(0.0,0.0,0.0)
			bpy.context.scene.objects.link(object)
		return {'FINISHED'}

# ------------------------------------------------------------------------
#	menus
# ------------------------------------------------------------------------

class BasicMenu(bpy.types.Menu):
	bl_idname = "OBJECT_MT_select_test"
	bl_label = "Select"

	def draw(self, context):
		layout = self.layout

		# built-in example operators
		layout.operator("object.select_all", text="Select/Deselect All").action = 'TOGGLE'
		layout.operator("object.select_all", text="Inverse").action = 'INVERT'
		layout.operator("object.select_random", text="Random")

# ------------------------------------------------------------------------
#	my tool in objectmode
# ------------------------------------------------------------------------

class OBJECT_PT_b3d_add_panel(Panel):
	bl_idname = "OBJECT_PT_b3d_add_panel"
	bl_label = "Добавление блоков"
	bl_space_type = "VIEW_3D"   
	bl_region_type = "TOOLS"	
	bl_category = "b3d Tools"
	#bl_context = "objectmode"   

	@classmethod
	def poll(self,context):
		return context.object is not None

	def draw(self, context):
		layout = self.layout
		scene = context.scene
		mytool = scene.my_tool
		global block_type
		block_type = int(mytool.addBlockType_enum)
		
		if block_type == 6566754:
			self.layout.label("Тип блока:")
			layout.prop(mytool, "addBlockType_enum", text="")
		
		if block_type == 0:
			layout.prop(mytool, "BlockName_string")
			self.layout.label("Тип блока:")
			layout.prop(mytool, "addBlockType_enum", text="")
			layout.prop(mytool, "addSpaceName_string")
			
			
		if block_type == 1:
			layout.prop(mytool, "BlockName_string")
			self.layout.label("Тип блока:")
			layout.prop(mytool, "addBlockType_enum", text="")
			layout.prop(mytool, "addSpaceName_string")
			layout.prop(mytool, "routeName_string")
			
		if block_type == 3:
			layout.prop(mytool, "BlockName_string")
			self.layout.label("Тип блока:")
			layout.prop(mytool, "addBlockType_enum", text="")
			layout.prop(mytool, "Radius")
			
		if block_type == 4:
			layout.prop(mytool, "BlockName_string")
			self.layout.label("Тип блока:")
			layout.prop(mytool, "addBlockType_enum", text="")
			layout.prop(mytool, "Radius")
			layout.prop(mytool, "addBlockName4_string")
			layout.prop(mytool, "addBlockName_string")
		
		if block_type == 5:
			layout.prop(mytool, "BlockName_string")
			self.layout.label("Тип блока:")
			layout.prop(mytool, "addBlockType_enum", text="")
			layout.prop(mytool, "addBlockName_string")
			layout.prop(mytool, "Radius")
			
		elif block_type == 10:
			layout.prop(mytool, "BlockName_string")
			self.layout.label("Тип блока:")
			layout.prop(mytool, "addBlockType_enum", text="")
			layout.prop(mytool, "Radius")
			layout.prop(mytool, "LOD_Distance")
			
		elif block_type == 12:
			layout.prop(mytool, "BlockName_string")
			self.layout.label("Тип блока:")
			layout.prop(mytool, "addBlockType_enum", text="")
			layout.prop(mytool, "CH")
			layout.prop(mytool, "CollisionType_enum")
			
		elif block_type == 13:
			layout.prop(mytool, "BlockName_string")
			self.layout.label("Тип блока:")
			layout.prop(mytool, "addBlockType_enum", text="")
			layout.prop(mytool, "triggerType_enum", text="")
			if mytool.triggerType_enum == "loader":
				layout.prop(mytool, "routeName_string")
			elif mytool.triggerType_enum == "radar0" or "radar1":
				layout.prop(mytool, "speed_limit")
			
		elif block_type == 14:
			layout.prop(mytool, "BlockName_string")
			self.layout.label("Тип блока:")
			layout.prop(mytool, "addBlockType_enum", text="")
			self.layout.label("Вариант преднастроек:")
			layout.prop(mytool, "T14_enum", text="")
			layout.prop(mytool, "Radius")

		elif block_type == 18:
			layout.prop(mytool, "BlockName_string")
			self.layout.label("Тип блока:")
			layout.prop(mytool, "addBlockType_enum", text="")
			layout.prop(mytool, "Radius")
			layout.prop(mytool, "addBlockName_string")
			layout.prop(mytool, "addSpaceName_string")

		elif block_type == 19:
			layout.prop(mytool, "BlockName_string")
			self.layout.label("Тип блока:")
			layout.prop(mytool, "addBlockType_enum", text="")
			
		elif block_type == 20:
			layout.prop(mytool, "BlockName_string")
			self.layout.label("Тип блока:")
			layout.prop(mytool, "addBlockType_enum", text="")

		elif block_type == 21:
			self.layout.label("Имя блока:")
			layout.prop(mytool, "Type21_enum", text="")
			layout.prop(mytool, "Refer_bool")
			self.layout.label("Тип блока:")
			layout.prop(mytool, "addBlockType_enum", text="")
			layout.prop(mytool, "Radius")
			layout.prop(mytool, "groupsNum_int")
			
		elif block_type == 24:
			layout.prop(mytool, "BlockName_string")
			self.layout.label("Тип блока:")
			layout.prop(mytool, "addBlockType_enum", text="")
			self.layout.label("Флаг:")
			layout.prop(mytool, "add24Flag_enum", text="")
			
		elif block_type == 25:
			layout.prop(mytool, "BlockName_string")
			self.layout.label("Тип блока:")
			layout.prop(mytool, "addBlockType_enum", text="")
			layout.prop(mytool, "addSoundName_string")
			layout.prop(mytool, "RSound")
			layout.prop(mytool, "SLevel")
			
		elif block_type == 28:
			layout.prop(mytool, "BlockName_string")
			self.layout.label("Тип блока:")
			layout.prop(mytool, "addBlockType_enum", text="")
			layout.prop(mytool, "Radius")
			layout.prop(mytool, "T28_radius")
			layout.prop(mytool, "texNum_int")
			
		elif block_type == 30:
			layout.prop(mytool, "BlockName_string")
			self.layout.label("Тип блока:")
			layout.prop(mytool, "addBlockType_enum", text="")
			layout.prop(mytool, "Radius")
			layout.prop(mytool, "addRoomName_string")
			
		elif block_type == 33:
			layout.prop(mytool, "BlockName_string")
			self.layout.label("Тип блока:")
			layout.prop(mytool, "addBlockType_enum", text="")
			layout.prop(mytool, "Radius")
			layout.prop(mytool, "RadiusLight")
			layout.prop(mytool, "Intensity")
			layout.prop(mytool, "R")
			layout.prop(mytool, "G")
			layout.prop(mytool, "B")
			
		elif block_type == 40:
			layout.prop(mytool, "BlockName_string")
			self.layout.label("Тип блока:")
			layout.prop(mytool, "addBlockType_enum", text="")
			self.layout.label("Тип генератора:")
			layout.prop(mytool, "generatorType_enum", text="")
			if mytool.generatorType_enum == "$$TreeGenerator1":
				layout.prop(mytool, "TGType_int")
				layout.prop(mytool, "Scale")
			if mytool.generatorType_enum == "$$DynamicGlow":
				layout.prop(mytool, "materialName_string")
				layout.prop(mytool, "Scale")
			else:
				self.layout.label("Данный тип генератора не поддерживается.")
				
		elif block_type == 444:
			layout.prop(mytool, "BlockName_string")
			self.layout.label("Тип блока:")
			layout.prop(mytool, "addBlockType_enum", text="")
			
		layout.operator("wm.add_operator")
			
		#layout.prop(mytool, "my_bool") 
		#layout.prop(mytool, "my_int")
		#layout.prop(mytool, "my_float")
		#layout.menu("OBJECT_MT_select_test", text="Presets", icon="SCENE")

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
		
		if block_type == 5:
			mytool.addBlockName1_string = object['add_name']
			mytool.Radius1 = object['node_radius']
			
		elif block_type == 7:
			if 'BType' in object:
				mytool.Faces_enum = str(object['BType'])
			else:
				mytool.Faces_enum = str(35)
				object['BType'] = 35
			if "type1" in object:
				mytool.addBlockMeshType_enum = str(object['type1'])
			else:
				object['type1'] = "manual"
				mytool.addBlockMeshType_enum = str(object['type1'])
			mytool.MType_enum = str(object['MType'])
			mytool.FType_enum = str(object['FType'])
			mytool.texNum_int = object['texNum']
			
		elif block_type == 10:
			mytool.Radius1 = object['node_radius']
			mytool.LOD_Distance1 = object['lod_distance']
			
		elif block_type == 12:
			mytool.CH1 = object['height']
			mytool.CollisionType_enum = object['CType']
			
		elif block_type == 18:
			mytool.Radius1 = object['node_radius']
			mytool.addBlockName1_string = object['add_name']
			mytool.addSpaceName1_string = object['space_name']
			
		elif block_type == 21:
			mytool.groupsNum1_int = object['groups_num']
			mytool.Radius1 = object['node_radius']

		elif block_type == 23:
			mytool.CollisionType_enum = str(object['CType'])
		
		elif block_type == 24:
			mytool.add24Flag_enum1 = str(object['flag'])
			
		elif block_type == 25:
			mytool.RSound1 = (object['RSound'])
			mytool.addSoundName1_string = object['sound_name']
			mytool.SLevel1 = (object['SLevel'])
			
		elif block_type == 28:
			mytool.texNum_int = object['texNum']
			mytool.T28_radius1 = object['sprite_radius']

		elif block_type == 33:
			mytool.Radius1 = object['node_radius']
			mytool.RadiusLight1 = object['radius_light']
			mytool.Intensity1 = object['intensity'] 
			mytool.R1 = object['R'] * 255
			mytool.G1 = object['G'] * 255
			mytool.B1 = object['B'] * 255	
		
		elif block_type == 37:
			if 'BType' in object:
				mytool.Faces_enum = str(object['BType'])
			else:
				mytool.Faces_enum = str(35)
				object['BType'] = 35
			if "type1" in object:
				mytool.addBlockMeshType_enum = str(object['type1'])
			else:
				object['type1'] = "manual"
				mytool.addBlockMeshType_enum = str(object['type1'])
			#mytool.addMeshType_enum = str(object['type2'])
			mytool.SType_enum = str(object['SType'])
			mytool.MType_enum = str(object['MType'])
			mytool.FType_enum = str(object['FType'])
			mytool.texNum_int = object['texNum']
		
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
				block_type = int(mytool.addBlockType_enum1)
				
			object['block_type'] = block_type
			
			if block_type == 5:
				object['add_name'] = mytool.addBlockName1_string
				object['node_radius'] = mytool.Radius1
				
			elif block_type == 7:
				object['type1'] = str(mytool.addBlockMeshType_enum)
				object['BType'] = int(mytool.Faces_enum)
				object['FType'] = int(mytool.FType_enum)
				object['MType'] = int(mytool.MType_enum)
				object['texNum'] = int(mytool.texNum_int)
				
			elif block_type == 10:
				object['node_radius'] = mytool.Radius1
				object['lod_distance'] = mytool.LOD_Distance1
				
			elif block_type == 12:
				object['height'] = mytool.CH1
				object['CType'] = int(mytool.CollisionType_enum)
				
			elif block_type == 18:
				object['node_radius'] = mytool.Radius1
				object['add_name'] = mytool.addBlockName1_string
				object['space_name'] = mytool.addSpaceName1_string
			
			elif block_type == 21:
				object['groups_num'] = mytool.groupsNum1_int
				object['node_radius'] = mytool.Radius1
			
			elif block_type == 23:
				object['CType'] = int(mytool.CollisionType_enum)
			
			elif block_type == 24:
				object['flag'] = int(mytool.add24Flag_enum1)
				
			elif block_type == 25:
				object['RSound'] = mytool.RSound1
				object['sound_name'] = mytool.addSoundName1_string
				object['SLevel'] = mytool.SLevel1
				
			elif block_type == 28:
				object['texNum'] = mytool.texNum_int
				object['node_radius'] = mytool.Radius1
				object['sprite_radius'] = mytool.T28_radius1
				
			elif block_type == 33:
				object['node_radius'] = mytool.Radius1
				object['radius_light'] = mytool.RadiusLight1
				object['intensity'] = mytool.Intensity1
				object['R'] = mytool.R1 / 255
				object['G'] = mytool.G1 / 255
				object['B'] = mytool.B1 / 255
				
			elif block_type == 37:
				object['type1'] = str(mytool.addBlockMeshType_enum)
				#object['type2'] = str(mytool.addMeshType_enum)
				object['BType'] = int(mytool.Faces_enum)
				object['SType'] = int(mytool.SType_enum)
				object['MType'] = int(mytool.MType_enum)
				object['FType'] = int(mytool.FType_enum)
				object['texNum'] = int(mytool.texNum_int)
			
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
		
class OBJECT_PT_b3d_edit_panel(Panel):
	bl_idname = "OBJECT_PT_b3d_edit_panel"
	bl_label = "Редактирование блоков"
	bl_space_type = "VIEW_3D"   
	bl_region_type = "TOOLS"	
	bl_category = "b3d Tools"
	#bl_context = "objectmode"   

	@classmethod
	def poll(self,context):
		return context.object is not None

	def draw(self, context):
		layout = self.layout
		scene = context.scene
		mytool = scene.my_tool
		
		#for i in range(len(bpy.context.selected_objects)):	
		
		for i in range(1):	
		
			object = bpy.context.selected_objects[i]
		
			if 'block_type' in object:
				block_type = object['block_type']
			else:
				block_type = None
				
			lenStr = str(len(object.children))
			
			if block_type == 0:
				self.layout.label("Тип блока: " + str(block_type))
				self.layout.label("Количество вложенных блоков: " + lenStr)		
			
			elif block_type == 1:
				self.layout.label("Тип блока: " + str(block_type))
				self.layout.label("Количество вложенных блоков: " + lenStr)
				
			elif block_type == 2:
				self.layout.label("Тип блока: " + str(block_type))
				self.layout.label("Количество вложенных блоков: " + lenStr)
		
			elif block_type == 3:
				self.layout.label("Тип блока: " + str(block_type))
				self.layout.label("Количество вложенных блоков: " + lenStr)
				
			elif block_type == 4:
				self.layout.label("Тип блока: " + str(block_type))
				self.layout.label("Количество вложенных блоков: " + lenStr)
			
			elif block_type == 5:
				self.layout.label("Тип блока: " + str(block_type))
				self.layout.label("Количество вложенных блоков: " + lenStr)
				if 'add_name' in object:
					layout.prop(mytool, "addBlockName1_string")
					layout.prop(mytool, "Radius1")
				else:
				   self.layout.label("Имя присоединённого блока не указано. Сохраните настройки,")
				   self.layout.label("а затем попробуйте выделить блок заново.")
				
			elif block_type == 6:
				self.layout.label("Тип блока: " + str(block_type))
				self.layout.label("Количество вложенных блоков: " + lenStr)
				
			elif block_type == 7:   
				self.layout.label("Тип блока: " + str(block_type))
				if 'texNum' in object:
					layout.prop(mytool, "addBlockMeshType_enum")
					
					if (mytool.addBlockMeshType_enum) == "auto":
						layout.prop(mytool, "FType_enum")
						layout.prop(mytool, "MType_enum")
					else:
						layout.prop(mytool, "Faces_enum")
						if int(mytool.Faces_enum) == 35:
							layout.prop(mytool, "MType_enum")
						else:
							layout.prop(mytool, "FType_enum")
						
					layout.prop(mytool, "texNum_int")
				else:
				   self.layout.label("Указаны не все атрибуты объекта.")
				   self.layout.label("Сохраните настройки, а затем попробуйте выделить блок заново.")

			elif block_type == 8:
				self.layout.label("Тип блока: " + str(block_type))
				self.layout.label("Количество вложенных блоков: " + lenStr)
				
			elif block_type == 9:
				self.layout.label("Тип блока: " + str(block_type))
				self.layout.label("Количество вложенных блоков: " + lenStr)

			elif block_type == 10:
				self.layout.label("Тип блока: " + str(block_type))
				if 'node_radius' in object:
					layout.prop(mytool, "Radius1")
					layout.prop(mytool, "LOD_Distance1")
				else:
				   self.layout.label("Указаны не все атрибуты объекта.")
				   self.layout.label("Сохраните настройки, а затем попробуйте выделить блок заново.")
				self.layout.label("Количество вложенных блоков: " + str(len(object.children) - 1))
				
			elif block_type == 11:
				self.layout.label("Тип блока: " + str(block_type))
				self.layout.label("Количество вложенных блоков: " + lenStr)

			elif block_type == 12:
				self.layout.label("Тип блока: " + str(block_type))
				if 'CType' in object:
					self.layout.label("Тип коллизии:")
					layout.prop(mytool, "CollisionType_enum", text="")
					layout.prop(mytool, "CH1")
				else:
					self.layout.label("Тип коллизии не указан. Сохраните настройки,")
					self.layout.label("а затем попробуйте выделить блок заново.")
				
			elif block_type == 13:
				self.layout.label("Тип блока: " + str(block_type))
				self.layout.label("Количество вложенных блоков: " + lenStr)

			elif block_type == 14:
				self.layout.label("Тип блока: " + str(block_type))
				self.layout.label("Количество вложенных блоков: " + lenStr)
				
			elif block_type == 15:
				self.layout.label("Тип блока: " + str(block_type))
				self.layout.label("Количество вложенных блоков: " + lenStr)

			elif block_type == 16:
				self.layout.label("Тип блока: " + str(block_type))
				self.layout.label("Количество вложенных блоков: " + lenStr)
				
			elif block_type == 17:
				self.layout.label("Тип блока: " + str(block_type))
				self.layout.label("Количество вложенных блоков: " + lenStr)
				
			elif block_type == 18:
				self.layout.label("Тип блока: " + str(block_type))
				self.layout.label("Количество вложенных блоков: " + lenStr)
				if 'add_name' in object:
					layout.prop(mytool, "Radius1")
					layout.prop(mytool, "addBlockName1_string")
					layout.prop(mytool, "addSpaceName1_string")
				else:
				   self.layout.label("Указаны не все атрибуты объекта.")
				   self.layout.label("Сохраните настройки, а затем попробуйте выделить блок заново.")

			elif block_type == 19:
				self.layout.label("Тип блока: " + str(block_type))
				self.layout.label("Количество вложенных блоков: " + lenStr)
				
			elif block_type == 20:
				self.layout.label("Тип блока: " + str(block_type))
				self.layout.label("Количество вложенных блоков: " + lenStr)

			elif block_type == 21:
				self.layout.label("Тип блока: " + str(block_type))
				self.layout.label("Количество вложенных блоков: " + str(len(object.children)-object['groups_num']+1))
				if 'groups_num' in object:
					layout.prop(mytool, "groupsNum1_int")
					layout.prop(mytool, "Radius1")
				else:
				   self.layout.label("Количество групп не указано. Сохраните настройки,")
				   self.layout.label("а затем попробуйте выделить блок заново.")

			elif block_type == 23:
				self.layout.label("Тип блока: " + str(block_type))
				self.layout.label("Количество вложенных блоков: " + lenStr)
				if 'CType' in object:
					self.layout.label("Тип коллизии:")
					layout.prop(mytool, "CollisionType_enum", text="")
				else:
					self.layout.label("Тип коллизии не указан. Сохраните настройки,")
					self.layout.label("а затем попробуйте выделить блок заново.")
				
			elif block_type == 24:
				self.layout.label("Тип блока: " + str(block_type))
				self.layout.label("Количество вложенных блоков: " + lenStr)
				if 'flag' in object:
					layout.prop(mytool, "add24Flag_enum1", text="")
				else:
				   self.layout.label("Флаг блока не указан. Сохраните настройки,")
				   self.layout.label("а затем попробуйте выделить блок заново.")
			
			elif block_type == 25:
				self.layout.label("Тип блока: " + str(block_type))
				if 'RSound' in object:
					layout.prop(mytool, "addSoundName1_string")
					layout.prop(mytool, "RSound1")
					layout.prop(mytool, "SLevel1")
				else:
					self.layout.label("Указаны не все атрибуты объекта.")
					self.layout.label("Сохраните настройки, а затем попробуйте выделить блок заново.")

			elif block_type == 26:
				self.layout.label("Тип блока: " + str(block_type))
				self.layout.label("Количество вложенных блоков: " + lenStr)
				
			elif block_type == 27:
				self.layout.label("Тип блока: " + str(block_type))
				self.layout.label("Количество вложенных блоков: " + lenStr)

			elif block_type == 28:
				self.layout.label("Тип блока: " + str(block_type))
				if 'sprite_radius' in object:
					layout.prop(mytool, "Radius1")
					layout.prop(mytool, "T28_radius1")
					layout.prop(mytool, "texNum_int")
				else:
				   self.layout.label("Указаны не все атрибуты объекта.")
				   self.layout.label("Сохраните настройки, а затем попробуйте выделить блок заново.")
				
			elif block_type == 29:
				self.layout.label("Тип блока: " + str(block_type))
				self.layout.label("Количество вложенных блоков: " + lenStr)

			elif block_type == 30:
				self.layout.label("Тип блока: " + str(block_type))
				self.layout.label("Количество вложенных блоков: " + lenStr)
				
			elif block_type == 31:
				self.layout.label("Тип блока: " + str(block_type))
				self.layout.label("Количество вложенных блоков: " + lenStr)

			elif block_type == 32:
				self.layout.label("Тип блока: " + str(block_type))
				self.layout.label("Количество вложенных блоков: " + lenStr)
				
			elif block_type == 33:
				self.layout.label("Тип блока: " + str(block_type))
				layout.prop(mytool, "Radius1")
				layout.prop(mytool, "RadiusLight1")
				layout.prop(mytool, "Intensity1")
				layout.prop(mytool, "R1")
				layout.prop(mytool, "G1")
				layout.prop(mytool, "B1")

			elif block_type == 34:
				self.layout.label("Тип блока: " + str(block_type))
				self.layout.label("Количество вложенных блоков: " + lenStr)
				
			elif block_type == 35:
				self.layout.label("Тип блока: " + str(block_type))
				self.layout.label("Количество вложенных блоков: " + lenStr)
			
			elif block_type == 36:
				self.layout.label("Тип блока: " + str(block_type))
				self.layout.label("Количество вложенных блоков: " + lenStr)

			elif block_type == 37:
				self.layout.label("Тип блока: " + str(block_type))
				#self.layout.label("Количество вложенных блоков: " + lenStr)
				if 'texNum' in object:
					layout.prop(mytool, "addBlockMeshType_enum")
					
					if (mytool.addBlockMeshType_enum) == "auto":
						layout.prop(mytool, "SType_enum")
						#layout.prop(mytool, "FType_enum")
						#layout.prop(mytool, "addMeshType_enum")
						layout.prop(mytool, "FType_enum")
						layout.prop(mytool, "MType_enum")
					else:
						layout.prop(mytool, "Faces_enum")
						if int(mytool.Faces_enum) == 35:
							layout.prop(mytool, "MType_enum")
							layout.prop(mytool, "SType_enum")
						else:
							layout.prop(mytool, "SType_enum")
							layout.prop(mytool, "FType_enum")
						
					layout.prop(mytool, "texNum_int")
				else:
				   self.layout.label("Указаны не все атрибуты объекта.")
				   self.layout.label("Сохраните настройки, а затем попробуйте выделить блок заново.")
				
			elif block_type == 38:
				self.layout.label("Тип блока: " + str(block_type))
				self.layout.label("Количество вложенных блоков: " + lenStr)

			elif block_type == 39:
				self.layout.label("Тип блока: " + str(block_type))
				self.layout.label("Количество вложенных блоков: " + lenStr)
				
			elif block_type == 40:
				self.layout.label("Тип блока: " + str(block_type))
				self.layout.label("Тип генератора: " + object['GType'])
				
			elif block_type == 444:
				self.layout.label("Тип объекта - разделитель")
			
			else:
				self.layout.label("Выбранный объект не имеет типа.")
				self.layout.label("Чтобы указать его, нажмите на кнопку сохранения настроек.")
				layout.prop(mytool, "addBlockType_enum1")
			
		layout.operator("wm.get_values_operator")
		layout.operator("wm.set_values_operator")
		layout.operator("wm.del_values_operator")	
		layout.operator("wm.fix_uv_operator")
		layout.operator("wm.fix_verts_operator")
		
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
			
class OBJECT_PT_b3d_blocks_panel(Panel):
	bl_idname = "OBJECT_PT_b3d_blocks_panel"
	bl_label = "Сборки блоков"
	bl_space_type = "VIEW_3D"   
	bl_region_type = "TOOLS"	
	bl_category = "b3d Tools"
	#bl_context = "objectmode"   

	@classmethod
	def poll(self,context):
		return context.object is not None

	def draw(self, context):
		layout = self.layout
		scene = context.scene
		mytool = scene.my_tool
		
		type = mytool.addBlocks_enum
		
		layout.prop(mytool, "addBlocks_enum")
		
		if type == "room":
			layout.prop(mytool, "addRoomNameIndex_string")
			layout.prop(mytool, "Radius")
		
		layout.operator("wm.add1_operator")

class OBJECT_PT_b3d_misc_panel(Panel):
	bl_idname = "OBJECT_PT_b3d_misc_panel"
	bl_label = "О плагине"
	bl_space_type = "VIEW_3D"   
	bl_region_type = "TOOLS"	
	bl_category = "b3d Tools"
	#bl_context = "objectmode"   

	@classmethod
	def poll(self,context):
		return context.object is not None

	def draw(self, context):
		layout = self.layout
		scene = context.scene
		mytool = scene.my_tool
		
		self.layout.label("Автор плагина: aleko2144")
		self.layout.label("vk.com/rnr_mods")
# ------------------------------------------------------------------------
# register and unregister
# ------------------------------------------------------------------------

def register():
	bpy.utils.register_module(__name__)
	bpy.types.Scene.my_tool = PointerProperty(type=PanelSettings)

def unregister():
	bpy.utils.unregister_module(__name__)
	del bpy.types.Scene.my_tool

if __name__ == "__main__":
	register()