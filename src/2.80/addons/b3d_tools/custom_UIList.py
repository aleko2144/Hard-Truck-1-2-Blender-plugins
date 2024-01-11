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

# -------------------------------------------------------------------
#   Operators
# -------------------------------------------------------------------

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
        if self.action == 'DOWN' and idx < len(param) - 1:
            item_next = param[idx+1].name
            param.move(idx, idx+1)
            idx += 1
            info = 'Item "%s" moved to position %d' % (item.name, idx + 1)
            self.report({'INFO'}, info)

        elif self.action == 'UP' and idx >= 1:
            item_prev = param[idx-1].name
            param.move(idx, idx-1)
            idx -= 1
            info = 'Item "%s" moved to position %d' % (item.name, idx + 1)
            self.report({'INFO'}, info)

        elif self.action == 'REMOVE':
            info = 'Item "%s" removed from list' % (param[idx].name)
            idx -= 1
            param.remove(idx)
            self.report({'INFO'}, info)

    if self.action == 'ADD':
        if context.object:
            item = param.add()
            # item.name = context.object.name
            # item.obj = context.object
            item['value'] = 0.0
            idx = len(param)-1
            # info = '"%s" added to list' % (item.name)
            # self.report({'INFO'}, info)
        else:
            pass
            # self.report({'INFO'}, "Nothing selected in the Viewport")
    return {"FINISHED"}

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


class CUSTOM_OT_addViewportSelection(Operator):
    """Add all items currently selected in the viewport"""
    bl_idname = "custom.add_viewport_selection"
    bl_label = "Add Viewport Selection to List"
    bl_description = "Add all items currently selected in the viewport"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scn = context.scene
        selected_objs = context.selected_objects
        if selected_objs:
            new_objs = []
            for i in selected_objs:
                item = scn.custom.add()
                item.name = i.name
                item.obj = i
                new_objs.append(item.name)
            info = ', '.join(map(str, new_objs))
            self.report({'INFO'}, 'Added: "%s"' % (info))
        else:
            self.report({'INFO'}, "Nothing selected in the Viewport")
        return{'FINISHED'}


class CUSTOM_OT_printItems(Operator):
    """Print all items and their properties to the console"""
    bl_idname = "custom.print_items"
    bl_label = "Print Items to Console"
    bl_description = "Print all items and their properties to the console"
    bl_options = {'REGISTER', 'UNDO'}

    reverse_order: BoolProperty(
        default=False,
        name="Reverse Order")

    @classmethod
    def poll(cls, context):
        return bool(context.scene.custom)

    def execute(self, context):
        scn = context.scene
        if self.reverse_order:
            for i in range(scn.custom_index, -1, -1):
                ob = scn.custom[i].obj
                print ("Object:", ob,"-",ob.name, ob.type)
        else:
            for item in scn.custom:
                ob = item.obj
                print ("Object:", ob,"-",ob.name, ob.type)
        return{'FINISHED'}


class CUSTOM_OT_clearList(Operator):
    """Clear all items of the list"""
    bl_idname = "custom.clear_list"
    bl_label = "Clear List"
    bl_description = "Clear all items of the list"
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return bool(context.scene.custom)

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        if bool(context.scene.custom):
            context.scene.custom.clear()
            self.report({'INFO'}, "All items removed")
        else:
            self.report({'INFO'}, "Nothing to remove")
        return{'FINISHED'}


class CUSTOM_OT_removeDuplicates(Operator):
    """Remove all duplicates"""
    bl_idname = "custom.remove_duplicates"
    bl_label = "Remove Duplicates"
    bl_description = "Remove all duplicates"
    bl_options = {'INTERNAL'}

    def find_duplicates(self, context):
        """find all duplicates by name"""
        name_lookup = {}
        for c, i in enumerate(context.scene.custom):
            name_lookup.setdefault(i.obj.name, []).append(c)
        duplicates = set()
        for name, indices in name_lookup.items():
            for i in indices[1:]:
                duplicates.add(i)
        return sorted(list(duplicates))

    @classmethod
    def poll(cls, context):
        return bool(context.scene.custom)

    def execute(self, context):
        scn = context.scene
        removed_items = []
        # Reverse the list before removing the items
        for i in self.find_duplicates(context)[::-1]:
            scn.custom.remove(i)
            removed_items.append(i)
        if removed_items:
            scn.custom_index = len(scn.custom)-1
            info = ', '.join(map(str, removed_items))
            self.report({'INFO'}, "Removed indices: %s" % (info))
        else:
            self.report({'INFO'}, "No duplicates")
        return{'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)


class CUSTOM_OT_selectItems(Operator):
    """Select Items in the Viewport"""
    bl_idname = "custom.select_items"
    bl_label = "Select Item(s) in Viewport"
    bl_description = "Select Items in the Viewport"
    bl_options = {'REGISTER', 'UNDO'}

    select_all = BoolProperty(
        default=False,
        name="Select all Items of List",
        options={'SKIP_SAVE'})

    @classmethod
    def poll(cls, context):
        return bool(context.scene.custom)

    def execute(self, context):
        scn = context.scene
        idx = scn.custom_index

        try:
            item = scn.custom[idx]
        except IndexError:
            self.report({'INFO'}, "Nothing selected in the list")
            return{'CANCELLED'}

        obj_error = False
        bpy.ops.object.select_all(action='DESELECT')
        if not self.select_all:
            name = scn.custom[idx].obj.name
            obj = scn.objects.get(name, None)
            if not obj:
                obj_error = True
            else:
                obj.select_set(True)
                info = '"%s" selected in Vieport' % (obj.name)
        else:
            selected_items = []
            unique_objs = set([i.obj.name for i in scn.custom])
            for i in unique_objs:
                obj = scn.objects.get(i, None)
                if obj:
                    obj.select_set(True)
                    selected_items.append(obj.name)

            if not selected_items:
                obj_error = True
            else:
                missing_items = unique_objs.difference(selected_items)
                if not missing_items:
                    info = '"%s" selected in Viewport' \
                        % (', '.join(map(str, selected_items)))
                else:
                    info = 'Missing items: "%s"' \
                        % (', '.join(map(str, missing_items)))
        if obj_error:
            info = "Nothing to select, object removed from scene"
        self.report({'INFO'}, info)
        return{'FINISHED'}


class CUSTOM_OT_deleteObject(Operator):
    """Delete object from scene"""
    bl_idname = "custom.delete_object"
    bl_label = "Remove Object from Scene"
    bl_description = "Remove object from scene"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return bool(context.scene.custom)

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        scn = context.scene
        selected_objs = context.selected_objects
        idx = scn.custom_index
        try:
            item = scn.custom[idx]
        except IndexError:
            pass
        else:
            ob = scn.objects.get(item.obj.name)
            if not ob:
                self.report({'INFO'}, "No object of that name found in scene")
                return {"CANCELLED"}
            else:
                bpy.ops.object.select_all(action='DESELECT')
                ob.select_set(True)
                bpy.ops.object.delete()

            info = ' Item "%s" removed from Scene' % (len(selected_objs))
            scn.custom_index -= 1
            scn.custom.remove(idx)
            self.report({'INFO'}, info)
        return{'FINISHED'}


# -------------------------------------------------------------------
#   Drawing
# -------------------------------------------------------------------

class CUSTOM_UL_items(UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        # obj = item.obj
        # custom_icon = "OUTLINER_OB_%s" % obj.type
        split = layout.split(factor=0.3)
        split.label(text="Index: %d" % (index))
        split.prop(item, "value", text="", emboss=False, translate=False)
        # split.prop(obj, "name", text="", emboss=False, translate=False, icon=custom_icon)

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
    CUSTOM_OT_addViewportSelection,
    CUSTOM_OT_printItems,
    CUSTOM_OT_clearList,
    CUSTOM_OT_removeDuplicates,
    CUSTOM_OT_selectItems,
    CUSTOM_OT_deleteObject,
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
    bpy.types.Scene.textures_index = IntProperty()
    bpy.types.Scene.materials_index = IntProperty()
    bpy.types.Scene.maskfiles_index = IntProperty()


def unregister():
    from bpy.utils import unregister_class
    for cls in _classes[::-1]:
        unregister_class(cls)

    del bpy.types.Scene.custom
    del bpy.types.Scene.custom_index
    del bpy.types.Scene.textures_index
    del bpy.types.Scene.materials_index
    del bpy.types.Scene.maskfiles_index



if __name__ == "__main__":
    register()