

# To support reload properly, try to access a package var, if it's there,
# reload everything
if "bpy" in locals():
    print("Reimporting modules!!!")
    import importlib

    importlib.reload(common)
    importlib.reload(class_descr)
    importlib.reload(classes)
    importlib.reload(import_b3d)
    importlib.reload(export_b3d)
    importlib.reload(imghelp)
    importlib.reload(panel)
    importlib.reload(menus)
else:
    import bpy
    from . import (
        common,
        class_descr,
        classes,
        import_b3d,
        export_b3d,
        imghelp,
        panel,
        menus
    )

def register():
    print("registering addon")
    class_descr.register()
    classes.register()
    menus.register()
    panel.register()


def unregister():
    print("unregistering addon")
    panel.unregister()
    menus.unregister()
    classes.unregister()
    class_descr.unregister()
