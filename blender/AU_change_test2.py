# script = "/media/nishida-stef-ubuntu/3A625DAF625D711D/FACS_pipeline/blender/AU_change_test2.py"
# exec(compile(open(script).read(), script, 'exec'))
import bpy
import os


class ModalTimerOperator(bpy.types.Operator):
    """Operator which runs its self from a timer"""
    bl_idname = "wm.modal_timer_operator"
    bl_label = "Modal Timer Operator"

    _timer = None

    def modal(self, context, event):
        if event.type in {'RIGHTMOUSE', 'ESC'}:
            self.cancel(context)
            return {'CANCELLED'}

        if event.type == 'TIMER':
            if bpy.data.shape_keys["Key"].key_blocks["Expressions_mouthSmileL_max"].value < 1:
                # change blendshape values
                bpy.data.shape_keys["Key"].key_blocks["Expressions_mouthSmileL_max"].value += 0.05
                print(bpy.data.shape_keys["Key"].key_blocks["Expressions_mouthSmileL_max"].value)
            else:
                self.cancel(context)
                return {'CANCELLED'}

        return {'PASS_THROUGH'}

    def execute(self, context):
        bpy.data.shape_keys["Key"].key_blocks["Expressions_mouthSmileL_max"].value = 0
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.01, context.window)
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        wm = context.window_manager
        wm.event_timer_remove(self._timer)
        print("Modal timer finished")
        output_path = bpy.context.scene.render.filepath
        bpy.context.scene.render.filepath = os.path.join("/home/nishida-stef-ubuntu/blender_output", "test.png")
        bpy.ops.render.opengl(write_still=True)
        #bpy.ops.image.save_as()
        bpy.context.scene.render.filepath = output_path


def register():
    bpy.utils.register_class(ModalTimerOperator)


def unregister():
    bpy.utils.unregister_class(ModalTimerOperator)


if __name__ == "__main__":
    register()

    # test call
    bpy.ops.wm.modal_timer_operator()
