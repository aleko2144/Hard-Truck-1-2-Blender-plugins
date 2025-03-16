import bpy

from ..compatibility import(
    get_ui_region,
    get_active_object
)

from ..common import (
    panel_logger
)

from .. import consts

from .common import (
    is_root_obj
)
from .ui_utils import (
    draw_common,
    draw_fields_by_type,
)

from .scripts import (
    apply_remove_transforms,
    hide_lod,
    show_lod,
    show_conditionals,
    hide_conditionals,
    show_hide_obj_by_type,
    get_objs_by_type,
    set_objs_by_type,
    get_per_face_by_type,
    set_per_face_by_type,
    get_per_vertex_by_type,
    set_per_vertex_by_type,
    show_hide_sphere,
    get_obj_by_prop,
    set_obj_by_prop,
    create_custom_attribute
)

from .classes import (
    BlockClassHandler
)

from .class_descr import (
    Blk020,Blk021,Blk023,
    Pfb008, Pfb028, Pfb035, Pvb008, Pvb035,
    Blk050,
    ResBlock
)

from .common import (
    get_current_res_index
)

from .custom_ui_list import (
    draw_list_controls
)


from bpy.props import (StringProperty,
                        BoolProperty,
                        IntProperty,
                        FloatProperty,
                        EnumProperty,
                        PointerProperty,
                        FloatVectorProperty,
                        CollectionProperty
                        )

from ..compatibility import (
    make_annotations,
    layout_split,
    get_context_collection_objects,
    get_or_create_collection,
    is_before_2_80,
    is_before_2_93,
    set_empty_type,
    set_empty_size,
    get_cursor_location
)

#Setup module logger
log = panel_logger

# ------------------------------------------------------------------------
#    store properties in the active scene
# ------------------------------------------------------------------------

def res_module_callback(scene, context):

    mytool = context.scene.my_tool
    res_modules = mytool.res_modules

    enum_properties = [("-1", "None", "")]

    enum_properties.extend([(str(i), cn.value, "") for i, cn in enumerate(res_modules)])

    return enum_properties

@make_annotations
class PanelSettings(bpy.types.PropertyGroup):

    res_modules = CollectionProperty(type=ResBlock)

    is_importing = bpy.props.BoolProperty(
        name ='isRESImporting',
        default = False
    )

    selected_res_module = EnumProperty(
        name="RES module",
        description="Selected RES module",
        items=res_module_callback
    )

    condition_group = bpy.props.IntProperty(
        name='Event number',
        description='Event number(object group), that should be shown/hidden. If -1, then all events are chosen. If event number is too big, closest suitable number is chosen.',
        default=-1,
        min=-1
    )

    block_name_string = bpy.props.StringProperty(
        name="Block name",
        default="",
        maxlen=30,
    )

    add_block_type_enum = bpy.props.EnumProperty(
        name="Block type",
        items= consts.blockTypeList
        )

    radius = bpy.props.FloatProperty(
        name = "Block rad",
        description = "Block rendering distance",
        default = 1.0,
        )

    cast_type_enum = bpy.props.EnumProperty(
        name="Cast type",
        items=[
            ('mesh', "Mesh", "Cast selected meshes to vertices(6,7,36,37) polygons blocks(8,35)"),
            ('colis3D', "3D collision", "Creates copy of selected mesh for 3D collision(23)"),
            ('colis2D', "2D collision", "Cast selected curve to 2D collision(20)"),
            ('way', "Transport path", "Cast selected curve to transport path(50)"),
        ]
    )

    vertex_block_enum = bpy.props.EnumProperty(
        name="Vertex block type",
        default = '37',
        items=[
            ('6', "6(no Normals)", "Block without normals. Mostly used in HT1"),
            ('7', "7(no Normals)", "Block without normals. Mostly used in HT2"),
            ('36', "36(with Normals)", "Block with normals. Mostly used in HT1"),
            ('37', "37(with Normals)", "Block with normals. Mostly used in HT2")
        ]
    )

    poly_block_enum = bpy.props.EnumProperty(
        name="Poly block type",
        default = '8',
        items=[
            ('8', "8(multiple textures)", "Block can use multiple materials per mesh. Casn use N-gons"),
            ('35', "35(single texture)", "Block use single materials per mesh. Use triangles")
        ]
    )


    add_blocks_enum = bpy.props.EnumProperty(
        name="Assembly type",
        items=[
                ('LOD_9', "Trigger(9)", "Trigger(9)"),
                ('LOD_10', "LOD(10)", "LOD(10)"),
                ('LOD_21', "Event(21)", "Event(21)"),
                #('07', "07", "Mesh (HT1)"),
                #('10', "10", "LOD"),
                #('12', "12", "Unk"),
                #('14', "14", "Car trigger"),
                #('18', "18", "Connector"),
                #('19', "19", "Room container"),
                #('20', "20", "2D collision"),
                #('21', "21", "Event container"),
                #('23', "23", "3D collision"),
                #('24', "24", "Locator"),
                #('28', "28", "2D-sprite"),
                #('33', "33", "Light source"),
                #('37', "37", "Mesh"),
                #('40', "40", "Object generator"),
               ]
        )

    lod_level_int = bpy.props.IntProperty(
        name='LOD level',
        description='LOD level',
        default=0,
        min=0
    )

    add_room_name_index_string = bpy.props.StringProperty(
        name="Room name",
        description="",
        default="aa_000",
        maxlen=30,
        )

    mirror_type_enum = bpy.props.EnumProperty(
        name="Block type",
        items=[ ('x', "x", ""),
                ('y', "y", ""),
                ('z', "z", ""),
               ]
        )

    parent_str = bpy.props.StringProperty(
        name ='Selected parent',
        description = 'New object will be parented to this object'
    )

    cast_copy = bpy.props.BoolProperty(
        name ='Create copy',
        description = 'Will be created copy of selected object and casted to B3D format',
        default = True
    )

# ------------------------------------------------------------------------
#    menus
# ------------------------------------------------------------------------

# class BasicMenu(bpy.types.Menu):
#     bl_idname = "OBJECT_MT_select_test"
#     bl_label = "Select"

#     def draw(self, context):
#         layout = self.layout

#         # built-in example operators
#         layout.operator("object.select_all", text="Select/Deselect All").action = 'TOGGLE'
#         layout.operator("object.select_all", text="Inverse").action = 'INVERT'
#         layout.operator("object.select_random", text="Random")

# ------------------------------------------------------------------------
#    operators / buttons
# ------------------------------------------------------------------------

class SetParentOperator(bpy.types.Operator):
    bl_idname = "wm.set_parent_operator"
    bl_label = "Set parent"

    def execute(self, context):
        scene = context.scene
        mytool = scene.my_tool

        if context.object is None:
            self.report({'INFO'}, "No object selected")
            return {'FINISHED'}

        mytool.parent_str = context.object.name

        return {'FINISHED'}


class SingleAddOperator(bpy.types.Operator):
    bl_idname = "wm.single_add_operator"
    bl_label = "Add block to scene"

    def execute(self, context):
        scene = context.scene
        mytool = scene.my_tool

        block_type = int(mytool.add_block_type_enum)

        cursor_pos = get_cursor_location()

        parent_obj = bpy.context.object

        object_name = mytool.block_name_string

        zclass = BlockClassHandler.get_class_def_by_type(block_type)

        # objects that are located in 0,0,0(technical empties)
        if block_type in [
            111,444,
            0,1,2,3,4,5,
            6,7,36,37, # vertexes
            # 8, 35 - polygons
            9,10,21,22, # groups
            11,12,13,14,15,16,17,18,19,
            # 20 - 2d collision
            # 23 - 3d collision
            # 28 - 2d sprite
            # 30 - portal
            # 24 - locator
            25,26,27,29,31,33,34,39,
            # 40 - generator
            51,52
        ]:
            b3d_obj = bpy.data.objects.new(object_name, None)
            b3d_obj.location=(0.0,0.0,0.0)
            b3d_obj[consts.BLOCK_TYPE] = block_type
            if parent_obj is not None and block_type != 111:
                b3d_obj.parent = parent_obj
            if block_type not in [111, 444, 0, 3, 8, 19]: # blocks without custom parameters
                set_objs_by_type(b3d_obj, zclass)
            get_context_collection_objects(context).link(b3d_obj)

            if block_type in [9,10,22,21]: #objects with subgroups

                group_cnt = 0
                if block_type in [9,10,21]:
                    group_cnt = 2
                elif block_type == 21:
                    group_cnt = b3d_obj[Blk021.GroupCnt.get_prop()]

                for i in range(group_cnt):
                    group = bpy.data.objects.new("GROUP_{}".format(i), None)
                    group.location=(0.0,0.0,0.0)
                    group[consts.BLOCK_TYPE] = 444
                    group.parent = b3d_obj
                    get_context_collection_objects(context).link(group)

        elif block_type in [24, 40, 51, 52]: # empties which location is important

            b3d_obj = bpy.data.objects.new(object_name, None)
            b3d_obj.location=cursor_pos
            b3d_obj[consts.BLOCK_TYPE] = block_type
            if parent_obj is not None and block_type != 111:
                b3d_obj.parent = parent_obj
            if block_type not in [111, 444, 0, 3, 8, 19]: # blocks without custom parameters
                set_objs_by_type(b3d_obj, zclass)

            if block_type in [24, 52]:
                set_empty_type(b3d_obj, 'ARROWS')
            elif block_type == 40:
                set_empty_type(b3d_obj, 'SPHERE')
                set_empty_size(b3d_obj, 5)
            elif block_type == 51:
                set_empty_type(b3d_obj, 'PLAIN_AXES')

            get_context_collection_objects(context).link(b3d_obj)

        elif block_type in [28, 30]:

            sprite_center = cursor_pos

            l_vertexes = []

            if block_type == 28:
                l_vertexes = [
                    (0.0, -1.0, -1.0),
                    (0.0, -1.0, 1.0),
                    (0.0, 1.0, 1.0),
                    (0.0, 1.0, -1.0)
                ]
            elif block_type == 30:
                l_vertexes = [
                    (0.0, -10.0, -20.0),
                    (0.0, -10.0, 20.0),
                    (0.0, 10.0, 20.0),
                    (0.0, 10.0, -20.0)
                ]

            l_faces = [(0,1,2,3)]

            b3d_mesh = (bpy.data.meshes.new(object_name))
            b3d_mesh.from_pydata(l_vertexes,[],l_faces)

            b3d_obj = bpy.data.objects.new(object_name, b3d_mesh)
            b3d_obj.location=sprite_center
            b3d_obj[consts.BLOCK_TYPE] = block_type
            if parent_obj is not None and block_type != 111:
                b3d_obj.parent = parent_obj
            if block_type not in [111, 444, 0, 3, 8, 19]: # blocks without custom parameters
                set_objs_by_type(b3d_obj, zclass)
            get_context_collection_objects(context).link(b3d_obj)

        return {'FINISHED'}

class TemplateAddOperator(bpy.types.Operator):
    bl_idname = "wm.template_add_operator"
    bl_label = "Add block assembly to scene"

    def execute(self, context):
        scene = context.scene
        mytool = scene.my_tool

        block_type = mytool.add_blocks_enum

        cursor_pos = get_cursor_location()

        def type05(name, radius, add_name):
            object_name = name
            b3d_obj = bpy.data.objects.new(object_name, None)
            b3d_obj[consts.BLOCK_TYPE] = 5
            b3d_obj.location=cursor_pos
            b3d_obj['node_radius'] = radius
            b3d_obj['add_name'] = add_name
            bpy.context.scene.objects.link(b3d_obj)
            b3d_obj.select = True

        def type19(name):
            object_name = name
            b3d_obj = bpy.data.objects.new(object_name, None)
            b3d_obj[consts.BLOCK_TYPE] = 19
            b3d_obj.location=cursor_pos
            bpy.context.scene.objects.link(b3d_obj)
            b3d_obj.select = True

        if block_type == "room":
            type19("room_" + mytool.add_room_name_index_string)
            room = get_active_object()

            type05(("road_" + mytool.add_room_name_index_string), mytool.radius, ("hit_road_" + mytool.add_room_name_index_string))
            road = get_active_object()

            type05(("obj_" + mytool.add_room_name_index_string), mytool.radius, ("hit_obj_" + mytool.add_room_name_index_string))
            obj = get_active_object()

            hit_road = type05(("hit_road_" + mytool.add_room_name_index_string), 0, "")
            hit_obj = type05(("hit_obj_" + mytool.add_room_name_index_string), 0, "")

            bpy.ops.object.select_all(action='DESELECT')

            room.select = True
            road.select = True
            obj.select = True

            bpy.context.scene.objects.active = room

            bpy.ops.object.parent_set()

            bpy.ops.object.select_all(action='DESELECT')

        return {'FINISHED'}

class CastAddOperator(bpy.types.Operator):
    bl_idname = "wm.cast_add_operator"
    bl_label = "Cast to B3D"

    def execute(self, context):
        scene = context.scene
        mytool = scene.my_tool

        cursor_pos = get_cursor_location()

        cast_type = mytool.cast_type_enum
        parent_obj = bpy.data.objects.get(mytool.parent_str)

        to_copy = int(mytool.cast_copy)

        if cast_type == 'mesh':
            vert_type = int(mytool.vertex_block_enum)
            poly_type = int(mytool.poly_block_enum)

            vertclass = BlockClassHandler.get_class_def_by_type(vert_type)
            polyclass = BlockClassHandler.get_class_def_by_type(poly_type)

            #creating vertex block
            vert_obj = bpy.data.objects.new(consts.EMPTY_NAME, None)
            vert_obj.location=(0.0,0.0,0.0)
            vert_obj[consts.BLOCK_TYPE] = vert_type
            vert_obj.parent = parent_obj
            set_objs_by_type(vert_obj, vertclass)
            get_context_collection_objects(context).link(vert_obj)

            # creating poly blocks
            for poly_obj in context.selected_objects:
                if poly_obj.type == 'MESH':

                    if to_copy:
                        new_obj = poly_obj.copy()
                        new_obj.data = poly_obj.data.copy()
                        new_obj[consts.BLOCK_TYPE] = poly_type
                        new_obj.parent = vert_obj
                        if poly_type != 8:
                            set_objs_by_type(new_obj, polyclass)

                        formats = [2]*len(new_obj.data.polygons)
                        if poly_type == 8:
                            create_custom_attribute(new_obj.data, formats, Pfb008, Pfb008.Format_Flags)
                        elif poly_type == 35:
                            create_custom_attribute(new_obj.data, formats, Pfb035, Pfb035.Format_Flags)

                        get_context_collection_objects(context).link(new_obj)

                        log.info("Created new B3D object: {}.".format(new_obj.name))
                    else:
                        poly_obj[consts.BLOCK_TYPE] = poly_type
                        poly_obj.parent = vert_obj
                        if poly_type != 8:
                            set_objs_by_type(poly_obj, polyclass)
                        formats = [2]*len(poly_obj.data.polygons)
                        if poly_type == 8:
                            create_custom_attribute(poly_obj.data, formats, Pfb008, Pfb008.Format_Flags)
                        elif poly_type == 35:
                            create_custom_attribute(poly_obj.data, formats, Pfb035, Pfb035.Format_Flags)

                        log.info("Cast existing B3D object: {}.".format(poly_obj.name))

                else:
                    log.info("Selected object {} is not Mesh. Changes not applied.".format(poly_obj.name))

        elif cast_type == 'colis3D':

            for poly_obj in context.selected_objects:
                if poly_obj.type == 'MESH':

                    if to_copy:
                        new_obj = poly_obj.copy()
                        new_obj.data = poly_obj.data.copy()
                        new_obj[consts.BLOCK_TYPE] = 23
                        new_obj.parent = parent_obj
                        set_objs_by_type(new_obj, Blk023)
                        get_context_collection_objects(context).link(new_obj)
                        log.info("Created new B3D 3d collision: {}.".format(new_obj.name))
                    else:
                        poly_obj[consts.BLOCK_TYPE] = 23
                        poly_obj.parent = parent_obj
                        set_objs_by_type(poly_obj, Blk023)
                        log.info("Cast existing object to B3D 3d collision: {}.".format(poly_obj.name))
                else:
                    log.info("Selected object {} is not Mesh. Changes not applied.".format(poly_obj.name))

        elif cast_type == 'colis2D':

            for poly_obj in context.selected_objects:
                if poly_obj.type == 'CURVE':

                    if to_copy:
                        new_obj = poly_obj.copy()
                        new_obj.data = poly_obj.data.copy()
                        new_obj[consts.BLOCK_TYPE] = 20
                        new_obj.data.bevel_depth = 0
                        new_obj.data.extrude = 10
                        new_obj.parent = parent_obj
                        set_objs_by_type(new_obj, Blk020)
                        get_context_collection_objects(context).link(new_obj)
                        log.info("Created new B3D 2d colision: {}.".format(new_obj.name))
                    else:
                        poly_obj[consts.BLOCK_TYPE] = 20
                        poly_obj.data.bevel_depth = 0
                        poly_obj.data.extrude = 10
                        poly_obj.parent = parent_obj
                        set_objs_by_type(poly_obj, Blk020)
                        log.info("Cast exiting object to B3D 2d colision: {}.".format(poly_obj.name))

                else:
                    log.info("Selected object {} is not Curve. Changes not applied.".format(poly_obj.name))

        elif cast_type == 'way':

            for poly_obj in context.selected_objects:
                if poly_obj.type == 'CURVE':

                    if to_copy:
                        new_obj = poly_obj.copy()
                        new_obj.data = poly_obj.data.copy()
                        new_obj[consts.BLOCK_TYPE] = 50
                        new_obj.data.bevel_depth = 0.3
                        new_obj.data.bevel_mode = 'ROUND'
                        new_obj.parent = parent_obj
                        set_objs_by_type(new_obj, Blk050)
                        get_context_collection_objects(context).link(new_obj)
                        log.info("Created new WAY Path: {}.".format(new_obj.name))
                    else:
                        poly_obj[consts.BLOCK_TYPE] = 50
                        poly_obj.data.bevel_depth = 0.3
                        poly_obj.data.bevel_mode = 'ROUND'
                        poly_obj.parent = parent_obj
                        set_objs_by_type(poly_obj, Blk050)
                        log.info("Cast existing object to WAY Path: {}.".format(poly_obj.name))

                else:
                    log.info("Selected object {} is not Curve. Changes not applied.".format(poly_obj.name))


        return {'FINISHED'}

class GetVertexValuesOperator(bpy.types.Operator):
    bl_idname = "wm.get_vertex_values_operator"
    bl_label = "Get block values"

    def execute(self, context):
        b3d_obj = get_active_object()
        block_type = b3d_obj[consts.BLOCK_TYPE]

        if block_type == 8:
            get_per_vertex_by_type(b3d_obj, Pvb008)
        elif block_type == 35:
            get_per_vertex_by_type(b3d_obj, Pvb035)

        return {'FINISHED'}

class GetFaceValuesOperator(bpy.types.Operator):
    bl_idname = "wm.get_face_values_operator"
    bl_label = "Get block values"

    def execute(self, context):
        b3d_obj = get_active_object()
        block_type = b3d_obj[consts.BLOCK_TYPE]

        if block_type == 8:
            get_per_face_by_type(b3d_obj, Pfb008)
        elif block_type == 28:
            get_per_face_by_type(b3d_obj, Pfb028)
        elif block_type == 35:
            get_per_face_by_type(b3d_obj, Pfb035)

        return {'FINISHED'}

class GetValuesOperator(bpy.types.Operator):
    bl_idname = "wm.get_block_values_operator"
    bl_label = "Get block values"

    def execute(self, context):
        scene = context.scene
        mytool = scene.my_tool

        b3d_obj = bpy.context.object
        block_type = b3d_obj[consts.BLOCK_TYPE]

        zclass = BlockClassHandler.get_class_def_by_type(block_type)

        if zclass is not None:
            get_objs_by_type(b3d_obj, zclass)

        return {'FINISHED'}

@make_annotations
class GetPropValueOperator(bpy.types.Operator):
    bl_idname = "wm.get_prop_value_operator"
    bl_label = "Get param value"

    pname = StringProperty()

    def execute(self, context):
        scene = context.scene
        mytool = scene.my_tool

        b3d_obj = bpy.context.object
        block_type = b3d_obj[consts.BLOCK_TYPE]

        zclass = BlockClassHandler.get_class_def_by_type(block_type)

        if zclass is not None:
            get_obj_by_prop(b3d_obj, zclass, self.pname)

        return {'FINISHED'}

class SetFaceValuesOperator(bpy.types.Operator):
    bl_idname = "wm.set_face_values_operator"
    bl_label = "Save block values"

    def execute(self, context):
        curtype = bpy.context.object[consts.BLOCK_TYPE]
        objects = [cn for cn in bpy.context.selected_objects if cn[consts.BLOCK_TYPE] is not None and cn[consts.BLOCK_TYPE] == curtype]

        for i in range(len(objects)):

            b3d_obj = objects[i]
            block_type = b3d_obj[consts.BLOCK_TYPE]

            if block_type == 8:
                set_per_face_by_type(b3d_obj, Pfb008)
            elif block_type == 28:
                set_per_face_by_type(b3d_obj, Pfb028)
            elif block_type == 35:
                set_per_face_by_type(b3d_obj, Pfb035)

        return {'FINISHED'}

class SetVertexValuesOperator(bpy.types.Operator):
    bl_idname = "wm.set_vertex_values_operator"
    bl_label = "Save block values"

    def execute(self, context):
        curtype = bpy.context.object[consts.BLOCK_TYPE]
        objects = [cn for cn in bpy.context.selected_objects if cn[consts.BLOCK_TYPE] is not None and cn[consts.BLOCK_TYPE] == curtype]

        for i in range(len(objects)):

            b3d_obj = objects[i]
            block_type = b3d_obj[consts.BLOCK_TYPE]

            if block_type == 8:
                set_per_vertex_by_type(b3d_obj, Pvb008)
            elif block_type == 35:
                set_per_vertex_by_type(b3d_obj, Pvb035)

        return {'FINISHED'}

class SetValuesOperator(bpy.types.Operator):
    bl_idname = "wm.set_block_values_operator"
    bl_label = "Save block values"

    def execute(self, context):
        scene = context.scene
        mytool = scene.my_tool

        block_type = ''

        active_obj = bpy.context.object

        curtype = active_obj[consts.BLOCK_TYPE]

        objects = [cn for cn in bpy.context.selected_objects if cn[consts.BLOCK_TYPE] is not None and cn[consts.BLOCK_TYPE] == curtype]

        for i in range(len(objects)):

            b3d_obj = objects[i]

            if consts.BLOCK_TYPE in b3d_obj:
                block_type = b3d_obj[consts.BLOCK_TYPE]
            else:
                block_type = 0

            b3d_obj[consts.BLOCK_TYPE] = block_type

            zclass = BlockClassHandler.get_class_def_by_type(block_type)

            if zclass is not None:
                set_objs_by_type(b3d_obj, zclass)

        return {'FINISHED'}

@make_annotations
class SetPropValueOperator(bpy.types.Operator):
    bl_idname = "wm.set_prop_value_operator"
    bl_label = "Save param value"

    pname = StringProperty()

    def execute(self, context):
        scene = context.scene
        mytool = scene.my_tool

        b3d_obj = bpy.context.object
        block_type = b3d_obj[consts.BLOCK_TYPE]

        zclass = BlockClassHandler.get_class_def_by_type(block_type)

        if zclass is not None:
            set_obj_by_prop(b3d_obj, zclass, self.pname)

        return {'FINISHED'}

class DelValuesOperator(bpy.types.Operator):
    bl_idname = "wm.del_block_values_operator"
    bl_label = "Delete block values"

    def execute(self, context):
        scene = context.scene
        mytool = scene.my_tool

        #b3d_obj = get_active_object()

        for i in range(len(bpy.context.selected_objects)):

            b3d_obj = bpy.context.selected_objects[i]

            if consts.BLOCK_TYPE in b3d_obj:
                del b3d_obj[consts.BLOCK_TYPE]

        return {'FINISHED'}

class FixUVOperator(bpy.types.Operator):
    bl_idname = "wm.fix_uv_operator"
    bl_label = "Fix UV for export"

    def execute(self, context):

        for i in range(len(bpy.context.selected_objects)):

            b3d_obj = bpy.context.selected_objects[i]

            bpy.ops.object.mode_set(mode = 'EDIT')

            context = bpy.context
            obj = context.edit_object
            me = obj.data
            bm = bmesh.from_edit_mesh(me)
            # old seams
            old_seams = [e for e in bm.edges if e.seam]
            # unmark
            for e in old_seams:
                e.seam = False
            # mark seams from uv islands
            bpy.ops.uv.seams_from_islands()
            seams = [e for e in bm.edges if e.seam]
            # split on seams
            print(seams)
            print("salo 111")
            bmesh.ops.split_edges(bm, edges=seams)
            # re instate old seams.. could clear new seams.
            for e in old_seams:
                e.seam = True
            bmesh.update_edit_mesh(me)

            boundary_seams = [e for e in bm.edges if e.seam and e.is_boundary]

            bpy.ops.object.mode_set(mode = 'OBJECT')

        return {'FINISHED'}

class FixVertsOperator(bpy.types.Operator):
    bl_idname = "wm.fix_verts_operator"
    bl_label = "Fix mesh for export"

    def execute(self, context):

        for i in range(len(bpy.context.selected_objects)):

            b3d_obj = bpy.context.selected_objects[i]

            bpy.ops.object.mode_set(mode = 'EDIT')
            bpy.ops.mesh.select_mode(type="FACE")
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.mesh.select_all(action='INVERT')
            bpy.ops.mesh.select_mode(type="VERT")
            bpy.ops.mesh.select_all(action='INVERT')
            bpy.ops.mesh.delete(type='VERT')

            bpy.ops.object.mode_set(mode = 'OBJECT')

        return {'FINISHED'}

class MirrorAndFlipObjectsOperator(bpy.types.Operator):
    bl_idname = "wm.mirror_objects_operator"
    bl_label = "Mirror objects"

    def execute(self, context):
        scene = context.scene
        mytool = scene.my_tool

        x = False
        y = False
        z = False

        if (mytool.mirror_type_enum) == "x":
            x = True
        else:
            x = False

        if (mytool.mirror_type_enum) == "y":
            y = True
        else:
            y = False

        if (mytool.mirror_type_enum) == "z":
            z = True
        else:
            z = False

        for b3d_obj in context.selected_objects:
            if b3d_obj.type == 'MESH':
                #b3d_obj = bpy.context.selected_objects[i]
                bpy.ops.transform.mirror(constraint_axis=(x, y, z), constraint_orientation='GLOBAL')
                bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

                #if object.type == 'MESH':
                bpy.ops.object.mode_set(mode = 'EDIT')
                bpy.ops.mesh.select_mode(type="FACE")
                bpy.ops.mesh.select_all(action='DESELECT')
                bpy.ops.mesh.select_all(action='INVERT')
                bpy.ops.mesh.flip_normals()
                bpy.ops.mesh.select_all(action='DESELECT')
                bpy.ops.object.mode_set(mode = 'OBJECT')




        #bpy.ops.object.mode_set(mode = 'OBJECT')

        return {'FINISHED'}

class ApplyTransformsOperator(bpy.types.Operator):
    bl_idname = "wm.apply_transforms_operator"
    bl_label = "Arrange/Remove objects"
    bl_description = "Creates copies of objects and arrange them at places(24) specified in connector(18)"

    def execute(self, context):
        scene = context.scene
        mytool = scene.my_tool

        apply_remove_transforms(self)

        return {'FINISHED'}

class ShowHide2DCollisionsOperator(bpy.types.Operator):
    bl_idname = "wm.show_hide_2d_collisions_operator"
    bl_label = "Show/Hide 2D collisions"
    bl_description = "If all 2D collisions(20) are hidden, shows them. otherwise - hide."

    def execute(self, context):
        scene = context.scene
        mytool = scene.my_tool

        show_hide_obj_by_type(self, 20)

        return {'FINISHED'}

class ShowHideCollisionsOperator(bpy.types.Operator):
    bl_idname = "wm.show_hide_collisions_operator"
    bl_label = "Show/Hide collisions"
    bl_description = "If all 3d collisions(23) are hidden, shows them. otherwise - hide."

    def execute(self, context):
        scene = context.scene
        mytool = scene.my_tool

        show_hide_obj_by_type(self, 23)

        return {'FINISHED'}

class ShowHideRoomBordersOperator(bpy.types.Operator):
    bl_idname = "wm.show_hide_room_borders_operator"
    bl_label = "Show/Hide portals"
    bl_description = "If all portals(30) are hidden, shows them. Otherwise - hide."

    def execute(self, context):
        scene = context.scene
        mytool = scene.my_tool

        show_hide_obj_by_type(self, 30)

        return {'FINISHED'}

class ShowHideGeneratorsOperator(bpy.types.Operator):
    bl_idname = "wm.show_hide_generator_operator"
    bl_label = "Show/Hide generator blocks"
    bl_description = "If all generator blocks(40) are hidden, shows them. Otherwise - hide."

    def execute(self, context):
        scene = context.scene
        mytool = scene.my_tool

        show_hide_obj_by_type(self, 40)

        return {'FINISHED'}

class ShowLODOperator(bpy.types.Operator):
    bl_idname = "wm.show_lod_operator"
    bl_label = "Show LOD"
    bl_description = "Shows LOD(10) of selected object. " + \
                    "If there is no active object, show LOD of all scene objects."

    def execute(self, context):
        scene = context.scene
        mytool = scene.my_tool

        objs = context.selected_objects
        if not len(objs):
            objs = [cn for cn in bpy.data.objects if is_root_obj(cn)]

        for obj in objs:
            show_lod(obj)
        self.report({'INFO'}, "{} LOD objects(block 10) are shown".format(len(objs)))

        return {'FINISHED'}

class HideLODOperator(bpy.types.Operator):
    bl_idname = "wm.hide_lod_operator"
    bl_label = "Hide LOD"
    bl_description = "Hides LOD(10) of selected object. " + \
                    "If there is no active object, hide LOD of all scene objects."

    def execute(self, context):
        scene = context.scene
        mytool = scene.my_tool

        objs = context.selected_objects
        if not len(objs):
            objs = [cn for cn in bpy.data.objects if is_root_obj(cn)]

        for obj in objs:
            hide_lod(obj)
        self.report({'INFO'}, "{} LOD objects(block 10) are hidden".format(len(objs)))

        return {'FINISHED'}

@make_annotations
class ShowConditionalsOperator(bpy.types.Operator):
    bl_idname = "wm.show_conditional_operator"
    bl_label = "Show events"
    bl_description = "Show event from selected event block(21). " + \
                    "If there is no active event block, show event of all scene event objects(21)"

    group  = bpy.props.IntProperty()

    def execute(self, context):
        scene = context.scene
        mytool = scene.my_tool

        objs = context.selected_objects
        if not len(objs):
            objs = [cn for cn in bpy.data.objects if is_root_obj(cn)]

        for obj in objs:
            show_conditionals(obj, self.group)
        self.report({'INFO'}, "{} Conditional objects(block 21) are shown".format(len(objs)))


        return {'FINISHED'}

@make_annotations
class HideConditionalsOperator(bpy.types.Operator):
    bl_idname = "wm.hide_conditional_operator"
    bl_label = "Hide events"
    bl_description = "Hide event from selected event block(21). " + \
                    "If there is no active event block, hide event of all scene event objects(21)"

    group  = bpy.props.IntProperty()

    def execute(self, context):
        scene = context.scene
        mytool = scene.my_tool

        objs = context.selected_objects
        if not len(objs):
            objs = [cn for cn in bpy.data.objects if is_root_obj(cn)]

        for obj in objs:
            hide_conditionals(obj, self.group)
        self.report({'INFO'}, "{} Conditional objects(block 21) are hidden".format(len(objs)))

        return {'FINISHED'}

@make_annotations
class ShowHideSphereOperator(bpy.types.Operator):
    bl_idname = "wm.show_hide_sphere_operator"
    bl_label = "Show/Hide sphere"
    bl_description = "Shows/Hides sphere"

    pname = bpy.props.StringProperty()

    def execute(self, context):
        scene = context.scene
        mytool = scene.my_tool

        obj = context.object

        show_hide_sphere(context, obj, self.pname)

        self.report({'INFO'}, "Sphere shown or hidden")

        return {'FINISHED'}

# ------------------------------------------------------------------------
# panels
# ------------------------------------------------------------------------

class OBJECT_PT_b3d_add_panel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_b3d_add_panel"
    bl_label = "Block add"
    bl_space_type = "VIEW_3D"
    bl_region_type = get_ui_region()
    bl_category = "b3d Tools"
    #bl_context = "objectmode"

    @classmethod
    def poll(self,context):
        return context.object is not None

    def draw(self, context):
        layout = self.layout
        mytool = context.scene.my_tool

        b3d_obj = bpy.context.object

        object_name = '' if b3d_obj is None else b3d_obj.name

        box = layout.box()
        box.label(text="Selected object: " + str(object_name))

class OBJECT_PT_b3d_single_add_panel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_b3d_single_add_panel"
    bl_label = "Single block"
    bl_parent_id = "OBJECT_PT_b3d_add_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = get_ui_region()
    bl_category = "b3d Tools"
    #bl_context = "objectmode"

    @classmethod
    def poll(self,context):
        return context.object is not None

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mytool = scene.my_tool
        # print(type(mytool))
        # print(bpy.types.Scene.my_tool)
        # print(dir(bpy.types.Scene.my_tool))
        # print(dir(context.scene.my_tool))
        block_type = int(mytool.add_block_type_enum)

        self.layout.label(text="Block type:")
        layout.prop(mytool, "add_block_type_enum", text="")
        layout.prop(mytool, "block_name_string")

        zclass = BlockClassHandler.get_class_def_by_type(block_type)

        if zclass is not None:
            draw_fields_by_type(self, zclass)

        layout.operator("wm.single_add_operator")

class OBJECT_PT_b3d_template_add_panel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_b3d_template_add_panel"
    bl_label = "Block template"
    bl_parent_id = "OBJECT_PT_b3d_add_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = get_ui_region()
    bl_category = "b3d Tools"
    #bl_context = "objectmode"

    @classmethod
    def poll(self,context):
        return context.object is not None

    def draw(self, context):
        layout = self.layout
        mytool = context.scene.my_tool

        block_type = mytool.add_blocks_enum

        layout.prop(mytool, "add_blocks_enum")

        if block_type == "LOD_9":

            layout.prop(mytool, "lod_level_int")

            zclass = BlockClassHandler.get_class_def_by_type(9)
            draw_fields_by_type(self, zclass)

        elif block_type == "LOD_10":

            layout.prop(mytool, "lod_level_int")

            zclass = BlockClassHandler.get_class_def_by_type(10)
            draw_fields_by_type(self, zclass)

        elif block_type == "LOD_21":

            layout.prop(mytool, "lod_level_int")

            zclass = BlockClassHandler.get_class_def_by_type(21)
            draw_fields_by_type(self, zclass)

            # layout.prop(mytool, "add_room_name_index_string")
            # layout.prop(mytool, "radius")


        layout.operator("wm.template_add_operator")

class OBJECT_PT_b3d_cast_add_panel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_b3d_cast_add_panel"
    bl_label = "Cast to B3D object"
    bl_parent_id = "OBJECT_PT_b3d_add_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = get_ui_region()
    bl_category = "b3d Tools"
    #bl_context = "objectmode"

    @classmethod
    def poll(self,context):
        return context.object is not None

    def draw(self, context):
        layout = self.layout
        mytool = context.scene.my_tool

        split = layout_split(layout, 0.75)
        c = split.column()
        c.prop(mytool, 'parent_str')
        c = split.column()
        c.operator("wm.set_parent_operator")

        layout.prop(mytool, "cast_type_enum")
        cast_type = mytool.cast_type_enum
        layout.prop(mytool, "cast_copy")
        box = layout.box()
        if cast_type == 'mesh':
            box.prop(mytool, "vertex_block_enum")
            box.prop(mytool, "poly_block_enum")

        box.operator("wm.cast_add_operator")

class OBJECT_PT_b3d_pfb_edit_panel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_b3d_pfb_edit_panel"
    bl_label = "Multiple polygons edit"
    bl_parent_id = "OBJECT_PT_b3d_edit_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = get_ui_region()
    bl_category = "b3d Tools"
    #bl_context = "objectmode"

    @classmethod
    def poll(self,context):
        b3d_obj = bpy.context.object
        if b3d_obj is not None: 
            if consts.BLOCK_TYPE in b3d_obj:
                block_type = b3d_obj[consts.BLOCK_TYPE]
            else:
                block_type = None

            return (context.object is not None) and block_type in [8, 28, 35]

    def draw(self, context):
        layout = self.layout
        mytool = context.scene.my_tool

        b3d_obj = bpy.context.object

        if b3d_obj is not None:

            if consts.BLOCK_TYPE in b3d_obj:
                block_type = b3d_obj[consts.BLOCK_TYPE]
            else:
                block_type = None

            if block_type == 8:
                draw_fields_by_type(self, Pfb008)
            if block_type == 28:
                draw_fields_by_type(self, Pfb028)
            if block_type == 35:
                draw_fields_by_type(self, Pfb035)

            if block_type in [8, 28, 35]:
                layout.operator("wm.get_face_values_operator")
                layout.operator("wm.set_face_values_operator")

class OBJECT_PT_b3d_pvb_edit_panel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_b3d_pvb_edit_panel"
    bl_label = "Multiple vertexes edit"
    bl_parent_id = "OBJECT_PT_b3d_edit_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = get_ui_region()
    bl_category = "b3d Tools"
    #bl_context = "objectmode"

    @classmethod
    def poll(self,context):
        #Disabled for now. More analyze needed.
        return False

        b3d_obj = bpy.context.object
        if consts.BLOCK_TYPE in b3d_obj:
            block_type = b3d_obj[consts.BLOCK_TYPE]
        else:
            block_type = None

        return (context.object is not None) and block_type in [8, 28, 35]

    def draw(self, context):
        layout = self.layout
        mytool = context.scene.my_tool

        b3d_obj = bpy.context.object

        if b3d_obj is not None:

            if consts.BLOCK_TYPE in b3d_obj:
                block_type = b3d_obj[consts.BLOCK_TYPE]
            else:
                block_type = None

            if block_type == 8:
                draw_fields_by_type(self, Pvb008)
            if block_type == 35:
                draw_fields_by_type(self, Pvb035)

            if block_type in [8, 28, 35]:
                layout.operator("wm.get_vertex_values_operator")
                layout.operator("wm.set_vertex_values_operator")

class OBJECT_PT_b3d_edit_panel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_b3d_edit_panel"
    bl_label = "Block edit"
    bl_space_type = "VIEW_3D"
    bl_region_type = get_ui_region()
    bl_category = "b3d Tools"
    #bl_context = "objectmode"

    @classmethod
    def poll(self,context):
        return context.object is not None

    def draw(self, context):
        layout = self.layout
        mytool = context.scene.my_tool

        b3d_obj = bpy.context.object
        if b3d_obj is not None:
            draw_common(self, b3d_obj)

class OBJECT_PT_b3d_pob_edit_panel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_b3d_pob_edit_panel"
    bl_label = "Multiple block edit"
    bl_parent_id = "OBJECT_PT_b3d_edit_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = get_ui_region()
    bl_category = "b3d Tools"
    #bl_context = "objectmode"

    @classmethod
    def poll(self,context):
        return context.object is not None

    def draw(self, context):
        layout = self.layout
        mytool = context.scene.my_tool

        block_type = ''
        #for i in range(len(bpy.context.selected_objects)):

        b3d_obj = bpy.context.object

        # if len(bpy.context.selected_objects):
        #     for i in range(1):
        if b3d_obj is not None:

            if consts.BLOCK_TYPE in b3d_obj:
                block_type = b3d_obj[consts.BLOCK_TYPE]
            # else:
            #     block_type = None

                len_str = str(len(b3d_obj.children))

                zclass = BlockClassHandler.get_class_def_by_type(block_type)

                layout.operator("wm.get_block_values_operator")
                layout.operator("wm.set_block_values_operator")

                if zclass is not None:
                    draw_fields_by_type(self, zclass)

            # else:
            #     self.layout.label(text="Выбранный объект не имеет типа.")
            #     self.layout.label(text="Чтобы указать его, нажмите на кнопку сохранения настроек.")

            # layout.operator("wm.del_block_values_operator")
            # layout.operator("wm.fix_uv_operator")
            # layout.operator("wm.fix_verts_operator")

class OBJECT_PT_b3d_pob_single_edit_panel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_b3d_pob_single_edit_panel"
    bl_label = "Single block edit"
    bl_parent_id = "OBJECT_PT_b3d_edit_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = get_ui_region()
    bl_category = "b3d Tools"
    #bl_context = "objectmode"

    @classmethod
    def poll(self,context):
        return context.object is not None

    def draw(self, context):
        layout = self.layout
        mytool = context.scene.my_tool

        #for i in range(len(bpy.context.selected_objects)):

        b3d_obj = bpy.context.object

        # if len(bpy.context.selected_objects):
        #     for i in range(1):
        if b3d_obj is not None:

            if consts.BLOCK_TYPE in b3d_obj:
                block_type = b3d_obj[consts.BLOCK_TYPE]
            # else:
            #     block_type = None

                len_str = str(len(b3d_obj.children))

                zclass = BlockClassHandler.get_class_def_by_type(block_type)

                if zclass is not None:
                    draw_fields_by_type(self, zclass, False)

            # else:
            #     self.layout.label(text="Выбранный объект не имеет типа.")
            #     self.layout.label(text="Чтобы указать его, нажмите на кнопку сохранения настроек.")

            # layout.operator("wm.del_block_values_operator")
            # layout.operator("wm.fix_uv_operator")
            # layout.operator("wm.fix_verts_operator")



class OBJECT_PT_b3d_func_panel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_b3d_func_panel"
    bl_label = "Additional options"
    bl_space_type = "VIEW_3D"
    bl_region_type = get_ui_region()
    bl_category = "b3d Tools"
    #bl_context = "objectmode"

    @classmethod
    def poll(self,context):
        return context.object is not None

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mytool = scene.my_tool


        # layout.prop(mytool, "mirror_type_enum")

        # layout.operator("wm.mirror_objects_operator")
        layout.operator("wm.apply_transforms_operator")
        layout.operator("wm.show_hide_collisions_operator")
        layout.operator("wm.show_hide_2d_collisions_operator")
        layout.operator("wm.show_hide_room_borders_operator")
        layout.operator("wm.show_hide_generator_operator")

        box = layout.box()
        box.operator("wm.show_lod_operator")
        box.operator("wm.hide_lod_operator")

        box = layout.box()
        box.prop(mytool, "condition_group")
        oper = box.operator("wm.show_conditional_operator")
        oper.group = getattr(mytool, 'condition_group')
        oper = box.operator("wm.hide_conditional_operator")
        oper.group = getattr(mytool, 'condition_group')

class OBJECT_PT_b3d_res_module_panel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_b3d_res_module_panel"
    bl_label = "RES resources"
    bl_space_type = "VIEW_3D"
    bl_region_type = get_ui_region()
    bl_category = "b3d Tools"

    @classmethod
    def poll(self,context):
        return context.object is not None

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mytool = scene.my_tool

        layout.prop(mytool, "selected_res_module")


class OBJECT_PT_b3d_palette_panel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_b3d_palette_panel"
    bl_label = "Palette"
    bl_parent_id = "OBJECT_PT_b3d_res_module_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = get_ui_region()
    bl_category = "b3d Tools"

    @classmethod
    def poll(self,context):
        return context.object is not None

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mytool = scene.my_tool

        res_ind = get_current_res_index()
        if res_ind != -1:
            cur_res_module = mytool.res_modules[res_ind]

            box = self.layout.box()

            box.prop(cur_res_module, "palette_subpath", text="Subpath")
            box.prop(cur_res_module, "palette_name", text="Path")

            row_indexes = bpy.context.scene.palette_row_indexes
            col_indexes = bpy.context.scene.palette_col_indexes

            rows = 32
            cols = 8
            row1 = layout_split(box.row(), 0.15)
            # row.template_list("CUSTOM_UL_colors", "palette_list", cur_res_module, "palette_colors", scene, "palette_index", type='GRID', columns = 2, rows=rows)
            col1 = row1.column()
            col2 = row1.column()
            col2.template_list("CUSTOM_UL_colors_grid", "indexes_col", col_indexes, "prop_list", scene, "palette_row_index", type='GRID', columns = cols, rows=1)

            row2 = layout_split(box.row(), 0.15)
            col1 = row2.column()
            col1.template_list("CUSTOM_UL_colors_grid", "indexes_row", row_indexes, "prop_list", scene, "palette_col_index", type='GRID', columns = 1, rows=rows)
            col2 = row2.column()
            col2.template_list("CUSTOM_UL_colors", "palette_list", cur_res_module, "palette_colors", scene, "palette_index", type='GRID', columns = cols, rows=rows)


class OBJECT_PT_b3d_maskfiles_panel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_b3d_maskfiles_panel"
    bl_label = "MSK-files"
    bl_parent_id = "OBJECT_PT_b3d_res_module_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = get_ui_region()
    bl_category = "b3d Tools"

    @classmethod
    def poll(self,context):
        return context.object is not None

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mytool = scene.my_tool

        res_ind = get_current_res_index()
        if res_ind != -1:
            cur_res_module = mytool.res_modules[res_ind]

            box = self.layout.box()

            rows = 2
            row = box.row()
            row.template_list("CUSTOM_UL_maskfiles", "maskfiles_list", cur_res_module, "maskfiles", scene, "maskfiles_index", rows=rows)

            draw_list_controls(row, "custom.list_action_arrbname", "res_modules", res_ind, "maskfiles", "maskfiles_index")

            maskfiles_index = scene.maskfiles_index
            if len(cur_res_module.maskfiles):
                cur_maskfile = cur_res_module.maskfiles[maskfiles_index]

                box.prop(cur_maskfile, "subpath", text="Subpath")
                box.prop(cur_maskfile, "name", text="Path")

                box.prop(cur_maskfile, "is_noload", text="Noload")

                split = layout_split(box, 0.3)
                split.prop(cur_maskfile, "is_someint", text="?Someint?")
                col = split.column()
                col.prop(cur_maskfile, "someint")

                col.enabled = cur_maskfile.is_someint

class OBJECT_PT_b3d_textures_panel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_b3d_textures_panel"
    bl_label = "Textures"
    bl_parent_id = "OBJECT_PT_b3d_res_module_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = get_ui_region()
    bl_category = "b3d Tools"

    @classmethod
    def poll(self,context):
        return context.object is not None

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mytool = scene.my_tool

        res_ind = get_current_res_index()
        if res_ind != -1:
            cur_res_module = mytool.res_modules[res_ind]

            box = self.layout.box()

            rows = 2
            row = box.row()
            row.template_list("CUSTOM_UL_textures", "textures_list", cur_res_module, "textures", scene, "textures_index", rows=rows)

            draw_list_controls(row, "custom.list_action_arrbname", "res_modules", res_ind, "textures", "textures_index")

            texture_index = scene.textures_index
            if (len(cur_res_module.textures)):
                cur_texture = cur_res_module.textures[texture_index]

                box.prop(cur_texture, "subpath", text="Subpath")
                box.prop(cur_texture, "name", text="Path")

                box.prop(cur_texture, "img_type", text="Image type")
                box.prop(cur_texture, "has_mipmap", text="Has mipmap")
                box.prop(cur_texture, "img_format", text="Image format")

                box.prop(cur_texture, "is_memfix", text="Memfix")
                box.prop(cur_texture, "is_noload", text="Noload")
                box.prop(cur_texture, "is_bumpcoord", text="Bympcoord")

                split = layout_split(box, 0.3)
                split.prop(cur_texture, "is_someint", text="?Someint?")
                col = split.column()
                col.prop(cur_texture, "someint")

                col.enabled = cur_texture.is_someint

class OBJECT_PT_b3d_materials_panel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_b3d_materials_panel"
    bl_label = "Materials"
    bl_parent_id = "OBJECT_PT_b3d_res_module_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = get_ui_region()
    bl_category = "b3d Tools"

    @classmethod
    def poll(self,context):
        return context.object is not None

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mytool = scene.my_tool

        res_ind = get_current_res_index()
        if res_ind != -1:
            cur_res_module = mytool.res_modules[res_ind]


            # self.layout.template_ID(item, 'id_value')

            box = self.layout.box()

            rows = 2
            row = box.row()
            row.template_list("CUSTOM_UL_materials", "materials_list", cur_res_module, "materials", scene, "materials_index", rows=rows)

            draw_list_controls(row, "custom.list_action_arrbname", "res_modules", res_ind, "materials", "materials_index")

            texture_index = scene.materials_index
            if (len(cur_res_module.materials)):
                cur_material = cur_res_module.materials[texture_index]

                split = layout_split(box, 0.3)
                split.prop(cur_material, "is_reflect", text="Reflect")
                col = split.column()
                col.enabled = cur_material.is_reflect
                col.prop(cur_material, "reflect")

                split = layout_split(box, 0.3)
                split.prop(cur_material, "is_specular", text="Specular")
                col = split.column()
                col.enabled = cur_material.is_specular
                col.prop(cur_material, "specular")

                split = layout_split(box, 0.3)
                split.prop(cur_material, "is_transp", text="Transparency")
                col = split.column()
                col.enabled = cur_material.is_transp
                col.prop(cur_material, "transp")

                split = layout_split(box, 0.3)
                split.prop(cur_material, "is_rot", text="Rotation")
                col = split.column()
                col.enabled = cur_material.is_rot
                col.prop(cur_material, "rot")

                split = layout_split(box, 0.3)
                split.prop(cur_material, "is_col", text="Color")
                col = split.column()
                col.enabled = cur_material.is_col
                col.prop(cur_material, "col_switch")
                if cur_material.col_switch:
                    col.prop(cur_material, "id_col", text="Col num")
                else:
                    col.prop(cur_material, "col", text="Col num")

                split = layout_split(box, 0.3)
                split.prop(cur_material, "is_tex", text="Texture TEX")
                col = split.column()
                col.enabled = cur_material.is_tex
                col.prop(cur_material, "tex_type")
                col.prop(cur_material, "tex_switch")
                if cur_material.tex_switch:
                    col.prop(cur_material, "id_tex", text="Tex num")
                else:
                    col.prop(cur_material, "tex", text="Tex num")

                split = layout_split(box, 0.3)
                split.prop(cur_material, "is_att", text="Att")
                col = split.column()
                col.enabled = cur_material.is_att
                col.prop(cur_material, "att_switch")
                if cur_material.att_switch:
                    col.prop(cur_material, "id_att", text="Att num")
                else:
                    col.prop(cur_material, "att", text="Att num")

                split = layout_split(box, 0.3)
                split.prop(cur_material, "is_msk", text="Maskfile")
                col = split.column()
                col.enabled = cur_material.is_msk
                col.prop(cur_material, "msk_switch")
                if cur_material.msk_switch:
                    col.prop(cur_material, "id_msk", text="Msk num")
                else:
                    col.prop(cur_material, "msk", text="Msk num")


                split = layout_split(box, 0.3)
                split.prop(cur_material, "is_power", text="Power")
                col = split.column()
                col.prop(cur_material, "power")
                col.enabled = cur_material.is_power

                split = layout_split(box, 0.3)
                split.prop(cur_material, "is_coord", text="Coord")
                col = split.column()
                col.prop(cur_material, "coord")
                col.enabled = cur_material.is_coord

                split = layout_split(box, 0.3)
                split.prop(cur_material, "is_envId", text="Env")
                col = split.column()
                col.prop(cur_material, "envId")
                col.enabled = cur_material.is_envId

                split = layout_split(box, 0.3)
                split.prop(cur_material, "is_env", text="Env")
                col = split.column()
                col.prop(cur_material, "env")
                col.enabled = cur_material.is_env

                split = layout_split(box, 0.3)
                split.prop(cur_material, "is_RotPoint", text="Rotation Center")
                col = split.column()
                col.prop(cur_material, "RotPoint")
                col.enabled = cur_material.is_RotPoint

                split = layout_split(box, 0.3)
                split.prop(cur_material, "is_move", text="Movement")
                col = split.column()
                col.prop(cur_material, "move")
                col.enabled = cur_material.is_move

                box.prop(cur_material, "is_noz", text="No Z")
                box.prop(cur_material, "is_nof", text="No F")
                box.prop(cur_material, "is_notile", text="No tiling")
                box.prop(cur_material, "is_notileu", text="No tiling U")
                box.prop(cur_material, "is_notilev", text="No tiling V")
                box.prop(cur_material, "is_alphamirr", text="Alphamirr")
                box.prop(cur_material, "is_bumpcoord", text="Bympcoord")
                box.prop(cur_material, "is_usecol", text="UseCol")
                box.prop(cur_material, "is_wave", text="Wave")

class OBJECT_PT_b3d_misc_panel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_b3d_misc_panel"
    bl_label = "About add-on"
    bl_space_type = "VIEW_3D"
    bl_region_type = get_ui_region()
    bl_category = "b3d Tools"
    #bl_context = "objectmode"

    @classmethod
    def poll(self,context):
        return context.object is not None

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mytool = scene.my_tool

        self.layout.label(text="Add-on author: aleko2144")
        self.layout.label(text="vk.com/rnr_mods")

# ------------------------------------------------------------------------
# register and unregister
# ------------------------------------------------------------------------

_classes = [
    PanelSettings,
    SetParentOperator,
    SingleAddOperator,
    TemplateAddOperator,
    CastAddOperator,
    # getters
    GetValuesOperator,
    GetPropValueOperator,
    GetFaceValuesOperator,
    GetVertexValuesOperator,
    # setters
    SetValuesOperator,
    SetPropValueOperator,
    SetFaceValuesOperator,
    SetVertexValuesOperator,
    # others
    DelValuesOperator,
    FixUVOperator,
    FixVertsOperator,
    MirrorAndFlipObjectsOperator,
    ApplyTransformsOperator,
    ShowHide2DCollisionsOperator,
    ShowHideCollisionsOperator,
    ShowHideRoomBordersOperator,
    ShowLODOperator,
    HideLODOperator,
    ShowHideGeneratorsOperator,
    ShowConditionalsOperator,
    HideConditionalsOperator,
    ShowHideSphereOperator,

    OBJECT_PT_b3d_add_panel,
    OBJECT_PT_b3d_single_add_panel,
    # OBJECT_PT_b3d_template_add_panel,
    OBJECT_PT_b3d_cast_add_panel,
    OBJECT_PT_b3d_edit_panel,
    OBJECT_PT_b3d_pob_single_edit_panel,
    OBJECT_PT_b3d_pob_edit_panel,
    OBJECT_PT_b3d_pfb_edit_panel,
    OBJECT_PT_b3d_pvb_edit_panel,
    OBJECT_PT_b3d_res_module_panel,
    OBJECT_PT_b3d_palette_panel,
    OBJECT_PT_b3d_maskfiles_panel,
    OBJECT_PT_b3d_textures_panel,
    OBJECT_PT_b3d_materials_panel,
    OBJECT_PT_b3d_func_panel,
    OBJECT_PT_b3d_misc_panel,
]

def register():
    for cls in _classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.my_tool = bpy.props.PointerProperty(type=PanelSettings)

def unregister():
    del bpy.types.Scene.my_tool
    for cls in _classes[::-1]:
        bpy.utils.unregister_class(cls)
