import struct
import sys
import timeit
import threading
import pdb

import bpy
import mathutils
import os.path
from bpy.props import *
from bpy_extras.image_utils import load_image
from ast import literal_eval as make_tuple

from math import sqrt
from math import atan2

import re

import bmesh

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
		print('brackets error: pos={} oc={}'.format(file.tell(), oc))
		#sys.exit()
		raise Exception()

def onebyte(file):
	return (file.read(1))

def readName(file):
	objName = file.read(32)
	if (objName[0] == 0):
		objName = "empty name"
		#objname = "Untitled_0x" + str(hex(file.tell()-36))
	else:
		objName = (objName.decode("cp1251").rstrip('\0'))
	return objName
	
	
		
class type05:
	name_fmt = '32c'
	byte1 = 'c'
	byte3 = '3c'
	def __init__(self,file):
		self.name = file.read(struct.calcsize(self.name_fmt)).decode("utf-8")
		_s = file.read(struct.calcsize(self.byte1))
		self.byte1 = struct.unpack(self.byte1,_s)
		_s = file.read(struct.calcsize(self.byte3))
		self.byte3 = struct.unpack(self.byte3,_s)
		
class type15:
	byte1 = 'c'
	byte1_2 = 'c'
	byte4 = '4c'
	byte3 = '3c'
	def __init__(self,file):
		self.byte1 = onebyte(file)					
		file.seek(3,1)								#
		
		_s = file.read(struct.calcsize(self.byte4))	#
		self.byte4 = struct.unpack(self.byte4,_s)
		
		self.byte1_2 = onebyte(file)				# кол-во вложеных обьектов 25
		
		_s = file.read(struct.calcsize(self.byte3))
		self.byte3 = struct.unpack(self.byte3,_s)
				

class coords3:
	def __init__(self, file):
		self.v = struct.unpack("<3f", file.read(12))

class quat:
	fmt = 'ffff'

	def __init__(self, file):
		_s = file.read(struct.calcsize(self.fmt))
		self.v = struct.unpack(self.fmt, _s)
		# Quats are stored x,y,z,w - this fixes it
		self.v = [self.v[-1], self.v[0], self.v[1], self.v[2]]
								
def Triangulate(faces):
	print('faces: '+str(faces))
	faces_new = []
	for t in range(len(faces)-2):
		faces_new.extend([faces[t],faces[t+1],faces[t+2]])
		# if t%2 ==0:
			# faces_new.extend([faces[t],faces[t+1],faces[t+2]])
		# else:
			# faces_new.extend([faces[t+2],faces[t+1],faces[t]])
			
			
			# if ((format == 0) or (format == 16) or (format == 1)):
				# faces_new.extend([faces[t+2],faces[t+1],faces[0]])
			# else:
				# faces_new.extend([faces[t+2],faces[t+1],faces[t]])
	print('faces new: '+str(faces_new))
	return faces_new

	
def MakePolyOk(faces):
	faces1 = []
	face = []
	for j in range(len(faces)):
		if (j%2 == 0):
			faces1.append(faces[j])
		else:
			face.append(faces[j])
			
	faces = face
	faces1.reverse()
	faces.extend(faces1)
	return faces

def parse_plm(input_file, color_format):
	with open (input_file,'r+b') as file:
		struct.unpack('<i',file.read(4))[0] #== 5065808:
		data_len = struct.unpack('<i',file.read(4))[0]
		
		
		##### PALT #####
		PALT = struct.unpack('<i',file.read(4))[0]
		#if PALT == 1414283600:
			#print("PALT")
		#else:
			#print("something went wrong")
		#	sys.exit()
			
		PALT_len = struct.unpack('<i',file.read(4))[0]
		
		colors_list = []
		
		for i in range(PALT_len):
			#print("COLOR " + str(i))
			R = 0
			G = 0
			B = 0
			
			R_dat = struct.unpack('<b',file.read(1))[0]
			if (R_dat <= 1):
				R = 255 + R_dat
			else:
				R = R_dat
			G_dat = struct.unpack('<b',file.read(1))[0]
			if (G_dat <= -1):
				G = 255 + G_dat
			else:
				G = G_dat
			B_dat = struct.unpack('<b',file.read(1))[0]
			if (B_dat <= -1):
				B = 255 + B_dat
			else:
				B = B_dat
			#print("R: " + str(R) + "G: " + str(G) + "B: " + str(B))
			#print("R: " + str(R_dat) + "G: " + str(G_dat) + "B: " + str(B_dat))
			#print("")
			
			col_1 = 0
			col_2 = 0
			col_3 = 0
			
			if (color_format[0] == "R"):
				col_1 = R
			elif (color_format[0] == "G"):
				col_1 = G
			elif (color_format[0] == "B"):
				col_1 = B
				
			if (color_format[1] == "R"):
				col_2 = R
			elif (color_format[1] == "G"):
				col_2 = G
			elif (color_format[1] == "B"):
				col_2 = B
				
			if (color_format[2] == "R"):
				col_3 = R
			elif (color_format[2] == "G"):
				col_3 = G
			elif (color_format[2] == "B"):
				col_3 = B
				
			colors_list.append( (col_1, col_2, col_3) )
		
		return colors_list
						
def parse_pro(input_file, colors_list):
	with open (input_file,'r') as file:
		#read all lines first
		pro = file.readlines()
		file.close()
		# you may also want to remove whitespace characters like `\n` at the end of each line
		pro = [x.strip() for x in pro] 
		
		#print(pro)
		##### TEXTUREFILES #####
		texturefiles_index = pro.index([i for i in pro if "TEXTUREFILES" in i][0])
		texturefiles_num = int(re.search(r'\d+', pro[texturefiles_index]).group())
		texturefiles = []
		for i in range(texturefiles_num):
			texturefiles.append(pro[texturefiles_index + 1 + i].split(".")[0]) # так как texturefiles_index = номер строки, где написано "TEXTUREFILES", сами текстуры на одну строку ниже
																			   # split нужен для того, чтобы убрать всё, что после точки - например, ".txr noload"
		#print("len texfiles: " + str(len(texturefiles)))
		##### MATERIALS #####
		materials_index = pro.index([i for i in pro if "MATERIALS" in i][0])
		materials_num = int(re.search(r'\d+', pro[materials_index]).group())
		materials = []
		for i in range(materials_num):
			materials.append(pro[materials_index + 1 + i]) # тоже самое, так как materials_index = номер строки, где написано "MATERIALS", сами материалы на одну строку ниже
			
		##### Параметры материалов (col %d) #####
		material_colors = []
		
		for i in range(materials_num):
			colNum_str = str(re.findall(r'col\s+\d+', materials[i]))
			colNum = 0
			if (colNum_str != "[]"):
				colNum_final = str(re.findall(r'\d+', colNum_str[2:-2]))[2:-2]
				#print(texNum_final)
				colNum = int(colNum_final) #[5:-2] нужно чтобы убрать ['tex и '], например: ['tex 10'] -> 10
				material_colors.append(str(colors_list[colNum]))
			else:
				material_colors.append("[]")
			
			
		##### Параметры материалов (tex %d) #####
		material_textures = []
		
		for i in range(materials_num):
			texNum_str = str(re.findall(r't\wx\s+\d+', materials[i])) # t\wx - так как помимо tex, ещё бывает ttx
			texNum = 0
			if (texNum_str != "[]"):
				texNum_final = str(re.findall(r'\d+', texNum_str[2:-2]))[2:-2]
				#print(texNum_final)
				texNum = int(texNum_final) #[5:-2] нужно чтобы убрать ['tex и '], например: ['tex 10'] -> 10
				material_textures.append(texturefiles[texNum-1])
			else:
				material_textures.append(material_colors[i])
				
		#for k in range(materials_num):
		#	print(materials[k] + " ---> " + material_textures[k])
		
		return material_textures
		
def read(file, context, op, filepath, search_tex_names, textures_format, color_format, tex_path):
	if file.read(3) == b'b3d':
		print ("correct file");
	else:
		print ("b3d error")
		
	file.seek(21,1);
	Imgs = []
	math = []
	#texr = []
	
	if (search_tex_names == True):
		colors_list = parse_plm(file.name[:-3] + "plm", color_format)
		material_textures = parse_pro(file.name[:-3] + "pro", colors_list)
	#print(material_textures)
	
	for i in range(struct.unpack('<i',file.read(4))[0]):
		#Imgs.append(file.read(32).decode("utf-8").rstrip('\0'))
		
		SNImg = file.read(32).decode("utf-8").rstrip('\0') #читаю имя
		#PImg = (filepath.rsplit('\\',1)[0] +'\\txr\\' +SNImg+'.tga') #полный путь ####################################################### 
		
		if (search_tex_names == True):
			if (material_textures[i][0] == "("):
				PImg = (material_textures[i])
			elif (material_textures[i][0] == "["):
				PImg = ("(255, 255, 255)")
			else:
				PImg = (filepath.rsplit('\\',1)[0] + "\\" + material_textures[i] + "." + textures_format)
		else:
			PImg = (filepath.rsplit('\\',1)[0] +'\\txr\\' +SNImg + "." + textures_format)
		
		#print (PImg)
		
		if (search_tex_names == True):
			if os.path.isfile(PImg):
				img = bpy.data.images.load(PImg)
			else:
				img = bpy.data.images.new(SNImg,1,1)
				if (material_textures[i][0] == "("):
					PImg = (material_textures[i])
					R = (float((PImg[1:-1].split(", "))[0])) / 255
					G = (float((PImg[1:-1].split(", "))[1])) / 255
					B = (float((PImg[1:-1].split(", "))[2])) / 255
					img.pixels = (B, G, R, 1.0)
					img.filepath_raw = (filepath.rsplit('\\',1)[0] + tex_path + "\\" + SNImg + "." + textures_format)
					img.file_format = textures_format.upper()
					img.save()
				else:
					print ('no '+PImg+' image')
		else:
			if os.path.isfile(PImg):
				img = bpy.data.images.load(PImg)
			else:
				PImg = (filepath.rsplit('\\',1)[0] +'\\txr\\' +SNImg[4:]+'.tga') #полный путь
				if os.path.isfile(PImg):
					img = bpy.data.images.load(PImg)
				else:
					img = bpy.data.images.new(SNImg,1,1)
					print ('no '+PImg+' image')
			
			#print(img.pixels)
			#name="Untitled", width=1024, height=1024, color=(0.0, 0.0, 0.0, 1.0), alpha=True, generated_type='BLANK', float=False, gen_context='NONE', use_stereo_3d=False
			#print ('no '+PImg+' image')
			
			#print(PImg[1:-1].split(", "))
			
			#print(int((PImg[1:-1].split(", "))[0]))
			#print(int((PImg[1:-1].split(", "))[1]))
			#print(int((PImg[1:-1].split(", "))[2]))
			#if (search_tex_names == False):
			#	PImg = (filepath.rsplit('\\',1)[0] +'\\txr\\' +SNImg+'.tga') #полный путь #####################################################################
			#PImg = (filepath.rsplit('\\',1)[0] +'\\txr\\' +SNImg[4:]+'.tga')
			#?
			#if os.path.isfile(PImg):
			#	img = bpy.data.images.load(PImg)
			#else:
			#	img = bpy.data.images.new(SNImg,1,1)#bpy.data.images.new(SNImg,1,1)
			#	print ('no '+PImg+' image')
				#print ('no '+PImg+' image')
		Imgs.append(img)
		#print(Imgs)
		
		
		tex = bpy.data.textures.new(SNImg,'IMAGE') 
		tex.use_preview_alpha = True
		tex.image = img #bpy.data.images[i]
		mat = bpy.data.materials.new(SNImg)
		mat.texture_slots.add()
		mat.texture_slots[0].uv_layer = 'UVmap'
		mat.texture_slots[0].texture = tex
		mat.texture_slots[0].use_map_alpha = True
		math.append(mat)
		
		
	file.seek(4,1)		
	
	ex = 0
	i = 0
	lvl = 0
	cnt = 0
	coords25 = []
	coords23 = []
	vertexes = []
	normals = []
	format = 0
	#
	b3dObj = 0
	uv = []
	add_uv = []
	num_add_UV = 0
	test_verts_num = 0
	b3dObj = bpy.data.objects.new(os.path.basename(op.properties.filepath),None)
	context.scene.objects.link(b3dObj)
	
	objString = [os.path.basename(op.properties.filepath)]
	
	while ex!=1:


		#if (file.tell()>23281193):
		#	break
		
		ex = openclose(file)
		if ex == 0:
			#print('-')
			del objString[-1]
			#objString = objString[:-1]
			lvl-=1
			#print((objString))
			#print('eob')
			#continue
		elif ex == 1: 
			print(str(cnt))
			file.close()
			break

		elif ex == 3:
			continue
		elif ex == 2:
			#print ('+')
			lvl+=1
			objName = readName(file)
			type = 	struct.unpack("<i",file.read(4))[0]
			#print (str(type))
			print(objName + ", type: " + str(type) + ", pos: " + str(file.tell()))
			if (type == 0):
				qu = quat(file).v
				objString.append(os.path.basename(op.properties.filepath))
				ff = file.seek(28,1)
			
			elif (type == 1):
				cnt+=1
				#b3dObj.append(
				b3dObj = bpy.data.objects.new(objName, None)
				b3dObj['block_type'] = 1
				b3dObj.parent = context.scene.objects[objString[-1]]
				context.scene.objects.link(b3dObj)
				objString.append(context.scene.objects[0].name)
				#b3dObj.hide = True				

				b3dObj['2 name'] = file.read(32).decode("cp1251").rstrip('\0')
				b3dObj['3 name'] = file.read(32).decode("cp1251").rstrip('\0')
				b3dObj['pos'] = str(file.tell())

			elif (type == 2):	#контейнер хз
				cnt+=1
				#b3dObj.append(
				b3dObj = bpy.data.objects.new(objName, None)
				b3dObj['block_type'] = 2
				b3dObj['pos'] = str(file.tell())
				b3dObj.parent = context.scene.objects[objString[-1]]
				context.scene.objects.link(b3dObj)
				objString.append(context.scene.objects[0].name)
				#b3dObj.hide = True				
				
				qu = quat(file).v
				struct.unpack("<4fi",file.read(20))
			elif (type == 3):	#
				cnt+=1
				#b3dObj.append(
				b3dObj = bpy.data.objects.new(objName, None)
				b3dObj['block_type'] = 3
				b3dObj['pos'] = str(file.tell())
				b3dObj.parent = context.scene.objects[objString[-1]]
				context.scene.objects.link(b3dObj)
				objString.append(context.scene.objects[0].name)
				#b3dObj.hide = True				
				
				qu = quat(file).v
				struct.unpack("<i",file.read(4))
			elif (type == 4):	#похоже на контейнер 05 совмещенный с 12
				cnt+=1
				b3dObj = bpy.data.objects.new(objName, None)
				b3dObj['block_type'] = 4
				b3dObj['pos'] = str(file.tell())
				b3dObj.parent = context.scene.objects[objString[-1]]
				context.scene.objects.link(b3dObj)
				
				objString.append(context.scene.objects[0].name)
				#b3dObj.hide = True				
				
				qu = quat(file).v
				str(file.read(32).decode("utf-8")).rstrip('\0')
				struct.unpack("<i7fi",file.read(36))
				
				
			elif (type==5): #общий контейнер
				#object = type05(file)
				cnt+=1
				
				b3dObj = bpy.data.objects.new(objName, None)		

				b3dObj['block_type'] = 5
				b3dObj['pos'] = str(file.tell())
				b3dObj['node_x'] = struct.unpack("<f",file.read(4))[0]
				b3dObj['node_y'] = struct.unpack("<f",file.read(4))[0]
				b3dObj['node_z'] = struct.unpack("<f",file.read(4))[0]
				b3dObj['node_radius'] = struct.unpack("<f",file.read(4))[0]
				b3dObj['add_name'] = readName(file)
				b3dObj.parent = context.scene.objects[objString[-1]]
				context.scene.objects.link(b3dObj)
				objString.append(context.scene.objects[0].name)
				file.seek(4,1)
				#b3dObj.hide = True	
				
			elif (type == 6):	
				vertexes = []
				uv = []

				cnt+=1
				b3dObj = bpy.data.objects.new(objName, None)
				b3dObj['block_type'] = 6
				b3dObj['pos'] = str(file.tell())
				b3dObj.parent = context.scene.objects[objString[-1]]
				context.scene.objects.link(b3dObj)
				
				objString.append(context.scene.objects[0].name)
				#b3dObj.hide = True				
				
				qu = quat(file).v
				readName(file)
				readName(file)
				num = struct.unpack("<i",file.read(4))[0]
				for i in range (num):
					vertexes.append(struct.unpack("<3f",file.read(12)))
					uv.append(struct.unpack("<2f",file.read(8)))
				struct.unpack("<i",file.read(4))[0]

			elif (type == 7):	#25? xyzuv TailLight? похоже на "хвост" движения	mesh
				format = 0;
				coords25 = []
				vertexes = []
				uv = []
				cnt+=1
				b3dObj = bpy.data.objects.new(objName, None)
				b3dObj['block_type'] = 7
				b3dObj.parent = context.scene.objects[objString[-1]]
				#b3dObj.hide = True				

					
				qu = quat(file).v
				str(struct.unpack("<8f",file.read(32))) #0-0
				
				
				num = struct.unpack("<i",file.read(4))[0]
				for i in range(num):
					vertexes.append(struct.unpack("<3f",file.read(12)))
					uv.append(struct.unpack("<2f",file.read(8))) #((struct.unpack("<f",file.read(4))[0], 1 - struct.unpack("<f",file.read(4))[0]))
					#str(struct.unpack("<5f",file.read(20)))
				str(struct.unpack("<i",file.read(4))[0])
				
				context.scene.objects.link(b3dObj)
				objString.append(context.scene.objects[0].name)
				
			elif (type == 8):	#тоже фейсы		face
				faces = []
				faces_all = []
				uvs = []
				add_uvs = []
				texnum = 0
				cnt+=1
				b3dMesh = (bpy.data.meshes.new(objName))
				b3dObj=bpy.data.objects.new(objName, b3dMesh)
				b3dObj['block_type'] = '8'
				b3dObj['pos'] = str(file.tell())
				b3dObj.parent = context.scene.objects[objString[-1]]
				
				#b3dObj.hide = True	
				qu = coords3(file).v
				
				#b3dObj.location = qu
				file.read(4)
				num = struct.unpack("<i",file.read(4))[0]
				
				###
				for i in range(num_add_UV):
					#инициализация массива дополнительных развёрток
					add_uvs_instance = []
					for j in range(num):
						add_uvs_instance.append((0.0, 0.0, 0.0))
						add_uvs.append(add_uvs_instance)
				########
				
				for i in range(num):
					faces = []
					faces_new = []
					format = struct.unpack("<i",file.read(4))[0]
					
					struct.unpack("<fi",file.read(8))
					texnum = struct.unpack("i",file.read(4))[0]
					
					num1 = struct.unpack("<i",file.read(4))[0]
					
					if ((format == 178) or (format == 50)):
						for j in range(num1):
							faces.append(struct.unpack("<i",file.read(4))[0])							
							struct.unpack("<5f",file.read(20))
					elif ((format == 176) or (format == 48)or (format == 179)or (format == 51)):
						for j in range(num1):
							faces.append(struct.unpack("<i",file.read(4))[0])							
							struct.unpack("<3f",file.read(12))
					elif ((format == 3) or (format == 2) or (format == 131)):
						for j in range(num1):
							faces.append(struct.unpack("<i",file.read(4))[0])							
							struct.unpack("<2f",file.read(8))
					elif format == 177:
						for j in range(num1):
							faces.append(struct.unpack("<i",file.read(4))[0])							
							struct.unpack("<f",file.read(4))
					else:
						for j in range(num1):
							faces.append(struct.unpack("<i",file.read(4))[0])
						#print ('faces:	'+str(faces))
					for t in range(len(faces)-2):
						if t%2 ==0:
							faces_new.append([faces[t],faces[t+1],faces[t+2]])
						else:
							if ((format == 0) or (format == 16) or (format == 1)):
								faces_new.append([faces[t+2],faces[t+1],faces[0]])
							else:
								faces_new.append([faces[t+2],faces[t+1],faces[t]])
						uvs.append((uv[faces_new[t][0]],uv[faces_new[t][1]],uv[faces_new[t][2]]))
						
						for n in range(num_add_UV):	
							add_uvs[n][i] = ((add_uv[n][faces_new[t][0]],
											add_uv[n][faces_new[t][1]],
											add_uv[n][faces_new[t][2]]))
											
							#print("{} {} {} | {} {} {}".format( uv[faces_new[t][0]],
							#									uv[faces_new[t][1]],
							#									uv[faces_new[t][2]],
							#									add_uv[n][faces_new[t][0]],
							#									add_uv[n][faces_new[t][1]],
							#									add_uv[n][faces_new[t][2]]))
							
					faces_all.extend(faces_new)
					#print(str(faces_all))
				#pdb.set_trace()
				Ev = threading.Event()
				Tr = threading.Thread(target=b3dMesh.from_pydata, args = (vertexes,[],faces_all))
				Tr.start()
				Ev.set()
				Tr.join()

				
				uvMesh = b3dMesh.uv_textures.new()
				#imgMesh = math[texnum].texture_slots[0].texture.image.size[0]
				uvMesh.name = 'default'
				uvLoop = b3dMesh.uv_layers[0]
				uvsMesh = []
				
				#print('uvs:	',str(uvs))
				for i, texpoly in enumerate(uvMesh.data):
					#texpoly.image = Imgs[texnum]
					poly = b3dMesh.polygons[i]
					for j,k in enumerate(poly.loop_indices):
						uvsMesh = [uvs[i][j][0],1 - uvs[i][j][1]]
						uvLoop.data[k].uv = uvsMesh
						
				#mat = b3dMesh.materials.append(math[texnum])
				
				context.scene.objects.link(b3dObj)
				objString.append(context.scene.objects[0].name)
				
				#второй и последующие слои UV
				
				"""
				print(add_uvs)
				print(uvs)
				
				for n in range(num_add_UV):
					uvMesh = b3dMesh.uv_textures.new()
					uvMesh.name = 'default' + str(n + 1)
					uvLoop = b3dMesh.uv_layers[n + 1]
					uvsMesh = []

					for i, texpoly in enumerate(uvMesh.data):
						poly = b3dMesh.polygons[i]
						for j,k in enumerate(poly.loop_indices):
							uvsMesh = [add_uvs[n][i][j][0], 1 - add_uvs[n][i][j][1]]
							uvLoop.data[k].uv = uvsMesh
				"""
				
			elif (type == 9):
				cnt+=1
				b3dObj = bpy.data.objects.new(objName, None)
				b3dObj['block_type'] = 9
				b3dObj['pos'] = str(file.tell())
				b3dObj.parent = context.scene.objects[objString[-1]]
				context.scene.objects.link(b3dObj)
				objString.append(context.scene.objects[0].name)
				#b3dObj.hide = True				
				

				qu = quat(file).v
				str(quat(file).v)
				#print
				file.seek(4,1)
			elif (type == 10): #контейнер, хз о чем
				
				cnt+=1
				b3dObj = bpy.data.objects.new(objName, None)
				b3dObj['block_type'] = 10
				b3dObj['pos'] = str(file.tell())
				b3dObj.parent = context.scene.objects[objString[-1]]
				context.scene.objects.link(b3dObj)
				objString.append(context.scene.objects[0].name)
				#b3dObj.hide = True				
				
				qu = quat(file).v
				quat(file)
				(onebyte(file))
				file.seek(3,1)

			elif (type == 11):
				cnt+=1
				b3dObj = bpy.data.objects.new(objName, None)
				b3dObj['block_type'] = 11
				b3dObj['pos'] = str(file.tell())
				b3dObj.parent = context.scene.objects[objString[-1]]
				context.scene.objects.link(b3dObj)
				objString.append(context.scene.objects[0].name)

				qu = quat(file).v
				#printwrite(writefile,tab1+'block 11 XYZW:	'+str(qu))
				file.seek(32,1)
				#printwrite(writefile,tab1+str(struct.unpack("<8f",file.read(32))))
				file.seek(4,1)
				#printwrite(writefile, tab1+'child:	'+str(struct.unpack("<i",file.read(4))[0]))

			elif (type == 12):
				cnt+=1
				b3dObj = bpy.data.objects.new(objName, None)
				b3dObj['block_type'] = 12
				b3dObj['pos'] = str(file.tell())
				b3dObj.parent = context.scene.objects[objString[-1]]
				context.scene.objects.link(b3dObj)
				objString.append(context.scene.objects[0].name)
				#b3dObj.hide = True				

				qu = quat(file).v
				file.read(28)
	
			elif (type == 13):
				cnt+=1
				b3dObj = bpy.data.objects.new(objName, None)
				b3dObj['block_type'] = 13
				b3dObj['pos'] = str(file.tell())
				b3dObj.parent = context.scene.objects[objString[-1]]
				context.scene.objects.link(b3dObj)
				objString.append(context.scene.objects[0].name)
				#b3dObj.hide = True				

			
				qu = quat(file).v
				num = []
				coords = []
				num = struct.unpack("3i",file.read(12))
				#printwrite(writefile,tab1+str(num))
				for i in range(num[-1]):
					coords.append(struct.unpack("f",file.read(4))[0])
				if num[-1]>0:
					pass
					#printwrite(writefile,tab1+'0d Coords:	'+str(coords))
					
			elif (type == 14): #sell_ ? 
				
				#cnt+=1
				#b3dObj = bpy.data.objects.new(objName, None)
				#b3dObj['block_type'] = 14
				#b3dObj['pos'] = str(file.tell())
				#b3dObj.parent = context.scene.objects[objString[-1]]
				#context.scene.objects.link(b3dObj)
				#objString.append(context.scene.objects[0].name)
				#b3dObj.hide = True				

				#qu = quat(file).v				
				#file.seek(24, 1)
				#var = struct.unpack("<i",file.read(4))[0]
				#print(str(file.tell()))
				#if var !=0:
				#	file.seek(len(objName), 1)
					#file.seek(4, 1)
				
				#file.seek(17,1)
				#file.seek(11,1)#0-0
				
				cnt+=1
				b3dObj = bpy.data.objects.new(objName, None)
				b3dObj['block_type'] = 14
				b3dObj['pos'] = str(file.tell())
				b3dObj.parent = context.scene.objects[objString[-1]]
				context.scene.objects.link(b3dObj)
				objString.append(context.scene.objects[0].name)
				
				qu = quat(file).v
				quat(file).v
				#printwrite(writefile,tab1+'XYZW:	'+str(qu))
				#printwrite(writefile,tab1+'XYZW:	'+ str(quat(file).v))
				some_var = struct.unpack("<i",file.read(4))[0]
				var0 = struct.unpack("<i",file.read(4))[0]
				var1 = struct.unpack("<i",file.read(4))[0]
				#printwrite(writefile,tab1+'some_var: {}'.format(some_var))
				#printwrite(writefile,tab1+'var0: {}'.format(var0))
				#printwrite(writefile,tab1+'var1: {}'.format(var1))
				if (some_var > 99):
					file.seek(-48, 1) #назад к самому началу блока
					file.seek(-32, 1) #char name[32]
					name = ""
					byte = file.read(1)
					if byte != b'\x00':
						file.seek(-1,1)
						name = str(file.read(32).decode("utf-8")).rstrip('\0')
					else:
						file.seek(31, 1)
						name = ""
					print(name)
					print(len(name))
					file.seek(48, 1) #в конец блока
					skip_len = 0
						
					if (len(name) > 15):
						skip_len = 20
						
					elif (11 < len(name) < 15 or len(name) == 15):
						skip_len = 16
						
					elif (7 < len(name) < 11 or len(name) == 11):
						skip_len = 12
						
					elif (3 < len(name) < 7 or len(name) == 7):
						skip_len = 8
							
					elif (len(name) < 3 or len(name) == 3):
						skip_len = 4
						
					file.seek(skip_len, 1)
				
				
			elif (type == 16):
				cnt+=1
				b3dObj = bpy.data.objects.new(objName, None)
				b3dObj['block_type'] = 16
				b3dObj['pos'] = str(file.tell())
				b3dObj.parent = context.scene.objects[objString[-1]]
				context.scene.objects.link(b3dObj)
				objString.append(context.scene.objects[0].name)
				#b3dObj.hide = True				

				qu = quat(file).v
				struct.unpack("11f",file.read(44))
			elif (type == 17):
				cnt+=1
				b3dObj = bpy.data.objects.new(objName, None)
				b3dObj['block_type'] = 17
				b3dObj['pos'] = str(file.tell())
				b3dObj.parent = context.scene.objects[objString[-1]]
				context.scene.objects.link(b3dObj)
				objString.append(context.scene.objects[0].name)
				#b3dObj.hide = True				

				qu = quat(file).v
				struct.unpack("11f",file.read(44))
				
			elif (type == 18):	#контейнер "применить к"
				qu = quat(file).v
				
				cnt+=1
				b3dObj = bpy.data.objects.new(objName, None)
				b3dObj['block_type'] = 18
				b3dObj['pos'] = str(file.tell())
				b3dObj['space_name'] = file.read(32).decode("utf-8").rstrip('\0')
				b3dObj['add_name'] = file.read(32).decode("utf-8").rstrip('\0')
				b3dObj.parent = context.scene.objects[objString[-1]]
				context.scene.objects.link(b3dObj)
				objString.append(context.scene.objects[0].name)
				
				
			elif (type == 19):
				cnt+=1
				b3dObj = bpy.data.objects.new(objName, None)
				b3dObj['block_type'] = 19
				b3dObj['pos'] = str(file.tell())
				b3dObj.parent = context.scene.objects[objString[-1]]
				context.scene.objects.link(b3dObj)
				objString.append(context.scene.objects[0].name)
				#b3dObj.hide = True				
			
				num = []
				num.append(struct.unpack("i",file.read(4))[0])
				#printwrite(writefile,tab1+str(num))

	
			elif (type == 20):
				cnt+=1
				#b3dObj = bpy.data.objects.new(objName, None)
				#b3dObj['block_type'] = 20
				#b3dObj.parent = context.scene.objects[objString[-1]]
				#context.scene.objects.link(b3dObj)
				#objString.append(context.scene.objects[0].name)

				qu = quat(file).v
			
				verts_count = struct.unpack("i",file.read(4))[0]
				struct.unpack("f",file.read(4))
				struct.unpack("f",file.read(4))
				floatX = struct.unpack("i",file.read(4))[0]
				print("floatX: " + str(floatX))
				for i in range(floatX):
					struct.unpack("f",file.read(4))
				print(objName)
				coords = []
				for i in range (verts_count):
					coords.append(struct.unpack("fff",file.read(12)))
					#printwrite(writefile,tab1+str(coords))
				#for i in range (title[3]):
				#	coords1.append(struct.unpack("f",file.read(4))[0])
				curveData = bpy.data.curves.new('curve', type='CURVE')
				
				curveData.dimensions = '3D'
				curveData.resolution_u = 2

				# map coords to spline
				polyline = curveData.splines.new('POLY')
				polyline.points.add(len(coords)-1)
				for i, coord in enumerate(coords):
					x,y,z = coord
					polyline.points[i].co = (x, y, z, 1)

				# create Object
				b3dObj = bpy.data.objects.new(objName, curveData)
				curveData.bevel_depth = 0.01

				# attach to scene and validate context
				#scn = bpy.context.scene
				#scn.objects.link(curveOB)
				#scn.objects.active = curveOB
				
				
				b3dObj.location = (0,0,0)
				b3dObj['block_type'] = 20
				b3dObj['pos'] = str(file.tell())
				b3dObj.hide = True
				b3dObj.parent = context.scene.objects[objString[-1]]
				context.scene.objects.link(b3dObj)
				objString.append(context.scene.objects[0].name)
				
				#bpy.context.scene.objects.link(object)  

			
			elif (type == 21): #testkey??? 
				qu = quat(file).v
				
				cnt+=1
				b3dObj = bpy.data.objects.new(objName, None)
				b3dObj['block_type'] = 21
				b3dObj['pos'] = str(file.tell())
				b3dObj.parent = context.scene.objects[objString[-1]]
				context.scene.objects.link(b3dObj)
				objString.append(context.scene.objects[0].name)
				#b3dObj.hide = True				
				object = type15(file)
				


			elif (type == 23): #colision mesh
				
				cnt+=1
				b3dMesh = (bpy.data.meshes.new(objName))
				b3dObj = bpy.data.objects.new(objName, b3dMesh)
				b3dObj['block_type'] = 23
				b3dObj['pos'] = str(file.tell())
				b3dObj.parent = context.scene.objects[objString[-1]]
				b3dObj.hide = True
				context.scene.objects.link(b3dObj)
				objString.append(context.scene.objects[0].name)
				
				
				#qu = quat(file).v

				var1 = struct.unpack("<i",file.read(4))[0]
				b3dObj['CType'] = struct.unpack("<i",file.read(4))[0]
				var4 = struct.unpack("<i",file.read(4))[0]
				for i in range(var4):
					struct.unpack("<i",file.read(4))[0]

				vertsBlockNum = struct.unpack("<i",file.read(4))[0]
				num = 0
				faces = []
				vertexes = []
				for i in range(vertsBlockNum):
					vertsInBlock = struct.unpack("<i",file.read(4))[0]
					
					if (vertsInBlock == 3):
						faces.append([num+1,num+2,num+0])
						num+=3
					elif(vertsInBlock ==4):
						faces.append([num+1,num+2,num+0,num+2,num+3,num+1])
						num+=4
						
					#faces.append([num+0,num+1,num+2,num+3,num+1,num+0])	
						
					#if (vertsInBlock == 3):
					#	faces.append([num+0,num+1,num+2])
					#	num+=3
					#elif(vertsInBlock ==4):
					#	faces.append([num+0,num+1,num+2,num+3,num+2,num+0])
					#	num+=3
						
					#else:
					#	for j in range(vertsInBlock-2):
					#		faces.append([num+j+0,num+j+2,num+j+1])
					#		num+=vertsInBlock
						
					for j in range(vertsInBlock):
						vertexes.append(struct.unpack("<3f",file.read(12)))
						#face =  [i*j+0,i*j+1,i*j+2]

						
				#print('verts: '+str((vertexes)))
				#print('faces: '+str( (faces)))
				
				b3dMesh.from_pydata(vertexes,[],faces)

				#faces =  [(num+0,num+1,num+2), (5,6,2), (6,7,3), (4,0,7)]
				
				#coords23.append(num1)
				#faces = (coords23[i][5],coords23[i][9],coords23[i][13])
				
				
				# Ev = threading.Event()
				# Tr = threading.Thread(target=b3dMesh.from_pydata, args = (vertexes,[],faces))
				# Tr.start()
				# Ev.set()
				# Tr.join()
				
				
				# mesh = []
				# meshFaces = []
				# numCnt = 0
				
				# num = struct.unpack("<i",file.read(4))[0]
				# #print (str(num))
				# for i in range(num):
					# num1 = struct.unpack("<i",file.read(4))[0]
					# #print ('num1:	'+str(num1))
					# numCnt = numCnt + num1
					# #mesh = []
					# faces = []
					# for j in range(num1):
						# #print(str(file.tell()))
						# mesh.append(coords3(file).v)
						# faces.append(j)
					# meshFaces.append(faces)
				
			elif (type == 24): #настройки положения обьекта
				cnt+=1
				
				#qu = quat(file).v
				#objString.append(context.scene.objects[0].name)
				#file.seek(20,1)
				
				m11 = struct.unpack("<f",file.read(4))[0]
				m12 = struct.unpack("<f",file.read(4))[0]
				m13 = struct.unpack("<f",file.read(4))[0]

				m21 = struct.unpack("<f",file.read(4))[0]
				m22 = struct.unpack("<f",file.read(4))[0]
				m23 = struct.unpack("<f",file.read(4))[0]

				m31 = struct.unpack("<f",file.read(4))[0]
				m32 = struct.unpack("<f",file.read(4))[0]
				m33 = struct.unpack("<f",file.read(4))[0]
				
				sp_pos = struct.unpack("<fff",file.read(12))

				x_d = 0.0
				y_d = 0.0
				z_d = 0.0
				
				PI = 3.14159265358979;
				test_var = 0.0
				test_var = ((m33*m33) + (m31*m31))
				var_cy = sqrt(test_var)

				if (var_cy > 16*sys.float_info.epsilon):
					z_d = atan2(m12, m22)
					x_d = atan2(- m32, var_cy)
					y_d = atan2(m31, m33)
				else:
					z_d = atan2(- m21, m11)
					x_d = atan2(- m32, var_cy)
					y_d = 0;
				
				rot_x = ((x_d * 180) / PI)
				rot_y = ((y_d * 180) / PI)
				rot_z = ((z_d * 180) / PI)


				
				#bpy.ops.mesh.primitive_ico_sphere_add(size=0.05, calc_uvs=True, location=sp_pos)
				b3dObj = bpy.data.objects.new(objName, None)
				#b3dObj = bpy.context.selected_objects[0]
				#b3dObj.name = objName
				b3dObj['block_type'] = 24
				b3dObj.rotation_euler[0] = x_d
				b3dObj.rotation_euler[1] = y_d
				b3dObj.rotation_euler[2] = z_d
				b3dObj.location = sp_pos
				
				#b3dObj['rotation_euler0'] = rot_x
				#b3dObj['rotation_euler1'] = rot_y
				#b3dObj['rotation_euler2'] = rot_z
				
				#bpy.ops.object.select_all(action='DESELECT')
				flag = struct.unpack("<i",file.read(4))[0]
				b3dObj['flag'] = flag
				file.seek(4,1)#01 00 00 00
				
				b3dObj.parent = context.scene.objects[objString[-1]]
				context.scene.objects.link(b3dObj)
				objString.append(context.scene.objects[0].name)
				
			elif (type == 25): #copSiren????/ контейнер
				
				cnt+=1
				b3dObj = bpy.data.objects.new(objName, None)
				b3dObj['block_type'] = 25
				b3dObj['pos'] = str(file.tell())
				b3dObj.parent = context.scene.objects[objString[-1]]
				context.scene.objects.link(b3dObj)
				objString.append(context.scene.objects[0].name)
				#b3dObj.hide = True				
			
				qu = coords3(file).v
				file.seek(32,1)
				ff = file.read(4)
				for i in range(10):
					file.seek(4,1)
			elif (type == 27): 
				
				cnt+=1
				b3dObj = bpy.data.objects.new(objName, None)
				b3dObj['block_type'] = 27
				b3dObj['pos'] = str(file.tell())
				b3dObj.parent = context.scene.objects[objString[-1]]
				context.scene.objects.link(b3dObj)
				objString.append(context.scene.objects[0].name)
				file.seek(36, 1)
				
			elif (type == 28): #face
				
				cnt+=1
				b3dMesh = (bpy.data.meshes.new(objName))
				#print('cnt:	'+str(cnt))
				b3dObj = bpy.data.objects.new(objName, b3dMesh)
				b3dObj['block_type'] = 28
				b3dObj['pos'] = str(file.tell())
				
				b3dObj.parent = context.scene.objects[objString[-1]]
				
				#b3dObj.hide = True				
				coords = []
				
				qu = quat(file).v
				file.seek(12,1)
				
				num = struct.unpack("<i",file.read(4))[0]
				
				for i in range(num):
					type = struct.unpack("i",file.read(4))[0]
					file.seek(12,1)
					vert_num = struct.unpack("i", file.read(4))[0]
					for k in range(vert_num):
						if (type == 0) :
							file.seek(8, 1) #x,y
						if type==256 or type == 1 or type == 2:
							file.seek(16,1) #x,y,u,v
						if type == -256:
							file.seek(8, 1) #x,y
			
				#for i in range(num):
				#	num1 = struct.unpack("i",file.read(4))[0]
				#	coords.extend(struct.unpack("f3i",file.read(16)))
				#	if (num1 == 2):
				#		coords.extend(struct.unpack('{}f'.format(coords[-1]*4),file.read(4*4*coords[-1])))

				#print(str(coords))
				# if num == 1:
					# coords.extend(struct.unpack("if3i",file.read(20)))
					# if (coords[0]>1):
						# for i in range(coords[4]):
							# coords.extend(struct.unpack("<4f",file.read(16)))
					# else:
						# coords.extend(struct.unpack("<8f",file.read(32)))

				# elif num ==2:
					# coords.extend(struct.unpack("if3i",file.read(20)))
					# for i in range(num*2):
						# coords.extend(struct.unpack("<7f",file.read(28)))
					# coords.extend(struct.unpack("<f",file.read(4)))
					
				# elif ((num == 10) or(num == 6)) : #db1
					# for i in range(num):
						# coords.extend(struct.unpack("if3i",file.read(20)))	
						# num1 = coords[-1]
						# for i in range (num1):
							# coords.append(struct.unpack("<2f",file.read(8)))
				# #b3dMesh.from_pydata(vertexes,[],faces)
				
				context.scene.objects.link(b3dObj) #добавляем в сцену обьект
				objString.append(context.scene.objects[0].name)
				
			elif (type == 29):	
				#cnt+=1
				#b3dObj = bpy.data.objects.new(objName, None)
				#b3dObj['block_type'] = 29
				#b3dObj['pos'] = str(file.tell())
				#b3dObj.parent = context.scene.objects[objString[-1]]
				##b3dObj.hide = True				
				#context.scene.objects.link(b3dObj)
				#objString.append(context.scene.objects[0].name)
				
				#qu = quat(file).v
				##num0 = struct.unpack("<i",file.read(4))[0]
				##struct.unpack("<i",file.read(4))[0]
				##struct.unpack("<7f",file.read(28))
				##if num0 == 4:
				##	struct.unpack("<f",file.read(4))[0]
				##elif num0 == 3:
				##	pass
				##struct.unpack("<i",file.read(4))[0]
				
				##дб1
				
				
				##дб2
				##struct.unpack("<i",file.read(4))[0]
				##struct.unpack("<i",file.read(4))[0]
				##struct.unpack("<fff",file.read(12))
				##struct.unpack("<fff",file.read(12))
				##struct.unpack("<i",file.read(4))[0]
				
				##struct.unpack("<i",file.read(4))[0]
				
				#num0 = struct.unpack("<i",file.read(4))[0]
				#num1 = struct.unpack("<i",file.read(4))[0]
				#struct.unpack("<fff",file.read(12))
				#struct.unpack("<fff",file.read(12))
				
				#struct.unpack("<f",file.read(4))[0]
				
				#if (num0 != 3):
				#	struct.unpack("<f",file.read(4))[0]
					
				#struct.unpack("<i",file.read(4))[0]
				
				cnt+=1
				b3dObj = bpy.data.objects.new(objName, None)
				b3dObj['block_type'] = 29
				b3dObj['pos'] = str(file.tell())
				b3dObj.parent = context.scene.objects[objString[-1]]		
				context.scene.objects.link(b3dObj)
				objString.append(context.scene.objects[0].name)
				
				qu = quat(file).v
				num0 = struct.unpack("<i",file.read(4))[0]
				num1 = struct.unpack("<i",file.read(4))[0]
					
				struct.unpack("<fff",file.read(12))
				struct.unpack("<fff",file.read(12))
					
				for i in range(num0 - 2):
					#add_float = struct.unpack("<f",file.read(4))[0]
					file.seek(4, 1)
						
					
				struct.unpack("<i",file.read(4))[0]
				
				
			elif (type == 30):	
				cnt+=1
				b3dObj = bpy.data.objects.new(objName, None)
				b3dObj['block_type'] = 30
				b3dObj['pos'] = str(file.tell())
				b3dObj.parent = context.scene.objects[objString[-1]]
				#b3dObj.hide = True				
				context.scene.objects.link(b3dObj)
				objString.append(context.scene.objects[0].name)

				qu = quat(file).v
				file.read(32)
				
				file.read(24)
			elif (type == 31):	
				cnt+=1
				b3dObj = bpy.data.objects.new(objName, None)
				b3dObj['block_type'] = 31
				b3dObj['pos'] = str(file.tell())
				b3dObj.parent = context.scene.objects[objString[-1]]
				#b3dObj.hide = True				
				context.scene.objects.link(b3dObj)
				objString.append(context.scene.objects[0].name)

				qu = quat(file).v
				num = struct.unpack("<i",file.read(4))[0]
				struct.unpack("<4f",file.read(16))
				struct.unpack("<i3f",file.read(16))
				for i in range(num):
					struct.unpack("<fi",file.read(8))

				
			elif (type == 33): #lamp
				
				cnt+=1
				b3dObj = bpy.data.objects.new(objName, None)
				b3dObj['block_type'] = 33
				b3dObj['pos'] = str(file.tell())
				b3dObj.parent = context.scene.objects[objString[-1]]
				#b3dObj.hide = True				
				context.scene.objects.link(b3dObj)
				objString.append(context.scene.objects[0].name)
				qu = quat(file).v
				#ff = file.read(4)
				#for i in range(18):
				#	file.seek(4,1)
				
				file.seek(4,1)
				b3dObj['light_type'] = struct.unpack("<i",file.read(4))[0]
				file.seek(4,1)
				#b3dObj.location = struct.unpack("<3f",file.read(12))
				file.seek(12, 1)
				file.seek(4,1)
				file.seek(4,1)
				file.seek(4,1)
				file.seek(4,1)#global_light_state
				file.seek(4,1)
				b3dObj['light_radius'] = struct.unpack("<f",file.read(4))[0]
				b3dObj['intensity'] = struct.unpack("<f",file.read(4))[0]
				file.seek(4,1)
				file.seek(4,1)
				b3dObj['R'] = struct.unpack("<f",file.read(4))[0]
				b3dObj['G'] = struct.unpack("<f",file.read(4))[0]
				b3dObj['B'] = struct.unpack("<f",file.read(4))[0]
				file.seek(4,1)
					
			elif (type == 34): #lamp
				num = 0
				cnt+=1
				b3dObj = bpy.data.objects.new(objName, None)
				b3dObj['block_type'] = 34
				b3dObj['pos'] = str(file.tell())
				b3dObj.parent = context.scene.objects[objString[-1]]
				#b3dObj.hide = True				
				context.scene.objects.link(b3dObj)
				objString.append(context.scene.objects[0].name)
				
				qu = quat(file).v
				ff = file.read(4)
				num = struct.unpack("<i",file.read(4))[0]
				for i in range(num):
					file.seek(16,1)
			elif (type == 35): #mesh
				coords23 = []
				
				cnt+=1
				b3dMesh = (bpy.data.meshes.new(objName))
				#print('cnt:	'+str(cnt))
				b3dObj = bpy.data.objects.new(objName, b3dMesh)
				#b3dObj['block_type'] = 35
				
				b3dObj.parent = context.scene.objects[objString[-1]]
				
				#b3dObj.hide = True				
				qu = quat(file).v
				faces = []
				num0 = struct.unpack("<i",file.read(4))[0]
				texNum = struct.unpack("<i",file.read(4))[0]
				num = struct.unpack("<i",file.read(4))[0]
				uvs = []
				add_uvs = []
				for i in range(num_add_UV):
					#инициализация массива дополнительных развёрток
					add_uvs_instance = []
					for j in range(num):
						add_uvs_instance.append((0.0, 0.0, 0.0))
						add_uvs.append(add_uvs_instance)
				########

				########
				faces1 = []
				
				#print (str(file.tell()))
				if num0<3:
					for i in range(num):
						faces1 = []
						num1=[]
						#coords23.append(struct.unpack("<i",file.read(4)))
						num1.append(struct.unpack("<i",file.read(4))[0])
						#print(str(file.tell()))
						if (num1[0] == 50):
							num1.extend(struct.unpack("<f4i5fi5fi5f",file.read(88)))
							coords23.append(num1)
							faces1 = (coords23[i][5],coords23[i][11],coords23[i][17])

						elif (num1[0] == 49):
							num1.extend(struct.unpack("<f3iififif",file.read(40)))
							coords23.append(num1)
							#print ('co23:	'+str(coords23))
							faces1 = (coords23[i][5],coords23[i][7],coords23[i][9])
						elif((num1[0] == 1) or (num1[0] == 0)):

							num1.extend(struct.unpack("<f6i",file.read(28)))
							coords23.append(num1)
							faces1 = coords23[i][5:8]
							#print('num1:	'+str(num1))
							# faces1 = coords23[i][4:7]
							# faces.append(faces1)
						elif ((num1[0] == 2) or (num1[0] == 3)):
							num1.extend(struct.unpack("<fiiiiffiffiff",file.read(52)))	
							coords23.append(num1)
							faces1=(coords23[i][5],coords23[i][8],coords23[i][11])
						else:
							num1.extend(struct.unpack("<f3iifffifffifff",file.read(64)))
							coords23.append(num1)
							faces1 = (coords23[i][5],coords23[i][9],coords23[i][13])
						#faces1 = faces1[0]
						faces.append(faces1)
						#faces1 = faces1[0]
						#uvs.append((coords25[faces1[0]][3:5] , coords25[faces1[1]][3:5] , coords25[faces1[2]][3:5]))
						#print ('faces	' + str(faces1)+'	'+str(uv))
						#print('f0:	'+str(faces1))
						#print(str(num1))
						#print(str(file.tell()))
						uvs.append((uv[faces1[0]],uv[faces1[1]],uv[faces1[2]]))
						
						for n in range(num_add_UV):	
							add_uvs[n][i] = ((add_uv[n][faces1[0]],
											add_uv[n][faces1[1]],
											add_uv[n][faces1[2]]))
						
				elif num0 == 3:
					#print(str(num))
					for i in range(num):
						#coords23.append([struct.unpack("<i",file.read(4))[0]])
						#file.read(4)
						#print(str(num)+'	'+str(i))
						coords23.append(struct.unpack("<if6i",file.read(32)))
						faces1 = coords23[i][5:8]
						faces.append(faces1)
						uvs.append((uv[faces1[0]],uv[faces1[1]],uv[faces1[2]]))
						#print (str(coords23))
						#print ('faces	' + str(faces1)+'	'+str(uv))
						
						for n in range(num_add_UV):	
							add_uvs[n][i] = ((add_uv[n][faces1[0]],
											add_uv[n][faces1[1]],
											add_uv[n][faces1[2]]))
						
				Ev = threading.Event()
				Tr = threading.Thread(target=b3dMesh.from_pydata, args = (vertexes,[],faces))
				Tr.start()
				Ev.set()
				Tr.join()
				
				#if ((format == 2) or (format == 515) or (format == 514) or (format == 258)):
					#i = 0
					#for i,vert in enumerate(b3dMesh.vertices):
						#vert.normal = normals[i]
						
						
				#uvMesh = b3dMesh.uv_textures.new()
				#b3dMesh.use_mirror_topology = True
				#imgMesh = math[coords23[i][3]].texture_slots[0].texture.image.size[0]
				#uvMesh.name = 'UVmap'
				#uvLoop = b3dMesh.uv_layers[0]
				#uvsMesh = []
				#print('uvs:	'+str(uvs))
				
				#uvMain = createTextureLayer("default", b3dMesh, uvs)
				
				uvMesh = b3dMesh.uv_textures.new()
				uvMesh.name = 'UVmap'
				uvLoop = b3dMesh.uv_layers[0]
				uvsMesh = []
				#первый слой UV
				for i, texpoly in enumerate(uvMesh.data):
					#print(str(i))
					poly = b3dMesh.polygons[i]
					#texpoly.image = Imgs[texNum]#coords23[i][3]]
					for j,k in enumerate(poly.loop_indices):
						uvsMesh = [uvs[i][j][0],1 - uvs[i][j][1]]
						uvLoop.data[k].uv = uvsMesh
				
				#b3dMesh.materials.append(math[texNum])#coords23[i][3]])
				
				
				b3dMesh.uv_textures['UVmap'].active = True
				b3dMesh.uv_textures['UVmap'].active_render = True



				context.scene.objects.link(b3dObj) #добавляем в сцену обьект
				
				#второй и последующие слои UV
				#print(add_uvs)
				
				for n in range(num_add_UV):
					uvMesh = b3dMesh.uv_textures.new()
					uvMesh.name = 'UVmap' + str(n + 1)
					uvLoop = b3dMesh.uv_layers[n + 1]
					uvsMesh = []

					for i, texpoly in enumerate(uvMesh.data):
						poly = b3dMesh.polygons[i]
						for j,k in enumerate(poly.loop_indices):
							#add_uv[n][i]
							uvsMesh = [add_uvs[n][i][j][0], 1 - add_uvs[n][i][j][1]]
							#uvsMesh = [add_uvs[n][i][j][0], 1 - add_uvs[n][i][j][1]]
							uvLoop.data[k].uv = uvsMesh
				

				b3dObj['MType'] = num0
				b3dObj['texNum'] = texNum
				b3dObj['FType'] = 0
				try:
					b3dObj['verts_format'] = b3dObj.parent['verts_format']
				except:
					b3dObj['verts_format'] = 2
				b3dObj['faces_container_type'] = 35
				b3dObj['pos'] = str(file.tell())
				b3dObj['block_type'] = b3dObj.parent['block_type']
				for face in b3dMesh.polygons:
					face.use_smooth = True
				objString.append(context.scene.objects[0].name)

			elif (type == 36):
				qu = quat(file).v
				coords25 = []
				vertexes = []
				normals =[]
				uv = []
				b3dObj['2 name'] = file.read(32).decode("cp1251").rstrip('\0')
				b3dObj['3 name'] = file.read(32).decode("cp1251").rstrip('\0')
				format = struct.unpack("<i",file.read(4))[0]
				iter = struct.unpack("<i",file.read(4))[0]
				if format == 0:
					objString.append(objString[-1])
					pass
				else:
					cnt+=1
					b3dObj = bpy.data.objects.new(objName, None)
					b3dObj['block_type'] = 36
					b3dObj['pos'] = str(file.tell())
					b3dObj.parent = context.scene.objects[objString[-1]]
					context.scene.objects.link(b3dObj)
					objString.append(context.scene.objects[0].name)
					##b3dObj.hide = True
					if format == 2:
						for i in range(iter):
							vertexes.append(struct.unpack("<3f",file.read(12)))
							uv.append(struct.unpack("<2f",file.read(8)))
							normals.append(struct.unpack("<3f",file.read(12)))
							#file.seek(12,1)
					elif format ==3:

						for i in range(iter):
							vertexes.append(struct.unpack("<3f",file.read(12)))
							uv.append(struct.unpack("<2f",file.read(8)))
							file.seek(4,1)
							
					elif ((format ==258) or (format ==515)):

						for i in range(iter):
							vertexes.append(struct.unpack("<3f",file.read(12)))
							uv.append(struct.unpack("<2f",file.read(8)))
							normals.append(struct.unpack("<3f",file.read(12)))
							file.seek(8,1)
					elif format ==514:
						for i in range(iter):
							vertexes.append(struct.unpack("<3f",file.read(12)))
							uv.append(struct.unpack("<2f",file.read(8)))
							normals.append(struct.unpack("<3f",file.read(12)))
							struct.unpack("<4f",file.read(16))
					#print(str(objName))
							
				file.seek(4,1)#01 00 00 00 subblocks count

			elif (type == 37):
				qu = coords3(file).v
				file.seek(4,1)
				coords25 = []
				vertexes = []
				normals = []
				uv = []
				add_uv = []
				
				test_verts_num = 0
				
				file.seek(32,1)
				#format = struct.unpack("<i",file.read(4))[0]
				
				##12.04.2022##
				verts_format = struct.unpack("<i",file.read(4))[0]
				file.seek(-4, 1)
				normals_format = struct.unpack_from("<B", file.read(1))[0] #первый байт - флаг "нормали/какой-то float"
				num_add_UV = struct.unpack_from("<B", file.read(1))[0]     #второй байт - флаг "количество дополнительных UV"
				file.seek(2, 1)                                            #третий и четвёртый байты вроде бы не используются
				##############
				
				iter = struct.unpack("<i",file.read(4))[0]
				
				#присвоение параметров объекту
				test_verts_num = iter
				b3dObj['verts_format'] = verts_format
				b3dObj['normals_format'] = normals_format
				b3dObj['num_add_UV'] = num_add_UV
				
				#### temp ####
				normals_str = ""
				uv_str = ""
					
				if normals_format == 1 or normals_format == 2:
					normals_str = "NX NY NZ"
				elif normals_format == 3:
					normals_str = "NX"

				for i in range(num_add_UV):
					uv_str += "UV{} ".format(i+2)
					#инициализация массива дополнительных развёрток
					add_uv_instance = []
					for j in range(iter):
						add_uv_instance.append((0.0, 0.0))
						add_uv.append(add_uv_instance)
				##############
					
				print("format={} | XYZ UV {} {}".format(verts_format, normals_str, uv_str))
				#print(add_uv)
				
				
				if verts_format == 0:
					objString.append(objString[-1])
					pass
				else:
					cnt+=1
					b3dObj = bpy.data.objects.new(objName, None)
					b3dObj['block_type'] = 37
					b3dObj['pos'] = str(file.tell())
					#b3dObj['SType'] = format
					b3dObj.parent = context.scene.objects[objString[-1]]
					#b3dObj.location = qu
					context.scene.objects.link(b3dObj)
					objString.append(context.scene.objects[0].name)
					##b3dObj.hide = True				
					
					for i in range(iter):
						#общее для всех вершин
						vertexes.append(struct.unpack("<3f",file.read(12)))
						uv.append(struct.unpack("<2f",file.read(8)))
						###
						if normals_format == 1 or normals_format == 2:
							normals.append(struct.unpack("<3f",file.read(12)))
						elif normals_format == 3:
							b3dObj['flt'] = struct.unpack("<f",file.read(4))[0]

						for j in range(num_add_UV):
							add_uv[j][i] = (struct.unpack("<2f",file.read(8)))
						###

					#print(str(objName))
							
				file.seek(4,1)#01 00 00 00 subblocks count
			elif (type == 39):
				cnt+=1
				b3dObj = bpy.data.objects.new(objName, None)
				b3dObj['block_type'] = 39
				b3dObj['pos'] = str(file.tell())
				b3dObj.parent = context.scene.objects[objString[-1]]
				context.scene.objects.link(b3dObj)
				objString.append(context.scene.objects[0].name)
				##b3dObj.hide = True				
			
				qu = quat(file).v
				quat(file)
				file.read(4)
				
				struct.unpack("<i",file.read(4))

			elif (type == 40):
				data = []
				data1 = []
				cnt+=1
				#objString.append(context.scene.objects[0].name)
				sp_pos = struct.unpack("<fff",file.read(12))	
				file.seek(4,1)				
				#bpy.ops.mesh.primitive_ico_sphere_add(size=0.05, calc_uvs=True, location=sp_pos)
				#b3dObj = bpy.context.selected_objects[0]
				b3dObj = bpy.data.objects.new(objName, None)	
				#b3dObj.name = objName
				b3dObj['block_type'] = 40
				b3dObj['pos'] = str(file.tell())
				b3dObj.parent = context.scene.objects[objString[-1]]
				objString.append(context.scene.objects[0].name)
				#bpy.ops.object.select_all(action='DESELECT')
				#b3dObj.hide = True				

				file.read(32)
				file.read(32)
				#file.read(52)
				data = struct.unpack("<3i",file.read(12))
				for i in range (data[-1]):
					data1.append(struct.unpack("f", file.read(4))[0])
				#print (str(data[-1])+'	'+str(data1))	
				
			#elif (type == 40):
			#	data = []
			#	data1 = []
			#	cnt+=1
			#	b3dObj = bpy.data.objects.new(objName, None)
			#	b3dObj['block_type'] = 40
			#	b3dObj.parent = context.scene.objects[objString[-1]]
			#	context.scene.objects.link(b3dObj)
			#	objString.append(context.scene.objects[0].name)
				#b3dObj.hide = True				

			#	qu = quat(file).v
			#	file.read(32)
			#	file.read(32)
				#file.read(52)
			#	data = struct.unpack("<3i",file.read(12))
			#	for i in range (data[-1]):
			#		data1.append(struct.unpack("f", file.read(4))[0])
				#print (str(data[-1])+'	'+str(data1))
			
			else:
				print(str(file.tell()))
				print ('smthng wrng')
				return
			#print(objName)
			
def readWayTxt(file, context, op, filepath):
	b3dObj = 0
	# b3dObj = bpy.data.objects.new(os.path.basename(op.properties.filepath),None)
	# context.scene.objects.link(b3dObj)
	
	# objString = [os.path.basename(op.properties.filepath)]
	
	type = None
	mnam_c = 0
	
	grom = 0
	rnod = 1
	rseg = 2
	mnam = 3
	mnam2nd = 4
	
	lineNum = 0 
	
	for line in file:
		if (type == grom):
			lineNum+=1
			if (lineNum == 2):
				#print (line.strip())	#GROM ROOM
				b3dObj = bpy.data.objects.new(line.strip(),None)
				b3dObj.parent = context.scene.objects[objString[-1]]
				context.scene.objects.link(b3dObj)
				objString.append(line.strip())
			elif (lineNum == 3):
				type = None			#GROM RESET
				lineNum = 0
		elif(type == rnod):
			lineNum+=1
			if (lineNum == 2):
				#print (line.strip())	#RNOD ROOM
				bpy.ops.mesh.primitive_ico_sphere_add(size=10, location=(0,0,0))
				b3dObj = bpy.context.object
				b3dObj.name = line.strip()
				b3dObj.parent = context.scene.objects[objString[-1]]
				objString.append(line.strip())
			elif (lineNum == 4):
				#print (line.strip())	#RNOD POS

				b3dObj.location = make_tuple(line.strip())#loc
			elif (lineNum == 5):
				type = None			#RNOD RESET
				lineNum = 0
				del objString[-1]
		elif(type == rseg):
			massline = 0
			lineNum+=1
			if (line[2:6]=='RTEN'):
				massline = 6
			else:
				massline = 4
			if (lineNum == massline):
				#print (line.strip())	#RSEG MASS
				
				b3dObj = bpy.data.objects.new('RSEG',None)				#
				b3dObj.parent = context.scene.objects[objString[-1]]	#
				objString.append(b3dObj.name)
				context.scene.objects.link(b3dObj)

				
				mass = make_tuple(line.strip())
				for pos in mass:
					bpy.ops.mesh.primitive_cylinder_add(radius = 1,location = pos)
					b3dObj = bpy.context.object
					b3dObj.name = 'location'
					b3dObj.parent = context.scene.objects[objString[-1]]
					#objString.append('RSEG')
				bpy.ops.curve.primitive_bezier_curve_add()
				b3dObj = bpy.context.object
				b3dObj.parent = context.scene.objects[objString[-1]]
				b3dObj.name = 'RSEGBezier'
				b3dObj.data.dimensions = '3D'
				b3dObj.data.fill_mode = 'FULL'
				b3dObj.data.bevel_depth = 0.1
				b3dObj.data.bevel_resolution = 4
				
				flatten = lambda mass: [item for sublist in mass for item in sublist]
				b3dObj.data.splines[0].bezier_points.add(len(mass)-2)
				b3dObj.data.splines[0].bezier_points.foreach_set("co",flatten(mass))
				
				points = b3dObj.data.splines[0].bezier_points
				
				for i,point in enumerate(points):
					point.handle_left_type = point.handle_right_type = "AUTO"
				
				type = None 	#reset
				lineNum = 0
				del objString[-1]
		elif(type == mnam):
			b3dObj = bpy.data.objects.new(line[1:mnam_c],None)
			b3dObj['root'] = True
			context.scene.objects.link(b3dObj)
			
			objString = [b3dObj.name]
			type = None
				
		elif(type == None):
			#print("line:	",line)
			if (line[0:2] == '  '):
				if (line[2:6] == 'RNOD'):
					type = rnod
				elif (line[2:6] == 'RSEG'):
					type = rseg
			else:
				if (line[0:4] == 'GROM'):
					if (len(objString)>1):
						del objString[-1]
					type = grom
				elif(line[0:4] == 'MNAM'):
					mnam_c = int(line[5])
					type = mnam					
					#print (line[0:4])