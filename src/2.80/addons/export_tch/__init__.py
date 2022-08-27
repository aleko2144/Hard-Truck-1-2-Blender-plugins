bl_info = {
	"name": "King of The Road *.tch exporter",
	"description": "",
	"author": "Andrey Prozhoga",
	"version": (0, 0, 1),
	"blender": (3, 0, 0),
	"location": "3D View > Tools",
	"warning": "",
	"wiki_url": "",
	"tracker_url": "vk.com/rnr_mods",
	"category": "Development"
}

import bpy
from mathutils import Matrix
from math import radians

from mathutils import Vector
from math import sqrt

import bmesh


def read_tch(context, filepath, use_some_setting):
	print("running read_tch...")
	#file = open(filepath, 'r', encoding='utf-8')
	#data = f.read()


	file = open(filepath, 'r')

	CollisionPlane = []

	CPlanes_num = 0

	field_ind = ""
	field_x = ""
	field_y = ""
	field_z = ""
	field_offset = ""

	for line in file:
		ColPlane_line = ""
		if "CollisionPlane" in line:
			CollisionPlane.append(line)
			#CPlanes_num += 1
	file.close()

	#print(str(CollisionPlane))
	ColPlane_vector = []


	for i in range(len(CollisionPlane)):#(CPlanes_num):
		if i < 10:
			ColPlane_vector.append((CollisionPlane[i])[16:].split(" "))
		else:
			ColPlane_vector.append((CollisionPlane[i])[17:].split(" "))
		#print(str(i))


	print(str(ColPlane_vector))
	# would normally load the data here
	#print(data)

	return {'FINISHED'}

def export_tch(context, filepath):
	print("exporting tch...")
	file = open(filepath, 'w')

	global global_matrix
	global_matrix = axis_conversion(to_forward="-Z",
										to_up="Y",
										).to_4x4() * Matrix.Scale(1, 4)

	global CollisionPlane_num
	CollisionPlane_num = 0

	forChild(bpy.data.objects['tch'],True, file, CollisionPlane_num)

	return {'FINISHED'}



def forChild(object, root, file, CollisionPlane_num):
	if (not root):
		if object.name == "Corner_Mark":
			verticesL = []
			uvs = []
			faces = []

			bm = bmesh.new()
			bm.from_mesh(object.data)
			bm.verts.ensure_lookup_table()
			bm.faces.ensure_lookup_table()

			bm.transform(global_matrix * object.matrix_world)

			bm.to_mesh(object.data)


			for v in bm.verts:
				verticesL.append((v.co))

			meshdata = object.data

			for i, polygon in enumerate(meshdata.polygons):
				for i1, loopindex in enumerate(polygon.loop_indices):
					meshloop = meshdata.loops[loopindex]
					faces.append(meshloop.vertex_index)

			vLen = len(verticesL)

			#for i,vert in enumerate(verticesL):
				#file.write("CornerMark_" + str(i) + "=" + str(vert[0][0]) + " " + str(-vert[0][2]) + " " + str(vert[0][1]))
				#file.write(str(object.data.vert[i][0][0]))

			v_num = 0

			for vert in object.data.vertices:
				v_num += 1
				file.write("Corner_Mark_" + str(v_num) + "=" + str(round(vert.co.x, 6)) + " " + str(round(-vert.co.z, 6)) + " " + str(round(vert.co.y, 6)) + "\n")
				#file.write(struct.pack("<f",vert.co.x))
				#file.write(struct.pack("<f",vert.co.y))
				#file.write(struct.pack("<f",vert.co.z))

		if object.name == "Corner_Mark_W":
			verticesL = []
			uvs = []
			faces = []

			bm = bmesh.new()
			bm.from_mesh(object.data)
			bm.verts.ensure_lookup_table()
			bm.faces.ensure_lookup_table()

			bm.transform(global_matrix * object.matrix_world)

			bm.to_mesh(object.data)


			for v in bm.verts:
				verticesL.append((v.co))

			meshdata = object.data

			for i, polygon in enumerate(meshdata.polygons):
				for i1, loopindex in enumerate(polygon.loop_indices):
					meshloop = meshdata.loops[loopindex]
					faces.append(meshloop.vertex_index)

			vLen = len(verticesL)

			v_num = 0

			for vert in object.data.vertices:
				v_num += 1
				file.write("Corner_Mark_W" + str(v_num) + "=" + str(round(vert.co.x, 6)) + " " + str(round(-vert.co.z, 6)) + " " + str(round(vert.co.y, 6)) + "\n")

		if object.name.find("CollisionPlane") != "Null" or "None":
			if object.name != "CollisionPlane":
				verticesL = []
				uvs = []
				faces = []

				bm = bmesh.new()
				bm.from_mesh(object.data)
				bm.verts.ensure_lookup_table()
				bm.faces.ensure_lookup_table()

				bm.transform(global_matrix * object.matrix_world)

				bm.to_mesh(object.data)


				for v in bm.verts:
					verticesL.append((v.co))

				meshdata = object.data

				for i, polygon in enumerate(meshdata.polygons):
					for i1, loopindex in enumerate(polygon.loop_indices):
						meshloop = meshdata.loops[loopindex]
						faces.append(meshloop.vertex_index)

				vLen = len(verticesL)

				#vector = Vector(0,0,0)

				#vector = mathutils.Vector((0.0, 0.0, 0.0))

				vector_to_plane = Vector((0.0, 0.0, 0.0))

				vector_to_plane = Vector((object.location.x, object.location.y, object.location.z))
				#print(vector_to_plane.normalized())

				vector_length = sqrt(vector_to_plane.x ** 2 + vector_to_plane.y ** 2 + vector_to_plane.z ** 2)
				vector_to_plane = vector_to_plane.normalized()

				#file.write("CollisionPlane" + str(v_num) + "=" + str(round(vert.co.x, 6)) + " " + str(round(-vert.co.z, 6)) + " " + str(round(vert.co.y, 6)) + "\n")
				#print(vector_to_plane)
				#file.write("CollisionPlane" + str(v_num) + "=" + str(vector_to_plane) + "\n")

				#if (vector_to_plane.x != 0 and vector_to_plane.y != 0 and vector_to_plane.z != 0):
				file.write("CollisionPlane" + str(CollisionPlane_num) + "=" + str(round(vector_to_plane.x, 6)) + " " + str(round(vector_to_plane.y, 6)) + " " + str(round(vector_to_plane.z, 6)) + " " + str(round(vector_length, 6)) + "\n")
				CollisionPlane_num += 1

	for child in object.children:
		forChild(child,False,file, CollisionPlane_num)

# ImportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import (
		ImportHelper,
		ExportHelper,
		orientation_helper_factory,
		path_reference_mode,
		axis_conversion,
		)
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator


class ImportTch(Operator, ImportHelper):
	"""This appears in the tooltip of the operator and in the generated docs"""
	bl_idname = "import_tch.some_data"  # important since its how bpy.ops.import_tch.some_data is constructed
	bl_label = "Import KOTR tch"

	# ImportHelper mixin class uses this
	filename_ext = ".txt"

	filter_glob = StringProperty(
			default="*.txt",
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

class ExportTch(Operator, ExportHelper):
	"""This appears in the tooltip of the operator and in the generated docs"""
	bl_idname = "export_tch.some_data"  # important since its how bpy.ops.import_tch.some_data is constructed
	bl_label = "Export KOTR tch"

	# ImportHelper mixin class uses this
	filename_ext = ".tch"

	filter_glob = StringProperty(
			default="*.tch",
			options={'HIDDEN'},
			maxlen=255,  # Max internal buffer length, longer would be clamped.
			)

	def execute(self, context):
		return export_tch(context, self.filepath)


# Only needed if you want to add into a dynamic menu
def menu_func_import(self, context):
	self.layout.operator(ImportTch.bl_idname, text="Import KOTR tch")

def menu_func_export(self, context):
	self.layout.operator(ExportTch.bl_idname, text="Export KOTR tch")


def register():
	bpy.utils.register_class(ImportTch)
	bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
	bpy.utils.register_class(ExportTch)
	bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
	bpy.utils.unregister_class(ImportTch)
	bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
	bpy.utils.unregister_class(ExportTch)
	bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)


if __name__ == "__main__":
	register()

	# test call
	bpy.ops.import_tch.some_data('INVOKE_DEFAULT')
