import struct
import sys
import timeit
import threading
import pdb
import time

import bmesh
import bpy
import mathutils
import os.path
from bpy.props import *
from mathutils import Matrix
from math import radians

from math import cos
from math import sin

import bpy_extras.mesh_utils


from .classes import (
	b_1,
	b_2,
	b_3,
	b_4,
	b_5,
	b_6,
	b_7,
	b_8,
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

from .scripts import (
    prop
)

from ..common import (
	log
)

from .common import (
	isRootObj,
	isEmptyName
)

from bpy_extras.io_utils import (
		ImportHelper,
		ExportHelper,
		#orientation_helper_factory,
		path_reference_mode,
		axis_conversion,
		)

from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       EnumProperty,
                       PointerProperty,
                       )
from bpy.types import (Panel,
                       Operator,
                       AddonPreferences,
                       PropertyGroup,
                       )

from bpy_extras.image_utils import load_image
from mathutils import Vector
from bpy import context

RoMesh = True

def openclose(file):
	oc = file.read(4)
	if (oc == (b'\x4D\x01\x00\x00')): #Begin Chunk
		return 2
	elif oc == (b'\x2B\x02\x00\x00'): #End Chunk
		# print('}')
		return 0
	elif oc == (b'\xbc\x01\x00\x00'): #Group Chunk
		#print('BC01')
		return 3
	elif oc == (b'\xde\x00\00\00'): #End Chunks
		print ('EOF')
		return 1
	else:
		print(str(file.tell()))
		print (str(oc))
		print('brackets error')
		sys.exit()

def uv_from_vert_first(uv_layer, v):
    for l in v.link_loops:
        uv_data = l[uv_layer]
        return uv_data.uv
    return None

def uv_from_vert_average(uv_layer, v):
    uv_average = Vector((0.0, 0.0))
    total = 0.0
    for loop in v.link_loops:
        uv_average += loop[uv_layer].uv
        total += 1.0

    if total != 0.0:
        return uv_average * (1.0 / total)
    else:
        return None

def write(file, context, op, filepath, generate_pro_file, textures_path):

	global myFile_pro
	myFile_pro = filepath
	if generate_pro_file == True:
		export_pro(myFile_pro, textures_path)

	global myFile
	myFile = filepath
	export(myFile, generate_pro_file)

def MsgBox(label = "", title = "Error", icon = 'ERROR'):

    def draw(self, context):
        self.layout.label(label)

    bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)

def export_pro(file, textures_path):
	file = open(myFile_pro+'.pro','w')

	#file.write('TEXTUREFILES ' + str(len(bpy.data.materials)) + '\n')

	#imgs = []
	#for img in bpy.data.images:
	#	imgs.append(img.name)

	#for material in bpy.data.materials:
	#	file.write('txr\\' + material.active_texture.name + '.txr' + '\n')

	#file.write('\n')

	file.write('MATERIALS ' + str(len(bpy.data.materials)) + '\n')

	materials = []
	num_tex = 0

	for material in bpy.data.materials:
		materials.append(material.name)

	for i in range(len(materials)):
		num_tex = i#imgs.index[i]
		#print(str(imgs[i]))
		file.write(materials[i] + ' tex ' + str(num_tex + 1) + '\n')

	file.write('TEXTUREFILES ' + str(len(bpy.data.materials)) + '\n')

	imgs = []
	for img in bpy.data.images:
		imgs.append(img.name)

	for material in bpy.data.materials:
		try:
			file.write(textures_path + material.texture_slots[0].texture.image.name[:-3] + 'txr' + '\n')
		except:
			file.write(textures_path + "error" + '.txr' + '\n')

	file.write('\n')

def writeName(name, file):
	objName = ''
	if not isEmptyName(name):
		objName = name
	nameLen = len(objName)
	if nameLen <= 32:
		file.write(objName.encode("cp1251"))
	file.write(bytearray(b'\00'*(32-nameLen)))
	return

def clone_node():
	b3d_node = bpy.data.objects['b3d']
	bpy.context.scene.objects.active = b3d_node
	bpy.ops.object.select_grouped(type='CHILDREN_RECURSIVE')
	b3d_node.select = True
	bpy.ops.object.duplicate(linked=False, mode='TRANSLATION')
	bpy.context.scene.objects.active.name = "b3d_temporary"

def delete_clone():
	b3d_node = bpy.data.objects['b3d_temporary']
	bpy.context.scene.objects.active = b3d_node
	bpy.ops.object.select_grouped(type='CHILDREN_RECURSIVE')
	b3d_node.select = True
	bpy.ops.object.delete()


def export(file, generate_pro_file):
	file = open(myFile,'wb')

	global global_matrix
	global_matrix = axis_conversion(to_forward="-Z",
										to_up="Y",
										).to_4x4() * Matrix.Scale(1, 4)

	global generatePro
	generatePro = generate_pro_file

	global verNums
	verNums = []

	#ba = bytearray(b'\x00' * 20)

	#file.write(ba)

	materials = []

	for material in bpy.data.materials:
		materials.append(material.name)

	#Header

	file.write(b'b3d\x00')#struct.pack("4c",b'B',b'3',b'D',b'\x00'))
	# file.write(struct.pack('<i',0)) #File Size
	# file.write(struct.pack('<i',6)) #Mat list offset
	# file.write(struct.pack('<i',len(materials)*8 + 1)) #Mat list Data Size
	# file.write(struct.pack('<i',len(materials)* 8 + 1 + 6)) #Data Chunks Offset
	# file.write(struct.pack('<i',0)) #Data Chunks Size
	# file.write(struct.pack('<i', 0)) #Materials Count


	file.write(struct.pack('<i',0)) #File Size
	file.write(struct.pack('<i',0)) #Mat list offset
	file.write(struct.pack('<i',0)) #Mat list Data Size
	file.write(struct.pack('<i',0)) #Data Chunks Offset
	file.write(struct.pack('<i',0)) #Data Chunks Size
	file.write(struct.pack('<i',0)) #Materials Count


	#todo: add material list
	# for i in range(len(materials)):
	# 	file.write(str.encode(materials[i]))#+ bytearray(b'\x00' * (32-len(img))))
	# 	imgNone = 32-len(materials[i])
	# 	ba = bytearray(b'\x00'* imgNone)
	# 	file.write(ba)

	file.write(struct.pack("<i",111)) # Begin_Chunks

	objs = [cn for cn in bpy.data.objects if isRootObj(cn)]
	curRoot = objs[0]

	rChild = curRoot.children


	curMaxCnt = 0
	curLevel = 0

	# prevLevel = 0
	for obj in rChild[:-1]:
		if obj['block_type'] == 10 or obj['block_type'] == 9:
			curMaxCnt = 2
		elif obj['block_type'] == 21:
			curMaxCnt = obj[prop(b_21.GroupCnt)]
		exportBlock(obj, True, curLevel, curMaxCnt, [0], None, file)
		file.write(struct.pack("<i", 444))

	obj = rChild[-1]

	if obj['block_type'] == 10 or obj['block_type'] == 9:
		curMaxCnt = 2
	elif obj['block_type'] == 21:
		curMaxCnt = obj[prop(b_21.GroupCnt)]
	exportBlock(obj, True, curLevel, curMaxCnt, [0], None, file)

	# clone_node()
	# forChild(bpy.data.objects['b3d_temporary'],True, file)
	# delete_clone()
	file.write(struct.pack("<i",222))#EOF

def export08(object, verticesL, file, faces, uvs):
	file.write(struct.pack("<i",333))
	file.write(bytearray(b'\x00'*32))

	file.write(struct.pack("<i",int(8)))

	file.write(struct.pack("<f",object.location.x))
	file.write(struct.pack("<f",object.location.y))
	file.write(struct.pack("<f",object.location.z))
	file.write(struct.pack("<f",0))

	#file.write(struct.pack("<i",object['MType']))
	#file.write(struct.pack("<i",object['texNum']))

	fLen = len(object.data.loops)//3
	file.write(struct.pack("<i",fLen))
	#file.write(struct.pack("<i", object['FType']))

	for i in range(fLen):

		if (object['FType']==0 or object['FType']==1):
			file.write(struct.pack("<i", object['FType']))
			file.write(struct.pack("<f",1.0))
			file.write(struct.pack("<i",32767))
			if generatePro == True:
				material_name = object.data.materials[0].name
				texNum = bpy.data.materials.find(material_name)
				file.write(struct.pack("<i",texNum))
			else:
				file.write(struct.pack("<i",object['texNum']))
			file.write(struct.pack("<i",3))
			file.write(struct.pack("<3i",faces[i*3],faces[i*3+1],faces[i*3+2]))
			verticesL

		if (object['FType']==2):
			file.write(struct.pack("<i", object['FType']))
			file.write(struct.pack("<f",1.0))
			file.write(struct.pack("<i",32767))
			if generatePro == True:
				material_name = object.data.materials[0].name
				texNum = bpy.data.materials.find(material_name)
				file.write(struct.pack("<i",texNum))
			else:
				file.write(struct.pack("<i",object['texNum']))
			file.write(struct.pack("<i",3))
			file.write(struct.pack("<i2f",faces[i*3],uvs[i*3].x, 1-uvs[i*3].y))
			file.write(struct.pack("<i2f",faces[i*3+1],uvs[i*3+1].x, 1-uvs[i*3+1].y))
			file.write(struct.pack("<i2f",faces[i*3+2],uvs[i*3+2].x, 1-uvs[i*3+2].y))

			#file.write(struct.pack("<i",3))
			#file.write(struct.pack("<i2f",faces[i*3],uvs[i*3].x, 1-uvs[i*3].y))
			#file.write(struct.pack("<i2f",faces[i*3+1],uvs[i*3+1].x, 1-uvs[i*3+2].y))
			#file.write(struct.pack("<i2f",faces[i*3+2],uvs[i*3+2].x, 1-uvs[i*3+2].y))

			verticesL

		if (object['FType']==144 or object['FType']==128):
			file.write(struct.pack("<i", object['FType']))
			file.write(struct.pack("<f",1.0))
			file.write(struct.pack("<i",32767))
			if generatePro == True:
				material_name = object.data.materials[0].name
				texNum = bpy.data.materials.find(material_name)
				file.write(struct.pack("<i",texNum))
			else:
				file.write(struct.pack("<i",object['texNum']))
			file.write(struct.pack("<i",3))
			file.write(struct.pack("<3i",faces[i*3],faces[i*3+1],faces[i*3+2]))
			verticesL

	file.write(struct.pack("<i",555))

def export35(object, verticesL, file, faces, uvs):
	file.write(struct.pack("<i",333))
	file.write(bytearray(b'\x00'*32))


	file.write(struct.pack("<i",int(35)))

	file.write(bytearray(b'\x00'*16))
	file.write(struct.pack("<i",object['MType']))
	if generatePro == True:
		material_name = object.data.materials[0].name
		texNum = bpy.data.materials.find(material_name)
		file.write(struct.pack("<i",texNum))
	else:
		file.write(struct.pack("<i",object['texNum']))

	fLen = len(object.data.loops)//3
	file.write(struct.pack("<i",fLen))

	for i in range(fLen):

		if (object['MType']==3):
			file.write(struct.pack("<i",16))#16
			file.write(struct.pack("<f",1.0))#1.0
			file.write(struct.pack("<i",32767))#32767
			if generatePro == True:
				material_name = object.data.materials[0].name
				texNum = bpy.data.materials.find(material_name)
				file.write(struct.pack("<i",texNum))
			else:
				file.write(struct.pack("<i",object['texNum']))
			file.write(struct.pack("<i",3))#VerNum
			file.write(struct.pack("<3i",faces[i*3],faces[i*3+1],faces[i*3+2]))
			#file.write(struct.pack("<iffiffiff",faces[i*3],verticesL[faces[i*3]][2][0],1-verticesL[faces[i*3]][2][1],faces[i*3+1],verticesL[faces[i*3+1]][2][0],1-verticesL[faces[i*3+1]][2][1],faces[i*3+2],verticesL[faces[i*3+2]][2][0],1-verticesL[faces[i*3+2]][2][1]))
			verticesL

		elif (object['MType']==1):
			file.write(struct.pack("<i",50))
			file.write(struct.pack("<f",0.1))
			file.write(struct.pack("<i",32767))
			if generatePro == True:
				material_name = object.data.materials[0].name
				texNum = bpy.data.materials.find(material_name)
				file.write(struct.pack("<i",texNum))
			else:
				file.write(struct.pack("<i",object['texNum']))
			file.write(struct.pack("<i",3))#VerNum

			file.write(struct.pack("<i5f",faces[i*3],uvs[i*3].x, 1-uvs[i*3].y, -verticesL[faces[i*3]][1][0], verticesL[faces[i*3]][1][1], verticesL[faces[i*3]][1][2]))
			file.write(struct.pack("<i5f",faces[i*3+1],uvs[i*3+1].x, 1-uvs[i*3+1].y, -verticesL[faces[i*3+1]][1][0], verticesL[faces[i*3+1]][1][1], verticesL[faces[i*3+1]][1][2]))
			file.write(struct.pack("<i5f",faces[i*3+2],uvs[i*3+2].x, 1-uvs[i*3+2].y, -verticesL[faces[i*3+2]][1][0], verticesL[faces[i*3+2]][1][1], verticesL[faces[i*3+2]][1][2]))

			#file.write(struct.pack("<iffiffiff",faces[i*3],uvs[i*3].x,uvs[i*3].y,faces[i*3+1],uvs[i*3+1].x,uvs[i*3+1].y,faces[i*3+2],uvs[i*3+2].x,uvs[i*3+2].y))

	file.write(struct.pack("<i",555)) #End Block

blocksWithChildren = [2,3,4,5,6,7,9]

def exportBlock(obj, isLast, curLevel, maxGroups, curGroups, extra, file):


	toProcessChild = False
	curMaxCnt = 0

	block = obj

	objName = block.name
	objType = block.get('block_type')

	l_extra = None
	passToMesh = []

	if objType != None:

		log.debug("{}_{}_{}".format(curLevel, block['level_group'], block.name))

		if len(curGroups) <= curLevel:
			curGroups.append(0)

		#write Group Chunk
		if block['level_group'] > curGroups[curLevel]:
			log.debug('group ended')
			file.write(struct.pack("<i",444))#Group Chunk
			curGroups[curLevel] = block['level_group']

		file.write(struct.pack("<i",333))#Begin Chunk

		blChildren = list(block.children)

		blChildren.sort(key=lambda cn: cn['level_group'])
		# blChildren.sort(key=lambda cn: cn.name, reverse=True)

		writeName(objName, file)
		file.write(struct.pack("<i", objType))

		if objType == 0:
			file.write(bytearray(b'\x00'*44))

		elif objType == 1:

			writeName(block[prop(b_1.Name1)], file)
			writeName(block[prop(b_1.Name2)], file)

		elif objType == 2:

			file.write(struct.pack("<3f", *block[prop(b_2.XYZ)]))
			file.write(struct.pack("<f", block[prop(b_2.R)]))
			file.write(struct.pack("<3f", *block[prop(b_2.Unk_XYZ)]))
			file.write(struct.pack("<f", block[prop(b_2.Unk_R)]))

			file.write(struct.pack("<i", len(block.children)))

			toProcessChild = True

		elif objType == 3:

			file.write(struct.pack("<3f", *block[prop(b_3.XYZ)]))
			file.write(struct.pack("<f", block[prop(b_3.R)]))

			file.write(struct.pack("<i", len(block.children)))

			toProcessChild = True

		elif objType == 4:

			file.write(struct.pack("<3f", *block[prop(b_4.XYZ)]))
			file.write(struct.pack("<f", block[prop(b_4.R)]))
			writeName(block[prop(b_4.Name1)], file)
			writeName(block[prop(b_4.Name2)], file)

			file.write(struct.pack("<i", len(block.children)))

			toProcessChild = True

		elif objType == 5:

			file.write(struct.pack("<3f", *block[prop(b_5.XYZ)]))
			file.write(struct.pack("<f", block[prop(b_5.R)]))
			writeName(block[prop(b_5.Name1)], file)

			file.write(struct.pack("<i", len(block.children)))

			toProcessChild = True

		elif objType == 6:

			file.write(struct.pack("<3f", *block[prop(b_6.XYZ)]))
			file.write(struct.pack("<f", block[prop(b_6.R)]))
			writeName(block[prop(b_6.Name1)], file)
			writeName(block[prop(b_6.Name2)], file)
			file.write(struct.pack("<i", 0)) # VertexCount

			file.write(struct.pack("<i", len(block.children)))

			toProcessChild = True

		elif objType == 7:

			file.write(struct.pack("<3f", *block[prop(b_7.XYZ)]))
			file.write(struct.pack("<f", block[prop(b_7.R)]))
			writeName(block[prop(b_7.Name1)], file)
			file.write(struct.pack("<i", 0)) # VertexCount

			file.write(struct.pack("<i", len(block.children)))

			toProcessChild = True

		elif objType == 8:

			file.write(struct.pack("<3f", *block[prop(b_8.XYZ)]))
			file.write(struct.pack("<f", block[prop(b_8.R)]))
			file.write(struct.pack("<i", 0)) # PolygonCount

		elif objType == 9 or objType == 22:

			file.write(struct.pack("<3f", *block[prop(b_9.XYZ)]))
			file.write(struct.pack("<f", block[prop(b_9.R)]))
			file.write(struct.pack("<3f", *block[prop(b_9.Unk_XYZ)]))
			file.write(struct.pack("<f", block[prop(b_9.Unk_R)]))

			file.write(struct.pack("<i", len(block.children)))

			toProcessChild = True
			curMaxCnt = 2
			maxGroups = 2

		elif objType == 10:

			file.write(struct.pack("<3f", *block[prop(b_10.XYZ)]))
			file.write(struct.pack("<f", block[prop(b_10.R)]))
			file.write(struct.pack("<3f", *block[prop(b_10.LOD_XYZ)]))
			file.write(struct.pack("<f", block[prop(b_10.LOD_R)]))

			file.write(struct.pack("<i", len(block.children)))

			blChildren.sort(key=lambda cn: cn['level_group'])
			log.debug(["{}_{}".format(cn['level_group'], cn.name) for cn in blChildren])

			toProcessChild = True
			curMaxCnt = 2

		elif objType == 11:

			file.write(struct.pack("<3f", *block[prop(b_11.XYZ)]))
			file.write(struct.pack("<f", block[prop(b_11.R)]))
			file.write(struct.pack("<3f", *block[prop(b_11.Unk_XYZ)]))
			file.write(struct.pack("<f", block[prop(b_11.Unk_R)]))

			file.write(struct.pack("<i", len(block.children)))

			toProcessChild = True

		elif objType == 12:

			file.write(struct.pack("<3f", *block[prop(b_12.XYZ)]))
			file.write(struct.pack("<f", block[prop(b_12.R)]))
			file.write(struct.pack("<3f", *block[prop(b_12.Unk_XYZ)]))
			file.write(struct.pack("<f", block[prop(b_12.Unk_R)]))
			file.write(struct.pack("<i", block[prop(b_12.Unk_Int1)]))
			file.write(struct.pack("<i", block[prop(b_12.Unk_Int2)]))
			file.write(struct.pack("<i", 0)) #Params Count

		elif objType == 13:

			file.write(struct.pack("<3f", *block[prop(b_13.XYZ)]))
			file.write(struct.pack("<f", block[prop(b_13.R)]))
			file.write(struct.pack("<i", block[prop(b_13.Unk_Int1)]))
			file.write(struct.pack("<i", block[prop(b_13.Unk_Int2)]))
			file.write(struct.pack("<i", 0)) #Params Count

		elif objType == 14:

			file.write(struct.pack("<3f", *block[prop(b_14.XYZ)]))
			file.write(struct.pack("<f", block[prop(b_14.R)]))
			file.write(struct.pack("<3f", *block[prop(b_14.Unk_XYZ)]))
			file.write(struct.pack("<f", block[prop(b_14.Unk_R)]))
			file.write(struct.pack("<i", block[prop(b_14.Unk_Int1)]))
			file.write(struct.pack("<i", block[prop(b_14.Unk_Int2)]))
			file.write(struct.pack("<i", 0)) #Params Count

		elif objType == 15:

			file.write(struct.pack("<3f", *block[prop(b_15.XYZ)]))
			file.write(struct.pack("<f", block[prop(b_15.R)]))
			file.write(struct.pack("<i", block[prop(b_15.Unk_Int1)]))
			file.write(struct.pack("<i", block[prop(b_15.Unk_Int2)]))
			file.write(struct.pack("<i", 0)) #Params Count

		elif objType == 16:

			file.write(struct.pack("<3f", *block[prop(b_16.XYZ)]))
			file.write(struct.pack("<f", block[prop(b_16.R)]))
			file.write(struct.pack("<3f", *block[prop(b_16.Unk_XYZ1)]))
			file.write(struct.pack("<3f", *block[prop(b_16.Unk_XYZ2)]))
			file.write(struct.pack("<f", block[prop(b_16.Unk_Float1)]))
			file.write(struct.pack("<f", block[prop(b_16.Unk_Float2)]))
			file.write(struct.pack("<i", block[prop(b_16.Unk_Int1)]))
			file.write(struct.pack("<i", block[prop(b_16.Unk_Int2)]))
			file.write(struct.pack("<i", 0)) #Params Count

		elif objType == 17:

			file.write(struct.pack("<3f", *block[prop(b_17.XYZ)]))
			file.write(struct.pack("<f", block[prop(b_17.R)]))
			file.write(struct.pack("<3f", *block[prop(b_17.Unk_XYZ1)]))
			file.write(struct.pack("<3f", *block[prop(b_17.Unk_XYZ2)]))
			file.write(struct.pack("<f", block[prop(b_17.Unk_Float1)]))
			file.write(struct.pack("<f", block[prop(b_17.Unk_Float2)]))
			file.write(struct.pack("<i", block[prop(b_17.Unk_Int1)]))
			file.write(struct.pack("<i", block[prop(b_17.Unk_Int2)]))
			file.write(struct.pack("<i", 0)) #Params Count

		elif objType == 18:

			file.write(struct.pack("<3f", *block[prop(b_18.XYZ)]))
			file.write(struct.pack("<f", block[prop(b_18.R)]))

			writeName(block[prop(b_18.Add_Name)], file)
			writeName(block[prop(b_18.Space_Name)], file)

		elif objType == 19:

			file.write(struct.pack("<i", len(block.children)))

			toProcessChild = True

		elif objType == 20:

			file.write(struct.pack("<3f", *block[prop(b_20.XYZ)]))
			file.write(struct.pack("<f", block[prop(b_20.R)]))
			file.write(struct.pack("<i", 0)) #Verts Count
			file.write(struct.pack("<i", block[prop(b_20.Unk_Int1)]))
			file.write(struct.pack("<i", block[prop(b_20.Unk_Int2)]))
			file.write(struct.pack("<i", 0)) #Unknowns Count

		elif objType == 21:

			file.write(struct.pack("<3f", *block[prop(b_21.XYZ)]))
			file.write(struct.pack("<f", block[prop(b_21.R)]))
			file.write(struct.pack("<i", block[prop(b_21.GroupCnt)]))
			file.write(struct.pack("<i", block[prop(b_21.Unk_Int2)]))

			file.write(struct.pack("<i", len(block.children)))

			toProcessChild = True
			curMaxCnt = block[prop(b_21.GroupCnt)]

		elif objType == 23:

			file.write(struct.pack("<i", block[prop(b_23.Unk_Int1)]))
			file.write(struct.pack("<i", block[prop(b_23.Surface)]))
			file.write(struct.pack("<i", 0)) #Unknowns Count
			file.write(struct.pack("<i", 0)) #Verts Count

		elif objType == 24:
			PI = 3.14159265358979

			cos_y = cos(-block.rotation_euler[1])
			sin_y = sin(-block.rotation_euler[1])
			cos_z = cos(-block.rotation_euler[2])
			sin_z = sin(-block.rotation_euler[2])
			cos_x = cos(-block.rotation_euler[0])
			sin_x = sin(-block.rotation_euler[0])

			file.write(struct.pack("<f", (cos_y * cos_z)*block.scale[0]))
			file.write(struct.pack("<f", (sin_y * sin_x - cos_y * sin_z * cos_x)*block.scale[1]))
			file.write(struct.pack("<f", (cos_y * sin_z * sin_x + sin_y * cos_x)*block.scale[2]))

			file.write(struct.pack("<f", (sin_z)*block.scale[0]))
			file.write(struct.pack("<f", (cos_z * cos_x)*block.scale[1]))
			file.write(struct.pack("<f", (-cos_z * sin_x)*block.scale[2]))

			file.write(struct.pack("<f", (-sin_y * cos_z)*block.scale[0]))
			file.write(struct.pack("<f", (sin_y * sin_z * cos_x + cos_y * sin_x)*block.scale[1]))
			file.write(struct.pack("<f", (-sin_y * sin_z * sin_x + cos_y * cos_x)*block.scale[2]))


			file.write(struct.pack("<f",block.location.x))
			file.write(struct.pack("<f",block.location.y))
			file.write(struct.pack("<f",block.location.z))

			file.write(struct.pack("<i",block[prop(b_24.Flag)]))

			file.write(struct.pack("<i", len(block.children)))

			toProcessChild = True

		elif objType == 25:

			file.write(struct.pack("<3i", *block[prop(b_25.XYZ)]))
			writeName(block[prop(b_25.Name)], file)
			file.write(struct.pack("<3f", *block[prop(b_25.Unk_XYZ1)]))
			file.write(struct.pack("<3f", *block[prop(b_25.Unk_XYZ2)]))
			file.write(struct.pack("<f", block[prop(b_25.Unk_Float1)]))
			file.write(struct.pack("<f", block[prop(b_25.Unk_Float2)]))
			file.write(struct.pack("<f", block[prop(b_25.Unk_Float3)]))
			file.write(struct.pack("<f", block[prop(b_25.Unk_Float4)]))
			file.write(struct.pack("<f", block[prop(b_25.Unk_Float5)]))

		elif objType == 26:

			file.write(struct.pack("<3f", *block[prop(b_26.XYZ)]))
			file.write(struct.pack("<f", block[prop(b_26.R)]))
			file.write(struct.pack("<3f", *block[prop(b_26.Unk_XYZ1)]))
			file.write(struct.pack("<3f", *block[prop(b_26.Unk_XYZ2)]))
			file.write(struct.pack("<3f", *block[prop(b_26.Unk_XYZ3)]))
			file.write(struct.pack("<i", len(block.children)))

			toProcessChild = True

		elif objType == 27:

			file.write(struct.pack("<3f", *block[prop(b_27.XYZ)]))
			file.write(struct.pack("<f", block[prop(b_27.R)]))
			file.write(struct.pack("<i",block[prop(b_27.Flag)]))
			file.write(struct.pack("<3f", *block[prop(b_27.Unk_XYZ)]))
			file.write(struct.pack("<i",block[prop(b_27.Material)]))

		elif objType == 28:

			file.write(struct.pack("<3f", *block[prop(b_28.XYZ)]))
			file.write(struct.pack("<f", block[prop(b_28.R)]))
			file.write(struct.pack("<3f", *block[prop(b_28.Unk_XYZ)]))
			file.write(struct.pack("<3f", 0)) #Vertex Count

		elif objType == 29:

			file.write(struct.pack("<3f", *block[prop(b_29.XYZ)]))
			file.write(struct.pack("<f", block[prop(b_29.R)]))
			file.write(struct.pack("<i",block[prop(b_29.Unk_Int1)]))
			file.write(struct.pack("<i",block[prop(b_29.Unk_Int2)]))
			file.write(struct.pack("<3f", *block[prop(b_29.Unk_XYZ)]))
			file.write(struct.pack("<f", block[prop(b_29.Unk_R)]))

			file.write(struct.pack("<i", len(block.children)))

			toProcessChild = True

		elif objType == 30:

			file.write(struct.pack("<3f", *block[prop(b_30.XYZ)]))
			file.write(struct.pack("<f", block[prop(b_30.R)]))
			writeName(block[prop(b_30.Name)], file)
			file.write(struct.pack("<3f", *block[prop(b_30.XYZ1)]))
			file.write(struct.pack("<3f", *block[prop(b_30.XYZ2)]))

		elif objType == 31:

			file.write(struct.pack("<3f", *block[prop(b_31.XYZ)]))
			file.write(struct.pack("<f", block[prop(b_31.R)]))
			file.write(struct.pack("<i",block[prop(b_31.Unk_Int1)]))
			file.write(struct.pack("<3f", *block[prop(b_31.Unk_XYZ1)]))
			file.write(struct.pack("<f", block[prop(b_31.Unk_R)]))
			file.write(struct.pack("<i",block[prop(b_31.Unk_Int2)]))
			file.write(struct.pack("<3f", *block[prop(b_31.Unk_XYZ2)]))

		elif objType == 33:

			file.write(struct.pack("<3f", *block[prop(b_33.XYZ)]))
			file.write(struct.pack("<f", block[prop(b_33.R)]))
			file.write(struct.pack("<i",block[prop(b_33.Use_Lights)]))
			file.write(struct.pack("<i",block[prop(b_33.Light_Type)]))
			file.write(struct.pack("<i",block[prop(b_33.Flag)]))
			file.write(struct.pack("<3f", *block[prop(b_33.Unk_XYZ1)]))
			file.write(struct.pack("<3f", *block[prop(b_33.Unk_XYZ2)]))
			file.write(struct.pack("<f",block[prop(b_33.Unk_Float1)]))
			file.write(struct.pack("<f",block[prop(b_33.Unk_Float2)]))
			file.write(struct.pack("<f",block[prop(b_33.Light_R)]))
			file.write(struct.pack("<f",block[prop(b_33.Intens)]))
			file.write(struct.pack("<f",block[prop(b_33.Unk_Float3)]))
			file.write(struct.pack("<f",block[prop(b_33.Unk_Float4)]))
			file.write(struct.pack("<3f", *block[prop(b_33.RGB)]))

			file.write(struct.pack("<i", len(block.children)))

			toProcessChild = True

		elif objType == 34:

			file.write(struct.pack("<3f", *block[prop(b_34.XYZ)]))
			file.write(struct.pack("<f", block[prop(b_34.R)]))
			file.write(struct.pack("<i", 0)) #skipped Int
			file.write(struct.pack("<i", 0)) #Verts count

		elif objType == 35:

			file.write(struct.pack("<3f", *block[prop(b_35.XYZ)]))
			file.write(struct.pack("<f", block[prop(b_35.R)]))
			file.write(struct.pack("<i",block[prop(b_35.MType)]))
			file.write(struct.pack("<i",block[prop(b_35.TexNum)]))



			file.write(struct.pack("<i", 0)) #Polygon count

		elif objType == 36:

			file.write(struct.pack("<3f", *block[prop(b_36.XYZ)]))
			file.write(struct.pack("<f", block[prop(b_36.R)]))
			writeName(block[prop(b_36.Name1)], file)
			writeName(block[prop(b_36.Name2)], file)
			file.write(struct.pack("<i", block[prop(b_36.MType)]))
			file.write(struct.pack("<i", 0)) #Vertex count

			file.write(struct.pack("<i", len(block.children)))

			toProcessChild = True

		elif objType == 37:

			file.write(struct.pack("<3f", *block[prop(b_37.XYZ)]))
			file.write(struct.pack("<f", block[prop(b_37.R)]))
			writeName(block[prop(b_37.Name1)], file)
			# file.write(struct.pack("<i", block[prop(b_37.SType)]))
			file.write(struct.pack("<i", 1))

			offset = 0
			for ch in block.children:
				obj = bpy.data.objects[ch.name]
				someProps = getMeshProps(obj)
				passToMesh.append({
					"offset": offset,
					"props": someProps
				})
				offset += len(someProps[0])

			file.write(struct.pack("<i", offset)) #Vertex count

			for mesh in passToMesh:
				verts, uvs, normals = mesh['props']
				for i, v in enumerate(verts):
					file.write(struct.pack("<3f", *v))
					file.write(struct.pack("<2f", *uvs[i]))
					file.write(struct.pack("<3f", *normals[i]))


			file.write(struct.pack("<i", len(block.children)))

			toProcessChild = True

		elif objType == 39:

			file.write(struct.pack("<3f", *block[prop(b_39.XYZ)]))
			file.write(struct.pack("<f", block[prop(b_39.R)]))
			file.write(struct.pack("<i", block[prop(b_39.Color_R)]))
			file.write(struct.pack("<f", block[prop(b_39.Unk_Float1)]))
			file.write(struct.pack("<f", block[prop(b_39.Fog_Start)]))
			file.write(struct.pack("<f", block[prop(b_39.Fog_End)]))
			file.write(struct.pack("<i", block[prop(b_39.Color_Id)]))
			file.write(struct.pack("<i", 0)) #Unknown count

			file.write(struct.pack("<i", len(block.children)))

			toProcessChild = True

		elif objType == 40:

			file.write(struct.pack("<3f", *block[prop(b_40.XYZ)]))
			file.write(struct.pack("<f", block[prop(b_40.R)]))
			writeName(block[prop(b_40.Name1)], file)
			writeName(block[prop(b_40.Name2)], file)
			file.write(struct.pack("<i", block[prop(b_40.Unk_Int1)]))
			file.write(struct.pack("<i", block[prop(b_40.Unk_Int2)]))
			file.write(struct.pack("<i", 0))

		if toProcessChild:
			if(len(block.children) > 0):
				for i, ch in enumerate(blChildren[:-1]):

					if len(passToMesh):
						l_extra = passToMesh[i]
					exportBlock(ch, False, curLevel+1, curMaxCnt, curGroups, l_extra, file)

				if len(passToMesh):
					l_extra = passToMesh[-1]
				exportBlock(blChildren[-1], True, curLevel+1, curMaxCnt, curGroups, l_extra, file)


		log.debug("{}_{}".format(curGroups, block.name))

		if isLast:
			log.info("{}_{}".format(maxGroups, curGroups[curLevel]))
			for i in range(maxGroups-1 - curGroups[curLevel]):
				log.debug('not enough in group')
				file.write(struct.pack("<i",444))#Group Chunk
			curGroups[curLevel] = 0

		file.write(struct.pack("<i",555))#End Chunk


	return curLevel

def getMeshProps(obj):

	mesh = obj.mesh

	vertexes = [cn.co for cn in mesh.vertices]

	uvs = [None] * len(vertexes)
	for poly in mesh.polygons:
		for li in poly.loop_indices:
			vi = mesh.loops[li].vertex_index
			uvs[vi] = mesh.uv_layers['UVmapPoly0'].data[li].uv

	normals = [cn.normal for cn in mesh.vertices]

	return [vertexes, uvs, normals]

def getMeshPolys(obj):
    mesh = obj.data
    pv = [list(cn.vertices) for cn in mesh.polygons]

    return pv

def forChild(object, root, file):
	if (not root):
		try:
			type = object['block_type']
			print(object.name)

			if type != 444 and type != 370:
				file.write(struct.pack("<i",333))#open case
				object_name = object.name.split(".")[0]

				if object.name[0:8] == 'Untitled':
					file.write(bytearray(b'\x00'*32))
				else:
					file.write(str.encode(object_name)+bytearray(b'\x00'*(32-len(object_name))))#Block Name

				if type != 37:
					file.write(struct.pack("<i",type)) #Block Type

			type1 = ""

			if "type1" in object:
				type1 = object['type1']
			else:
				type1 = "manual"


			#if (type == 0):
			#	file.write(bytearray(b'\x00'*12))
			#	file.write(bytearray(b'\x00'*32))

			if (type == 0):
				file.write(str.encode(object['add_space'])+bytearray(b'\x00'*(32-len(object['add_space']))))
				file.write(struct.pack("<f",object.location.x))
				file.write(struct.pack("<f",object.location.y))
				file.write(struct.pack("<f",object.location.z))

			#if (type == 0):
				#file.write(str.encode(object['add_space'])+bytearray(b'\x00'*(32-len(object['add_space']))))
				#file.write(struct.pack("<f",object.location.x))
				#file.write(struct.pack("<f",object.location.y))
				#file.write(struct.pack("<f",object.location.z))

			if (type == 1): #camera
				file.write(str.encode(object['add_space'])+bytearray(b'\x00'*(32-len(object['add_space'])))) #obs_space
				file.write(str.encode(object['route_name'])+bytearray(b'\x00'*(32-len(object['route_name'])))) #start_room

			elif(type==3):
				file.write(struct.pack("<f",object.location.x))
				file.write(struct.pack("<f",object.location.y))
				file.write(struct.pack("<f",object.location.z))
				file.write(struct.pack("<f",object['node_radius']))
				file.write(struct.pack("<i",len(object.children)))

			elif(type==4):
				file.write(struct.pack("<f",object.location.x))
				file.write(struct.pack("<f",object.location.y))
				file.write(struct.pack("<f",object.location.z))
				file.write(struct.pack("<f",object['node_radius']))
				file.write(str.encode(object['add_name'])+bytearray(b'\x00'*(32-len(object['add_name']))))
				file.write(str.encode(object['add_name1'])+bytearray(b'\x00'*(32-len(object['add_name1']))))
				file.write(struct.pack("<i",len(object.children)))

			elif(type==5):
				file.write(struct.pack("<f",object.location.x))
				file.write(struct.pack("<f",object.location.y))
				file.write(struct.pack("<f",object.location.z))
				file.write(struct.pack("<f",object['node_radius']))
				file.write(str.encode(object['add_name'])+bytearray(b'\x00'*(32-len(object['add_name']))))#Block Name
				file.write(struct.pack("<i",len(object.children)))

			elif (type==7 and type1 == "manual"):
				verticesL = []
				uvs = []
				faces = []

				bm = bmesh.new()
				bm.from_mesh(object.data)
				bm.verts.ensure_lookup_table()
				bm.faces.ensure_lookup_table()

				try:
					uv_layer = bm.loops.layers.uv[0]
				except:
					pass

				#mesh = obj.data
				#bm = bmesh.new()
				#bm.from_mesh(mesh)

				#bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method=0, ngon_method=0)
				bmesh.ops.triangulate(bm, faces=bm.faces, quad_method=0, ngon_method=0)
				bm.transform(global_matrix * object.matrix_world)

				bm.to_mesh(object.data)
				#bm.free()

				#bmesh.ops.triangulate(bm, faces=bm.faces)


				for v in bm.verts:
					try:
						uv_first = uv_from_vert_first(uv_layer, v)
						uv_average = uv_from_vert_average(uv_layer, v)
						verticesL.append((v.co,v.normal,uv_average))
					except:
						pass
				for f in bm.faces:
					f.normal_flip()

				meshdata = object.data

				for i, polygon in enumerate(meshdata.polygons):
					for i1, loopindex in enumerate(polygon.loop_indices):
						meshloop = meshdata.loops[loopindex]
						faces.append(meshloop.vertex_index)
						try:
							uvs.append(meshdata.uv_layers[0].data[loopindex].uv)
						except:
							pass
					verNums.extend(polygon.vertices)

				file.write(struct.pack("<f",object.location.x))
				file.write(struct.pack("<f",object.location.y))
				file.write(struct.pack("<f",object.location.z))
				file.write(struct.pack("<f",0))
				file.write(bytearray(b'\x00'*32))
				vLen = len(verticesL)

				file.write(struct.pack("<i",vLen))

				for i,vert in enumerate(verticesL):
						file.write(struct.pack("<f",vert[0][0])) #x
						file.write(struct.pack("<f",-vert[0][2])) #z
						file.write(struct.pack("<f",vert[0][1])) #y

						try:
							file.write(struct.pack("<f",vert[2][0])) #u
							file.write(struct.pack("<f",1-vert[2][1])) #v
						except:
							file.write(struct.pack("<f",0)) #u
							file.write(struct.pack("<f",0)) #v

				file.write(struct.pack("<i",1))

				#type 8

				if object['BType'] == 8:
					export08(object, verticesL, file, faces, uvs)
				else:
					export35(object, verticesL, file, faces, uvs)

				#file.write(struct.pack("<i",555))

			elif (type==7 and type1 == "auto"):
				verticesL = []
				uvs = []
				faces = []

				bm = bmesh.new()
				bm.from_mesh(object.data)
				bm.verts.ensure_lookup_table()
				bm.faces.ensure_lookup_table()

				try:
					uv_layer = bm.loops.layers.uv[0]
				except:
					pass

				#mesh = obj.data
				#bm = bmesh.new()
				#bm.from_mesh(mesh)

				#bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method=0, ngon_method=0)
				bmesh.ops.triangulate(bm, faces=bm.faces, quad_method=0, ngon_method=0)
				bm.transform(global_matrix * object.matrix_world)

				bm.to_mesh(object.data)
				#bm.free()

				#bmesh.ops.triangulate(bm, faces=bm.faces)


				for v in bm.verts:
					try:
						uv_first = uv_from_vert_first(uv_layer, v)
						uv_average = uv_from_vert_average(uv_layer, v)
						verticesL.append((v.co,v.normal,uv_average))
					except:
						pass
				for f in bm.faces:
					f.normal_flip()

				meshdata = object.data

				for i, polygon in enumerate(meshdata.polygons):
					for i1, loopindex in enumerate(polygon.loop_indices):
						meshloop = meshdata.loops[loopindex]
						faces.append(meshloop.vertex_index)
						try:
							uvs.append(meshdata.uv_layers[0].data[loopindex].uv)
						except:
							pass
					verNums.extend(polygon.vertices)

				file.write(struct.pack("<f",object.location.x))
				file.write(struct.pack("<f",object.location.y))
				file.write(struct.pack("<f",object.location.z))
				file.write(struct.pack("<f",15))
				file.write(bytearray(b'\x00'*32))
				vLen = len(verticesL)

				file.write(struct.pack("<i",vLen))

				for i,vert in enumerate(verticesL):
						file.write(struct.pack("<f",vert[0][0])) #x
						file.write(struct.pack("<f",-vert[0][2])) #z
						file.write(struct.pack("<f",vert[0][1])) #y

						try:
							file.write(struct.pack("<f",vert[2][0])) #u
							file.write(struct.pack("<f",1-vert[2][1])) #v
						except:
							file.write(struct.pack("<f",0)) #u
							file.write(struct.pack("<f",0)) #v

				smoothed_faces = []
				flat_faces = []

				for face in bm.faces:
					if face.smooth == True:
						for i in range(len(face.verts)):
							smoothed_faces.append(face.verts[i].index)
					else:
						for i in range(len(face.verts)):
							flat_faces.append(face.verts[i].index)
						#for i, polygon in enumerate(meshdata.polygons):
						#	for i1, loopindex in enumerate(polygon.loop_indices):
						#		meshloop = meshdata.loops[loopindex]
						#		flat_faces.append(meshloop.vertex_index)

				print(smoothed_faces)
				print("salo")
				print(flat_faces)

				mesh_blocks = 0

				if len(smoothed_faces) > 0:
					mesh_blocks += 1

				if len(flat_faces) > 0:
					mesh_blocks += 1

				file.write(struct.pack("<i",mesh_blocks))

				#35

				if len(smoothed_faces) > 0:
					file.write(struct.pack("<i",333))
					file.write(bytearray(b'\x00'*32))


					file.write(struct.pack("<i",int(35)))

					file.write(bytearray(b'\x00'*16))
					file.write(struct.pack("<i",object['MType']))
					if generatePro == True:
						material_name = object.data.materials[0].name
						texNum = bpy.data.materials.find(material_name)
						file.write(struct.pack("<i",texNum))
					else:
						file.write(struct.pack("<i",object['texNum']))

					fLen = len(smoothed_faces)//3
					file.write(struct.pack("<i",fLen))

					for i in range(fLen):

						if (object['MType']==3):
							file.write(struct.pack("<i",16))
							file.write(struct.pack("<f",1.0))
							file.write(struct.pack("<i",32767))
							if generatePro == True:
								material_name = object.data.materials[0].name
								texNum = bpy.data.materials.find(material_name)
								file.write(struct.pack("<i",texNum))
							else:
								file.write(struct.pack("<i",object['texNum']))
							file.write(struct.pack("<i",3))#VerNum
							file.write(struct.pack("<3i",smoothed_faces[i*3],smoothed_faces[i*3+1],smoothed_faces[i*3+2]))
							#file.write(struct.pack("<iffiffiff",faces[i*3],verticesL[faces[i*3]][2][0],1-verticesL[faces[i*3]][2][1],faces[i*3+1],verticesL[faces[i*3+1]][2][0],1-verticesL[faces[i*3+1]][2][1],faces[i*3+2],verticesL[faces[i*3+2]][2][0],1-verticesL[faces[i*3+2]][2][1]))
							verticesL

						elif (object['MType']==1):
							file.write(struct.pack("<i",50))
							file.write(struct.pack("<f",1.0))
							file.write(struct.pack("<i",32767))
							if generatePro == True:
								material_name = object.data.materials[0].name
								texNum = bpy.data.materials.find(material_name)
								file.write(struct.pack("<i",texNum))
							else:
								file.write(struct.pack("<i",object['texNum']))
							file.write(struct.pack("<i",3))#VerNum

							file.write(struct.pack("<i5f",smoothed_faces[i*3],uvs[i*3].x, 1-uvs[i*3].y, -verticesL[smoothed_faces[i*3]][1][0], verticesL[smoothed_faces[i*3]][1][1], verticesL[smoothed_faces[i*3]][1][2]))
							file.write(struct.pack("<i5f",smoothed_faces[i*3+1],uvs[i*3+1].x, 1-uvs[i*3+1].y, -verticesL[smoothed_faces[i*3+1]][1][0], verticesL[smoothed_faces[i*3+1]][1][1], verticesL[smoothed_faces[i*3+1]][1][2]))
							file.write(struct.pack("<i5f",smoothed_faces[i*3+2],uvs[i*3+2].x, 1-uvs[i*3+2].y, -verticesL[smoothed_faces[i*3+2]][1][0], verticesL[smoothed_faces[i*3+2]][1][1], verticesL[smoothed_faces[i*3+2]][1][2]))

							#file.write(struct.pack("<iffiffiff",faces[i*3],uvs[i*3].x,uvs[i*3].y,faces[i*3+1],uvs[i*3+1].x,uvs[i*3+1].y,faces[i*3+2],uvs[i*3+2].x,uvs[i*3+2].y))

					file.write(struct.pack("<i",555))

				#08

				if len(flat_faces) > 0:
					file.write(struct.pack("<i",333))
					file.write(bytearray(b'\x00'*32))

					file.write(struct.pack("<i",int(8)))

					file.write(struct.pack("<f",object.location.x))
					file.write(struct.pack("<f",object.location.y))
					file.write(struct.pack("<f",object.location.z))
					file.write(struct.pack("<f",0))

					#file.write(struct.pack("<i",object['MType']))
					#file.write(struct.pack("<i",object['texNum']))

					fLen = len(flat_faces)//3
					file.write(struct.pack("<i",fLen))
					#file.write(struct.pack("<i", object['FType']))

					for i in range(fLen):

						if (object['FType']==0 or object['FType']==1):
							file.write(struct.pack("<i", object['FType']))
							file.write(struct.pack("<f",1.0))
							file.write(struct.pack("<i",32767))
							if generatePro == True:
								material_name = object.data.materials[0].name
								texNum = bpy.data.materials.find(material_name)
								file.write(struct.pack("<i",texNum))
							else:
								file.write(struct.pack("<i",object['texNum']))
							file.write(struct.pack("<i",3))
							file.write(struct.pack("<3i",flat_faces[i*3],flat_faces[i*3+1],flat_faces[i*3+2]))
							verticesL

						if (object['FType']==2):
							file.write(struct.pack("<i", object['FType']))
							file.write(struct.pack("<f",1.0))
							file.write(struct.pack("<i",32767))
							if generatePro == True:
								material_name = object.data.materials[0].name
								texNum = bpy.data.materials.find(material_name)
								file.write(struct.pack("<i",texNum))
							else:
								file.write(struct.pack("<i",object['texNum']))
							file.write(struct.pack("<i",3))
							file.write(struct.pack("<i2f",flat_faces[i*3],uvs[i*3].x, 1-uvs[i*3].y))
							file.write(struct.pack("<i2f",flat_faces[i*3+1],uvs[i*3+1].x, 1-uvs[i*3+1].y))
							file.write(struct.pack("<i2f",flat_faces[i*3+2],uvs[i*3+2].x, 1-uvs[i*3+2].y))

							#file.write(struct.pack("<i",3))
							#file.write(struct.pack("<i2f",faces[i*3],uvs[i*3].x, 1-uvs[i*3].y))
							#file.write(struct.pack("<i2f",faces[i*3+1],uvs[i*3+1].x, 1-uvs[i*3+2].y))
							#file.write(struct.pack("<i2f",faces[i*3+2],uvs[i*3+2].x, 1-uvs[i*3+2].y))

							verticesL

						if (object['FType']==144 or object['FType']==128):
							file.write(struct.pack("<i", object['FType']))
							file.write(struct.pack("<f",1.0))
							file.write(struct.pack("<i",32767))
							if generatePro == True:
								material_name = object.data.materials[0].name
								texNum = bpy.data.materials.find(material_name)
								file.write(struct.pack("<i",texNum))
							else:
								file.write(struct.pack("<i",object['texNum']))
							file.write(struct.pack("<i",3))
							file.write(struct.pack("<3i",flat_faces[i*3],flat_faces[i*3+1],flat_faces[i*3+2]))
							verticesL

					file.write(struct.pack("<i",555))

			elif (type==10):

				file.write(struct.pack("<f",object.location.x))
				file.write(struct.pack("<f",object.location.y))
				file.write(struct.pack("<f",object.location.z))
				file.write(struct.pack("<f",object['node_radius']))

				file.write(struct.pack("<f",object.location.x))
				file.write(struct.pack("<f",object.location.y))
				file.write(struct.pack("<f",object.location.z))
				file.write(struct.pack("<f",object['lod_distance']))

				file.write(struct.pack("<i",len(object.children) - 1))

			elif (type==12): # flat collision
				file.write(struct.pack("<f",0))
				file.write(struct.pack("<f",0))
				file.write(struct.pack("<f",0))
				file.write(struct.pack("<f",0))
				file.write(struct.pack("<f",0))
				file.write(struct.pack("<f",0))
				file.write(struct.pack("<f",object['pos']))
				file.write(struct.pack("<f",-object['height']))
				file.write(struct.pack("<i",1))
				file.write(struct.pack("<i",object['CType']))
				file.write(struct.pack("<i",0))

			elif (type==13): #trigger
				file.write(struct.pack("<f",0))
				file.write(struct.pack("<f",0))
				file.write(struct.pack("<f",0))
				if object['type'] == "loader":
					file.write(struct.pack("<f",0))
					file.write(struct.pack("<i",4095))
					file.write(struct.pack("<i",0))
					file.write(struct.pack("<i",1))
					file.write(str.encode(object['route_name'])+bytearray(b'\x00'*(3-len(object['route_name']))))
					file.write(bytearray(b'\xCD'))
				if object['type'] == "radar0":
					file.write(struct.pack("<f",object['var0']))
					file.write(struct.pack("<i",-(object.location.x + 4)))
					file.write(struct.pack("<i",object['var2']))
					file.write(struct.pack("<i",object['speed_limit']))
					file.write(struct.pack("<f",1))
					file.write(struct.pack("<f",0))
					file.write(struct.pack("<f",0))
				if object['type'] == "radar1":
					file.write(struct.pack("<f",object['var0']))
					file.write(struct.pack("<i",object['var1']))
					file.write(struct.pack("<i",object['var2']))
					file.write(struct.pack("<i",object['speed_limit']))
					file.write(struct.pack("<f",1))
					file.write(struct.pack("<f",0))
					file.write(struct.pack("<f",0))

			elif (type==14): # event object (ball in tb.b3d or sell block)
				file.write(struct.pack("<f",0))
				file.write(struct.pack("<f",0))
				file.write(struct.pack("<f",0))
				file.write(struct.pack("<f",0))
				file.write(struct.pack("<f",object['var0']))
				file.write(struct.pack("<f",object['var1']))
				file.write(struct.pack("<f",object['var2']))
				file.write(struct.pack("<f",object['var3']))
				file.write(struct.pack("<i",object['var4']))
				file.write(struct.pack("<i",0))
				file.write(struct.pack("<i",0))

			elif (type==18): # connects model with space

				file.write(struct.pack("<f",object.location.x))
				file.write(struct.pack("<f",object.location.y))
				file.write(struct.pack("<f",object.location.z))
				file.write(struct.pack("<f",object['node_radius']))

				file.write(str.encode(object['space_name'])+bytearray(b'\x00'*(32-len(object['space_name']))))
				file.write(str.encode(object['add_name'])+bytearray(b'\x00'*(32-len(object['add_name']))))

			elif (type==19):
				file.write(struct.pack("<i",len(object.children)))

			elif (type==20): # sharp collision
				verticesL = []

				file.write(struct.pack("<f",0))
				file.write(struct.pack("<f",0))
				file.write(struct.pack("<f",0))
				file.write(struct.pack("<f",0))

				#bm = bmesh.new()
				#bm.from_mesh(object.data)
				#bm.verts.ensure_lookup_table()

				#for v in bm.verts:
				#	verticesL.append(v.co)

				#VerNum = len(verticesL)+1

				#file.write(struct.pack("<i",VerNum))	#vertices+1
				for subcurve in object.data.splines:
					file.write(struct.pack("<i",len(subcurve.points)))

				file.write(struct.pack("<f",0))
				file.write(struct.pack("<f",0))
				file.write(struct.pack("<f",0))

				for point in subcurve.points:
					file.write(struct.pack("<f",point.co.x))
					file.write(struct.pack("<f",point.co.y))
					file.write(struct.pack("<f",point.co.z))

				#for i in range(VerNum):
				#	if (i==VerNum-1):
				#		file.write(struct.pack("<f",verticesL[0][0]))
				#		file.write(struct.pack("<f",verticesL[0][2]))
				#		file.write(struct.pack("<f",verticesL[0][1]))

				#	else:
				#		file.write(struct.pack("<f",verticesL[i][0]))
				#		file.write(struct.pack("<f",verticesL[i][2]))
				#		file.write(struct.pack("<f",verticesL[i][1]))

			elif (type==21):

				file.write(struct.pack("<f",object.location.x))
				file.write(struct.pack("<f",object.location.y))
				file.write(struct.pack("<f",object.location.z))
				file.write(struct.pack("<f",object['node_radius']))

				file.write(struct.pack("<i",object['groups_num']))
				file.write(struct.pack("<i",0))

				file.write(struct.pack("<i",len(object.children)-object['groups_num']+1))


			elif (type==23):
				file.write(struct.pack("<i",1))
				file.write(struct.pack("<i",object['CType']))
				file.write(struct.pack("<i",0))

				bm = bmesh.new()
				bm.from_mesh(object.data)
				bm.verts.ensure_lookup_table()
				bm.faces.ensure_lookup_table()

				bmesh.ops.triangulate(bm, faces=bm.faces, quad_method=0, ngon_method=0)

				bm.transform(global_matrix * object.matrix_world)
				bm.to_mesh(object.data)

				file.write(struct.pack("<i",len(bm.faces)))

				for face in bm.faces:
					#file.write(struct.pack("<i",len(face.verts)))
					file.write(struct.pack("<i",3))

					#file.write(struct.pack("<fff",face.verts[0].co[0],face.verts[0].co[2],face.verts[0].co[1]))
					#file.write(struct.pack("<fff",face.verts[1].co[0],face.verts[1].co[2],face.verts[1].co[1]))
					#file.write(struct.pack("<fff",face.verts[2].co[0],face.verts[2].co[2],face.verts[2].co[1]))

					#file.write(struct.pack("<fff",face.verts[1].co[0],face.verts[1].co[2],face.verts[1].co[1]))
					#file.write(struct.pack("<fff",face.verts[0].co[0],face.verts[0].co[2],face.verts[0].co[1]))
					#file.write(struct.pack("<fff",face.verts[2].co[0],face.verts[2].co[2],face.verts[2].co[1]))

					file.write(struct.pack("<fff",face.verts[0].co[0],-face.verts[0].co[2],face.verts[0].co[1]))
					file.write(struct.pack("<fff",face.verts[1].co[0],-face.verts[1].co[2],face.verts[1].co[1]))
					file.write(struct.pack("<fff",face.verts[2].co[0],-face.verts[2].co[2],face.verts[2].co[1]))

			elif (type==24):
				#file.write(struct.pack("<f",1))
				#file.write(struct.pack("<f",0))
				#file.write(struct.pack("<f",0))

				#file.write(struct.pack("<f",0))
				#file.write(struct.pack("<f",1))
				#file.write(struct.pack("<f",0))

				#file.write(struct.pack("<f",0))
				#file.write(struct.pack("<f",0))
				#file.write(struct.pack("<f",1))
				#PI = 3.14159265358979
				#object.rotation_euler[0] *= -1
				#object.rotation_euler[1] *= -1
				#object.rotation_euler[2] *= -1

				#object_matrix = object.matrix_world.to_3x3() #.normalized()

				PI = 3.14159265358979


				cos_y = cos(-object.rotation_euler[1])
				sin_y = sin(-object.rotation_euler[1])
				cos_z = cos(-object.rotation_euler[2])
				sin_z = sin(-object.rotation_euler[2])
				cos_x = cos(-object.rotation_euler[0])
				sin_x = sin(-object.rotation_euler[0])

				file.write(struct.pack("<f",(cos_y * cos_z)*object.scale[0]))
				file.write(struct.pack("<f",(sin_y * sin_x - cos_y * sin_z * cos_x)*object.scale[1]))
				file.write(struct.pack("<f",(cos_y * sin_z * sin_x + sin_y * cos_x)*object.scale[2]))
				file.write(struct.pack("<f",(sin_z)*object.scale[0]))
				file.write(struct.pack("<f",(cos_z * cos_x)*object.scale[1]))
				file.write(struct.pack("<f",(-cos_z * sin_x)*object.scale[2]))
				file.write(struct.pack("<f",(-sin_y * cos_z)*object.scale[0]))
				file.write(struct.pack("<f",(sin_y * sin_z * cos_x + cos_y * sin_x)*object.scale[1]))
				file.write(struct.pack("<f",(-sin_y * sin_z * sin_x + cos_y * cos_x)*object.scale[2]))

				"""
				if ((object.rotation_euler[0] * 180/PI) < -180):
					object.rotation_euler[0] = (360+(object.rotation_euler[0] * 180/PI)) * PI/180
				elif ((object.rotation_euler[0] * 180/PI) > 180):
					object.rotation_euler[0] = (360-(object.rotation_euler[0] * 180/PI)) * PI/180

				if ((object.rotation_euler[1] * 180/PI) < -180):
					object.rotation_euler[1] = (360+(object.rotation_euler[1] * 180/PI)) * PI/180
				elif ((object.rotation_euler[1] * 180/PI) > 180):
					object.rotation_euler[1] = (360-(object.rotation_euler[1] * 180/PI)) * PI/180

				if ((object.rotation_euler[2] * 180/PI) < -180):
					object.rotation_euler[2] = (360+(object.rotation_euler[2] * 180/PI)) * PI/180
				elif ((object.rotation_euler[2] * 180/PI) > 180):
					object.rotation_euler[2] = (360-(object.rotation_euler[2] * 180/PI)) * PI/180
				"""

				#file.write(struct.pack("<f",object_matrix[0][0]))
				#file.write(struct.pack("<f",object_matrix[0][1]))
				#file.write(struct.pack("<f",object_matrix[0][2]))

				#file.write(struct.pack("<f",object_matrix[1][0]))
				#file.write(struct.pack("<f",object_matrix[1][1]))
				#file.write(struct.pack("<f",object_matrix[1][2]))

				#file.write(struct.pack("<f",object_matrix[2][0]))
				#file.write(struct.pack("<f",object_matrix[2][1]))
				#file.write(struct.pack("<f",object_matrix[2][2]))

				file.write(struct.pack("<f",object.location.x))
				file.write(struct.pack("<f",object.location.y))
				file.write(struct.pack("<f",object.location.z))

				file.write(struct.pack("<i",(object['flag'])))
				file.write(struct.pack("<i",len(object.children)))

			elif (type==25):

				file.write(struct.pack("<i",32767))
				file.write(struct.pack("<i",2))
				file.write(struct.pack("<i",256))

				file.write(str.encode(object['sound_name'])+bytearray(b'\x00'*(32-len(object['sound_name']))))

				file.write(struct.pack("<f",object.location.x))
				file.write(struct.pack("<f",object.location.y))
				file.write(struct.pack("<f",object.location.z))

				file.write(struct.pack("<f",1))
				file.write(struct.pack("<f",0))
				file.write(struct.pack("<f",0))

				file.write(struct.pack("<f",6.2831855))
				file.write(struct.pack("<f",3.1415927))
				file.write(struct.pack("<f",40))

				file.write(struct.pack("<f",object['RSound']))
				file.write(struct.pack("<f",object['SLevel']))

			elif (type==28):
				file.write(struct.pack("<f",0)) #node_x
				file.write(struct.pack("<f",0)) #node_y
				file.write(struct.pack("<f",0)) #node_z
				file.write(struct.pack("<f",0))
				file.write(struct.pack("<f",object.location.x))
				file.write(struct.pack("<f",object.location.y))
				file.write(struct.pack("<f",object.location.z))
				file.write(struct.pack("<2ifi",1,2,1,32767))
				if generatePro == True:
					material_name = object.data.materials[0].name
					texNum = bpy.data.materials.find(material_name)
					file.write(struct.pack("<i",texNum))
				else:
					file.write(struct.pack("<i",object['texNum']))
					file.write(struct.pack("<i",4))

				file.write(struct.pack("<f",(-object['sprite_radius'])))
				file.write(struct.pack("<f",(object['sprite_radius'])))
				file.write(struct.pack("<f",0))
				file.write(struct.pack("<f",0))

				file.write(struct.pack("<f",(-object['sprite_radius'])))
				file.write(struct.pack("<f",(-object['sprite_radius'])))
				file.write(struct.pack("<f",0))
				file.write(struct.pack("<f",1))

				file.write(struct.pack("<f",(object['sprite_radius'])))
				file.write(struct.pack("<f",(-object['sprite_radius'])))
				file.write(struct.pack("<f",1))
				file.write(struct.pack("<f",1))

				file.write(struct.pack("<f",(object['sprite_radius'])))
				file.write(struct.pack("<f",(object['sprite_radius'])))
				file.write(struct.pack("<f",1))
				file.write(struct.pack("<f",0))

			elif (type==30): # level loader
				verticesL = []

				file.write(struct.pack("<f",object.location.x))
				file.write(struct.pack("<f",object.location.y))
				file.write(struct.pack("<f",object.location.z + 50))
				file.write(struct.pack("<f",(object['radius'])))
				file.write(str.encode(object['room_name'])+bytearray(b'\x00'*(32-len(object['room_name']))))

				#location_1 = bpy.context.scene.cursor_location
				#bpy.context.scene.cursor_location = (0.0, 0.0, 0.0)
				#bpy.ops.object.origin_set(type='ORIGIN_CURSOR')

				bm = bmesh.new()
				bm.from_mesh(object.data)
				bm.transform(global_matrix * object.matrix_world)
				bm.verts.ensure_lookup_table()
				#bm.free()

				for v in bm.verts:
					verticesL.append(v.co)

				#VerNum = len(verticesL)+1


				#for i in range(VerNum):
				#	if (i==VerNum-1):
				#		file.write(struct.pack("<f",verticesL[0][0]))
				#		file.write(struct.pack("<f",verticesL[0][1]))
				#		file.write(struct.pack("<f",verticesL[0][2]))

				file.write(struct.pack("<f",verticesL[3][0]))
				file.write(struct.pack("<f",-verticesL[3][2]))
				file.write(struct.pack("<f",verticesL[3][1]))

				file.write(struct.pack("<f",verticesL[1][0]))
				file.write(struct.pack("<f",-verticesL[1][2]))
				file.write(struct.pack("<f",verticesL[1][1]))

				#bpy.context.scene.cursor_location = location_1
				bm.free()


			elif (type==33):
				file.write(struct.pack("<f",object.location.x)) #node pos
				file.write(struct.pack("<f",object.location.y))
				file.write(struct.pack("<f",object.location.z))
				file.write(struct.pack("<f",(object['node_radius'])))
				file.write(struct.pack("<i",1)) #use_lights
				file.write(struct.pack("<i",(object['light_type'])))
				file.write(struct.pack("<i",2))
				file.write(struct.pack("<f",object.location.x)) #lamp pos
				file.write(struct.pack("<f",object.location.y))
				file.write(struct.pack("<f",object.location.z))
				file.write(struct.pack("<5f",0,0,1,1,0))
				file.write(struct.pack("<f",(object['light_radius'])))
				file.write(struct.pack("<f",(object['intensity'])))
				file.write(struct.pack("<f",0))
				file.write(struct.pack("<f",0))
				file.write(struct.pack("<f",(object['R'])))
				file.write(struct.pack("<f",(object['G'])))
				file.write(struct.pack("<f",(object['B'])))
				file.write(struct.pack("<i",len(object.children)))

			elif (type==37 and type1 == "manual"):
				verticesL = []
				uvs = []
				faces = []

				bm = bmesh.new()
				bm.from_mesh(object.data)
				bm.verts.ensure_lookup_table()
				bm.faces.ensure_lookup_table()

				uv_layer = bm.loops.layers.uv[0]

				#mesh = obj.data
				#bm = bmesh.new()
				#bm.from_mesh(mesh)

				#bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method=0, ngon_method=0)
				bmesh.ops.triangulate(bm, faces=bm.faces, quad_method=0, ngon_method=0)

				bm.transform(global_matrix * object.matrix_world)
				bm.to_mesh(object.data)
				#bm.free()

				#bmesh.ops.triangulate(bm, faces=bm.faces)


				for v in bm.verts:
					uv_first = uv_from_vert_first(uv_layer, v)
					uv_average = uv_from_vert_average(uv_layer, v)

					verticesL.append((v.co,v.normal,uv_average))

				#for f in bm.faces:
					#f.normal_flip()

				#if (object['MType']==3):
					#meshdata = object.data
					#matrix = mathutils.Matrix(([1,0,0,0],[0,0,-1,0],[0,0,0,0],[1,0,0,1]))
					#matrix = mathutils.Matrix(([1,0,0,0],[0,0,-1,0],[0,1,0,0],[1,1,1,1]))
					#meshdata.transform(matrix,0)
					#meshdata.flip_normals()

				#elif (object['MType']==1):
					#meshdata = object.data
					#matrix = mathutils.Matrix(([1,0,0,0],[0,0,1,0],[0,-1,0,0],[0,0,0,1]))
					#meshdata.transform(matrix,0)
					#meshdata.flip_normals()

					#for v in bm.verts:
					#	v.co.x *= -1
					#bmesh.update_edit_mesh(me)

				meshdata = object.data


				for i, polygon in enumerate(meshdata.polygons):
					for i1, loopindex in enumerate(polygon.loop_indices):
						meshloop = meshdata.loops[loopindex]
						faces.append(meshloop.vertex_index)
						uvs.append(meshdata.uv_layers[0].data[loopindex].uv)
					verNums.extend(polygon.vertices)

				file.write(struct.pack("<i",type))
				file.write(struct.pack("<f",object.location.x))
				file.write(struct.pack("<f",object.location.y))
				file.write(struct.pack("<f",object.location.z))
				file.write(struct.pack("<f",0))
				file.write(bytearray(b'\x00'*32))
				vLen = len(verticesL)

				file.write(struct.pack("<i",object['SType'])) # 2 - normals, 3 - verts+uv(no normal), 258 - rain
				file.write(struct.pack("<i",vLen))

				#normals = []

				#for i in range(len(verticesL)):                             ############ это работает, но нормали что так, что так - одно и то же получается
				#	normal_local = object.data.vertices[i].normal.to_4d()
				#	normal_local.w = 0
				#	normal_local = (object.matrix_world * normal_local).to_3d()
				#	normals.append(normal_local)
				#	print(normal_local)


				for i,vert in enumerate(verticesL):

						file.write(struct.pack("<f",vert[0][0])) #x
						file.write(struct.pack("<f",-vert[0][2])) #z
						file.write(struct.pack("<f",vert[0][1])) #y
						try:
							file.write(struct.pack("<f",vert[2][0])) #u
							file.write(struct.pack("<f",1-vert[2][1])) #v
						except:
							file.write(struct.pack("<f",0)) #u
							file.write(struct.pack("<f",0)) #v

						if (object['SType'] == 2):
							file.write(struct.pack("<f",vert[1][0])) #nx
							file.write(struct.pack("<f",vert[1][1])) #nz
							file.write(struct.pack("<f",vert[1][2])) #ny

						elif (object['SType'] == 3):
							file.write(struct.pack("<f",1))

						elif (object['SType'] == 258) or (object['SType'] == 515):
							file.write(struct.pack("<f",vert[1][0])) #nx
							file.write(struct.pack("<f",vert[1][1])) #nz
							file.write(struct.pack("<f",vert[1][2])) #ny
							file.write(struct.pack("<2f",0,1))
							#file.write(struct.pack("<f",vert[2][0])) #u
							#file.write(struct.pack("<f",1-vert[2][1])) #v

						elif (object['SType'] == 514):
							file.write(struct.pack("<f",vert[1][0])) #nx
							file.write(struct.pack("<f",vert[1][1])) #nz
							file.write(struct.pack("<f",vert[1][2])) #ny
							file.write(struct.pack("<4f",0,1,0,1))
							#file.write(struct.pack("<f",vert[2][0])) #u
							#file.write(struct.pack("<f",1-vert[2][1])) #v
							#file.write(struct.pack("<f",vert[2][0])) #u
							#file.write(struct.pack("<f",1-vert[2][1])) #v

				file.write(struct.pack("<i",1))

				if object['BType'] == 35:
					export35(object, verticesL, file, faces, uvs)
				else:
					export08(object, verticesL, file, faces, uvs)

				#file.write(struct.pack("<i",555))

			elif(type == 40):
				file.write(struct.pack("<f",object.location.x))
				file.write(struct.pack("<f",object.location.y))
				file.write(struct.pack("<f",object.location.z))
				file.write(struct.pack("<f",object['node_radius']))
				file.write(bytearray(b'\x00'*32))
				file.write(str.encode(object['GType'])+bytearray(b'\x00'*(32-len(object['GType']))))

				if object['GType'] == "$$TreeGenerator1":
					file.write(struct.pack("<i",object['TGType'])) #file.write(struct.pack("<i",TGType))
					file.write(struct.pack("<i",0))
					file.write(struct.pack("<i",10))
					file.write(struct.pack("<f",0))
					file.write(struct.pack("<f",0))
					file.write(struct.pack("<f",0.28))
					file.write(struct.pack("<f",0))
					file.write(struct.pack("<f",0))
					file.write(struct.pack("<f",0))
					file.write(struct.pack("<f",0.11))
					file.write(struct.pack("<f",0))
					file.write(struct.pack("<f",0))
					file.write(struct.pack("<f",0))

				if object['GType'] == "$$DynamicGlow":
					file.write(struct.pack("<i",9))
					file.write(struct.pack("<i",0))
					file.write(struct.pack("<i",11))
					file.write(struct.pack("<f",1))
					file.write(struct.pack("<f",150))
					file.write(struct.pack("<f",object['scale'])) #1
					file.write(struct.pack("<f",5))
					file.write(struct.pack("<f",1.0471976))
					file.write(struct.pack("<f",2))
					file.write(str.encode(object['mat_name'])+bytearray(b'\x00'*(12-len(object['mat_name']))))
					file.write(struct.pack("<i",16256))
					file.write(struct.pack("<i",-842186592))

			#others blocks
			#

			elif (type==371 and object['type1'] == "auto1"):

				verticesL = []
				uvs = []
				faces = []

				bm = bmesh.new()
				bm.from_mesh(object.data)
				bm.verts.ensure_lookup_table()
				bm.faces.ensure_lookup_table()

				uv_layer = bm.loops.layers.uv[0]

				#mesh = obj.data
				#bm = bmesh.new()
				#bm.from_mesh(mesh)

				#bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method=0, ngon_method=0)
				bmesh.ops.triangulate(bm, faces=bm.faces, quad_method=0, ngon_method=0)

				bm.transform(global_matrix * object.matrix_world)
				bm.to_mesh(object.data)
				#bm.free()

				#bmesh.ops.triangulate(bm, faces=bm.faces)


				for v in bm.verts:
					uv_first = uv_from_vert_first(uv_layer, v)
					uv_average = uv_from_vert_average(uv_layer, v)
					verticesL.append((v.co,v.normal,uv_average))
				#for f in bm.faces:
				#	f.normal_flip()

				meshdata = object.data

				for i, polygon in enumerate(meshdata.polygons):
					for i1, loopindex in enumerate(polygon.loop_indices):
						meshloop = meshdata.loops[loopindex]
						faces.append(meshloop.vertex_index)
						uvs.append(meshdata.uv_layers[0].data[loopindex].uv)
					verNums.extend(polygon.vertices)

				file.write(struct.pack("<i",333))
				file.write(bytearray(b'\x00'*32))
				file.write(struct.pack("<i",37))
				file.write(struct.pack("<f",object.location.x))
				file.write(struct.pack("<f",object.location.y))
				file.write(struct.pack("<f",object.location.z))
				file.write(struct.pack("<f",0))
				file.write(bytearray(b'\x00'*32))

				file.write(struct.pack("<i",object['SType'])) # 2 - normals, 3 - verts+uv(no normal), 258 - rain
				file.write(struct.pack("<i",vLen))

				for i,vert in enumerate(verticesL):
						file.write(struct.pack("<f",vert[0][0])) #x
						file.write(struct.pack("<f",-vert[0][2])) #z
						file.write(struct.pack("<f",vert[0][1])) #y
						try:
							file.write(struct.pack("<f",vert[2][0])) #u
							file.write(struct.pack("<f",1-vert[2][1])) #v
						except:
							file.write(struct.pack("<f",0)) #u
							file.write(struct.pack("<f",0)) #v

						if (object['SType'] == 2):
							file.write(struct.pack("<f",vert[1][0])) #nx
							file.write(struct.pack("<f",-vert[1][2])) #ny
							file.write(struct.pack("<f",vert[1][1])) #nz

						elif (object['SType'] == 3):
							file.write(struct.pack("<f",1))

						elif (object['SType'] == 258) or (object['SType'] == 515):
							file.write(struct.pack("<f",vert[1][0])) #nx
							file.write(struct.pack("<f",-vert[1][2])) #ny
							file.write(struct.pack("<f",vert[1][1])) #nz
							file.write(struct.pack("<2f",0,1))
							#file.write(struct.pack("<f",vert[2][0])) #u
							#file.write(struct.pack("<f",1-vert[2][1])) #v

						elif (object['SType'] == 514):
							file.write(struct.pack("<f",vert[1][0])) #nx
							file.write(struct.pack("<f",-vert[1][2])) #ny
							file.write(struct.pack("<f",vert[1][1])) #nz
							file.write(struct.pack("<4f",0,1,0,1))
							#file.write(struct.pack("<f",vert[2][0])) #u
							#file.write(struct.pack("<f",1-vert[2][1])) #v
							#file.write(struct.pack("<f",vert[2][0])) #u
							#file.write(struct.pack("<f",1-vert[2][1])) #v

				smoothed_faces = []
				flat_faces = []

				for face in bm.faces:
					if face.smooth == True:
						for i in range(len(face.verts)):
							smoothed_faces.append(face.verts[i].index)
					else:
						for i in range(len(face.verts)):
							flat_faces.append(face.verts[i].index)
						#for i, polygon in enumerate(meshdata.polygons):
						#	for i1, loopindex in enumerate(polygon.loop_indices):
						#		meshloop = meshdata.loops[loopindex]
						#		flat_faces.append(meshloop.vertex_index)

				print(smoothed_faces)
				print("salo")
				print(flat_faces)

				mesh_blocks = 0

				if len(smoothed_faces) > 0:
					mesh_blocks += 1

				if len(flat_faces) > 0:
					mesh_blocks += 1

				file.write(struct.pack("<i",mesh_blocks))

				#35

				if len(smoothed_faces) > 0:
					file.write(struct.pack("<i",333))
					file.write(bytearray(b'\x00'*32))


					file.write(struct.pack("<i",int(35)))

					file.write(bytearray(b'\x00'*16))
					file.write(struct.pack("<i",object['MType']))
					if generatePro == True:
						material_name = object.data.materials[0].name
						texNum = bpy.data.materials.find(material_name)
						file.write(struct.pack("<i",texNum))
					else:
						file.write(struct.pack("<i",object['texNum']))

					fLen = len(smoothed_faces)//3
					file.write(struct.pack("<i",fLen))

					for i in range(fLen):

						if (object['MType']==3):
							file.write(struct.pack("<i",16))
							file.write(struct.pack("<f",1.0))
							file.write(struct.pack("<i",32767))
							if generatePro == True:
								material_name = object.data.materials[0].name
								texNum = bpy.data.materials.find(material_name)
								file.write(struct.pack("<i",texNum))
							else:
								file.write(struct.pack("<i",object['texNum']))
							file.write(struct.pack("<i",3))#VerNum
							file.write(struct.pack("<3i",smoothed_faces[i*3],smoothed_faces[i*3+1],smoothed_faces[i*3+2]))
							#file.write(struct.pack("<iffiffiff",faces[i*3],verticesL[faces[i*3]][2][0],1-verticesL[faces[i*3]][2][1],faces[i*3+1],verticesL[faces[i*3+1]][2][0],1-verticesL[faces[i*3+1]][2][1],faces[i*3+2],verticesL[faces[i*3+2]][2][0],1-verticesL[faces[i*3+2]][2][1]))
							verticesL

						elif (object['MType']==1):
							file.write(struct.pack("<i",50))
							file.write(struct.pack("<f",1.0))
							file.write(struct.pack("<i",32767))
							if generatePro == True:
								material_name = object.data.materials[0].name
								texNum = bpy.data.materials.find(material_name)
								file.write(struct.pack("<i",texNum))
							else:
								file.write(struct.pack("<i",object['texNum']))
							file.write(struct.pack("<i",3))#VerNum

							file.write(struct.pack("<i5f",smoothed_faces[i*3],uvs[i*3].x, 1-uvs[i*3].y, -verticesL[smoothed_faces[i*3]][1][0], verticesL[smoothed_faces[i*3]][1][2], verticesL[smoothed_faces[i*3]][1][1]))
							file.write(struct.pack("<i5f",smoothed_faces[i*3+1],uvs[i*3+1].x, 1-uvs[i*3+1].y, -verticesL[smoothed_faces[i*3+1]][1][0], verticesL[smoothed_faces[i*3+1]][1][2], verticesL[smoothed_faces[i*3+1]][1][1]))
							file.write(struct.pack("<i5f",smoothed_faces[i*3+2],uvs[i*3+2].x, 1-uvs[i*3+2].y, -verticesL[smoothed_faces[i*3+2]][1][0], verticesL[smoothed_faces[i*3+2]][1][2], verticesL[smoothed_faces[i*3+2]][1][1]))

							#file.write(struct.pack("<iffiffiff",faces[i*3],uvs[i*3].x,uvs[i*3].y,faces[i*3+1],uvs[i*3+1].x,uvs[i*3+1].y,faces[i*3+2],uvs[i*3+2].x,uvs[i*3+2].y))

					file.write(struct.pack("<i",555))

				#08

				if len(flat_faces) > 0:
					file.write(struct.pack("<i",333))
					file.write(bytearray(b'\x00'*32))

					file.write(struct.pack("<i",int(8)))

					file.write(struct.pack("<f",object.location.x))
					file.write(struct.pack("<f",object.location.y))
					file.write(struct.pack("<f",object.location.z))
					file.write(struct.pack("<f",0))

					#file.write(struct.pack("<i",object['MType']))
					#file.write(struct.pack("<i",object['texNum']))

					fLen = len(flat_faces)//3
					file.write(struct.pack("<i",fLen))
					#file.write(struct.pack("<i", object['FType']))

					for i in range(fLen):

						if (object['FType']==0 or object['FType']==1):
							file.write(struct.pack("<i", object['FType']))
							file.write(struct.pack("<f",1.0))
							file.write(struct.pack("<i",32767))
							if generatePro == True:
								material_name = object.data.materials[0].name
								texNum = bpy.data.materials.find(material_name)
								file.write(struct.pack("<i",texNum))
							else:
								file.write(struct.pack("<i",object['texNum']))
							file.write(struct.pack("<i",3))
							file.write(struct.pack("<3i",flat_faces[i*3],flat_faces[i*3+1],flat_faces[i*3+2]))
							verticesL

						if (object['FType']==2):
							file.write(struct.pack("<i", object['FType']))
							file.write(struct.pack("<f",1.0))
							file.write(struct.pack("<i",32767))
							if generatePro == True:
								material_name = object.data.materials[0].name
								texNum = bpy.data.materials.find(material_name)
								file.write(struct.pack("<i",texNum))
							else:
								file.write(struct.pack("<i",object['texNum']))
							file.write(struct.pack("<i",3))
							file.write(struct.pack("<i2f",flat_faces[i*3],uvs[i*3].x, 1-uvs[i*3].y))
							file.write(struct.pack("<i2f",flat_faces[i*3+1],uvs[i*3+1].x, 1-uvs[i*3+1].y))
							file.write(struct.pack("<i2f",flat_faces[i*3+2],uvs[i*3+2].x, 1-uvs[i*3+2].y))

							#file.write(struct.pack("<i",3))
							#file.write(struct.pack("<i2f",faces[i*3],uvs[i*3].x, 1-uvs[i*3].y))
							#file.write(struct.pack("<i2f",faces[i*3+1],uvs[i*3+1].x, 1-uvs[i*3+2].y))
							#file.write(struct.pack("<i2f",faces[i*3+2],uvs[i*3+2].x, 1-uvs[i*3+2].y))

							verticesL

						if (object['FType']==144 or object['FType']==128):
							file.write(struct.pack("<i", object['FType']))
							file.write(struct.pack("<f",1.0))
							file.write(struct.pack("<i",32767))
							if generatePro == True:
								material_name = object.data.materials[0].name
								texNum = bpy.data.materials.find(material_name)
								file.write(struct.pack("<i",texNum))
							else:
								file.write(struct.pack("<i",object['texNum']))
							file.write(struct.pack("<i",3))
							file.write(struct.pack("<3i",flat_faces[i*3],flat_faces[i*3+1],flat_faces[i*3+2]))
							verticesL

					file.write(struct.pack("<i",555))

			#	bpy.ops.object.mode_set(mode = 'EDIT')

			#	context = bpy.context
			#	obj = context.edit_object
			#	me = obj.data
			#	bm = bmesh.from_edit_mesh(me)
			#	# old seams
			#	old_seams = [e for e in bm.edges if e.seam]
			#	# unmark
			#	for e in old_seams:
			#		e.seam = False
			#	# mark seams from uv islands
			#	bpy.ops.uv.seams_from_islands()
			#	seams = [e for e in bm.edges if e.seam]
			#	# split on seams
			#	print(seams)
			#	print("salo 111")
			#	bmesh.ops.split_edges(bm, edges=seams)
			#	# re instate old seams.. could clear new seams.
			#	for e in old_seams:
			#		e.seam = True
			#	bmesh.update_edit_mesh(me)

			#	boundary_seams = [e for e in bm.edges if e.seam and e.is_boundary]

			#	bpy.ops.object.mode_set(mode = 'OBJECT')

			elif (type==37 and object['type1'] == "auto"):

				verticesL = []
				uvs = []
				faces = []

				bm = bmesh.new()
				bm.from_mesh(object.data)
				bm.verts.ensure_lookup_table()
				bm.faces.ensure_lookup_table()

				uv_layer = bm.loops.layers.uv[0]

				#mesh = obj.data
				#bm = bmesh.new()
				#bm.from_mesh(mesh)

				#bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method=0, ngon_method=0)
				bmesh.ops.triangulate(bm, faces=bm.faces, quad_method=0, ngon_method=0)

				bm.transform(global_matrix * object.matrix_world)
				bm.to_mesh(object.data)
				#bm.free()

				#bmesh.ops.triangulate(bm, faces=bm.faces)


				for v in bm.verts:
					uv_first = uv_from_vert_first(uv_layer, v)
					uv_average = uv_from_vert_average(uv_layer, v)
					verticesL.append((v.co,v.normal,uv_average))
				#for f in bm.faces:
				#	f.normal_flip()

				meshdata = object.data

				for i, polygon in enumerate(meshdata.polygons):
					for i1, loopindex in enumerate(polygon.loop_indices):
						meshloop = meshdata.loops[loopindex]
						faces.append(meshloop.vertex_index)
						uvs.append(meshdata.uv_layers[0].data[loopindex].uv)
					verNums.extend(polygon.vertices)

				file.write(struct.pack("<i",37))
				file.write(struct.pack("<f",object.location.x))
				file.write(struct.pack("<f",object.location.y))
				file.write(struct.pack("<f",object.location.z))
				file.write(struct.pack("<f",0))
				file.write(bytearray(b'\x00'*32))
				vLen = len(verticesL)

				file.write(struct.pack("<i",object['SType'])) # 2 - normals, 3 - verts+uv(no normal), 258 - rain
				file.write(struct.pack("<i",vLen))

				for i,vert in enumerate(verticesL):
						file.write(struct.pack("<f",vert[0][0])) #x
						file.write(struct.pack("<f",-vert[0][2])) #z
						file.write(struct.pack("<f",vert[0][1])) #y
						try:
							file.write(struct.pack("<f",vert[2][0])) #u
							file.write(struct.pack("<f",1-vert[2][1])) #v
						except:
							file.write(struct.pack("<f",0)) #u
							file.write(struct.pack("<f",0)) #v

						if (object['SType'] == 2):
							file.write(struct.pack("<f",vert[1][0])) #nx
							file.write(struct.pack("<f",-vert[1][2])) #ny
							file.write(struct.pack("<f",vert[1][1])) #nz

						elif (object['SType'] == 3):
							file.write(struct.pack("<f",1))

						elif (object['SType'] == 258) or (object['SType'] == 515):
							file.write(struct.pack("<f",vert[1][0])) #nx
							file.write(struct.pack("<f",-vert[1][2])) #ny
							file.write(struct.pack("<f",vert[1][1])) #nz
							file.write(struct.pack("<2f",0,1))
							#file.write(struct.pack("<f",vert[2][0])) #u
							#file.write(struct.pack("<f",1-vert[2][1])) #v

						elif (object['SType'] == 514):
							file.write(struct.pack("<f",vert[1][0])) #nx
							file.write(struct.pack("<f",-vert[1][2])) #ny
							file.write(struct.pack("<f",vert[1][1])) #nz
							file.write(struct.pack("<4f",0,1,0,1))
							#file.write(struct.pack("<f",vert[2][0])) #u
							#file.write(struct.pack("<f",1-vert[2][1])) #v
							#file.write(struct.pack("<f",vert[2][0])) #u
							#file.write(struct.pack("<f",1-vert[2][1])) #v

				smoothed_faces = []
				flat_faces = []

				for face in bm.faces:
					if face.smooth == True:
						for i in range(len(face.verts)):
							smoothed_faces.append(face.verts[i].index)
					else:
						for i in range(len(face.verts)):
							flat_faces.append(face.verts[i].index)
						#for i, polygon in enumerate(meshdata.polygons):
						#	for i1, loopindex in enumerate(polygon.loop_indices):
						#		meshloop = meshdata.loops[loopindex]
						#		flat_faces.append(meshloop.vertex_index)

				print(smoothed_faces)
				print("salo")
				print(flat_faces)

				mesh_blocks = 0

				if len(smoothed_faces) > 0:
					mesh_blocks += 1

				if len(flat_faces) > 0:
					mesh_blocks += 1

				file.write(struct.pack("<i",mesh_blocks))

				#35

				if len(smoothed_faces) > 0:
					file.write(struct.pack("<i",333))
					file.write(bytearray(b'\x00'*32))


					file.write(struct.pack("<i",int(35)))

					file.write(bytearray(b'\x00'*16))
					file.write(struct.pack("<i",object['MType']))
					if generatePro == True:
						material_name = object.data.materials[0].name
						texNum = bpy.data.materials.find(material_name)
						file.write(struct.pack("<i",texNum))
					else:
						file.write(struct.pack("<i",object['texNum']))

					fLen = len(smoothed_faces)//3
					file.write(struct.pack("<i",fLen))

					for i in range(fLen):

						if (object['MType']==3):
							file.write(struct.pack("<i",16))
							file.write(struct.pack("<f",1.0))
							file.write(struct.pack("<i",32767))
							if generatePro == True:
								material_name = object.data.materials[0].name
								texNum = bpy.data.materials.find(material_name)
								file.write(struct.pack("<i",texNum))
							else:
								file.write(struct.pack("<i",object['texNum']))
							file.write(struct.pack("<i",3))#VerNum
							file.write(struct.pack("<3i",smoothed_faces[i*3],smoothed_faces[i*3+1],smoothed_faces[i*3+2]))
							#file.write(struct.pack("<iffiffiff",faces[i*3],verticesL[faces[i*3]][2][0],1-verticesL[faces[i*3]][2][1],faces[i*3+1],verticesL[faces[i*3+1]][2][0],1-verticesL[faces[i*3+1]][2][1],faces[i*3+2],verticesL[faces[i*3+2]][2][0],1-verticesL[faces[i*3+2]][2][1]))
							verticesL

						elif (object['MType']==1):
							file.write(struct.pack("<i",50))
							file.write(struct.pack("<f",1.0))
							file.write(struct.pack("<i",32767))
							if generatePro == True:
								material_name = object.data.materials[0].name
								texNum = bpy.data.materials.find(material_name)
								file.write(struct.pack("<i",texNum))
							else:
								file.write(struct.pack("<i",object['texNum']))
							file.write(struct.pack("<i",3))#VerNum

							file.write(struct.pack("<i5f",smoothed_faces[i*3],uvs[i*3].x, 1-uvs[i*3].y, -verticesL[smoothed_faces[i*3]][1][0], verticesL[smoothed_faces[i*3]][1][2], verticesL[smoothed_faces[i*3]][1][1]))
							file.write(struct.pack("<i5f",smoothed_faces[i*3+1],uvs[i*3+1].x, 1-uvs[i*3+1].y, -verticesL[smoothed_faces[i*3+1]][1][0], verticesL[smoothed_faces[i*3+1]][1][2], verticesL[smoothed_faces[i*3+1]][1][1]))
							file.write(struct.pack("<i5f",smoothed_faces[i*3+2],uvs[i*3+2].x, 1-uvs[i*3+2].y, -verticesL[smoothed_faces[i*3+2]][1][0], verticesL[smoothed_faces[i*3+2]][1][2], verticesL[smoothed_faces[i*3+2]][1][1]))

							#file.write(struct.pack("<iffiffiff",faces[i*3],uvs[i*3].x,uvs[i*3].y,faces[i*3+1],uvs[i*3+1].x,uvs[i*3+1].y,faces[i*3+2],uvs[i*3+2].x,uvs[i*3+2].y))

					file.write(struct.pack("<i",555))

				#08

				if len(flat_faces) > 0:
					file.write(struct.pack("<i",333))
					file.write(bytearray(b'\x00'*32))

					file.write(struct.pack("<i",int(8)))

					file.write(struct.pack("<f",object.location.x))
					file.write(struct.pack("<f",object.location.y))
					file.write(struct.pack("<f",object.location.z))
					file.write(struct.pack("<f",0))

					#file.write(struct.pack("<i",object['MType']))
					#file.write(struct.pack("<i",object['texNum']))

					fLen = len(flat_faces)//3
					file.write(struct.pack("<i",fLen))
					#file.write(struct.pack("<i", object['FType']))

					for i in range(fLen):

						if (object['FType']==0 or object['FType']==1):
							file.write(struct.pack("<i", object['FType']))
							file.write(struct.pack("<f",1.0))
							file.write(struct.pack("<i",32767))
							if generatePro == True:
								material_name = object.data.materials[0].name
								texNum = bpy.data.materials.find(material_name)
								file.write(struct.pack("<i",texNum))
							else:
								file.write(struct.pack("<i",object['texNum']))
							file.write(struct.pack("<i",3))
							file.write(struct.pack("<3i",flat_faces[i*3],flat_faces[i*3+1],flat_faces[i*3+2]))
							verticesL

						if (object['FType']==2):
							file.write(struct.pack("<i", object['FType']))
							file.write(struct.pack("<f",1.0))
							file.write(struct.pack("<i",32767))
							if generatePro == True:
								material_name = object.data.materials[0].name
								texNum = bpy.data.materials.find(material_name)
								file.write(struct.pack("<i",texNum))
							else:
								file.write(struct.pack("<i",object['texNum']))
							file.write(struct.pack("<i",3))
							file.write(struct.pack("<i2f",flat_faces[i*3],uvs[i*3].x, 1-uvs[i*3].y))
							file.write(struct.pack("<i2f",flat_faces[i*3+1],uvs[i*3+1].x, 1-uvs[i*3+1].y))
							file.write(struct.pack("<i2f",flat_faces[i*3+2],uvs[i*3+2].x, 1-uvs[i*3+2].y))

							#file.write(struct.pack("<i",3))
							#file.write(struct.pack("<i2f",faces[i*3],uvs[i*3].x, 1-uvs[i*3].y))
							#file.write(struct.pack("<i2f",faces[i*3+1],uvs[i*3+1].x, 1-uvs[i*3+2].y))
							#file.write(struct.pack("<i2f",faces[i*3+2],uvs[i*3+2].x, 1-uvs[i*3+2].y))

							verticesL

						if (object['FType']==144 or object['FType']==128):
							file.write(struct.pack("<i", object['FType']))
							file.write(struct.pack("<f",1.0))
							file.write(struct.pack("<i",32767))
							if generatePro == True:
								material_name = object.data.materials[0].name
								texNum = bpy.data.materials.find(material_name)
								file.write(struct.pack("<i",texNum))
							else:
								file.write(struct.pack("<i",object['texNum']))
							file.write(struct.pack("<i",3))
							file.write(struct.pack("<3i",flat_faces[i*3],flat_faces[i*3+1],flat_faces[i*3+2]))
							verticesL

					file.write(struct.pack("<i",555))


				#if object['BType'] == 35:
				#	export35(object, verticesL, file, faces, uvs)
				#else:
				#	export08(object, verticesL, file, faces, uvs)

				#file.write(struct.pack("<i",555))

			#elif(type == 41):
			#	None
				#export 40blk

			elif (type==444):
				file.write(struct.pack("<i",444))

			elif (type==370):
				pass

			else:
				print('Unknown block type: '+str(type))

		#except (TypeError):
		#	print('TypeError object: '+object.name) #ошибка меша
		#	MsgBox('Check "' + object.name + '" object.', "TypeError", 'ERROR')

		#except (IndexError):
		#	print('IndexError object: '+object.name) #uv
		#	MsgBox('Check "' + object.name + '" object UV.', "IndexError", 'ERROR')

		except (KeyError):
			print('KeyError object: '+object.name) #custom properties
			MsgBox('Check custom properties on "' + object.name + '" object.', "KeyError", 'ERROR')

	for child in object.children:
		forChild(child,False,file)
	if (not root):
		if object['block_type'] != 444:
			file.write(struct.pack("<i",555)) #CloseCase

	#if (not root):
	#	if ( (type == 0) or (type == 5)):
	#		file.write(struct.pack("<i",555)) #CloseCase



