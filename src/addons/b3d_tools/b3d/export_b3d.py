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
    LEVEL_GROUP,
    BLOCK_TYPE
)

from ..common import (
    exportb3d_logger
)

from .common import (
    get_col_property_by_name,
    get_material_index_in_res,
    get_non_copy_name,
    is_root_obj,
    get_root_obj,
    is_empty_name,
    get_all_children,
    get_mult_obj_bounding_sphere,
    get_single_bounding_sphere,
    write_size,
    ftoi,
    RGBPacker
)


from ..compatibility import (
    get_uv_layers,
    matrix_multiply,
    get_empty_size,
    is_before_2_93
)

#Setup module logger
log = exportb3d_logger

def export_pro(file, textures_path):
    # file = open(myFile_pro+'.pro','w')

    #file.write('TEXTUREFILES ' + str(len(bpy.data.materials)) + '\n')

    #imgs = []
    #for img in bpy.data.images:
    #    imgs.append(img.name)

    #for material in bpy.data.materials:
    #    file.write('txr\\' + material.active_texture.name + '.txr' + '\n')

    #file.write('\n')

    file.write('MATERIALS {}\n'.format(str(len(bpy.data.materials))))

    materials = []
    num_tex = 0

    for material in bpy.data.materials:
        materials.append(material.name)

    for i in range(len(materials)):
        num_tex = i
        file.write('{} tex {}\n'.format(materials[i], str(num_tex + 1)))

    file.write('TEXTUREFILES {}\n'.format(str(len(bpy.data.materials))))

    imgs = []
    for img in bpy.data.images:
        imgs.append(img.name)

    for material in bpy.data.materials:
        try:
            file.write("{}{}txr\n".format(textures_path, material.texture_slots[0].texture.image.name[:-3]))
        except:
            file.write("{}error.txr\n".format(textures_path))

    file.write('\n')

def write_name(name, file):
    obj_name = ''
    if not is_empty_name(name):
        obj_name = name
    name_len = len(obj_name)
    if name_len <= 32:
        file.write(obj_name.encode("cp1251"))
    file.write(bytearray(b'\00'*(32-name_len)))
    return



def get_room_name(cur_res_module, room_string):
    result = ''
    room_split = room_string.split(':')
    res_module = room_split[0]
    room_name = room_split[1]

    if cur_res_module == res_module:
        result = room_name
    else:
        result = room_string

    return result

borders = {}
current_res = ''
current_room_name = ''

meshes_in_empty = {}
empty_to_mesh_keys = {}
unique_arrays = {}
created_bounders = {}

def fill_bounding_sphere_lists():

    global meshes_in_empty
    global empty_to_mesh_keys
    global unique_arrays
    global created_bounders

    # Getting 'empty' objects
    objs = [cn for cn in bpy.data.objects if cn.get(BLOCK_TYPE) in [8, 28, 35]]

    for obj in objs:
        cur_mesh_name = obj.name
        cur_obj = obj.parent
        while not is_root_obj(cur_obj):
            if cur_obj.get(BLOCK_TYPE) != 444:
                if meshes_in_empty.get(cur_obj.name) is None:
                    meshes_in_empty[cur_obj.name] = []
                    meshes_in_empty[cur_obj.name].append({
                        "obj": cur_mesh_name,
                        "transf": cur_mesh_name
                    })
                else:
                    meshes_in_empty[cur_obj.name].append({
                        "obj": cur_mesh_name,
                        "transf": cur_mesh_name
                    })

            cur_obj = cur_obj.parent

    #extend with 18 blocks
    objs = [cn for cn in bpy.data.objects if cn.get(BLOCK_TYPE) == 18]

    for obj in objs:
        referenceable_name = obj.get(Blk018.Add_Name.get_prop())
        space_name = obj.get(Blk018.Space_Name.get_prop())
        cur_mesh_list = meshes_in_empty.get(referenceable_name)
        if cur_mesh_list is not None:

            # global coords for 18 blocks parents
            global_transf_mesh_list = [{
                "obj": cn.get("obj"),
                "transf": space_name
                # "transf": cn.get("transf")
            } for cn in cur_mesh_list]

            cur_obj = obj.parent
            while not is_root_obj(cur_obj):
                if cur_obj.get(BLOCK_TYPE) != 444:
                    if meshes_in_empty.get(cur_obj.name) is None:
                        meshes_in_empty[cur_obj.name] = []
                        meshes_in_empty[cur_obj.name].extend(global_transf_mesh_list)
                    else:
                        meshes_in_empty[cur_obj.name].extend(global_transf_mesh_list)

                cur_obj = cur_obj.parent

            # local coords for 18 block itself
            cur_obj = obj
            local_transf_mesh_list = [{
                "obj": cn.get("obj"),
                # "transf": space_name
                "transf": cn.get("transf")
            } for cn in cur_mesh_list]

            if meshes_in_empty.get(cur_obj.name) is None:
                meshes_in_empty[cur_obj.name] = []
                meshes_in_empty[cur_obj.name].extend(local_transf_mesh_list)
            else:
                meshes_in_empty[cur_obj.name].extend(local_transf_mesh_list)

    # meshesInEmptyStr = [str(cn) for cn in meshes_in_empty.values()]

    # for m in meshesInEmptyStr:
    #     log.debug(m)

    for empty_name in meshes_in_empty.keys():
        meshes_in_empty[empty_name].sort(key= lambda x: '{}{}'.format(str(x["obj"]), str(x["transf"])))

        key = "||".join(['{}{}'.format(str(cn["obj"]), str(cn["transf"])) for cn in meshes_in_empty[empty_name]])
        empty_to_mesh_keys[empty_name] = key
        if not key in unique_arrays:
            unique_arrays[key] = meshes_in_empty[empty_name]

    for key in unique_arrays.keys():
        # objArr = [bpy.data.objects[cn] for cn in unique_arrays[key]]
        # created_bounders[key] = get_mult_obj_bounding_sphere(objArr)
        created_bounders[key] = get_mult_obj_bounding_sphere(unique_arrays[key])


def create_border_list():

    global borders
    global current_res
    borders = {}

    border_blocks = [cn for cn in bpy.data.objects if cn.get(BLOCK_TYPE) == 30 \
        and (cn.get(Blk030.ResModule1.get_prop()) == current_res or cn.get(Blk030.ResModule2.get_prop()) == current_res)]

    for bb in border_blocks:

        module1_name = bb[Blk030.ResModule1.get_prop()]
        module2_name = bb[Blk030.ResModule2.get_prop()]
        room1_name = bb[Blk030.RoomName1.get_prop()]
        room2_name = bb[Blk030.RoomName2.get_prop()]

        border1 = '{}:{}'.format(module1_name, room1_name)
        border2 = '{}:{}'.format(module2_name, room2_name)

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


def write_mesh_sphere(file, obj):

    block_type = obj.get(BLOCK_TYPE)

    if block_type in [
        8,35,
        28,30
    ]:
        result = get_single_bounding_sphere(obj)
        center = result[0]
        rad = result[1]

        file.write(struct.pack("<3f", *center))
        file.write(struct.pack("<f", rad))


def write_calculated_sphere(file, obj):
    global created_bounders
    global empty_to_mesh_keys

    block_type = obj.get(BLOCK_TYPE)

    center = (0.0, 0.0, 0.0)
    rad = 0.0

    # objects with children
    if block_type in [
        2,3,4,5,6,7,9,
        10,11,18,19,21,24,
        26,29,33,36,37,39
    ]:
        key = empty_to_mesh_keys.get(obj.name)
        if key is not None:
            result = created_bounders.get(key)
            center = result[0]
            rad = result[1]

    file.write(struct.pack("<3f", *center))
    file.write(struct.pack("<f", rad))


def write_bound_sphere(file, center, rad):
    file.write(struct.pack("<3f", *center))
    file.write(struct.pack("<f", rad))


# def write_size(file, ms):
#     end_ms = file.tell()
#     size = end_ms - ms - 4
#     file.seek(ms, 0)
#     file.write(struct.pack("<i", size))
#     file.seek(end_ms, 0)


def export_b3d(context, op, export_dir):

    global current_res

    global meshes_in_empty
    global empty_to_mesh_keys
    global unique_arrays
    global created_bounders

    meshes_in_empty = {}
    empty_to_mesh_keys = {}
    unique_arrays = {}
    created_bounders = {}

    fill_bounding_sphere_lists()

    if not os.path.isdir(export_dir):
        export_dir = os.path.dirname(export_dir)

    if op.partial_export:
        selected_obj = bpy.context.object
        if selected_obj is None:
            log.error('No selected object in outliner')
            return False

        exported_objects = [selected_obj.name]
    else:
        exported_objects = [sn.name for sn in op.res_modules if sn.state is True]

    for obj_name in exported_objects:

        obj = bpy.data.objects["{}.b3d".format(obj_name)]
        cur_root = get_root_obj(obj)

        all_objs = []

        if is_root_obj(obj):
            all_objs = cur_root.children
        else:
            all_objs = [obj]

        filepath = os.path.join(export_dir, cur_root.name)

        with open(filepath, 'wb') as file:

            # materials = []

            # for material in bpy.data.materials:
            #     materials.append(material.name)

            cp_materials = 0
            cp_data_blocks = 0
            cp_eof = 0

            #Header

            file.write(b'b3d\x00')#struct.pack("4c",b'b',b'3',b'D',b'\x00'))

            #reserve places for sizes
            file.write(struct.pack('<i',0)) #File Size
            file.write(struct.pack('<i',0)) #Mat list offset
            file.write(struct.pack('<i',0)) #Mat list Data Size
            file.write(struct.pack('<i',0)) #Data Chunks Offset
            file.write(struct.pack('<i',0)) #Data Chunks Size

            cp_materials = int(file.tell()/4)


            spaces = [cn for cn in all_objs if cn.get(BLOCK_TYPE) == 24]
            other = [cn for cn in all_objs if cn.get(BLOCK_TYPE) != 24]

            r_child = []
            r_child.extend(spaces)
            r_child.extend(other)

            res_modules = bpy.context.scene.my_tool.res_modules
            cur_res_name = cur_root.name[:-4]
            cur_module = get_col_property_by_name(res_modules, cur_res_name)

            current_res = cur_res_name
            create_border_list()

            file.write(struct.pack('<i', len(cur_module.materials))) #Materials Count
            for mat in cur_module.materials:
                write_name(mat.mat_name, file)

            cp_data_blocks = int(file.tell()/4)

            cur_max_cnt = 0
            cur_level = 0

            file.write(struct.pack("<i",111)) # Begin_Chunks

            # prevLevel = 0
            if len(r_child) > 0:
                for obj in r_child[:-1]:
                    if obj.get(BLOCK_TYPE) == 10 or obj.get(BLOCK_TYPE) == 9:
                        cur_max_cnt = 2
                    elif obj.get(BLOCK_TYPE) == 21:
                        cur_max_cnt = obj[Blk021.GroupCnt.get_prop()]
                    export_block(obj, False, cur_level, cur_max_cnt, [0], {}, file)

                    file.write(struct.pack("<i", 444))

                obj = r_child[-1]
                if obj.get(BLOCK_TYPE) == 10 or obj.get(BLOCK_TYPE) == 9:
                    cur_max_cnt = 2
                elif obj.get(BLOCK_TYPE) == 21:
                    cur_max_cnt = obj[Blk021.GroupCnt.get_prop()]
                export_block(obj, False, cur_level, cur_max_cnt, [0], {}, file)

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

def common_sort(cur_center, arr):
    global created_bounders
    global empty_to_mesh_keys

    def dist(cur_center, obj):

        center = None
        rad = None

        key = empty_to_mesh_keys.get(obj.name)
        if key is not None:
            result = created_bounders.get(key)
            center = result[0]
            rad = result[1]

        if center is None or rad is None:
            return 0
        else:
            return (sum(map(lambda xx,yy : (xx-yy)**2,cur_center,center)))**0.5

    new_list = [(obj, dist(cur_center, obj)) for obj in arr]
    new_list.sort(key= lambda x: x[1])
    return list(map(lambda x: x[0], new_list))

def export_block(obj, is_last, cur_level, max_groups, cur_groups, extra, file):

    global borders
    global current_res
    global current_room_name

    to_process_child = False
    cur_max_cnt = 0

    block = obj

    obj_name = get_non_copy_name(block.name)
    obj_type = block.get(BLOCK_TYPE)

    pass_to_mesh = {}

    if obj_type is not None:

        log.debug("{}_{}_{}_{}".format(block.get(BLOCK_TYPE), cur_level, 0, block.name))

        bl_children = list(block.children)

        cur_center = None
        cur_center = list(block.location)

        if obj_type == 444:
            if int(block.name[6]) > 0: #GROUP_?
                file.write(struct.pack("<i",444))#Group Chunk

            bl_children = common_sort(cur_center, bl_children)

            if(len(bl_children) > 0):
                for i, ch in enumerate(bl_children[:-1]):

                    export_block(ch, False, cur_level+1, cur_max_cnt, cur_groups, extra, file)

                export_block(bl_children[-1], True, cur_level+1, cur_max_cnt, cur_groups, extra, file)

        else:

            file.write(struct.pack("<i",333))#Begin Chunk

            if obj_type not in [9, 10, 21]:
                bl_children = common_sort(cur_center, bl_children)

            if obj_type == 30:
                write_name('', file)
            else:
                write_name(obj_name, file)

            file.write(struct.pack("<i", obj_type))

            if obj_type == 0:
                file.write(bytearray(b'\x00'*44))

            elif obj_type == 1:

                write_name(block[Blk001.Name1.get_prop()], file)
                write_name(block[Blk001.Name2.get_prop()], file)

            elif obj_type == 2:

                write_calculated_sphere(file, block)
                file.write(struct.pack("<3f", *block[Blk002.Unk_XYZ.get_prop()]))
                file.write(struct.pack("<f", block[Blk002.Unk_R.get_prop()]))

                file.write(struct.pack("<i", len(block.children)))

                to_process_child = True

            elif obj_type == 3:

                write_calculated_sphere(file, block)

                file.write(struct.pack("<i", len(block.children)))

                to_process_child = True

            elif obj_type == 4:

                write_calculated_sphere(file, block)
                write_name(block[Blk004.Name1.get_prop()], file)
                write_name(block[Blk004.Name2.get_prop()], file)

                file.write(struct.pack("<i", len(block.children)))

                to_process_child = True

            elif obj_type == 5:

                write_calculated_sphere(file, block)
                write_name(block[Blk005.Name1.get_prop()], file)

                file.write(struct.pack("<i", len(block.children)))

                to_process_child = True

            elif obj_type == 6:

                write_calculated_sphere(file, block)
                write_name(block[Blk006.Name1.get_prop()], file)
                write_name(block[Blk006.Name2.get_prop()], file)

                offset = 0
                all_children = [cn for cn in get_all_children(block) if cn.get(BLOCK_TYPE) and cn.get(BLOCK_TYPE) in [35, 8, 28]]
                all_children.sort(key = lambda block:block.name)
                for ch in all_children:
                    obj = bpy.data.objects[ch.name]
                    some_props = get_mesh_props(obj)
                    pass_to_mesh[obj.name] = {
                        "offset": offset,
                        "props": some_props
                    }
                    offset += len(some_props[0])

                file.write(struct.pack("<i", offset)) #Vertex count

                for key in sorted(pass_to_mesh.keys()):
                    verts, uvs, normals, faces, local_verts = pass_to_mesh[key]['props']
                    for i, v in enumerate(verts):
                        file.write(struct.pack("<3f", *v))
                        file.write(struct.pack("<f", uvs[i][0]))
                        file.write(struct.pack("<f", 1 - uvs[i][1]))

                file.write(struct.pack("<i", len(block.children)))

                to_process_child = True

            elif obj_type == 7:

                write_calculated_sphere(file, block)
                write_name(block[Blk007.Name1.get_prop()], file)

                offset = 0
                all_children = [cn for cn in get_all_children(block) if cn.get(BLOCK_TYPE) and cn.get(BLOCK_TYPE) in [35, 8, 28]]
                all_children.sort(key = lambda block:block.name)
                for ch in all_children:
                    # obj = bpy.data.objects[ch.name]
                    some_props = get_mesh_props(ch)
                    pass_to_mesh[ch.name] = {
                        "offset": offset,
                        "props": some_props
                    }
                    offset += len(some_props[0])

                file.write(struct.pack("<i", offset)) #Vertex count

                for key in sorted(pass_to_mesh.keys()):
                    verts, uvs, normals, faces, local_verts = pass_to_mesh[key]['props']
                    for i, v in enumerate(verts):
                        file.write(struct.pack("<3f", *v))
                        file.write(struct.pack("<f", uvs[i][0]))
                        file.write(struct.pack("<f", 1 - uvs[i][1]))

                file.write(struct.pack("<i", len(block.children)))

                to_process_child = True

            elif obj_type == 8:

                l_pass_to_mesh = extra['pass_to_mesh'][block.name]

                l_offset = l_pass_to_mesh['offset']
                verts, uvs, normals, polygons, local_verts = l_pass_to_mesh['props']

                write_mesh_sphere(file, block)
                # file.write(struct.pack("<i", 0)) # PolygonCount
                file.write(struct.pack("<i", len(polygons))) #Polygon count
                
                mesh = block.data
                
                if is_before_2_93():
                    format_flags_attrs = []
                    colors = mesh.vertex_colors.get(Pfb008.Format_Flags.get_prop()).data
                    for poly in polygons:
                        val = RGBPacker.unpack_4floats_to_int([0.0, *(colors[poly.loop_indices[0]].color)])
                        format_flags_attrs.append(val)
                else:
                    format_flags_attrs = obj.data.attributes.get(Pfb008.Format_Flags.get_prop())
                    format_flags_attrs = format_flags_attrs.data
                # format_flags_attrs = None #temporary
                # if format_flags_attrs is not None:


                for poly in polygons:
                    poly_format = 0
                    uv_count = 0
                    use_normals = False
                    normal_switch = False
                    l_material_ind = get_material_index_in_res(obj.data.materials[poly.material_index].name, current_res)
                    if format_flags_attrs is None:
                        format_raw = 2 # default
                    else:
                        if is_before_2_93():
                            format_raw = format_flags_attrs[poly.index]
                        else:
                            format_raw = format_flags_attrs[poly.index].value
                    # format_raw = 0 #temporary
                    file.write(struct.pack("<i", format_raw))
                    file.write(struct.pack("<f", 1.0)) # TODO: not consts
                    file.write(struct.pack("<i", 32767)) # TODO: not consts
                    file.write(struct.pack("<i", l_material_ind))
                    file.write(struct.pack("<i", len(poly.vertices)))

                    poly_format = format_raw ^ 1
                    uv_count = ((poly_format & 0xFF00) >> 8)

                    if poly_format & 0b10:
                        uv_count += 1

                    if poly_format & 0b100000 and poly_format & 0b10000:
                        use_normals = True
                        if poly_format & 0b1:
                            normal_switch = True
                        else:
                            normal_switch = False

                    l_uvs = {}
                    for li in poly.loop_indices:
                        vi = mesh.loops[li].vertex_index
                        l_uvs[vi] = mesh.uv_layers[0].data[li].uv

                    for i, vert in enumerate(poly.vertices):
                        file.write(struct.pack("<i", l_offset + vert))
                        for k in range(uv_count):
                            file.write(struct.pack("<f", l_uvs[vert][0]))
                            file.write(struct.pack("<f", 1 - l_uvs[vert][1]))
                        if use_normals:
                            if normal_switch:
                                file.write(struct.pack("<3f", *normals[vert]))
                            else:
                                file.write(struct.pack("<f", 1.0))

            elif obj_type == 9 or obj_type == 22:

                write_calculated_sphere(file, block)
                file.write(struct.pack("<3f", *block[Blk009.Unk_XYZ.get_prop()]))
                file.write(struct.pack("<f", block[Blk009.Unk_R.get_prop()]))

                child_cnt = 0
                for ch in block.children:
                    child_cnt += len(ch.children)

                file.write(struct.pack("<i", child_cnt))

                to_process_child = True
                cur_max_cnt = 2
                # max_groups = 2

            elif obj_type == 10:

                write_calculated_sphere(file, block)
                file.write(struct.pack("<3f", *block[Blk010.LOD_XYZ.get_prop()]))
                file.write(struct.pack("<f", block[Blk010.LOD_R.get_prop()]))

                child_cnt = 0
                for ch in block.children:
                    child_cnt += len(ch.children)

                file.write(struct.pack("<i", child_cnt))

                to_process_child = True
                cur_max_cnt = 2

            elif obj_type == 11:

                write_calculated_sphere(file, block)
                file.write(struct.pack("<3f", *block[Blk011.Unk_XYZ1.get_prop()]))
                file.write(struct.pack("<3f", *block[Blk011.Unk_XYZ2.get_prop()]))
                file.write(struct.pack("<f", block[Blk011.Unk_R1.get_prop()]))
                file.write(struct.pack("<f", block[Blk011.Unk_R2.get_prop()]))

                file.write(struct.pack("<i", len(block.children)))

                to_process_child = True

            elif obj_type == 12:

                write_bound_sphere(file, (0.0,0.0,0.0), 0.0)
                file.write(struct.pack("<3f", *block[Blk012.Unk_XYZ1.get_prop()]))
                file.write(struct.pack("<f", block[Blk012.Unk_R.get_prop()]))
                file.write(struct.pack("<i", block[Blk012.Unk_Int1.get_prop()]))
                file.write(struct.pack("<i", block[Blk012.Unk_Int2.get_prop()]))
                item_list = block[Blk012.Unk_List.get_prop()]
                # file.write(struct.pack("<i", 0)) #Params Count
                file.write(struct.pack("<i", len(item_list)))

                for item in item_list:
                    file.write(struct.pack("<f", item))

            elif obj_type == 13:

                write_bound_sphere(file, (0.0,0.0,0.0), 0.0)
                file.write(struct.pack("<i", block[Blk013.Unk_Int1.get_prop()]))
                file.write(struct.pack("<i", block[Blk013.Unk_Int2.get_prop()]))
                item_list = block[Blk013.Unk_List.get_prop()]
                # file.write(struct.pack("<i", 0)) #Params Count
                file.write(struct.pack("<i", len(item_list)))

                for item in item_list:
                    file.write(struct.pack("<f", item))

            elif obj_type == 14:

                write_bound_sphere(file, (0.0,0.0,0.0), 0.0)
                file.write(struct.pack("<3f", *block[Blk014.Unk_XYZ.get_prop()]))
                file.write(struct.pack("<f", block[Blk014.Unk_R.get_prop()]))
                file.write(struct.pack("<i", block[Blk014.Unk_Int1.get_prop()]))
                file.write(struct.pack("<i", block[Blk014.Unk_Int2.get_prop()]))
                item_list = block[Blk014.Unk_List.get_prop()]
                # file.write(struct.pack("<i", 0)) #Params Count
                file.write(struct.pack("<i", len(item_list)))

                for item in item_list:
                    file.write(struct.pack("<f", item))

            elif obj_type == 15:

                write_bound_sphere(file, (0.0,0.0,0.0), 0.0)
                file.write(struct.pack("<i", block[Blk015.Unk_Int1.get_prop()]))
                file.write(struct.pack("<i", block[Blk015.Unk_Int2.get_prop()]))
                item_list = block[Blk015.Unk_List.get_prop()]
                # file.write(struct.pack("<i", 0)) #Params Count
                file.write(struct.pack("<i", len(item_list)))

                for item in item_list:
                    file.write(struct.pack("<f", item))

            elif obj_type == 16:

                write_bound_sphere(file, (0.0,0.0,0.0), 0.0)
                file.write(struct.pack("<3f", *block[Blk016.Unk_XYZ1.get_prop()]))
                file.write(struct.pack("<3f", *block[Blk016.Unk_XYZ2.get_prop()]))
                file.write(struct.pack("<f", block[Blk016.Unk_Float1.get_prop()]))
                file.write(struct.pack("<f", block[Blk016.Unk_Float2.get_prop()]))
                file.write(struct.pack("<i", block[Blk016.Unk_Int1.get_prop()]))
                file.write(struct.pack("<i", block[Blk016.Unk_Int2.get_prop()]))
                item_list = block[Blk016.Unk_List.get_prop()]
                # file.write(struct.pack("<i", 0)) #Params Count
                file.write(struct.pack("<i", len(item_list)))

                for item in item_list:
                    file.write(struct.pack("<f", item))

            elif obj_type == 17:

                write_bound_sphere(file, (0.0,0.0,0.0), 0.0)
                file.write(struct.pack("<3f", *block[Blk017.Unk_XYZ1.get_prop()]))
                file.write(struct.pack("<3f", *block[Blk017.Unk_XYZ2.get_prop()]))
                file.write(struct.pack("<f", block[Blk017.Unk_Float1.get_prop()]))
                file.write(struct.pack("<f", block[Blk017.Unk_Float2.get_prop()]))
                file.write(struct.pack("<i", block[Blk017.Unk_Int1.get_prop()]))
                file.write(struct.pack("<i", block[Blk017.Unk_Int2.get_prop()]))
                item_list = block[Blk017.Unk_List.get_prop()]
                # file.write(struct.pack("<i", 0)) #Params Count
                file.write(struct.pack("<i", len(item_list)))

                for item in item_list:
                    file.write(struct.pack("<f", item))

            elif obj_type == 18:

                write_calculated_sphere(file, block)
                write_name(block[Blk018.Space_Name.get_prop()], file)
                write_name(block[Blk018.Add_Name.get_prop()], file)

            elif obj_type == 19:

                current_room_name = '{}:{}'.format(current_res, obj_name)
                border_blocks = borders[current_room_name]
                bl_children.extend(border_blocks)

                file.write(struct.pack("<i", len(bl_children)))

                to_process_child = True

            elif obj_type == 20:

                write_bound_sphere(file, (0.0,0.0,0.0), 0.0)
                point_list = []
                for sp in block.data.splines:
                    for point in sp.points:
                        point_list.append(point.co)
                # file.write(struct.pack("<i", 0)) #Verts Count
                file.write(struct.pack("<i", len(point_list))) #Verts Count
                file.write(struct.pack("<i", block[Blk020.Unk_Int1.get_prop()]))
                file.write(struct.pack("<i", block[Blk020.Unk_Int2.get_prop()]))

                # Unknowns list
                item_list = block[Blk020.Unk_List.get_prop()]
                file.write(struct.pack("<i", len(item_list)))
                for item in item_list:
                    file.write(struct.pack("<f", item))

                # Points list
                for point in point_list:
                    file.write(struct.pack("<3f", *(matrix_multiply(block.matrix_world, Vector(point[:3])))))
                    # file.write(struct.pack("<f", point.x))
                    # file.write(struct.pack("<f", point.y))
                    # file.write(struct.pack("<f", point.z))

            elif obj_type == 21:

                write_calculated_sphere(file, block)
                file.write(struct.pack("<i", block[Blk021.GroupCnt.get_prop()]))
                file.write(struct.pack("<i", block[Blk021.Unk_Int2.get_prop()]))

                child_cnt = 0
                for ch in block.children:
                    child_cnt += len(ch.children)

                file.write(struct.pack("<i", child_cnt))

                to_process_child = True
                cur_max_cnt = block[Blk021.GroupCnt.get_prop()]

            elif obj_type == 23:

                file.write(struct.pack("<i", block[Blk023.Unk_Int1.get_prop()]))
                file.write(struct.pack("<i", block[Blk023.Surface.get_prop()]))
                # file.write(struct.pack("<i", 0)) #Params Count

                # Unknowns list
                item_list = block[Blk023.Unk_List.get_prop()]
                file.write(struct.pack("<i", len(item_list)))
                for item in item_list:
                    file.write(struct.pack("<i", item))

                # Points list
                mesh = block.data
                file.write(struct.pack("<i", len(mesh.polygons)))
                for poly in mesh.polygons:
                    file.write(struct.pack("<i", len(poly.vertices)))
                    l_vertexes = poly.vertices
                    for vert in poly.vertices:
                        file.write(struct.pack("<3f", *(matrix_multiply(block.matrix_world, Vector(mesh.vertices[vert].co)))))

                # file.write(struct.pack("<i", 0)) #Verts Count

            elif obj_type == 24:
                pi = 3.14159265358979

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

                file.write(struct.pack("<i", block[Blk024.Flag.get_prop()]))

                file.write(struct.pack("<i", len(block.children)))

                to_process_child = True

            elif obj_type == 25:

                file.write(struct.pack("<3i", *block[Blk025.Unk_XYZ.get_prop()]))
                write_name(block[Blk025.Name.get_prop()], file)
                file.write(struct.pack("<3f", *block[Blk025.Unk_XYZ1.get_prop()]))
                file.write(struct.pack("<3f", *block[Blk025.Unk_XYZ2.get_prop()]))
                file.write(struct.pack("<f", block[Blk025.Unk_Float1.get_prop()]))
                file.write(struct.pack("<f", block[Blk025.Unk_Float2.get_prop()]))
                file.write(struct.pack("<f", block[Blk025.Unk_Float3.get_prop()]))
                file.write(struct.pack("<f", block[Blk025.Unk_Float4.get_prop()]))
                file.write(struct.pack("<f", block[Blk025.Unk_Float5.get_prop()]))

            elif obj_type == 26:

                write_calculated_sphere(file, block)
                file.write(struct.pack("<3f", *block[Blk026.Unk_XYZ1.get_prop()]))
                file.write(struct.pack("<3f", *block[Blk026.Unk_XYZ2.get_prop()]))
                file.write(struct.pack("<3f", *block[Blk026.Unk_XYZ3.get_prop()]))

                file.write(struct.pack("<i", len(block.children)))

                to_process_child = True

            elif obj_type == 27:

                write_bound_sphere(file, (0.0,0.0,0.0), 0.0)
                file.write(struct.pack("<i", block[Blk027.Flag.get_prop()]))
                file.write(struct.pack("<3f", *block[Blk027.Unk_XYZ.get_prop()]))
                file.write(struct.pack("<i", block[Blk027.Material.get_prop()]))

            elif obj_type == 28: #must be 4 coord plane

                # sprite_center = block[Blk028.Sprite_Center.get_prop()]
                sprite_center = 0.125 * sum((Vector(b) for b in block.bound_box), Vector())
                sprite_center = matrix_multiply(block.matrix_world, sprite_center)

                write_mesh_sphere(file, block)
                file.write(struct.pack("<3f", *block.location)) #sprite center

                mesh = block.data

                if is_before_2_93():
                    format_flags_attrs = []
                    colors = mesh.vertex_colors.get(Pfb008.Format_Flags.get_prop()).data
                    for poly in polygons:
                        val = RGBPacker.unpack_4floats_to_int([0.0, *(colors[poly.loop_indices[0]].color)])
                        format_flags_attrs.append(val)
                else:
                    format_flags_attrs = obj.data.attributes.get(Pfb008.Format_Flags.get_prop())
                    format_flags_attrs = format_flags_attrs.data
                # format_flags_attrs = None #temporary
                some_props = get_mesh_props(obj)

                l_verts = some_props[4]
                # l_uvs = some_props[1]
                l_normals = some_props[2]
                l_polygons = some_props[3]
                l_material = obj.data.materials[obj.data.polygons[0].material_index].name

                file.write(struct.pack("<i", len(l_polygons)))

                for poly in l_polygons:

                    l_uvs = {}
                    for li in poly.loop_indices:
                        vi = mesh.loops[li].vertex_index
                        l_uvs[vi] = mesh.uv_layers[0].data[li].uv

                    verts = poly.vertices

                    if format_flags_attrs is None:
                        format_raw = 2 # default
                    else:
                        if is_before_2_93():
                            format_raw = format_flags_attrs[poly.index]
                        else:
                            format_raw = format_flags_attrs[poly.index].value

                    file.write(struct.pack("<i", format_raw)) # format with UVs TODO: not consts
                    file.write(struct.pack("<f", 1.0)) # TODO: not consts
                    file.write(struct.pack("<i", 32767)) # TODO: not consts
                    file.write(struct.pack("<i", get_material_index_in_res(l_material, current_res)))
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

            elif obj_type == 29:

                write_calculated_sphere(file, block)
                file.write(struct.pack("<i", block[Blk029.Unk_Int1.get_prop()]))
                file.write(struct.pack("<i", block[Blk029.Unk_Int2.get_prop()]))
                file.write(struct.pack("<3f", *block[Blk029.Unk_XYZ.get_prop()]))
                file.write(struct.pack("<f", block[Blk029.Unk_R.get_prop()]))

                file.write(struct.pack("<i", len(block.children)))

                to_process_child = True

            elif obj_type == 30:

                write_mesh_sphere(file, block)

                module1_name = block[Blk030.ResModule1.get_prop()]
                module2_name = block[Blk030.ResModule2.get_prop()]
                room1_name = block[Blk030.RoomName1.get_prop()]
                room2_name = block[Blk030.RoomName2.get_prop()]

                roomname1 = '{}:{}'.format(module1_name, room1_name)
                roomname2 = '{}:{}'.format(module2_name, room2_name)
                to_import_second_side = False
                if current_room_name == roomname1:
                    to_import_second_side = True
                elif current_room_name == roomname2:
                    to_import_second_side = False

                if to_import_second_side:
                    write_name(get_room_name(current_res, roomname2), file)
                else:
                    write_name(get_room_name(current_res, roomname1), file)

                vertexes = [matrix_multiply(block.matrix_world, cn.co) for cn in block.data.vertices]

                if to_import_second_side:
                    p1 = vertexes[0]
                    p2 = vertexes[2]
                else:
                    p1 = vertexes[1]
                    p2 = vertexes[3]

                file.write(struct.pack("<3f", *p1))
                file.write(struct.pack("<3f", *p2))

            elif obj_type == 31:

                write_bound_sphere(file, (0.0,0.0,0.0), 0.0)
                file.write(struct.pack("<i", block[Blk031.Unk_Int1.get_prop()]))
                file.write(struct.pack("<3f", *block[Blk031.Unk_XYZ1.get_prop()]))
                file.write(struct.pack("<f", block[Blk031.Unk_R.get_prop()]))
                file.write(struct.pack("<i", block[Blk031.Unk_Int2.get_prop()]))
                file.write(struct.pack("<3f", *block[Blk031.Unk_XYZ2.get_prop()]))

            elif obj_type == 33:

                write_calculated_sphere(file, block)
                file.write(struct.pack("<i", block[Blk033.Use_Lights.get_prop()]))
                file.write(struct.pack("<i", block[Blk033.Light_Type.get_prop()]))
                file.write(struct.pack("<i", block[Blk033.Flag.get_prop()]))
                file.write(struct.pack("<3f", *block[Blk033.Unk_XYZ1.get_prop()]))
                file.write(struct.pack("<3f", *block[Blk033.Unk_XYZ2.get_prop()]))
                file.write(struct.pack("<f", block[Blk033.Unk_Float1.get_prop()]))
                file.write(struct.pack("<f", block[Blk033.Unk_Float2.get_prop()]))
                file.write(struct.pack("<f", block[Blk033.Light_R.get_prop()]))
                file.write(struct.pack("<f", block[Blk033.Intens.get_prop()]))
                file.write(struct.pack("<f", block[Blk033.Unk_Float3.get_prop()]))
                file.write(struct.pack("<f", block[Blk033.Unk_Float4.get_prop()]))
                file.write(struct.pack("<3f", *block[Blk033.RGB.get_prop()]))

                file.write(struct.pack("<i", len(block.children)))

                to_process_child = True

            elif obj_type == 34:

                write_bound_sphere(file, (0.0,0.0,0.0), 0.0)
                file.write(struct.pack("<i", 0)) #skipped Int
                point_list = []
                for sp in block.data.splines:
                    for point in sp.points:
                        point_list.append(point.co)
                file.write(struct.pack("<i", len(point_list))) #Verts count
                for point in point_list:
                    file.write(struct.pack("<f", point.x))
                    file.write(struct.pack("<f", point.y))
                    file.write(struct.pack("<f", point.z))
                    file.write(struct.pack("<i", block[Blk034.UnkInt.get_prop()]))

            elif obj_type == 35: #TODO: Texture coordinates are absent for moving texture(1)(mat_refl_road)(null))
                                #probably UVMapVert1 on road objects = tp import them too

                l_pass_to_mesh = extra['pass_to_mesh'][block.name]
                
                l_offset = l_pass_to_mesh['offset']
                verts, uvs, normals, polygons, local_verts = l_pass_to_mesh['props']

                write_mesh_sphere(file, block)
                file.write(struct.pack("<i", block[Blk035.MType.get_prop()]))
                # file.write(struct.pack("<i", 3))
                file.write(struct.pack("<i", block[Blk035.TexNum.get_prop()]))
                # file.write(struct.pack("<i", 0)) #Polygon count
                file.write(struct.pack("<i", len(polygons))) #Polygon count

                mesh = block.data

                if is_before_2_93():
                    format_flags_attrs = []
                    colors = mesh.vertex_colors.get(Pfb008.Format_Flags.get_prop()).data
                    for poly in polygons:
                        val = RGBPacker.unpack_4floats_to_int([0.0, *(colors[poly.loop_indices[0]].color)])
                        format_flags_attrs.append(val)
                else:
                    format_flags_attrs = obj.data.attributes.get(Pfb008.Format_Flags.get_prop())
                    format_flags_attrs = format_flags_attrs.data
                # format_flags_attrs = None #temporary

                for poly in polygons:
                    poly_format = 0
                    uv_count = 0
                    use_normals = False
                    normal_switch = False
                    l_material_ind = get_material_index_in_res(obj.data.materials[poly.material_index].name, current_res)
                    if format_flags_attrs is None:
                        format_raw = 2 # default
                    else:
                        if is_before_2_93():
                            format_raw = format_flags_attrs[poly.index]
                        else:
                            format_raw = format_flags_attrs[poly.index].value
                    # format_raw = 0
                    file.write(struct.pack("<i", format_raw))
                    file.write(struct.pack("<f", 1.0)) # TODO: not consts
                    file.write(struct.pack("<i", 32767)) # TODO: not consts
                    file.write(struct.pack("<i", l_material_ind))
                    file.write(struct.pack("<i", len(poly.vertices))) #Verts count

                    poly_format = format_raw ^ 1
                    uv_count = ((poly_format & 0xFF00) >> 8)

                    if poly_format & 0b10:
                        uv_count += 1

                    if poly_format & 0b100000 and poly_format & 0b10000:
                        use_normals = True
                        if poly_format & 0b1:
                            normal_switch = True
                        else:
                            normal_switch = False

                    l_uvs = {}
                    for li in poly.loop_indices:
                        vi = mesh.loops[li].vertex_index
                        l_uvs[vi] = mesh.uv_layers[0].data[li].uv

                    for i, vert in enumerate(poly.vertices):
                        file.write(struct.pack("<i", l_offset + vert))
                        for k in range(uv_count):
                            file.write(struct.pack("<f", l_uvs[vert][0]))
                            file.write(struct.pack("<f", 1 - l_uvs[vert][1]))
                        if use_normals:
                            if normal_switch:
                                file.write(struct.pack("<3f", *normals[vert]))
                            else:
                                file.write(struct.pack("<f", 1.0))

            elif obj_type == 36:

                # isSecondUvs = False
                format_raw = block[Blk036.VType.get_prop()]
                normal_switch = False
                write_calculated_sphere(file, block)
                write_name(block[Blk036.Name1.get_prop()], file)
                write_name(block[Blk036.Name2.get_prop()], file)

                offset = 0
                all_children = [cn for cn in get_all_children(block) if cn.get(BLOCK_TYPE) and cn.get(BLOCK_TYPE) in [35, 8, 28]]
                all_children.sort(key = lambda block:block.name)
                for ch in all_children:
                    # obj = bpy.data.objects[ch.name]
                    some_props = get_mesh_props(ch)
                    pass_to_mesh[ch.name] = {
                        "offset": offset,
                        "props": some_props
                    }

                    # if get_uv_layers(obj.data).get('UVmapVert1'):
                    #     isSecondUvs = True


                    offset += len(some_props[0])

                #temporary
                # if isSecondUvs:
                #     format_raw = 258
                # else:
                #     format_raw = 2

                extra_uv_count = format_raw >> 8
                vert_format = format_raw & 0xFF

                if vert_format == 1 or vert_format == 2:
                    normal_switch = True
                elif vert_format == 3:
                    normal_switch = False


                file.write(struct.pack("<i", format_raw))
                file.write(struct.pack("<i", offset)) #Vertex count

                for key in sorted(pass_to_mesh.keys()):
                    verts, uvs, normals, faces, local_verts = pass_to_mesh[key]['props']
                    for i, v in enumerate(verts):
                        file.write(struct.pack("<3f", *v))
                        file.write(struct.pack("<f", uvs[i][0]))
                        file.write(struct.pack("<f", 1 - uvs[i][1]))

                        for k in range(extra_uv_count):
                            file.write(struct.pack("<f", uvs[i][0]))
                            file.write(struct.pack("<f", 1 - uvs[i][1]))

                        if normal_switch:
                            file.write(struct.pack("<3f", *normals[i]))
                        else:
                            file.write(struct.pack("<f", 1.0))

                file.write(struct.pack("<i", len(block.children)))

                to_process_child = True

            elif obj_type == 37:

                # isSecondUvs = False
                format_raw = block[Blk037.VType.get_prop()]
                normal_switch = False
                write_calculated_sphere(file, block)
                write_name(block[Blk037.Name1.get_prop()], file)
                # file.write(struct.pack("<i", block[Blk037.VType.get_prop()]))


                offset = 0
                all_children = [cn for cn in get_all_children(block) if cn.get(BLOCK_TYPE) and cn.get(BLOCK_TYPE) in [35, 8, 28]]
                all_children.sort(key = lambda block:block.name)
                for ch in all_children:
                    # obj = bpy.data.objects[ch.name]
                    some_props = get_mesh_props(ch)
                    pass_to_mesh[ch.name] = {
                        "offset": offset,
                        "props": some_props
                    }
                    # if get_uv_layers(obj.data).get('UVmapVert1'):
                    #     isSecondUvs = True

                    offset += len(some_props[0])

                # if isSecondUvs:
                #     format_raw = 258
                # else:
                #     format_raw = 2

                extra_uv_count = format_raw >> 8
                vert_format = format_raw & 0xFF

                if vert_format == 1 or vert_format == 2:
                    normal_switch = True
                elif vert_format == 3:
                    normal_switch = False

                file.write(struct.pack("<i", format_raw))

                file.write(struct.pack("<i", offset)) #Vertex count


                for key in sorted(pass_to_mesh.keys()):
                    verts, uvs, normals, faces, local_verts = pass_to_mesh[key]['props']
                    for i, v in enumerate(verts):
                        file.write(struct.pack("<3f", *v))
                        file.write(struct.pack("<f", uvs[i][0]))
                        file.write(struct.pack("<f", 1 - uvs[i][1]))

                        for k in range(extra_uv_count):
                            file.write(struct.pack("<f", uvs[i][0]))
                            file.write(struct.pack("<f", 1 - uvs[i][1]))

                        if normal_switch:
                            file.write(struct.pack("<3f", *normals[i]))
                        else:
                            file.write(struct.pack("<f", 1.0))

                file.write(struct.pack("<i", len(block.children)))

                to_process_child = True

            elif obj_type == 39:

                write_calculated_sphere(file, block)
                file.write(struct.pack("<i", block[Blk039.Color_R.get_prop()]))
                file.write(struct.pack("<f", block[Blk039.Unk_Float1.get_prop()]))
                file.write(struct.pack("<f", block[Blk039.Fog_Start.get_prop()]))
                file.write(struct.pack("<f", block[Blk039.Fog_End.get_prop()]))
                file.write(struct.pack("<i", block[Blk039.Color_Id.get_prop()]))
                file.write(struct.pack("<i", 0)) #Unknown count

                file.write(struct.pack("<i", len(block.children)))

                to_process_child = True

            elif obj_type == 40:

                write_bound_sphere(file, block.location, get_empty_size(block))
                write_name(block[Blk040.Name1.get_prop()], file)
                write_name(block[Blk040.Name2.get_prop()], file)
                file.write(struct.pack("<i", block[Blk040.Unk_Int1.get_prop()]))
                file.write(struct.pack("<i", block[Blk040.Unk_Int2.get_prop()]))
                item_list = block[Blk040.Unk_List.get_prop()]
                file.write(struct.pack("<i", len(item_list)))
                for item in item_list:
                    file.write(struct.pack("<f", item))

            if to_process_child:
                l_extra = extra
                if(len(bl_children) > 0):
                    for i, ch in enumerate(bl_children[:-1]):

                        if len(pass_to_mesh) > 0:
                            l_extra['pass_to_mesh'] = pass_to_mesh
                        export_block(ch, False, cur_level+1, cur_max_cnt, cur_groups, l_extra, file)

                    if len(pass_to_mesh) > 0:
                        l_extra['pass_to_mesh'] = pass_to_mesh
                    export_block(bl_children[-1], True, cur_level+1, cur_max_cnt, cur_groups, l_extra, file)

            file.write(struct.pack("<i",555))#End Chunk

    return cur_level


blocksWithChildren = [2,3,4,5,6,7,9]


def get_mesh_props(obj):

    mesh = obj.data

    polygons = mesh.polygons

    mat = obj.matrix_world

    vertexes = [(matrix_multiply(mat, cn.co)) for cn in mesh.vertices]

    local_verts = [cn.co for cn in mesh.vertices]

    uvs = [None] * len(vertexes)
    for poly in polygons:
        for li in poly.loop_indices:
            vi = mesh.loops[li].vertex_index
            uvs[vi] = mesh.uv_layers[0].data[li].uv     #UVMap

    normals = [cn.normal for cn in mesh.vertices]

    return [vertexes, uvs, normals, polygons, local_verts]

