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
    def __init__(self):
        self.au_to_blendshapes = AUtoBlendShapes()

    async def facs_to_blendshape(self, au_dict):  # , id_cb, type_cb
        # au_dict: received facs values in JSON format

        # print("----------------------------")
        # print(type(au_dict))
        # # change JSON to Python internal dict
        # facs_dict = json.loads(au_dict)
        # print(type(facs_dict))
        # print("---")
        # pretty printing
        #print(json.dumps(facs_dict, indent=4))  # , indent=4, sort_keys=True

        # change facs to blendshapes
        # TODO if None (should not receive any None prob)
        blend_dict = self.au_to_blendshapes.output_blendshapes(au_dict)
        # print(blend_dict)

        # add blend dict under 'data' to received message and remove FACS
        # msg_dict = self.structure_dict(facs_dict, blend_dict)

        # publish blendshapes
        # print(blend_dict)
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
        self.blendshape = BlendShapeMsg()

    async def blenshape_sub_pub(self):
        # keep listening to all published message on topic 'facs'
        while True:
            msg = await self.sub_socket.recv_multipart()
            print("message: {}".format(msg))

            # check not finished; timestamp is empty (b'')
            if msg[1]:
                # process message
                msg[2] = json.loads(msg[2].decode('utf-8'))
                # check not empty
                if msg[2]:
                    # transform Action Units to Blend Shapes
                    msg[2]['blendshapes'] = await self.blendshape.facs_to_blendshape(msg[2]['au_r'])
                    # remove au_r from dict
                    msg[2].pop('au_r')

                print(msg)
                # async always needs `send_multipart()`
                await self.pub_socket.send_multipart([msg[0],  # topic
                                          msg[1],  # timestamp
                                          # data in JSON format or empty byte
                                          json.dumps(msg[2]).encode('utf-8')
                                          ])

            # send message we're done
            else:
                print("No more messages to publish; Blend Shapes done")
                await self.pub_socket.send_multipart([msg[0], b'', b''])


if __name__ == '__main__':
    # command line arguments
    parser = argparse.ArgumentParser()

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

    args, leftovers = parser.parse_known_args()
    print("The following arguments are used: {}".format(args))
    print("The following arguments are ignored: {}\n".format(leftovers))

    # init FACSvatar message class
    facsvatar_messages = FACSvatarMessages(**vars(args))
    # start processing messages; give list of functions to call async
    facsvatar_messages.start([facsvatar_messages.blenshape_sub_pub])
