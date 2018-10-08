# Copyright (c) Stef van der Struijk
# License: GNU Lesser General Public License


import os
import sys
import argparse
import json


# own imports; if statement for documentation
if __name__ == '__main__':
    sys.path.append("..")
    from facsvatarzeromq import FACSvatarZeroMQ
    from au2blendshapes_mb import AUtoBlendShapes  # when using Manuel Bastioni models
    #from au2blendshapes_mh import AUtoBlendShapes  # when using FACSHuman models
else:
    from modules.facsvatarzeromq import FACSvatarZeroMQ
    from .au2blendshapes_mb import AUtoBlendShapes  # when using Manuel Bastioni models
    # from .au2blendshapes_mh import AUtoBlendShapes  # when using FACSHuman models


# process everything that is received
class BlendShapeMsg:
    def __init__(self, au_folder):
        self.au_to_blendshapes = AUtoBlendShapes(au_folder)

    async def facs_to_blendshape(self, au_dict):
        # au_dict: received facs values in JSON format

        # change facs to blendshapes
        # TODO if None (should not receive any None prob)
        blend_dict = self.au_to_blendshapes.output_blendshapes(au_dict)

        return blend_dict

    # # restructure to frame, timestamp, data={head_pose, blendshape}
    # def structure_dict(self, facs_dict, blend_dict):
    #     #   restructure
    #     # copy whole message except data part
    #     msg_dict = {k: v for k, v in facs_dict.items() if k is not 'data'}
    #     # init key 'data' again
    #     msg_dict['data'] = {}
    #     # copy 'head_pose' back into data
    #     msg_dict['data']['head_pose'] = deepcopy(facs_dict['data']['head_pose'])
    #     msg_dict['data']['blend_shape'] = deepcopy(blend_dict)
    #
    #     return msg_dict


# client to message broker server
class FACSvatarMessages(FACSvatarZeroMQ):
    """Receives FACS and Head movement data; FACS --> Blend Shapes; Publish new data"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.blendshape = BlendShapeMsg(self.misc["au_folder"])

    async def blenshape_sub_pub(self):
        # keep listening to all published message on topic 'facs'
        while True:
            # msg = await self.sub_socket.recv_multipart()
            key, timestamp, data = await self.sub_socket.sub()
            print("Received message: {}".format([key, timestamp, data]))

            # check not finished; timestamp is empty (b'')
            if timestamp:
                # check not empty
                if data:
                    # transform Action Units to Blend Shapes
                    data['blendshapes'] = await self.blendshape.facs_to_blendshape(data['au_r'])
                    # remove au_r from dict
                    data.pop('au_r')

                print(data)
                await self.pub_socket.pub(data, key)

            # send message we're done
            else:
                print("No more messages to publish; Blend Shapes done")
                await self.pub_socket.pub(b'', key)


if __name__ == '__main__':
    # command line arguments
    parser = argparse.ArgumentParser()

    # logging commandline arguments
    parser.add_argument("--module_id", default="facstoblend_1",
                        help="Module id for different instances of same module")
    parser.add_argument("--loglevel", default=argparse.SUPPRESS,
                        help="Specify how detailed the terminal/logfile output should be;"
                             "DEBUG, INFO, WARNING, ERROR or CRITICAL; Default: INFO")

    # subscriber to FACS / head movement data
    parser.add_argument("--sub_ip", default=argparse.SUPPRESS,
                        help="IP (e.g. 192.168.x.x) of where to sub to; Default: 127.0.0.1 (local)")
    parser.add_argument("--sub_port", default="5571",
                        help="Port of where to sub to; Default: 5571")
    parser.add_argument("--sub_key", default=argparse.SUPPRESS,
                        help="Key for filtering message; Default: '' (all keys)")
    parser.add_argument("--sub_bind", default=False,
                        help="True: socket.bind() / False: socket.connect(); Default: False")

    # publisher of Blend Shape / head movement data
    parser.add_argument("--pub_ip", default=argparse.SUPPRESS,
                        help="IP (e.g. 192.168.x.x) of where to pub to; Default: 127.0.0.1 (local)")
    parser.add_argument("--pub_port", default="5572",
                        help="Port of where to pub to; Default: 5572")
    parser.add_argument("--pub_key", default="blendshapes.human",
                        help="Key for filtering message; Default: blendshapes.human")
    parser.add_argument("--pub_bind", default=True,
                        help="True: socket.bind() / False: socket.connect(); Default: True")

    # module specific commandline arguments
    parser.add_argument("--au_folder", default="au_json",
                        help="Name of folder with AU conversion files; Default: au_json")

    args, leftovers = parser.parse_known_args()
    print("The following arguments are used: {}".format(args))
    print("The following arguments are ignored: {}\n".format(leftovers))

    # init FACSvatar message class
    facsvatar_messages = FACSvatarMessages(**vars(args))
    # start processing messages; give list of functions to call async
    facsvatar_messages.start([facsvatar_messages.blenshape_sub_pub])
