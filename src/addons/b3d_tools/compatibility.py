# https://github.com/CGCookie/blender-addon-updater/blob/master/addon_updater_ops.py
import bpy

def is_before_2_80():
    return not hasattr(bpy.app, "version") or bpy.app.version < (2, 80)

def is_before_2_93():
    return bpy.app.version < (2, 93, 0)

def make_annotations(cls):
    """Add annotation attribute to fields to avoid Blender 2.8+ warnings"""

    if is_before_2_80():
        return cls
    if is_before_2_93():
        bl_props = {k: v for k, v in cls.__dict__.items() if isinstance(v, tuple)}
    else:
        bl_props = {k: v for k, v in cls.__dict__.items()
                    if isinstance(v, bpy.props._PropertyDeferred)}
    if bl_props:
        if '__annotations__' not in cls.__dict__:
            setattr(cls, '__annotations__', {})
        annotations = cls.__dict__['__annotations__']
        for k, v in bl_props.items():
            annotations[k] = v
            delattr(cls, k)
    return cls

    
def layout_split(layout, factor=0.0, align=False):
    """Intermediate method for pre and post blender 2.8 split UI function"""
    if not hasattr(bpy.app, "version") or bpy.app.version < (2, 80):
        return layout.split(percentage=factor, align=align)
    return layout.split(factor=factor, align=align)


def get_user_preferences(context=None):
    """Intermediate method for pre and post blender 2.8 grabbing preferences"""
    if not context:
        context = bpy.context
    prefs = None
    if hasattr(context, "user_preferences"):
        return context.user_preferences
    elif hasattr(context, "preferences"):
        return context.preferences
    # To make the addon stable and non-exception prone, return None
    # raise Exception("Could not fetch user preferences")
    else:
        return None
    
def get_object_hidden(block):
    if is_before_2_80():
        return block.hide
    else:
        return block.hide_get()


def set_object_hidden(block, state):
    if is_before_2_80():
        block.hide = state
    else:
        block.hide_set(state)

def get_or_create_collection(name):
    if is_before_2_80():
        return bpy.context.scene
    else:
        collection = bpy.data.collections.get(name)
        if collection is None:
            return bpy.data.collections.new(name)
        else:
            return collection

def get_context_collection_objects(context):
    if is_before_2_80():
        return context.scene.objects
    else:
        return context.collection.objects

def get_uv_layers(mesh):
    if is_before_2_80():
        return mesh.uv_textures
    else:
        return mesh.uv_layers

def set_empty_type(empty, etype):
    if is_before_2_80():
        empty.empty_draw_type = etype
    else:
        empty.empty_display_type = etype

def get_empty_type(empty, etype):
    if is_before_2_80():
        return empty.empty_draw_type
    else:
        return empty.empty_display_type

def set_empty_size(empty, esize):
    if is_before_2_80():
        empty.empty_draw_size = esize
    else:
        empty.empty_display_size = esize

def get_empty_size(empty):
    if is_before_2_80():
        return empty.empty_draw_size
    else:
        return empty.empty_display_size

def get_active_object():
    if is_before_2_80():
        return bpy.context.scene.objects.active
    else:
        return bpy.context.view_layer.objects.active

def set_active_object(obj):
    if is_before_2_80():
        bpy.context.scene.objects.active = obj
    else:
        bpy.context.view_layer.objects.active = obj

def get_cursor_location():
    if is_before_2_80():
        return bpy.context.scene.cursor_location
    else:
        return bpy.context.scene.cursor.location

def matrix_multiply(a, b):
    if is_before_2_80():
        return a * b
    else:
        return a @ b

def get_ui_region():
    if is_before_2_80():
        return "TOOLS"
    else:
        return "UI"

def get_ui_menu():
    if is_before_2_80():
        return "INFO_MT" 
    else:
        return "TOPBAR_MT"

