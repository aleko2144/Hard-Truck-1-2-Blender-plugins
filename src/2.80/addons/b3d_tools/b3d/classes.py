
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
	fieldType,
	FloatBlock
)

from .class_descr import (
	b_1,
	b_2,
	# b_3,
	b_4,
	b_5,
	b_6,
	b_7,
	# b_8,
	b_9,
	b_10,
	b_11,
	b_12,
	b_13,
	b_14,
	b_15,
	b_16,
	b_17,
	b_18,
	b_20,
	b_21,
	b_22,
	b_23,
	b_24,
	b_25,
	b_26,
	b_27,
	b_28,
	b_29,
	b_30,
	b_31,
	b_33,
	b_34,
	b_35,
	b_36,
	b_37,
	b_39,
	b_40,
	pfb_8,
	pfb_28,
	pfb_35,
	pvb_8,
	pvb_35
)

from .common import (
	resMaterialsCallback,
	spacesCallback,
	referenceablesCallback,
	roomsCallback,
	modulesCallback,
	getMytoolBlockNameByClass
)


def setCustObjValue(subtype, bname, pname):
	def callback_func(self, context):

		mytool = context.scene.my_tool
		result = getattr(getattr(mytool, bname), '{}_enum'.format(pname))
		if subtype == fieldType.INT:
			result = int(result)
		elif subtype == fieldType.FLOAT:
			result = float(result)
		elif subtype == fieldType.FLOAT:
			result = str(result)

		setattr(
			bpy.context.object,
			'["{}"]'.format(pname),
			result
		)

	return callback_func

def createTypeClass(zclass, multipleEdit = True):
	attrs = [obj for obj in zclass.__dict__.keys() if not obj.startswith('__')]

	bname, bnum = getMytoolBlockNameByClass(zclass, multipleEdit)

	block_num = zclass.__name__.split('_')[1]
	attributes = {
		'__annotations__' : {

		}
	}
	for attr in attrs:
		obj = zclass.__dict__[attr]
		pname = obj['prop']
		prop = None

		if multipleEdit: # lock switches only for multiple edit
			lockProp = BoolProperty(
				name = "On./Off.",
				description = "Enable/Disable param for editing",
				default = True
			)

		if obj['type'] == fieldType.STRING \
		or obj['type'] == fieldType.COORD \
		or obj['type'] == fieldType.RAD \
		or obj['type'] == fieldType.FLOAT \
		or obj['type'] == fieldType.INT \
		or obj['type'] == fieldType.LIST:

			if multipleEdit: # lock switches only for multiple edit
				attributes['__annotations__']["show_"+pname] = lockProp

			if obj['type'] == fieldType.STRING and multipleEdit:
				prop = StringProperty(
					name = obj['name'],
					description = obj['description'],
					default = obj['default'],
					maxlen = 32
				)

			elif obj['type'] == fieldType.COORD and multipleEdit:
				prop = FloatVectorProperty(
					name = obj['name'],
					description = obj['description'],
					default = obj['default']
				)

			elif (obj['type'] == fieldType.RAD or obj['type'] == fieldType.FLOAT) and multipleEdit:
				prop = FloatProperty(
					name = obj['name'],
					description = obj['description'],
					default = obj['default']
				)

			elif obj['type'] == fieldType.INT and multipleEdit:
				prop = IntProperty(
					name = obj['name'],
					description = obj['description'],
					default = obj['default']
				)

			elif obj['type'] == fieldType.LIST:
				prop = CollectionProperty(
					name = obj['name'],
					description = obj['description'],
					type = FloatBlock
				)

			attributes['__annotations__'][pname] = prop

		elif obj['type'] == fieldType.ENUM \
		or obj['type'] == fieldType.ENUM_DYN:


			if multipleEdit: # lock switches only for multiple edit
				attributes['__annotations__']["show_"+pname] = lockProp

			enum_callback = None
			subtype = obj.get('subtype')

			if obj.get('callback') == fieldType.SPACE_NAME:
				enum_callback = spacesCallback
			elif obj.get('callback') == fieldType.REFERENCEABLE:
				enum_callback = referenceablesCallback
			elif obj.get('callback') == fieldType.MATERIAL_IND:
				enum_callback = resMaterialsCallback
			elif obj.get('callback') == fieldType.ROOM:
				enum_callback = roomsCallback(bname, '{}_res'.format(pname))
			elif obj.get('callback') == fieldType.RES_MODULE:
				enum_callback = modulesCallback

			if obj['type'] == fieldType.ENUM:
				prop = None
				prop_enum = None
				prop_switch = None

				prop_switch = BoolProperty(
					name = 'Use dropdown',
					description = 'Dropdown selection',
					default = False
				)

				prop_enum = EnumProperty(
					name = obj['name'],
					description = obj['description'],
					items = obj['items'],
					default = obj['default'],
					update = setCustObjValue(subtype, bname, pname)
				)

				if multipleEdit:
					prop = EnumProperty(
						name = obj['name'],
						description = obj['description'],
						default = obj['default'],
						items = obj['items']
					)

				attributes['__annotations__']['{}_switch'.format(pname)] = prop_switch
				attributes['__annotations__']['{}_enum'.format(pname)] = prop_enum

				if multipleEdit:
					attributes['__annotations__']['{}'.format(pname)] = prop

			elif obj['type'] == fieldType.ENUM_DYN:
				# prop = None
				prop_enum = None
				prop_switch = None

				prop_switch = BoolProperty(
					name = 'Use dropdown',
					description = 'Dropdown selection',
					default = False
				)

				prop_enum = EnumProperty(
					name = obj['name'],
					description = obj['description'],
					items = enum_callback,
					update = setCustObjValue(subtype, bname, pname)
				)


				if multipleEdit:
					if subtype == fieldType.STRING:
						prop = StringProperty(
							name = obj['name'],
							description = obj['description'],
							maxlen = 32
						)
					if subtype == fieldType.INT:
						prop = IntProperty(
							name = obj['name'],
							description = obj['description']
						)

				attributes['__annotations__']['{}_switch'.format(pname)] = prop_switch
				attributes['__annotations__']['{}_enum'.format(pname)] = prop_enum

				if multipleEdit:
					attributes['__annotations__']['{}'.format(pname)] = prop

		elif obj['type'] == fieldType.V_FORMAT: # currently only available in vertex edit

			attributes['__annotations__']["show_{}".format(pname)] = lockProp

			prop1 = BoolProperty(
				name = 'Triangulation offset',
				description = 'Order in which vertexes are read depends on that',
				default = True
			)
			attributes['__annotations__']['{}_{}'.format(pname, 'triang_offset')] = prop1

			prop2 = BoolProperty(
				name = 'Use UV',
				description = 'If active, writes UV during export.',
				default = True
			)
			attributes['__annotations__']['{}_{}'.format(pname, 'use_uvs')] = prop2

			prop3 = BoolProperty(
				name = 'Use normals',
				description = 'If active, writes normal during export.',
				default = True
			)
			attributes['__annotations__']['{}_{}'.format(pname, 'use_normals')] = prop3

			prop4 = BoolProperty(
				name = 'Normal switch',
				description = 'If active, use <float> for en(dis)abling normals. If not active use <float vector> for common normals. Is ignored if "Use normals" is inactive',
				default = True
			)
			attributes['__annotations__']['{}_{}'.format(pname, 'normal_flag')] = prop4

	if multipleEdit:
		newclass = type("{}_gen".format(zclass.__name__), (bpy.types.PropertyGroup,), attributes)
	else:
		newclass = type("s_{}_gen".format(zclass.__name__), (bpy.types.PropertyGroup,), attributes)
	return newclass


perFaceBlock_8 = createTypeClass(pfb_8)
perFaceBlock_28 = createTypeClass(pfb_28)
perFaceBlock_35 = createTypeClass(pfb_35)

perVertBlock_8 = createTypeClass(pvb_8)
perVertBlock_35 = createTypeClass(pvb_35)

s_block_1 = createTypeClass(b_1, False)
s_block_2 = createTypeClass(b_2, False)
# s_block_3 = createTypeClass(b_3, False)
s_block_4 = createTypeClass(b_4, False)
s_block_5 = createTypeClass(b_5, False)
s_block_6 = createTypeClass(b_6, False)
s_block_7 = createTypeClass(b_7, False)
# s_block_8 = createTypeClass(b_8, False)
s_block_9 = createTypeClass(b_9, False)
s_block_10 = createTypeClass(b_10, False)
s_block_11 = createTypeClass(b_11, False)
s_block_12 = createTypeClass(b_12, False)
s_block_13 = createTypeClass(b_13, False)
s_block_14 = createTypeClass(b_14, False)
s_block_15 = createTypeClass(b_15, False)
s_block_16 = createTypeClass(b_16, False)
s_block_17 = createTypeClass(b_17, False)
s_block_18 = createTypeClass(b_18, False)
s_block_20 = createTypeClass(b_20, False)
s_block_21 = createTypeClass(b_21, False)
s_block_22 = createTypeClass(b_22, False)
s_block_23 = createTypeClass(b_23, False)
s_block_24 = createTypeClass(b_24, False)
s_block_25 = createTypeClass(b_25, False)
s_block_26 = createTypeClass(b_26, False)
s_block_27 = createTypeClass(b_27, False)
s_block_28 = createTypeClass(b_28, False)
s_block_29 = createTypeClass(b_29, False)
s_block_30 = createTypeClass(b_30, False)
s_block_31 = createTypeClass(b_31, False)
s_block_33 = createTypeClass(b_33, False)
s_block_34 = createTypeClass(b_34, False)
s_block_35 = createTypeClass(b_35, False)
s_block_36 = createTypeClass(b_36, False)
s_block_37 = createTypeClass(b_37, False)
s_block_39 = createTypeClass(b_39, False)
s_block_40 = createTypeClass(b_40, False)

block_1 = createTypeClass(b_1)
block_2 = createTypeClass(b_2)
# block_3 = createTypeClass(b_3)
block_4 = createTypeClass(b_4)
block_5 = createTypeClass(b_5)
block_6 = createTypeClass(b_6)
block_7 = createTypeClass(b_7)
# block_8 = createTypeClass(b_8)
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
	s_block_1,
	s_block_2,
	# s_block_3,
	s_block_4,
	s_block_5,
	s_block_6,
	s_block_7,
	# s_block_8,
	s_block_9,
	s_block_10,
	s_block_11,
	s_block_12,
	s_block_13,
	s_block_14,
	s_block_15,
	s_block_16,
	s_block_17,
	s_block_18,
	s_block_20,
	s_block_21,
	s_block_22,
	s_block_23,
	s_block_24,
	s_block_25,
	s_block_26,
	s_block_27,
	s_block_28,
	s_block_29,
	s_block_30,
	s_block_31,
	s_block_33,
	s_block_34,
	s_block_35,
	s_block_36,
	s_block_37,
	s_block_39,
	s_block_40,

	block_1,
	block_2,
	# block_3,
	block_4,
	block_5,
	block_6,
	block_7,
	# block_8,
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