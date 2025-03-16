import struct
import bpy
import re
from mathutils import Vector
import math

from ..common import common_logger
from ..consts import (
    BLOCK_TYPE,
    EMPTY_NAME
)

from ..compatibility import (
    is_before_2_80,
    matrix_multiply
)

#Setup module logger
log = common_logger

def write_size(file, ms, write_ms=None):
    if write_ms is None:
        write_ms = ms
    end_ms = file.tell()
    size = end_ms - ms
    file.seek(write_ms, 0)
    file.write(struct.pack("<i", size))
    file.seek(end_ms, 0)

def get_not_numeric_name(name):
    re_is_copy = re.compile(r'\|')
    match_ind = re_is_copy.search(name)
    result = name
    if match_ind:
        result = name[match_ind.span()[0]+1:]
    return result

def get_non_copy_name(name):
    re_is_copy = re.compile(r'\.[0-9]*$')
    match_ind = re_is_copy.search(name)
    result = name
    if match_ind:
        result = name[:match_ind.span()[0]]
    return result

def is_root_obj(obj):
    return obj.parent is None and obj.name[-4:] == '.b3d'

def get_root_obj(obj):
    result = obj
    while not is_root_obj(result):
        result = result.parent
    return result

def is_empty_name(name):
    re_is_empty = re.compile(r'.*{}.*'.format(EMPTY_NAME))
    return re_is_empty.search(name)

def is_mesh_block(obj):
    # 18 - for correct transform apply
    return obj.get("block_type") is not None \
        and (obj["block_type"]==8 or obj["block_type"]==35\
        or obj["block_type"]==28 \
        # or obj["block_type"]==18
        )

def is_ref_block(obj):
    return obj.get("block_type") is not None and obj["block_type"]==18

def unmask_template(templ):
    offset = 0
    unmasks = []
    t_a = int(templ[0])
    t_r = int(templ[1])
    t_g = int(templ[2])
    t_b = int(templ[3])
    total_bytes = t_r + t_g + t_b + t_a
    for i in range(4):
        cur_int = int(templ[i])
        lzeros = offset
        bits = cur_int
        rzeros = total_bytes - lzeros - bits
        unmasks.append([lzeros, bits, rzeros])
        offset += cur_int
    return unmasks

class BitMask:
    def __init__(self):
        self.lzeros = 0
        self.ones = 0
        self.rzeros = 0

def unmask_bits(num, bytes_cnt=2):
    bits = [int(digit) for digit in bin(num)[2:]]
    bitmask = BitMask()
    if num == 0:
        return bitmask
    for bit in bits:
        if bit:
            bitmask.ones+=1
        else:
            bitmask.rzeros+=1
        bitmask.lzeros = bytes_cnt*8 - len(bits)
    return bitmask


def read_cstring(file):
    try:
        chrs = []
        i = 0
        chrs.append(file.read(1).decode("utf-8"))
        while ord(chrs[i]) != 0:
            chrs.append(file.read(1).decode("utf-8"))
            i += 1
        return "".join(chrs[:-1])
    except TypeError as e:
        log.warning("Error in read_cstring. Nothing to read")
        return ""

def write_cstring(txt, file):
    if txt[-1] != "\00":
        txt += "\00"
    file.write(txt.encode("cp1251"))


def read_res_sections(filepath):
    sections = []
    with open(filepath, "rb") as file:
        k = 0
        while 1:
            category = read_cstring(file)
            if(len(category) > 0):
                res_split = category.split(" ")
                cat_id = res_split[0]
                cnt = int(res_split[1])

                sections.append({})

                sections[k]["name"] = cat_id
                sections[k]["cnt"] = cnt
                sections[k]["data"] = []

                log.info("Reading category {}".format(cat_id))
                log.info("Element count in category is {}.".format(cnt))
                if cnt > 0:
                    log.info("Start processing...")
                    res_data = []
                    if cat_id in ["COLORS", "MATERIALS", "SOUNDS"]: # save only .txt
                        for i in range(cnt):
                            data = {}
                            data['row'] = read_cstring(file)
                            res_data.append(data)

                    else: #PALETTEFILES, SOUNDFILES, BACKFILES, MASKFILES, TEXTUREFILES
                        for i in range(cnt):

                            data = {}
                            data['row'] = read_cstring(file)
                            data['size'] = struct.unpack("<i",file.read(4))[0]
                            data['bytes'] = file.read(data['size'])
                            res_data.append(data)

                    sections[k]['data'] = res_data

                else:
                    log.info("Skip category")
                k += 1
            else:
                break
    return sections


class HTMaterial():

    def __init__(self):
        self.prefix = ""
        self.path = ""
        self.reflect = None #HT1 float
        self.specular = None #HT1 float
        self.transp = None # float
        self.rot = None # float
        self.col = None # int
        self.tex = None # int
        self.ttx = None # int
        self.itx = None # int
        self.att = None # int
        self.msk = None # int
        self.power = None # int
        self.coord = None # int
        self.envId = None # int
        self.env = None #scale x,y  2 floats
        self.rotPoint = None # 2 floats
        self.move = None # 2 floats
        self.noz = False # bool
        self.nof = False # bool
        self.notile = False # bool
        self.notileu = False # bool
        self.notilev = False # bool
        self.alphamirr = False # bool
        self.bumpcoord = False # bool
        self.usecol = False # bool
        self.wave = False # bool

def get_col_property_by_name(col_property, value, col_name = 'value'):
    result = None
    for item in col_property:
        if getattr(item, col_name) == value:
            result = item
            break
    return result

def get_col_property_index_by_name(col_property, value, col_name='value'):
    result = -1
    for idx, item in enumerate(col_property):
        if getattr(item, col_name) == value:
            result = idx
            break
    return result

def exists_col_property_by_name(col_property, value, col_name='value'):
    for item in col_property:
        if getattr(item, col_name) == value:
            return True
    return False

def get_material_index_in_res(mat_name, res_module_name):
    res_modules = bpy.context.scene.my_tool.res_modules
    cur_module = get_col_property_by_name(res_modules, res_module_name)
    cur_material_ind = get_col_property_index_by_name(cur_module.materials, mat_name, 'mat_name')
    if cur_material_ind == -1:
        cur_material_ind = 1
    return cur_material_ind

def get_color_img_name(module_name, index):
    return "col_{}_{:03d}".format(module_name, index)

# https://blenderartists.org/t/index-lookup-in-a-collection/512818/2
def get_col_property_index(prop):
    txt = prop.path_from_id()
    pos = txt.rfind('[')
    col_index = txt[pos+1: len(txt)-1]
    return int(col_index)

def get_current_res_index():
    mytool = bpy.context.scene.my_tool
    return int(mytool.selected_res_module)

def get_current_res_module():
    mytool = bpy.context.scene.my_tool
    res_module = None
    ind = get_current_res_index()
    if ind > -1:
        res_module = mytool.res_modules[ind]
    return res_module

def get_active_palette_module(res_module):
    mytool = bpy.context.scene.my_tool
    if res_module:
        if len(res_module.palette_colors) > 0:
            return res_module

        common_res_module = get_col_property_by_name(mytool.res_modules, 'COMMON')
        if len(common_res_module.palette_colors) > 0:
            return common_res_module
    return None

def update_color_preview(res_module, ind):
    module_name = res_module.value
    bpy_image = bpy.data.images.get(get_color_img_name(module_name, ind+1))
    if bpy_image is None:
        bpy_image = bpy.data.images.new(get_color_img_name(module_name, ind+1), width=1, height=1, alpha=1)
    bpy_image.pixels[0] = res_module.palette_colors[ind].value[0]
    bpy_image.pixels[1] = res_module.palette_colors[ind].value[1]
    bpy_image.pixels[2] = res_module.palette_colors[ind].value[2]
    bpy_image.pixels[3] = res_module.palette_colors[ind].value[3]
    if not is_before_2_80:
        bpy_image.preview_ensure()
        bpy_image.preview.reload()


def get_mat_texture_ref_dict(res_module):
    mat_to_texture = {}
    texture_to_mat = {}
    for i, mat in enumerate(res_module.materials):
        if mat.is_tex:
            mat_to_texture[i] = mat.tex-1
            texture_to_mat[mat.tex-1] = i

    return [mat_to_texture, texture_to_mat]


def rgb_to_srgb(r, g, b, alpha = 1):
    # convert from RGB to sRGB
    r_linear = r / 255.0
    g_linear = g / 255.0
    b_linear = b / 255.0

    def srgb_transform(value):
        if value <= 0.04045:
            return value / 12.92
        else:
            return math.pow(((value + 0.055) / 1.055), 2.4)

    r_srgb = srgb_transform(r_linear)
    g_srgb = srgb_transform(g_linear)
    b_srgb = srgb_transform(b_linear)

    return (r_srgb, g_srgb, b_srgb, alpha)


def srgb_to_rgb(r, g, b):
    # convert from sRGB to RGB

    def srgb_inverse_transform(value):
        if value <= 0.04045 / 12.92:
            return value * 12.92
        else:
            return math.pow(value, 1 / 2.4) * 1.055 - 0.055

    r_rgb = srgb_inverse_transform(r)
    g_rgb = srgb_inverse_transform(g)
    b_rgb = srgb_inverse_transform(b)

    return (round(r_rgb * 255), round(g_rgb * 255), round(b_rgb * 255))

# https://blender.stackexchange.com/questions/234388/how-to-convert-rgb-to-hex-almost-there-1-error-colors
# def linear_to_srgb8(c):
#     if c < 0.0031308:
#         srgb = 0.0 if c < 0.0 else c * 12.92
#     else:
#         srgb = 1.055 * math.pow(c, 1.0 / 2.4) - 0.055
#     if srgb > 1: srgb = 1

#     return round(255*srgb)

#https://blender.stackexchange.com/questions/158896/how-set-hex-in-rgb-node-python
# def srgb_to_linearrgb(c):
#     if   c < 0:       return 0
#     elif c < 0.04045: return c/12.92
#     else:             return ((c+0.055)/1.055)**2.4

# def hex_to_rgb(r,g,b,alpha=1):
#     return tuple([srgb_to_linearrgb(c/0xff) for c in (r,g,b)] + [alpha])


def get_used_vertices_and_transform(vertices, faces):
    indices = set()
    old_new_transf = {}
    new_old_transf = {}
    new_vertexes = []
    new_faces = []
    for face in faces:
        for idx in face:
            indices.add(idx)
    indices = sorted(indices)
    for idx in indices:
        old_new_transf[idx] = len(new_vertexes)
        new_old_transf[len(new_vertexes)] = idx
        new_vertexes.append(vertices[idx])
    new_faces = get_used_faces(faces, old_new_transf)

    return [new_vertexes, new_faces, indices, old_new_transf, new_old_transf]

def transform_vertices(vertices, idx_transf):
    new_vertices = []
    for idx in vertices:
        new_vertices.append(idx_transf[idx])
    return new_vertices

def get_used_faces(faces, idx_transf):
    new_faces = []
    for face in faces:
        new_face = get_used_face(face, idx_transf)
        new_faces.append(tuple(new_face))
    return new_faces

def get_user_vertices(faces):
    indices = set()
    for face in faces:
        for idx in face:
            indices.add(idx)
    return list(indices)


def get_used_face(face, idx_transf):
    new_face = []
    for idx in face:
        new_face.append(idx_transf[idx])
    return new_face


def get_polygons_by_selected_vertices(obj):
    data = obj.data
    # data = bpy.context.object.data
    selected_polygons = []
    for f in data.polygons:
        s = True
        for v in f.vertices:
            if not data.vertices[v].select:
                s = False
                break
        if s:
            selected_polygons.append(f)
    return selected_polygons

def get_selected_vertices(obj):
    data = obj.data
    # data = bpy.context.object.data
    selected_vertices = []
    for v in data.vertices:
        if v.select:
            selected_vertices.append(v)

    return selected_vertices


def get_all_children(obj):
    all_children = []
    current_objs = [obj]
    while(1):
        next_children = []
        if len(current_objs) > 0:
            for obj in current_objs:
                next_children.extend(obj.children)
            current_objs = next_children
            all_children.extend(current_objs)
        else:
            break
    return all_children

# class MyToolBlockHandler():

def get_pythagor_length(p1, p2):
    return (sum(map(lambda xx,yy : (xx-yy)**2,p1,p2)))**0.5

# https://b3d.interplanety.org/en/how-to-calculate-the-bounding-sphere-for-selected-objects/
def get_mult_obj_bounding_sphere(objn_transfs, mode='BBOX'):
    # return the bounding sphere center and radius for objects (in global coordinates)
    # if not isinstance(objects, list):
    #     objects = [objects]
    points_co_global = []
    # if mode == 'GEOMETRY':
    #     # GEOMETRY - by all vertices/points - more precis, more slow
    #     for obj in objects:
    #         points_co_global.extend([obj.matrix_world @ vertex.co for vertex in obj.data.vertices])
    if mode == 'BBOX':
        # BBOX - by object bounding boxes - less precis, quick
        for objn_transf in objn_transfs:
            obj = bpy.data.objects[objn_transf['obj']]
            transf = bpy.data.objects[objn_transf['transf']]
            points_co_global.extend([matrix_multiply(transf.matrix_world, Vector(bbox)) for bbox in obj.bound_box])

    def get_center(l):
        return (max(l) + min(l)) / 2 if l else 0.0

    x, y, z = [[point_co[i] for point_co in points_co_global] for i in range(3)]
    b_sphere_center = Vector([get_center(axis) for axis in [x, y, z]]) if (x and y and z) else None
    b_sphere_radius = max(((point - b_sphere_center) for point in points_co_global)) if b_sphere_center else None
    return [b_sphere_center, b_sphere_radius.length]

# https://blender.stackexchange.com/questions/62040/get-center-of-geometry-of-an-object
def get_single_bounding_sphere(obj, local = False):
    center = 0.125 * sum((Vector(b) for b in obj.bound_box), Vector())
    p1 = obj.bound_box[0]
    if not local:
        center = matrix_multiply(obj.matrix_world, center)
        p1 = matrix_multiply(obj.matrix_world, Vector(obj.bound_box[0]))
    rad = get_pythagor_length(center, p1)
    return [center, rad]

def get_center_coord(vertices):
    if len(vertices) == 0:
        return (0.0, 0.0, 0.0)
    x = [p[0] for p in vertices]
    y = [p[1] for p in vertices]
    z = [p[2] for p in vertices]
    centroid = (sum(x) / len(vertices), sum(y) / len(vertices), sum(z) / len(vertices))

    return centroid

def get_level_group(obj):
    parent = obj.parent
    if parent is None:
        return 0
    if parent.get(BLOCK_TYPE) == 444:
        return int(parent.name[6]) #GROUP_n
    return 0

class RGBPacker:
    
    @staticmethod
    def pack_byte_to_float(_byte):
        return _byte / 255

    @staticmethod
    def pack_int_to_3floats(_int):
        result = [0.0, 0.0, 0.0]
        result[0] = RGBPacker.pack_byte_to_float((_int >> 16) & 255)
        result[1] = RGBPacker.pack_byte_to_float((_int >> 8) & 255)
        result[2] = RGBPacker.pack_byte_to_float((_int) & 255)
        return result

    @staticmethod
    def pack_int_to_4floats(_int):
        result = [0.0, 0.0, 0.0, 0.0]
        result[0] = RGBPacker.pack_byte_to_float((_int >> 24) & 255)
        result[1] = RGBPacker.pack_byte_to_float((_int >> 16) & 255)
        result[2] = RGBPacker.pack_byte_to_float((_int >> 8) & 255)
        result[3] = RGBPacker.pack_byte_to_float((_int) & 255)
        return result

    @staticmethod
    def unpack_float_to_byte(_float):
        return round(_float * 255)

    @staticmethod
    def unpack_3floats_to_int(_float_arr):
        result = 0
        result = result | (RGBPacker.unpack_float_to_byte(_float_arr[0]) << 16)
        result = result | (RGBPacker.unpack_float_to_byte(_float_arr[1]) << 8)
        result = result | (RGBPacker.unpack_float_to_byte(_float_arr[2]))
        return result


    @staticmethod
    def unpack_4floats_to_int(_float_arr):
        result = 0
        result = result | (RGBPacker.unpack_float_to_byte(_float_arr[0]) << 24)
        result = result | (RGBPacker.unpack_float_to_byte(_float_arr[1]) << 16)
        result = result | (RGBPacker.unpack_float_to_byte(_float_arr[2]) << 8)
        result = result | (RGBPacker.unpack_float_to_byte(_float_arr[3]))
        return result


class FloatPacker:
    templ_f = 0b111111000000000000000000000000 #mantissa mask, predefined 6 bits to decrease conversion error
    mask_f = 0b111111011111111000000000000000 # float mask for mantissa 6 bits and first 8 exponent bits
    b_shift = 15 #bit shifting to correct exponent

    @staticmethod
    def pack_byte_to_float(_byte):
        return itof((FloatPacker.templ_f | (_byte << FloatPacker.b_shift)) & FloatPacker.mask_f)
            
    @staticmethod
    def pack_int_to_4floats(_int):
        result = [0.0, 0.0, 0.0, 0.0]
        result[0] = FloatPacker.pack_byte_to_float((_int >> 24) & 255)
        result[1] = FloatPacker.pack_byte_to_float((_int >> 16) & 255)
        result[2] = FloatPacker.pack_byte_to_float((_int >> 8) & 255)
        result[3] = FloatPacker.pack_byte_to_float((_int) & 255)
        return result
    
    @staticmethod
    def unpack_float_to_byte(_float):
        return ftoi(_float) >> FloatPacker.b_shift & 255

    @staticmethod
    def unpack_4floats_to_int(_float_arr):
        result = 0
        result = result | (FloatPacker.unpack_float_to_byte(_float_arr[0]) << 24)
        result = result | (FloatPacker.unpack_float_to_byte(_float_arr[1]) << 16)
        result = result | (FloatPacker.unpack_float_to_byte(_float_arr[2]) << 8)
        result = result | (FloatPacker.unpack_float_to_byte(_float_arr[3]))
        return result

def ftoi(_float):
    return struct.unpack('<i', struct.pack('<f', _float))[0]

def itof(_int):
    return struct.unpack('<f', struct.pack('<i', _int))[0]

def referenceables_callback(self, context):

    mytool = context.scene.my_tool
    root_obj = get_root_obj(context.object)

    referenceables = [cn for cn in root_obj.children if cn.get(BLOCK_TYPE) != 24]

    enum_properties = [(cn.name, cn.name, "") for i, cn in enumerate(referenceables)]

    return enum_properties

def spaces_callback(self, context):

    mytool = context.scene.my_tool
    root_obj = get_root_obj(context.object)

    spaces = [cn for cn in bpy.data.objects if cn.get(BLOCK_TYPE) == 24 and get_root_obj(cn) == root_obj]

    enum_properties = [(cn.name, cn.name, "") for i, cn in enumerate(spaces)]

    return enum_properties

def res_materials_callback(self, context):

    mytool = context.scene.my_tool
    root_obj = get_root_obj(context.object)
    module_name = root_obj.name[:-4]

    res_modules = mytool.res_modules
    cur_module = get_col_property_by_name(res_modules, module_name)

    enum_properties = [(str(i), cn.mat_name, "") for i, cn in enumerate(cur_module.materials)]

    return enum_properties

def rooms_callback(bname, pname):
    def callback_func(self, context):

        enum_properties = []

        mytool = context.scene.my_tool
        res_module = context.object.path_resolve('["{}"]'.format(pname))

        root_obj = bpy.data.objects.get('{}.b3d'.format(res_module))
        if root_obj:
            rooms = [cn for cn in root_obj.children if cn.get(BLOCK_TYPE) == 19]

            enum_properties = [(cn.name, cn.name, "") for i, cn in enumerate(rooms)]

        return enum_properties
    return callback_func


def modules_callback(self, context):

    modules = [cn for cn in bpy.data.objects if is_root_obj(cn)]
    enum_properties = [(cn.name[:-4], cn.name[:-4], "") for i, cn in enumerate(modules)]
    return enum_properties


def res_modules_callback(self, context):

    mytool = bpy.context.scene.my_tool
    modules = [cn for cn in mytool.res_modules if cn.value != "-1"]
    enum_properties = [(cn.value, cn.value, "") for i, cn in enumerate(modules)]
    return enum_properties