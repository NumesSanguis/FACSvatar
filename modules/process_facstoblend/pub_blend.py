import os
import sys
import argparse
import six
import json
from copy import deepcopy
import asyncio
import zmq.asyncio
from zmq.asyncio import Context
import traceback
import logging

# own imports; if statement for documentation
if __name__ == '__main__':
    from au2blendshapes_mb import AUtoBlendShapes  # when using Manuel Bastioni models
    #from au2blendshapes_mh import AUtoBlendShapes  # when using FACSHuman models
else:
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
class NetworkSetup:
    """
    ZeroMQ network setup
    """
    def __init__(self, address='127.0.0.1', port_facs='5571', port_blend='5572'):
        self.url = "tcp://{}:{}".format(address, port_facs)
        self.ctx = Context.instance()

        self.url2 = "tcp://{}:{}".format(address, port_blend)
        self.ctx2 = Context.instance()

        self.blendshape = BlendShapeMsg()

        # activate publishers / subscribers
        asyncio.get_event_loop().run_until_complete(asyncio.wait([
            self.blenshape_sub_pub(),
        ]))

    async def blenshape_sub_pub(self):
        # setup subscriber
        sub = self.ctx.socket(zmq.SUB)
        sub.connect(self.url)
        sub.setsockopt(zmq.SUBSCRIBE, b'')
        print("BlendShape sub initialized")

        pub = self.ctx2.socket(zmq.PUB)
        pub.bind(self.url2)
        print("BlendShape pub initialized")

        # without try statement, no error output
        try:
            # keep listening to all published message on topic 'facs'
            while True:
                msg = await sub.recv_multipart()
                print("message: {}".format(msg))

                # check not finished; timestamp is empty (b'')
                if msg[1]:
                    # process message
                    msg[2] = json.loads(msg[2].decode('utf-8'))
                    # transform Action Units to Blend Shapes
                    msg[2]['blendshapes'] = await self.blendshape.facs_to_blendshape(msg[2]['au_r'])
                    # remove au_r from dict
                    msg[2].pop('au_r')

                    # async always needs `send_multipart()`
                    print(msg)

                    await pub.send_multipart([msg[0],  # topic
                                              msg[1],  # timestamp
                                              # data in JSON format or empty byte
                                              json.dumps(msg[2]).encode('utf-8')
                                              ])

                # send message we're done
                else:
                    print("No more messages to publish; Blend Shapes done")
                    await pub.send_multipart([msg[0], b'', b''])

        except Exception as e:
            print("Error with blendshape")
            # print(e)
            logging.error(traceback.format_exc())
            print()

        finally:
            # TODO disconnect pub/sub
            pass

        # # get FACS message
        # async for msg in self.blendshape.blendshape_msg_gen():
        #     print(msg)
        #     # publish blendshape
        #     await pub.send_multipart([b'blendshapes', msg.encode('utf-8')])


if __name__ == '__main__':
    # get ZeroMQ version
    print("Current libzmq version is %s" % zmq.zmq_version())
    print("Current  pyzmq version is %s" % zmq.pyzmq_version())

    # command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip_pub", default=argparse.SUPPRESS,
                        help="IP (e.g. 192.168.x.x) of where to pub to; Default 127.0.0.1 (local)")
    parser.add_argument("--port_pub", default=argparse.SUPPRESS,
                        help="Port of where to pub to; Default 5572")
    parser.add_argument("--ip_sub", default=argparse.SUPPRESS,
                        help="IP (e.g. 192.168.x.x) of where to sub to; Default 127.0.0.1 (local)")
    parser.add_argument("--port_sub", default=argparse.SUPPRESS,
                        help="Port of where to sub to; Default 5571")

    args, leftovers = parser.parse_known_args()
    NetworkSetup(**vars(args))
