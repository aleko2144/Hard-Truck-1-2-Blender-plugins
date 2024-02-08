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
    srgb_to_rgb,
    write_size,
    read_res_sections,
    get_active_palette_module,
    get_mat_texture_ref_dict

)

from .imghelp import (
    convert_tga32_to_txr
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

    file.write(f'MATERIALS {str(len(bpy.data.materials))}\n')

    materials = []
    num_tex = 0

    for material in bpy.data.materials:
        materials.append(material.name)

    for i in range(len(materials)):
        num_tex = i
        file.write(f'{materials[i]} tex {str(num_tex + 1)}\n')

    file.write(f'TEXTUREFILES {str(len(bpy.data.materials))}\n')

    imgs = []
    for img in bpy.data.images:
        imgs.append(img.name)

    for material in bpy.data.materials:
        try:
            file.write(f"{textures_path}{material.texture_slots[0].texture.image.name[:-3]}txr\n")
        except:
            file.write(f"{textures_path}error.txr\n")

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

def cstring(txt, file):
    if txt[-1] != "\00":
        txt += "\00"
    file.write(txt.encode("cp1251"))


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
        meshes_in_empty[empty_name].sort(key= lambda x: f'{str(x["obj"])}{str(x["transf"])}')

        key = "||".join([f'{str(cn["obj"])}{str(cn["transf"])}' for cn in meshes_in_empty[empty_name]])
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

        border1 = f'{module1_name}:{room1_name}'
        border2 = f'{module2_name}:{room2_name}'

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


def save_image_as(image, path):

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


def write_palettefiles(res_module, file):

    size = 0
    if len(res_module.palette_colors) > 0:
        size = 1

    cstring(f"PALETTEFILES {size}", file)
    if size > 0:
        palette_name = res_module.palette_name
        if palette_name is None or len(palette_name) == 0:
            palette_name = f"{res_module.value}.plm"
        cstring(f"{palette_name}", file)
        pal_name_ms = file.tell()
        file.seek(4,1)
        file.write("PALT".encode("cp1251"))
        palt_ms = file.tell()
        file.seek(4,1)
        file.write("PLM\00".encode("cp1251"))
        plm_ms = file.tell()
        file.seek(4,1)
        for color in res_module.palette_colors:
            rgbcol = srgb_to_rgb(*color.value[:3])
            file.write(struct.pack("<B", rgbcol[0]))
            file.write(struct.pack("<B", rgbcol[1]))
            file.write(struct.pack("<B", rgbcol[2]))

        write_size(file, pal_name_ms)
        write_size(file, palt_ms)
        write_size(file, plm_ms)


def write_soundfiles(res_module, file):
    size = 0
    cstring("SOUNDFILES 0", file)


def write_backfiles(res_module, file):
    size = 0
    cstring("BACKFILES 0", file)


def write_maskfiles(res_module, file):
    size = 0
    cstring("MASKFILES 0", file)


def write_texturefiles(res_module, file, filepath, save_images = True):
    size = len(res_module.textures)

    cstring(f"TEXTUREFILES {size}", file)
    if size > 0:
        export_folder = os.path.dirname(filepath)
        basename = os.path.basename(filepath)[:-4]
        export_folder = os.path.join(export_folder, f'{basename}_export')
        export_folder_path = Path(export_folder)
        export_folder_path.mkdir(exist_ok=True, parents=True)

        mat_to_texture, texture_to_mat = get_mat_texture_ref_dict(res_module)
        palette_module = get_active_palette_module(res_module)
        palette = palette_module.palette_colors

        for i, texture in enumerate(res_module.textures):
            used_in_mat = res_module.materials[texture_to_mat[i]]
            transp_color = (0,0,0)
            if used_in_mat.tex_type == 'ttx' and used_in_mat.is_col:
                transp_color = srgb_to_rgb(*(palette[used_in_mat.col-1].value[:3]))

            basepath_no_ext = os.path.splitext(texture.tex_name)[0]

            image_name = f"{basepath_no_ext}.tga"
            txr_name = f"{basepath_no_ext}.txr"
            image_path = os.path.join(export_folder, image_name)
            texture_subpath = texture.subpath.rstrip("\\")
            texture_name = f'{texture_subpath}{chr(92)}{txr_name}'

            tex_params = []
            if texture.is_someint:
                tex_params.append(f"{texture.someint}")

            for param in ["noload", "bumpcoord", "memfix"]:
                if getattr(texture, f'is_{param}'):
                    tex_params.append(f"{param}")

            if len(tex_params) > 0:
                tex_str = f'{texture_name} {"  ".join(tex_params)}'
            else:
                tex_str = texture_name
            cstring(tex_str, file)

            if save_images:
                save_image_as(texture.id_tex, image_path)

            convert_tga32_to_txr(image_path, 2, texture.img_type, texture.img_format, texture.has_mipmap, transp_color)

            texture_size_ms = file.tell()
            file.write(struct.pack("<i", 0))
            outpath = os.path.splitext(image_path)[0] + ".txr"
            with open(outpath, "rb") as txr_file:
                txr_text = txr_file.read()
            file.write(txr_text)
            write_size(file, texture_size_ms)
            file.write(struct.pack('<i', 0))



def write_materials(res_module, file):
    size = len(res_module.materials)
    cstring(f"MATERIALS {size}", file)
    if size > 0:
        for material in res_module.materials:
            if material.id_mat is not None:
                mat_name = material.id_mat.name
                mat_str = mat_name
                mat_params = []
                if material.is_tex:
                    mat_params.append(f"{material.tex_type} {material.tex}")

                for param in ["col", "att", "msk", "power", "coord"]:
                    if getattr(material, f'is_{param}'):
                        int_param = getattr(material, param)
                        mat_params.append(f"{param} {int_param}")

                for param in ["reflect", "specular", "transp", "rot"]:
                    if getattr(material, f'is_{param}'):
                        float_param = float(getattr(material, param))
                        mat_params.append(f"{param} {float_param:.2f}")

                for param in ["noz", "nof", "notile", "notileu", "notilev", \
                                "alphamirr", "bumpcoord", "usecol", "wave"]:
                    if getattr(material, f'is_{param}'):
                        mat_params.append(f"{param}")

                for param in ["RotPoint", "move", "env"]:
                    if getattr(material, f'is_{param}'):
                        param1, param2 = getattr(material, param)
                        mat_params.append(f"{param} {param1:.2f} {param2:.2f}")

                if material.is_envId:
                    mat_params.append(f"env{material.envId}")

                mat_params_str = "  ".join(mat_params)

                mat_str = f"{mat_name} {mat_params_str}"
                cstring(mat_str, file)

def write_colors(res_module, file):
    size = 0
    cstring("COLORS 0", file)


def write_sounds(res_module, file):
    size = 0
    cstring("SOUNDS 0", file)



def export_res(context, op, export_dir):
    mytool = bpy.context.scene.my_tool

    exported_modules = [sn.name for sn in op.res_modules if sn.state is True]
    if not os.path.isdir(export_dir):
        export_dir = os.path.dirname(export_dir)

    for module_name in exported_modules:

        res_module = get_col_property_by_name(mytool.res_modules, module_name)
        if res_module is not None:

            filepath = os.path.join(export_dir, f"{res_module.value}.res")

            if op.to_merge:

                # allSections = ["PALETTEFILES", "SOUNDFILES", "SOUNDS", "BACKFILES", "MASKFILES", "COLORS", "TEXTUREFILES", "MATERIALS"]

                if not os.path.exists(filepath):
                    log.error(f"Not found file to merge into: {filepath}")
                    continue

                sections = read_res_sections(filepath)

                sections_to_merge = [cn.name for cn in op.res_sections if cn.state is True]

                with open(filepath, "wb") as file:
                    for section in sections:
                        log.debug(section['name'])
                        if section['name'] in sections_to_merge:
                            if section['name'] == 'TEXTUREFILES':
                                write_texturefiles(res_module, file, filepath, op.export_images)
                            elif section['name'] == 'PALETTEFILES':
                                write_palettefiles(res_module, file)
                            elif section['name'] == 'MASKFILES':
                                write_maskfiles(res_module, file)
                            elif section['name'] == 'MATERIALS':
                                write_materials(res_module, file)
                        else:
                            cstring(f'{section["name"]} {section["cnt"]}', file)
                            if section['name'] in ["COLORS", "MATERIALS", "SOUNDS"]:
                                for data in section['data']:
                                    cstring(data['row'], file)
                            else:
                                for data in section['data']:
                                    cstring(data['row'], file)
                                    file.write(struct.pack('<i', data['size']))
                                    file.write(data['bytes'])

            else:
                with open(filepath, 'wb') as file:

                    write_palettefiles(res_module, file)
                    write_soundfiles(res_module, file)
                    write_backfiles(res_module, file)
                    write_maskfiles(res_module, file)
                    write_colors(res_module, file)
                    write_texturefiles(res_module, file, filepath, op.export_images)
                    write_materials(res_module, file)



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

        obj = bpy.data.objects[f"{obj_name}.b3d"]
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

        log.debug(f"{block.get(BLOCK_TYPE)}_{cur_level}_{0}_{block.name}")

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
                for ch in all_children:
                    obj = bpy.data.objects[ch.name]
                    some_props = get_mesh_props(obj)
                    pass_to_mesh[obj.name] = {
                        "offset": offset,
                        "props": some_props
                    }
                    offset += len(some_props[0])

                file.write(struct.pack("<i", offset)) #Vertex count

                for mesh in pass_to_mesh.values():
                    verts, uvs, normals, faces, local_verts = mesh['props']
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
                for ch in all_children:
                    obj = bpy.data.objects[ch.name]
                    some_props = get_mesh_props(obj)
                    pass_to_mesh[obj.name] = {
                        "offset": offset,
                        "props": some_props
                    }
                    offset += len(some_props[0])

                file.write(struct.pack("<i", offset)) #Vertex count

                for mesh in pass_to_mesh.values():
                    verts, uvs, normals, faces, local_verts = mesh['props']
                    for i, v in enumerate(verts):
                        file.write(struct.pack("<3f", *v))
                        file.write(struct.pack("<f", uvs[i][0]))
                        file.write(struct.pack("<f", 1 - uvs[i][1]))

                file.write(struct.pack("<i", len(block.children)))

                to_process_child = True

            elif obj_type == 8:

                l_pass_to_mesh = extra['pass_to_mesh'][block.name]

                offset = l_pass_to_mesh['offset']
                verts, uvs, normals, polygons, local_verts = l_pass_to_mesh['props']

                write_mesh_sphere(file, block)
                # file.write(struct.pack("<i", 0)) # PolygonCount
                file.write(struct.pack("<i", len(polygons))) #Polygon count

                format_flags_attrs = obj.data.attributes.get(Pfb008.Format_Flags.get_prop())
                if format_flags_attrs is not None:
                    format_flags_attrs = format_flags_attrs.data

                mesh = block.data

                for poly in polygons:
                    poly_format = 0
                    uv_count = 0
                    use_normals = False
                    normal_switch = False
                    l_material_ind = get_material_index_in_res(obj.data.materials[poly.material_index].name, current_res)
                    if format_flags_attrs is None:
                        format_raw = 2 # default
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
                        l_uvs[vi] = mesh.uv_layers['UVMap'].data[li].uv

                    for i, vert in enumerate(poly.vertices):
                        file.write(struct.pack("<i", offset + vert))
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

                current_room_name = f'{current_res}:{obj_name}'
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
                    file.write(struct.pack("<3f", *(block.matrix_world @ Vector(point[:3]))))
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
                        file.write(struct.pack("<3f", *(block.matrix_world @ Vector(mesh.vertices[vert].co))))

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
                sprite_center = block.matrix_world @ sprite_center

                write_mesh_sphere(file, block)
                file.write(struct.pack("<3f", *block.location)) #sprite center


                format_flags_attrs = obj.data.attributes[Pfb028.Format_Flags.get_prop()].data
                some_props = get_mesh_props(obj)

                mesh = block.data

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
                        l_uvs[vi] = mesh.uv_layers['UVMap'].data[li].uv

                    verts = poly.vertices

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

                roomname1 = f'{module1_name}:{room1_name}'
                roomname2 = f'{module2_name}:{room2_name}'
                to_import_second_side = False
                if current_room_name == roomname1:
                    to_import_second_side = True
                elif current_room_name == roomname2:
                    to_import_second_side = False

                if to_import_second_side:
                    write_name(get_room_name(current_res, roomname2), file)
                else:
                    write_name(get_room_name(current_res, roomname1), file)

                vertexes = [block.matrix_world @ cn.co for cn in block.data.vertices]

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
                file.write(struct.pack("<3f", *block[Blk033.RGB]))

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

                offset = l_pass_to_mesh['offset']
                verts, uvs, normals, polygons, local_verts = l_pass_to_mesh['props']

                write_mesh_sphere(file, block)
                file.write(struct.pack("<i", block[Blk035.MType.get_prop()]))
                # file.write(struct.pack("<i", 3))
                file.write(struct.pack("<i", block[Blk035.TexNum.get_prop()]))
                # file.write(struct.pack("<i", 0)) #Polygon count
                file.write(struct.pack("<i", len(polygons))) #Polygon count

                format_flags_attrs = obj.data.attributes[Pfb035.Format_Flags.get_prop()].data

                mesh = block.data

                for poly in polygons:
                    poly_format = 0
                    uv_count = 0
                    use_normals = False
                    normal_switch = False
                    l_material_ind = get_material_index_in_res(obj.data.materials[poly.material_index].name, current_res)
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
                        l_uvs[vi] = mesh.uv_layers['UVMap'].data[li].uv

                    for i, vert in enumerate(poly.vertices):
                        file.write(struct.pack("<i", offset + vert))
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
                for ch in all_children:
                    obj = bpy.data.objects[ch.name]
                    some_props = get_mesh_props(obj)
                    pass_to_mesh[obj.name] = {
                        "offset": offset,
                        "props": some_props
                    }

                    # if obj.data.uv_layers.get('UVmapVert1'):
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

                for mesh in pass_to_mesh.values():
                    verts, uvs, normals, faces, local_verts = mesh['props']
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
                for ch in all_children:
                    obj = bpy.data.objects[ch.name]
                    some_props = get_mesh_props(obj)
                    pass_to_mesh[obj.name] = {
                        "offset": offset,
                        "props": some_props
                    }
                    # if obj.data.uv_layers.get('UVmapVert1'):
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


                for mesh in pass_to_mesh.values():
                    verts, uvs, normals, faces, local_verts = mesh['props']
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

                write_bound_sphere(file, block.location, block.empty_display_size)
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

    vertexes = [(mat @ cn.co) for cn in mesh.vertices]

    local_verts = [cn.co for cn in mesh.vertices]

    uvs = [None] * len(vertexes)
    for poly in polygons:
        for li in poly.loop_indices:
            vi = mesh.loops[li].vertex_index
            uvs[vi] = mesh.uv_layers['UVMap'].data[li].uv

    normals = [cn.normal for cn in mesh.vertices]

    return [vertexes, uvs, normals, polygons, local_verts]

