# https://blender.stackexchange.com/questions/28504/blender-ignores-changes-to-python-scripts/28505#28505
# When bpy is already in local, we know this is not the initial import...
# if "bpy" in locals():
#     # ...so we need to reload our submodule(s) using importlib
#     import importlib
#     if "my_submodule" in locals():
#         importlib.reload(my_submodule)


# This is only relevant on first run, on later reloads those modules
# are already in locals() and those statements do not do anything.
# import bpy
# import my_submodule

import bpy


bl_info = {
    "name": "addonreloader",
    "author": "Stef van der Struijk",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Tools > hallochen",
    "description": "Reload any addon with a button click",
    "warning": "Oopsy2",
    'wiki_url': "",
    'tracker_url': "",
    "category": "Tests"
}


class ReloadButton(bpy.types.Operator):
    """Reload an addon"""  # Use this as a tooltip for menu items and buttons.
    bl_idname = "object.addonreloader"  # Unique identifier for buttons and menu items to reference.
    bl_label = "Reload any addon"  # Display name in the interface.
    bl_options = {'REGISTER', 'INTERNAL'}  # Enable ?

    def execute(self, context):  # execute() is called when running the operator.
        bpy.ops.preferences.addon_enable(module="hallochen")

        return {'FINISHED'}  # Lets Blender know the operator finished successfully.


classes = (
    ReloadButton,
)

register, unregister = bpy.utils.register_classes_factory(classes)


# def register():
#     # addon updater code and configurations
#     # in case of broken version, try to register the updater first
#     # so that users can revert back to a working version
#     # addon_updater_ops.register(bl_info)
#
#     # register the example panel, to show updater buttons
#     for cls in classes:
#         bpy.utils.register_class(cls)
#
#
# def unregister():
#     # addon updater unregister
#     # addon_updater_ops.unregister()
#
#     # register the example panel, to show updater buttons
#     for cls in reversed(classes):
#         bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
