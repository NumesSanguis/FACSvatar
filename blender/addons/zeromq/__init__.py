"""Passing data/commands in&out of Blender through the ZeroMQ messaging library"""

import bpy

bl_info = {  # https://wiki.blender.org/wiki/Process/Addons/Guidelines/metainfo
    "name": "zeromq_data",
    "author": "Stef van der Struijk",
    "version": (0, 1),
    "blender": (2, 80, 0),
    "location": "View3D > Tools > zeromq",
    "description": "Connects Blender with outside programs through ZeroMQ",
    "warning": "",
    "wiki_url": "https://github.com/NumesSanguis/FACSvatar",
    "category": "Development",
}

# https://docs.blender.org/api/blender2.8/bpy.app.timers.html


class OBJECT_OT_zeromq_connect(bpy.types.Operator):
    bl_idname = "object.zeromq_connect"
    bl_label = "Setting-up ZeroMQ connection"
    bl_options = {'REGISTER'}  # , 'UNDO'

    prop_ip: bpy.props.StringProperty(name="IP", default="127.0.0.1")  # , options={"PROPORTIONAL"}

    def execute(self, context):
        msg = f"Connecting on {self.prop_ip}"
        self.report({'INFO'}, msg)
        print(msg)
        return {'FINISHED'}


class VIEW3D_PT_zeromq(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""
    bl_label = "ZeroMQ setup Layout"
    bl_idname = "VIEW3D_PT_zeromq_layout"
    bl_space_type = 'VIEW_3D'  # 'PROPERTIES'
    bl_region_type = 'UI'  # 'WINDOW'
    bl_category = "ZeroMQ"
    # bl_context = "scene"

    # prop_ip: bpy.props.StringProperty(name="IP", default="127.0.0.1")

    def draw(self, context):
        scene = context.scene
        # zmq_props = self.layout.operator('object.zeromq_connect')

        # Create a simple row.
        self.layout.label(text="https://github.com/NumesSanguis/FACSvatar")

        #row = self.layout.row()
        #row.operator("self.reload_addon", text="Reload me")
        #row.prop(scene, "frame_start")
        #row.prop(scene, "frame_end")

        box = self.layout.box()
        box.label(text="ZeroMQ settings:")
        # box.prop(zmq_props, "prop_ip")
        context.window_manager.prop_ip: bpy.props.StringProperty(name="IP", default="127.0.0.1")
        box.prop(context.window_manager, "prop_ip")
        # box.prop(self.layout.operator('object.zeromq_connect'), "prop_ip")
        # self.layout.operator('object.zeromq_connect').prop_ip = context.window_manager.your_wm_property
        # box.operator('object.zeromq_connect').prop_ip
        #box.prop(scene, "frame_start")
        # box.operator('object.zeromq_connect', text="Reload me")

        # save the IP address into the add-on preferences


# bpy.types.window_manager = bpy.props.StringProperty(name="IP", default="127.0.0.1")


classes = (
    OBJECT_OT_zeromq_connect,
    VIEW3D_PT_zeromq,
    # ZeroMQQueue,
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()