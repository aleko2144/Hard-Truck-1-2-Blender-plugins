import bpy
import struct
import os
import sys

def readName(file):
	text_len = 0
	str_len = 0
	
	text_len = struct.unpack("<i",file.read(4))[0]
		
	if (text_len > 15):
		str_len = 20
		
	elif (11 < text_len < 15 or text_len == 15):
		str_len = 16
		
	elif (7 < text_len < 11 or text_len == 11):
		str_len = 12
		
	elif (3 < text_len < 7 or text_len == 7):
		str_len = 8
			
	elif (text_len < 3 or text_len == 3):
		str_len = 4
		
	string = file.read(str_len).decode("utf-8")
	return string

def openclose(file, path):
	if file.tell() == os.path.getsize(path):
		print ('EOF')
		return 1
	else:
		return 2
	print(str(os.path.getsize(path)))
	
def read(file, context):
	file_path = file
	file = open(file, 'rb')
	
	ex = 0
	while ex!=1:
		ex = openclose(file, file_path)
		if ex == 1: 
			file.close()
			break

		elif ex == 2:
			type = file.read(4).decode("cp1251")
			
			global r
			
			if type == "WTWR": #WTWR
				object_name = "way"
				object = bpy.data.objects.new(object_name, None) 
				object.location=(0,0,0)
				object['c_bytes_len'] = struct.unpack("<i",file.read(4))[0]
				object['type'] = "way"

				file.seek(4, 1) #MNAM
				object['mnam'] = readName(file)
				
				file.seek(8, 1) #GDAT
				
				bpy.context.scene.objects.link(object)
				print("after wtwr: " + str(file.tell()))
				
				
			elif type == "GROM": #GROM
				object_name = "GROM"
				object = bpy.data.objects.new(object_name, None) 
				object.location=(0,0,0)
				object['c_bytes_len'] = struct.unpack("<i",file.read(4))[0]
				object['type'] = "room"
				
				file.seek(4, 1)
				object.name = readName(file)
				object.parent = bpy.data.objects['way']
				r = bpy.data.objects[object.name]
				bpy.context.scene.objects.link(object)
				
				file.seek(-4, 1)
				print("after grom: " + str(file.tell()))
				
			elif type == "RSEG": #RSEG
				c_bytes_len = struct.unpack("<i",file.read(4))[0]
				type = "RSEG"
				print("RSEG readed.")
					
				file.seek(8, 1)
				attr1 = struct.unpack("<i",file.read(4))[0]
				attr2 = struct.unpack("<d",file.read(8))[0]
				attr3 = struct.unpack("<i",file.read(4))[0]
				print("ATTR: " + str(attr1) + " " + str(attr2) + " " + str(attr3))
				print("ATTR readed.")
			
				file.seek(8, 1)
				wdth = struct.unpack("<d",file.read(8))[0]
				struct.unpack("<d",file.read(8))[0]
				print("WDTH: " + str(wdth))
				print("WDTH readed.")
				
				file.seek(4, 1)
				bytes_len = struct.unpack("<i",file.read(4))[0]
				len_points = struct.unpack("<i",file.read(4))[0]
				print("Points in VDTH: " + str(len_points))
					
				points = []
				for i in range (len_points):
					points.append(struct.unpack("ddd",file.read(24)))
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
				object['type'] = "rseg"
				object['bytes_len'] = bytes_len
				object['attr1'] = attr1
				object['attr2'] = attr2
				object['attr3'] = attr3
				object['wdth'] = wdth
				object.parent = r
				context.scene.objects.link(object)
				print("after rseg: " + str(file.tell()))
					
			elif type == "RNOD": #RNOD
				object_name = "RNOD"
				c_bytes_len = struct.unpack("<i",file.read(4))[0]
				file.seek(4, 1)
				
				name = readName(file)
				
				file.seek(4, 1)
				bytes_len = struct.unpack("<i",file.read(4))[0]
				print("pos: " + str(file.tell()))
				pos = struct.unpack("ddd",file.read(24))
				print("rnod pos: " + str(pos))
				object = bpy.ops.mesh.primitive_ico_sphere_add(size=0.05, calc_uvs=True, location=pos)	
				object = bpy.context.selected_objects[0]
				
				object.name = name
				object['type'] = "POSN"
				object['bytes_len'] = bytes_len
				
				if file.read(4).decode("cp1251") == "ORTN":
					object_matrix = []
					
					bytes_len = struct.unpack("<i",file.read(4))[0]
					object['bytes_len'] = bytes_len
					for i in range(3):
						object_matrix.append(struct.unpack("<ddd",file.read(24)))
					
					pos1 = struct.unpack("ddd",file.read(24))
					print("pos 1: " + str(pos1))
					
					object['type'] = "ORTN"
				else:
					file.seek(-4, 1)
				
				file.seek(4, 1)
				file.seek(4, 1)
				print("flag: " + str(file.tell()))
				object['flag'] = struct.unpack("<i",file.read(4))[0]
				object.parent = r
				print(str(object['flag']))
				print("after rnod: " + str(file.tell()))
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
		bpy.context.scene.objects.link(object)	
		
	if type == "RNAM":
		object_name = type
		object = bpy.data.objects.new(object_name, None) 
		object.location=(0,0,0)
		object['str'] = waytool.name_string
		bpy.context.scene.objects.link(object)	
		
	if type == "NNAM":
		object_name = type
		object = bpy.data.objects.new(object_name, None) 
		object.location=(0,0,0)
		object['str'] = waytool.name_string
		bpy.context.scene.objects.link(object)	
		
	if type == "ORTN":
		object = bpy.ops.mesh.primitive_ico_sphere_add(size=0.05, calc_uvs=True, location=(0.0,0.0,0.0))	
		object = bpy.context.selected_objects[0]
		object.name = type
		object.location=cursor_pos1
		
	if type == "POSN":
		object = bpy.ops.mesh.primitive_ico_sphere_add(size=0.05, calc_uvs=True, location=(0.0,0.0,0.0))	
		object = bpy.context.selected_objects[0]
		object.name =type
		object.location=cursor_pos1
	return {'FINISHED'}