import math
import bpy

from ..consts import (
    BLOCK_TYPE
)

from .class_descr import (
    FieldType
)

from .classes import (
    BlockClassHandler
)

from .common import (
    get_level_group,
    get_class_attributes
)


def draw_multi_select_list(self, layout, list_name, per_row):

    i = 0
    list_obj = getattr(self, list_name)
    rowcnt = math.floor(len(list_obj)/per_row)

    if len(list_obj) > 0:

        for j in range(rowcnt):
            row = layout.row()
            for block in list_obj[i:i+per_row]:
                row.prop(block, 'state', text=block['name'], toggle=True)
            i+=per_row
        row = layout.row()
        for block in list_obj[i:]:
            row.prop(block, 'state', text=block['name'], toggle=True)
    else:
        layout.label(text='No items')


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


def draw_fields_by_type(l_self, zclass, multiple_edit = True):

    attrs_cls = get_class_attributes(zclass)
    boxes = {}
    for attr_class_name in attrs_cls:
        attr_class = zclass.__dict__[attr_class_name]

        bname, bnum = BlockClassHandler.get_mytool_block_name_by_class(zclass, multiple_edit)

        ftype = attr_class.get_block_type()
        subtype = attr_class.get_subtype()
        cur_group_name = attr_class.get_group()
        prop_text = attr_class.get_name()
        pname = attr_class.get_prop()
        blocktool = bpy.context.scene.block_tool
        cur_layout = l_self.layout

        if cur_group_name is not None or len(cur_group_name) > 0:
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
            
            blk = getattr(blocktool, bname) if hasattr(blocktool, bname) else None
            if blk is not None:

                box = cur_layout.box()

                show_attr = getattr(blk, 'show_{}'.format(pname)) if hasattr(blk, 'show_{}'.format(pname)) else None

                if multiple_edit:
                    if hasattr(blk, 'show_{}'.format(pname)):
                        box.prop(blk, "show_{}".format(pname))

                col = box.column()
                if ftype in [
                    FieldType.STRING,
                    FieldType.COORD,
                    FieldType.RAD,
                    FieldType.INT,
                    FieldType.FLOAT
                ]:
                    if multiple_edit: # getting from my_tool
                        attr = getattr(blocktool, bname)
                        if attr is not None:
                            col.prop(attr, pname)
                    else:
                        col.prop(bpy.context.object, '["{}"]'.format(pname), text=prop_text)

                elif ftype in [FieldType.ENUM_DYN, FieldType.ENUM]:
                    
                    switch_attr = getattr(blk, '{}_switch'.format(pname)) if hasattr(blk, '{}_switch'.format(pname)) else None
                    enum_attr = getattr(blk, '{}_enum'.format(pname)) if hasattr(blk, '{}_enum'.format(pname)) else None

                    if switch_attr is not None:
                        col.prop(blk, '{}_switch'.format(pname))
                        
                        if switch_attr:
                            # if enum_attr:
                            col.prop(blk, '{}_enum'.format(pname))

                        else:
                            if multiple_edit:
                                if hasattr(blk, pname):
                                    col.prop(blk, pname)
                            else:
                                col.prop(bpy.context.object, '["{}"]'.format(pname), text=prop_text)

                elif ftype == FieldType.LIST:

                    scn = bpy.context.scene

                    rows = 2

                    row = box.row()
                    props = row.operator("wm.get_prop_value_operator")
                    props.pname = pname
                    props = row.operator("wm.set_prop_value_operator")
                    props.pname = pname
                    row = box.row()
                    row.template_list("CUSTOM_UL_items", "", blk, pname, scn, "custom_index", rows=rows)

                    col = row.column(align=True)
                    props = col.operator("custom.list_action", icon='PLUS', text="")
                    props.action = 'ADD'
                    props.bname = bname
                    props.pname = pname
                    props.customindex = "custom_index"
                    props = col.operator("custom.list_action", icon='CANCEL', text="")
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
                    if show_attr:
                        col.enabled = True
                    else:
                        col.enabled = False

        elif ftype == FieldType.V_FORMAT:
            if multiple_edit:
                blk = getattr(blocktool, bname) if hasattr(blocktool, bname) else None
                if blk is not None:
                    box = cur_layout.box()

                    if hasattr(blk, "show_{}".format(pname)):
                        box.prop(blk, "show_{}".format(pname))
                    
                    if hasattr(blk, "{}_show_int".format(pname)):
                        box.prop(blk, "{}_show_int".format(pname))
                        
                    col1 = box.column()
                    if getattr(blk, "{}_show_int".format(pname)) == True:
                        
                        if hasattr(blk, "{}_format_raw".format(pname)):
                            col1.prop(blk, "{}_format_raw".format(pname))
                    else:

                        if hasattr(blk, "{}_triang_offset".format(pname)):
                            col1.prop(blk, "{}_triang_offset".format(pname))

                        if hasattr(blk, "{}_use_uvs".format(pname)):
                            col1.prop(blk, "{}_use_uvs".format(pname))

                        if hasattr(blk, "{}_use_normals".format(pname)):
                            col1.prop(blk, "{}_use_normals".format(pname))

                        if hasattr(blk, "{}_normal_flag".format(pname)):
                            col1.prop(blk, "{}_normal_flag".format(pname))

                    if hasattr(blk, "show_{}".format(pname)):
                        col1.enabled = getattr(blk, "show_{}".format(pname))

        elif ftype == FieldType.WAY_SEG_FLAGS:
            blk = getattr(blocktool, bname) if hasattr(blocktool, bname) else None
            if blk is not None:
                box = cur_layout.box()
                if multiple_edit:

                    if hasattr(blk, "show_{}".format(pname)):
                        box.prop(blk, "show_{}".format(pname))
                    
                    if hasattr(blk, "{}_show_int".format(pname)):
                        box.prop(blk, "{}_show_int".format(pname))
                        
                    col1 = box.column()
                    if getattr(blk, "{}_show_int".format(pname)) == True:
                        
                        if hasattr(blk, "{}_segment_flags".format(pname)):
                            col1.prop(blk, "{}_segment_flags".format(pname))

                    else:

                        if hasattr(blk, "{}_is_curve".format(pname)):
                            col1.prop(blk, "{}_is_curve".format(pname))

                        if hasattr(blk, "{}_is_path".format(pname)):
                            col1.prop(blk, "{}_is_path".format(pname))

                        if hasattr(blk, "{}_is_right_lane".format(pname)):
                            col1.prop(blk, "{}_is_right_lane".format(pname))

                        if hasattr(blk, "{}_is_left_lane".format(pname)):
                            col1.prop(blk, "{}_is_left_lane".format(pname))

                        if hasattr(blk, "{}_is_fillable".format(pname)):
                            col1.prop(blk, "{}_is_fillable".format(pname))

                        if hasattr(blk, "{}_is_hidden".format(pname)):
                            col1.prop(blk, "{}_is_hidden".format(pname))

                        if hasattr(blk, "{}_no_traffic".format(pname)):
                            col1.prop(blk, "{}_no_traffic".format(pname))


                    if hasattr(blk, "show_{}".format(pname)):
                        col1.enabled = getattr(blk, "show_{}".format(pname))
                else:

                    col = box.column()
                    col.prop(bpy.context.object, '["{}"]'.format(pname), text=prop_text)
