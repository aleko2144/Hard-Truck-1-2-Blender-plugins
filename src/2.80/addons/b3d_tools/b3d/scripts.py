import bpy
import re

from .class_descr import (
    Blk018,
    Blk021
)
from ..common import (
    scripts_logger
)
from .common import (
    get_polygons_by_selected_vertices,
    get_selected_vertices,
    is_root_obj,
    is_mesh_block,
    get_root_obj,
    get_all_children,
    get_level_group
)
from .class_descr import (
    FieldType
)

from .classes import (
    BlockClassHandler
)

from ..consts import (
    BLOCK_TYPE,
    EMPTY_NAME,
    TRANSF_COLLECTION,
    TEMP_COLLECTION
)

log = scripts_logger

reb3d_space = re.compile(r'.*b3dSpaceCopy.*')
reb3d_mesh = re.compile(r'.*b3dcopy.*')

class Graph:

    def __init__(self, graph):
        self.graph = graph

    def dfs_util(self, val, visited):

        visited[val]["in"] += 1
        for v in self.graph[val]:
            if self.graph.get(v) is not None:
                visited[val]["out"] += 1
                self.dfs_util(v, visited)

    def dfs(self, start=None):
        visited = {}
        for val in self.graph.keys():
            visited[val] = {
                "in": 0,
                "out": 0
            }

        search_in = []
        if start is not None:
            search_in.append(start.name)
        else:
            search_in = self.graph.keys()

        for val in search_in:
            for v in self.graph[val]:
                if self.graph.get(v) is not None:
                    visited[val]["out"] += 1
                    self.dfs_util(v, visited)

        return visited


def prop(obj):
    return obj['prop']


def apply_transforms():
    roots = [cn for cn in bpy.data.objects if is_root_obj(cn)]
    for root in roots:
        hroots = get_hierarchy_roots(root)
        for hroot in hroots:
            obj = bpy.data.objects.get(hroot)
            if obj is not None:
                apply_transform(obj)

def apply_transform(root):

    transf_collection = bpy.data.collections.get(TRANSF_COLLECTION)
    if transf_collection is None:
        transf_collection = bpy.data.collections.new(TRANSF_COLLECTION)
        bpy.context.scene.collection.children.link(transf_collection)

    if bpy.data.objects.get('b3dCenterSpace') is None:
        b3d_obj = bpy.data.objects.new('b3dCenterSpace', None)
        b3d_obj[BLOCK_TYPE] = 24
        b3d_obj.rotation_euler[0] = 0.0
        b3d_obj.rotation_euler[1] = 0.0
        b3d_obj.rotation_euler[2] = 0.0
        b3d_obj.location = (0.0, 0.0, 0.0)
        transf_collection.objects.link(b3d_obj)

    if bpy.data.objects.get('b3dCenterSpace' + '_b3dSpaceCopy') is None:
        b3d_obj = bpy.data.objects.new('b3dCenterSpace' + '_b3dSpaceCopy', None)
        b3d_obj[BLOCK_TYPE] = 24
        b3d_obj.rotation_euler[0] = 0.0
        b3d_obj.rotation_euler[1] = 0.0
        b3d_obj.rotation_euler[2] = 0.0
        b3d_obj.location = (0.0, 0.0, 0.0)
        transf_collection.objects.link(b3d_obj)

    stack = [[root, 'b3dCenterSpace', 'b3dCenterSpace' + '_b3dSpaceCopy']]

    while stack:
        block, prev_space, prev_space_copy = stack.pop()

        prev_space_obj = bpy.data.objects.get(prev_space)
        prev_space_copy_obj = bpy.data.objects.get(prev_space_copy)

        # log.debug("{} {}".format(block[BLOCK_TYPE], block.name))
        # log.debug(prev_space)
        # log.debug(prev_space_copy)

        if block[BLOCK_TYPE] == 18:
            obj_name = block[prop(Blk018.Add_Name)]
            space_name = block[prop(Blk018.Space_Name)]

            dest_obj = bpy.data.objects.get(obj_name)

            if not block.hide_get():

                if space_name == EMPTY_NAME:
                    space_name = prev_space

                space_obj = bpy.data.objects.get(space_name)

                if(space_obj == None):
                    log.warn("Transformation object not found in " + block.name)
                    return

                if(dest_obj == None):
                    log.warn("Destination object not found in " + block.name)
                    return

                space_copy = None
                if bpy.data.objects.get(space_obj.name + "_b3dSpaceCopy"):
                    space_copy = bpy.data.objects[space_obj.name + "_b3dSpaceCopy"]
                else:
                    space_copy = space_obj.copy()
                    space_copy.parent = prev_space_copy_obj
                    space_copy.rotation_euler[0] = space_obj.rotation_euler[0]
                    space_copy.rotation_euler[1] = space_obj.rotation_euler[1]
                    space_copy.rotation_euler[2] = space_obj.rotation_euler[2]
                    space_copy.location = space_obj.location
                    space_copy.name = space_obj.name + "_b3dSpaceCopy"
                    transf_collection.objects.link(space_copy)
                stack.append([dest_obj, space_obj.name, space_copy.name])
            # else:
            #     stack.append([dest_obj, prev_space, prev_space_copy])

            continue

        if is_mesh_block(block) and not block.hide_get():
            # block.hide_set(True)
            # log.debug(block.name)
            # log.debug(prev_space)
            newmesh = block.copy()
            # newmesh.data = mesh.data.copy() # for NOT linked copy
            newmesh.parent = prev_space_copy_obj
            newmesh.name = f"{block.name}_b3dcopy"
            # log.info("Linking {}".format(newmesh.name))
            transf_collection.objects.link(newmesh)
            # newmesh.hide_set(False)

        for direct_child in block.children:
            stack.append([direct_child, prev_space, prev_space_copy])


def apply_remove_transforms(self):
    to_remove = False
    for obj in (bpy.data.objects):
        if reb3d_space.search(obj.name):
            to_remove = True
            break
    if to_remove:
        remove_transforms()
        self.report({'INFO'}, "Transforms removed")
    else:
        apply_transforms()
        self.report({'INFO'}, "Transforms applied")

def remove_transforms():
    spaces = [cn for cn in bpy.data.objects if reb3d_space.search(cn.name)]
    meshes = [cn for cn in bpy.data.objects if reb3d_mesh.search(cn.name)]

    reb3d_pos = re.compile(r'b3dcopy')

    bpy.ops.object.select_all(action = 'DESELECT')

    for mesh in meshes:
        # res = reb3d_pos.search(mesh.name)
        # postfixStart = res.start()
        # original = bpy.data.objects[mesh.name[:postfixStart-1]]
        # original.hide_set(False)
        mesh.select_set(True)
    bpy.ops.object.delete()

    for space in spaces:
        space.select_set(True)
    bpy.ops.object.delete()


def show_hide_obj_by_type(self, block_type):
    objs = [cn for cn in bpy.data.objects if cn.get("block_type") is not None and cn["block_type"]==block_type]
    hidden_obj = [cn for cn in bpy.data.objects if cn.get("block_type") is not None and cn["block_type"]==block_type and cn.hide_get()]
    if len(objs) == len(hidden_obj):
        for obj in objs:
            obj.hide_set(False)
        self.report({'INFO'}, f"{len(objs)} (block {block_type}) objects are shown")
    else:
        for obj in objs:
            obj.hide_set(True)
        self.report({'INFO'}, f"{len(objs)} (block {block_type}) objects are hidden")

def show_hide_obj_tree_by_type(block_type):
    objs = [cn for cn in bpy.data.objects if cn.get("block_type") is not None and cn["block_type"]==block_type]
    hidden_obj = [cn for cn in bpy.data.objects if cn.get("block_type") is not None and cn["block_type"]==block_type and cn.hide_get()]
    if len(objs) == len(hidden_obj):
        for obj in objs:
            children = get_all_children(obj)
            for child in children:
                child.hide_set(False)
            obj.hide_set(False)
    else:
        for obj in objs:
            children = get_all_children(obj)
            for child in children:
                child.hide_set(True)
            obj.hide_set(True)

def get_hierarchy_roots(root):
    global_root = root
    while global_root.parent is not None:
        global_root = global_root.parent

    blocks18 = [cn for cn in bpy.data.objects if cn[BLOCK_TYPE] is not None and cn[BLOCK_TYPE] == 18 and get_root_obj(cn) == global_root]
    ref_set = set()
    for cn in blocks18:
        #out refs
        if bpy.data.objects.get(cn[prop(Blk018.Add_Name)]) is not None:
            ref_set.add(cn[prop(Blk018.Add_Name)])

        #in refs
        temp = cn
        while temp.parent is not global_root:
            temp = temp.parent
        ref_set.add(temp.name)

    referenceables = list(ref_set)
    referenceables.sort()

    other = [cn.name for cn in global_root.children if cn[BLOCK_TYPE] is not None \
        and (cn[BLOCK_TYPE] in [4, 5, 19]) \
        and cn.name not in referenceables ]

    no_dub_graph = {}
    graph = {}
    for r in referenceables:
        no_dub_graph[r] = set()

    for r in referenceables:
        references = [cn for cn in get_all_children(bpy.data.objects[r]) if cn[BLOCK_TYPE] is not None and cn[BLOCK_TYPE] == 18]
        for ref_obj in references:
            no_dub_graph[r].add(ref_obj[prop(Blk018.Add_Name)])

    for r in referenceables:
        graph[r] = list(no_dub_graph[r])

    zgraph = Graph(graph)

    closest_root = root
    if closest_root != global_root:
        if closest_root.name not in graph:
            while (closest_root.parent[BLOCK_TYPE] is not None and closest_root.parent[BLOCK_TYPE] != 5 \
            and closest_root.parent.name not in graph) or closest_root.parent is None: # closest or global
                closest_root = closest_root.parent
    else:
        closest_root = None

    visited = zgraph.dfs(closest_root)

    roots = [cn for cn in visited.keys() if (visited[cn]["in"] == 0) and (visited[cn]["out"] > 0)]

    res = other
    res.extend(roots)

    return res


def process_lod(root, state, explevel = 0, curlevel = -1):

    stack = [[root, curlevel, False]]

    while stack:
        bl_children = []
        block, clevel, is_active = stack.pop()

        if block[BLOCK_TYPE] == 18:
            ref_obj = bpy.data.objects.get(block[prop(Blk018.Add_Name)])
            if ref_obj is not None:
                stack.append([ref_obj, clevel, is_active])
                if is_active:
                    block.hide_set(state)

        if block[BLOCK_TYPE] == 10:
            clevel += 1

        if block[BLOCK_TYPE] in [9, 10, 21]:
            for ch in block.children:
                bl_children.extend(ch.children)
        else:
            bl_children = block.children

        if is_active and is_mesh_block(block):
            block.hide_set(state)

        for direct_child in bl_children:

            # if direct_child[BLOCK_TYPE] == 444:
            #     log.debug("Skipping {}".format(direct_child.name))
            #     for ch in direct_child.children:
            #         stack.append([ch, clevel, is_active])
            #     continue

            if clevel == explevel:
                # if direct_child[LEVEL_GROUP] == 1:
                if get_level_group(direct_child) == 1:
                    stack.append([direct_child, clevel, True])
                else:
                    stack.append([direct_child, -1, is_active])
            elif clevel > explevel:
                stack.append([direct_child, clevel, True])
            else:
                stack.append([direct_child, clevel, is_active])


def show_lod(root):
    if root.parent is None:
        hroots = get_hierarchy_roots(root)
        for hroot in hroots:
            obj = bpy.data.objects.get(hroot)
            if obj is not None:
                process_lod(obj, False, 0, -1)
    else:
        process_lod(root, False, 0, -1)

def hide_lod(root):
    if root.parent is None:
        hroots = get_hierarchy_roots(root)
        for hroot in hroots:
            obj = bpy.data.objects.get(hroot)
            if obj is not None:
                process_lod(obj, True, 0, -1)
    else:
        process_lod(root, True, 0, -1)


def process_cond(root, group, state):

    curlevel = 0
    globlevel = 0

    stack = [[root, curlevel, globlevel, 0, False]]

    while stack:
        bl_children = []
        block, clevel, glevel, group_max, is_active = stack.pop()

        l_group = group

        if block[BLOCK_TYPE] == 18:
            ref_obj = bpy.data.objects.get(block[prop(Blk018.Add_Name)])
            if ref_obj is not None:
                stack.append([ref_obj, clevel+1, glevel, group_max, is_active])
                if is_active:
                    block.hide_set(state)

        if block[BLOCK_TYPE] == 21:
            glevel += 1
            clevel = 1
            group_max = block[prop(Blk021.GroupCnt)]
            if l_group > group_max-1:
                l_group = group_max-1


        if block[BLOCK_TYPE] in [9, 10, 21]:
            for ch in block.children:
                bl_children.extend(ch.children)
        else:
            bl_children = block.children

        if is_active and is_mesh_block(block):
            block.hide_set(state)

        for direct_child in bl_children:
            log.debug(f"Processing {direct_child.name}")
            next_state = False
            if glevel == 1:
                next_state = True
            elif glevel > 1:
                next_state = is_active and True
            if clevel == 1:
                # if direct_child[LEVEL_GROUP] == l_group or l_group == -1:
                if get_level_group(direct_child) == l_group or l_group == -1:
                    stack.append([direct_child, clevel+1, glevel, group_max, next_state])
                else:
                    stack.append([direct_child, clevel+1, glevel, group_max, False])
            elif clevel > 1:
                stack.append([direct_child, clevel+1, glevel, group_max, is_active])
            else:
                stack.append([direct_child, clevel+1, glevel, group_max, False])

def show_conditionals(root, group):

    if root.parent is None:
        hroots = get_hierarchy_roots(root)
        for hroot in hroots:
            obj = bpy.data.objects.get(hroot)
            if obj is not None:
                process_cond(obj, group, False)
    else:
        process_cond(root, group, False)


def hide_conditionals(root, group):

    if root.parent is None:
        hroots = get_hierarchy_roots(root)
        for hroot in hroots:
            obj = bpy.data.objects.get(hroot)
            if obj is not None:
                process_cond(obj, group, True)
    else:
        process_cond(root, group, True)

def create_center_driver(src_obj, bname, pname):
    d = None
    for i in range(3):

        d = src_obj.driver_add('location', i).driver

        v = d.variables.new()
        v.name = f'location{i}'
        # v.targets[0].id_type = 'SCENE'
        # v.targets[0].id = bpy.context.scene
        # v.targets[0].data_path = 'my_tool.{}.{}[{}]'.format(bname, pname, i)
        v.targets[0].id = bpy.context.object
        v.targets[0].data_path = f'["{pname}"][{i}]'

        d.expression = v.name

def create_rad_driver(src_obj, bname, pname):
    d = src_obj.driver_add('empty_display_size').driver

    v1 = d.variables.new()
    v1.name = 'rad'
    # v1.targets[0].id_type = 'SCENE'
    # v1.targets[0].id = bpy.context.scene
    # v1.targets[0].data_path = 'my_tool.{}.{}'.format(bname, pname)
    v1.targets[0].id = bpy.context.object
    v1.targets[0].data_path = f'["{pname}"]'

    d.expression = v1.name

def show_hide_sphere(context, root, pname):

    transf_collection = bpy.data.collections.get(TEMP_COLLECTION)
    if transf_collection is None:
        transf_collection = bpy.data.collections.new(TEMP_COLLECTION)
        bpy.context.scene.collection.children.link(transf_collection)

    obj_name = f"{root.name}||{pname}||temp"

    b3d_obj = bpy.data.objects.get(obj_name)

    if b3d_obj is not None:
        bpy.data.objects.remove(b3d_obj, do_unlink=True)
    else:

        bnum = root.get(BLOCK_TYPE)

        center_name = f"{pname}_center"
        rad_name = f"{pname}_rad"

        center = root.get(center_name)
        rad = root.get(rad_name)

        # creating object

        b3d_obj = bpy.data.objects.new(obj_name, None)
        b3d_obj.empty_display_type = 'SPHERE'
        b3d_obj.empty_display_size = rad
        b3d_obj.location = center
        b3d_obj.parent = root.parent

        transf_collection.objects.link(b3d_obj)

        # center driver
        bname = BlockClassHandler.get_mytool_block_name('Blk', bnum)

        create_center_driver(b3d_obj, bname, center_name)

        # rad driver
        create_rad_driver(b3d_obj, bname, rad_name)

def draw_common(l_self, obj):
    block_type = None
    level_group = None
    if BLOCK_TYPE in obj:
        block_type = obj[BLOCK_TYPE]

    level_group = get_level_group(obj)

    len_str = str(len(obj.children))

    box = l_self.layout.box()
    box.label(text="Block type: " + str(block_type))
    box.label(text="Children block count: " + len_str)
    box.label(text="Block group: " + str(level_group))

def draw_all_fields_by_type(l_self, context, zclass, multiple_edit = True):
    draw_fields_by_type(l_self, context, zclass, multiple_edit)

def draw_fields_by_type(l_self, context, zclass, multiple_edit = True):

    attrs = [obj for obj in zclass.__dict__.keys() if not obj.startswith('__')]
    boxes = {}
    for attr in attrs:
        obj = zclass.__dict__[attr]

        bname, bnum = BlockClassHandler.get_mytool_block_name_by_class(zclass, multiple_edit)

        ftype = obj.get('type')
        subtype = obj.get('subtype')
        cur_group_name = obj.get('group')
        prop_text = obj.get('name')
        pname = obj.get('prop')
        blocktool = context.scene.block_tool
        cur_layout = l_self.layout

        if cur_group_name is not None:
            if boxes.get(cur_group_name) is None:
                boxes[cur_group_name] = l_self.layout.box()
            cur_layout = boxes[cur_group_name]


        if ftype == FieldType.SPHERE_EDIT:
            if not multiple_edit: # sphere edit available only in single object edit
                box = cur_layout.box()
                col = box.column()

                props = col.operator("wm.show_hide_sphere_operator")
                props.pname = pname

        elif ftype == FieldType.STRING \
        or ftype == FieldType.COORD \
        or ftype == FieldType.RAD \
        or ftype == FieldType.INT \
        or ftype == FieldType.FLOAT \
        or ftype == FieldType.ENUM \
        or ftype == FieldType.ENUM_DYN \
        or ftype == FieldType.LIST:

            box = cur_layout.box()
            if multiple_edit:
                box.prop(getattr(blocktool, bname), "show_"+pname)

            col = box.column()
            if ftype in [
                FieldType.STRING,
                FieldType.COORD,
                FieldType.RAD,
                FieldType.INT,
                FieldType.FLOAT
            ]:
                if multiple_edit: # getting from my_tool
                    col.prop(getattr(blocktool, bname), pname)
                else:
                    col.prop(context.object, f'["{pname}"]', text=prop_text)

            elif ftype in [FieldType.ENUM_DYN, FieldType.ENUM]:

                col.prop(getattr(blocktool, bname), f'{pname}_switch')

                if(getattr(getattr(blocktool, bname), f'{pname}_switch')):
                    col.prop(getattr(blocktool, bname), f'{pname}_enum')
                else:
                    if multiple_edit:
                        col.prop(getattr(blocktool, bname), pname)
                    else:
                        col.prop(context.object, f'["{pname}"]', text=prop_text)

            elif ftype == FieldType.LIST:
                collect = getattr(blocktool, bname)

                scn = bpy.context.scene

                rows = 2

                row = box.row()
                props = row.operator("wm.get_prop_value_operator")
                props.pname = pname
                props = row.operator("wm.set_prop_value_operator")
                props.pname = pname
                row = box.row()
                row.template_list("CUSTOM_UL_items", "", collect, pname, scn, "custom_index", rows=rows)

                col = row.column(align=True)
                props = col.operator("custom.list_action", icon='ADD', text="")
                props.action = 'ADD'
                props.bname = bname
                props.pname = pname
                props.customindex = "custom_index"
                props = col.operator("custom.list_action", icon='REMOVE', text="")
                props.action = 'REMOVE'
                props.bname = bname
                props.pname = pname
                props.customindex = "custom_index"
                col.separator()
                props = col.operator("custom.list_action", icon='TRIA_UP', text="")
                props.action = 'UP'
                props.bname = bname
                props.pname = pname
                props.customindex = "custom_index"
                props = col.operator("custom.list_action", icon='TRIA_DOWN', text="")
                props.action = 'DOWN'
                props.bname = bname
                props.pname = pname
                props.customindex = "custom_index"

            if multiple_edit:
                if getattr(getattr(blocktool, bname), "show_"+pname):
                    col.enabled = True
                else:
                    col.enabled = False

        elif ftype == FieldType.V_FORMAT:
            if multiple_edit:
                box = cur_layout.box()
                box.prop(getattr(blocktool, bname), f"show_{pname}".format(pname))

                col1 = box.column()
                col1.prop(getattr(blocktool, bname), f"{pname}_triang_offset")
                col1.prop(getattr(blocktool, bname), f"{pname}_use_uvs")
                col1.prop(getattr(blocktool, bname), f"{pname}_use_normals")
                col1.prop(getattr(blocktool, bname), f"{pname}_normal_flag")

                if getattr(getattr(blocktool, bname), "show_"+pname):
                    col1.enabled = True
                else:
                    col1.enabled = False


def get_obj_by_prop(context, b3d_obj, zclass, pname):

    attrs = [obj for obj in zclass.__dict__.keys() if not obj.startswith('__')]
    bname, bnum = BlockClassHandler.get_mytool_block_name_by_class(zclass, True)

    blocktool = context.scene.block_tool
    for b_attr in attrs:
        obj = zclass.__dict__[b_attr]

        if obj['prop'] == pname:

            if obj['type'] == FieldType.LIST:

                col = getattr(getattr(blocktool, bname), obj['prop'])

                col.clear()
                for i, obj in enumerate(b3d_obj[obj['prop']]):
                    item = col.add()
                    item.index = i
                    item.value = obj

def get_all_objs_by_type(context, b3d_obj, zclass):
    get_objs_by_type(context, b3d_obj, zclass)

def get_objs_by_type(context, b3d_obj, zclass):
    attrs = [obj for obj in zclass.__dict__.keys() if not obj.startswith('__')]
    bname, bnum = BlockClassHandler.get_mytool_block_name_by_class(zclass)

    blocktool = context.scene.block_tool
    for b_attr in attrs:
        obj = zclass.__dict__[b_attr]

        if obj['type'] != FieldType.SPHERE_EDIT:
            if getattr(getattr(blocktool, bname), "show_"+obj['prop']) is not None \
                and getattr(getattr(blocktool, bname), "show_"+obj['prop']):

                if obj['type'] == FieldType.FLOAT \
                or obj['type'] == FieldType.RAD:
                    setattr(
                        getattr(blocktool, bname),
                        obj['prop'],
                        float(b3d_obj[obj['prop']])
                    )

                elif obj['type'] == FieldType.INT:
                    setattr(
                        getattr(blocktool, bname),
                        obj['prop'],
                        int(b3d_obj[obj['prop']])
                    )

                elif obj['type'] == FieldType.STRING:
                    getattr(blocktool, bname)[obj['prop']] = str(b3d_obj[obj['prop']])

                elif obj['type'] == FieldType.ENUM \
                or obj['type'] == FieldType.ENUM_DYN:
                    setattr(
                        getattr(blocktool, bname),
                        obj['prop'],
                        str(b3d_obj[obj['prop']])
                    )

                elif obj['type'] == FieldType.LIST:

                    col = getattr(getattr(blocktool, bname), obj['prop'])

                    col.clear()
                    for i, obj in enumerate(b3d_obj[obj['prop']]):
                        item = col.add()
                        item.index = i
                        item.value = obj

                else:
                    setattr(
                        getattr(blocktool, bname),
                        obj['prop'],
                        b3d_obj[obj['prop']]
                    )

def set_obj_by_prop(context, b3d_obj, zclass, pname):

    attrs = [obj for obj in zclass.__dict__.keys() if not obj.startswith('__')]
    bname, bnum = BlockClassHandler.get_mytool_block_name_by_class(zclass, True)

    blocktool = context.scene.block_tool
    for b_attr in attrs:
        obj = zclass.__dict__[b_attr]

        if obj['prop'] == pname:

            if obj['type'] == FieldType.LIST:
                collect = getattr(getattr(blocktool, bname), obj['prop'])

                arr = []
                for item in list(collect):
                    arr.append(item.value)

                b3d_obj[obj['prop']] = arr

def set_all_objs_by_type(context, b3d_obj, zclass):
    set_objs_by_type(context, b3d_obj, zclass)

# def setObjsDefaultByType(context, b3d_obj, zclass):

def set_objs_by_type(context, b3d_obj, zclass):
    attrs = [obj for obj in zclass.__dict__.keys() if not obj.startswith('__')]

    bname, bnum = BlockClassHandler.get_mytool_block_name_by_class(zclass)
    blocktool = context.scene.block_tool
    for b_attr in attrs:
        obj = zclass.__dict__[b_attr]
        if obj['type'] != FieldType.SPHERE_EDIT:
            # if getattr(getattr(mytool, bname), "show_"+obj['prop']) is not None \
            #     and getattr(getattr(mytool, bname), "show_"+obj['prop']):

                if obj['type'] == FieldType.FLOAT or obj['type'] == FieldType.RAD:
                    b3d_obj[obj['prop']] = float(getattr(getattr(blocktool, bname), obj['prop']))

                elif obj['type'] == FieldType.INT:
                    b3d_obj[obj['prop']] = int(getattr(getattr(blocktool, bname), obj['prop']))

                # elif obj['type'] == FieldType.MATERIAL_IND:
                #     b3d_obj[obj['prop']] = int(getattr(getattr(mytool, bname), obj['prop']))

                elif obj['type'] == FieldType.STRING:
                    b3d_obj[obj['prop']] = str(getattr(getattr(blocktool, bname), obj['prop']))

                # elif obj['type'] == FieldType.SPACE_NAME \
                # or obj['type'] == FieldType.REFERENCEABLE:
                #     b3d_obj[obj['prop']] = str(getattr(getattr(mytool, bname), obj['prop']))

                elif obj['type'] == FieldType.ENUM:

                    if obj['subtype'] == FieldType.INT:
                        b3d_obj[obj['prop']] = int(getattr(getattr(blocktool, bname), obj['prop']))

                    elif obj['subtype'] == FieldType.STRING:
                        b3d_obj[obj['prop']] = str(getattr(getattr(blocktool, bname), obj['prop']))

                    elif obj['subtype'] == FieldType.FLOAT:
                        b3d_obj[obj['prop']] = float(getattr(getattr(blocktool, bname), obj['prop']))

                elif obj['type'] == FieldType.ENUM_DYN:
                    b3d_obj[obj['prop']] = str(getattr(getattr(blocktool, bname), obj['prop']))

                elif obj['type'] == FieldType.COORD:
                    xyz = getattr(getattr(blocktool, bname), obj['prop'])
                    b3d_obj[obj['prop']] = (xyz[0],xyz[1],xyz[2])

                elif obj['type'] == FieldType.LIST:
                    collect = getattr(getattr(blocktool, bname), obj['prop'])

                    arr = []
                    for item in list(collect):
                        arr.append(item.value)

                    b3d_obj[obj['prop']] = arr

                else:
                    b3d_obj[obj['prop']] = getattr(getattr(blocktool, bname), obj['prop'])

def get_from_attributes(context, obj, attrs, bname, index):

    blocktool = context.scene.block_tool

    if getattr(getattr(blocktool, bname), "show_"+obj['prop']) is not None \
        and getattr(getattr(blocktool, bname), "show_"+obj['prop']):

        if obj['type'] == FieldType.FLOAT:
            getattr(blocktool, bname)[obj['prop']] = float(getattr(attrs[index], "value"))

        elif obj['type'] == FieldType.COORD:
            getattr(blocktool, bname)[obj['prop']] = getattr(attrs[index], "vector")

        elif obj['type'] == FieldType.INT:
            getattr(blocktool, bname)[obj['prop']] = int(getattr(attrs[index], "value"))

        elif obj['type'] == FieldType.V_FORMAT:
            v_format = getattr(attrs[index], "value") ^ 1
            triang_offset = v_format & 0b10000000
            use_uv = v_format & 0b10
            use_normals = v_format & 0b10000 and v_format & 0b100000
            normal_flag = v_format & 1

            getattr(blocktool, bname)[f'{obj["prop"]}_triang_offset'] = triang_offset
            getattr(blocktool, bname)[f'{obj["prop"]}_use_uvs'] = use_uv
            getattr(blocktool, bname)[f'{obj["prop"]}_use_normals'] = use_normals
            getattr(blocktool, bname)[f'{obj["prop"]}_normal_flag'] = normal_flag

def set_from_attributes(context, obj, attrs, bname, index):

    blocktool = context.scene.block_tool

    if getattr(getattr(blocktool, bname), "show_"+obj['prop']) is not None \
        and getattr(getattr(blocktool, bname), "show_"+obj['prop']):

        if obj['type'] == FieldType.FLOAT:
            attrs[index].value = getattr(blocktool, bname)[obj['prop']]

        elif obj['type'] == FieldType.INT:
            attrs[index].value = getattr(blocktool, bname)[obj['prop']]

        elif obj['type'] == FieldType.COORD:
            attrs[index].vector = getattr(blocktool, bname)[obj['prop']]

        elif obj['type'] == FieldType.V_FORMAT:
            value = 0
            triang_offset = getattr(blocktool, bname)[f'{obj["prop"]}_triang_offset']
            use_uv = getattr(blocktool, bname)[f'{obj["prop"]}_use_uvs']
            use_normals = getattr(blocktool, bname)[f'{obj["prop"]}_use_normals']
            normal_flag = getattr(blocktool, bname)[f'{obj["prop"]}_normal_flag']

            if triang_offset:
                value = value ^ 0b10000000
            if use_uv:
                value = value ^ 0b10
            if use_normals:
                value = value ^ 0b110000
            if normal_flag:
                value = value ^ 0b1

            value = value ^ 1

            attrs[index].value = value

def get_per_face_by_type(context, b3d_obj, zclass):
    zattrs = [obj for obj in zclass.__dict__.keys() if not obj.startswith('__')]

    bname, bnum = BlockClassHandler.get_mytool_block_name_by_class(zclass)

    mesh = b3d_obj.data
    bpy.ops.object.mode_set(mode = 'OBJECT')
    polygons = get_polygons_by_selected_vertices(b3d_obj)
    indexes = [cn.index for cn in polygons]

    if len(indexes) > 0:
        index = indexes[0]
        for b_attr in zattrs:
            obj = zclass.__dict__[b_attr]
            attrs = mesh.attributes[obj['prop']].data
            get_from_attributes(context, obj, attrs, bname, index)

    bpy.ops.object.mode_set(mode = 'EDIT')

def get_per_vertex_by_type(context, b3d_obj, zclass):
    zattrs = [obj for obj in zclass.__dict__.keys() if not obj.startswith('__')]

    bname, bnum = BlockClassHandler.get_mytool_block_name_by_class(zclass)

    mesh = b3d_obj.data
    bpy.ops.object.mode_set(mode = 'OBJECT')
    vertices = get_selected_vertices(b3d_obj)
    indexes = [cn.index for cn in vertices]

    if len(indexes) > 0:
        index = indexes[0]
        for b_attr in zattrs:
            obj = zclass.__dict__[b_attr]
            attrs = mesh.attributes[obj['prop']].data
            get_from_attributes(context, obj, attrs, bname, index)

    bpy.ops.object.mode_set(mode = 'EDIT')

def set_per_vertex_by_type(context, b3d_obj, zclass):
    zattrs = [obj for obj in zclass.__dict__.keys() if not obj.startswith('__')]

    bname, bnum = BlockClassHandler.get_mytool_block_name_by_class(zclass)

    mesh = b3d_obj.data

    bpy.ops.object.mode_set(mode = 'OBJECT')
    vertices = get_selected_vertices(b3d_obj)
    indexes = [cn.index for cn in vertices]

    for index in indexes:
        for b_attr in zattrs:
            obj = zclass.__dict__[b_attr]
            attrs = mesh.attributes[obj['prop']].data
            set_from_attributes(context, obj, attrs, bname, index)

    bpy.ops.object.mode_set(mode = 'EDIT')

def set_per_face_by_type(context, b3d_obj, zclass):
    zattrs = [obj for obj in zclass.__dict__.keys() if not obj.startswith('__')]

    bname, bnum = BlockClassHandler.get_mytool_block_name_by_class(zclass)

    mesh = b3d_obj.data

    bpy.ops.object.mode_set(mode = 'OBJECT')
    polygons = get_polygons_by_selected_vertices(b3d_obj)
    indexes = [cn.index for cn in polygons]

    for index in indexes:
        for b_attr in zattrs:
            obj = zclass.__dict__[b_attr]
            attrs = mesh.attributes[obj['prop']].data
            set_from_attributes(context, obj, attrs, bname, index)

    bpy.ops.object.mode_set(mode = 'EDIT')

def create_custom_attribute(mesh, values, zclass, zobj):
    ctype = BlockClassHandler.get_block_type_from_bclass(zclass)
    domain = ''
    if ctype == 'Pvb':
        domain = 'POINT'
    elif ctype == 'Pfb':
        domain = 'FACE'

    if zobj['type'] == FieldType.FLOAT:
        ztype = 'FLOAT'
        mesh.attributes.new(name=zobj['prop'], type=ztype, domain=domain)
        attr = mesh.attributes[zobj['prop']].data
        for i in range(len(attr)):
            setattr(attr[i], "value", values[i])

    elif zobj['type'] == FieldType.COORD:
        ztype = 'FLOAT_VECTOR'
        mesh.attributes.new(name=zobj['prop'], type=ztype, domain=domain)
        attr = mesh.attributes[zobj['prop']].data
        for i in range(len(attr)):
            setattr(attr[i], "vector", values[i])

    elif zobj['type'] == FieldType.INT:
        ztype = 'INT'
        mesh.attributes.new(name=zobj['prop'], type=ztype, domain=domain)
        attr = mesh.attributes[zobj['prop']].data
        for i in range(len(attr)):
            setattr(attr[i], "value", values[i])

    elif zobj['type'] == FieldType.V_FORMAT:
        ztype = 'INT'
        mesh.attributes.new(name=zobj['prop'], type=ztype, domain=domain)
        attr = mesh.attributes[zobj['prop']].data
        for i in range(len(attr)):
            setattr(attr[i], "value", values[i])

