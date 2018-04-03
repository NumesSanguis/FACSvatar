# script = "/media/nishida-stef-ubuntu/3A625DAF625D711D/FACS_pipeline/blender/facsvatar_zeromq.py"
# exec(compile(open(script).read(), script, 'exec'))
import bpy
import os
import sys
import asyncio
sys.path.append('/home/nishida-stef-ubuntu/anaconda3/envs/blender/lib/python3.5/site-packages')
import zmq
#from zmq.asyncio import Context
import json

context = bpy.context
scene = context.scene


class FACSvatarZeroMQ(bpy.types.Operator):
    """ZeroMQ subscriber for FACS data (and head movement)"""
    bl_idname = "wm.facsvatar_zeromq"
    bl_label = "FACSvatar ZeroMQ"
    # bl_options = {'REGISTER'}

    _timer = None

    def __init__(self, address='127.0.0.1', port='5572'):
        print("FACSvatar ZeroMQ initialising...")

        # init ZeroMQ subscriber
        url = "tcp://{}:{}".format(address, port)
        ctx = zmq.Context.instance()
        self.sub = ctx.socket(zmq.SUB)
        self.sub.connect(url)
        self.sub.setsockopt(zmq.SUBSCRIBE, b'')

        self.frame = bpy.context.scene.frame_current
        self.pause_loop_count = 0

        print("FACSvatar ZeroMQ initialised")

    def modal(self, context, event):
        if event.type in {'ESC'}:  # 'RIGHTMOUSE',
            self.cancel(context)
            return {'CANCELLED'}

        if event.type == 'TIMER':
            # get the current selected object
            mb_model = bpy.context.selected_objects[0]  # bpy.data.objects["FACSvatar_body"]
            # print(mb_model)

            # only run this code if the object selected is a MB character:
            # if "angry01" in mb_model:
            if mb_model.data.shape_keys:  # and \
                    # hasattr(mb_model.data.shape_keys.key_blocks, 'Expressions_browsMidVert_max'):
                # alternate whether to receive message or not
                if self.pause_loop_count >= 5:
                    # get ZeroMQ message
                    msg_data = self.sub.recv_multipart()[1].decode('utf-8')

                    # message data is not None
                    if msg_data:
                        msg_json = json.loads(msg_data)
                        #print(msg_json)
                        # mb_model = context.object
                        #print(mb_model)

                        # set-up facial expression
                        # au01 = msg_json['data']['facs']['AU01_r']
                        # print(au01)
                        # mb_model.AU01 = au01
                        # print(mb_model.AU01)

                        for bs in msg_json['data']['blend_shape']:
                            # print(bs)
                            # MB fix Caucasian female
                            # if not bs == "Expressions_eyeClosedR_max":
                            val = msg_json['data']['blend_shape'][bs]
                            mb_model.data.shape_keys.key_blocks[bs].value = val
                            mb_model.data.shape_keys.key_blocks[bs] \
                                .keyframe_insert(data_path="value", frame=self.frame)

                        # brow = msg_json['data']['blend_shape']['Expressions_browsMidVert_max']
                        # mb_model.data.shape_keys.key_blocks['Expressions_browsMidVert_max'].value = brow
                        # mb_model.data.shape_keys.key_blocks['Expressions_browsMidVert_max']\
                        #     .keyframe_insert(data_path="value", frame=self.frame)
                        # active_shape_key_index

                        # save as keyframe
                        bpy.context.scene.frame_set(self.frame)
                        # bpy.ops.mbast.keyframe_expression()  # MB function

                        self.frame += 1

                    # None means finished TODO not working
                    else:
                        print("No more messages")
                        return {'CANCELLED'}

                    self.pause_loop_count = 0

                else:
                    self.pause_loop_count += 1

            else:
                print("No MB character selected")
                return {'CANCELLED'}

        return {'PASS_THROUGH'}

    def execute(self, context):
        print("FACSvatar ZeroMQ executing...")

        wm = context.window_manager
        self._timer = wm.event_timer_add(0.3, context.window)
        wm.modal_handler_add(self)

        print("FACSvatar ZeroMQ executed")

        return {'RUNNING_MODAL'}

    # async def echo_startter(self):
    #     process = await asyncio.create_subprocess_exec()

    def cancel(self, context):
        wm = context.window_manager
        wm.event_timer_remove(self._timer)

    async def echo(self):
        print("echo")
        while True:
            await asyncio.sleep(.3)


def register():
    bpy.utils.register_class(FACSvatarZeroMQ)


def unregister():
    bpy.utils.unregister_class(FACSvatarZeroMQ)


if __name__ == "__main__":
    print("starting FACSvatar ZeroMQ")
    register()

    # call
    bpy.ops.wm.facsvatar_zeromq()
