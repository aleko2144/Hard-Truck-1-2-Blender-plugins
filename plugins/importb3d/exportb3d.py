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

from bpy_extras.io_utils import (
		ImportHelper,
		ExportHelper,
		orientation_helper_factory,
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

scene = bpy.context.scene
RoMesh = True

def openclose(file):
	oc = file.read(4)	
	if (oc == (b'\x4D\x01\x00\x00')):
		return 2
	elif oc == (b'\x2B\x02\x00\x00'):
		# print('}')
		return 0
	elif oc == (b'\xbc\x01\x00\x00'):
		#print('BC01')
		return 3
	elif oc == (b'\xde\x00\00\00'):
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
	file = open(myFile+'.b3d','wb')

	global global_matrix
	global_matrix = axis_conversion(to_forward="-Z",
										to_up="Y",
										).to_4x4() * Matrix.Scale(1, 4)
										
	global generatePro
	generatePro = generate_pro_file
	
	global verNums
	verNums = []
	
	file.write(b'B3D\x00')#struct.pack("4c",b'B',b'3',b'D',b'\x00'))
	#ba = bytearray(b'\x00' * 20)
	
	#file.write(ba)
	
	file.write(struct.pack('<i',0))
	
	file.write(struct.pack('<i',6))
	
	materials = []
	
	for material in bpy.data.materials:
		materials.append(material.name)
		
	file.write(struct.pack('<i',len(materials)*8 + 1))
		
	file.write(struct.pack('<i',len(materials)* 8 + 1 + 6))
	
	file.write(struct.pack('<i',0))
	
	file.write(struct.pack('<i',len(materials)))

	for i in range(len(materials)):
		file.write(str.encode(materials[i]))#+ bytearray(b'\x00' * (32-len(img))))
		imgNone = 32-len(materials[i])
		ba = bytearray(b'\x00'* imgNone)
		file.write(ba)
		
	file.write(struct.pack("<i",111))
	clone_node()
	forChild(bpy.data.objects['b3d_temporary'],True, file)
	delete_clone()
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
			
	file.write(struct.pack("<i",555))

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
		
		
		
