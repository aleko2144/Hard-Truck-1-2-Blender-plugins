import time
import datetime
import os
from pathlib import Path


import bpy

from .imghelp import (
    convert_txr_to_tga32,
    msk_to_tga32,
    parse_plm,
    get_txr_params
)

from .common import (
    get_col_property_by_name,
    get_col_property_index_by_name,
    get_active_palette_module,
    update_color_preview,
    get_color_img_name,
    unmask_bits,
    read_res_sections,
    srgb_to_rgb,
    get_mat_texture_ref_dict
)

from ..compatibility import (
    get_user_preferences,
    is_before_2_93
)

from ..common import (
    importres_logger
)

log = importres_logger

def import_common_dot_res(self, context, common_res_path):
    scene = context.scene
    mytool = scene.my_tool

    mytool.is_importing = True

    log.info('Importing file {}'.format(common_res_path))
    t = time.mktime(datetime.datetime.now().timetuple())
    with open(common_res_path, 'rb') as file:
        import_res(file, context, self, common_res_path)
    t = time.mktime(datetime.datetime.now().timetuple()) - t
    log.info('Finished importing in {t} seconds')

    mytool.is_importing = False

    
def import_multiple_res(self, files, context):

    scene = context.scene
    mytool = scene.my_tool
    user_prefs = get_user_preferences()
    common_res_path = user_prefs.addons['b3d_tools'].preferences.COMMON_RES_Path

    mytool.is_importing = True

    for resfile in self.files:
        filepath = os.path.join(self.directory, "{}.{}".format(os.path.splitext(resfile.name)[0], self.res_extension))

        if filepath != common_res_path: #COMMON.RES imported before

            log.info('Importing file {}'.format(filepath))
            t = time.mktime(datetime.datetime.now().timetuple())
            with open(filepath, 'rb') as file:
                import_res(file, context, self, filepath)
            t = time.mktime(datetime.datetime.now().timetuple()) - t
            log.info('Finished importing in {} seconds'.format(t))

    mytool.is_importing = False


def import_res(file, context, self, filepath):

    scene = context.scene
    mytool = scene.my_tool

    #Initialize palette index list
    row_indexes = bpy.context.scene.palette_row_indexes.prop_list
    col_indexes = bpy.context.scene.palette_col_indexes.prop_list

    if len(col_indexes) == 0:
        for i in range(8):
            col_indexes.add()
            col_indexes[i].value = i+1
        
    if len(row_indexes) == 0:
        for i in range(32):
            row_indexes.add()
            row_indexes[i].value = i*8


    res_modules = getattr(mytool, "res_modules")
    res_basename = os.path.basename(filepath)[:-4] #cut extension

    import_resources(filepath, res_modules, self.to_unpack_res, self.textures_format, self.to_convert_txr)

    res_module = get_col_property_by_name(res_modules, res_basename)
    create_materials(res_module)
    load_materials(res_module)


def import_resources(filepath, res_modules, to_unpack_res = True, image_format = 'tga', convert_txr = True):

    res_basepath = os.path.dirname(filepath)
    res_basename = os.path.basename(filepath)[:-4] #cut extension

    unpack_path = os.path.join(res_basepath, res_basename + r"_unpack")

    res_index = get_col_property_index_by_name(res_modules, res_basename)
    res_module = None

    if res_index >= 0:
        res_module = res_modules[res_index]
    if res_module:
        #delete RES module
        log.info("Removing res_module {}".format(res_index))
        res_modules.remove(res_index)

    res_module = res_modules.add()
    res_module.value = res_basename

    unpack_res(res_module, filepath, to_unpack_res)

    load_palette_files(unpack_path, res_module)

    load_texturefiles(unpack_path, res_module, image_format, convert_txr)

    load_maskfiles(unpack_path, res_module, image_format, convert_txr)


def create_materials(res_module):

    material_list = res_module.materials

    for material in material_list:
        create_material(res_module, material)

#https://blender.stackexchange.com/questions/118646/add-a-texture-to-an-object-using-python-and-blender-2-8
def create_material(res_module, mat):
    mytool = bpy.context.scene.my_tool

    texture_list = res_module.textures
    palette_module = get_active_palette_module(res_module)
    palette = palette_module.palette_colors

    new_mat = bpy.data.materials.get(mat.mat_name)
    if new_mat is None:
        new_mat = bpy.data.materials.new(name=mat.mat_name)
    new_mat.use_nodes = True
        
    bsdf = new_mat.node_tree.nodes.get("Principled BSDF")
    if bsdf is None:
        bsdf = new_mat.node_tree.nodes.new("ShaderNodeBsdfPrincipled")

    mat_output = new_mat.node_tree.nodes.get("Material Output")
    if mat_output is None:
        mat_output = new_mat.node_tree.nodes.new("ShaderNodeOutputMaterial")

    new_mat.node_tree.links.new(bsdf.outputs['BSDF'], mat_output.inputs['Surface'])        

    for link in bsdf.inputs['Base Color'].links:
        new_mat.node_tree.nodes.remove(link.from_node)

    # for link in bsdf.inputs['Alpha'].links:
    #     new_mat.node_tree.nodes.remove(link.from_node)

    if (mat.is_tex and int(mat.tex) > 0):
        path = texture_list[mat.tex-1].tex_name
        tex_image = new_mat.node_tree.nodes.new("ShaderNodeTexImage")
        tex_image.image = bpy.data.images.get(path)
        new_mat.node_tree.links.new(bsdf.inputs['Base Color'], tex_image.outputs['Color'])
        # new_mat.node_tree.links.new(bsdf.inputs['Alpha'], tex_image.outputs['Alpha'])

    elif mat.is_col and int(mat.col) > 0:
        tex_color = new_mat.node_tree.nodes.new("ShaderNodeRGB")
        tex_color.outputs['Color'].default_value = palette[mat.col-1].value
        new_mat.node_tree.links.new(bsdf.inputs['Base Color'], tex_color.outputs['Color'])


def load_materials(res_module):
    mytool = bpy.context.scene.my_tool
    for mat in res_module.materials:
        material = bpy.data.materials.get(mat.mat_name)
        if material is not None:
            mat.id_mat = material
            if mat.is_col:
                palette_module = get_active_palette_module(res_module)
                palette = palette_module.palette_colors
                if palette:
                    image = bpy.data.images.get(get_color_img_name(palette_module.value, mat.col))
                    if image is not None:
                        mat.id_col = image

            if mat.is_tex:
                image = res_module.textures[mat.tex-1]
                if image and image.id_tex:
                    mat.id_tex = image.id_tex

            if mat.is_msk:
                image = res_module.maskfiles[mat.msk-1]
                if image and image.id_msk:
                    mat.id_msk = image.id_msk

            if mat.is_att:
                image = res_module.materials[mat.att-1]
                if image and image.id_mat:
                    mat.id_att = image.id_mat



def load_texturefiles(basedir, res_module, image_format, convert_txr):
    mat_to_texture, texture_to_mat = get_mat_texture_ref_dict(res_module)
    palette_module = get_active_palette_module(res_module)
    palette = palette_module.palette_colors

    for i, texture in enumerate(res_module.textures):
        used_in_mat = res_module.materials[texture_to_mat[i]]
        transp_color = (0,0,0)
        if used_in_mat.tex_type == 'ttx' and used_in_mat.is_col:
            transp_color = srgb_to_rgb(*(palette[used_in_mat.col-1].value[:3]))

        no_ext_path = os.path.splitext(os.path.join(basedir, "TEXTUREFILES", texture.subpath, texture.tex_name))[0]
        result = None
        img_path = "{}.txr".format(no_ext_path)
        if convert_txr:
            result = convert_txr_to_tga32(img_path, transp_color)
        else:
            result = get_txr_params(img_path)
        filename_no_ext = os.path.basename(no_ext_path)
        img_name = "{}.{}".format(filename_no_ext, image_format)
        log.debug('Importing image {}'.format(img_name))

        img_path = "{}.{}".format(no_ext_path, image_format)
        texture.tex_name = img_name
        img = bpy.data.images.get(img_name)
        if img is None:
            # bpy.data.images.remove(img)
            img = bpy.data.images.load(img_path)
        texture.id_tex = img

        img_format = result['format']
        if img_format is not None:
            r = unmask_bits(img_format[0]).ones
            g = unmask_bits(img_format[1]).ones
            b = unmask_bits(img_format[2]).ones
            a = unmask_bits(img_format[3]).ones

            format_str = str(a) + str(r) + str(g) + str(b)
            if format_str not in ['4444', '0565']:
                format_str = '4444'
            texture.img_format = format_str

        texture.has_mipmap = result['has_mipmap']


def load_maskfiles(basedir, res_module, image_format, convert_txr):
    for maskfile in res_module.maskfiles:
        no_ext_path = os.path.splitext(os.path.join(basedir, "MASKFILES", maskfile.subpath, maskfile.msk_name))[0]
        if convert_txr:
            msk_to_tga32("{}.msk".format(no_ext_path))
        filename_no_ext = os.path.basename(no_ext_path)
        img_name = "{}.{}".format(filename_no_ext, image_format)
        img_path = "{}.{}".format(no_ext_path, image_format)
        maskfile.msk_name = img_name
        img = bpy.data.images.get(img_name)
        if img is None:
            # bpy.data.images.remove(img)
            img = bpy.data.images.load(img_path)
        maskfile.id_msk = img



def load_palette_files(basedir, res_module):
    if len(res_module.palette_name) > 0:
        palette_path = os.path.join(basedir, "PALETTEFILES", res_module.palette_subpath, res_module.palette_name)
        parse_plm(res_module, palette_path)
        for i, pal_color in enumerate(res_module.palette_colors):
            update_color_preview(res_module, i)


def get_res_folder(filepath):
    basename = os.path.basename(filepath)
    basepath = os.path.dirname(filepath)
    return os.path.join(basepath, "{}_unpack".format(basename[:-4]))


def save_material(res_module, material_str):
    name_split = material_str.split(" ")
    name = name_split[0]
    params = name_split[1:]

    material = res_module.materials.add()
    material.mat_name = name
    i = 0
    while i < len(params):
        param_name = params[i].replace('"', '')
        if len(param_name) > 0:
            if param_name in ["tex", "ttx", "itx"]:
                setattr(material, "is_tex", True)
                setattr(material, "tex", int(params[i+1]))
                setattr(material, "tex_type", param_name)
                i+=1
            elif param_name in ["col", "att", "msk", "power", "coord"]:
                setattr(material, "is_" + param_name, True)
                setattr(material, param_name, int(params[i+1]))
                i+=1
            elif param_name in ["reflect", "specular", "transp", "rot"]:
                setattr(material, param_name, float(params[i+1]))
                i+=1
            elif param_name in ["noz", "nof", "notile", "notileu", "notilev", \
                                "alphamirr", "bumpcoord", "usecol", "wave"]:
                setattr(material, "is_" + param_name, True)
                # i+=1
            elif param_name in ["RotPoint", "move"]:
                setattr(material, "is_" + param_name, True)
                setattr(material, param_name, [float(params[i+1]), float(params[i+2])])
                i+=2
            elif param_name[0:3] == "env":
                envid = param_name[3:]
                if len(envid) > 0:
                    setattr(material, "is_envId", True)
                    setattr(material, "envId", int(envid))
                else:
                    setattr(material, "is_env", True)
                    setattr(material, "env", [float(params[i+1]), float(params[i+2])])
                    i+=2
        i+=1


def save_maskfile_params(maskfile, params):
    i = 0
    while i < len(params):
        param_name = params[i].replace('"', '')
        if param_name == "noload":
            setattr(maskfile, "is_noload", True)
        else:
            some_int = None
            try:
                some_int = int(params[i])
            except:
                pass
            if some_int:
                setattr(maskfile, "is_someint", True)
                setattr(maskfile, "someint", some_int)
        i+=1


def save_texture_params(texture, params):
    i = 0
    while i < len(params):
        param_name = params[i].replace('"', '')
        if param_name in ["noload", "bumpcoord", "memfix"]:
            setattr(texture, "is_" + param_name, True)
        else:
            some_int = None
            try:
                some_int = int(params[i])
            except:
                pass
            if some_int:
                setattr(texture, "is_someint", True)
                setattr(texture, "someint", some_int)
        i+=1



def unpack_res(res_module, filepath, save_on_disk = True):
    log.info("Unpacking {}:".format(filepath))

    resdir = get_res_folder(filepath)
    curfolder = resdir
    if not os.path.exists(resdir):
        os.mkdir(resdir)

    sections = read_res_sections(filepath)

    for section in sections:
        section_name = section["name"]
        if section["cnt"] > 0:
            curfolder = os.path.join(resdir, section_name)
            if section_name in ["COLORS", "MATERIALS", "SOUNDS"]: # save only .txt
                binfile_path = os.path.join(curfolder, "{}.txt".format(section_name))
                if save_on_disk:
                    binfile_base = os.path.dirname(binfile_path)
                    binfile_base = Path(binfile_base)
                    binfile_base.mkdir(exist_ok=True, parents=True)
                    with open(binfile_path, "wb") as out_file:
                        for data in section['data']:
                            out_file.write((data['row']+"\n").encode("UTF-8"))
                if section_name == "MATERIALS":
                    for data in section['data']:
                        save_material(res_module, data['row'])
            else:
                for data in section['data']:
                    name_split = data['row'].split(" ")
                    fullname = name_split[0]
                    params = name_split[1:]
                    path_split = fullname.split("\\")
                    name = path_split[-1]
                    subpath = ""
                    if len(path_split) > 1:
                        subpath = "\\".join(path_split[:-1])
                    binfile_path = os.path.join(curfolder, "{}".format(fullname))
                    if save_on_disk:
                        binfile_base = os.path.dirname(binfile_path)
                        binfile_base = Path(binfile_base)
                        binfile_base.mkdir(exist_ok=True, parents=True)
                        with open(binfile_path, "wb") as binfile:
                            log.info("Saving file {}".format(binfile.name))
                            binfile.write(data['bytes'])

                    if section_name == "TEXTUREFILES":
                        texture = res_module.textures.add()
                        texture.tex_name = name
                        texture.subpath = subpath
                        save_texture_params(texture, params)

                    elif section_name == "MASKFILES":
                        maskfile = res_module.maskfiles.add()
                        maskfile.msk_name = name
                        maskfile.subpath = subpath
                        save_maskfile_params(maskfile, params)

                    elif section_name == "PALETTEFILES":
                        res_module.palette_subpath = subpath
                        res_module.palette_name = name

    return