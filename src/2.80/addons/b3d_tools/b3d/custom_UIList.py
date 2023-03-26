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
    getCurrentRESModule,
    updateColorPreview
)

# -------------------------------------------------------------------
#   Operators
# -------------------------------------------------------------------

def action_invoke_color(self, context, event, arr_bname = False):
    scn = context.scene
    idx = getattr(scn, self.customindex)
    mytool = scn.my_tool

    resModule = getCurrentRESModule()

    if arr_bname:
        param = getattr(getattr(mytool, self.bname)[self.bindex], self.pname)
    else:
        param = getattr(getattr(mytool, self.bname), self.pname)

    try:
        item = param[idx]
    except IndexError:
        pass
    else:
        if self.action == 'DOWN' and idx < len(param) - 1:
            param.move(idx, idx+1)
            setattr(scn, self.customindex, idx+1)
            updateColorPreview(resModule, idx)
            updateColorPreview(resModule, idx+1)
            info = 'Item "%s" moved to position %d' % (item.name, idx+1)
            self.report({'INFO'}, info)

        elif self.action == 'UP' and idx >= 1:
            param.move(idx, idx-1)
            setattr(scn, self.customindex, idx-1)
            updateColorPreview(resModule, idx)
            updateColorPreview(resModule, idx-1)
            info = 'Item "%s" moved to position %d' % (item.name, idx-1)
            self.report({'INFO'}, info)

        elif self.action == 'REMOVE':
            info = 'Item "%s" removed from list' % (param[idx].name)
            setattr(scn, self.customindex, idx-1)
            param.remove(idx)
            for i in range(idx-1, len(param)-1):
                updateColorPreview(resModule, i)
            self.report({'INFO'}, info)

    if self.action == 'ADD':
        if context.object:
            item = param.add()
            updateColorPreview(resModule, len(param)-1)
            for i in range(len(param)-1, idx+1, -1):
                param.move(i, i-1)
            setattr(scn, self.customindex, idx)
            self.report({'INFO'}, "Item added to list on position %d" % (idx))
    return {"FINISHED"}


def action_invoke(self, context, event, arr_bname = False):
    scn = context.scene
    idx = getattr(scn, self.customindex)
    mytool = scn.my_tool

    if arr_bname:
        param = getattr(getattr(mytool, self.bname)[self.bindex], self.pname)
    else:
        param = getattr(getattr(mytool, self.bname), self.pname)

    try:
        item = param[idx]
    except IndexError:
        pass
    else:
        print(param)

        if self.action == 'DOWN' and idx < len(param) - 1:
            param.move(idx, idx+1)
            setattr(scn, self.customindex, idx+1)
            info = 'Item "%s" moved to position %d' % (item.name, idx+1)
            self.report({'INFO'}, info)

        elif self.action == 'UP' and idx >= 1:
            param.move(idx, idx-1)
            setattr(scn, self.customindex, idx-1)
            info = 'Item "%s" moved to position %d' % (item.name, idx-1)
            self.report({'INFO'}, info)

        elif self.action == 'REMOVE':
            info = 'Item "%s" removed from list' % (param[idx].name)
            setattr(scn, self.customindex, idx-1)
            param.remove(idx)
            self.report({'INFO'}, info)

    if self.action == 'ADD':
        if context.object:
            item = param.add()
            for i in range(len(param)-1, idx+1, -1):
                param.move(i, i-1)
            setattr(scn, self.customindex, idx)
            self.report({'INFO'}, "Item added to list on position %d" % (idx))
    return {"FINISHED"}


class CUSTOM_OT_actions_color(Operator):
    """Move items up and down, add and remove"""
    bl_idname = "custom.list_action_color"
    bl_label = "List Actions"
    bl_description = "Move items up and down, add and remove"
    bl_options = {'REGISTER'}

    action: bpy.props.EnumProperty(
        items=(
            ('UP', "Up", ""),
            ('DOWN', "Down", ""),
            ('REMOVE', "Remove", ""),
            ('ADD', "Add", "")))

    bname: bpy.props.StringProperty()

    bindex: bpy.props.IntProperty(default=-1)

    pname: bpy.props.StringProperty()

    customindex: bpy.props.StringProperty()

    def invoke(self, context, event):
        return action_invoke_color(self, context, event, True)


class CUSTOM_OT_actions_arrbname(Operator):
    """Move items up and down, add and remove"""
    bl_idname = "custom.list_action_arrbname"
    bl_label = "List Actions"
    bl_description = "Move items up and down, add and remove"
    bl_options = {'REGISTER'}

    action: bpy.props.EnumProperty(
        items=(
            ('UP', "Up", ""),
            ('DOWN', "Down", ""),
            ('REMOVE', "Remove", ""),
            ('ADD', "Add", "")))

    bname: bpy.props.StringProperty()

    bindex: bpy.props.IntProperty(default=-1)

    pname: bpy.props.StringProperty()

    customindex: bpy.props.StringProperty()

    def invoke(self, context, event):
        return action_invoke(self, context, event, True)


class CUSTOM_OT_actions(Operator):
    """Move items up and down, add and remove"""
    bl_idname = "custom.list_action"
    bl_label = "List Actions"
    bl_description = "Move items up and down, add and remove"
    bl_options = {'REGISTER'}

    action: bpy.props.EnumProperty(
        items=(
            ('UP', "Up", ""),
            ('DOWN', "Down", ""),
            ('REMOVE', "Remove", ""),
            ('ADD', "Add", "")))

    bname: bpy.props.StringProperty()

    pname: bpy.props.StringProperty()

    customindex: bpy.props.StringProperty()

    def invoke(self, context, event):
        return action_invoke(self, context, event, False)


# -------------------------------------------------------------------
#   Drawing
# -------------------------------------------------------------------

class CUSTOM_UL_colors(UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        split = layout.split(factor=0.5)
        split.label(text="%d" % (index+1))
        split.prop(item, "value", text="")

    def invoke(self, context, event):
        pass


class CUSTOM_UL_materials(UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        split = layout.split(factor=0.3)
        split.label(text="Index: %d" % (index+1))
        split.template_ID(item, 'id_value')

    def invoke(self, context, event):
        pass

class CUSTOM_UL_textures(UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        split = layout.split(factor=0.3)
        split.label(text="Index: %d" % (index+1))
        split.template_ID(item, 'id_value')

    def invoke(self, context, event):
        pass

class CUSTOM_UL_items(UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        split = layout.split(factor=0.3)
        split.label(text="Index: %d" % (index+1))
        split.prop(item, "value", text="", emboss=False, translate=False)

    def invoke(self, context, event):
        pass

class CUSTOM_PT_objectList(Panel):
    """Adds a custom panel to the TEXT_EDITOR"""
    bl_idname = 'TEXT_PT_my_panel'
    bl_space_type = "TEXT_EDITOR"
    bl_region_type = "UI"
    bl_label = "Custom Object List Demo"

    def draw(self, context):
        layout = self.layout
        scn = bpy.context.scene

        rows = 2
        row = layout.row()
        row.template_list("CUSTOM_UL_items", "float_list", scn, "custom", scn, "custom_index", rows=rows)

        col = row.column(align=True)
        col.operator("custom.list_action", icon='ADD', text="").action = 'ADD'
        col.operator("custom.list_action", icon='REMOVE', text="").action = 'REMOVE'
        col.separator()
        col.operator("custom.list_action", icon='TRIA_UP', text="").action = 'UP'
        col.operator("custom.list_action", icon='TRIA_DOWN', text="").action = 'DOWN'


def drawListControls(layout, list_type, bname, bindex, pname, custom_index):
        col = layout.column(align=True)

        props = col.operator(list_type, icon='ADD', text="")
        props.action = 'ADD'
        props.bname = bname
        props.bindex = bindex
        props.pname = pname
        props.customindex = custom_index

        props = col.operator(list_type, icon='REMOVE', text="")
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

class CUSTOM_PG_objectCollection(PropertyGroup):
    #name: StringProperty() -> Instantiated by default
    obj: PointerProperty(
        name="Object",
        type=bpy.types.Object)


# -------------------------------------------------------------------
#   Register & Unregister
# -------------------------------------------------------------------

_classes = [
    CUSTOM_OT_actions,
    CUSTOM_OT_actions_arrbname,
    CUSTOM_OT_actions_color,
    CUSTOM_UL_colors,
    CUSTOM_UL_textures,
    CUSTOM_UL_materials,
    CUSTOM_UL_items,
    CUSTOM_PT_objectList,
    CUSTOM_PG_objectCollection,
]

def register():
    from bpy.utils import register_class
    for cls in _classes:
        register_class(cls)

    # Custom scene properties
    bpy.types.Scene.custom = CollectionProperty(type=CUSTOM_PG_objectCollection)
    bpy.types.Scene.custom_index = IntProperty()
    bpy.types.Scene.palette_index = IntProperty()
    bpy.types.Scene.textures_index = IntProperty()
    bpy.types.Scene.materials_index = IntProperty()
    bpy.types.Scene.maskfiles_index = IntProperty()


def unregister():
    from bpy.utils import unregister_class
    for cls in _classes[::-1]:
        unregister_class(cls)

    del bpy.types.Scene.custom
    del bpy.types.Scene.custom_index
    del bpy.types.Scene.palette_index
    del bpy.types.Scene.textures_index
    del bpy.types.Scene.materials_index
    del bpy.types.Scene.maskfiles_index



if __name__ == "__main__":
    register()