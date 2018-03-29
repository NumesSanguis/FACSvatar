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

# own imports
from au2blendshapes_mb import AUtoBlendShapes  # when using Manuel Bastioni models
#from au2blendshapes_mh import AUtoBlendShapes  # when using FACSHuman models


# process everything that is received
class BlendShapeMsg:
    def __init__(self):
        self.au_to_blendshapes = AUtoBlendShapes()

    async def facs_to_blendshape(self, facs_json):  # , id_cb, type_cb
        # facs_json: received facs values in JSON format

        print("----------------------------")
        print(type(facs_json))
        # change JSON to Python internal dict
        facs_dict = json.loads(facs_json)
        print(type(facs_dict))
        print("---")
        # pretty printing
        #print(json.dumps(facs_dict, indent=4))  # , indent=4, sort_keys=True

        # change facs to blendshapes
        # TODO if None (should not receive any None prob)
        blend_dict = self.au_to_blendshapes.output_blendshapes(facs_dict['data']['facs'])
        # print(blend_dict)

        # add blend dict under 'data' to received message and remove FACS
        msg_dict = self.structure_dict(facs_dict, blend_dict)

        # publish blendshapes
        # TODO double json.dump
        print(json.dumps(msg_dict, indent=4))
        return json.dumps(msg_dict)

    # restructure to frame, timestamp, data={head_pose, blendshape}
    def structure_dict(self, facs_dict, blend_dict):
        #   restructure
        # copy whole message except data part
        msg_dict = {k: v for k, v in facs_dict.items() if k is not 'data'}
        # init key 'data' again
        msg_dict['data'] = {}
        # copy 'head_pose' back into data
        msg_dict['data']['head_pose'] = deepcopy(facs_dict['data']['head_pose'])
        msg_dict['data']['blend_shape'] = deepcopy(blend_dict)

        return msg_dict


# client to message broker server
class NetworkSetup:
    """
    Our WAMP session class .. setup register/subscriber/publisher here
    """
    def __init__(self, address='127.0.0.1', port_facs='5571', port_blend='5572'):
        self.url = "tcp://{}:{}".format(address, port_facs)
        self.ctx = Context.instance()

        self.url2 = "tcp://{}:{}".format(address, port_blend)
        self.ctx2 = Context.instance()

        self.blendshape = BlendShapeMsg()

        # activate publishers / subscribers
        asyncio.get_event_loop().run_until_complete(asyncio.wait([
            self.blenshape_sub(),
        ]))

    async def blenshape_sub(self):
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
            # keep listening to all published message on topic 'world'
            while True:
                [topic, msg_sub] = await sub.recv_multipart()
                print("FACS sub; topic: {}\tmessage: {}".format(topic, msg_sub))
                # process message
                msg_pub = await self.blendshape.facs_to_blendshape(msg_sub.decode('utf-8'))

                # await asyncio.sleep(.2)

                # publish message to topic 'sekai'
                # async always needs `send_multipart()`
                await pub.send_multipart([topic, msg_pub.encode('utf-8')])

        except Exception as e:
            print("Error with sub world")
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

    print("Arguments given: {}".format(sys.argv))
    print("0, 2, or 3 arguments are expected (port_facs, port_blend, (address)), e.g.: 5571 5572 127.0.0.1")

    # no arguments
    if len(sys.argv) == 1:
        NetworkSetup()

    # local network, only port
    elif len(sys.argv) == 2:
        NetworkSetup(port_facs=sys.argv[1])

    # full network control
    elif len(sys.argv) == 3:
        NetworkSetup(port_facs=sys.argv[1], port_blend=sys.argv[2], address=sys.argv[3])

    else:
        print("Received incorrect number of arguments")
