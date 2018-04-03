# script = "/media/nishida-stef-ubuntu/3A625DAF625D711D/FACS_pipeline/blender/AU_change_test2.py"
# exec(compile(open(script).read(), script, 'exec'))
import bpy
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

    _timer = None

    # mb_model = bpy.context.selected_objects[0]

    def modal(self, context, event):
        if event.type in {'RIGHTMOUSE', 'ESC'}:
            self.cancel(context)
            return {'CANCELLED'}

        if event.type == 'TIMER':
            if bpy.data.shape_keys["Key"].key_blocks["Expressions_mouthSmileL_max"].value < 1:
                # change blendshape values
                bpy.data.shape_keys["Key"].key_blocks["Expressions_mouthSmileL_max"].value += 0.05
                print(bpy.data.shape_keys["Key"].key_blocks["Expressions_mouthSmileL_max"].value)

            # if bpy.data.objects["LaBRI_body"]["AU01"].value < 1:
            #     # change blendshape values
            #     bpy.data.objects["LaBRI_body"]["AU01"].value += 0.05
            #     print(bpy.data.shape_keys["Key"].key_blocks["AU01"].value)
            else:
                self.cancel(context)
                return {'CANCELLED'}

        return {'PASS_THROUGH'}

    def execute(self, context):
        print(sys.version)
        # for key in bpy.data.shape_keys["Key"].key_blocks:
        #     print(key)
        # mb_model = scene.objects.get("LaBRI__body")
        # print(mb_model)  # ["AU01"]
        # print(context.object)
        # print(mb_model == context.object)

        # if context.object == scene.objects.get("LaBRI__body"):
        # mb_model = context.object
        mb_model = bpy.context.selected_objects[0]
        print(mb_model)

        print(dir(mb_model))  # [method_name for method_name in dir(mb_model) if callable(getattr(object, method_name))])

        mb_model.data.shape_keys.key_blocks['Expressions_browsMidVert_max'].value = .9
        mb_model.data.shape_keys.key_blocks['Expressions_browsMidVert_max'].keyframe_insert(data_path="value", frame=10)

        # for exp in mb_model:
        #     print(exp)

        # print(mb_model.angry01 == mb_model["angry01"])
        # mb_model["angry01"] = 0.10
        # # mb_model.angry01 = 0.10
        # print(mb_model["angry01"])
        # mb_model["angry01"] = 0.90
        # print(mb_model["angry01"])


        bpy.ops.mbast.keyframe_expression()

        # context.object.AU01 = .50
        # bpy.data.shape_keys["Key"].key_blocks["Expressions_mouthSmileL_max"].value = 0
        # wm = context.window_manager
        # self._timer = wm.event_timer_add(0.01, context.window)
        # wm.modal_handler_add(self)

        return {'RUNNING_MODAL'}

    def cancel(self, context):
        wm = context.window_manager
        wm.event_timer_remove(self._timer)
        print("Modal timer finished")
        # output_path = bpy.context.scene.render.filepath
        # bpy.context.scene.render.filepath = os.path.join("/home/nishida-stef-ubuntu/blender_output", "test.png")
        # bpy.ops.render.opengl(write_still=True)
        # #bpy.ops.image.save_as()
        # bpy.context.scene.render.filepath = output_path


def register():
    bpy.utils.register_class(ModalTimerOperator)


def unregister():
    bpy.utils.unregister_class(ModalTimerOperator)


if __name__ == "__main__":
    register()

    # test call
    bpy.ops.wm.modal_timer_operator()
