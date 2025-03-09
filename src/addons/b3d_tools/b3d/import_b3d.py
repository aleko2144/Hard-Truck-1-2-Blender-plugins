import enum
import struct
import sys
import time
import datetime
import bpy
import os.path
import os

from math import sqrt
from math import atan2

import re

from .class_descr import (
    Blk001,
    Blk002,
    # Blk003,
    Blk004,
    Blk005,
    Blk006,
    Blk007,
    # Blk008,
    Blk009,
    Blk010,
    Blk011,
    Blk012,
    Blk013,
    Blk014,
    Blk015,
    Blk016,
    Blk017,
    Blk018,
    Blk020,
    Blk021,
    Blk022,
    Blk023,
    Blk024,
    Blk025,
    Blk026,
    Blk027,
    Blk028,
    Blk029,
    Blk030,
    Blk031,
    Blk033,
    Blk034,
    Blk035,
    Blk036,
    Blk037,
    Blk039,
    Blk040,
    Pfb008,
    Pfb028,
    Pfb035,
    Pvb008,
    Pvb035
)

from ..consts import (
    EMPTY_NAME,
    BLOCK_TYPE,
    BORDER_COLLECTION
)

from .scripts import (
    create_custom_attribute
)


from .common import (
    get_col_property_by_name,
    get_col_property_index_by_name,
    get_used_face,
    get_used_vertices_and_transform,
    get_polygons_by_selected_vertices,
    get_center_coord,
)

from ..common import (
    recalc_to_local_coord,
    importb3d_logger
)

from ..compatibility import (
    get_context_collection_objects,
    get_or_create_collection,
    is_before_2_80,
    set_empty_type,
    set_empty_size,
    get_uv_layers,
    get_active_object,
    set_active_object
)


#Setup module logger
log = importb3d_logger


def thread_import_b3d(self, files, context):
    for b3dfile in files:
        filepath = os.path.join(self.directory, b3dfile.name)

        log.info('Importing file {}'.format(filepath))
        t = time.mktime(datetime.datetime.now().timetuple())
        with open(filepath, 'rb') as file:
            import_b3d(file, context, self, filepath)
        t = time.mktime(datetime.datetime.now().timetuple()) - t
        log.info('Finished importing in {} seconds'.format(t))


class ChunkType(enum.Enum):
    END_CHUNK = 0
    END_CHUNKS = 1
    BEGIN_CHUNK = 2
    GROUP_CHUNK = 3

def openclose(file):
    oc = file.read(4)
    if (oc == (b'\x4D\x01\x00\x00')): # Begin_Chunk(111)
        return ChunkType.BEGIN_CHUNK
    elif oc == (b'\x2B\x02\x00\x00'): # End_Chunk(555)
        return ChunkType.END_CHUNK
    elif oc == (b'\xbc\x01\x00\x00'): # Group_Chunk(444)
        return ChunkType.GROUP_CHUNK
    elif oc == (b'\xde\x00\00\00'): # End_Chunks(222)
        return ChunkType.END_CHUNKS
    else:
        raise Exception()

def onebyte(file):
    return (file.read(1))

def read_name(file):
    obj_name = file.read(32)
    if (obj_name[0] == 0):
        obj_name = EMPTY_NAME
        #objname = "Untitled_0x" + str(hex(pos-36))
    else:
        obj_name = (obj_name.decode("cp1251").rstrip('\0'))
    return obj_name


def triangulate(faces):
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
    return faces_new


def make_poly_ok(faces):
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


def parse_pro(input_file, colors_list):
    with open (input_file,'r') as file:
        #read all lines first
        pro = file.readlines()
        file.close()
        # you may also want to remove whitespace characters like `\n` at the end of each line
        pro = [x.strip() for x in pro]

        ##### TEXTUREFILES #####
        texturefiles_index = pro.index([i for i in pro if "TEXTUREFILES" in i][0])
        texturefiles_num = int(re.search(r'\d+', pro[texturefiles_index]).group())
        texturefiles = []
        for i in range(texturefiles_num):
            texturefiles.append(pro[texturefiles_index + 1 + i].split(".")[0]) # так как texturefiles_index = номер строки, где написано "TEXTUREFILES", сами текстуры на одну строку ниже
                                                                               # split нужен для того, чтобы убрать всё, что после точки - например, ".txr noload"
        ##### MATERIALS #####
        materials_index = pro.index([i for i in pro if "MATERIALS" in i][0])
        materials_num = int(re.search(r'\d+', pro[materials_index]).group())
        materials = []
        for i in range(materials_num):
            materials.append(pro[materials_index + 1 + i]) # тоже самое, так как materials_index = номер строки, где написано "MATERIALS", сами материалы на одну строку ниже

        ##### Параметры материалов (col %d) #####
        material_colors = []

        for i in range(materials_num):
            colnum_str = str(re.findall(r'col\s+\d+', materials[i]))
            colnum = 0
            if (colnum_str != "[]"):
                colnum_final = str(re.findall(r'\d+', colnum_str[2:-2]))[2:-2]
                colnum = int(colnum_final) #[5:-2] нужно чтобы убрать ['tex и '], например: ['tex 10'] -> 10
                material_colors.append(str(colors_list[colnum]))
            else:
                material_colors.append("[]")


        ##### Параметры материалов (tex %d) #####
        material_textures = []

        for i in range(materials_num):
            texnum_str = str(re.findall(r't\wx\s+\d+', materials[i])) # t\wx - так как помимо tex, ещё бывает ttx
            texnum = 0
            if (texnum_str != "[]"):
                texnum_final = str(re.findall(r'\d+', texnum_str[2:-2]))[2:-2]
                texnum = int(texnum_final) #[5:-2] нужно чтобы убрать ['tex и '], например: ['tex 10'] -> 10
                material_textures.append(texturefiles[texnum-1])
            else:
                material_textures.append(material_colors[i])

        #for k in range(materials_num):

        return material_textures

def import_raw(file, context, op, filepath):

    basename1 = os.path.basename(filepath)[:-4]
    basename2 = basename1+"_2"
    basename1 = basename1+"_1"

    vertexes = []
    faces1 = []
    faces2 = []

    counter = 0

    width = 257

    for i in range(width):
        for j in range(width):
            vertexes.append((i*10,j*10,struct.unpack('<B',file.read(1))[0]))
            file.read(1)

    for i in range(width-1):
        for j in range(i,width-1):
            counter = i*width+j
            if i == j:
                faces1.append((counter, counter+1, counter+width+1))
            else:
                faces1.append((counter, counter+1, counter+width+1, counter+width))

    for i in range(width-1):
        for j in range(i,width-1):
            counter = j*width+i
            if i == j:
                faces2.append((counter, counter+width, counter+width+1))
            else:
                faces2.append((counter, counter+1, counter+width+1, counter+width))


    b3d_mesh1 = bpy.data.meshes.new(basename1)
    b3d_mesh2 = bpy.data.meshes.new(basename2)

    b3d_mesh1.from_pydata(vertexes,[],faces1)

    # Ev = threading.Event()
    # Tr = threading.Thread(target=b3d_mesh1.from_pydata, args = (vertexes,[],faces1))
    # Tr.start()
    # Ev.set()
    # Tr.join()

    b3d_mesh2.from_pydata(vertexes,[],faces2)

    # Ev = threading.Event()
    # Tr = threading.Thread(target=b3d_mesh2.from_pydata, args = (vertexes,[],faces2))
    # Tr.start()
    # Ev.set()
    # Tr.join()


    b3d_obj1 = bpy.data.objects.new(basename1, b3d_mesh1)
    get_context_collection_objects(context).link(b3d_obj1)

    b3d_obj2 = bpy.data.objects.new(basename2, b3d_mesh2)
    get_context_collection_objects(context).link(b3d_obj2)


def set_uv_values(uvObj, b3dMesh, uv):
    if is_before_2_80():
        # uvObj = b3dMesh.uv_textures.new()
        # imgMesh = math[texnum].texture_slots[0].texture.image.size[0]
        # uvObj.name = 'default'
        uvLoop = b3dMesh.uv_layers[0]
        uvs_mesh = []

        #print('uvs:	',str(uvs))
        for i, texpoly in enumerate(uvObj.data):
            # texpoly.image = Imgs[texnum]
            poly = b3dMesh.polygons[i]
            for j,loop in enumerate(poly.loop_indices):
                uvs_mesh = [uv[i][j][0],1 - uv[i][j][1]]
                uvLoop.data[loop].uv = uvs_mesh
    else:
        
        # custom_uv = get_uv_layers(b3d_mesh).new()
        # custom_uv.name = "UVMap"
        uvs_mesh = []

        for i, texpoly in enumerate(b3dMesh.polygons):
            for j,loop in enumerate(texpoly.loop_indices):
                uvs_mesh = [uv[i][j][0],1 - uv[i][j][1]]
                uvObj.data[loop].uv = uvs_mesh


def assign_material_by_vertices(obj, vert_indexes, mat_index):
    set_active_object(obj)
    # bpy.ops is slow https://blender.stackexchange.com/questions/2848/why-avoid-bpy-ops#comment11187_2848
    # bpy.ops.object.mode_set(mode = 'EDIT')
    # bpy.ops.mesh.select_mode(type= 'VERT')
    # bpy.ops.mesh.select_all(action = 'DESELECT')
    # bpy.ops.object.mode_set(mode = 'OBJECT')
    vert = obj.data.vertices
    face = obj.data.polygons
    edge = obj.data.edges
    for i in face:
        i.select=False
    for i in edge:
        i.select=False
    for i in vert:
        i.select=False

    for idx in vert_indexes:
        obj.data.vertices[idx].select = True
    selected_polygons = get_polygons_by_selected_vertices(get_active_object())
    for poly in selected_polygons:
        poly.material_index = mat_index


def import_b3d(file, context, self, filepath):
    if file.read(3) == b'b3d':
        log.info("correct file")
    else:
        log.error("b3d error")
    scene = context.scene
    mytool = scene.my_tool

    #skip to materials list
    file.seek(21,1)

    res_modules = getattr(mytool, "res_modules")

    res_path = ''
    if len(self.res_location) > 0 and os.path.exists(self.res_location):
        res_path = self.res_location
    else:
        res_path = filepath

    res_basename = os.path.basename(res_path)[:-4] #cut extension

    if self.to_import_textures:
        res_module = get_col_property_by_name(res_modules, res_basename)

    blocks_to_import = self.blocks_to_import

    used_blocks = {}
    for block in blocks_to_import:
        used_blocks[block.name] = block.state

    # Parsing b3d
    material_textures = []
    materials_count = struct.unpack('<i',file.read(4))[0]
    material_list = []
    # Adding Materials
    for i in range(materials_count):

        sn_img = file.read(32).decode("utf-8").rstrip('\0') #читаю имя
        material_list.append(sn_img)

    file.seek(4,1) #Skip Begin_Chunks(111)

    # Processing vertices

    ex = 0
    i = 0
    lvl = 0
    cnt = 0
    level_groups = []
    vertexes = []
    normals = []
    formats = []
    #
    vertex_block_uvs = []
    poly_block_uvs = []
    # 30 block
    borders = {}
    current_room_name = ""


    uv = []

    b3d_name = os.path.basename(filepath)

    b3d_obj = bpy.data.objects.get(b3d_name)
    if b3d_obj is None:
        b3d_obj = bpy.data.objects.new(b3d_name, None)
        b3d_obj[BLOCK_TYPE] = 111
        get_context_collection_objects(context).link(b3d_obj) # root object

    obj_string = [b3d_obj.name]

    while ex!=ChunkType.END_CHUNKS:

        ex = openclose(file)
        if ex == ChunkType.END_CHUNK:

            parent_obj = context.scene.objects.get(obj_string[-2])
            if parent_obj.get(BLOCK_TYPE) in [9, 10, 21]:
                del obj_string[-1]

            del obj_string[-1]
            level_groups[lvl] = 0
            lvl-=1

        elif ex == ChunkType.END_CHUNKS:
            file.close()
            break

        elif ex == ChunkType.GROUP_CHUNK:
            if len(level_groups) <= lvl:
                for i in range(lvl+1-len(level_groups)):
                    level_groups.append(0)

            if lvl > 0:

                level_groups[lvl] +=1
                parent_obj = context.scene.objects.get(obj_string[-1])

                if parent_obj.name[:6] == 'GROUP_':
                    del obj_string[-1]
                    parent_obj = context.scene.objects.get(obj_string[-1])

                if level_groups[lvl] > 0:

                    if len(parent_obj.children) == 0:
                        group_obj_name = 'GROUP_0'

                        b3d_obj = bpy.data.objects.new(group_obj_name, None)
                        b3d_obj[BLOCK_TYPE] = 444

                        b3d_obj.parent = parent_obj
                        get_context_collection_objects(context).link(b3d_obj)
                        # obj_string.append(b3d_obj.name)

                group_obj_name = 'GROUP_{}'.format(level_groups[lvl])

                b3d_obj = bpy.data.objects.new(group_obj_name, None)
                b3d_obj[BLOCK_TYPE] = 444

                b3d_obj.parent = context.scene.objects.get(obj_string[-1])
                get_context_collection_objects(context).link(b3d_obj)

                obj_string.append(b3d_obj.name)

            continue
        elif ex == ChunkType.BEGIN_CHUNK:
            lvl+=1
            if len(level_groups) <= lvl:
                for i in range(lvl+1-len(level_groups)):
                    level_groups.append(0)

            t1 = time.perf_counter()

            parent_obj = context.scene.objects.get(obj_string[-1])

            if parent_obj.get(BLOCK_TYPE) in [9, 10, 21]:

                group_obj_name = 'GROUP_0'

                b3d_obj = bpy.data.objects.new(group_obj_name, None)
                b3d_obj[BLOCK_TYPE] = 444

                b3d_obj.parent = parent_obj
                get_context_collection_objects(context).link(b3d_obj)

                obj_string.append(b3d_obj.name)

            obj_string.append("")

            only_name = read_name(file)
            block_type = struct.unpack("<i",file.read(4))[0]
            # obj_name = "{}_{}".format(str(block_type).zfill(2), only_name)
            obj_name = only_name
            real_name = only_name

            parent_obj = context.scene.objects.get(obj_string[-2])



            # log.debug("{}_{}".format(block_type, obj_name))
            # log.debug("{}_{}".format(lvl - 1, level_groups))
            # log.info("Importing block #{}: {}".format(block_type, obj_name))
            # log.info("block_type: {}, active: {}".format(block_type, used_blocks[str(block_type)]))
            if (block_type == 0): # Empty Block

                # bounding_sphere = struct.unpack("<4f",file.read(16))
                ff = file.seek(44,1)

                if not used_blocks[str(block_type)]:
                    continue

                b3d_obj = bpy.data.objects.new(obj_name, None)
                b3d_obj[BLOCK_TYPE] = block_type

                b3d_obj.parent = parent_obj
                get_context_collection_objects(context).link(b3d_obj)
                real_name = b3d_obj.name
                obj_string[-1] = b3d_obj.name

            elif (block_type == 1):
                name1 = read_name(file) #?
                name2 = read_name(file) #?

                if not used_blocks[str(block_type)]:
                    continue

                b3d_obj = bpy.data.objects.new(obj_name, None)
                b3d_obj[BLOCK_TYPE] = block_type
                b3d_obj[Blk001.Name1.get_prop()] = name1
                b3d_obj[Blk001.Name2.get_prop()] = name2

                b3d_obj.parent = parent_obj
                get_context_collection_objects(context).link(b3d_obj)
                real_name = b3d_obj.name
                obj_string[-1] = b3d_obj.name


            elif (block_type == 2):    #контейнер хз
                bounding_sphere = struct.unpack("<4f",file.read(16))
                unknown_sphere = struct.unpack("<4f",file.read(16))
                child_cnt = struct.unpack("<i",file.read(4))

                if not used_blocks[str(block_type)]:
                    continue

                b3d_obj = bpy.data.objects.new(obj_name, None)
                b3d_obj[BLOCK_TYPE] = block_type
                # b3d_obj[Blk002.XYZ.get_prop()] = bounding_sphere[0:3]
                # b3d_obj[Blk002.r.get_prop()] = bounding_sphere[3]
                b3d_obj[Blk002.Unk_XYZ.get_prop()] = unknown_sphere[0:3]
                b3d_obj[Blk002.Unk_R.get_prop()] = unknown_sphere[3]

                b3d_obj.parent = parent_obj
                get_context_collection_objects(context).link(b3d_obj)
                real_name = b3d_obj.name
                obj_string[-1] = b3d_obj.name


            elif (block_type == 3):    #
                bounding_sphere = struct.unpack("<4f",file.read(16))
                child_cnt = struct.unpack("<i",file.read(4))

                if not used_blocks[str(block_type)]:
                    continue

                b3d_obj = bpy.data.objects.new(obj_name, None)
                b3d_obj[BLOCK_TYPE] = block_type
                # b3d_obj[Blk003.XYZ.get_prop()] = bounding_sphere[0:3]
                # b3d_obj[Blk003.r.get_prop()] = bounding_sphere[3]

                b3d_obj.parent = parent_obj
                get_context_collection_objects(context).link(b3d_obj)
                real_name = b3d_obj.name
                obj_string[-1] = b3d_obj.name


            elif (block_type == 4):    #похоже на контейнер 05 совмещенный с 12
                bounding_sphere = struct.unpack("<4f",file.read(16))
                name1 = read_name(file)
                name2 = read_name(file)
                child_cnt = struct.unpack("<i",file.read(4))[0]

                if not used_blocks[str(block_type)]:
                    continue

                b3d_obj = bpy.data.objects.new(obj_name, None)
                b3d_obj[BLOCK_TYPE] = block_type
                # b3d_obj[Blk004.XYZ.get_prop()] = bounding_sphere[0:3]
                # b3d_obj[Blk004.r.get_prop()] = bounding_sphere[3]
                b3d_obj[Blk004.Name1.get_prop()] = name1
                b3d_obj[Blk004.Name2.get_prop()] = name2

                b3d_obj.parent = parent_obj
                get_context_collection_objects(context).link(b3d_obj)
                real_name = b3d_obj.name
                obj_string[-1] = b3d_obj.name

            elif (block_type == 5): #общий контейнер

                # bounding_sphere
                bounding_sphere = struct.unpack("<4f",file.read(16))
                name = read_name(file)
                child_cnt = struct.unpack("<i",file.read(4))[0]

                if not used_blocks[str(block_type)]:
                    continue
                b3d_obj = bpy.data.objects.new(obj_name, None) #create empty
                b3d_obj[BLOCK_TYPE] = block_type
                # b3d_obj[Blk005.XYZ.get_prop()] = (bounding_sphere[0:3])
                # b3d_obj[Blk005.r.get_prop()] = (bounding_sphere[3])
                b3d_obj[Blk005.Name1.get_prop()] = name

                b3d_obj.parent = parent_obj
                get_context_collection_objects(context).link(b3d_obj)
                real_name = b3d_obj.name
                obj_string[-1] = b3d_obj.name

            elif (block_type == 6):
                vertexes = []
                uv = []
                normals = []
                normals_off = []

                bounding_sphere = struct.unpack("<4f",file.read(16))
                name1 = read_name(file)
                name2 = read_name(file)
                vertex_count = struct.unpack("<i",file.read(4))[0]
                for i in range (vertex_count):
                    vertexes.append(struct.unpack("<3f",file.read(12)))
                    uv.append(struct.unpack("<2f",file.read(8)))
                    normals.append((0.0, 0.0, 0.0))
                    normals_off.append(1.0)

                child_cnt = struct.unpack("<i",file.read(4))[0]

                if not used_blocks[str(block_type)]:
                    continue

                b3d_obj = bpy.data.objects.new(obj_name, None)
                b3d_obj[BLOCK_TYPE] = block_type
                # b3d_obj[Blk006.XYZ.get_prop()] = bounding_sphere[0:3]
                # b3d_obj[Blk006.r.get_prop()] = bounding_sphere[3]
                b3d_obj[Blk006.Name1.get_prop()] = name1
                b3d_obj[Blk006.Name2.get_prop()] = name2

                b3d_obj.parent = parent_obj
                get_context_collection_objects(context).link(b3d_obj)
                real_name = b3d_obj.name
                obj_string[-1] = b3d_obj.name

            elif (block_type == 7):    #25? xyzuv TailLight? похоже на "хвост" движения    mesh
                vertexes = []
                normals = []
                normals_off = []
                # uv = []
                vertex_block_uvs = []

                vertex_block_uvs.append([])

                bounding_sphere = struct.unpack("<4f",file.read(16))
                group_name = read_name(file) #0-0

                vertex_count = struct.unpack("<i",file.read(4))[0]
                for i in range(vertex_count):
                    vertexes.append(struct.unpack("<3f",file.read(12)))
                    vertex_block_uvs[0].append(struct.unpack("<2f",file.read(8)))
                    normals.append((0.0, 0.0, 0.0))
                    normals_off.append(1.0)
                    # uv.append(struct.unpack("<2f",file.read(8)))


                child_cnt = struct.unpack("<i",file.read(4))[0]

                if not used_blocks[str(block_type)]:
                    continue

                b3d_obj = bpy.data.objects.new(obj_name, None)
                b3d_obj[BLOCK_TYPE] = block_type
                # b3d_obj[Blk007.XYZ.get_prop()] = bounding_sphere[0:3]
                # b3d_obj[Blk007.r.get_prop()] = bounding_sphere[3]
                b3d_obj[Blk007.Name1.get_prop()] = group_name

                b3d_obj.parent = parent_obj
                get_context_collection_objects(context).link(b3d_obj)
                real_name = b3d_obj.name
                obj_string[-1] = b3d_obj.name

            elif (block_type == 8):    #тоже фейсы        face
                faces = []
                faces_all = []
                overriden_uvs = []
                texnums = {}
                uv_indexes = []
                formats = []
                unk_floats = []
                unk_ints = []
                l_normals = normals
                l_normals_off = normals_off


                bounding_sphere = struct.unpack("<4f",file.read(16)) # skip bounding sphere
                polygon_count = struct.unpack("<i",file.read(4))[0]

                for i in range(polygon_count):
                    faces = []
                    faces_new = []

                    format_raw = struct.unpack("<i",file.read(4))[0]
                    poly_format = format_raw ^ 1
                    uv_count = ((poly_format & 0xFF00) >> 8) #ah
                    triangulate_offset = poly_format & 0b10000000

                    if poly_format & 0b10:
                        uv_count += 1

                    poly_block_uvs = [{}]

                    poly_block_len = len(poly_block_uvs)

                    for i in range(uv_count - poly_block_len):
                        poly_block_uvs.append({})

                    unk_float = struct.unpack("<f",file.read(4))[0]
                    unk_int = struct.unpack("<i",file.read(4))[0]
                    texnum = struct.unpack("<i",file.read(4))[0]

                    vertex_count = struct.unpack("<i",file.read(4))[0]

                    for j in range(vertex_count):
                        face_idx = struct.unpack("<i",file.read(4))[0]
                        faces.append(face_idx)
                        if poly_format & 0b10:
                            # uv override
                            for k in range(uv_count):
                                poly_block_uvs[k][face_idx] = struct.unpack("<2f",file.read(8))
                        else:
                            poly_block_uvs[0][face_idx] = vertex_block_uvs[0][face_idx]
                        # if used with no-normals vertex blocks(6,7) use this normals
                        if poly_format & 0b100000 and poly_format & 0b10000:
                            if poly_format & 0b1:
                                l_normals[face_idx] = struct.unpack("<3f",file.read(12))
                            else:
                                l_normals_off[face_idx] = struct.unpack("<f",file.read(4))

                    #Save materials for faces
                    if texnum in texnums:
                        texnums[texnum].append(faces)
                    else:
                        texnums[texnum] = []
                        texnums[texnum].append(faces)


                    #Without triangulation
                    # uv_new = ()
                    # for t in range(len(faces)):
                    #     uv_new = uv_new + (uv[faces[t]],)
                    # uvs.append(uv_new)
                    # faces_all.append(faces)

                    if len(poly_block_uvs) > len(overriden_uvs):
                        for i in range(len(poly_block_uvs)-len(overriden_uvs)):
                            overriden_uvs.append([])

                    #Triangulating faces
                    for t in range(len(faces)-2):
                        if not triangulate_offset:
                            if t%2 == 0:
                                faces_new.append([faces[t-1],faces[t],faces[t+1]])
                            else:
                                faces_new.append([faces[t],faces[t+1],faces[t+2]])
                        else:
                            if t%2 == 0:
                                faces_new.append([faces[t],faces[t+1],faces[t+2]])
                            else:
                                faces_new.append([faces[t],faces[t+2],faces[t+1]])

                        for u, over_uv in enumerate(poly_block_uvs):
                            if over_uv:
                                overriden_uvs[u].append((over_uv[faces_new[t][0]], over_uv[faces_new[t][1]], over_uv[faces_new[t][2]]))

                        uv_indexes.append(faces_new[t])
                        formats.append(format_raw)
                        unk_floats.append(unk_float)
                        unk_ints.append(unk_int)

                    faces_all.extend(faces_new)

                if not used_blocks[str(block_type)]:
                    continue

                b3d_mesh = (bpy.data.meshes.new(obj_name))

                cur_vertexes, cur_faces, indices, old_new_transf, new_old_transf = get_used_vertices_and_transform(vertexes, faces_all)

                cur_normals = []
                cur_normals_off = []
                for i in range(len(cur_vertexes)):
                    cur_normals.append(l_normals[new_old_transf[i]])
                    cur_normals_off.append(l_normals_off[new_old_transf[i]])

                cur_vertexes = recalc_to_local_coord(bounding_sphere[:3], cur_vertexes)

                b3d_mesh.from_pydata(cur_vertexes,[],cur_faces)

                # Ev = threading.Event()
                # Tr = threading.Thread(target=b3d_mesh.from_pydata, args = (cur_vertexes,[],cur_faces))
                # Tr.start()
                # Ev.set()
                # Tr.join()

                # newIndices = get_user_vertices(cur_faces)

                if len(normals) > 0:
                    b3d_mesh.use_auto_smooth = True
                    normal_list = []
                    for i,vert in enumerate(b3d_mesh.vertices):
                        normal_list.append(normals[new_old_transf[i]])
                        # b3d_mesh.vertices[idx].normal = normals[idx]
                    b3d_mesh.normals_split_custom_set_from_vertices(normal_list)

                #Setup UV
                # custom_uv = b3d_mesh.uv_layers.new()
                # custom_uv.name = "UVmap"

                # for k, texpoly in enumerate(b3d_mesh.polygons):
                #     for j,loop in enumerate(texpoly.loop_indices):
                #         uvs_mesh = (uvs[k][j][0], 1-uvs[k][j][1])
                #         custom_uv.data[loop].uv = uvs_mesh

                # for simplicity
                # for u, uvMap in enumerate(vertex_block_uvs):

                #     custom_uv = get_uv_layers(b3d_mesh).new()
                #     custom_uv.name = "UVmapVert{}".format(u)
                #     uvs_mesh = []

                #     for i, texpoly in enumerate(b3d_mesh.polygons):
                #         for j,loop in enumerate(texpoly.loop_indices):
                #             uvs_mesh = (uvMap[uv_indexes[i][j]][0],1 - uvMap[uv_indexes[i][j]][1])
                #             custom_uv.data[loop].uv = uvs_mesh

                for u, uv_over in enumerate(overriden_uvs):

                    custom_uv = get_uv_layers(b3d_mesh).new()
                    custom_uv.name = "UVMap"
                    
                    set_uv_values(custom_uv, b3d_mesh, uv_over)
                    
                create_custom_attribute(b3d_mesh, formats, Pfb008, Pfb008.Format_Flags)

                # those are usually consts in all objects
                # create_custom_attribute(b3d_mesh, unk_floats, Pfb008, Pfb008.Unk_Float1)
                # create_custom_attribute(b3d_mesh, unk_ints, Pfb008, Pfb008.Unk_Int2)

                # cancel for now, maybe find workaround later
                # create_custom_attribute(b3d_mesh, cur_normals_off, Pvb008, Pvb008.Normal_Switch)
                # create_custom_attribute(b3d_mesh, cur_normals, Pvb008, Pvb008.Custom_Normal)

                #Create Object

                b3d_obj = bpy.data.objects.new(obj_name, b3d_mesh)
                b3d_obj[BLOCK_TYPE] = block_type
                b3d_obj.location = bounding_sphere[0:3]
                # b3d_obj[Blk008.XYZ.get_prop()] = bounding_sphere[0:3]
                # b3d_obj[Blk008.r.get_prop()] = bounding_sphere[3]
                b3d_obj.parent = parent_obj
                get_context_collection_objects(context).link(b3d_obj)
                real_name = b3d_obj.name
                obj_string[-1] = b3d_obj.name

                if self.to_import_textures:
                    #For assign_material_by_vertices just-in-case
                    # bpy.ops.object.mode_set(mode = 'OBJECT')
                    #Set appropriate meaterials
                    if len(texnums.keys()) > 1:
                        for texnum in texnums:
                            mat = res_module.materials[int(texnum)].id_mat
                            # mat = bpy.data.materials.get(res_module.materials[int(texnum)].mat_name)
                            b3d_mesh.materials.append(mat)
                            last_index = len(b3d_mesh.materials)-1

                            for vert_arr in texnums[texnum]:
                                new_vert_arr = get_used_face(vert_arr, old_new_transf)
                                # self.lock.acquire()
                                assign_material_by_vertices(b3d_obj, new_vert_arr, last_index)
                                # self.lock.release()
                    else:
                        for texnum in texnums:
                            mat = res_module.materials[int(texnum)].id_mat
                            # mat = bpy.data.materials.get(res_module.materials[int(texnum)].mat_name)
                            b3d_mesh.materials.append(mat)



            elif (block_type == 9 or block_type == 22):

                bounding_sphere = struct.unpack("<4f",file.read(16))
                unknown_sphere = struct.unpack("<4f",file.read(16))
                child_cnt = struct.unpack("<i",file.read(4))[0]

                if not used_blocks[str(block_type)]:
                    continue

                b3d_obj = bpy.data.objects.new(obj_name, None)
                b3d_obj[BLOCK_TYPE] = block_type
                # b3d_obj[Blk009.XYZ.get_prop()] = bounding_sphere[0:3]
                # b3d_obj[Blk009.r.get_prop()] = bounding_sphere[3]
                b3d_obj[Blk009.Unk_XYZ.get_prop()] = unknown_sphere[0:3]
                b3d_obj[Blk009.Unk_R.get_prop()] = unknown_sphere[3]

                b3d_obj.parent = parent_obj
                get_context_collection_objects(context).link(b3d_obj)
                real_name = b3d_obj.name
                obj_string[-1] = b3d_obj.name

            elif (block_type == 10): #контейнер, хз о чем LOD

                bounding_sphere = struct.unpack("<4f",file.read(16))
                unknown_sphere = struct.unpack("<4f",file.read(16))
                child_cnt = struct.unpack("<i",file.read(4))[0]

                if not used_blocks[str(block_type)]:
                    continue

                b3d_obj = bpy.data.objects.new(obj_name, None)
                b3d_obj[BLOCK_TYPE] = block_type
                # b3d_obj[Blk010.XYZ.get_prop()] = bounding_sphere[0:3]
                # b3d_obj[Blk010.r.get_prop()] = bounding_sphere[3]
                b3d_obj[Blk010.LOD_XYZ.get_prop()] = unknown_sphere[0:3]
                b3d_obj[Blk010.LOD_R.get_prop()] = unknown_sphere[3]

                b3d_obj.parent = parent_obj
                get_context_collection_objects(context).link(b3d_obj)
                real_name = b3d_obj.name
                obj_string[-1] = b3d_obj.name


            elif (block_type == 11):
                bounding_sphere = struct.unpack("<4f",file.read(16))
                unknown_point1 = struct.unpack("<3f",file.read(12))
                unknown_point2 = struct.unpack("<3f",file.read(12))
                unknown_r1 = struct.unpack("<i",file.read(4))[0]
                unknown_r2 = struct.unpack("<i",file.read(4))[0]
                child_cnt = struct.unpack("<i",file.read(4))[0]

                if not used_blocks[str(block_type)]:
                    continue

                b3d_obj = bpy.data.objects.new(obj_name, None)
                b3d_obj[BLOCK_TYPE] = block_type
                # b3d_obj[Blk011.XYZ.get_prop()] = bounding_sphere[0:3]
                # b3d_obj[Blk011.r.get_prop()] = bounding_sphere[3]
                b3d_obj[Blk011.Unk_XYZ1.get_prop()] = unknown_point1
                b3d_obj[Blk011.Unk_XYZ2.get_prop()] = unknown_point2
                b3d_obj[Blk011.Unk_R1.get_prop()] = unknown_r1
                b3d_obj[Blk011.Unk_R2.get_prop()] = unknown_r2

                b3d_obj.parent = parent_obj
                get_context_collection_objects(context).link(b3d_obj)
                real_name = b3d_obj.name
                obj_string[-1] = b3d_obj.name

            elif (block_type == 12):

                l_params = []
                bounding_sphere = struct.unpack("<4f",file.read(16))
                unknown_sphere = struct.unpack("<4f",file.read(16))
                unknown1 = struct.unpack("<i",file.read(4))[0]
                unknown2 = struct.unpack("<i",file.read(4))[0]
                cnt = struct.unpack("<i",file.read(4))[0]
                for i in range(cnt):
                    l_params.append(struct.unpack("f",file.read(4))[0])

                if not used_blocks[str(block_type)]:
                    continue

                b3d_obj = bpy.data.objects.new(obj_name, None)
                b3d_obj[BLOCK_TYPE] = block_type
                # b3d_obj[Blk012.XYZ.get_prop()] = bounding_sphere[0:3]
                # b3d_obj[Blk012.r.get_prop()] = bounding_sphere[3]
                b3d_obj[Blk012.Unk_XYZ1.get_prop()] = unknown_sphere[0:3]
                b3d_obj[Blk012.Unk_R.get_prop()] = unknown_sphere[3]
                b3d_obj[Blk012.Unk_Int1.get_prop()] = unknown1
                b3d_obj[Blk012.Unk_Int2.get_prop()] = unknown2
                b3d_obj[Blk012.Unk_List.get_prop()] = l_params

                b3d_obj.parent = parent_obj
                get_context_collection_objects(context).link(b3d_obj)
                real_name = b3d_obj.name
                obj_string[-1] = b3d_obj.name

            elif (block_type == 13):

                l_params = []
                bounding_sphere = struct.unpack("<4f",file.read(16))
                unknown1 = struct.unpack("<i",file.read(4))[0]
                unknown2 = struct.unpack("<i",file.read(4))[0]
                cnt = struct.unpack("<i",file.read(4))[0]
                for i in range(cnt):
                    l_params.append(struct.unpack("f",file.read(4))[0])

                if not used_blocks[str(block_type)]:
                    continue

                b3d_obj = bpy.data.objects.new(obj_name, None)
                b3d_obj[BLOCK_TYPE] = block_type
                # b3d_obj[Blk013.XYZ.get_prop()] = bounding_sphere[0:3]
                # b3d_obj[Blk013.r.get_prop()] = bounding_sphere[3]
                b3d_obj[Blk013.Unk_Int1.get_prop()] = unknown1
                b3d_obj[Blk013.Unk_Int2.get_prop()] = unknown2
                b3d_obj[Blk013.Unk_List.get_prop()] = l_params

                b3d_obj.parent = parent_obj
                get_context_collection_objects(context).link(b3d_obj)
                real_name = b3d_obj.name
                obj_string[-1] = b3d_obj.name

            elif (block_type == 14): #sell_ ?

                l_params = []

                bounding_sphere = struct.unpack("<4f",file.read(16))
                unknown_sphere = struct.unpack("<4f",file.read(16))

                unknown1 = struct.unpack("<i",file.read(4))[0]
                unknown2 = struct.unpack("<i",file.read(4))[0]
                cnt = struct.unpack("<i",file.read(4))[0]

                for i in range(cnt):
                    l_params.append(struct.unpack("f",file.read(4))[0])

                if not used_blocks[str(block_type)]:
                    continue

                b3d_obj = bpy.data.objects.new(obj_name, None)
                b3d_obj[BLOCK_TYPE] = block_type
                # b3d_obj[Blk014.XYZ.get_prop()] = bounding_sphere[0:3]
                # b3d_obj[Blk014.r.get_prop()] = bounding_sphere[3]
                b3d_obj[Blk014.Unk_XYZ.get_prop()] = unknown_sphere[0:3]
                b3d_obj[Blk014.Unk_R.get_prop()] = unknown_sphere[3]
                b3d_obj[Blk014.Unk_Int1.get_prop()] = unknown1
                b3d_obj[Blk014.Unk_Int2.get_prop()] = unknown2
                b3d_obj[Blk014.Unk_List.get_prop()] = l_params

                b3d_obj.parent = parent_obj
                get_context_collection_objects(context).link(b3d_obj)
                real_name = b3d_obj.name
                obj_string[-1] = b3d_obj.name

            elif (block_type == 15):

                l_params = []
                bounding_sphere = struct.unpack("<4f",file.read(16))
                unknown1 = struct.unpack("<i",file.read(4))[0]
                unknown2 = struct.unpack("<i",file.read(4))[0]
                cnt = struct.unpack("<i",file.read(4))[0]
                for i in range(cnt):
                    l_params.append(struct.unpack("f",file.read(4))[0])

                if not used_blocks[str(block_type)]:
                    continue

                b3d_obj = bpy.data.objects.new(obj_name, None)
                b3d_obj[BLOCK_TYPE] = block_type
                # b3d_obj[Blk015.XYZ.get_prop()] = bounding_sphere[0:3]
                # b3d_obj[Blk015.r.get_prop()] = bounding_sphere[3]
                b3d_obj[Blk015.Unk_Int1.get_prop()] = unknown1
                b3d_obj[Blk015.Unk_Int2.get_prop()] = unknown2
                b3d_obj[Blk015.Unk_List.get_prop()] = l_params

                b3d_obj.parent = parent_obj
                get_context_collection_objects(context).link(b3d_obj)
                real_name = b3d_obj.name
                obj_string[-1] = b3d_obj.name

            elif (block_type == 16):

                l_params = []

                bounding_sphere = struct.unpack("<4f",file.read(16))
                vector1 = struct.unpack("<3f",file.read(12))
                vector2 = struct.unpack("<3f",file.read(12))
                unk1 = struct.unpack("<f",file.read(4))[0]
                unk2 = struct.unpack("<f",file.read(4))[0]

                unknown1 = struct.unpack("<i",file.read(4))[0]
                unknown2 = struct.unpack("<i",file.read(4))[0]
                cnt = struct.unpack("<i",file.read(4))[0]
                for i in range(cnt):
                    l_params.append(struct.unpack("f",file.read(4))[0])

                if not used_blocks[str(block_type)]:
                    continue

                b3d_obj = bpy.data.objects.new(obj_name, None)
                b3d_obj[BLOCK_TYPE] = block_type
                # b3d_obj[Blk016.XYZ.get_prop()] = bounding_sphere[0:3]
                # b3d_obj[Blk016.r.get_prop()] = bounding_sphere[3]
                b3d_obj[Blk016.Unk_XYZ1.get_prop()] = vector1
                b3d_obj[Blk016.Unk_XYZ2.get_prop()] = vector2
                b3d_obj[Blk016.Unk_Float1.get_prop()] = unk1
                b3d_obj[Blk016.Unk_Float2.get_prop()] = unk2
                b3d_obj[Blk016.Unk_Int1.get_prop()] = unknown1
                b3d_obj[Blk016.Unk_Int2.get_prop()] = unknown2
                b3d_obj[Blk013.Unk_List.get_prop()] = l_params


                b3d_obj.parent = parent_obj
                get_context_collection_objects(context).link(b3d_obj)
                real_name = b3d_obj.name
                obj_string[-1] = b3d_obj.name

            elif (block_type == 17):

                l_params = []

                bounding_sphere = struct.unpack("<4f",file.read(16))
                vector1 = struct.unpack("<3f",file.read(12))
                vector2 = struct.unpack("<3f",file.read(12))
                unk1 = struct.unpack("<f",file.read(4))[0]
                unk2 = struct.unpack("<f",file.read(4))[0]

                unknown1 = struct.unpack("<i",file.read(4))[0]
                unknown2 = struct.unpack("<i",file.read(4))[0]
                cnt = struct.unpack("<i",file.read(4))[0]
                for i in range(cnt):
                    l_params.append(struct.unpack("f",file.read(4))[0])

                if not used_blocks[str(block_type)]:
                    continue

                b3d_obj = bpy.data.objects.new(obj_name, None)
                b3d_obj[BLOCK_TYPE] = block_type
                # b3d_obj[Blk017.XYZ.get_prop()] = bounding_sphere[0:3]
                # b3d_obj[Blk017.r.get_prop()] = bounding_sphere[3]
                b3d_obj[Blk017.Unk_XYZ1.get_prop()] = vector1
                b3d_obj[Blk017.Unk_XYZ2.get_prop()] = vector2
                b3d_obj[Blk017.Unk_Float1.get_prop()] = unk1
                b3d_obj[Blk017.Unk_Float2.get_prop()] = unk2
                b3d_obj[Blk017.Unk_Int1.get_prop()] = unknown1
                b3d_obj[Blk017.Unk_Int2.get_prop()] = unknown2
                b3d_obj[Blk017.Unk_List.get_prop()] = l_params

                b3d_obj.parent = parent_obj
                get_context_collection_objects(context).link(b3d_obj)
                real_name = b3d_obj.name
                obj_string[-1] = b3d_obj.name

            elif (block_type == 18):    #контейнер "применить к"

                bounding_sphere = struct.unpack("<4f",file.read(16))
                space_name = read_name(file)
                add_name = read_name(file)
                # b3d_obj['space_name'] = file.read(32).decode("utf-8").rstrip('\0')
                # b3d_obj['add_name'] = file.read(32).decode("utf-8").rstrip('\0')

                if not used_blocks[str(block_type)]:
                    continue

                b3d_obj = bpy.data.objects.new(obj_name, None)
                b3d_obj[BLOCK_TYPE] = block_type
                # b3d_obj[Blk018.XYZ.get_prop()] = bounding_sphere[0:3]
                # b3d_obj[Blk018.r.get_prop()] = bounding_sphere[3]
                b3d_obj[Blk018.Add_Name.get_prop()] = add_name
                b3d_obj[Blk018.Space_Name.get_prop()] = space_name

                b3d_obj.parent = parent_obj
                get_context_collection_objects(context).link(b3d_obj)
                real_name = b3d_obj.name
                obj_string[-1] = b3d_obj.name


            elif (block_type == 19):

                child_cnt = struct.unpack("i",file.read(4))[0]

                current_room_name = "{}:{}".format(res_basename, obj_name)

                if not used_blocks[str(block_type)]:
                    continue

                b3d_obj = bpy.data.objects.get(obj_name)
                if b3d_obj is None:
                    b3d_obj = bpy.data.objects.new(obj_name, None)
                    b3d_obj[BLOCK_TYPE] = block_type

                    b3d_obj.parent = parent_obj
                    get_context_collection_objects(context).link(b3d_obj)
                real_name = b3d_obj.name
                obj_string[-1] = b3d_obj.name


            elif (block_type == 20):
                bounding_sphere = struct.unpack("<4f",file.read(16))

                verts_count = struct.unpack("i",file.read(4))[0]

                unknown1 = struct.unpack("<i",file.read(4))[0]
                unknown2 = struct.unpack("<i",file.read(4))[0]

                unknowns = []
                cnt = struct.unpack("i",file.read(4))[0]
                for i in range(cnt):
                    unknowns.append(struct.unpack("f",file.read(4))[0])

                coords = []
                for i in range(verts_count):
                    coords.append(struct.unpack("fff",file.read(12)))

                if not used_blocks[str(block_type)]:
                    continue

                curve_data = bpy.data.curves.new('curve', type='CURVE')

                curve_data.dimensions = '2D'
                curve_data.resolution_u = 2

                # map coords to spline
                polyline = curve_data.splines.new('POLY')
                polyline.points.add(len(coords)-1)

                if len(coords) > 0:
                    origin_point = coords[0]
                else:
                    origin_point = bounding_sphere[0:3]

                new_coords = recalc_to_local_coord(origin_point, coords)

                for i, coord in enumerate(new_coords):
                    x,y,z = coord
                    polyline.points[i].co = (x, y, z, 1)

                curve_data.bevel_depth = 0
                curve_data.extrude = 10

                # create Object
                b3d_obj = bpy.data.objects.new(obj_name, curve_data)
                # b3d_obj.location = (0,0,0)
                b3d_obj[BLOCK_TYPE] = block_type
                b3d_obj.location = origin_point
                # b3d_obj[Blk020.XYZ.get_prop()] = bounding_sphere[0:3]
                # b3d_obj[Blk020.r.get_prop()] = bounding_sphere[3]
                b3d_obj[Blk020.Unk_Int1.get_prop()] = unknown1
                b3d_obj[Blk020.Unk_Int2.get_prop()] = unknown2
                b3d_obj[Blk020.Unk_List.get_prop()] = unknowns

                b3d_obj.parent = parent_obj
                get_context_collection_objects(context).link(b3d_obj)
                real_name = b3d_obj.name
                obj_string[-1] = b3d_obj.name

            elif (block_type == 21): #testkey???

                bounding_sphere = struct.unpack("<4f",file.read(16))
                group_cnt = struct.unpack("<i",file.read(4))[0]
                unknown2 = struct.unpack("<i",file.read(4))[0]
                child_cnt = struct.unpack("<i",file.read(4))[0]

                if not used_blocks[str(block_type)]:
                    continue

                b3d_obj = bpy.data.objects.new(obj_name, None)
                b3d_obj[BLOCK_TYPE] = block_type
                # b3d_obj[Blk021.XYZ.get_prop()] = bounding_sphere[0:3]
                # b3d_obj[Blk021.r.get_prop()] = bounding_sphere[3]
                b3d_obj[Blk021.GroupCnt.get_prop()] = group_cnt
                b3d_obj[Blk021.Unk_Int2.get_prop()] = unknown2
                b3d_obj.parent = parent_obj
                get_context_collection_objects(context).link(b3d_obj)
                real_name = b3d_obj.name
                obj_string[-1] = b3d_obj.name

            elif (block_type == 23): #colision mesh

                var1 = struct.unpack("<i",file.read(4))[0]
                ctype = struct.unpack("<i",file.read(4))[0]
                cnt = struct.unpack("<i",file.read(4))[0]
                unknowns = []
                for i in range(cnt):
                    unknowns.append(struct.unpack("<i",file.read(4))[0])

                verts_block_num = struct.unpack("<i",file.read(4))[0]
                num = 0
                faces = []
                l_vertexes = []
                for i in range(verts_block_num):
                    verts_in_block = struct.unpack("<i",file.read(4))[0]


                    face = []
                    for j in range(verts_in_block):
                        face.append(num)
                        num+=1
                        l_vertexes.append(struct.unpack("<3f",file.read(12)))
                    faces.append(face)

                if not used_blocks[str(block_type)]:
                    continue

                b3d_mesh = (bpy.data.meshes.new(obj_name))

                centroid = get_center_coord(l_vertexes)

                l_vertexes = recalc_to_local_coord(centroid, l_vertexes)

                b3d_mesh.from_pydata(l_vertexes,[],faces)

                b3d_obj = bpy.data.objects.new(obj_name, b3d_mesh)
                b3d_obj[BLOCK_TYPE] = block_type
                b3d_obj.location = centroid
                b3d_obj[Blk023.Unk_Int1.get_prop()] = var1
                b3d_obj[Blk023.Surface.get_prop()] = ctype
                b3d_obj[Blk023.Unk_List.get_prop()] = unknowns

                b3d_obj.parent = parent_obj
                get_context_collection_objects(context).link(b3d_obj)
                real_name = b3d_obj.name
                obj_string[-1] = b3d_obj.name

            elif (block_type == 24): #настройки положения обьекта

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

                flag = struct.unpack("<i",file.read(4))[0]
                child_cnt = struct.unpack("<i", file.read(4))[0]

                if not used_blocks[str(block_type)]:
                    continue

                x_d = 0.0
                y_d = 0.0
                z_d = 0.0

                pi = 3.14159265358979
                test_var = 0.0
                test_var = ((m33*m33) + (m31*m31))
                var_cy = sqrt(test_var)

                if (var_cy > 16*sys.float_info.epsilon):
                    z_d = atan2(m12, m22)
                    x_d = atan2(- m32, var_cy)
                    y_d = atan2(m31, m33)
                    # log.debug("MORE than 16")
                else:
                    z_d = atan2(- m21, m11)
                    x_d = atan2(- m32, var_cy)
                    y_d = 0
                    # log.debug("LESS than 16")

                rot_x = ((x_d * 180) / pi)
                rot_y = ((y_d * 180) / pi)
                rot_z = ((z_d * 180) / pi)

                b3d_obj = bpy.data.objects.new(obj_name, None)
                b3d_obj[BLOCK_TYPE] = block_type
                b3d_obj.rotation_euler[0] = x_d
                b3d_obj.rotation_euler[1] = y_d
                b3d_obj.rotation_euler[2] = z_d
                b3d_obj.location = sp_pos
                set_empty_type(b3d_obj, 'ARROWS')
                b3d_obj[Blk024.Flag.get_prop()] = flag
                b3d_obj.parent = parent_obj
                get_context_collection_objects(context).link(b3d_obj)
                real_name = b3d_obj.name
                obj_string[-1] = b3d_obj.name

            elif (block_type == 25): #copSiren????/ контейнер

                unknown1 = struct.unpack("<3i",file.read(12))

                name = read_name(file)
                unknown_sphere1 = struct.unpack("<3f",file.read(12))
                unknown_sphere2 = struct.unpack("<3f",file.read(12))
                unknown2 = struct.unpack("<5f",file.read(20))

                if not used_blocks[str(block_type)]:
                    continue

                b3d_obj = bpy.data.objects.new(obj_name, None)
                b3d_obj[BLOCK_TYPE] = block_type
                b3d_obj[Blk025.Unk_XYZ.get_prop()] = unknown1
                b3d_obj[Blk025.Name.get_prop()] = name
                b3d_obj[Blk025.Unk_XYZ1.get_prop()] = unknown_sphere1
                b3d_obj[Blk025.Unk_XYZ2.get_prop()] = unknown_sphere2
                b3d_obj[Blk025.Unk_Float1.get_prop()] = unknown2[0]
                b3d_obj[Blk025.Unk_Float2.get_prop()] = unknown2[1]
                b3d_obj[Blk025.Unk_Float3.get_prop()] = unknown2[2]
                b3d_obj[Blk025.Unk_Float4.get_prop()] = unknown2[3]
                b3d_obj[Blk025.Unk_Float5.get_prop()] = unknown2[4]

                b3d_obj.parent = parent_obj
                get_context_collection_objects(context).link(b3d_obj)
                real_name = b3d_obj.name
                obj_string[-1] = b3d_obj.name

            elif (block_type == 26):

                bounding_sphere = struct.unpack("<4f",file.read(16))

                unknown_sphere1 = struct.unpack("<3f",file.read(12))
                unknown_sphere2 = struct.unpack("<3f",file.read(12))
                unknown_sphere3 = struct.unpack("<3f",file.read(12))

                child_cnt = struct.unpack("<i",file.read(4))

                if not used_blocks[str(block_type)]:
                    continue

                b3d_obj = bpy.data.objects.new(obj_name, None)
                b3d_obj[BLOCK_TYPE] = block_type
                # b3d_obj[Blk026.XYZ.get_prop()] = bounding_sphere[0:3]
                # b3d_obj[Blk026.r.get_prop()] = bounding_sphere[3]
                b3d_obj[Blk026.Unk_XYZ1.get_prop()] = unknown_sphere1
                b3d_obj[Blk026.Unk_XYZ2.get_prop()] = unknown_sphere2
                b3d_obj[Blk026.Unk_XYZ3.get_prop()] = unknown_sphere3

                b3d_obj.parent = parent_obj
                get_context_collection_objects(context).link(b3d_obj)
                real_name = b3d_obj.name
                obj_string[-1] = b3d_obj.name

            elif (block_type == 27):

                bounding_sphere = struct.unpack("<4f",file.read(16))
                flag1 = struct.unpack("<i",file.read(4))
                unknown_sphere = struct.unpack("<3f",file.read(12))

                material_id = struct.unpack("<i",file.read(4))

                if not used_blocks[str(block_type)]:
                    continue

                b3d_obj = bpy.data.objects.new(obj_name, None)
                b3d_obj[BLOCK_TYPE] = block_type
                # b3d_obj[Blk027.XYZ.get_prop()] = bounding_sphere[0:3]
                # b3d_obj[Blk027.r.get_prop()] = bounding_sphere[3]
                b3d_obj[Blk027.Flag.get_prop()] = flag1
                b3d_obj[Blk027.Unk_XYZ.get_prop()] = unknown_sphere
                b3d_obj[Blk027.Material.get_prop()] = material_id

                b3d_obj.parent = parent_obj
                get_context_collection_objects(context).link(b3d_obj)
                real_name = b3d_obj.name
                obj_string[-1] = b3d_obj.name

            elif (block_type == 28): #face

                l_vertexes = []
                l_faces = []
                faces_new = []
                l_faces_all = []
                l_uvs = []
                scale_base = 1
                curface = 0
                texnums = {}
                vertex_block_uvs = []
                vertex_block_uvs.append([])
                overriden_uvs = []
                uv_indexes = []
                formats = []
                unk_floats = []
                unk_ints = []

                bounding_sphere = struct.unpack("<4f",file.read(16))
                sprite_center = struct.unpack("<3f",file.read(12))

                polygon_count = struct.unpack("<i",file.read(4))[0]

                for i in range(polygon_count):

                    format_raw = struct.unpack("<i",file.read(4))[0]
                    poly_format = format_raw & 0xFFFF
                    uv_count = ((format_raw & 0xFF00) >> 8) + 1 #ah
                    triangulate_offset = poly_format & 0b10000000

                    unk_float = struct.unpack("<f",file.read(4))[0]
                    unk_int = struct.unpack("<i",file.read(4))[0]
                    texnum = struct.unpack("<i",file.read(4))[0]

                    vert_num = struct.unpack("<i", file.read(4))[0]

                    poly_block_uvs = [{}]

                    poly_block_len = len(poly_block_uvs)

                    for i in range(uv_count - poly_block_len):
                        poly_block_uvs.append({})

                    l_faces = []
                    faces_new = []

                    for k in range(vert_num):
                        scale_u = struct.unpack("<f", file.read(4))[0]
                        scale_v = struct.unpack("<f", file.read(4))[0]
                        l_vertexes.append((sprite_center[0], sprite_center[1]-scale_u*scale_base, sprite_center[2]+scale_v*scale_base))
                        l_faces.append(curface)
                        if poly_format & 0b10:
                            vertex_block_uvs[0].append(struct.unpack("<2f",file.read(8)))
                            poly_block_uvs[0][curface] = vertex_block_uvs[0][curface]
                            for j in range(uv_count-1):
                                poly_block_uvs[j][curface] = struct.unpack("<2f",file.read(8))
                        # else:
                        #     poly_block_uvs[0][curface] = vertex_block_uvs[0][curface]
                        curface += 1


                    #Save materials for faces
                    if texnum in texnums:
                        texnums[texnum].append(l_faces)
                    else:
                        texnums[texnum] = []
                        texnums[texnum].append(l_faces)

                    # store uv coords for each face
                    if len(poly_block_uvs) > len(overriden_uvs):
                        for i in range(len(poly_block_uvs)-len(overriden_uvs)):
                            overriden_uvs.append([])

                    #Triangulating faces
                    for t in range(len(l_faces)-2):
                        if not triangulate_offset:
                            if t%2 == 0:
                                faces_new.append([l_faces[t-1],l_faces[t],l_faces[t+1]])
                            else:
                                faces_new.append([l_faces[t],l_faces[t+1],l_faces[t+2]])
                        else:
                            if t%2 == 0:
                                faces_new.append([l_faces[t],l_faces[t+1],l_faces[t+2]])
                            else:
                                faces_new.append([l_faces[t],l_faces[t+2],l_faces[t+1]])

                        for u, over_uv in enumerate(poly_block_uvs):
                            if over_uv: #not empty
                                overriden_uvs[u].append((over_uv[faces_new[t][0]], over_uv[faces_new[t][1]], over_uv[faces_new[t][2]]))

                    # store face indexes for setting uv coords later
                        uv_indexes.append(faces_new[t])
                        formats.append(format_raw)
                        unk_floats.append(unk_float)
                        unk_ints.append(unk_int)

                    l_faces_all.extend(faces_new)


                if not used_blocks[str(block_type)]:
                    continue

                b3d_mesh = (bpy.data.meshes.new(obj_name))

                l_vertexes = recalc_to_local_coord(bounding_sphere[:3], l_vertexes)

                b3d_mesh.from_pydata(l_vertexes,[],l_faces_all)

                # Ev = threading.Event()
                # Tr = threading.Thread(target=b3d_mesh.from_pydata, args = (l_vertexes,[],l_faces_all))
                # Tr.start()
                # Ev.set()
                # Tr.join()


                # for simplicity
                # for u, uvMap in enumerate(vertex_block_uvs):
                #     if len(uvMap):
                #         custom_uv = get_uv_layers(b3d_mesh).new()
                #         custom_uv.name = "UVmapVert{}".format(u)
                #         uvs_mesh = []

                #         for i, texpoly in enumerate(b3d_mesh.polygons):
                #             for j,loop in enumerate(texpoly.loop_indices):
                #                 uvs_mesh = (uvMap[uv_indexes[i][j]][0],1 - uvMap[uv_indexes[i][j]][1])
                #                 custom_uv.data[loop].uv = uvs_mesh

                for u, uv_over in enumerate(overriden_uvs):
                    if len(uv_over):
                        custom_uv = get_uv_layers(b3d_mesh).new()
                        custom_uv.name = "UVMap"
                        
                        set_uv_values(custom_uv, b3d_mesh, uv_over)
                       
                if self.to_import_textures:
                    #For assign_material_by_vertices just-in-case
                    # bpy.ops.object.mode_set(mode = 'OBJECT')
                    #Set appropriate meaterials
                    if len(texnums.keys()) > 1:
                        for texnum in texnums:
                            mat = res_module.materials[int(texnum)].id_mat
                            # mat = bpy.data.materials.get(res_module.materials[int(texnum)].mat_name)
                            b3d_mesh.materials.append(mat)
                            last_index = len(b3d_mesh.materials)-1

                            for vert_arr in texnums[texnum]:
                                # self.lock.acquire()
                                assign_material_by_vertices(b3d_obj, vert_arr, last_index)
                                # self.lock.release()
                    else:
                        for texnum in texnums:
                            mat = res_module.materials[int(texnum)].id_mat
                            # mat = bpy.data.materials.get(res_module.materials[int(texnum)].mat_name)
                            b3d_mesh.materials.append(mat)

                create_custom_attribute(b3d_mesh, formats, Pfb028, Pfb028.Format_Flags)

                # those are usually consts in all objects
                # create_custom_attribute(b3d_mesh, unk_floats, Pfb028, Pfb028.Unk_Float1)
                # create_custom_attribute(b3d_mesh, unk_ints, Pfb028, Pfb028.Unk_Int2)

                b3d_obj = bpy.data.objects.new(obj_name, b3d_mesh)
                b3d_obj[BLOCK_TYPE] = block_type
                # b3d_obj[Blk028.XYZ.get_prop()] = bounding_sphere[0:3]
                # b3d_obj[Blk028.r.get_prop()] = bounding_sphere[3]
                b3d_obj[Blk028.Sprite_Center.get_prop()] = sprite_center
                b3d_obj.location = bounding_sphere[0:3]

                b3d_obj.parent = parent_obj
                get_context_collection_objects(context).link(b3d_obj) #добавляем в сцену обьект
                real_name = b3d_obj.name
                obj_string[-1] = b3d_obj.name

            elif (block_type == 29):

                bounding_sphere = struct.unpack("<4f",file.read(16))
                num0 = struct.unpack("<i",file.read(4))[0]
                num1 = struct.unpack("<i",file.read(4))[0]

                unknown_sphere = struct.unpack("<4f",file.read(16))

                if num0 > 0:
                    f = struct.unpack("<{}f".format(num0),file.read(4*num0))

                child_cnt = struct.unpack("<i",file.read(4))[0]

                if not used_blocks[str(block_type)]:
                    continue

                b3d_obj = bpy.data.objects.new(obj_name, None)
                b3d_obj[BLOCK_TYPE] = block_type
                # b3d_obj[Blk029.XYZ.get_prop()] = bounding_sphere[0:3]
                # b3d_obj[Blk029.r.get_prop()] = bounding_sphere[3]
                b3d_obj[Blk029.Unk_Int1.get_prop()] = num0
                b3d_obj[Blk029.Unk_Int2.get_prop()] = num1
                b3d_obj[Blk029.Unk_XYZ.get_prop()] = unknown_sphere[0:3]
                b3d_obj[Blk029.Unk_R.get_prop()] = unknown_sphere[3]

                b3d_obj.parent = parent_obj
                get_context_collection_objects(context).link(b3d_obj)
                real_name = b3d_obj.name
                obj_string[-1] = b3d_obj.name

            elif (block_type == 30):

                bounding_sphere = struct.unpack("<4f",file.read(16))
                connected_room_name = read_name(file)

                p1 = struct.unpack("<3f",file.read(12))
                p2 = struct.unpack("<3f",file.read(12))

                if not used_blocks[str(block_type)]:
                    continue

                splitted = connected_room_name.split(":")
                module_name = ""
                room_name = ""

                if len(splitted) == 2:
                    module_name = splitted[0]
                    room_name = splitted[1]
                elif len(splitted) == 1:
                    module_name = res_basename
                    room_name = splitted[0]

                full_room_name = "{}:{}".format(module_name, room_name)

                sorted_rooms = sorted([current_room_name, full_room_name])


                border_name = "|".join(sorted_rooms)


                if not border_name in borders:
                    borders[border_name] = {
                        "bounding_point": bounding_sphere[0:3],
                        "bounding_rad": bounding_sphere[3],
                        "points": [None]*4
                    }


                    if sorted_rooms[0] == current_room_name:
                        borders[border_name]["points"] = [
                            (p1[0], p1[1], p1[2]),
                            (p1[0], p1[1], p2[2]),
                            (p2[0], p2[1], p2[2]),
                            (p2[0], p2[1], p1[2]),
                        ]
                    else:
                        borders[border_name]["points"] = [
                            (p1[0], p1[1], p2[2]),
                            (p1[0], p1[1], p1[2]),
                            (p2[0], p2[1], p1[2]),
                            (p2[0], p2[1], p2[2]),
                        ]

            elif (block_type == 31):

                bounding_sphere = struct.unpack("<4f",file.read(16))

                num = struct.unpack("<i",file.read(4))[0]
                unknown_sphere = struct.unpack("<4f",file.read(16))
                num2 = struct.unpack("<i",file.read(4))[0]
                unknown = struct.unpack("<3f",file.read(12))
                for i in range(num):
                    struct.unpack("<fi",file.read(8))

                if not used_blocks[str(block_type)]:
                    continue

                b3d_obj = bpy.data.objects.new(obj_name, None)
                b3d_obj[BLOCK_TYPE] = block_type
                # b3d_obj[Blk031.XYZ.get_prop()] = bounding_sphere[0:3]
                # b3d_obj[Blk031.r.get_prop()] = bounding_sphere[3]
                b3d_obj[Blk031.Unk_Int1.get_prop()] = num
                b3d_obj[Blk031.Unk_XYZ1.get_prop()] = unknown_sphere[0:3]
                b3d_obj[Blk031.Unk_R.get_prop()] = unknown_sphere[3]
                b3d_obj[Blk031.Unk_Int2.get_prop()] = num2
                b3d_obj[Blk031.Unk_XYZ2.get_prop()] = unknown

                b3d_obj.parent = parent_obj
                get_context_collection_objects(context).link(b3d_obj)
                real_name = b3d_obj.name
                obj_string[-1] = b3d_obj.name

            elif (block_type == 33): #lamp

                bounding_sphere = struct.unpack("<4f",file.read(16))

                use_lights = struct.unpack("<i",file.read(4))[0]
                light_type = struct.unpack("<i",file.read(4))[0]
                flag1 = struct.unpack("<i",file.read(4))[0]

                unknown_vector1 = struct.unpack("<3f",file.read(12))
                unknown_vector2 = struct.unpack("<3f",file.read(12))
                unknown1 = struct.unpack("<f",file.read(4))[0]#global_light_state
                unknown2 = struct.unpack("<f",file.read(4))[0]
                light_radius = struct.unpack("<f",file.read(4))[0]
                intensity = struct.unpack("<f",file.read(4))[0]
                unknown3 = struct.unpack("<f",file.read(4))[0]
                unknown4 = struct.unpack("<f",file.read(4))[0]
                rgb = struct.unpack("<3f",file.read(12))

                child_cnt = struct.unpack("<i",file.read(4))[0]

                if not used_blocks[str(block_type)]:
                    continue

                b3d_obj = bpy.data.objects.new(obj_name, None)
                b3d_obj[BLOCK_TYPE] = block_type
                # b3d_obj[Blk033.XYZ.get_prop()] = bounding_sphere[0:3]
                # b3d_obj[Blk033.r.get_prop()] = bounding_sphere[3]
                b3d_obj[Blk033.Use_Lights.get_prop()] = use_lights
                b3d_obj[Blk033.Light_Type.get_prop()] = light_type
                b3d_obj[Blk033.Flag.get_prop()] = flag1
                b3d_obj[Blk033.Unk_XYZ1.get_prop()] = unknown_vector1
                b3d_obj[Blk033.Unk_XYZ2.get_prop()] = unknown_vector2
                b3d_obj[Blk033.Unk_Float1.get_prop()] = unknown1
                b3d_obj[Blk033.Unk_Float2.get_prop()] = unknown2
                b3d_obj[Blk033.Light_R.get_prop()] = light_radius
                b3d_obj[Blk033.Intens.get_prop()] = intensity
                b3d_obj[Blk033.Unk_Float3.get_prop()] = unknown3
                b3d_obj[Blk033.Unk_Float4.get_prop()] = unknown4
                b3d_obj[Blk033.RGB.get_prop()] = rgb


                b3d_obj.parent = parent_obj
                get_context_collection_objects(context).link(b3d_obj)
                real_name = b3d_obj.name
                obj_string[-1] = b3d_obj.name

            elif (block_type == 34): #lamp
                num = 0

                bounding_sphere = struct.unpack("<4f",file.read(16))
                file.read(4) #skipped Int
                num = struct.unpack("<i",file.read(4))[0]
                l_coords = []

                unknown1 = 0

                for i in range(num):
                    l_coords.append(struct.unpack("<3f",file.read(12)))
                    unknown1 = struct.unpack("<i",file.read(4))[0]

                if not used_blocks[str(block_type)]:
                    continue

                curve_data = bpy.data.curves.new('curve', type='CURVE')

                curve_data.dimensions = '3D'
                curve_data.resolution_u = 2

                # map coords to spline
                polyline = curve_data.splines.new('POLY')
                polyline.points.add(len(l_coords)-1)
                for i, coord in enumerate(l_coords):
                    x,y,z = coord
                    polyline.points[i].co = (x, y, z, 1)

                curve_data.bevel_depth = 0.01

                b3d_obj = bpy.data.objects.new(obj_name, curve_data)
                b3d_obj[BLOCK_TYPE] = block_type
                # b3d_obj[Blk034.XYZ.get_prop()] = bounding_sphere[0:3]
                # b3d_obj[Blk034.r.get_prop()] = bounding_sphere[3]
                b3d_obj[Blk034.UnkInt.get_prop()] = unknown1

                b3d_obj.parent = parent_obj
                get_context_collection_objects(context).link(b3d_obj)
                real_name = b3d_obj.name
                obj_string[-1] = b3d_obj.name

            elif (block_type == 35): #mesh

                bounding_sphere = struct.unpack("<4f",file.read(16))
                faces_all = []
                faces = []
                poly_block_uvs = []

                m_type = struct.unpack("<i",file.read(4))[0]
                texnum = struct.unpack("<i",file.read(4))[0]
                polygon_count = struct.unpack("<i",file.read(4))[0]
                overriden_uvs = []
                uv_indexes = []
                l_normals = normals
                l_normals_off = normals_off

                formats = []
                unk_floats = []
                unk_ints = []

                for i in range(polygon_count):
                    faces = []
                    format_raw = struct.unpack("<i",file.read(4))[0]
                    poly_format = format_raw ^ 1
                    uv_count = ((poly_format & 0xFF00) >> 8) #ah
                    triangulate_offset = poly_format & 0b10000000

                    if poly_format & 0b10:
                        uv_count += 1

                    poly_block_uvs = [{}]

                    poly_block_len = len(poly_block_uvs)

                    for i in range(uv_count - poly_block_len):
                        poly_block_uvs.append({})

                    unk_float = struct.unpack("<f",file.read(4))[0]
                    unk_int = struct.unpack("<i",file.read(4))[0]
                    texnum = struct.unpack("<i",file.read(4))[0]

                    vertex_count = struct.unpack("<i",file.read(4))[0]

                    for j in range(vertex_count):
                        face_idx = struct.unpack("<i",file.read(4))[0]
                        faces.append(face_idx)
                        if poly_format & 0b10:
                            # uv override
                            for k in range(uv_count):
                                poly_block_uvs[k][face_idx] = struct.unpack("<2f",file.read(8))
                        else:
                            poly_block_uvs[0][face_idx] = vertex_block_uvs[0][face_idx]
                        if poly_format & 0b100000 and poly_format & 0b10000:
                            if poly_format & 0b1:
                                l_normals[face_idx] = struct.unpack("<3f",file.read(12))
                            else:
                                l_normals_off[face_idx] = struct.unpack("<f",file.read(4))


                    faces_all.append(faces)

                    formats.append(format_raw)
                    unk_floats.append(unk_float)
                    unk_ints.append(unk_int)

                    # store uv coords for each face
                    if len(poly_block_uvs) > len(overriden_uvs):
                        for i in range(len(poly_block_uvs)-len(overriden_uvs)):
                            overriden_uvs.append([])

                    for u, over_uv in enumerate(poly_block_uvs):
                        if over_uv:
                            overriden_uvs[u].append((over_uv[faces[0]], over_uv[faces[1]], over_uv[faces[2]]))

                    # store face indexes for setting uv coords later
                    uv_indexes.append((faces[0], faces[1], faces[2]))

                    #https://docs.blender.org/api/current/bpy.types.bpy_prop_collection.html#bpy.types.bpy_prop_collection
                    #seq must be uni-dimensional
                    # normals_set.extend([normals[faces[0]], normals[faces[1]], normals[faces[2]]])
                    # normals_set.extend(list(normals[faces[0]]))
                    # normals_set.extend(list(normals[faces[1]]))
                    # normals_set.extend(list(normals[faces[2]]))
                    # intens_set.extend(list(intencities[faces[0]]))
                    # intens_set.extend(list(intencities[faces[1]]))
                    # intens_set.extend(list(intencities[faces[2]]))
                    # intens_set.extend([intencities[faces[0]], intencities[faces[1]], intencities[faces[2]]])

                if not used_blocks[str(block_type)]:
                    continue

                # log.debug(vertex_block_uvs)
                # log.debug(overriden_uvs)

                b3d_mesh = (bpy.data.meshes.new(obj_name))
                cur_vertexes, cur_faces, indices, old_new_transf, new_old_transf = get_used_vertices_and_transform(vertexes, faces_all)

                cur_normals = []
                cur_normals_off = []
                for i in range(len(cur_vertexes)):
                    cur_normals.append(l_normals[new_old_transf[i]])
                    cur_normals_off.append(l_normals_off[new_old_transf[i]])

                cur_vertexes = recalc_to_local_coord(bounding_sphere[:3], cur_vertexes)

                b3d_mesh.from_pydata(cur_vertexes,[],cur_faces)

                # Ev = threading.Event()
                # Tr = threading.Thread(target=b3d_mesh.from_pydata, args = (cur_vertexes,[],cur_faces))
                # Tr.start()
                # Ev.set()
                # Tr.join()

                # newIndices = get_user_vertices(cur_faces)

                # blender generates his own normals, so imported vertex normals doesn't affect
                # them too much.
                if len(normals) > 0:
                    b3d_mesh.use_auto_smooth = True
                    normal_list = []
                    for i,vert in enumerate(b3d_mesh.vertices):
                        normal_list.append(normals[new_old_transf[i]])
                        # b3d_mesh.vertices[idx].normal = normals[idx]
                    # log.debug(normal_list)
                    b3d_mesh.normals_split_custom_set_from_vertices(normal_list)

                # if len(normals) > 0:
                #     for i,idx in enumerate(newIndices):
                #         b3d_mesh.vertices[idx].normal = normals[idx]


                # for simplicity
                # for u, uvMap in enumerate(vertex_block_uvs):

                #     custom_uv = get_uv_layers(b3d_mesh).new()
                #     custom_uv.name = "UVmapVert{}".format(u)
                #     uvs_mesh = []

                #     for i, texpoly in enumerate(b3d_mesh.polygons):
                #         for j,loop in enumerate(texpoly.loop_indices):
                #             uvs_mesh = (uvMap[uv_indexes[i][j]][0],1 - uvMap[uv_indexes[i][j]][1])
                #             custom_uv.data[loop].uv = uvs_mesh

                for u, uv_over in enumerate(overriden_uvs):

                    custom_uv = get_uv_layers(b3d_mesh).new()
                    custom_uv.name = "UVMap"
                    
                    set_uv_values(custom_uv, b3d_mesh, uv_over)
                    
                # b3d_mesh.attributes["my_normal"].data.foreach_set("vector", normals_set)

                create_custom_attribute(b3d_mesh, formats, Pfb035, Pfb035.Format_Flags)
                # those are usually consts in all objects
                # create_custom_attribute(b3d_mesh, unk_floats, Pfb035, Pfb035.Unk_Float1)
                # create_custom_attribute(b3d_mesh, unk_ints, Pfb035, Pfb035.Unk_Int2)

                # cancel for now, maybe find workaround later
                # create_custom_attribute(b3d_mesh, cur_normals_off, Pvb035, Pvb035.Normal_Switch)
                # create_custom_attribute(b3d_mesh, cur_normals, Pvb035, Pvb035.Custom_Normal)

                if self.to_import_textures:
                    mat = res_module.materials[int(texnum)].id_mat
                    # mat = bpy.data.materials.get(res_module.materials[int(texnum)].mat_name)
                    b3d_mesh.materials.append(mat)


                b3d_obj = bpy.data.objects.new(obj_name, b3d_mesh)
                b3d_obj.parent = parent_obj
                b3d_obj[BLOCK_TYPE] = block_type
                b3d_obj.location = bounding_sphere[0:3]
                # b3d_obj[Blk035.XYZ.get_prop()] = bounding_sphere[0:3]
                # b3d_obj[Blk035.r.get_prop()] = bounding_sphere[3]
                b3d_obj[Blk035.MType.get_prop()] = m_type
                b3d_obj[Blk035.TexNum.get_prop()] = texnum
                # b3d_obj['FType'] = 0
                # try:
                #     b3d_obj['SType'] = b3d_obj.parent['SType']
                # except:
                #     b3d_obj['SType'] = 2
                # b3d_obj['BType'] = 35
                real_name = b3d_obj.name
                # for face in b3d_mesh.polygons:
                #     face.use_smooth = True
                get_context_collection_objects(context).link(b3d_obj) #добавляем в сцену обьект
                obj_string[-1] = b3d_obj.name

            elif (block_type == 36):

                vertexes = []
                normals = []
                normals_off = []
                uv = []
                vertex_block_uvs = []

                bounding_sphere = struct.unpack("<4f",file.read(16))
                name1 = read_name(file)
                name2 = read_name(file)

                format_raw = struct.unpack("<i",file.read(4))[0]
                uv_count = format_raw >> 8
                vert_format = format_raw & 0xFF

                vertex_block_uvs.append([])
                for i in range(uv_count):
                    vertex_block_uvs.append([])

                vertex_count = struct.unpack("<i",file.read(4))[0]
                if vert_format == 0:
                    pass
                else:
                    for i in range(vertex_count):
                        vertexes.append(struct.unpack("<3f",file.read(12)))
                        vertex_block_uvs[0].append(struct.unpack("<2f",file.read(8)))
                        for j in range(uv_count):
                            vertex_block_uvs[j+1].append(struct.unpack("<2f",file.read(8)))
                        if vert_format == 1 or vert_format == 2:    #Vertex with normals
                            normals.append(struct.unpack("<3f",file.read(12)))
                            normals_off.append(1.0)
                        elif vert_format == 3: #отличается от шаблона 010Editor
                            normals.append((0.0, 0.0, 0.0))
                            normals_off.append(struct.unpack("<f",file.read(4))[0])
                        else:
                            normals.append((0.0, 0.0, 0.0))
                            normals_off.append(1.0)

                child_cnt = struct.unpack("<i",file.read(4))[0]#01 00 00 00 subblocks count

                if not used_blocks[str(block_type)]:
                    continue

                b3d_obj = bpy.data.objects.new(obj_name, None)
                b3d_obj[BLOCK_TYPE] = block_type
                # b3d_obj[Blk036.XYZ.get_prop()] = bounding_sphere[0:3]
                # b3d_obj[Blk036.r.get_prop()] = bounding_sphere[3]
                b3d_obj[Blk036.Name1.get_prop()] = name1
                b3d_obj[Blk036.Name2.get_prop()] = name2
                b3d_obj[Blk036.VType.get_prop()] = format_raw

                b3d_obj.parent = parent_obj
                get_context_collection_objects(context).link(b3d_obj)
                real_name = b3d_obj.name
                obj_string[-1] = b3d_obj.name

            elif (block_type == 37):

                vertexes = []
                normals = []
                normals_off = []
                vertex_block_uvs = []
                uv = []

                bounding_sphere = struct.unpack("<4f",file.read(16))

                group_name = read_name(file)

                format_raw = struct.unpack("<i",file.read(4))[0]
                uv_count = format_raw >> 8
                vert_format = format_raw & 0xFF

                vertex_block_uvs.append([])
                for i in range(uv_count):
                    vertex_block_uvs.append([])


                vertex_count = struct.unpack("<i",file.read(4))[0]

                if vertex_count > 0:

                    if vert_format == 0:
                        pass
                    else:
                        for i in range(vertex_count):
                            vertexes.append(struct.unpack("<3f",file.read(12)))
                            vertex_block_uvs[0].append(struct.unpack("<2f",file.read(8)))
                            for j in range(uv_count):
                                vertex_block_uvs[j+1].append(struct.unpack("<2f",file.read(8)))
                            if vert_format == 1 or vert_format == 2:    #Vertex with normals
                                normals.append(struct.unpack("<3f",file.read(12)))
                                normals_off.append(1.0)
                            elif vert_format == 3: #отличается от шаблона 010Editor
                                normals.append((0.0, 0.0, 0.0))
                                normals_off.append(struct.unpack("<f",file.read(4))[0])
                            else:
                                normals.append((0.0, 0.0, 0.0))
                                normals_off.append(1.0)

                child_cnt = struct.unpack("<i",file.read(4))[0]#01 00 00 00 subblocks count

                # if len(vertex_block_uvs) == 2:
                #     vertex_block_uvs = [vertex_block_uvs[1], vertex_block_uvs[0]]


                if not used_blocks[str(block_type)]:
                    continue

                b3d_obj = bpy.data.objects.new(obj_name, None) #create empty
                b3d_obj[BLOCK_TYPE] = block_type
                # b3d_obj[Blk037.XYZ.get_prop()] = bounding_sphere[0:3]
                # b3d_obj[Blk037.r.get_prop()] = bounding_sphere[3]
                b3d_obj[Blk037.Name1.get_prop()] = group_name
                b3d_obj[Blk037.VType.get_prop()] = format_raw

                b3d_obj.parent = parent_obj
                get_context_collection_objects(context).link(b3d_obj)
                real_name = b3d_obj.name
                obj_string[-1] = b3d_obj.name

            elif (block_type == 39):

                bounding_sphere = struct.unpack("<4f",file.read(16))
                color_r = struct.unpack("<i",file.read(4))
                unknown = struct.unpack("<f",file.read(4))
                fog_start = struct.unpack("<f",file.read(4))
                fog_end = struct.unpack("<f",file.read(4))
                color_id = struct.unpack("<i",file.read(4))
                child_cnt = struct.unpack("<i",file.read(4))

                if not used_blocks[str(block_type)]:
                    continue

                b3d_obj = bpy.data.objects.new(obj_name, None)
                b3d_obj[BLOCK_TYPE] = block_type
                # b3d_obj[Blk039.XYZ.get_prop()] = bounding_sphere[0:3]
                # b3d_obj[Blk039.r.get_prop()] = bounding_sphere[3]
                b3d_obj[Blk039.Color_R.get_prop()] = color_r
                b3d_obj[Blk039.Unk_Float1.get_prop()] = unknown
                b3d_obj[Blk039.Fog_Start.get_prop()] = fog_start
                b3d_obj[Blk039.Fog_End.get_prop()] = fog_end
                b3d_obj[Blk039.Color_Id.get_prop()] = color_id

                b3d_obj.parent = parent_obj
                get_context_collection_objects(context).link(b3d_obj)
                real_name = b3d_obj.name
                obj_string[-1] = b3d_obj.name

            elif (block_type == 40):
                l_params = []

                bounding_sphere = struct.unpack("<4f",file.read(16))

                name1 = read_name(file)
                name2 = read_name(file)

                unknown1 = struct.unpack("<i",file.read(4))[0]
                unknown2 = struct.unpack("<i",file.read(4))[0]
                cnt = struct.unpack("<i",file.read(4))[0]

                for i in range(cnt):
                    l_params.append(struct.unpack("f",file.read(4))[0])

                if not used_blocks[str(block_type)]:
                    continue

                b3d_obj = bpy.data.objects.new(obj_name, None)
                b3d_obj[BLOCK_TYPE] = block_type
                # b3d_obj[Blk040.XYZ.get_prop()] = bounding_sphere[0:3]
                # b3d_obj[Blk040.r.get_prop()] = bounding_sphere[3]
                b3d_obj[Blk040.Name1.get_prop()] = name1
                b3d_obj[Blk040.Name2.get_prop()] = name2
                b3d_obj[Blk040.Unk_Int1.get_prop()] = unknown1
                b3d_obj[Blk040.Unk_Int2.get_prop()] = unknown2
                b3d_obj[Blk040.Unk_List.get_prop()] = l_params

                b3d_obj.location = bounding_sphere[:3]
                
                set_empty_type(b3d_obj, 'SPHERE')
                set_empty_size(b3d_obj, bounding_sphere[3])
                get_context_collection_objects(context).link(b3d_obj)
                real_name = b3d_obj.name

                b3d_obj.parent = parent_obj
                obj_string[-1] = b3d_obj.name
            else:
                log.warning('smthng wrng')
                return

            t2 = time.perf_counter()

            log.debug("Time: {:.6f} | Block #{}: {}".format(t2-t1, block_type, real_name))

    #create room borders(30)
    transf_collection = get_or_create_collection(BORDER_COLLECTION)
    if not is_before_2_80():
        if transf_collection.name not in bpy.context.scene.collection.children:
            bpy.context.scene.collection.children.link(transf_collection)

    for key in borders.keys():

        border = borders[key]

        b3d_mesh = (bpy.data.meshes.new("{}_mesh".format(key)))
        #0-x
        #1-y
        #2-z

        points = border["points"]

        l_vertexes = [
            points[0],
            points[1],
            points[2],
            points[3],
        ]


        l_vertexes = recalc_to_local_coord(border["bounding_point"], l_vertexes)

        l_faces = [
            (0,1,2,3)
        ]

        b3d_mesh.from_pydata(l_vertexes,[],l_faces)

        # Tr = threading.Thread(target=b3d_mesh.from_pydata, args = (l_vertexes,[],l_faces))
        # Tr.start()
        # Tr.join()
        room_names = key.split("|")
        splitted1 = room_names[0].split(":")
        splitted2 = room_names[1].split(":")

        res_name1 = splitted1[0]
        room_name1 = splitted1[1]

        res_name2 = splitted2[0]
        room_name2 = splitted2[1]

        b3d_obj = bpy.data.objects.new(key, b3d_mesh)
        b3d_obj[BLOCK_TYPE] = 30
        b3d_obj.location = border["bounding_point"]
        # b3d_obj[Blk030.XYZ.get_prop()] = border["bounding_point"]
        # b3d_obj[Blk030.r.get_prop()] = border["bounding_rad"]
        b3d_obj[Blk030.ResModule1.get_prop()] = res_name1
        b3d_obj[Blk030.RoomName1.get_prop()] = room_name1
        b3d_obj[Blk030.ResModule2.get_prop()] = res_name2
        b3d_obj[Blk030.RoomName2.get_prop()] = room_name2
        # b3d_obj[Blk030.Name.get_prop()] = connected_room_name
        # b3d_obj[Blk030.XYZ1.get_prop()] = p1
        # b3d_obj[Blk030.XYZ2.get_prop()] = p2

        b3d_obj.parent = None
        transf_collection.objects.link(b3d_obj)
