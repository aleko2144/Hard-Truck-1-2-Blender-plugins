import os
import bpy
import struct

from pathlib import Path


from ..common import (
    exportres_logger
)

from .common import (
    write_cstring,
    srgb_to_rgb,
    read_res_sections,
    get_col_property_by_name,
    write_size,
    get_mat_texture_ref_dict,
    get_active_palette_module,
    is_inside_module,
    get_used_materials
)

from .imghelp import (
    convert_tga32_to_txr
)

log = exportres_logger

def export_res(context, op, export_dir):
    mytool = bpy.context.scene.my_tool

    exported_modules = [sn.name for sn in op.res_modules if sn.state is True]
    if not os.path.isdir(export_dir):
        export_dir = os.path.dirname(export_dir)

    for module_name in exported_modules:

        res_module = get_col_property_by_name(mytool.res_modules, module_name)
        if res_module is not None:

            filepath = os.path.join(export_dir, "{}.res".format(res_module.value))

            if op.to_merge:

                # allSections = ["PALETTEFILES", "SOUNDFILES", "SOUNDS", "BACKFILES", "MASKFILES", "COLORS", "TEXTUREFILES", "MATERIALS"]

                if not os.path.exists(filepath):
                    log.error("Not found file to merge into: {}".format(filepath))
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
                            write_cstring('{} {}'.format(section["name"], section["cnt"]), file)
                            if section['name'] in ["COLORS", "MATERIALS", "SOUNDS"]:
                                for data in section['data']:
                                    write_cstring(data['row'], file)
                            else:
                                for data in section['data']:
                                    write_cstring(data['row'], file)
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



def write_palettefiles(res_module, file):

    size = 0
    if len(res_module.palette_colors) > 0:
        size = 1

    write_cstring("PALETTEFILES {}".format(size), file)
    if size > 0:
        palette_name = res_module.palette_name
        if palette_name is None or len(palette_name) == 0:
            palette_name = "{}.plm".format(res_module.value)
        write_cstring("{}".format(palette_name), file)
        pal_name_write_ms = file.tell()
        file.write(struct.pack("<i", 0)) # reserve
        pal_name_ms = file.tell()
        file.write("PLM\00".encode("cp1251"))
        plm_write_ms = file.tell()
        file.write(struct.pack("<i", 0)) # reserve
        plm_ms = file.tell()
        file.write("PALT".encode("cp1251"))
        palt_write_ms = file.tell()
        file.write(struct.pack("<i", 0)) # reserve
        palt_ms = file.tell()
        for color in res_module.palette_colors:
            rgbcol = srgb_to_rgb(*color.value[:3])
            file.write(struct.pack("<B", rgbcol[0]))
            file.write(struct.pack("<B", rgbcol[1]))
            file.write(struct.pack("<B", rgbcol[2]))

        write_size(file, pal_name_ms, pal_name_write_ms)
        write_size(file, plm_ms, plm_write_ms)
        write_size(file, palt_ms, palt_write_ms)


def write_soundfiles(res_module, file):
    size = 0
    write_cstring("SOUNDFILES 0", file)


def write_backfiles(res_module, file):
    size = 0
    write_cstring("BACKFILES 0", file)


def write_maskfiles(res_module, file):
    size = 0
    write_cstring("MASKFILES 0", file)


def write_texturefiles(res_module, file, filepath, save_images = True):
    size = len(res_module.textures)

    write_cstring("TEXTUREFILES {}".format(size), file)
    if size > 0:
        export_folder = os.path.dirname(filepath)
        basename = os.path.basename(filepath)[:-4]
        export_folder = os.path.join(export_folder, '{}_export'.format(basename))
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

            image_name = "{}.tga".format(basepath_no_ext)
            txr_name = "{}.txr".format(basepath_no_ext)
            image_path = os.path.join(export_folder, image_name)
            texture_subpath = texture.subpath.rstrip("\\")
            texture_name = '{}{}{}'.format(texture_subpath, chr(92), txr_name)

            tex_params = []
            if texture.is_someint:
                tex_params.append("{}".format(texture.someint))

            for param in ["noload", "bumpcoord", "memfix"]:
                if getattr(texture, 'is_{}'.format(param)):
                    tex_params.append("{}".format(param))

            if len(tex_params) > 0:
                tex_str = '{} {}'.format(texture_name, "  ".join(tex_params))
            else:
                tex_str = texture_name
            write_cstring(tex_str, file)

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
    module_name = res_module.value
    

    # used_materials = sorted(get_used_materials(module_name))
    used_materials = [cn.mat_name for cn in res_module.materials]

    size = len(used_materials)
    write_cstring("MATERIALS {}".format(size), file)
    if size > 0:
        for material_name in used_materials:
            material = get_col_property_by_name(res_module.materials, material_name, 'mat_name')
            if material.id_mat is not None:
                mat_name = material.id_mat.name
                mat_str = mat_name
                mat_params = []
                if material.is_tex:
                    mat_params.append("{} {}".format(material.tex_type, material.tex))

                for param in ["col", "att", "msk", "power", "coord"]:
                    if getattr(material, 'is_{}'.format(param)):
                        int_param = getattr(material, param)
                        mat_params.append("{} {}".format(param, int_param))

                for param in ["reflect", "specular", "transp", "rot"]:
                    if getattr(material, 'is_{}'.format(param)):
                        float_param = float(getattr(material, param))
                        mat_params.append("{} {:.2f}".format(param, float_param))

                for param in ["noz", "nof", "notile", "notileu", "notilev", \
                                "alphamirr", "bumpcoord", "usecol", "wave"]:
                    if getattr(material, 'is_{}'.format(param)):
                        mat_params.append("{}".format(param))

                for param in ["RotPoint", "move", "env"]:
                    if getattr(material, 'is_{}'.format(param)):
                        param1, param2 = getattr(material, param)
                        mat_params.append("{} {:.2f} {:.2f}".format(param, param1, param2))

                if material.is_envId:
                    mat_params.append("env{}".format(material.envId))

                mat_params_str = "  ".join(mat_params)

                mat_str = "{} {}".format(mat_name, mat_params_str)
                write_cstring(mat_str, file)

def write_colors(res_module, file):
    size = 0
    write_cstring("COLORS 0", file)


def write_sounds(res_module, file):
    size = 0
    write_cstring("SOUNDS 0", file)


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
