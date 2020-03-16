bl_info = {
	"name": "Rig'N'Roll meshes importer",
	"description": "",
	"author": "Andrey Prozhoga",
	"version": (0, 0, 5),
	"blender": (2, 79, 0),
	"location": "3D View > Tools",
	"warning": "",
	"wiki_url": "",
	"tracker_url": "vk.com/rnr_mods",
	"category": "Import-Export"
}

import bpy
import struct
import sys
import argparse
import timeit
import threading
import pdb
import bmesh

def read_string_ht3(file):
	byte = b'\x10'
	counter = 0
	
	ret = "none"
		
	pos_start = file.tell()
		
	while byte != b'\x00':
		
		byte = file.read(1)
		counter += 1;
			
		if counter > 256:
			break
						
	file.seek(pos_start, 0)
	
	ret = ""
	name_bytes = file.read(counter)
	
	try:
		ret = str(name_bytes.decode("utf-8")).rstrip('\0')
	except UnicodeDecodeError:
		ret = ""
	#print(counter)
	return ret
	
def skip_string_ht3(file):
	byte = b'\x10'
	counter = 0
	
	ret = "none"
		
	pos_start = file.tell()
		
	while byte != b'\x00':
		
		byte = file.read(1)
		counter += 1;
			
		if counter > 256:
			break
						
	file.seek(pos_start, 0)
	file.seek(counter, 1)


def read_wdb_data(context, filepath, use_some_setting):
	#print("running read_wdb_data...")
	
	file = open(filepath, 'rb')
	
	file.seek(156, 1) #WDB, type 406, ещё что-нибудь
	type = struct.unpack("<i",file.read(4))[0]
		
	sections_def = []
	sections = []
	
	if (type == 407):
		section_length = struct.unpack("<i",file.read(4))[0]
		file.seek(8, 1) # Default
		names_count = struct.unpack("<i",file.read(4))[0]
			
		for i in range(names_count):
			section_type = struct.unpack("<i",file.read(4))[0]
			section_addr = struct.unpack("<i",file.read(4))[0]
			section_name_addr = struct.unpack("<i",file.read(4))[0]
				
			current_offset = file.tell();	
			file.seek(section_name_addr, 0)		
			block_name = read_string_ht3(file)
				
			file.seek(section_addr, 0)
			real_type = struct.unpack("<i",file.read(4))[0]
			block_length = struct.unpack("<i",file.read(4))[0]
			file.seek(current_offset, 0)
		
			sections.append( (section_type, section_addr, section_name_addr, block_name, len(block_name) + 1, real_type) )
			
	for i in range(len(sections)):
		#section[0] - block type
		#section[1] - offset
		#section[2] - name offset
		#section[3] - name
		#section[4] - name length
		#section[5] - real type (не то, что в начале файла, а то, что действительно записано по смещению)
		#видимо, тип, указанный в section[0] - и есть настоящий тип, а section[5] - подтип, разновидность блока
		
		# if sections[i][5] == 116:
			# name = ""
			
			# if (len(sections[i][3]) > 0):
				# name = sections[i][3]
			# else:
				# name = ("Untitled_" + str(sections[i][1]))
		
			# output_obj = open((output_spaces_dir + name + ".obj"),'w')
			# printw(out_file, "SimpleSpaceData (116), position " + str(hex(sections[i][1])) + ", name=" + name)
			# output_obj.write("# SimpleSpaceData (116), position " + str(hex(sections[i][1])) + '\n')
			# output_obj.write('\n')
			
			# output_obj.write("o " + name + '\n')
			# output_obj.write('\n')
			
			# file.seek(sections[i][1] + 4, 0) #к блоку 
			
			# file.seek(12, 1)
			# file.seek(sections[i][4], 1) #skip name
			# file.seek(32, 1)

			# m0_0 = struct.unpack('<d',file.read(8))[0]
			# m0_1 = struct.unpack('<d',file.read(8))[0]
			# m0_2 = struct.unpack('<d',file.read(8))[0]
			
			# m1_0 = struct.unpack('<d',file.read(8))[0]
			# m1_1 = struct.unpack('<d',file.read(8))[0]
			# m1_2 = struct.unpack('<d',file.read(8))[0]
			
			# m2_0 = struct.unpack('<d',file.read(8))[0]
			# m2_1 = struct.unpack('<d',file.read(8))[0]
			# m2_2 = struct.unpack('<d',file.read(8))[0]
			
			# x = struct.unpack('<d',file.read(8))[0]
			# y = struct.unpack('<d',file.read(8))[0]
			# z = struct.unpack('<d',file.read(8))[0]
			
			# output_obj.write(f"# {m0_0} {m0_1} {m0_2}" + '\n')
			# output_obj.write(f"# {m1_0} {m1_1} {m1_2}" + '\n')
			# output_obj.write(f"# {m2_0} {m2_1} {m2_2}" + '\n')
			
			# output_obj.write(f"v {x} {y} {z}" + '\n')
			
			# output_obj.write('\n')			
		
		if sections[i][5] == 309 or sections[i][5] == 310: #312, указанный в начале файла, обычно равен 309
			name = ""
			
			if (len(sections[i][3]) > 0):
				name = sections[i][3]
			else:
				name = ("Untitled_" + str(sections[i][1]))
		
			#output_obj = open((output_meshes_dir + name + ".obj"),'w')
			#output_debug_obj = open((output_meshes_dir + name + "_debug.obj"),'w')
			
			print(str(sections[i][5]) + " " + str(hex(sections[i][1])))
			
			file.seek(sections[i][1] + 4, 0) #к блоку
			
			block_length = struct.unpack("<i",file.read(4))[0]
			
			file.seek(sections[i][4], 1) #skip name
			
			verts_type = struct.unpack("<i",file.read(4))[0]
			
			vertices_len = struct.unpack('<i',file.read(4))[0]
			
			vertices = []
			vert_normals = []
			uvs = []
			
			#print(str(vertices_len))
			#print(str(file.tell()))
			
			if (vertices_len > 999990):
				print("Vertices num is too big. Check position " + str(hex(file.tell())) + ".")
				input("Press ENTER key to exit.")
				sys.exit()
			else:
				if (verts_type == 18):
					for i in range(vertices_len):
					
						x = struct.unpack('<f',file.read(4))[0]
						y = struct.unpack('<f',file.read(4))[0]
						z = struct.unpack('<f',file.read(4))[0]
						
						nx = struct.unpack('<f',file.read(4))[0]
						ny = struct.unpack('<f',file.read(4))[0]
						nz = struct.unpack('<f',file.read(4))[0]
						
						vertices.append((x, y, z))
						vert_normals.append((nx, ny, nz))
						uvs.append((0, 0))
				elif (verts_type == 258):
					for i in range(vertices_len):
					
						x = struct.unpack('<f',file.read(4))[0]
						y = struct.unpack('<f',file.read(4))[0]
						z = struct.unpack('<f',file.read(4))[0]
						
						u = struct.unpack('<f',file.read(4))[0]
						v = struct.unpack('<f',file.read(4))[0]
						
						vertices.append((x, y, z))
						uvs.append((u, v))
						
				elif (verts_type == 274):
					for i in range(vertices_len):
					
						x = struct.unpack('<f',file.read(4))[0]
						y = struct.unpack('<f',file.read(4))[0]
						z = struct.unpack('<f',file.read(4))[0]
						
						nx = struct.unpack('<f',file.read(4))[0]
						ny = struct.unpack('<f',file.read(4))[0]
						nz = struct.unpack('<f',file.read(4))[0]
						
						u = struct.unpack('<f',file.read(4))[0]
						v = struct.unpack('<f',file.read(4))[0]
						
						vertices.append((x, y, z))
						vert_normals.append((nx, ny, nz))
						uvs.append((u, v))
						
				elif (verts_type == 338):
					for i in range(vertices_len):
					
						x = struct.unpack('<f',file.read(4))[0]
						y = struct.unpack('<f',file.read(4))[0]
						z = struct.unpack('<f',file.read(4))[0]
						
						nx = struct.unpack('<f',file.read(4))[0]
						ny = struct.unpack('<f',file.read(4))[0]
						nz = struct.unpack('<f',file.read(4))[0]
						
						file.seek(4, 1)
						
						u = struct.unpack('<f',file.read(4))[0]
						v = struct.unpack('<f',file.read(4))[0]
						
						vertices.append((x, y, z))
						vert_normals.append((nx, ny, nz))
						uvs.append((u, v))													
				elif (verts_type == 514):
					for i in range(vertices_len):
					
						x = struct.unpack('<f',file.read(4))[0]
						y = struct.unpack('<f',file.read(4))[0]
						z = struct.unpack('<f',file.read(4))[0]
						
						u = struct.unpack('<f',file.read(4))[0]
						v = struct.unpack('<f',file.read(4))[0]
						
						u1 = struct.unpack('<f',file.read(4))[0]
						v1 = struct.unpack('<f',file.read(4))[0]
						
						vertices.append((x, y, z))
						uvs.append((u, v))						
				elif (verts_type == 530):	
					for i in range(vertices_len):
					
						x = struct.unpack('<f',file.read(4))[0]
						y = struct.unpack('<f',file.read(4))[0]
						z = struct.unpack('<f',file.read(4))[0]
						
						nx = struct.unpack('<f',file.read(4))[0]
						ny = struct.unpack('<f',file.read(4))[0]
						nz = struct.unpack('<f',file.read(4))[0]
						
						u = struct.unpack('<f',file.read(4))[0]
						v = struct.unpack('<f',file.read(4))[0]
						
						u1 = struct.unpack('<f',file.read(4))[0]
						v1 = struct.unpack('<f',file.read(4))[0]
						
						vertices.append((x, y, z))
						vert_normals.append((nx, ny, nz))
						uvs.append((u, v))					
				elif (verts_type == 594):
					for i in range(vertices_len):
					
						x = struct.unpack('<f',file.read(4))[0]
						y = struct.unpack('<f',file.read(4))[0]
						z = struct.unpack('<f',file.read(4))[0]
						
						nx = struct.unpack('<f',file.read(4))[0]
						ny = struct.unpack('<f',file.read(4))[0]
						nz = struct.unpack('<f',file.read(4))[0]
						
						file.seek(4, 1)
						
						u = struct.unpack('<f',file.read(4))[0]
						v = struct.unpack('<f',file.read(4))[0]
						
						u1 = struct.unpack('<f',file.read(4))[0]
						v1 = struct.unpack('<f',file.read(4))[0]
						
						vertices.append((x, y, z))
						vert_normals.append((nx, ny, nz))
						uvs.append((u, v))						
				elif (verts_type == 786):	
					for i in range(vertices_len):
					
						x = struct.unpack('<f',file.read(4))[0]
						y = struct.unpack('<f',file.read(4))[0]
						z = struct.unpack('<f',file.read(4))[0]
						
						nx = struct.unpack('<f',file.read(4))[0]
						ny = struct.unpack('<f',file.read(4))[0]
						nz = struct.unpack('<f',file.read(4))[0]
						
						u = struct.unpack('<f',file.read(4))[0]
						v = struct.unpack('<f',file.read(4))[0]
						
						file.seek(16, 1)
						
						vertices.append((x, y, z))
						vert_normals.append((nx, ny, nz))
						uvs.append((u, v))						
				elif (verts_type == 1042):
					for i in range(vertices_len):
					
						x = struct.unpack('<f',file.read(4))[0]
						y = struct.unpack('<f',file.read(4))[0]
						z = struct.unpack('<f',file.read(4))[0]
						
						nx = struct.unpack('<f',file.read(4))[0]
						ny = struct.unpack('<f',file.read(4))[0]
						nz = struct.unpack('<f',file.read(4))[0]
						
						u = struct.unpack('<f',file.read(4))[0]
						v = struct.unpack('<f',file.read(4))[0]
						
						file.seek(24, 1)
						
						vertices.append((x, y, z))
						vert_normals.append((nx, ny, nz))
						uvs.append((u, v))	
				elif (verts_type == 1106):
					for i in range(vertices_len):
					
						x = struct.unpack('<f',file.read(4))[0]
						y = struct.unpack('<f',file.read(4))[0]
						z = struct.unpack('<f',file.read(4))[0]
						
						nx = struct.unpack('<f',file.read(4))[0]
						ny = struct.unpack('<f',file.read(4))[0]
						nz = struct.unpack('<f',file.read(4))[0]
						
						file.seek(4, 1) #diffuse
						
						u = struct.unpack('<f',file.read(4))[0]
						v = struct.unpack('<f',file.read(4))[0]
						
						file.seek(8, 1)
						file.seek(8, 1)
						file.seek(8, 1)
						
						
						vertices.append((x, y, z))
						vert_normals.append((nx, ny, nz))
						uvs.append((u, v))	
				elif (verts_type == 1298):
					for i in range(vertices_len):
					
						x = struct.unpack('<f',file.read(4))[0]
						y = struct.unpack('<f',file.read(4))[0]
						z = struct.unpack('<f',file.read(4))[0]
						
						nx = struct.unpack('<f',file.read(4))[0]
						ny = struct.unpack('<f',file.read(4))[0]
						nz = struct.unpack('<f',file.read(4))[0]
						
						u = struct.unpack('<f',file.read(4))[0]
						v = struct.unpack('<f',file.read(4))[0]
						
						file.seek(8, 1)
						file.seek(8, 1) #
						file.seek(8, 1) #
						file.seek(8, 1) #
						
						vertices.append((x, y, z))
						vert_normals.append((nx, ny, nz))
						uvs.append((u, v))	
				elif (verts_type == 4370):
					for i in range(vertices_len):
					
						x = struct.unpack('<f',file.read(4))[0]
						y = struct.unpack('<f',file.read(4))[0]
						z = struct.unpack('<f',file.read(4))[0]
						
						bindex = struct.unpack('<i', file.read(4))[0]
						
						nx = struct.unpack('<f',file.read(4))[0]
						ny = struct.unpack('<f',file.read(4))[0]
						nz = struct.unpack('<f',file.read(4))[0]
						
						u = struct.unpack('<f',file.read(4))[0]
						v = struct.unpack('<f',file.read(4))[0]

						vertices.append((x, y, z))
						vert_normals.append((nx, ny, nz))
						uvs.append((u, v))

						#group = wdbObj.vertex_groups.new(name = "BINDEX_" + str(bindex))
						#group.add(i, 0.1, 'ADD')
						
				elif (verts_type == 4374):
					for i in range(vertices_len):
					
						x = struct.unpack('<f',file.read(4))[0]
						y = struct.unpack('<f',file.read(4))[0]
						z = struct.unpack('<f',file.read(4))[0]
						
						blend = struct.unpack('<f',file.read(4))[0]
						bindex = struct.unpack('<i', file.read(4))[0]

						nx = struct.unpack('<f',file.read(4))[0]
						ny = struct.unpack('<f',file.read(4))[0]					
						nz = struct.unpack('<f',file.read(4))[0]
						
						u = struct.unpack('<f',file.read(4))[0]
						v = struct.unpack('<f',file.read(4))[0]

						vertices.append((x, y, z))
						vert_normals.append((nx, ny, nz))
						uvs.append((u, v))						
				elif (verts_type == 4434):
					for i in range(vertices_len):
					
						x = struct.unpack('<f',file.read(4))[0]
						y = struct.unpack('<f',file.read(4))[0]
						z = struct.unpack('<f',file.read(4))[0]
						
						bindex = struct.unpack('<i', file.read(4))[0]
						
						nx = struct.unpack('<f',file.read(4))[0]
						ny = struct.unpack('<f',file.read(4))[0]
						nz = struct.unpack('<f',file.read(4))[0]

						file.seek(4, 1)

						u = struct.unpack('<f',file.read(4))[0]
						v = struct.unpack('<f',file.read(4))[0]

						vertices.append((x, y, z))
						vert_normals.append((nx, ny, nz))
						uvs.append((u, v))
				elif (verts_type == 4626):
					for i in range(vertices_len):
					
						x = struct.unpack('<f',file.read(4))[0]
						y = struct.unpack('<f',file.read(4))[0]
						z = struct.unpack('<f',file.read(4))[0]
						

						
						bindex = struct.unpack('<i', file.read(4))[0]

						nx = struct.unpack('<f',file.read(4))[0]
						ny = struct.unpack('<f',file.read(4))[0]					
						nz = struct.unpack('<f',file.read(4))[0]
						u = struct.unpack('<f',file.read(4))[0]
						v = struct.unpack('<f',file.read(4))[0]
						u1 = struct.unpack('<f',file.read(4))[0]
						v1 = struct.unpack('<f',file.read(4))[0]
						#v8 = struct.unpack('<f',file.read(4))[0]
						
						vertices.append((x, y, z))
						vert_normals.append((nx, ny, nz))
						uvs.append((u, v))				
				elif (verts_type == 4882):
					for i in range(vertices_len):
					
						x = struct.unpack('<f',file.read(4))[0]
						y = struct.unpack('<f',file.read(4))[0]
						z = struct.unpack('<f',file.read(4))[0]
						
						file.seek(4, 1)
						
						nx = struct.unpack('<f',file.read(4))[0]
						ny = struct.unpack('<f',file.read(4))[0]					
						nz = struct.unpack('<f',file.read(4))[0]
						
						u = struct.unpack('<f',file.read(4))[0]
						v = struct.unpack('<f',file.read(4))[0]
						
						u2 = struct.unpack('<f',file.read(4))[0]
						v2 = struct.unpack('<f',file.read(4))[0]
						
						u3 = struct.unpack('<f',file.read(4))[0]
						v3 = struct.unpack('<f',file.read(4))[0]
						#v8 = struct.unpack('<f',file.read(4))[0]
						
						vertices.append((x, y, z))
						vert_normals.append((nx, ny, nz))
						uvs.append((u, v))											
				elif (verts_type == 5202):
					for i in range(vertices_len):
					
						x = struct.unpack('<f',file.read(4))[0]
						y = struct.unpack('<f',file.read(4))[0]
						z = struct.unpack('<f',file.read(4))[0]
						
						bindex = struct.unpack('<i',file.read(4))[0]
						
						nx = struct.unpack('<f',file.read(4))[0]
						ny = struct.unpack('<f',file.read(4))[0]
						nz = struct.unpack('<f',file.read(4))[0]
						
						file.seek(4, 1)
						
						u = struct.unpack('<f',file.read(4))[0]
						v = struct.unpack('<f',file.read(4))[0]
						
						u1 = struct.unpack('<f',file.read(4))[0]
						v1 = struct.unpack('<f',file.read(4))[0]
						
						u2 = struct.unpack('<f',file.read(4))[0]
						v2 = struct.unpack('<f',file.read(4))[0]
						
						u3 = struct.unpack('<f',file.read(4))[0]
						v3 = struct.unpack('<f',file.read(4))[0]
						
						vertices.append((x, y, z))
						vert_normals.append((nx, ny, nz))
						uvs.append((u, v))
				elif (verts_type == 8466):
					for i in range(vertices_len):
					
						x = struct.unpack('<f',file.read(4))[0]
						y = struct.unpack('<f',file.read(4))[0]
						z = struct.unpack('<f',file.read(4))[0]
						
						nx = struct.unpack('<f',file.read(4))[0]
						ny = struct.unpack('<f',file.read(4))[0]
						nz = struct.unpack('<f',file.read(4))[0]
						
						u = struct.unpack('<f',file.read(4))[0]
						v = struct.unpack('<f',file.read(4))[0]
						
						file.seek(12, 1) #24
						
						vertices.append((x, y, z))
						vert_normals.append((nx, ny, nz))
						uvs.append((u, v))						
				elif (verts_type == 8530):
					for i in range(vertices_len):
					
						x = struct.unpack('<f',file.read(4))[0]
						y = struct.unpack('<f',file.read(4))[0]
						z = struct.unpack('<f',file.read(4))[0]
						
						nx = struct.unpack('<f',file.read(4))[0]
						ny = struct.unpack('<f',file.read(4))[0]
						nz = struct.unpack('<f',file.read(4))[0]
						
						file.seek(4, 1)
						
						u = struct.unpack('<f',file.read(4))[0]
						v = struct.unpack('<f',file.read(4))[0]
						
						file.seek(12, 1)
						
						vertices.append((x, y, z))
						vert_normals.append((nx, ny, nz))
						uvs.append((u, v))						
				elif (verts_type == 8722):
					for i in range(vertices_len):
					
						x = struct.unpack('<f',file.read(4))[0]
						y = struct.unpack('<f',file.read(4))[0]
						z = struct.unpack('<f',file.read(4))[0]
						
						nx = struct.unpack('<f',file.read(4))[0]
						ny = struct.unpack('<f',file.read(4))[0]
						nz = struct.unpack('<f',file.read(4))[0]
						
						u = struct.unpack('<f',file.read(4))[0]
						v = struct.unpack('<f',file.read(4))[0]
						
						file.seek(20, 1)
						
						vertices.append((x, y, z))
						vert_normals.append((nx, ny, nz))
						uvs.append((u, v))											
				elif (verts_type == 3416834):
					for i in range(vertices_len):
					
						x = struct.unpack('<f',file.read(4))[0]
						y = struct.unpack('<f',file.read(4))[0]
						z = struct.unpack('<f',file.read(4))[0]
						
						nx = struct.unpack('<f',file.read(4))[0]
						ny = struct.unpack('<f',file.read(4))[0]
						nz = struct.unpack('<f',file.read(4))[0]
						
						file.seek(4, 1)
						
						u = struct.unpack('<f',file.read(4))[0]
						v = struct.unpack('<f',file.read(4))[0]
						
						file.seek(12, 1)
						
						vertices.append((x, y, z))
						vert_normals.append((nx, ny, nz))
						uvs.append((u, v))													
				elif (verts_type == 3420930): #4882
					for i in range(vertices_len):
					
						x = struct.unpack('<f',file.read(4))[0]
						y = struct.unpack('<f',file.read(4))[0]
						z = struct.unpack('<f',file.read(4))[0]
						
						file.seek(4, 1)
						
						nx = struct.unpack('<f',file.read(4))[0]
						ny = struct.unpack('<f',file.read(4))[0]					
						nz = struct.unpack('<f',file.read(4))[0]
						
						u = struct.unpack('<f',file.read(4))[0]
						v = struct.unpack('<f',file.read(4))[0]
						
						u2 = struct.unpack('<f',file.read(4))[0]
						v2 = struct.unpack('<f',file.read(4))[0]
						
						u3 = struct.unpack('<f',file.read(4))[0]
						v3 = struct.unpack('<f',file.read(4))[0]
						#v8 = struct.unpack('<f',file.read(4))[0]
						
						vertices.append((x, y, z))
						vert_normals.append((nx, ny, nz))
						uvs.append((u, v))											
				elif (verts_type == 5506066):
					for i in range(vertices_len):
					
						x = struct.unpack('<f',file.read(4))[0]
						y = struct.unpack('<f',file.read(4))[0]
						z = struct.unpack('<f',file.read(4))[0]
						
						nx = struct.unpack('<f',file.read(4))[0]
						ny = struct.unpack('<f',file.read(4))[0]					
						nz = struct.unpack('<f',file.read(4))[0]
					
						u = struct.unpack('<f',file.read(4))[0]
						v = struct.unpack('<f',file.read(4))[0]
						
						file.seek(36, 1)
						
						vertices.append((x, y, z))
						vert_normals.append((nx, ny, nz))
						uvs.append((u, v))					
				elif (verts_type == 5510162):
					for i in range(vertices_len):
					
						x = struct.unpack('<f',file.read(4))[0]
						y = struct.unpack('<f',file.read(4))[0]
						z = struct.unpack('<f',file.read(4))[0]
						
						var_int = struct.unpack('<i',file.read(4))[0] #номер плоскости?
						#file.seek(4, 1) #int
						
						nx = struct.unpack('<f',file.read(4))[0]
						ny = struct.unpack('<f',file.read(4))[0]
						nz = struct.unpack('<f',file.read(4))[0]
						
						u = struct.unpack('<f',file.read(4))[0]
						v = struct.unpack('<f',file.read(4))[0]

						file.seek(36, 1)

						vertices.append((x, y, z))
						vert_normals.append((nx, ny, nz))
						uvs.append((u, v))							
				elif (verts_type == 5510166):
					for i in range(vertices_len):
					
						x = struct.unpack('<f',file.read(4))[0]
						y = struct.unpack('<f',file.read(4))[0]
						z = struct.unpack('<f',file.read(4))[0]
						
						blend = struct.unpack('<f',file.read(4))[0]
						bindex = struct.unpack('<i', file.read(4))[0]

						nx = struct.unpack('<f',file.read(4))[0]
						ny = struct.unpack('<f',file.read(4))[0]					
						nz = struct.unpack('<f',file.read(4))[0]
						
						u = struct.unpack('<f',file.read(4))[0]
						v = struct.unpack('<f',file.read(4))[0]
						
						u1 = struct.unpack('<f',file.read(4))[0]
						v1 = struct.unpack('<f',file.read(4))[0]
						w1 = struct.unpack('<f',file.read(4))[0]
						
						u2 = struct.unpack('<f',file.read(4))[0]
						v2 = struct.unpack('<f',file.read(4))[0]
						w2 = struct.unpack('<f',file.read(4))[0]
						
						u3 = struct.unpack('<f',file.read(4))[0]
						v3 = struct.unpack('<f',file.read(4))[0]
						w3 = struct.unpack('<f',file.read(4))[0]

						vertices.append((x, y, z))
						vert_normals.append((nx, ny, nz))
						uvs.append((u, v))		
				elif (verts_type == 22021394):
					for i in range(vertices_len):
					
						x = struct.unpack('<f',file.read(4))[0]
						y = struct.unpack('<f',file.read(4))[0]
						z = struct.unpack('<f',file.read(4))[0]
						
						nx = struct.unpack('<f',file.read(4))[0]
						ny = struct.unpack('<f',file.read(4))[0]					
						nz = struct.unpack('<f',file.read(4))[0]
						
						u = struct.unpack('<f',file.read(4))[0]
						v = struct.unpack('<f',file.read(4))[0]

						file.seek(8, 1) #uv1
						file.seek(8, 1) #uv2
						file.seek(8, 1) #uv3
						file.seek(8, 1) #uv4
						file.seek(8, 1) #uv5
						
						file.seek(4, 1)
						
						vertices.append((x, y, z))
						vert_normals.append((nx, ny, nz))
						uvs.append((u, v))						
				elif (verts_type == 22025490):
					for i in range(vertices_len):
					
						x = struct.unpack('<f',file.read(4))[0]
						y = struct.unpack('<f',file.read(4))[0]
						z = struct.unpack('<f',file.read(4))[0]
						
						nx = struct.unpack('<f',file.read(4))[0]
						ny = struct.unpack('<f',file.read(4))[0]					
						nz = struct.unpack('<f',file.read(4))[0]
						
						u = struct.unpack('<f',file.read(4))[0]
						v = struct.unpack('<f',file.read(4))[0]
						
						file.seek(8, 1) #uv1
						file.seek(8, 1) #uv2
						file.seek(8, 1) #uv3
						file.seek(8, 1) #uv4
						file.seek(8, 1) #uv5
						file.seek(8, 1) #uv6
						
						vertices.append((x, y, z))
						vert_normals.append((nx, ny, nz))
						uvs.append((u, v))							
				else:
					print(str(hex(file.tell())))
					print("Unknown verts type: " + str(verts_type))
					print("Verts length (counted): " + str(int((block_length - 16 - sections[i][4]) / vertices_len)))
					#input("Press ENTER key to exit.")
					sys.exit()
					
				if (len(vertices) != len(uvs)):
					print("VERTICES ARRAY LENGTH != UV ARRAY LENGTH, ERROR")
					sys.exit()
					
			mesh_type = struct.unpack("<i",file.read(4))[0]
			
			print(str(mesh_type) + " " + str(hex(file.tell() - 4)))
			
			#print("type: " + str(mesh_type))
			mesh_section_length = struct.unpack("<i",file.read(4))[0]
			skip_string_ht3(file)
			faces_type = struct.unpack("<i",file.read(4))[0]
			
			#faces_count = 0
			
			#if (fc_1 == 73084):
			#	faces_count = 55
			#else:
			#	faces_count  = struct.unpack("<i",file.read(4))[0]
			
			faces_count = struct.unpack("<i",file.read(4))[0]
			
			faces = []
			
			if (faces_count > 256000):
				print("Faces num is too big. Check position " + str(hex(file.tell())) + ".")
				sys.exit()
			else:	
				if (mesh_type == 312):
					for i in range(int(faces_count / 3)):
						f1_r = struct.unpack("<H",file.read(2))[0]
						f2_r = struct.unpack("<H",file.read(2))[0]
						f3_r = struct.unpack("<H",file.read(2))[0]
						
						f1 = 0
						f2 = 0
						f3 = 0
						
						if (f1_r <= vertices_len):
							f1 = f1_r
										
						if (f2_r <= vertices_len):
							f2 = f2_r
											
						if (f3_r <= vertices_len):
							f3 = f3_r
							
						faces.append((f1, f2, f3))
						#faces.append(f1)
						#faces.append(f2)
						#faces.append(f3)

				elif (mesh_type == 313): #needs to be fixed
					for i in range(int(faces_count / 3)):
						
						f1_r = struct.unpack("<H",file.read(2))[0]
						f2_r = struct.unpack("<H",file.read(2))[0]
						f3_r = struct.unpack("<H",file.read(2))[0]
						
						# if (f1_r + 2 < vertices_len):
							# f1 = f1_r + 1
						# else:
							# f1 = -1
								
						# if (f2_r + 2 < vertices_len):
							# f2 = f2_r + 1
						# else:
							# f2 = -1
								
						# if (f3_r + 2 < vertices_len):
							# f3 = f3_r + 1
						# else:
							# f3 = -1
							
							
						# output_obj.write(f"f {f1}/{f1} {f2}/{f2} {f3}/{f3}")
						# output_obj.write('\n')
						
						f1 = 0
						f2 = 0
						f3 = 0
						
						if (f1_r <= vertices_len):
							f1 = f1_r
										
						if (f2_r <= vertices_len):
							f2 = f2_r
											
						if (f3_r <= vertices_len):
							f3 = f3_r
							
						faces.append((f1, f2, f3))
							
			wdbMesh = (bpy.data.meshes.new(name))
			wdbObj = bpy.data.objects.new(name, wdbMesh)
			#wdbMesh.from_pydata(vertices,[], faces)
	
			# scene = bpy.context.scene
			# scene.objects.link(wdbObj)  # put the object into the scene (link)
			# scene.objects.active = wdbObj  # set as the active object in the scene
			# wdbObj.select = True  # select object

			# wdbMesh = bpy.context.object.data
			# bm = bmesh.new()

			# for v in vertices:
				# bm.verts.new(v)

			# bm.to_mesh(wdbMesh)  
			# bm.free() 
			
			faces.reverse()
			
			Ev = threading.Event()
			Tr = threading.Thread(target=wdbMesh.from_pydata, args = (vertices,[],faces))
			Tr.start()
			Ev.set()
			Tr.join()
			
			uvMesh = wdbMesh.uv_textures.new()
			uvMesh.name = 'UVmap'
			uv_layer = wdbMesh.uv_layers[0]
			
			for poly in wdbMesh.polygons:
				for index in range(poly.loop_start, poly.loop_start+ poly.loop_total):
					vInd = wdbMesh.loops[index].vertex_index
					uv_layer.data[index].uv = (uvs[vInd][0], 1 - uvs[vInd][1])
					
			if ((verts_type != 258) or (verts_type != 514)):
				i = 0
				for i,vert in enumerate(wdbMesh.vertices):
					try:
						vert.normal = vert_normals[i]
					except IndexError:
						pass
			
			for face in wdbMesh.polygons:
				face.use_smooth = True


			context.scene.objects.link(wdbObj)
			
	print("EOF")
	
	#for i in range(len(vertices)):
				
	#for i in range(len(uvs)):
							
	#for i in range(len(vert_normals)):
	
	file.close()


	return {'FINISHED'}


# ImportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator


class ImportWDB(Operator, ImportHelper):
    """Import from WDB file format (.wdb)"""
    bl_idname = "import_wdb.wdb_data"  # important since its how bpy.ops.import_wdb.wdb_data is constructed
    bl_label = "Import R'n'R .wdb"

    # ImportHelper mixin class uses this
    filename_ext = ".wdb"

    filter_glob = StringProperty(
            default="*.wdb",
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
        return read_wdb_data(context, self.filepath, self.use_setting)


# Only needed if you want to add into a dynamic menu
def menu_func_import(self, context):
    self.layout.operator(ImportWDB.bl_idname, text="Rig'n'Roll WDB (.wdb)")


def register():
    bpy.utils.register_class(ImportWDB)
    bpy.types.INFO_MT_file_import.append(menu_func_import)


def unregister():
    bpy.utils.unregister_class(ImportWDB)
    bpy.types.INFO_MT_file_import.remove(menu_func_import)


if __name__ == "__main__":
    register()

    # test call
    bpy.ops.import_wdb.wdb_data('INVOKE_DEFAULT')
