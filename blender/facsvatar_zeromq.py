# script = "/*path*/blender/facsvatar_zeromq.py"
# exec(compile(open(script).read(), script, 'exec'))
import bpy
import os
import sys
import asyncio
sys.path.append('/*path*/anaconda3/envs/blender/lib/python3.5/site-packages')
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

    def __init__(self, address='127.0.0.1', port='5572', head_movement=True):
        print("FACSvatar ZeroMQ initialising...")

        self.head_movement = head_movement

        # init ZeroMQ subscriber
        url = "tcp://{}:{}".format(address, port)
        ctx = zmq.Context.instance()
        self.sub = ctx.socket(zmq.SUB)
        self.sub.connect(url)
        self.sub.setsockopt(zmq.SUBSCRIBE, b'')

        self.frame = bpy.context.scene.frame_current
        self.pause_loop_count = 0

        self.find_MBLabModel()

        print("FACSvatar ZeroMQ initialised")

    def find_MBLabModel(self):
        # get manuel bastioni character in scene
        self.mb_obj = None
        for obj in scene.objects:
            print(obj)
            if obj.name.endswith("_armature") or obj.name.startswith("MBlab_sk"):
                print("MBLab object found!")
                self.mb_obj = obj
                self.head_bones = [self.mb_obj.pose.bones['head'], self.mb_obj.pose.bones['neck']]
                for bone in self.head_bones:
                    # https://blender.stackexchange.com/questions/28159/how-to-rotate-a-bone-using-python
                    # Set rotation mode to Euler XYZ, easier to understand than default quaternions
                    bone.rotation_mode = 'XYZ'

                # find child *_body of MB character
                for child in self.mb_obj.children:
                    print(child)

                    if child.name.endswith("_body") or child.name.startswith("MBlab_bd"):
                        self.mb_body = child
                        print("Body found!")
                        print(self.mb_body)

                # stop search, found MB object
                break

    # set Shape Keys for chestExpansion
    def breathing(self, full_cycle=1):
        # set Shape Key values
        self.mb_body.data.shape_keys.key_blocks["Expressions_chestExpansion_min"].value = full_cycle
        self.mb_body.data.shape_keys.key_blocks["Expressions_chestExpansion_max"].value = abs(full_cycle - 1)

        # insert keyframes
        self.mb_body.data.shape_keys.key_blocks["Expressions_chestExpansion_min"] \
            .keyframe_insert(data_path="value", frame=self.frame)
        self.mb_body.data.shape_keys.key_blocks["Expressions_chestExpansion_max"] \
            .keyframe_insert(data_path="value", frame=self.frame)

    # match head pose name with bones in blender
    def rotate_head_bones(self, xyz, pose, inv=1):
        # head bone
        self.head_bones[0].rotation_euler[xyz] = pose * .95 * inv
        # neck bone
        self.head_bones[1].rotation_euler[xyz] = pose * .5 * inv

    def modal(self, context, event):
        if event.type in {'ESC'}:  # 'RIGHTMOUSE',
            self.cancel(context)
            return {'CANCELLED'}

        if event.type == 'TIMER':
            print("Frame: {}".format(self.frame))

            # if self.pause_loop_count >= 5:
            # get ZeroMQ message
            msg = self.sub.recv_multipart()

            # check not finished; timestamp is empty (b'')
            if msg[1]:
                # self.blendshapes_json = json.loads(msg[3].decode('utf8'))
                # self.head_json = json.loads(msg[4].decode('utf8'))
                msg[2] = json.loads(msg[2].decode('utf8'))

                # print(dir(self.mb_obj))
                # if object was not found in initialisation
                try:
                    self.mb_obj
                except:
                    self.find_MBLabModel()

                # # set pose only if pose data is available and not empty
                if self.head_movement:
                    if 'pose' in msg[2] and msg[2]['pose']:
                        # set head rotation
                        if len(self.head_bones) == 2:
                            bpy.context.scene.objects.active = self.mb_obj
                            bpy.ops.object.mode_set(mode='POSE')  # mode for bone rotation

                            # for pose_name in enumerate(msg_json['data']['head_pose']):
                            pose_head = msg[2]['pose']
                            self.rotate_head_bones(0, pose_head['pose_Rx'])  # pitch
                            self.rotate_head_bones(1, pose_head['pose_Ry'], -1)  # jaw
                            self.rotate_head_bones(2, pose_head['pose_Rz'], -1)  # roll

                            # set key frames
                            bpy.ops.object.mode_set(mode='OBJECT')  # mode for key frame
                            self.head_bones[0].keyframe_insert(data_path="rotation_euler", frame=self.frame)
                            self.head_bones[1].keyframe_insert(data_path="rotation_euler", frame=self.frame)

                        else:
                            print("Head bone and neck bone not found")

                    else:
                        print("No pose data found")

                else:
                    print("Head movement data ignored")

                # set blendshapes only if blendshape data is available and not empty
                if 'blendshapes' in msg[2] and msg[2]['blendshapes']:
                    # if object was not found in initialisation
                    try:
                        self.mb_body
                    except:
                        self.find_MBLabModel()

                    # set all shape keys values
                    bpy.context.scene.objects.active = self.mb_body
                    for bs in msg[2]['blendshapes']:
                        # skip setting shape keys for breathing from data
                        if not bs.startswith("Expressions_chestExpansion"):
                            # print(bs)
                            # MB fix Caucasian female
                            # if not bs == "Expressions_eyeClosedR_max":
                            val = msg[2]['blendshapes'][bs]
                            self.mb_body.data.shape_keys.key_blocks[bs].value = val
                            self.mb_body.data.shape_keys.key_blocks[bs] \
                                .keyframe_insert(data_path="value", frame=self.frame)

                else:
                    print("No blendshapes data found")

                # breathing (cycles of 3 sec)
                if self.frame == 0:
                    self.breathing()

                # every 1.5 sec (30 fps)
                elif self.frame % 45 == 0:
                    # full cycle
                    if self.frame % 90 == 0:
                        self.breathing(full_cycle=1)
                    # half cycle
                    else:
                        self.breathing(full_cycle=0)

                # save as keyframe
                # bpy.context.scene.frame_set(self.frame)
                # bpy.ops.mbast.keyframe_expression()  # MB function

                self.frame += 1

            # None means finished TODO not working
            else:
                print("No more messages")
                return {'CANCELLED'}

            # self.pause_loop_count = 0

            # else:
            #     self.pause_loop_count += 1

        return {'PASS_THROUGH'}

    def execute(self, context):
        print("FACSvatar ZeroMQ executing...")

        # only add timer if MB character in scene
        if self.mb_obj:
            print("Found Manuel Bastioni object")
            wm = context.window_manager
            self._timer = wm.event_timer_add(0.04, context.window)
            wm.modal_handler_add(self)
        else:
            print("No Manuel Bastioni object in scene")
            return {'CANCELLED'}

        print("FACSvatar ZeroMQ executed")

        return {'RUNNING_MODAL'}

    # async def echo_startter(self):
    #     process = await asyncio.create_subprocess_exec()

    def cancel(self, context):
        wm = context.window_manager
        wm.event_timer_remove(self._timer)

    # async def echo(self):
    #     print("echo")
    #     while True:
    #         await asyncio.sleep(.3)


def register():
    bpy.utils.register_class(FACSvatarZeroMQ)


def unregister():
    bpy.utils.unregister_class(FACSvatarZeroMQ)


if __name__ == "__main__":
    print("starting FACSvatar ZeroMQ")
    register()

    # call
    bpy.ops.wm.facsvatar_zeromq()
