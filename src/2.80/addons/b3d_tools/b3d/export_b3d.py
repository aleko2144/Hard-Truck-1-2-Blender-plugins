import struct
import sys
from pathlib import Path

import bpy
from mathutils import Vector
from bpy.props import *
import os.path

from math import cos
from math import sin



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

from .scripts import (
	prop
)

from ..consts import (
	LEVEL_GROUP,
	BLOCK_TYPE
)

from ..common import (
	log
)

from .common import (
	getColPropertyByName,
	getMaterialIndexInRES,
	getNonCopyName,
	isRootObj,
	getRootObj,
	isEmptyName,
	getAllChildren,
	getMultObjBoundingSphere,
	getSingleCoundingSphere,
	srgb_to_rgb,
	writeSize,
	readRESSections,
	getActivePaletteModule,
	getMatTextureRefDict

)

from .imghelp import (
	convertTGA32toTXR
)

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


def export_pro(file, textures_path):
	# file = open(myFile_pro+'.pro','w')

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

def cString(txt, file):
	if txt[-1] != "\00":
		txt += "\00"
	file.write(txt.encode("cp1251"))


def getRoomName(curResModule, roomString):
	result = ''
	roomSplit = roomString.split(':')
	resModule = roomSplit[0]
	roomName = roomSplit[1]

	if curResModule == resModule:
		result = roomName
	else:
		result = roomString

	return result

borders = {}
currentRes = ''
currentRoomName = ''

meshesInEmpty = {}
emptyToMeshKeys = {}
uniqueArrays = {}
createdBounders = {}

def fillBoundingSphereLists():

	global meshesInEmpty
	global emptyToMeshKeys
	global uniqueArrays
	global createdBounders

	# Getting 'empty' objects
	objs = [cn for cn in bpy.data.objects if cn.get(BLOCK_TYPE) in [8, 28, 35]]

	for obj in objs:
		curMeshName = obj.name
		curObj = obj.parent
		while not isRootObj(curObj):
			if curObj.get(BLOCK_TYPE) != 444:
				if meshesInEmpty.get(curObj.name) is None:
					meshesInEmpty[curObj.name] = []
					meshesInEmpty[curObj.name].append({
						"obj": curMeshName,
						"transf": curMeshName
					})
				else:
					meshesInEmpty[curObj.name].append({
						"obj": curMeshName,
						"transf": curMeshName
					})

			curObj = curObj.parent

	#extend with 18 blocks
	objs = [cn for cn in bpy.data.objects if cn.get(BLOCK_TYPE) == 18]

	for obj in objs:
		referenceableName = obj.get(prop(b_18.Add_Name))
		spaceName = obj.get(prop(b_18.Space_Name))
		curMeshList = meshesInEmpty.get(referenceableName)
		if curMeshList is not None:

			# global coords for 18 blocks parents
			globalTransfMeshList = [{
				"obj": cn.get("obj"),
				"transf": spaceName
				# "transf": cn.get("transf")
			} for cn in curMeshList]

			curObj = obj.parent
			while not isRootObj(curObj):
				if curObj.get(BLOCK_TYPE) != 444:
					if meshesInEmpty.get(curObj.name) is None:
						meshesInEmpty[curObj.name] = []
						meshesInEmpty[curObj.name].extend(globalTransfMeshList)
					else:
						meshesInEmpty[curObj.name].extend(globalTransfMeshList)

				curObj = curObj.parent

			# local coords for 18 block itself
			curObj = obj
			localTransfMeshList = [{
				"obj": cn.get("obj"),
				# "transf": spaceName
				"transf": cn.get("transf")
			} for cn in curMeshList]

			if meshesInEmpty.get(curObj.name) is None:
				meshesInEmpty[curObj.name] = []
				meshesInEmpty[curObj.name].extend(localTransfMeshList)
			else:
				meshesInEmpty[curObj.name].extend(localTransfMeshList)

	# meshesInEmptyStr = [str(cn) for cn in meshesInEmpty.values()]

	# for m in meshesInEmptyStr:
	# 	log.debug(m)

	for emptyName in meshesInEmpty.keys():
		meshesInEmpty[emptyName].sort(key= lambda x: "{}{}".format(str(x["obj"]), str(x["transf"])))

		key = "||".join(["{}{}".format(str(cn["obj"]), str(cn["transf"])) for cn in meshesInEmpty[emptyName]])
		emptyToMeshKeys[emptyName] = key
		if not key in uniqueArrays:
			uniqueArrays[key] = meshesInEmpty[emptyName]

	for key in uniqueArrays.keys():
		# objArr = [bpy.data.objects[cn] for cn in uniqueArrays[key]]
		# createdBounders[key] = getMultObjBoundingSphere(objArr)
		createdBounders[key] = getMultObjBoundingSphere(uniqueArrays[key])


def createBorderList():

	global borders
	global currentRes
	borders = {}

	borderBlocks = [cn for cn in bpy.data.objects if cn.get(BLOCK_TYPE) == 30 \
		and (cn.get(prop(b_30.ResModule1)) == currentRes or cn.get(prop(b_30.ResModule2)) == currentRes)]

	for bb in borderBlocks:

		border1 = '{}:{}'.format(bb[prop(b_30.ResModule1)], bb[prop(b_30.RoomName1)])
		border2 = '{}:{}'.format(bb[prop(b_30.ResModule2)], bb[prop(b_30.RoomName2)])

		if not border1 in borders:
			borders[border1] = []
			borders[border1].append(bb)
		else:
			borders[border1].append(bb)

		if not border2 in borders:
			borders[border2] = []
			borders[border2].append(bb)
		else:
			borders[border2].append(bb)


def writeMeshSphere(file, obj):

	blockType = obj.get(BLOCK_TYPE)

	if blockType in [
		8,35,
		28,30
	]:
		result = getSingleCoundingSphere(obj)
		center = result[0]
		rad = result[1]

		file.write(struct.pack("<3f", *center))
		file.write(struct.pack("<f", rad))


def writeCalculatedSphere(file, obj):
	global createdBounders
	global emptyToMeshKeys

	blockType = obj.get(BLOCK_TYPE)

	center = (0.0, 0.0, 0.0)
	rad = 0.0

	# objects with children
	if blockType in [
		2,3,4,5,6,7,9,
		10,11,18,19,21,24,
		26,29,33,36,37,39
	]:
		key = emptyToMeshKeys.get(obj.name)
		if key is not None:
			result = createdBounders.get(key)
			center = result[0]
			rad = result[1]

	file.write(struct.pack("<3f", *center))
	file.write(struct.pack("<f", rad))


def writeBoundSphere(file, center, rad):
	file.write(struct.pack("<3f", *center))
	file.write(struct.pack("<f", rad))


# def writeSize(file, ms):
# 	endMs = file.tell()
# 	size = endMs - ms - 4
# 	file.seek(ms, 0)
# 	file.write(struct.pack("<i", size))
# 	file.seek(endMs, 0)


def saveImageAs(image, path):

	scene = bpy.data.scenes.new("Temp")

	name = os.path.basename(path)

	show_name = image.name
	image.name = name

	# use docs.blender.org/api/current/bpy.types.ImageFormatSettings.html for more properties
	settings = scene.render.image_settings
	settings.file_format = 'TARGA_RAW'  # Options: 'BMP', 'IRIS', 'PNG', 'JPEG', 'JPEG2000', 'TARGA', 'TARGA_RAW', 'CINEON', 'DPX', 'OPEN_EXR_MULTILAYER', 'OPEN_EXR', 'HDR', 'TIFF', 'WEBP'
	# settings.color_depth = '32'
	# settings.color_management = 'OVERRIDE'
	settings.color_mode = 'RGBA'
	settings.compression = 0
	settings.quality = 100


	image.save_render(path, scene=scene)

	bpy.data.scenes.remove(scene)
	image.name = show_name


def writePALETTEFILES(resModule, file):

	size = 0
	if len(resModule.palette_colors) > 0:
		size = 1

	cString("PALETTEFILES {}".format(size), file)
	if size > 0:
		palette_name = resModule.palette_name
		if palette_name is None or len(palette_name) == 0:
			palette_name = "{}.plm".format(resModule.value)
		cString("{}".format(palette_name), file)
		PalName_ms = file.tell()
		file.seek(4,1)
		file.write("PALT".encode("cp1251"))
		PALT_ms = file.tell()
		file.seek(4,1)
		file.write("PLM\00".encode("cp1251"))
		PLM_ms = file.tell()
		file.seek(4,1)
		for color in resModule.palette_colors:
			rgbcol = srgb_to_rgb(*color.value[:3])
			file.write(struct.pack("<B", rgbcol[0]))
			file.write(struct.pack("<B", rgbcol[1]))
			file.write(struct.pack("<B", rgbcol[2]))

		writeSize(file, PalName_ms)
		writeSize(file, PALT_ms)
		writeSize(file, PLM_ms)


def writeSOUNDFILES(resModule, file):
	size = 0
	cString("SOUNDFILES {}".format(0), file)


def writeBACKFILES(resModule, file):
	size = 0
	cString("BACKFILES {}".format(0), file)


def writeMASKFILES(resModule, file):
	size = 0
	cString("MASKFILES {}".format(0), file)


def writeTEXTUREFILES(resModule, file, filepath, saveImages = True):
	size = len(resModule.textures)

	cString("TEXTUREFILES {}".format(size), file)
	if size > 0:
		exportFolder = os.path.dirname(filepath)
		basename = os.path.basename(filepath)[:-4]
		exportFolder = os.path.join(exportFolder, '{}_export'.format(basename))
		exportFolderPath = Path(exportFolder)
		exportFolderPath.mkdir(exist_ok=True, parents=True)

		maatToTexture, textureToMat = getMatTextureRefDict(resModule)
		paletteModule = getActivePaletteModule(resModule)
		palette = paletteModule.palette_colors

		for i, texture in enumerate(resModule.textures):
			usedInMat = resModule.materials[textureToMat[i]]
			transpColor = (0,0,0)
			if usedInMat.tex_type == 'ttx' and usedInMat.is_col:
				transpColor = srgb_to_rgb(*(palette[usedInMat.col-1].value[:3]))

			imageName = "{}.tga".format(os.path.splitext(texture.name)[0])
			imagePath = os.path.join(exportFolder, imageName)
			textureName = "{}\\{}".format(texture.subpath.rstrip("\\"), "{}.txr".format(os.path.splitext(texture.name)[0]))

			texParams = []
			if texture.is_someint:
				texParams.append("{}".format(texture.someint))

			for param in ["noload", "bumpcoord", "memfix"]:
				if getattr(texture, 'is_{}'.format(param)):
					texParams.append("{}".format(param))

			if len(texParams) > 0:
				texStr = "{} {}".format(textureName, "  ".join(texParams))
			else:
				texStr = textureName
			cString(texStr, file)

			if saveImages:
				saveImageAs(texture.id_value, imagePath)

			convertTGA32toTXR(imagePath, 2, texture.img_type, texture.img_format, texture.has_mipmap, transpColor)

			TextureSize_ms = file.tell()
			file.write(struct.pack("<i", 0))
			outpath = os.path.splitext(imagePath)[0] + ".txr"
			with open(outpath, "rb") as txrFile:
				txrText = txrFile.read()
			file.write(txrText)
			writeSize(file, TextureSize_ms)
			file.write(struct.pack('<i', 0))



def writeMATERIALS(resModule, file):
	size = len(resModule.materials)
	cString("MATERIALS {}".format(size), file)
	if size > 0:
		for material in resModule.materials:
			if material.id_value is not None:
				matName = material.id_value.name
				matStr = matName
				matParams = []
				if material.is_tex:
					matParams.append("{} {}".format(material.tex_type, material.tex))
				for param in ["col", "att", "msk", "power", "coord"]:
					if getattr(material, 'is_{}'.format(param)):
						matParams.append("{} {}".format(param, getattr(material, param)))
				for param in ["reflect", "specular", "transp", "rot"]:
					if getattr(material, 'is_{}'.format(param)):
						matParams.append("{} {:.2f}".format(param, float(getattr(material, param))))
				for param in ["noz", "nof", "notile", "notileu", "notilev", \
                                "alphamirr", "bumpcoord", "usecol", "wave"]:
					if getattr(material, 'is_{}'.format(param)):
						matParams.append("{}".format(param))
				for param in ["RotPoint", "move", "env"]:
					if getattr(material, 'is_{}'.format(param)):
						matParams.append("{} {:.2f} {:.2f}".format(param, getattr(material, param)[0], getattr(material, param)[1]))
				if material.is_envId:
					matParams.append("env{}".format(material.envId))

				matStr = "{} {}".format(matName, "  ".join(matParams))
				cString(matStr, file)

def writeCOLORS(resModule, file):
	size = 0
	cString("COLORS {}".format(0), file)


def writeSOUNDS(resModule, file):
	size = 0
	cString("SOUNDS {}".format(0), file)



def exportRes(context, op, exportDir):
	mytool = bpy.context.scene.my_tool

	exportedModules = [sn.name for sn in op.res_modules if sn.state == True]

	if not os.path.isdir(exportDir):
		exportDir = os.path.dirname(exportDir)

	for moduleName in exportedModules:

		resModule = getColPropertyByName(mytool.resModules, moduleName)
		if resModule is not None:

			filepath = os.path.join(exportDir, "{}.res".format(resModule.value))

			if op.to_merge:

				# allSections = ["PALETTEFILES", "SOUNDFILES", "SOUNDS", "BACKFILES", "MASKFILES", "COLORS", "TEXTUREFILES", "MATERIALS"]

				if not os.path.exists(filepath):
					log.error("Not found file to merge into: {}".format(filepath))
					continue

				sections = readRESSections(filepath)

				sectionsToMerge = [cn.name for cn in op.res_sections if cn.state == True]

				with open(filepath, "wb") as file:
					for section in sections:
						log.debug(section['name'])
						if section['name'] in sectionsToMerge:
							if section['name'] == 'TEXTUREFILES':
								writeTEXTUREFILES(resModule, file, filepath, op.export_images)
							elif section['name'] == 'PALETTEFILES':
								writePALETTEFILES(resModule, file)
							elif section['name'] == 'MASKFILES':
								writeMASKFILES(resModule, file)
							elif section['name'] == 'MATERIALS':
								writeMATERIALS(resModule, file)
						else:
							cString("{} {}".format(section['name'], section['cnt']), file)
							if section['name'] in ["COLORS", "MATERIALS", "SOUNDS"]:
								for data in section['data']:
									cString(data['row'], file)
							else:
								for data in section['data']:
									cString(data['row'], file)
									file.write(struct.pack('<i', data['size']))
									file.write(data['bytes'])

			else:
				with open(filepath, 'wb') as file:

					writePALETTEFILES(resModule, file)
					writeSOUNDFILES(resModule, file)
					writeBACKFILES(resModule, file)
					writeMASKFILES(resModule, file)
					writeCOLORS(resModule, file)
					writeTEXTUREFILES(resModule, file, filepath, op.export_images)
					writeMATERIALS(resModule, file)



def exportB3d(context, op, filepath):

	global currentRes

	global meshesInEmpty
	global emptyToMeshKeys
	global uniqueArrays
	global createdBounders

	meshesInEmpty = {}
	emptyToMeshKeys = {}
	uniqueArrays = {}
	createdBounders = {}

	fillBoundingSphereLists()

	file = open(filepath, 'wb')

	materials = []

	for material in bpy.data.materials:
		materials.append(material.name)

	cp_materials = 0
	cp_data_blocks = 0
	cp_eof = 0

	#Header

	file.write(b'b3d\x00')#struct.pack("4c",b'B',b'3',b'D',b'\x00'))

	file.write(struct.pack('<i',0)) #File Size
	file.write(struct.pack('<i',0)) #Mat list offset
	file.write(struct.pack('<i',0)) #Mat list Data Size
	file.write(struct.pack('<i',0)) #Data Chunks Offset
	file.write(struct.pack('<i',0)) #Data Chunks Size

	cp_materials = int(file.tell()/4)

	objs = [cn for cn in bpy.data.objects if isRootObj(cn)]
	# curRoot = objs[0]
	obj = bpy.context.object
	curRoot = getRootObj(obj)

	allObjs = []

	if isRootObj(obj):
		allObjs = curRoot.children
	else:
		allObjs = [obj]

	spaces = [cn for cn in allObjs if cn.get(BLOCK_TYPE) == 24]
	other = [cn for cn in allObjs if cn.get(BLOCK_TYPE) != 24]

	rChild = []
	rChild.extend(spaces)
	rChild.extend(other)

	resModules = bpy.context.scene.my_tool.resModules
	curResName = curRoot.name[:-4]
	curModule = getColPropertyByName(resModules, curResName)

	currentRes = curResName
	createBorderList()

	file.write(struct.pack('<i', len(curModule.materials))) #Materials Count
	for mat in curModule.materials:
		writeName(mat.value, file)

	cp_data_blocks = int(file.tell()/4)

	curMaxCnt = 0
	curLevel = 0

	file.write(struct.pack("<i",111)) # Begin_Chunks

	# prevLevel = 0
	if len(rChild) > 0:
		for obj in rChild[:-1]:
			if obj.get(BLOCK_TYPE) == 10 or obj.get(BLOCK_TYPE) == 9:
				curMaxCnt = 2
			elif obj.get(BLOCK_TYPE) == 21:
				curMaxCnt = obj[prop(b_21.GroupCnt)]
			exportBlock(obj, False, curLevel, curMaxCnt, [0], {}, file)

			file.write(struct.pack("<i", 444))

		obj = rChild[-1]
		if obj.get(BLOCK_TYPE) == 10 or obj.get(BLOCK_TYPE) == 9:
			curMaxCnt = 2
		elif obj.get(BLOCK_TYPE) == 21:
			curMaxCnt = obj[prop(b_21.GroupCnt)]
		exportBlock(obj, False, curLevel, curMaxCnt, [0], {}, file)

	file.write(struct.pack("<i",222))#EOF

	cp_eof = int(file.tell()/4)

	file.seek(4,0)
	file.write(struct.pack("<i", cp_eof))
	file.seek(8,0)
	file.write(struct.pack("<i", cp_materials))
	file.seek(12,0)
	file.write(struct.pack("<i", cp_data_blocks - cp_materials))
	file.seek(16,0)
	file.write(struct.pack("<i", cp_data_blocks))
	file.seek(20,0)
	file.write(struct.pack("<i", cp_eof - cp_data_blocks))

def commonSort(curCenter, arr):
	global createdBounders
	global emptyToMeshKeys

	def dist(curCenter, obj):

		center = None
		rad = None

		key = emptyToMeshKeys.get(obj.name)
		if key is not None:
			result = createdBounders.get(key)
			center = result[0]
			rad = result[1]

		if center is None or rad is None:
			return 0
		else:
			return (sum(map(lambda xx,yy : (xx-yy)**2,curCenter,center)))**0.5

	newList = [(obj, dist(curCenter, obj)) for obj in arr]
	newList.sort(key= lambda x: x[1])
	return list(map(lambda x: x[0], newList))

def exportBlock(obj, isLast, curLevel, maxGroups, curGroups, extra, file):

	global borders
	global currentRes
	global currentRoomName

	toProcessChild = False
	curMaxCnt = 0

	block = obj

	objName = getNonCopyName(block.name)
	objType = block.get(BLOCK_TYPE)

	passToMesh = {}

	if objType != None:

		log.debug("{}_{}_{}_{}".format(block.get(BLOCK_TYPE), curLevel, 0, block.name))

		blChildren = list(block.children)

		curCenter = None
		curCenter = list(block.location)

		if objType == 444:
			if int(block.name[6]) > 0:
				file.write(struct.pack("<i",444))#Group Chunk

			blChildren = commonSort(curCenter, blChildren)

			if(len(blChildren) > 0):
				for i, ch in enumerate(blChildren[:-1]):

					exportBlock(ch, False, curLevel+1, curMaxCnt, curGroups, extra, file)

				exportBlock(blChildren[-1], True, curLevel+1, curMaxCnt, curGroups, extra, file)

		else:

			file.write(struct.pack("<i",333))#Begin Chunk

			if objType not in [9, 10, 21]:
				blChildren = commonSort(curCenter, blChildren)

			if objType == 30:
				writeName('', file)
			else:
				writeName(objName, file)

			file.write(struct.pack("<i", objType))

			if objType == 0:
				file.write(bytearray(b'\x00'*44))

			elif objType == 1:

				writeName(block[prop(b_1.Name1)], file)
				writeName(block[prop(b_1.Name2)], file)

			elif objType == 2:

				writeCalculatedSphere(file, block)
				file.write(struct.pack("<3f", *block[prop(b_2.Unk_XYZ)]))
				file.write(struct.pack("<f", block[prop(b_2.Unk_R)]))

				file.write(struct.pack("<i", len(block.children)))

				toProcessChild = True

			elif objType == 3:

				writeCalculatedSphere(file, block)

				file.write(struct.pack("<i", len(block.children)))

				toProcessChild = True

			elif objType == 4:

				writeCalculatedSphere(file, block)
				writeName(block[prop(b_4.Name1)], file)
				writeName(block[prop(b_4.Name2)], file)

				file.write(struct.pack("<i", len(block.children)))

				toProcessChild = True

			elif objType == 5:

				writeCalculatedSphere(file, block)
				writeName(block[prop(b_5.Name1)], file)

				file.write(struct.pack("<i", len(block.children)))

				toProcessChild = True

			elif objType == 6:

				writeCalculatedSphere(file, block)
				writeName(block[prop(b_6.Name1)], file)
				writeName(block[prop(b_6.Name2)], file)

				offset = 0
				allChildren = [cn for cn in getAllChildren(block) if cn.get(BLOCK_TYPE) and cn.get(BLOCK_TYPE) in [35, 8, 28]]
				for ch in allChildren:
					obj = bpy.data.objects[ch.name]
					someProps = getMeshProps(obj)
					passToMesh[obj.name] = {
						"offset": offset,
						"props": someProps
					}
					offset += len(someProps[0])

				file.write(struct.pack("<i", offset)) #Vertex count

				for mesh in passToMesh.values():
					verts, uvs, normals, faces, local_verts = mesh['props']
					for i, v in enumerate(verts):
						file.write(struct.pack("<3f", *v))
						file.write(struct.pack("<f", uvs[i][0]))
						file.write(struct.pack("<f", 1 - uvs[i][1]))

				file.write(struct.pack("<i", len(block.children)))

				toProcessChild = True

			elif objType == 7:

				writeCalculatedSphere(file, block)
				writeName(block[prop(b_7.Name1)], file)

				offset = 0
				allChildren = [cn for cn in getAllChildren(block) if cn.get(BLOCK_TYPE) and cn.get(BLOCK_TYPE) in [35, 8, 28]]
				for ch in allChildren:
					obj = bpy.data.objects[ch.name]
					someProps = getMeshProps(obj)
					passToMesh[obj.name] = {
						"offset": offset,
						"props": someProps
					}
					offset += len(someProps[0])

				file.write(struct.pack("<i", offset)) #Vertex count

				for mesh in passToMesh.values():
					verts, uvs, normals, faces, local_verts = mesh['props']
					for i, v in enumerate(verts):
						file.write(struct.pack("<3f", *v))
						file.write(struct.pack("<f", uvs[i][0]))
						file.write(struct.pack("<f", 1 - uvs[i][1]))

				file.write(struct.pack("<i", len(block.children)))

				toProcessChild = True

			elif objType == 8:

				l_passToMesh = extra['passToMesh'][block.name]

				offset = l_passToMesh['offset']
				verts, uvs, normals, polygons, local_verts = l_passToMesh['props']

				writeMeshSphere(file, block)
				# file.write(struct.pack("<i", 0)) # PolygonCount
				file.write(struct.pack("<i", len(polygons))) #Polygon count

				format_flags_attrs = obj.data.attributes.get(prop(pfb_8.Format_Flags))
				if format_flags_attrs is not None:
					format_flags_attrs = format_flags_attrs.data

				mesh = block.data

				for poly in polygons:
					format = 0
					uvCount = 0
					useNormals = False
					normalSwitch = False
					l_material_ind = getMaterialIndexInRES(obj.data.materials[poly.material_index].name)
					if format_flags_attrs is None:
						formatRaw = 2 # default
					else:
						formatRaw = format_flags_attrs[poly.index].value
					# formatRaw = 0 #temporary
					file.write(struct.pack("<i", formatRaw))
					file.write(struct.pack("<f", 1.0)) # TODO: not consts
					file.write(struct.pack("<i", 32767)) # TODO: not consts
					file.write(struct.pack("<i", l_material_ind))
					file.write(struct.pack("<i", len(poly.vertices)))

					format = formatRaw ^ 1
					uvCount = ((format & 0xFF00) >> 8)

					if format & 0b10:
						uvCount += 1

					if format & 0b100000 and format & 0b10000:
						useNormals = True
						if format & 0b1:
							normalSwitch = True
						else:
							normalSwitch = False

					l_uvs = {}
					for li in poly.loop_indices:
						vi = mesh.loops[li].vertex_index
						l_uvs[vi] = mesh.uv_layers['UVMap'].data[li].uv

					for i, vert in enumerate(poly.vertices):
						file.write(struct.pack("<i", offset + vert))
						for k in range(uvCount):
							file.write(struct.pack("<f", l_uvs[vert][0]))
							file.write(struct.pack("<f", 1 - l_uvs[vert][1]))
						if useNormals:
							if normalSwitch:
								file.write(struct.pack("<3f", *normals[vert]))
							else:
								file.write(struct.pack("<f", 1.0))

			elif objType == 9 or objType == 22:

				writeCalculatedSphere(file, block)
				file.write(struct.pack("<3f", *block[prop(b_9.Unk_XYZ)]))
				file.write(struct.pack("<f", block[prop(b_9.Unk_R)]))

				childCnt = 0
				for ch in block.children:
					childCnt += len(ch.children)

				file.write(struct.pack("<i", childCnt))

				toProcessChild = True
				curMaxCnt = 2
				# maxGroups = 2

			elif objType == 10:

				writeCalculatedSphere(file, block)
				file.write(struct.pack("<3f", *block[prop(b_10.LOD_XYZ)]))
				file.write(struct.pack("<f", block[prop(b_10.LOD_R)]))

				childCnt = 0
				for ch in block.children:
					childCnt += len(ch.children)

				file.write(struct.pack("<i", childCnt))

				toProcessChild = True
				curMaxCnt = 2

			elif objType == 11:

				writeCalculatedSphere(file, block)
				file.write(struct.pack("<3f", *block[prop(b_11.Unk_XYZ1)]))
				file.write(struct.pack("<3f", *block[prop(b_11.Unk_XYZ2)]))
				file.write(struct.pack("<f", block[prop(b_11.Unk_R1)]))
				file.write(struct.pack("<f", block[prop(b_11.Unk_R2)]))

				file.write(struct.pack("<i", len(block.children)))

				toProcessChild = True

			elif objType == 12:

				writeBoundSphere(file, (0.0,0.0,0.0), 0.0)
				file.write(struct.pack("<3f", *block[prop(b_12.Unk_XYZ)]))
				file.write(struct.pack("<f", block[prop(b_12.Unk_R)]))
				file.write(struct.pack("<i", block[prop(b_12.Unk_Int1)]))
				file.write(struct.pack("<i", block[prop(b_12.Unk_Int2)]))
				itemList = block[prop(b_12.Unk_List)]
				# file.write(struct.pack("<i", 0)) #Params Count
				file.write(struct.pack("<i", len(itemList)))

				for item in itemList:
					file.write(struct.pack("<f", item))

			elif objType == 13:

				writeBoundSphere(file, (0.0,0.0,0.0), 0.0)
				file.write(struct.pack("<i", block[prop(b_13.Unk_Int1)]))
				file.write(struct.pack("<i", block[prop(b_13.Unk_Int2)]))
				itemList = block[prop(b_13.Unk_List)]
				# file.write(struct.pack("<i", 0)) #Params Count
				file.write(struct.pack("<i", len(itemList)))

				for item in itemList:
					file.write(struct.pack("<f", item))

			elif objType == 14:

				writeBoundSphere(file, (0.0,0.0,0.0), 0.0)
				file.write(struct.pack("<3f", *block[prop(b_14.Unk_XYZ)]))
				file.write(struct.pack("<f", block[prop(b_14.Unk_R)]))
				file.write(struct.pack("<i", block[prop(b_14.Unk_Int1)]))
				file.write(struct.pack("<i", block[prop(b_14.Unk_Int2)]))
				itemList = block[prop(b_14.Unk_List)]
				# file.write(struct.pack("<i", 0)) #Params Count
				file.write(struct.pack("<i", len(itemList)))

				for item in itemList:
					file.write(struct.pack("<f", item))

			elif objType == 15:

				writeBoundSphere(file, (0.0,0.0,0.0), 0.0)
				file.write(struct.pack("<i", block[prop(b_15.Unk_Int1)]))
				file.write(struct.pack("<i", block[prop(b_15.Unk_Int2)]))
				itemList = block[prop(b_15.Unk_List)]
				# file.write(struct.pack("<i", 0)) #Params Count
				file.write(struct.pack("<i", len(itemList)))

				for item in itemList:
					file.write(struct.pack("<f", item))

			elif objType == 16:

				writeBoundSphere(file, (0.0,0.0,0.0), 0.0)
				file.write(struct.pack("<3f", *block[prop(b_16.Unk_XYZ1)]))
				file.write(struct.pack("<3f", *block[prop(b_16.Unk_XYZ2)]))
				file.write(struct.pack("<f", block[prop(b_16.Unk_Float1)]))
				file.write(struct.pack("<f", block[prop(b_16.Unk_Float2)]))
				file.write(struct.pack("<i", block[prop(b_16.Unk_Int1)]))
				file.write(struct.pack("<i", block[prop(b_16.Unk_Int2)]))
				itemList = block[prop(b_16.Unk_List)]
				# file.write(struct.pack("<i", 0)) #Params Count
				file.write(struct.pack("<i", len(itemList)))

				for item in itemList:
					file.write(struct.pack("<f", item))

			elif objType == 17:

				writeBoundSphere(file, (0.0,0.0,0.0), 0.0)
				file.write(struct.pack("<3f", *block[prop(b_17.Unk_XYZ1)]))
				file.write(struct.pack("<3f", *block[prop(b_17.Unk_XYZ2)]))
				file.write(struct.pack("<f", block[prop(b_17.Unk_Float1)]))
				file.write(struct.pack("<f", block[prop(b_17.Unk_Float2)]))
				file.write(struct.pack("<i", block[prop(b_17.Unk_Int1)]))
				file.write(struct.pack("<i", block[prop(b_17.Unk_Int2)]))
				itemList = block[prop(b_17.Unk_List)]
				# file.write(struct.pack("<i", 0)) #Params Count
				file.write(struct.pack("<i", len(itemList)))

				for item in itemList:
					file.write(struct.pack("<f", item))

			elif objType == 18:

				writeCalculatedSphere(file, block)
				writeName(block[prop(b_18.Space_Name)], file)
				writeName(block[prop(b_18.Add_Name)], file)

			elif objType == 19:

				currentRoomName = '{}:{}'.format(currentRes, objName)
				borderBlocks = borders[currentRoomName]
				blChildren.extend(borderBlocks)

				file.write(struct.pack("<i", len(blChildren)))

				toProcessChild = True

			elif objType == 20:

				writeBoundSphere(file, (0.0,0.0,0.0), 0.0)
				pointList = []
				for sp in block.data.splines:
					for point in sp.points:
						pointList.append(point.co)
				# file.write(struct.pack("<i", 0)) #Verts Count
				file.write(struct.pack("<i", len(pointList))) #Verts Count
				file.write(struct.pack("<i", block[prop(b_20.Unk_Int1)]))
				file.write(struct.pack("<i", block[prop(b_20.Unk_Int2)]))

				# Unknowns list
				itemList = block[prop(b_20.Unk_List)]
				file.write(struct.pack("<i", len(itemList)))
				for item in itemList:
					file.write(struct.pack("<f", item))

				# Points list
				for point in pointList:
					file.write(struct.pack("<f", point.x))
					file.write(struct.pack("<f", point.y))
					file.write(struct.pack("<f", point.z))

			elif objType == 21:

				writeCalculatedSphere(file, block)
				file.write(struct.pack("<i", block[prop(b_21.GroupCnt)]))
				file.write(struct.pack("<i", block[prop(b_21.Unk_Int2)]))

				childCnt = 0
				for ch in block.children:
					childCnt += len(ch.children)

				file.write(struct.pack("<i", childCnt))

				toProcessChild = True
				curMaxCnt = block[prop(b_21.GroupCnt)]

			elif objType == 23:

				file.write(struct.pack("<i", block[prop(b_23.Unk_Int1)]))
				file.write(struct.pack("<i", block[prop(b_23.Surface)]))
				# file.write(struct.pack("<i", 0)) #Params Count

				# Unknowns list
				itemList = block[prop(b_23.Unk_List)]
				file.write(struct.pack("<i", len(itemList)))
				for item in itemList:
					file.write(struct.pack("<i", item))

				# Points list
				mesh = block.data
				file.write(struct.pack("<i", len(mesh.polygons)))
				for poly in mesh.polygons:
					file.write(struct.pack("<i", len(poly.vertices)))
					l_vertexes = poly.vertices
					for vert in poly.vertices:
						file.write(struct.pack("<3f", *(block.matrix_world @ Vector(mesh.vertices[vert].co))))

				# file.write(struct.pack("<i", 0)) #Verts Count

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


				file.write(struct.pack("<f", block.location.x))
				file.write(struct.pack("<f", block.location.y))
				file.write(struct.pack("<f", block.location.z))

				file.write(struct.pack("<i", block[prop(b_24.Flag)]))

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

				writeCalculatedSphere(file, block)
				file.write(struct.pack("<3f", *block[prop(b_26.Unk_XYZ1)]))
				file.write(struct.pack("<3f", *block[prop(b_26.Unk_XYZ2)]))
				file.write(struct.pack("<3f", *block[prop(b_26.Unk_XYZ3)]))

				file.write(struct.pack("<i", len(block.children)))

				toProcessChild = True

			elif objType == 27:

				writeBoundSphere(file, (0.0,0.0,0.0), 0.0)
				file.write(struct.pack("<i", block[prop(b_27.Flag)]))
				file.write(struct.pack("<3f", *block[prop(b_27.Unk_XYZ)]))
				file.write(struct.pack("<i", block[prop(b_27.Material)]))

			elif objType == 28: #must be 4 coord plane

				# sprite_center = block[prop(b_28.Sprite_Center)]
				sprite_center = 0.125 * sum((Vector(b) for b in block.bound_box), Vector())
				sprite_center = block.matrix_world @ sprite_center

				writeMeshSphere(file, block)
				file.write(struct.pack("<3f", *block.location)) #sprite center


				format_flags_attrs = obj.data.attributes[prop(pfb_28.Format_Flags)].data
				someProps = getMeshProps(obj)

				mesh = block.data

				l_verts = someProps[4]
				# l_uvs = someProps[1]
				l_normals = someProps[2]
				l_polygons = someProps[3]
				l_material = obj.data.materials[obj.data.polygons[0].material_index].name

				file.write(struct.pack("<i", len(l_polygons)))

				for poly in l_polygons:

					l_uvs = {}
					for li in poly.loop_indices:
						vi = mesh.loops[li].vertex_index
						l_uvs[vi] = mesh.uv_layers['UVMap'].data[li].uv

					verts = poly.vertices

					formatRaw = format_flags_attrs[poly.index].value

					file.write(struct.pack("<i", formatRaw)) # format with UVs TODO: not consts
					file.write(struct.pack("<f", 1.0)) # TODO: not consts
					file.write(struct.pack("<i", 32767)) # TODO: not consts
					file.write(struct.pack("<i", getMaterialIndexInRES(l_material)))
					file.write(struct.pack("<i", len(verts)))
					for i, vert in enumerate(verts):
						# scale_u = sprite_center[1] - l_verts[vert][1]
						# scale_v = l_verts[vert][2] - sprite_center[2]
						scale_u = -l_verts[vert][1]
						scale_v = l_verts[vert][2]
						file.write(struct.pack("<f", scale_u))
						file.write(struct.pack("<f", scale_v))
						#UVs
						file.write(struct.pack("<f", l_uvs[vert][0]))
						file.write(struct.pack("<f", 1-l_uvs[vert][1]))

			elif objType == 29:

				writeCalculatedSphere(file, block)
				file.write(struct.pack("<i", block[prop(b_29.Unk_Int1)]))
				file.write(struct.pack("<i", block[prop(b_29.Unk_Int2)]))
				file.write(struct.pack("<3f", *block[prop(b_29.Unk_XYZ)]))
				file.write(struct.pack("<f", block[prop(b_29.Unk_R)]))

				file.write(struct.pack("<i", len(block.children)))

				toProcessChild = True

			elif objType == 30:

				writeMeshSphere(file, block)

				roomName1 = '{}:{}'.format(block[prop(b_30.ResModule1)], block[prop(b_30.RoomName1)])
				roomName2 = '{}:{}'.format(block[prop(b_30.ResModule2)], block[prop(b_30.RoomName2)])
				toImportSecondSide = False
				if currentRoomName == roomName1:
					toImportSecondSide = True
				elif currentRoomName == roomName2:
					toImportSecondSide = False

				if toImportSecondSide:
					writeName(getRoomName(currentRes, roomName2), file)
				else:
					writeName(getRoomName(currentRes, roomName1), file)

				vertexes = [block.matrix_world @ cn.co for cn in block.data.vertices]

				if toImportSecondSide:
					p1 = vertexes[0]
					p2 = vertexes[2]
				else:
					p1 = vertexes[1]
					p2 = vertexes[3]

				file.write(struct.pack("<3f", *p1))
				file.write(struct.pack("<3f", *p2))

			elif objType == 31:

				writeBoundSphere(file, (0.0,0.0,0.0), 0.0)
				file.write(struct.pack("<i", block[prop(b_31.Unk_Int1)]))
				file.write(struct.pack("<3f", *block[prop(b_31.Unk_XYZ1)]))
				file.write(struct.pack("<f", block[prop(b_31.Unk_R)]))
				file.write(struct.pack("<i", block[prop(b_31.Unk_Int2)]))
				file.write(struct.pack("<3f", *block[prop(b_31.Unk_XYZ2)]))

			elif objType == 33:

				writeCalculatedSphere(file, block)
				file.write(struct.pack("<i", block[prop(b_33.Use_Lights)]))
				file.write(struct.pack("<i", block[prop(b_33.Light_Type)]))
				file.write(struct.pack("<i", block[prop(b_33.Flag)]))
				file.write(struct.pack("<3f", *block[prop(b_33.Unk_XYZ1)]))
				file.write(struct.pack("<3f", *block[prop(b_33.Unk_XYZ2)]))
				file.write(struct.pack("<f", block[prop(b_33.Unk_Float1)]))
				file.write(struct.pack("<f", block[prop(b_33.Unk_Float2)]))
				file.write(struct.pack("<f", block[prop(b_33.Light_R)]))
				file.write(struct.pack("<f", block[prop(b_33.Intens)]))
				file.write(struct.pack("<f", block[prop(b_33.Unk_Float3)]))
				file.write(struct.pack("<f", block[prop(b_33.Unk_Float4)]))
				file.write(struct.pack("<3f", *block[prop(b_33.RGB)]))

				file.write(struct.pack("<i", len(block.children)))

				toProcessChild = True

			elif objType == 34:

				writeBoundSphere(file, (0.0,0.0,0.0), 0.0)
				file.write(struct.pack("<i", 0)) #skipped Int
				pointList = []
				for sp in block.data.splines:
					for point in sp.points:
						pointList.append(point.co)
				file.write(struct.pack("<i", len(pointList))) #Verts count
				for point in pointList:
					file.write(struct.pack("<f", point.x))
					file.write(struct.pack("<f", point.y))
					file.write(struct.pack("<f", point.z))
					file.write(struct.pack("<i", block[prop(b_34.UnkInt)]))

			elif objType == 35: #TODO: Texture coordinates are absent for moving texture(1)(mat_refl_road)(null))
								#probably UVMapVert1 on road objects = tp import them too

				l_passToMesh = extra['passToMesh'][block.name]

				offset = l_passToMesh['offset']
				verts, uvs, normals, polygons, local_verts = l_passToMesh['props']

				writeMeshSphere(file, block)
				file.write(struct.pack("<i", block[prop(b_35.MType)]))
				# file.write(struct.pack("<i", 3))
				file.write(struct.pack("<i", block[prop(b_35.TexNum)]))
				# file.write(struct.pack("<i", 0)) #Polygon count
				file.write(struct.pack("<i", len(polygons))) #Polygon count

				format_flags_attrs = obj.data.attributes[prop(pfb_35.Format_Flags)].data

				mesh = block.data

				for poly in polygons:
					format = 0
					uvCount = 0
					useNormals = False
					normalSwitch = False
					l_material_ind = getMaterialIndexInRES(obj.data.materials[poly.material_index].name)
					formatRaw = format_flags_attrs[poly.index].value
					# formatRaw = 0
					file.write(struct.pack("<i", formatRaw))
					file.write(struct.pack("<f", 1.0)) # TODO: not consts
					file.write(struct.pack("<i", 32767)) # TODO: not consts
					file.write(struct.pack("<i", l_material_ind))
					file.write(struct.pack("<i", len(poly.vertices))) #Verts count

					format = formatRaw ^ 1
					uvCount = ((format & 0xFF00) >> 8)

					if format & 0b10:
						uvCount += 1

					if format & 0b100000 and format & 0b10000:
						useNormals = True
						if format & 0b1:
							normalSwitch = True
						else:
							normalSwitch = False

					l_uvs = {}
					for li in poly.loop_indices:
						vi = mesh.loops[li].vertex_index
						l_uvs[vi] = mesh.uv_layers['UVMap'].data[li].uv

					for i, vert in enumerate(poly.vertices):
						file.write(struct.pack("<i", offset + vert))
						for k in range(uvCount):
							file.write(struct.pack("<f", l_uvs[vert][0]))
							file.write(struct.pack("<f", 1 - l_uvs[vert][1]))
						if useNormals:
							if normalSwitch:
								file.write(struct.pack("<3f", *normals[vert]))
							else:
								file.write(struct.pack("<f", 1.0))

			elif objType == 36:

				# isSecondUvs = False
				formatRaw = block[prop(b_36.VType)]
				normalSwitch = False
				writeCalculatedSphere(file, block)
				writeName(block[prop(b_36.Name1)], file)
				writeName(block[prop(b_36.Name2)], file)

				offset = 0
				allChildren = [cn for cn in getAllChildren(block) if cn.get(BLOCK_TYPE) and cn.get(BLOCK_TYPE) in [35, 8, 28]]
				for ch in allChildren:
					obj = bpy.data.objects[ch.name]
					someProps = getMeshProps(obj)
					passToMesh[obj.name] = {
						"offset": offset,
						"props": someProps
					}

					# if obj.data.uv_layers.get('UVmapVert1'):
					# 	isSecondUvs = True


					offset += len(someProps[0])

				#temporary
				# if isSecondUvs:
				# 	formatRaw = 258
				# else:
				# 	formatRaw = 2

				extraUvCount = formatRaw >> 8
				format = formatRaw & 0xFF

				if format == 1 or format == 2:
					normalSwitch = True
				elif format == 3:
					normalSwitch = False



				file.write(struct.pack("<i", formatRaw))
				file.write(struct.pack("<i", offset)) #Vertex count

				for mesh in passToMesh.values():
					verts, uvs, normals, faces, local_verts = mesh['props']
					for i, v in enumerate(verts):
						file.write(struct.pack("<3f", *v))
						file.write(struct.pack("<f", uvs[i][0]))
						file.write(struct.pack("<f", 1 - uvs[i][1]))

						for k in range(extraUvCount):
							file.write(struct.pack("<f", uvs[i][0]))
							file.write(struct.pack("<f", 1 - uvs[i][1]))

						if normalSwitch:
							file.write(struct.pack("<3f", *normals[i]))
						else:
							file.write(struct.pack("<f", 1.0))

				file.write(struct.pack("<i", len(block.children)))

				toProcessChild = True

			elif objType == 37:

				# isSecondUvs = False
				formatRaw = block[prop(b_37.VType)]
				normalSwitch = False
				writeCalculatedSphere(file, block)
				writeName(block[prop(b_37.Name1)], file)
				# file.write(struct.pack("<i", block[prop(b_37.VType)]))


				offset = 0
				allChildren = [cn for cn in getAllChildren(block) if cn.get(BLOCK_TYPE) and cn.get(BLOCK_TYPE) in [35, 8, 28]]
				for ch in allChildren:
					obj = bpy.data.objects[ch.name]
					someProps = getMeshProps(obj)
					passToMesh[obj.name] = {
						"offset": offset,
						"props": someProps
					}
					# if obj.data.uv_layers.get('UVmapVert1'):
					# 	isSecondUvs = True

					offset += len(someProps[0])

				# if isSecondUvs:
				# 	formatRaw = 258
				# else:
				# 	formatRaw = 2

				extraUvCount = formatRaw >> 8
				format = formatRaw & 0xFF

				if format == 1 or format == 2:
					normalSwitch = True
				elif format == 3:
					normalSwitch = False

				file.write(struct.pack("<i", formatRaw))

				file.write(struct.pack("<i", offset)) #Vertex count


				for mesh in passToMesh.values():
					verts, uvs, normals, faces, local_verts = mesh['props']
					for i, v in enumerate(verts):
						file.write(struct.pack("<3f", *v))
						file.write(struct.pack("<f", uvs[i][0]))
						file.write(struct.pack("<f", 1 - uvs[i][1]))

						for k in range(extraUvCount):
							file.write(struct.pack("<f", uvs[i][0]))
							file.write(struct.pack("<f", 1 - uvs[i][1]))

						if normalSwitch:
							file.write(struct.pack("<3f", *normals[i]))
						else:
							file.write(struct.pack("<f", 1.0))

				file.write(struct.pack("<i", len(block.children)))

				toProcessChild = True

			elif objType == 39:

				writeCalculatedSphere(file, block)
				file.write(struct.pack("<i", block[prop(b_39.Color_R)]))
				file.write(struct.pack("<f", block[prop(b_39.Unk_Float1)]))
				file.write(struct.pack("<f", block[prop(b_39.Fog_Start)]))
				file.write(struct.pack("<f", block[prop(b_39.Fog_End)]))
				file.write(struct.pack("<i", block[prop(b_39.Color_Id)]))
				file.write(struct.pack("<i", 0)) #Unknown count

				file.write(struct.pack("<i", len(block.children)))

				toProcessChild = True

			elif objType == 40:

				writeBoundSphere(file, block.location, block.empty_display_size)
				writeName(block[prop(b_40.Name1)], file)
				writeName(block[prop(b_40.Name2)], file)
				file.write(struct.pack("<i", block[prop(b_40.Unk_Int1)]))
				file.write(struct.pack("<i", block[prop(b_40.Unk_Int2)]))
				itemList = block[prop(b_40.Unk_List)]
				file.write(struct.pack("<i", len(itemList)))
				for item in itemList:
					file.write(struct.pack("<f", item))

			if toProcessChild:
				l_extra = extra
				if(len(blChildren) > 0):
					for i, ch in enumerate(blChildren[:-1]):

						if len(passToMesh) > 0:
							l_extra['passToMesh'] = passToMesh
						exportBlock(ch, False, curLevel+1, curMaxCnt, curGroups, l_extra, file)

					if len(passToMesh) > 0:
						l_extra['passToMesh'] = passToMesh
					exportBlock(blChildren[-1], True, curLevel+1, curMaxCnt, curGroups, l_extra, file)

			file.write(struct.pack("<i",555))#End Chunk

	return curLevel


blocksWithChildren = [2,3,4,5,6,7,9]


def getMeshProps(obj):

	mesh = obj.data

	polygons = mesh.polygons

	mat = obj.matrix_world

	vertexes = [(mat @ cn.co) for cn in mesh.vertices]

	local_verts = [cn.co for cn in mesh.vertices]

	uvs = [None] * len(vertexes)
	for poly in polygons:
		for li in poly.loop_indices:
			vi = mesh.loops[li].vertex_index
			uvs[vi] = mesh.uv_layers['UVMap'].data[li].uv

	normals = [cn.normal for cn in mesh.vertices]

	return [vertexes, uvs, normals, polygons, local_verts]

