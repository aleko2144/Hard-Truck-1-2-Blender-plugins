# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# https://blender.stackexchange.com/questions/30444/create-an-interface-which-is-similar-to-the-material-list-box
# https://gist.github.com/p2or/5acad9e29ddb071096f9f004ae6cace7

bl_info = {
    "name": "object-pointer-uilist-dev",
    "description": "",
    "author": "p2or",
    "version": (0, 1),
    "blender": (2, 80, 0),
    "location": "Text Editor",
    "warning": "", # used for warning icon and text in addons panel
    "wiki_url": "",
    "tracker_url": "",
    "category": "Development"
}

import bpy

from bpy.props import (IntProperty,
                       BoolProperty,
                       StringProperty,
                       CollectionProperty,
                       PointerProperty)

from bpy.types import (Operator,
                       Panel,
                       PropertyGroup,
                       UIList)

from .common import (
    get_current_res_module,
    update_color_preview
)

from ..compatibility import (
    make_annotations,
    layout_split
)

from ..common import (
    classes_logger
)

log = classes_logger
# -------------------------------------------------------------------
#   Operators
# -------------------------------------------------------------------

def action_invoke(self, context, event, arr_bname = False):
    scn = context.scene
    idx = getattr(scn, self.customindex)

    if arr_bname:
        tool = scn.my_tool
        param = getattr(getattr(tool, self.bname)[self.bindex], self.pname)
    else:
        tool = scn.block_tool
        param = getattr(getattr(tool, self.bname), self.pname)

    try:
        item = param[idx]
    except IndexError:
        pass
    else:
        if self.action == 'DOWN' and idx < len(param) - 1:
            param.move(idx, idx+1)
            setattr(scn, self.customindex, idx+1)
            info = 'Item "{}" moved to position {}'.format(item.name, idx+1)
            self.report({'INFO'}, info)

        elif self.action == 'UP' and idx >= 1:
            param.move(idx, idx-1)
            setattr(scn, self.customindex, idx-1)
            info = 'Item "{}" moved to position {}'.format(item.name, idx+1)
            self.report({'INFO'}, info)

        elif self.action == 'REMOVE':
            info = 'Item "{}" removed from list'.format(param[idx].name)
            if idx == 0:
                setattr(scn, self.customindex, 0)
            else:
                setattr(scn, self.customindex, idx-1)
            param.remove(idx)
            self.report({'INFO'}, info)

    if self.action == 'ADD':
        if context.object:
            item = param.add()
            for i in range(len(param)-1, idx+1, -1):
                param.move(i, i-1)
            setattr(scn, self.customindex, idx)
            self.report({'INFO'}, "Item added to list on position {}".format(idx))
    return {"FINISHED"}


@make_annotations
class CUSTOM_OT_actions_arrbname(Operator):
    """Move items up and down, add and remove"""
    bl_idname = "custom.list_action_arrbname"
    bl_label = "List Actions"
    bl_description = "Move items up and down, add and remove"
    bl_options = {'REGISTER'}

    action = bpy.props.EnumProperty(
        items=(
            ('UP', "Up", ""),
            ('DOWN', "Down", ""),
            ('REMOVE', "Remove", ""),
            ('ADD', "Add", "")))

    bname = bpy.props.StringProperty()

    bindex = bpy.props.IntProperty(default=-1)

    pname = bpy.props.StringProperty()

    customindex = bpy.props.StringProperty()

    def invoke(self, context, event):
        return action_invoke(self, context, event, True)


@make_annotations
class CUSTOM_OT_actions(Operator):
    """Move items up and down, add and remove"""
    bl_idname = "custom.list_action"
    bl_label = "List Actions"
    bl_description = "Move items up and down, add and remove"
    bl_options = {'REGISTER'}

    action = bpy.props.EnumProperty(
        items=(
            ('UP', "Up", ""),
            ('DOWN', "Down", ""),
            ('REMOVE', "Remove", ""),
            ('ADD', "Add", "")))

    bname = bpy.props.StringProperty()

    pname = bpy.props.StringProperty()

    customindex = bpy.props.StringProperty()

    def invoke(self, context, event):
        return action_invoke(self, context, event, False)


# -------------------------------------------------------------------
#   Drawing
# -------------------------------------------------------------------

class CUSTOM_UL_colors(UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.prop(item, "value", text="")

    def invoke(self, context, event):
        pass

class CUSTOM_UL_colors_grid(UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.label(text="{}".format(item.value))

    def invoke(self, context, event):
        pass


class CUSTOM_UL_materials(UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        split = layout_split(layout, 0.15)
        split.label(text= "{}".format(index+1))
        split.template_ID(item, 'id_mat')

    def invoke(self, context, event):
        pass

class CUSTOM_UL_textures(UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        split = layout_split(layout, 0.15)
        split.label(text= "{}".format(index+1))
        split.template_ID(item, 'id_tex')

    def invoke(self, context, event):
        pass

class CUSTOM_UL_maskfiles(UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        split = layout_split(layout, 0.15)
        split.label(text= "{}".format(index+1))
        split.template_ID(item, 'id_msk')

    def invoke(self, context, event):
        pass

class CUSTOM_UL_items(UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        split = layout_split(layout, 0.15)
        split.label(text= "{}".format(index+1))
        split.prop(item, "value", text="", emboss=False, translate=False)

    def invoke(self, context, event):
        pass


def draw_list_controls(layout, list_type, bname, bindex, pname, custom_index):
    col = layout.column(align=True)

    props = col.operator(list_type, icon='PLUS', text="")
    props.action = 'ADD'
    props.bname = bname
    props.bindex = bindex
    props.pname = pname
    props.customindex = custom_index

    props = col.operator(list_type, icon='CANCEL', text="")
    props.action = 'REMOVE'
    props.bname = bname
    props.bindex = bindex
    props.pname = pname
    props.customindex = custom_index

    col.separator()

    props = col.operator(list_type, icon='TRIA_UP', text="")
    props.action = 'UP'
    props.bname = bname
    props.bindex = bindex
    props.pname = pname
    props.customindex = custom_index

    props = col.operator(list_type, icon='TRIA_DOWN', text="")
    props.action = 'DOWN'
    props.bname = bname
    props.bindex = bindex
    props.pname = pname
    props.customindex = custom_index


# -------------------------------------------------------------------
#   Collection
# -------------------------------------------------------------------

@make_annotations
class PropIndex(PropertyGroup):
    value = IntProperty()

@make_annotations
class PropIndexList(PropertyGroup):
    prop_list = CollectionProperty(type=PropIndex)



# -------------------------------------------------------------------
#   Register & Unregister
# -------------------------------------------------------------------

_classes = [
    CUSTOM_OT_actions,
    CUSTOM_OT_actions_arrbname,
    CUSTOM_UL_colors,
    CUSTOM_UL_colors_grid,
    CUSTOM_UL_textures,
    CUSTOM_UL_maskfiles,
    CUSTOM_UL_materials,
    CUSTOM_UL_items,
    PropIndex,
    PropIndexList
]

def register():
    for cls in _classes:
        if(not cls.is_registered):
            bpy.utils.register_class(cls)

    # Custom scene properties
    bpy.types.Scene.custom_index = IntProperty()
    bpy.types.Scene.palette_index = IntProperty()
    bpy.types.Scene.textures_index = IntProperty()
    bpy.types.Scene.materials_index = IntProperty()
    bpy.types.Scene.maskfiles_index = IntProperty()
    bpy.types.Scene.palette_row_indexes = PointerProperty(type=PropIndexList)
    bpy.types.Scene.palette_row_index = IntProperty()
    bpy.types.Scene.palette_col_indexes = PointerProperty(type=PropIndexList)
    bpy.types.Scene.palette_col_index = IntProperty()
    




def unregister():
    for cls in _classes[::-1]:
        if(cls.is_registered):
            bpy.utils.unregister_class(cls)

    attrs = [
        "custom_index", "palette_index", 
        "textures_index", "materials_index", "maskfiles_index"
        "palette_row_indexes", "palette_row_index",
        "palette_col_indexes","palette_col_index"

    ]

    for attr in attrs:
        if(hasattr(bpy.types.Scene, attr)):
            delattr(bpy.types.Scene, attr)
