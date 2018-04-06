# script = "/*path*/blender/facsvatar_zeromq.py"
# exec(compile(open(script).read(), script, 'exec'))
import bpy
import math
import os
import sys
#sys.path.append('/home/nishida-stef-ubuntu/anaconda3/envs/zeromq/lib/python3.6/site-packages')
#import zmq

context = bpy.context
scene = context.scene


class ModalTimerOperator(bpy.types.Operator):
    """Operator which runs its self from a timer"""
    bl_idname = "wm.modal_timer_operator"
    bl_label = "Modal Timer Operator"

    def __init__(self):
        self.mb_obj = None

        for obj in scene.objects:
            if obj.name.endswith("_armature"):
                self.mb_obj = obj

                # find child *_body of MB character
                for child in self.mb_obj.children:
                    if child.name.endswith("_body"):
                        self.mb_body = child
                        print(self.mb_body)

                break

        if self.mb_obj:
            print("Found Manuel Bastioni object")
            print(dir(self.mb_obj))



        else:
            print("No Manuel Bastioni object in scene")

    def execute(self, context):
        print(sys.version)
        # print(dir(bpy.data.objects))

        # ob = bpy.data.objects['FACSvatar_asian_female_armature']
        # ob = bpy.ops.object.select_pattern(pattern="*_armature")
        # print(ob)
        bpy.context.scene.objects.active = self.mb_obj
        bpy.ops.object.mode_set(mode='POSE')  # mode for bone rotation

        # headbone
        bone_head = self.mb_obj.pose.bones['head']
        print(bone_head)
        # Set rotation mode to Euler XYZ, easier to understand
        # than default quaternions
        bone_head.rotation_mode = 'XYZ'

        # rotate
        print("rotate")
        bone_head.rotation_euler[0] = math.pi  # .rotate_axis('Z', math.pi)

        bpy.ops.object.mode_set(mode='OBJECT')  # mode for key frame
        # insert a keyframe
        bone_head.keyframe_insert(data_path="rotation_euler", frame=0)

        self.mb_body.data.shape_keys.key_blocks["Expressions_chestExpansion_max"].value = 0
        self.mb_body.data.shape_keys.key_blocks["Expressions_chestExpansion_max"] \
            .keyframe_insert(data_path="value", frame=0)

        self.mb_body.data.shape_keys.key_blocks["Expressions_browSqueezeL_max"].value = 1
        self.mb_body.data.shape_keys.key_blocks["Expressions_browSqueezeL_max"] \
            .keyframe_insert(data_path="value", frame=10)

        self.mb_body.data.shape_keys.key_blocks["Expressions_chestExpansion_max"].value = 1
        self.mb_body.data.shape_keys.key_blocks["Expressions_chestExpansion_max"] \
            .keyframe_insert(data_path="value", frame=20)

        # mb_model = scene.objects.get("LaBRI__body")
        # print(mb_model)  # ["AU01"]
        # print(context.object)
        # print(mb_model == context.object)

        # if context.object == scene.objects.get("LaBRI__body"):
        # mb_model = context.object
        # mb_model = bpy.context.selected_objects[0]
        # print(mb_model)
        #
        # print(dir(mb_model))  # [method_name for method_name in dir(mb_model) if callable(getattr(object, method_name))])

        # mb_model.data.shape_keys.key_blocks['Expressions_browsMidVert_max'].value = .9
        # mb_model.data.shape_keys.key_blocks['Expressions_browsMidVert_max'].keyframe_insert(data_path="value", frame=10)

        return {'RUNNING_MODAL'}


def register():
    bpy.utils.register_class(ModalTimerOperator)


def unregister():
    bpy.utils.unregister_class(ModalTimerOperator)


if __name__ == "__main__":
    register()

    # test call
    bpy.ops.wm.modal_timer_operator()
