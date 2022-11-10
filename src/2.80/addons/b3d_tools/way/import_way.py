import bpy
import struct
import os
import sys

def readName(file, text_len):
	# text_len = 0
	str_len = 0

	rem = text_len % 4
	fill_len = (text_len + 4 - rem if rem else text_len) - text_len

	# if (text_len > 15):
	# 	str_len = 20

	# elif (11 < text_len < 15 or text_len == 15):
	# 	str_len = 16

	# elif (7 < text_len < 11 or text_len == 11):
	# 	str_len = 12

	# elif (3 < text_len < 7 or text_len == 7):
	# 	str_len = 8

	# elif (text_len < 3 or text_len == 3):
	# 	str_len = 4

	# string = file.read(str_len).decode("utf-8")

	string = file.read(text_len).decode("cp1251")
	if fill_len > 0:
		file.seek(fill_len, 1)
	return string

def openclose(file, path):
	if file.tell() == os.path.getsize(path):
		print ('EOF')
		return 1
	else:
		return 2
	print(str(os.path.getsize(path)))

def read(file, context, filepath):
	# file_path = file
	# file = open(file, 'rb')

	ex = 0
	rootName = os.path.basename(filepath)
	rootObject = bpy.data.objects.new(rootName, None)
	rootObject.location=(0,0,0)
	context.collection.objects.link(rootObject)

	while ex!=1:
		ex = openclose(file, filepath)
		if ex == 1:
			file.close()
			break

		elif ex == 2:
			type = file.read(4).decode("cp1251")

			global r

			if type == "WTWR": #WTWR
				rootObject['wtwr_size'] = struct.unpack("<i",file.read(4))[0]

				# file.seek(4, 1) #MNAM
				# rootObject['mnam'] = readName(file)

				# file.seek(4, 1) #GDAT
				# gdat_size = struct.unpack("<i",file.read(4))[0]

				# context.collection.objects.link(rootObject)
				print("after wtwr: " + str(file.tell()))

			elif type == "MNAM": #MNAM
				nameLen = struct.unpack("<i",file.read(4))[0]
				rootObject['mnam'] = readName(file, nameLen)
				print("after mnam: " + str(file.tell()))

			elif type == "GDAT": #MNAM
				rootObject['gdat_size'] = struct.unpack("<i",file.read(4))[0]
				print("after gdat: " + str(file.tell()))

			elif type == "GROM": #GROM
				object_name = "GROM"
				object = bpy.data.objects.new(object_name, None)
				object.location=(0,0,0)
				object['grom_size'] = struct.unpack("<i",file.read(4))[0]
				object['type'] = "room"

				subtype = file.read(4).decode("cp1251")
				if subtype == "RNAM":
					nameLen = struct.unpack("<i",file.read(4))[0]
					object.name = readName(file, nameLen)

				object.parent = bpy.data.objects[rootName]
				r = bpy.data.objects[object.name]
				context.collection.objects.link(object)

				# file.seek(-4, 1)
				print("after grom: " + str(file.tell()))


			elif type == "RSEG": #RSEG
				rseg_size = struct.unpack("<i",file.read(4))[0]
				rseg_size_cur = rseg_size

				points = []

				while rseg_size_cur > 0:
					subtype = file.read(4).decode("cp1251")
					subtypeSize = struct.unpack("<i",file.read(4))[0]
					if subtype == "ATTR":
						attr1 = struct.unpack("<i",file.read(4))[0]
						attr2 = struct.unpack("<d",file.read(8))[0]
						attr3 = struct.unpack("<i",file.read(4))[0]
						print("ATTR: " + str(attr1) + " " + str(attr2) + " " + str(attr3))
						rseg_size_cur = rseg_size_cur-subtypeSize-8 #subtype+subtypeSize
					elif subtype == "WDTH":
						wdth1 = struct.unpack("<d",file.read(8))[0]
						wdth2 = struct.unpack("<d",file.read(8))[0]
						print("WDTH: {} {}".format(str(wdth1), str(wdth2)))
						rseg_size_cur = rseg_size_cur-subtypeSize-8 #subtype+subtypeSize
					elif subtype == "VDAT":
						len_points = struct.unpack("<i",file.read(4))[0]
						print("Points in VDAT: " + str(len_points))
						for i in range (len_points):
							points.append(struct.unpack("ddd",file.read(24)))
						rseg_size_cur = rseg_size_cur-subtypeSize-8 #subtype+subtypeSize
					elif subtype == "RTEN":
						unknown1 = file.read(subtypeSize)
						rseg_size_cur = rseg_size_cur-subtypeSize-8 #subtype+subtypeSize

				if len(points):
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
					print("setting properties...")
					# object['type'] = "rseg"
					# object['bytes_len'] = vdat_size
					# object['attr1'] = attr1
					# object['attr2'] = attr2
					# object['attr3'] = attr3
					# object['wdth'] = wdth1
					object.parent = r
					context.collection.objects.link(object)
				print("after rseg: " + str(file.tell()))

			elif type == "RNOD": #RNOD
				rnod_size = struct.unpack("<i",file.read(4))[0]
				rnod_size_cur = rnod_size

				object_matrix = []

				while rnod_size_cur > 0:
					subtype = file.read(4).decode("cp1251")
					subtypeSize = struct.unpack("<i",file.read(4))[0]
					if subtype == "NNAM":
						print(file.tell())
						name = readName(file, subtypeSize)
						rnod_size_cur = rnod_size_cur-subtypeSize-8 #subtype+subtypeSize
					elif subtype == "POSN":
						pos = struct.unpack("ddd",file.read(24))
						rnod_size_cur = rnod_size_cur-subtypeSize-8 #subtype+subtypeSize
					elif subtype == "ORTN":
						for i in range(4):
							object_matrix.append(struct.unpack("<ddd",file.read(24)))
						rnod_size_cur = rnod_size_cur-subtypeSize-8 #subtype+subtypeSize
					elif subtype == "FLAG":
						pos = struct.unpack("<i",file.read(4))
						rnod_size_cur = rnod_size_cur-subtypeSize-8 #subtype+subtypeSize

				if len(object_matrix) > 0:

					cur_pos = object_matrix[3]
					object = bpy.ops.mesh.primitive_ico_sphere_add(radius=0.2, calc_uvs=True, location=cur_pos)
					object = bpy.context.selected_objects[0]
					object.parent = r
			else:
				print("Unknown type: " + type + " on position " + str(file.tell()))
			#sys.exit()
		#except:
		#print(str(file.tell()))
		#print('error')

	return {'FINISHED'}

def bak():
	if type == "FLAG":
		object_name = type
		object = bpy.data.objects.new(object_name, None)
		object.location=(0,0,0)
		object['flag'] = waytool.flag_int
		bpy.context.collection.objects.link(object)

	if type == "RNAM":
		object_name = type
		object = bpy.data.objects.new(object_name, None)
		object.location=(0,0,0)
		object['str'] = waytool.name_string
		bpy.context.collection.objects.link(object)

	if type == "NNAM":
		object_name = type
		object = bpy.data.objects.new(object_name, None)
		object.location=(0,0,0)
		object['str'] = waytool.name_string
		bpy.context.collection.objects.link(object)

	if type == "ORTN":
		object = bpy.ops.mesh.primitive_ico_sphere_add(radius=0.05, calc_uvs=True, location=(0.0,0.0,0.0))
		object = bpy.context.selected_objects[0]
		object.name = type
		object.location=cursor_pos1

	if type == "POSN":
		object = bpy.ops.mesh.primitive_ico_sphere_add(radius=0.05, calc_uvs=True, location=(0.0,0.0,0.0))
		object = bpy.context.selected_objects[0]
		object.name =type
		object.location=cursor_pos1
	return {'FINISHED'}