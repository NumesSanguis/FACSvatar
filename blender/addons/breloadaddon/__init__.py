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


bl_info = {
    "name": "bReloadAddon",
    "author": "Stef van der Struijk",
    "version": (0, 1),
    "blender": (2, 80, 0),
    "location": "View3D > Sidebar > Create Tab",
    "description": "Does properly what addon_enable() is supposed to do",
    "warning": "",
    "wiki_url": "https://github.com/NumesSanguis/FACSvatar",
    "category": "Development"
    }
    
import sys
import bpy
from bpy.types import Operator, Panel, PropertyGroup
from bpy.props import StringProperty, PointerProperty


# trigger addon reload
class BRELOAD_OT_reload_addon(bpy.types.Operator):
    """Reloads specified add-on"""
    bl_idname = "breload.reload_addon"
    bl_label = "Reloads specified add-on"  # Display name in the interface.
    bl_options = {'REGISTER'}
    
    def execute(self, context):        # execute() is called when running the operator.
        # access properties stored in WindowManager
        breload_properties = context.window_manager.breload_properties
        msg = f"Reloading {breload_properties.breload_name}"
        self.report({'INFO'}, msg)
        print(msg)
        # print(type(breload_properties.breload_name))
        self.addon_enable(breload_properties.breload_name)
        return {'FINISHED'}
        
    def addon_enable(self, module_name):
        """Enables an addon by name."""

        import importlib

        mod = sys.modules.get(module_name)
        mod.__addon_enabled__ = False
        try:
            importlib.reload(mod)
            self.report({'INFO'}, "Reload successful")
            print("Reload successful")
        except Exception as ex:
            # handle_error(ex)
            self.report({'INFO'}, f"Failed: {ex}")
            print(f"Failed: {ex}")
            del sys.modules[module_name]
            return None

        mod.register()
        # * OK loaded successfully! *
        mod.__addon_enabled__ = True
        

# allow addon name modification through interface
class BRELOAD_PT_specifyAddon(Panel):
    bl_label = "bReloadPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    # bl_context = "objectmode"
    bl_category = "bReload"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        # access properties stored in WindowManager
        breload_properties = context.window_manager.breload_properties
        # create string field
        self.layout.prop(breload_properties, "breload_name")
        # create button to reload addon
        self.layout.operator("breload.reload_addon")
        

# global access to properties
class BReloadProperties(PropertyGroup):
    breload_name: StringProperty(name="Addon",
                              description="Reload specified add-on",
                              default="blendzmq",
                              )


classes = (
    BRELOAD_OT_reload_addon,
    BRELOAD_PT_specifyAddon,
    BReloadProperties,
    )

# store keymaps here to access after registration
addon_keymaps = []

# register, unregister = bpy.utils.register_classes_factory(classes)
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
        
    # make globally available through WindowManager
    wm = bpy.types.WindowManager
    wm.breload_properties = PointerProperty(type=BReloadProperties)

    # Note that in background mode (no GUI available), keyconfigs are not available either,
    # kc = bpy.context.window_manager.keyconfigs.addon
    # if kc:
    #     # set keyboard shortcut
    #     # for 'EMPTY', 'VIEW_3D', 'IMAGE_EDITOR', 'NODE_EDITOR'
    #     km = kc.keymaps.new(name='bReload addon', space_type='3D')
    #     kmi = km.keymap_items.new("breload.reload_addon", 'R', 'PRESS', ctrl=True, shift=True)
    #     addon_keymaps.append((km, kmi))

def unregister():
    # Note: when unregistering, it's usually good practice to do it in reverse order you registered.
    # Can avoid strange issues like keymap still referring to operators already unregistered...
    # handle the keymap
    # for km, kmi in addon_keymaps:
    #     # if kmi.name == "breload.reload_addon"
    #     km.keymap_items.remove(kmi)
    # addon_keymaps.clear()

    for cls in classes:
        bpy.utils.unregister_class(cls)
        
    del bpy.types.WindowManager.breload_properties
