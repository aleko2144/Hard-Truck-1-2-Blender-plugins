

if "bpy" in locals():
    print("Reimporting modules!!!")
    import importlib
    importlib.reload(scripts)
else:
    import bpy
    from . import (
        scripts
    )

from ..common import (
	getRegion
)

from .. import consts

from .common import (
	isRootObj
)
from .scripts import (
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
	setAllObjsByType,
	getPerFaceByType,
	setPerFaceByType,
	getPerVertexByType,
	setPerVertexByType,
	showHideSphere,

)


from .classes import (
	block_1,block_2,block_3,block_4,block_5,block_6,block_7,block_8,block_9,block_10,\
	block_11,block_12,block_13,block_14,block_15,block_16,block_17,block_18,block_20,\
	block_21,block_22,block_23,block_24,block_25,block_26,block_27,block_28,block_29,block_30,\
	block_31,block_33,block_34,block_35,block_36,block_37,block_39,block_40,block_common,\
	perFaceBlock_8, perFaceBlock_28, perFaceBlock_35, perVertBlock_8, perVertBlock_35
)
from .class_descr import (
	getClassDefByType,
	b_1,b_2,b_3,b_4,b_5,b_6,b_7,b_8,b_9,b_10,\
	b_11,b_12,b_13,b_14,b_15,b_16,b_17,b_18,b_20,\
	b_21,b_22,b_23,b_24,b_25,b_26,b_27,b_28,b_29,b_30,\
	b_31,b_33,b_34,b_35,b_36,b_37,b_39,b_40,b_common, \
	pfb_8, pfb_28, pfb_35, pvb_8, pvb_35,
	ResBlock
)


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




# ------------------------------------------------------------------------
#	store properties in the active scene
# ------------------------------------------------------------------------

def resModuleCallback(scene, context):

	mytool = context.scene.my_tool
	resModules = mytool.resModules

	enumProperties = [(str(i), cn.value, "") for i, cn in enumerate(resModules)]

	return enumProperties



class PanelSettings(bpy.types.PropertyGroup):

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

	perFaceBlock8: PointerProperty(type=perFaceBlock_8)
	perFaceBlock28: PointerProperty(type=perFaceBlock_28)
	perFaceBlock35: PointerProperty(type=perFaceBlock_35)
	perVertBlock8: PointerProperty(type=perVertBlock_8)
	perVertBlock35: PointerProperty(type=perVertBlock_35)

	resModules: CollectionProperty(type=ResBlock)

	selectedResModule: EnumProperty(
        name="RES module",
        description="Selected RES module",
        items=resModuleCallback
	)

	conditionGroup : bpy.props.IntProperty(
		name='Event number',
		description='Event number(object group), that should be shown/hidden. If -1, then all events are chosen. If event number is too big, closest suitable number is chosen.',
		default=-1,
		min=-1
	)

	BlockName_string : bpy.props.StringProperty(
		name="Block name",
		default="",
		maxlen=30,
		)

	addBlockType_enum : bpy.props.EnumProperty(
		name="Block type",
		items= consts.blockTypeList
		)

	Radius : bpy.props.FloatProperty(
		name = "Block rad",
		description = "Block rendering distance",
		default = 1.0,
		)

	addBlocks_enum : bpy.props.EnumProperty(
		name="Assembly type",
		items=[ ('room', "Room", "Room"),
				#('07', "07", "Mesh (HT1)"),
				#('10', "10", "LOD"),
				#('12', "12", "Unk"),
				#('14', "14", "Car trigger"),
				#('18', "18", "Connector"),
				#('19', "19", "Room container"),
				#('20', "20", "2D collision"),
				#('21', "21", "Event container"),
				#('23', "23", "3D collision"),
				#('24', "24", "Locator"),
				#('28', "28", "2D-sprite"),
				#('33', "33", "Light source"),
				#('37', "37", "Mesh"),
				#('40', "40", "Object generator"),
			   ]
		)

	addRoomNameIndex_string : bpy.props.StringProperty(
		name="Room name",
		description="",
		default="aa_000",
		maxlen=30,
		)

	mirrorType_enum : bpy.props.EnumProperty(
		name="Block type",
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
	bl_label = "Add block to scene"

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
			bpy.context.scene.objects.link(object)

		elif block_type == 1:
			object = bpy.data.objects.new(object_name, None)
			object.location=cursor_pos
			object['block_type'] = block_type
			setAllObjsByType(context, object, b_1)
			bpy.context.scene.objects.link(object)

		elif block_type == 2:
			object = bpy.data.objects.new(object_name, None)
			object.location=cursor_pos
			object['block_type'] = block_type
			setAllObjsByType(context, object, b_2)
			bpy.context.scene.objects.link(object)

		elif block_type == 3:
			object = bpy.data.objects.new(object_name, None)
			object.location=cursor_pos
			object['block_type'] = block_type
			setAllObjsByType(context, object, b_3)
			bpy.context.scene.objects.link(object)

		elif block_type == 4:
			object = bpy.data.objects.new(object_name, None)
			object.location=cursor_pos #(0.0,0.0,0.0)
			object['block_type'] = block_type
			setAllObjsByType(context, object, b_4)
			bpy.context.scene.objects.link(object)

		elif block_type == 5:
			object = bpy.data.objects.new(object_name, None)
			object.location=cursor_pos #(0.0,0.0,0.0)
			object['block_type'] = block_type
			setAllObjsByType(context, object, b_5)
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
			bpy.context.scene.objects.link(object)

		elif block_type == 13:
			object = bpy.data.objects.new(object_name, None)
			object.location=cursor_pos
			object['block_type'] = block_type
			setAllObjsByType(context, object, b_13)
			bpy.context.scene.objects.link(object)

		elif block_type == 14:
			object = bpy.data.objects.new(object_name, None)
			object.location=cursor_pos
			object['block_type'] = block_type
			setAllObjsByType(context, object, b_14)

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
			context.scene.objects.link(object)

		elif block_type == 21:
			object['block_type'] = block_type
			object.location=cursor_pos
			setAllObjsByType(context, object, b_20)
			bpy.context.scene.objects.link(object)

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
			object = bpy.data.objects.new(object_name, None)
			object.location=cursor_pos
			object['block_type'] = block_type
			setAllObjsByType(context, object, b_24)
			bpy.context.scene.objects.link(object)

		elif block_type == 25:
			object = bpy.data.objects.new(object_name, None)
			object.location=cursor_pos
			object['block_type'] = block_type
			setAllObjsByType(context, object, b_25)
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
			bpy.context.scene.objects.link(object)

		elif block_type == 29:
			object = bpy.data.objects.new(object_name, None)
			object.location=cursor_pos
			object['block_type'] = block_type
			setAllObjsByType(context, object, b_29)
			bpy.context.scene.objects.link(object)

		elif block_type == 30:
			object = bpy.data.objects.new(object_name, None)
			object.location=cursor_pos
			object['block_type'] = block_type
			setAllObjsByType(context, object, b_30)
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
		return {'FINISHED'}

class GetVertexValuesOperator(bpy.types.Operator):
	bl_idname = "wm.get_vertex_values_operator"
	bl_label = "Get block values"

	def execute(self, context):
		object = bpy.context.selected_objects[0]
		block_type = object['block_type']

		if block_type == 8:
			getPerVertexByType(context, object, pvb_8)
		elif block_type == 35:
			getPerVertexByType(context, object, pvb_35)

		return {'FINISHED'}

class GetFaceValuesOperator(bpy.types.Operator):
	bl_idname = "wm.get_face_values_operator"
	bl_label = "Get block values"

	def execute(self, context):
		object = bpy.context.selected_objects[0]
		block_type = object['block_type']

		if block_type == 8:
			getPerFaceByType(context, object, pfb_8)
		elif block_type == 28:
			getPerFaceByType(context, object, pfb_28)
		elif block_type == 35:
			getPerFaceByType(context, object, pfb_35)

		return {'FINISHED'}

class GetValuesOperator(bpy.types.Operator):
	bl_idname = "wm.get_block_values_operator"
	bl_label = "Get block values"

	def execute(self, context):
		scene = context.scene
		mytool = scene.my_tool

		object = bpy.context.object
		block_type = object['block_type']

		zclass = getClassDefByType(block_type)

		if zclass is not None:
			getAllObjsByType(context, object, zclass)

		return {'FINISHED'}

class SetFaceValuesOperator(bpy.types.Operator):
	bl_idname = "wm.set_face_values_operator"
	bl_label = "Save block values"

	def execute(self, context):
		curtype = bpy.context.object['block_type']
		objects = [cn for cn in bpy.context.selected_objects if cn['block_type'] is not None and cn['block_type'] == curtype]

		for i in range(len(objects)):

			object = objects[i]
			block_type = object['block_type']

			if block_type == 8:
				setPerFaceByType(context, object, pfb_8)
			elif block_type == 28:
				setPerFaceByType(context, object, pfb_28)
			elif block_type == 35:
				setPerFaceByType(context, object, pfb_35)

		return {'FINISHED'}

class SetVertexValuesOperator(bpy.types.Operator):
	bl_idname = "wm.set_vertex_values_operator"
	bl_label = "Save block values"

	def execute(self, context):
		curtype = bpy.context.object['block_type']
		objects = [cn for cn in bpy.context.selected_objects if cn['block_type'] is not None and cn['block_type'] == curtype]

		for i in range(len(objects)):

			object = objects[i]
			block_type = object['block_type']

			if block_type == 8:
				setPerVertexByType(context, object, pvb_8)
			elif block_type == 35:
				setPerVertexByType(context, object, pvb_35)

		return {'FINISHED'}

class SetValuesOperator(bpy.types.Operator):
	bl_idname = "wm.set_block_values_operator"
	bl_label = "Save block values"

	def execute(self, context):
		scene = context.scene
		mytool = scene.my_tool

		global block_type
		global lenStr
		#object = bpy.context.selected_objects[0]

		active_obj = bpy.context.object

		curtype = active_obj['block_type']

		objects = [cn for cn in bpy.context.selected_objects if cn['block_type'] is not None and cn['block_type'] == curtype]

		for i in range(len(objects)):

			object = objects[i]

			if 'block_type' in object:
				block_type = object['block_type']
			else:
				block_type = 0

			object['block_type'] = block_type

			zclass = getClassDefByType(block_type)

			if zclass is not None:
				setAllObjsByType(context, object, zclass)

		return {'FINISHED'}

class DelValuesOperator(bpy.types.Operator):
	bl_idname = "wm.del_block_values_operator"
	bl_label = "Delete block values"

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
	bl_label = "Fix UV for export"

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
	bl_label = "Fix mesh for export"

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
	bl_label = "Mirror objects"

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
	bl_label = "Arrange/Remove objects"
	bl_description = "Creates copies of objects and arrange them at places(24) specified in connector(18)"

	def execute(self, context):
		scene = context.scene
		mytool = scene.my_tool

		applyRemoveTransforms(self)

		return {'FINISHED'}

class ShowHideCollisionsOperator(bpy.types.Operator):
	bl_idname = "wm.show_hide_collisions_operator"
	bl_label = "Show/Hide collisions"
	bl_description = "If all 3d collisions(23) are hidden, shows them. otherwise - hide."

	def execute(self, context):
		scene = context.scene
		mytool = scene.my_tool

		showHideObjByType(self, 23)

		return {'FINISHED'}

class ShowHideRoomBordersOperator(bpy.types.Operator):
	bl_idname = "wm.show_hide_room_borders_operator"
	bl_label = "Show/Hide portals"
	bl_description = "If all portals(30) are hidden, shows them. Otherwise - hide."

	def execute(self, context):
		scene = context.scene
		mytool = scene.my_tool

		showHideObjByType(self, 30)

		return {'FINISHED'}

class ShowHideGeneratorsOperator(bpy.types.Operator):
	bl_idname = "wm.show_hide_generator_operator"
	bl_label = "Show/Hide generator blocks"
	bl_description = "If all generator blocks(40) are hidden, shows them. Otherwise - hide."

	def execute(self, context):
		scene = context.scene
		mytool = scene.my_tool

		showHideObjByType(self, 40)

		return {'FINISHED'}

class ShowLODOperator(bpy.types.Operator):
	bl_idname = "wm.show_lod_operator"
	bl_label = "Show LOD"
	bl_description = "Shows LOD(10) of selected object. " + \
					"If there is no active object, show LOD of all scene objects."

	def execute(self, context):
		scene = context.scene
		mytool = scene.my_tool

		objs = context.selected_objects
		if not len(objs):
			objs = [cn for cn in bpy.data.objects if isRootObj(cn)]

		for obj in objs:
			showLOD(obj)
		self.report({'INFO'}, "{} LOD objects(block 10) are shown".format(len(objs)))

		return {'FINISHED'}

class HideLODOperator(bpy.types.Operator):
	bl_idname = "wm.hide_lod_operator"
	bl_label = "Hide LOD"
	bl_description = "Hides LOD(10) of selected object. " + \
					"If there is no active object, hide LOD of all scene objects."

	def execute(self, context):
		scene = context.scene
		mytool = scene.my_tool

		objs = context.selected_objects
		if not len(objs):
			objs = [cn for cn in bpy.data.objects if isRootObj(cn)]

		for obj in objs:
			hideLOD(obj)
		self.report({'INFO'}, "{} LOD objects(block 10) are hidden".format(len(objs)))

		return {'FINISHED'}

class ShowConditionalsOperator(bpy.types.Operator):
	bl_idname = "wm.show_conditional_operator"
	bl_label = "Show events"
	bl_description = "Show event from selected event block(21). " + \
					"If there is no active event block, show event of all scene event objects(21)"

	group : bpy.props.IntProperty()

	def execute(self, context):
		scene = context.scene
		mytool = scene.my_tool

		objs = context.selected_objects
		if not len(objs):
			objs = [cn for cn in bpy.data.objects if isRootObj(cn)]

		for obj in objs:
			showConditionals(obj, self.group)
		self.report({'INFO'}, "{} Conditional objects(block 21) are shown".format(len(objs)))


		return {'FINISHED'}

class HideConditionalsOperator(bpy.types.Operator):
	bl_idname = "wm.hide_conditional_operator"
	bl_label = "Hide events"
	bl_description = "Hide event from selected event block(21). " + \
					"If there is no active event block, hide event of all scene event objects(21)"

	group : bpy.props.IntProperty()

	def execute(self, context):
		scene = context.scene
		mytool = scene.my_tool

		objs = context.selected_objects
		if not len(objs):
			objs = [cn for cn in bpy.data.objects if isRootObj(cn)]

		for obj in objs:
			hideConditionals(obj, self.group)
		self.report({'INFO'}, "{} Conditional objects(block 21) are hidden".format(len(objs)))

		return {'FINISHED'}

class AddBlocksOperator(bpy.types.Operator):
	bl_idname = "wm.add1_operator"
	bl_label = "Add block assembly to scene"

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

class ShowHideSphereOperator(bpy.types.Operator):
	bl_idname = "wm.show_hide_sphere_operator"
	bl_label = "Show/Hide sphere"
	bl_description = "Shows/Hides sphere"

	pname: bpy.props.StringProperty()

	def execute(self, context):
		scene = context.scene
		mytool = scene.my_tool

		obj = context.object

		showHideSphere(context, obj, self.pname)

		self.report({'INFO'}, "Sphere shown or hidden")

		return {'FINISHED'}

class GetValuesModalOperator(bpy.types.Operator):
	bl_idname = "wm.get_block_values_modal_operator"
	bl_label = "Automatically get block values on object select"
	bl_description = "Updates values in b3d panel"

	# @classmethod
	# def poll(cls, context):
	# 	return context.object is not None and context.object.get('block_type') is not None

	def modal(self, context, event):
		if event.type == 'LEFTMOUSE':
			if context.object is not None:
				obj = context.object
				if context.object.get('block_type') is not None:
					block_type = obj.get('block_type')

					zclass = getClassDefByType(block_type)
					if zclass is not None:
						getAllObjsByType(context, obj, zclass)

		return {'PASS_THROUGH'}

	def execute(self, context):
		wm = context.window_manager
		wm.modal_handler_add(self)
		return {'RUNNING_MODAL'}


# ------------------------------------------------------------------------
# panels
# ------------------------------------------------------------------------

class OBJECT_PT_b3d_add_panel(bpy.types.Panel):
	bl_idname = "OBJECT_PT_b3d_add_panel"
	bl_label = "Add blocks"
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

		self.layout.label(text="Block type:")
		layout.prop(mytool, "addBlockType_enum", text="")
		layout.prop(mytool, "BlockName_string")

		zclass = getClassDefByType(block_type)

		if zclass is not None:
			drawAllFieldsByType(self, context, zclass)

		layout.operator("wm.add_operator")

class OBJECT_PT_b3d_pfb_edit_panel(bpy.types.Panel):
	bl_idname = "OBJECT_PT_b3d_pfb_edit_panel"
	bl_label = "Polygon params"
	bl_parent_id = "OBJECT_PT_b3d_edit_panel"
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

		object = bpy.context.object

		if object is not None:

			if 'block_type' in object:
				block_type = object['block_type']
			else:
				block_type = None

			if block_type == 8:
				drawAllFieldsByType(self, context, pfb_8)
			if block_type == 28:
				drawAllFieldsByType(self, context, pfb_28)
			if block_type == 35:
				drawAllFieldsByType(self, context, pfb_35)


		layout.operator("wm.get_face_values_operator")
		layout.operator("wm.set_face_values_operator")

class OBJECT_PT_b3d_pvb_edit_panel(bpy.types.Panel):
	bl_idname = "OBJECT_PT_b3d_pvb_edit_panel"
	bl_label = "Vertex params"
	bl_parent_id = "OBJECT_PT_b3d_edit_panel"
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

		object = bpy.context.object

		if object is not None:

			if 'block_type' in object:
				block_type = object['block_type']
			else:
				block_type = None

			if block_type == 8:
				drawAllFieldsByType(self, context, pvb_8)
			if block_type == 35:
				drawAllFieldsByType(self, context, pvb_35)


		layout.operator("wm.get_vertex_values_operator")
		layout.operator("wm.set_vertex_values_operator")

class OBJECT_PT_b3d_edit_panel(bpy.types.Panel):
	bl_idname = "OBJECT_PT_b3d_edit_panel"
	bl_label = "Block edit"
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

		object = bpy.context.object
		if object is not None:
			drawCommon(self, object)

class OBJECT_PT_b3d_pob_edit_panel(bpy.types.Panel):
	bl_idname = "OBJECT_PT_b3d_pob_edit_panel"
	bl_label = "Object params"
	bl_parent_id = "OBJECT_PT_b3d_edit_panel"
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

		object = bpy.context.object

		# if len(bpy.context.selected_objects):
		# 	for i in range(1):
		if object is not None:

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

			zclass = getClassDefByType(block_type)

			layout.operator("wm.get_block_values_operator")
			layout.operator("wm.set_block_values_operator")

			if zclass is not None:
				drawAllFieldsByType(self, context, zclass)

			# else:
			# 	self.layout.label(text="Выбранный объект не имеет типа.")
			# 	self.layout.label(text="Чтобы указать его, нажмите на кнопку сохранения настроек.")

			layout.operator("wm.del_block_values_operator")
			layout.operator("wm.fix_uv_operator")
			layout.operator("wm.fix_verts_operator")

class OBJECT_PT_b3d_blocks_panel(bpy.types.Panel):
	bl_idname = "OBJECT_PT_b3d_blocks_panel"
	bl_label = "Blocks assembly"
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

		type = mytool.addBlocks_enum

		layout.prop(mytool, "addBlocks_enum")

		if type == "room":
			layout.prop(mytool, "addRoomNameIndex_string")
			layout.prop(mytool, "Radius")

		layout.operator("wm.add1_operator")

class OBJECT_PT_b3d_func_panel(bpy.types.Panel):
	bl_idname = "OBJECT_PT_b3d_func_panel"
	bl_label = "Additional options"
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

class OBJECT_PT_b3d_res_module_panel(bpy.types.Panel):
	bl_idname = "OBJECT_PT_b3d_res_module_panel"
	bl_label = "RES resources"
	bl_space_type = "VIEW_3D"
	bl_region_type = getRegion()
	bl_category = "b3d Tools"

	@classmethod
	def poll(self,context):
		return context.object is not None

	def draw(self, context):
		layout = self.layout
		scene = context.scene
		mytool = scene.my_tool

		layout.prop(mytool, "selectedResModule")

class OBJECT_PT_b3d_maskfiles_panel(bpy.types.Panel):
	bl_idname = "OBJECT_PT_b3d_maskfiles_panel"
	bl_label = "MSK-files"
	bl_parent_id = "OBJECT_PT_b3d_res_module_panel"
	bl_space_type = "VIEW_3D"
	bl_region_type = getRegion()
	bl_category = "b3d Tools"

	@classmethod
	def poll(self,context):
		return context.object is not None

	def draw(self, context):
		layout = self.layout
		scene = context.scene
		mytool = scene.my_tool

		currentRes = int(mytool.selectedResModule)
		curResModule = mytool.resModules[currentRes]

		box = self.layout.box()

		rows = 2
		row = box.row()
		row.template_list("CUSTOM_UL_items", "maskfiles_list", curResModule, "maskfiles", scene, "maskfiles_index", rows=rows)

		col = row.column(align=True)

		props = col.operator("custom.list_action_arrbname", icon='ADD', text="")
		props.action = 'ADD'
		props.bname = "resModules"
		props.bindex = currentRes
		props.pname = "maskfiles"
		props.customindex = "maskfiles_index"

		props = col.operator("custom.list_action_arrbname", icon='REMOVE', text="")
		props.action = 'REMOVE'
		props.bname = "resModules"
		props.bindex = currentRes
		props.pname = "maskfiles"
		props.customindex = "maskfiles_index"

		col.separator()

		props = col.operator("custom.list_action_arrbname", icon='TRIA_UP', text="")
		props.action = 'UP'
		props.bname = "resModules"
		props.bindex = currentRes
		props.pname = "maskfiles"
		props.customindex = "maskfiles_index"

		props = col.operator("custom.list_action_arrbname", icon='TRIA_DOWN', text="")
		props.action = 'DOWN'
		props.bname = "resModules"
		props.bindex = currentRes
		props.pname = "maskfiles"
		props.customindex = "maskfiles_index"

		#Maskfile edit
		box = self.layout.box()

		maskfiles_index = scene.maskfiles_index
		if len(curResModule.maskfiles):
			curMaskfile = curResModule.maskfiles[maskfiles_index]

			box.prop(curMaskfile, "is_noload", text="Noload")

			split = box.split(factor=0.3)
			split.prop(curMaskfile, "is_someint", text="?Someint?")
			col = split.column()
			col.prop(curMaskfile, "someint")

			col.enabled = curMaskfile.is_someint

class OBJECT_PT_b3d_textures_panel(bpy.types.Panel):
	bl_idname = "OBJECT_PT_b3d_textures_panel"
	bl_label = "Textures"
	bl_parent_id = "OBJECT_PT_b3d_res_module_panel"
	bl_space_type = "VIEW_3D"
	bl_region_type = getRegion()
	bl_category = "b3d Tools"

	@classmethod
	def poll(self,context):
		return context.object is not None

	def draw(self, context):
		layout = self.layout
		scene = context.scene
		mytool = scene.my_tool

		currentRes = int(mytool.selectedResModule)
		curResModule = mytool.resModules[currentRes]

		box = self.layout.box()

		rows = 2
		row = box.row()
		row.template_list("CUSTOM_UL_items", "textures_list", curResModule, "textures", scene, "textures_index", rows=rows)

		col = row.column(align=True)

		props = col.operator("custom.list_action_arrbname", icon='ADD', text="")
		props.action = 'ADD'
		props.bname = "resModules"
		props.bindex = currentRes
		props.pname = "textures"
		props.customindex = "textures_index"

		props = col.operator("custom.list_action_arrbname", icon='REMOVE', text="")
		props.action = 'REMOVE'
		props.bname = "resModules"
		props.bindex = currentRes
		props.pname = "textures"
		props.customindex = "textures_index"

		col.separator()

		props = col.operator("custom.list_action_arrbname", icon='TRIA_UP', text="")
		props.action = 'UP'
		props.bname = "resModules"
		props.bindex = currentRes
		props.pname = "textures"
		props.customindex = "textures_index"

		props = col.operator("custom.list_action_arrbname", icon='TRIA_DOWN', text="")
		props.action = 'DOWN'
		props.bname = "resModules"
		props.bindex = currentRes
		props.pname = "textures"
		props.customindex = "textures_index"

		#Texture edit
		box = self.layout.box()

		textureIndex = scene.textures_index
		if (len(curResModule.textures)):
			curTexture = curResModule.textures[textureIndex]

			box.prop(curTexture, "is_memfix", text="Memfix")
			box.prop(curTexture, "is_noload", text="Noload")
			box.prop(curTexture, "is_bumpcoord", text="Bympcoord")

			split = box.split(factor=0.3)
			split.prop(curTexture, "is_someint", text="?Someint?")
			col = split.column()
			col.prop(curTexture, "someint")

			col.enabled = curTexture.is_someint

class OBJECT_PT_b3d_materials_panel(bpy.types.Panel):
	bl_idname = "OBJECT_PT_b3d_materials_panel"
	bl_label = "Materials"
	bl_parent_id = "OBJECT_PT_b3d_res_module_panel"
	bl_space_type = "VIEW_3D"
	bl_region_type = getRegion()
	bl_category = "b3d Tools"

	@classmethod
	def poll(self,context):
		return context.object is not None

	def draw(self, context):
		layout = self.layout
		scene = context.scene
		mytool = scene.my_tool

		currentRes = int(mytool.selectedResModule)
		curResModule = mytool.resModules[currentRes]

		box = self.layout.box()

		rows = 2
		row = box.row()
		row.template_list("CUSTOM_UL_items", "materials_list", curResModule, "materials", scene, "materials_index", rows=rows)

		col = row.column(align=True)

		props = col.operator("custom.list_action_arrbname", icon='ADD', text="")
		props.action = 'ADD'
		props.bname = "resModules"
		props.bindex = currentRes
		props.pname = "materials"
		props.customindex = "materials_index"

		props = col.operator("custom.list_action_arrbname", icon='REMOVE', text="")
		props.action = 'REMOVE'
		props.bname = "resModules"
		props.bindex = currentRes
		props.pname = "materials"
		props.customindex = "materials_index"

		col.separator()

		props = col.operator("custom.list_action_arrbname", icon='TRIA_UP', text="")
		props.action = 'UP'
		props.bname = "resModules"
		props.bindex = currentRes
		props.pname = "materials"
		props.customindex = "materials_index"

		props = col.operator("custom.list_action_arrbname", icon='TRIA_DOWN', text="")
		props.action = 'DOWN'
		props.bname = "resModules"
		props.bindex = currentRes
		props.pname = "materials"
		props.customindex = "materials_index"

		#Material edit
		box = self.layout.box()

		textureIndex = scene.materials_index
		if (len(curResModule.materials)):
			curMaterial = curResModule.materials[textureIndex]

			split = box.split(factor=0.3)
			split.prop(curMaterial, "is_reflect", text="Reflect")
			col = split.column()
			col.prop(curMaterial, "reflect")
			col.enabled = curMaterial.is_reflect

			split = box.split(factor=0.3)
			split.prop(curMaterial, "is_specular", text="Specular")
			col = split.column()
			col.prop(curMaterial, "specular")
			col.enabled = curMaterial.is_specular

			split = box.split(factor=0.3)
			split.prop(curMaterial, "is_transp", text="Transparency")
			col = split.column()
			col.prop(curMaterial, "transp")
			col.enabled = curMaterial.is_transp

			split = box.split(factor=0.3)
			split.prop(curMaterial, "is_rot", text="Rotation")
			col = split.column()
			col.prop(curMaterial, "rot")
			col.enabled = curMaterial.is_rot

			split = box.split(factor=0.3)
			split.prop(curMaterial, "is_col", text="Color")
			col = split.column()
			col.prop(curMaterial, "col")
			col.enabled = curMaterial.is_col

			split = box.split(factor=0.3)
			split.prop(curMaterial, "is_tex", text="Texture TEX")
			col = split.column()
			col.prop(curMaterial, "tex")
			col.enabled = curMaterial.is_tex

			split = box.split(factor=0.3)
			split.prop(curMaterial, "is_ttx", text="Texture TTX")
			col = split.column()
			col.prop(curMaterial, "ttx")
			col.enabled = curMaterial.is_ttx

			split = box.split(factor=0.3)
			split.prop(curMaterial, "is_itx", text="Texture ITX")
			col = split.column()
			col.prop(curMaterial, "itx")
			col.enabled = curMaterial.is_itx

			split = box.split(factor=0.3)
			split.prop(curMaterial, "is_att", text="Att")
			col = split.column()
			col.prop(curMaterial, "att")
			col.enabled = curMaterial.is_att

			split = box.split(factor=0.3)
			split.prop(curMaterial, "is_msk", text="Maskfile")
			col = split.column()
			col.prop(curMaterial, "msk")
			col.enabled = curMaterial.is_msk

			split = box.split(factor=0.3)
			split.prop(curMaterial, "is_power", text="Power")
			col = split.column()
			col.prop(curMaterial, "power")
			col.enabled = curMaterial.is_power

			split = box.split(factor=0.3)
			split.prop(curMaterial, "is_coord", text="Coord")
			col = split.column()
			col.prop(curMaterial, "coord")
			col.enabled = curMaterial.is_coord

			split = box.split(factor=0.3)
			split.prop(curMaterial, "is_env", text="Env")
			col = split.column()
			col.prop(curMaterial, "envId")
			col.prop(curMaterial, "env")
			col.enabled = curMaterial.is_env

			split = box.split(factor=0.3)
			split.prop(curMaterial, "is_rotPoint", text="Rotation Center")
			col = split.column()
			col.prop(curMaterial, "rotPoint")
			col.enabled = curMaterial.is_rotPoint

			split = box.split(factor=0.3)
			split.prop(curMaterial, "is_move", text="Movement")
			col = split.column()
			col.prop(curMaterial, "move")
			col.enabled = curMaterial.is_move

			box.prop(curMaterial, "is_noz", text="No Z")
			box.prop(curMaterial, "is_nof", text="No F")
			box.prop(curMaterial, "is_notile", text="No tiling")
			box.prop(curMaterial, "is_notileu", text="No tiling U")
			box.prop(curMaterial, "is_notilev", text="No tiling V")
			box.prop(curMaterial, "is_alphamirr", text="Alphamirr")
			box.prop(curMaterial, "is_bumpcoord", text="Bympcoord")
			box.prop(curMaterial, "is_usecol", text="UseCol")
			box.prop(curMaterial, "is_wave", text="Wave")

class OBJECT_PT_b3d_misc_panel(bpy.types.Panel):
	bl_idname = "OBJECT_PT_b3d_misc_panel"
	bl_label = "About add-on"
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

		self.layout.label(text="Add-on author: aleko2144")
		self.layout.label(text="vk.com/rnr_mods")
# ------------------------------------------------------------------------
# register and unregister
# ------------------------------------------------------------------------

_classes = (
	PanelSettings,
	AddOperator,
	# getters
	GetValuesOperator,
	GetFaceValuesOperator,
	GetVertexValuesOperator,
	# setters
	SetValuesOperator,
	SetFaceValuesOperator,
	SetVertexValuesOperator,
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
	AddBlocksOperator,
	ShowHideSphereOperator,
	GetValuesModalOperator,

	OBJECT_PT_b3d_add_panel,
	OBJECT_PT_b3d_edit_panel,
	OBJECT_PT_b3d_pob_edit_panel,
	OBJECT_PT_b3d_pfb_edit_panel,
	OBJECT_PT_b3d_pvb_edit_panel,
	OBJECT_PT_b3d_res_module_panel,
	OBJECT_PT_b3d_maskfiles_panel,
	OBJECT_PT_b3d_textures_panel,
	OBJECT_PT_b3d_materials_panel,
	OBJECT_PT_b3d_blocks_panel,
	OBJECT_PT_b3d_func_panel,
	OBJECT_PT_b3d_misc_panel,
)

# @bpy.app.handlers.persistent
def load_handler(scene):
	print('invoking modal operator')
	bpy.ops.wm.get_block_values_modal_operator()

def register():
	for cls in _classes:
		bpy.utils.register_class(cls)
	bpy.types.Scene.my_tool = bpy.props.PointerProperty(type=PanelSettings)

	bpy.app.handlers.load_post.append(load_handler)

def unregister():
	del bpy.types.Scene.my_tool
	for cls in _classes[::-1]:
		bpy.utils.unregister_class(cls)

	if load_handler in bpy.app.handlers.load_post:
		bpy.app.handlers.load_post.remove(load_handler)
