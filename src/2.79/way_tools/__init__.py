bl_info = {
	"name": "King of The Road *.way exporter",
	"description": "",
	"author": "Andrey Prozhoga",
	"version": (0, 0, 2),
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

import struct

bytes_len = 0

# panel

class PanelSettings1(PropertyGroup):

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
	
	addWBlockType_enum = EnumProperty(
		name="Тип блока",
		items=[ ('VDAT', "VDAT", ""), #
				('WDTH', "WDTH", ""), #
				('RTEN', "RTEN", ""),
				('ATTR', "ATTR", ""), #
				('FLAG', "FLAG", ""), #
				('ORTN', "ORTN", ""),
				('POSN', "POSN", ""),
				('NNAM', "NNAM", ""),
				('RNOD', "RNOD", ""),
				('RNAM', "RNAM", ""),
				('GROM', "GROM", ""),
				('GDAT', "GDAT", ""),
				('MNAM', "MNAM", ""),
				('WTWR', "WTWR", ""),
			   ]
		)
		
	addWDBlockType_enum = EnumProperty(
		name="Тип блока",
		items=[ ('way', "Way", ""),
				('room', "Room", ""),
				('rseg', "Road segment", ""),
				('rnod', "Node", ""),
				('ortn', "Node with orientation block", ""),
			   ]
		)
	
	attr_int_0 = IntProperty(
		name = "Параметр 1",
		description="Тип дороги",
		default = 1,
		min = 0
		)
		
	attr_dbl_0 = FloatProperty(
		name = "Граница дороги",
		description="A integer property",
		default = 0,
		min = 0
		)
		
	attr_int_1 = IntProperty(
		name = "Параметр 3",
		description="-",
		default = 1,
		min = 0
		)
		
	wdth_dbl_0 = FloatProperty(
		name = "Параметр 1",
		description="",
		min = 0
		)
		
	wdth_dbl_1 = FloatProperty(
		name = "Параметр 2",
		description="",
		min = 0
		)
		
	flag_int = IntProperty(
		name = "Флаг",
		description="",
		min = 0, #0 - fuel node?, 1 - town node (проверено)
		)
		
	name_string = StringProperty(
		name="Имя объекта",
		default="",
		maxlen=20,
		)
##########################################
	mnam_string = StringProperty(
		name="Имя карты",
		default="aa",
		maxlen=20,
		)
		
	rnam_string = StringProperty(
		name="Имя комнаты",
		default="room_aa_000",
		maxlen=20,
		)
		
	nnam_string = StringProperty(
		name="Node name",
		default="pos_parking_00",
		maxlen=20,
		)
		
	wdth_val1 = FloatProperty(
		name = "Ширина дороги",
		description="",
		default=14,
		min = 0,
		)
	
	wdth_val2 = FloatProperty(
		name = "Ширина дороги",
		description="",
		default=14,
		min = 0,
		)
		
	attr_1 = IntProperty(
		name = "Тип дороги",
		description="",
		default = 1,
		min = 0
		)
		
	attr_2 = FloatProperty(
		name = "Граница дороги",
		description="",
		default = 0.1,
		min = 0
		)
		
	attr_3 = IntProperty(
		name = "Параметр 3",
		description="",
		default = 1,
		min = 0
		)
		
	flag_val = IntProperty(
		name = "Флаг",
		description="",
		min = 0,
		)

class AddOperator1(bpy.types.Operator):
	bl_idname = "wm.add_operator1"
	bl_label = "Добавить блок на сцену"

	def execute(self, context):
		scene = context.scene
		waytool = scene.way_tool

		global blockW_type
		
		blockW_type = waytool.addWBlockType_enum
		
		global cursor_pos1
		cursor_pos1 = bpy.context.scene.cursor_location
		
		
		if blockW_type == "WDTH":
			object_name = waytool.addWBlockType_enum
			object = bpy.data.objects.new(object_name, None) 
			object.location=(0,0,0)
			object['var1'] = waytool.wdth_dbl_0
			object['var2'] = waytool.wdth_dbl_1
			bpy.context.scene.objects.link(object)
			
		if blockW_type == "ATTR":
			object_name = waytool.addWBlockType_enum
			object = bpy.data.objects.new(object_name, None) 
			object.location=(0,0,0)
			object['var1'] = waytool.attr_int_0
			object['var2'] = waytool.attr_dbl_0
			object['var3'] = waytool.attr_int_1
			bpy.context.scene.objects.link(object)
			
		if blockW_type == "FLAG":
			object_name = waytool.addWBlockType_enum
			object = bpy.data.objects.new(object_name, None) 
			object.location=(0,0,0)
			object['flag'] = waytool.flag_int
			bpy.context.scene.objects.link(object)	
			
		if blockW_type == "MNAM":
			object_name = waytool.addWBlockType_enum
			object = bpy.data.objects.new(object_name, None) 
			object.location=(0,0,0)
			object['str'] = waytool.name_string
			bpy.context.scene.objects.link(object)	
			
		if blockW_type == "RNAM":
			object_name = waytool.addWBlockType_enum
			object = bpy.data.objects.new(object_name, None) 
			object.location=(0,0,0)
			object['str'] = waytool.name_string
			bpy.context.scene.objects.link(object)	
			
		if blockW_type == "NNAM":
			object_name = waytool.addWBlockType_enum
			object = bpy.data.objects.new(object_name, None) 
			object.location=(0,0,0)
			object['str'] = waytool.name_string
			bpy.context.scene.objects.link(object)	
			
		if blockW_type == "ORTN":
			object = bpy.ops.mesh.primitive_ico_sphere_add(size=0.05, calc_uvs=True, location=(0.0,0.0,0.0))	
			object = bpy.context.selected_objects[0]
			object.name = waytool.addWBlockType_enum
			object.location=cursor_pos1
			
		if blockW_type == "POSN":
			object = bpy.ops.mesh.primitive_ico_sphere_add(size=0.05, calc_uvs=True, location=(0.0,0.0,0.0))	
			object = bpy.context.selected_objects[0]
			object.name =waytool.addWBlockType_enum
			object.location=cursor_pos1
			
		return {'FINISHED'}
		
class SetValuesOperator1(bpy.types.Operator):
	bl_idname = "wm.set_values_operator1"
	bl_label = "Сохранить настройки блока"

	def execute(self, context):
		scene = context.scene
		waytool = scene.way_tool

		object = bpy.context.selected_objects[0]
		
		if object.name[0:4] == 'ATTR':
			object['var1'] = waytool.attr_int_0
			object['var2'] = waytool.attr_dbl_0
			object['var3'] = waytool.attr_int_1
			
		elif object.name[0:4] == 'WDTH':
			object['var1'] = waytool.wdth_dbl_0
			object['var2'] = waytool.wdth_dbl_1
			
		return {'FINISHED'}
			
class AddOperator11(bpy.types.Operator):
	bl_idname = "wm.add_operator11"
	bl_label = "Добавить объект на сцену"

	def execute(self, context):
		scene = context.scene
		waytool = scene.way_tool

		global blockWD_type
		
		blockWD_type = waytool.addWDBlockType_enum
		
		global cursor_pos1
		cursor_pos1 = bpy.context.scene.cursor_location
		
		if blockWD_type == "way":
			way = bpy.data.objects.new("way", None) 
			way.location=(0,0,0)
			way['type'] = "way"
			way['mnam'] = waytool.mnam_string
			bpy.context.scene.objects.link(way)
		
		
		if blockWD_type == "room":
			object_name = waytool.rnam_string
			object = bpy.data.objects.new(object_name, None) 
			object.location=(0,0,0)
			object['type'] = "room"
			bpy.context.scene.objects.link(object)
			
		if blockWD_type == "rseg":
		
			points = [(0,0,0), (0,1,0)]
					
			curveData = bpy.data.curves.new('curve', type='CURVE')
			
			curveData.dimensions = '3D'
			curveData.resolution_u = 2

			polyline = curveData.splines.new('POLY')
			polyline.points.add(len(points)-1)
			for i, coord in enumerate(points):
				x,y,z = coord
				polyline.points[i].co = (x, y, z, 1)

			object = bpy.data.objects.new("RSEG", curveData)
			curveData.bevel_depth = 0.01
					
			object.location = (0,0,0)
			
			object.name = "RSEG"
			object['type'] = "rseg"
			object['attr1'] = waytool.attr_1
			object['attr2'] = waytool.attr_2
			object['attr3'] = waytool.attr_3
			object['wdth1'] = waytool.wdth_val1
			object['wdth2'] = waytool.wdth_val2
			context.scene.objects.link(object)
			
		if blockWD_type == "rnod" or blockWD_type == "ortn":
			object = bpy.ops.mesh.primitive_ico_sphere_add(size=0.05, calc_uvs=True, location=(0.0,0.0,0.0))	
			object = bpy.context.selected_objects[0]
			object.name = waytool.nnam_string
			object.location=cursor_pos1
			object['type'] = waytool.addWDBlockType_enum
			object['flag'] = waytool.flag_val
			
		return {'FINISHED'}
			
class OBJECT_PT_way_add_panel(Panel):
	bl_idname = "OBJECT_PT_way_add_panel"
	bl_label = "Добавление блоков"
	bl_space_type = "VIEW_3D"   
	bl_region_type = "TOOLS"	
	bl_category = "way Tools"
	#bl_context = "objectmode"   

	@classmethod
	def poll(self,context):
		return context.object is not None

	def draw(self, context):
		layout = self.layout
		scene = context.scene
		waytool = scene.way_tool
		global blockW_type
		blockW_type = waytool.addWBlockType_enum
		
		self.layout.label("Тип блока:")
		layout.prop(waytool, "addWBlockType_enum", text="")
		
		if blockW_type == "ATTR":
			layout.prop(waytool, "attr_int_0")
			layout.prop(waytool, "attr_dbl_0")
			layout.prop(waytool, "attr_int_1")
			
		if blockW_type == "WDTH":
			layout.prop(waytool, "wdth_dbl_0")
			layout.prop(waytool, "wdth_dbl_1")
			
		if blockW_type == "FLAG":
			layout.prop(waytool, "flag_int")
			
		if blockW_type == "MNAM":
			layout.prop(waytool, "name_string")
			
		if blockW_type == "RNAM":
			layout.prop(waytool, "name_string")
			
		if blockW_type == "NNAM":
			layout.prop(waytool, "name_string")
			
		layout.operator("wm.add_operator1")
		
class GetValuesOperator1(bpy.types.Operator):
	bl_idname = "wm.get_values_operator1"
	bl_label = "Получить настройки блока"

	def execute(self, context):
		scene = context.scene
		waytool = scene.way_tool

		object = bpy.context.selected_objects[0]
		
		if object.name[0:4] == 'ATTR':
			waytool.attr_int_0 = object['var1']
			waytool.attr_dbl_0 = object['var2']
			waytool.attr_int_1 = object['var3']
			
		elif object.name[0:4] == 'WDTH':
			waytool.wdth_dbl_0 = object['var1']
			waytool.wdth_dbl_1 = object['var2']
			
		elif object.name[0:4] == 'FLAG':
			waytool.flag_int = object['flag']
			
		elif object.name[0:4] == 'MNAM':
			waytool.name_string = object['str']
			
		elif object.name[0:4] == 'RNAM':
			waytool.name_string = object['str']
			
		elif object.name[0:4] == 'NNAM':
			waytool.name_string = object['str']
			
		return {'FINISHED'}
		
class OBJECT_PT_way_edit_panel(Panel):
	bl_idname = "OBJECT_PT_way_edit_panel"
	bl_label = "Редактирование блоков"
	bl_space_type = "VIEW_3D"   
	bl_region_type = "TOOLS"	
	bl_category = "way Tools"
	#bl_context = "objectmode"   

	@classmethod
	def poll(self,context):
		return context.object is not None

	def draw(self, context):
		layout = self.layout
		scene = context.scene
		waytool = scene.way_tool
		
		object = bpy.context.selected_objects[0]
		
		if object.name[0:4] == "ATTR":
			layout.prop(waytool, "attr_int_0")
			layout.prop(waytool, "attr_dbl_0")
			layout.prop(waytool, "attr_int_1")
			
		if object.name[0:4] == "WDTH":
			layout.prop(waytool, "wdth_dbl_0")
			layout.prop(waytool, "wdth_dbl_1")
			
		if object.name[0:4] == "FLAG":
			layout.prop(waytool, "flag_int")
			
		if object.name[0:4] == "MNAM":
			layout.prop(waytool, "name_string")
			
		if object.name[0:4] == "RNAM":
			layout.prop(waytool, "name_string")
			
		if object.name[0:4] == "NNAM":
			layout.prop(waytool, "name_string")
			
		layout.operator("wm.get_values_operator1")
		layout.operator("wm.set_values_operator1")	
		
class OBJECT_PT_way_misc_panel(Panel):
	bl_idname = "OBJECT_PT_way_misc_panel"
	bl_label = "О плагине"
	bl_space_type = "VIEW_3D"   
	bl_region_type = "TOOLS"	
	bl_category = "way Tools"
	#bl_context = "objectmode"   

	@classmethod
	def poll(self,context):
		return context.object is not None

	def draw(self, context):
		layout = self.layout
		scene = context.scene
		waytool = scene.way_tool
		
		self.layout.label("Автор плагина: aleko2144")
		self.layout.label("vk.com/rnr_mods")
		
class OBJECT_PT_blocks_panel(Panel):
	bl_idname = "OBJECT_PT_blocks_panel"
	bl_label = "Создание блоков"
	bl_space_type = "VIEW_3D"   
	bl_region_type = "TOOLS"	
	bl_category = "way Tools"
	#bl_context = "objectmode"   

	@classmethod
	def poll(self,context):
		return context.object is not None

	def draw(self, context):
		layout = self.layout
		scene = context.scene
		waytool = scene.way_tool
		
		layout.prop(waytool, "addWDBlockType_enum")
		
		if waytool.addWDBlockType_enum == "way":
			layout.prop(waytool, "mnam_string")
			
		if waytool.addWDBlockType_enum == "room":
			layout.prop(waytool, "rnam_string")
			
		if waytool.addWDBlockType_enum == "rseg":
			layout.prop(waytool, "attr_1")
			layout.prop(waytool, "attr_2")
			layout.prop(waytool, "attr_3")
			layout.prop(waytool, "wdth_val1")
			layout.prop(waytool, "wdth_val2")
			
		if waytool.addWDBlockType_enum == "rnod" or waytool.addWDBlockType_enum == "ortn":
			layout.prop(waytool, "nnam_string")
			layout.prop(waytool, "flag_val")
		
		layout.operator("wm.add_operator11")
	
# exporter

def MsgBox(label = "", title = "Error", icon = 'ERROR'):

    def draw(self, context):
        self.layout.label(label)

    bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)

def export(context, filepath, use_some_setting):
	file = open(filepath, 'wb')
	#SetBytesLength(bpy.data.objects['way'], True)
	#SetCBytesLength(bpy.data.objects['way'], True)
	#SetRS(bpy.data.objects['way'], True)
	#SetGR(bpy.data.objects['way'], True)
	#SetGD(bpy.data.objects['way'], True)
	#SetMN(bpy.data.objects['way'], True)
	#SetWT(bpy.data.objects['way'], True)
	ClearBytes(bpy.data.objects['way'], True)
	SetNodeBytes(bpy.data.objects['way'], True)
	SetRSEGBytes(bpy.data.objects['way'], True)
	SetRoomBytes(bpy.data.objects['way'], True)
	SetWayBytes(bpy.data.objects['way'], True)
	SetWayBytes1(bpy.data.objects['way'], True)
	writeWTWR(bpy.data.objects['way'], file)
	forChild(bpy.data.objects['way'],True, file)
	
	file.close()

	return {'FINISHED'}

def SetBytesLength(object, root):
	if (not root):
		if object.name[0:4] == 'VDAT': 
			for subcurve in object.data.splines:
				bytes_len = (len(subcurve.points) * 24) + 4 + 4 + 4
			object['bytes_len'] = bytes_len
			object['c_bytes_len'] = 0
				
		if object.name[0:4] == 'ATTR':
			bytes_len = 24
			object['bytes_len'] = bytes_len
			object['c_bytes_len'] = 0
			
		elif object.name[0:4] == 'WDTH':
			bytes_len = 24
			object['bytes_len'] = bytes_len
			object['c_bytes_len'] = 0
			
		elif object.name[0:4] == 'ORTN':
			bytes_len = 96
			object['bytes_len'] = bytes_len
			object['c_bytes_len'] = 0
				
		elif object.name[0:4] == 'POSN':
			bytes_len = 32
			object['bytes_len'] = bytes_len
			object['c_bytes_len'] = 0
				
		elif object.name[0:4] == 'RSEG':
			bytes_len = 8
			object['bytes_len'] = bytes_len
			object['c_bytes_len'] = 0
				
		elif object.name[0:4] == 'RNAM':
		
			text_len = 0
			
			if (len(str(object['str'])) > 15):
				text_len = 20
			
			elif (11 < len(str(object['str'])) < 15 or len(str(object['str'])) == 15):
				text_len = 16
			
			elif (7 < len(str(object['str'])) < 11 or len(str(object['str'])) == 11):
				text_len = 12
			
			elif (3 < len(str(object['str'])) < 7 or len(str(object['str'])) == 7):
				text_len = 8
				
			elif (len(str(object['str'])) < 3 or len(str(object['str'])) == 3):
				text_len = 4
		
			bytes_len = 8 + text_len
			
			object['bytes_len'] = bytes_len
			object['c_bytes_len'] = 0
				
		elif object.name[0:4] == 'RNOD':
			bytes_len = 8
			object['bytes_len'] = bytes_len
			object['c_bytes_len'] = 0
				
		elif object.name[0:4] == 'NNAM':
			text_len = 0
			
			if (len(str(object['str'])) > 15):
				text_len = 20
			
			elif (11 < len(str(object['str'])) < 15 or len(str(object['str'])) == 15):
				text_len = 16
			
			elif (7 < len(str(object['str'])) < 11 or len(str(object['str'])) == 11):
				text_len = 12
			
			elif (3 < len(str(object['str'])) < 7 or len(str(object['str'])) == 7):
				text_len = 8
				
			elif (len(str(object['str'])) < 3 or len(str(object['str'])) == 3):
				text_len = 4
		
			bytes_len = 8 + text_len
			object['bytes_len'] = bytes_len
			object['c_bytes_len'] = 0
			
		elif object.name[0:4] == 'GROM':
			bytes_len = 8
			object['bytes_len'] = bytes_len
			object['c_bytes_len'] = 0
			
		elif object.name[0:4] == 'GDAT':
			bytes_len = 8
			object['bytes_len'] = bytes_len
			object['c_bytes_len'] = 0
			
		elif object.name[0:4] == 'MNAM':
			text_len = 0
			
			if (len(str(object['str'])) > 15):
				text_len = 20
			
			elif (11 < len(str(object['str'])) < 15 or len(str(object['str'])) == 15):
				text_len = 16
			
			elif (7 < len(str(object['str'])) < 11 or len(str(object['str'])) == 11):
				text_len = 12
			
			elif (3 < len(str(object['str'])) < 7 or len(str(object['str'])) == 7):
				text_len = 8
				
			elif (len(str(object['str'])) < 3 or len(str(object['str'])) == 3):
				text_len = 4
		
			bytes_len = 8 + text_len
			object['bytes_len'] = bytes_len
			object['c_bytes_len'] = 0
				
		elif object.name[0:4] == 'WTWR':
			bytes_len = 8
			object['bytes_len'] = bytes_len
			object['c_bytes_len'] = 0
				
		elif object.name[0:4] == 'FLAG':
			bytes_len = 12
			object['bytes_len'] = bytes_len
			object['c_bytes_len'] = 0
			#object['flag'] = 1
			
	for child in object.children:
		SetBytesLength(child,False)
		

def SetCBytesLength(object, root):
	varCB = 0
	if (not root):
		if object.name[0:4] == 'RSEG':
			bytes_len = 8
				
		elif object.name[0:4] == 'RNOD':
			for x in range (len(object.children)):
				varCB += object.children[x]['bytes_len']
		
			object['c_bytes_len'] = varCB
			
	for child in object.children:
		SetCBytesLength(child,False)	

def SetRS(object, root):	
	varRS = 0
	if (not root):
		if object.name[0:4] == 'RSEG':
			for r in range (len(object.children)):
				varRS += object.children[r]['bytes_len'] + object.children[r]['c_bytes_len']
		
			object['c_bytes_len'] = varRS
	
	for child in object.children:
		SetRS(child, False)	
		
def SetGR(object, root):
	varGR = 0
	if (not root):
		if object.name[0:4] == 'GROM':
			for j in range (len(object.children)):
				varGR += object.children[j]['bytes_len'] + object.children[j]['c_bytes_len']
		
			object['c_bytes_len'] = varGR
	
	for child in object.children:
		SetGR(child, False)
		
def SetGD(object, root):
	variable = 0
	if (not root):
		if object.name[0:4] == 'GDAT':
			for n in range (len(object.children)):
				variable += object.children[n]['bytes_len'] + object.children[n]['c_bytes_len']
		
			object['c_bytes_len'] = variable
	
	for child in object.children:
		SetGD(child, False)
		
def SetMN(object, root):
	varMN = 0
	if (not root):
		if object.name[0:4] == 'MNAM':
			for i in range (len(object.children)):
				varMN = object.children[i]['bytes_len'] + object.children[i]['c_bytes_len']
		
			object['c_bytes_len'] = varMN
			
	for child in object.children:
		SetMN(child, False)
		
def SetWT(object, root):
	varWT = 0
	if (not root):
		if object.name[0:4] == 'WTWR':
			for i in range (len(object.children)):
				varWT = object.children[i]['bytes_len'] + object.children[i]['c_bytes_len']
		
			object['c_bytes_len'] = varWT
			
	for child in object.children:
		SetWT(child, False)
				
		
def GetCBytesLength(object, root):
	var1 = 0
	if (not root):
		#for object in bpy.data.objects:
		if (object.children):
			for i in range (len(object.children)):
				var1 = object.children[i]['bytes_len'] + object['bytes_len']
				#object['c_bytes_len'] = var1 
				object['c_bytes_len'] = var1 + object['c_bytes_len']
			print(str(var1))
			
	for child in object.children:
		GetCBytesLength(child,False)
		
def SetRSEGBytes(object, root):	
	if (not root):
		if object['type'] == 'rseg':
			for subcurve in object.data.splines:
				object['bytes_len'] = 68 + len(subcurve.points) * 24
	
			room = object.parent
			room['c_bytes_len'] += object['bytes_len']
			
	for child in object.children:
		SetRSEGBytes(child, False)	
		
def SetNodeBytes(object, root):	
	var_node = 0
	print("SetNodeBytes")
	try:
		if object['type'] == 'rnod' or object['type'] == 'ortn':
			object_name = object.name.split(".")[0]
			text_len1 = 0
			if (len(str(object_name)) > 15):
				text_len1 = 20
			
			elif (11 < len(str(object_name)) < 15 or len(str(object_name)) == 15):
				text_len1 = 16
			
			elif (7 < len(str(object_name)) < 11 or len(str(object_name)) == 11):
				text_len1 = 12
			
			elif (3 < len(str(object_name)) < 7 or len(str(object_name)) == 7):
				text_len1 = 8
				
			elif (len(str(object_name)) < 3 or len(str(object_name)) == 3):
				text_len1 = 4
			
			var_node = text_len1 + 16 + 32 + 12
			if object['type'] == "ortn":
				var_node += 104
			object['bytes_len'] = var_node
			
			#object.parent['c_bytes_len'] += var_node
			room = object.parent
			room['c_bytes_len'] += var_node

		for child in object.children:
			SetNodeBytes(child, False)
	except:
		pass
		
def SetRoomBytes(object, root):	
	var_r = 0
	if object['type'] == 'room':
		object_name = object.name.split(".")[0]
		text_len1 = 0
		if (len(str(object_name)) > 15):
			text_len1 = 20
			
		elif (11 < len(str(object_name)) < 15 or len(str(object_name)) == 15):
			text_len1 = 16
			
		elif (7 < len(str(object_name)) < 11 or len(str(object_name)) == 11):
			text_len1 = 12
		
		elif (3 < len(str(object_name)) < 7 or len(str(object_name)) == 7):
			text_len1 = 8
				
		elif (len(str(object_name)) < 3 or len(str(object_name)) == 3):
			text_len1 = 4
			
		var_r = text_len1 + 16
		
		object['bytes_len'] = var_r #+ 8
		
		#way = object.parent
		#way['c_bytes_len'] += object['bytes_len']

	for child in object.children:
		SetRoomBytes(child, False)
		
def SetWayBytes(object, root):	
	if object['type'] == 'room':
		way = object.parent
		print(object['bytes_len'])
		way['c_bytes_len'] = way['c_bytes_len'] + object['c_bytes_len'] + object['bytes_len']

	for child in object.children:
		SetWayBytes(child, False)
		
def SetWayBytes1(object, root):	
	if object['type'] == 'way':
		object['bytes_len'] = 20 + object['c_bytes_len']

	for child in object.children:
		SetWayBytes1(child, False)
		
def ClearBytes(object, root):	
	if object['type'] == 'room':
		object['bytes_len'] = 0
		object['c_bytes_len'] = 0
		
	if object['type'] == 'way':
		object['bytes_len'] = 0
		object['c_bytes_len'] = 0

	for child in object.children:
		ClearBytes(child, False)
		
def writeWTWR(object, file):
	file.write(str.encode('WTWR'))
	file.write(struct.pack("<i", object['bytes_len']))
				
	file.write(str.encode('MNAM'))
	file.write(struct.pack("<i", len(str(object['mnam'])) + 1))
	file.write(str.encode(str(object['mnam']))+bytearray(b'\x00'*2))
				
	file.write(str.encode('GDAT'))
	file.write(struct.pack("<i", object['c_bytes_len']))
	
def forChild(object, root, file):
	if (not root):
		#for object in bpy.data.objects:
		bytes_len = 0
		obj_len = len(object.children)
		if object['type'] == 'rseg':
			file.write(str.encode('RSEG'))
			
			for subcurve in object.data.splines:
				object['bytes_len'] = 68 + len(subcurve.points) * 24
				object['c_bytes_len'] = 60 + len(subcurve.points) * 24
				file.write(struct.pack("<i", object['c_bytes_len']))
			
			file.write(str.encode('ATTR'))
			file.write(struct.pack("<i", 16))
			file.write(struct.pack("<i", object['attr1']))
			file.write(struct.pack("<d", object['attr2']))
			file.write(struct.pack("<i", object['attr3']))
			
			file.write(str.encode('WDTH'))
			file.write(struct.pack("<i", 16))
			file.write(struct.pack("<d", object['wdth1']))
			file.write(struct.pack("<d", object['wdth2']))
			
			for subcurve in object.data.splines:
				file.write(str.encode('VDAT'))
				bytes_len = (len(subcurve.points) * 24) + 4
				file.write(struct.pack("<i",bytes_len))
				file.write(struct.pack("<i",len(subcurve.points)))
			for point in subcurve.points:
				file.write(struct.pack("<d",point.co.x))
				file.write(struct.pack("<d",point.co.y))
				file.write(struct.pack("<d",point.co.z))
			
		elif object['type'] == 'rnod' or object['type'] == "ortn":
			file.write(str.encode('RNOD'))
			object_name = object.name.split(".")[0]
			text_len1 = 0
			if (len(str(object_name)) > 15):
				text_len1 = 20
			
			elif (11 < len(str(object_name)) < 15 or len(str(object_name)) == 15):
				text_len1 = 16
			
			elif (7 < len(str(object_name)) < 11 or len(str(object_name)) == 11):
				text_len1 = 12
			
			elif (3 < len(str(object_name)) < 7 or len(str(object_name)) == 7):
				text_len1 = 8
				
			elif (len(str(object_name)) < 3 or len(str(object_name)) == 3):
				text_len1 = 4
				
			object['c_bytes_len'] = text_len1 + 8 + 32 + 12
			
			if object['type'] == "ortn":
				object['c_bytes_len'] += 104
				
			file.write(struct.pack("<i", object['c_bytes_len']))
				
			file.write(str.encode('NNAM'))
			file.write(struct.pack("<i", len(str(object_name)) + 1))
			text_len = 0
			
			if (len(str(object_name)) > 15):
				file.write(str.encode(object_name)+bytearray(b'\x00'*(20-len(str(object_name)))))
				text_len = 20
			
			elif (11 < len(str(object_name)) < 15 or len(str(object_name)) == 15):
				file.write(str.encode(object_name)+bytearray(b'\x00'*(16-len(str(object_name)))))
				text_len = 16
			
			elif (7 < len(str(object_name)) < 11 or len(str(object_name)) == 11):
				file.write(str.encode(object_name)+bytearray(b'\x00'*(12-len(str(object_name)))))
				text_len = 12
			
			elif (3 < len(str(object_name)) < 7 or len(str(object_name)) == 7):
				file.write(str.encode(object_name)+bytearray(b'\x00'*(8-len(str(object_name)))))
				text_len = 8
				
			elif (len(str(object_name)) < 3 or len(str(object_name)) == 3):
				file.write(str.encode(object_name)+bytearray(b'\x00'*(4-len(str(object_name)))))
				text_len = 4
		
			#bytes_len = 8 + text_len
			
			file.write(str.encode('POSN'))
			file.write(struct.pack("<i", 24))
			file.write(struct.pack("<d", object.location.x))
			file.write(struct.pack("<d", object.location.y))
			file.write(struct.pack("<d", object.location.z))
			
			if object['type'] == "ortn":
				object_matrix = object.matrix_world.to_3x3()
			
				file.write(str.encode('ORTN'))
				file.write(struct.pack("<i", 96))
					
				file.write(struct.pack("<d",object_matrix[0][0]))
				file.write(struct.pack("<d",object_matrix[0][1]))
				file.write(struct.pack("<d",object_matrix[0][2]))
					
				file.write(struct.pack("<d",object_matrix[1][0]))
				file.write(struct.pack("<d",object_matrix[1][1]))
				file.write(struct.pack("<d",object_matrix[1][2]))
					
				file.write(struct.pack("<d",object_matrix[2][0]))
				file.write(struct.pack("<d",object_matrix[2][1]))
				file.write(struct.pack("<d",object_matrix[2][2]))
				
				file.write(struct.pack("<d", object.location.x))
				file.write(struct.pack("<d", object.location.y))
				file.write(struct.pack("<d", object.location.z))
				
			file.write(str.encode('FLAG'))
			file.write(struct.pack("<ii", 4, object['flag']))
			
		elif object['type'] == "room":
			file.write(str.encode('GROM'))
			
			object_name = object.name.split(".")[0]
			text_len1 = 0
			if (len(str(object_name)) > 15):
				text_len1 = 20
			
			elif (11 < len(str(object_name)) < 15 or len(str(object_name)) == 15):
				text_len1 = 16
			
			elif (7 < len(str(object_name)) < 11 or len(str(object_name)) == 11):
				text_len1 = 12
			
			elif (3 < len(str(object_name)) < 7 or len(str(object_name)) == 7):
				text_len1 = 8
				
			elif (len(str(object_name)) < 3 or len(str(object_name)) == 3):
				text_len1 = 4
			
			object['bytes_len'] = 8 + text_len1 + object['c_bytes_len']
			object['c_bytes_len'] = object['c_bytes_len'] + 20
			
			file.write(struct.pack("<i", object['c_bytes_len']))
		
			file.write(str.encode('RNAM'))
			file.write(struct.pack("<i", len(str(object_name)) + 1))
			text_len = 0
			
			if (len(str(object_name)) > 15):
				file.write(str.encode(object_name)+bytearray(b'\x00'*(20-len(str(object_name)))))
				text_len = 20
			
			elif (11 < len(str(object_name)) < 15 or len(str(object_name)) == 15):
				file.write(str.encode(object_name)+bytearray(b'\x00'*(16-len(str(object_name)))))
				text_len = 16
			
			elif (7 < len(str(object_name)) < 11 or len(str(object_name)) == 11):
				file.write(str.encode(object_name)+bytearray(b'\x00'*(12-len(str(object_name)))))
				text_len = 12
			
			elif (3 < len(str(object_name)) < 7 or len(str(object_name)) == 7):
				file.write(str.encode(object_name)+bytearray(b'\x00'*(8-len(str(object_name)))))
				text_len = 8
				
			elif (len(str(object_name)) < 3 or len(str(object_name)) == 3):
				file.write(str.encode(object_name)+bytearray(b'\x00'*(4-len(str(object_name)))))
				text_len = 4

	for child in object.children:
		forChild(child,False,file)

# ExportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator

class ImportSomeData(Operator, ExportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "import_test.some_data"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Import *.way"

    # ExportHelper mixin class uses this
    filename_ext = ".way"

    filter_glob = StringProperty(
            default="*.way",
            options={'HIDDEN'},
            maxlen=255,  # Max internal buffer length, longer would be clamped.
            )

    def execute(self, context):
        from . import import_way
        with open(self.filepath, 'r') as file:
            import_way.read(self.filepath, context)
        return {'FINISHED'}

class ExportSomeData(Operator, ExportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "export_test.some_data"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Export *.way"

    # ExportHelper mixin class uses this
    filename_ext = ".way"

    filter_glob = StringProperty(
            default="*.way",
            options={'HIDDEN'},
            maxlen=255,  # Max internal buffer length, longer would be clamped.
            )

    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling.
    use_setting = BoolProperty(
            name="Example Boolean",
            description="Example Tooltip",
            default=True,
            )

    type = EnumProperty(
            name="Example Enum",
            description="Choose between two items",
            items=(('OPT_A', "First Option", "Description one"),
                   ('OPT_B', "Second Option", "Description two")),
            default='OPT_A',
            )

    def execute(self, context):
        return export(context, self.filepath, self.use_setting)


# Only needed if you want to add into a dynamic menu
def menu_func_export(self, context):
    self.layout.operator(ExportSomeData.bl_idname, text="Export KOTR *.way")
	
def menu_func_import(self, context):
    self.layout.operator(ImportSomeData.bl_idname, text="Import KOTR *.way")

def register():
	bpy.utils.register_class(ExportSomeData)
	bpy.types.INFO_MT_file_export.append(menu_func_export)
	
	bpy.utils.register_class(ImportSomeData)
	bpy.types.INFO_MT_file_import.append(menu_func_import)
	
	bpy.utils.register_module(__name__)
	bpy.types.Scene.way_tool = PointerProperty(type=PanelSettings1)


def unregister():
	bpy.utils.unregister_class(ExportSomeData)
	bpy.types.INFO_MT_file_export.remove(menu_func_export)
	
	bpy.utils.unregister_class(ImportSomeData)
	bpy.types.INFO_MT_file_import.remove(menu_func_import)
	
	bpy.utils.unregister_module(__name__)
	del bpy.types.Scene.way_tool


if __name__ == "__main__":
    register()

    # test call
    bpy.ops.export_test.some_data('INVOKE_DEFAULT')
