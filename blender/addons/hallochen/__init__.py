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

# Blender tutorial
# https://www.youtube.com/watch?v=Fr1HN0XgB58

import bpy
from math import pi, sin, cos
import colorsys
from random import TWOPI


bl_info = {
    "name": "hallochen",
    "author": "Stef van der Struijk",
    "version": (0, 1),
    "blender": (2, 80, 0),
    "location": "View3D > Tools > hallochen",
    "description": "How to make a Blender add-on - The Test",
    "warning": "",
    'wiki_url': "",
    'tracker_url': "",
    "category": "Tests"
}



class ObjectMoveX(bpy.types.Operator):
    """My Object Moving Script"""      # Use this as a tooltip for menu items and buttons.
    bl_idname = "object.move_x"        # Unique identifier for buttons and menu items to reference.
    bl_label = "Move X by One"         # Display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}  # Enable undo for the operator.

    # def execute(self, context):        # execute() is called when running the operator.
    #
    #     # The original script
    #     scene = context.scene
    #     for obj in scene.objects:
    #         obj.location.x -= 1.0
    #
    #     return {'FINISHED'}            # Lets Blender know the operator finished successfully.

    def execute(self, context):        # execute() is called when running the operator.
        # Center of sphere.
        centerz = 0.0
        centery = 0.0
        centerx = 0.0

        # Sphere diameter.
        diameter = 8.0

        # Baseline size of each cube.
        sz = 3.0 / diameter

        latitude = 16
        longitude = latitude * 2

        invlatitude = 1.0 / (latitude - 1)
        invlongitude = 1.0 / (longitude - 1)
        iprc = 0.0
        jprc = 0.0
        phi = 0.0
        theta = 0.0

        for i in range(0, latitude, 1):
            iprc = i * invlatitude
            phi = pi * (i + 1) * invlatitude

            sinphi = sin(phi)
            cosphi = cos(phi)

            rad = 0.01 + sz * abs(sinphi) * 0.99
            z = cosphi * diameter

            for j in range(0, longitude, 1):
                jprc = j * invlongitude
                theta = TWOPI * j / longitude

                sintheta = sin(theta)
                costheta = cos(theta)

                x = sinphi * costheta * diameter
                y = sinphi * sintheta * diameter

                bpy.ops.object.light_add(type='AREA', radius=1, location=(centerx + x, centery + y, centerz + z))
                # bpy.ops.mesh.primitive_cube_add(location=(centerx + x, centery + y, centerz + z), size=rad)

                # Cache the current object being worked on.
                current = bpy.context.object

                # Name the object and its mesh data.
                # Pad the number up to 2 places.
                current.name = 'Cube ({0:0>2d}, {1:0>2d})'.format(i, j)
                current.data.name = 'Mesh ({0:0>2d}, {1:0>2d})'.format(i, j)

                # Rotate the cube to match the sphere's surface.
                current.rotation_euler = (0.0, phi, theta)

                # Create a material.
                mat = bpy.data.materials.new(name='Material ({0:0>2d}, {1:0>2d})'.format(i, j))

                # Assign a diffuse color to the material using colorsys's HSV-RGB conversion.
                mat.diffuse_color = (*colorsys.hsv_to_rgb(jprc, 1.0 - iprc, 1.0), 1)
        current.data.materials.append(mat)


class HelloButton(bpy.types.Panel):  # bpy.types.Operator
    """My hello saying script"""  # Use this as a tooltip for menu items and buttons.
    bl_idname = "OBJECT_PT_hallochen"  # Unique identifier for buttons and menu items to reference.
    bl_label = "Hallochen - Say hello"  # Display name in the interface.
    # bl_options = {'REGISTER', 'UNDO'}  # Enable undo for the operator.
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Hallo"

    # def execute(self, context):  # execute() is called when running the operator.
    #     # The original script
    #     scene = context.scene
    #     for obj in scene.objects:
    #         obj.location.y += 2.0
    #     # print("Hello")
    #
    #     return {'FINISHED'}  # Lets Blender know the operator finished successfully.

    def move_object(self, obj):
        if obj:
            obj.location.z += 1.0

        return {'FINISHED'}

    # custom UI: https://blender.stackexchange.com/questions/57306/how-to-create-a-custom-ui
    def draw(self, context):
        layout = self.layout
        obj = context.object

        box = layout.box()
        if obj:
            box.label(text=f"Hallo {obj.name}")
        else:
            box.label(text=f"No object selected :(")

        row = layout.row()
        row.label(text="Add!")
        row.operator("mesh.primitive_cube_add")

        row = layout.row()
        row.label(text="Move!")
        row.operator("object.move_x", text="Execute me")  # , icon='ARMATURE_DATA'

        row = layout.row()
        row.label(text="Move it..")
        #row.operator("self.move_object", text="up!")


classes = (
    HelloButton,
    ObjectMoveX,
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
