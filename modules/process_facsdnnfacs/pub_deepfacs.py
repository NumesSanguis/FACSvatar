# Copyright (c) Stef van der Struijk
# License: GNU Lesser General Public License


import os
import sys
import argparse
import json
from os.path import join
import numpy as np
import pandas as pd
import keras
import traceback
import logging
import zmq.asyncio


# own imports; if statement for documentation
if __name__ == '__main__':
    sys.path.append("..")
    from facsvatarzeromq import FACSvatarZeroMQ
else:
    from modules.facsvatarzeromq import FACSvatarZeroMQ


# process everything that is received
class DeepFACSMsg:
    def __init__(self):
        # load Keras model
        self.facs_model = keras.models.load_model(join("models", "mimicry_trained.h5"))

    async def facs_deep_facs(self, au_dict):  # , id_cb, type_cb
        """Receives a dict of AUs, returns a dict of deep generated AUs"""

        # print()
        # print(au_dict)
        # print(type(au_dict))

        #   get values for prediction
        # cast json to pandas series
        # au_df = pd.DataFrame.from_dict(au_dict)
        # print(au_df)
        # print(au_df.values)

        # au_series = pd.Series(au_dict)
        # print(au_series)
        # print(au_series.values)

        # au_df = pd.DataFrame.from_dict(au_dict, orient='index')
        # deep_au_array_val = self.facs_model.predict(au_df.values)
        # print(deep_au_array_val)

        # dict to numpy
        au_array_key = np.fromiter(au_dict.keys(), dtype='S16')
        au_array_val = np.fromiter(au_dict.values(), dtype=float)

        # predict
        # print()
        # print(au_array_val)
        # au_array_val_t = au_array_val[np.newaxis]
        # print(au_array_val_t)
        # print(au_array_val_t.shape)

        au_array_val = au_array_val.reshape(1, 1, 17)
        deep_au_array_val = self.facs_model.predict(au_array_val)  # [np.newaxis]
        # print()
        print(deep_au_array_val)
        # print(np.asarray(deep_au_array_val))

        # cast into dict format
        # print()
        print(np.squeeze(deep_au_array_val))
        deep_au_dict = dict(zip(au_array_key, np.squeeze(deep_au_array_val).tolist()))
        print(deep_au_dict)
        # change key type from byte to string
        deep_au_dict = {k.decode("utf-8"): v for k, v in deep_au_dict.items()}
        # print(deep_au_dict)

        print("\n")
        print(au_dict)
        print(deep_au_dict)

        # sys.exit()
        # return
        return deep_au_dict


# client to message broker server
class FACSvatarMessages(FACSvatarZeroMQ):
    """Receives FACS and Head movement data; FACS --> DNN --> FACS; Publish new data"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.deepfacs = DeepFACSMsg()

    # receiving data
    async def deep_sub_pub(self):
        # keep listening to all published message on topic 'facs'
        while True:
            msg = await self.sub_socket.recv_multipart()
            print("message: {}".format(msg))

            # if pub key is specified
            # if self.pub_key:
            #     msg[0] = self.pub_key.encode('utf-8')

            # check not finished; timestamp is empty (b'')
            if msg[1]:
                # process message
                msg[2] = json.loads(msg[2].decode('utf-8'))
                # generate Action Units based on user Action Units
                msg[2]['au_r'] = await self.deepfacs.facs_deep_facs(msg[2]['au_r'])

                # async always needs `send_multipart()`
                # print(msg)

                await self.pub_socket.send_multipart([("dnn." + msg[0].decode('utf-8')).encode('utf-8'),  # topic / key
                                          msg[1],  # timestamp
                                          # data in JSON format or empty byte
                                          json.dumps(msg[2]).encode('utf-8')
                                          ])

            # send message we're done
            else:
                print("No more messages to publish; Deep FACS done")
                await self.pub_socket.send_multipart([msg[0], b'', b''])

    # receiving commands
    async def set_parameters(self):
        while True:
            try:
                [id_dealer, topic, data] = await self.rout_socket.recv_multipart()
                print("Command received from '{}', with topic '{}' and msg '{}'".format(id_dealer, topic, data))

                # set subscriber key
                if topic.decode('utf-8').startswith("dnn"):
                    await self.change_user()
                else:
                    print("Command ignored")

                # change subscription key
                # await self.set_subscriber(data)

            except Exception as e:
                print("Error with router function")
                # print(e)
                logging.error(traceback.format_exc())
                print()

    # change user for what FACS data to subscribe (p0 or p1); 2 speakers only for now
    async def change_user(self):
        print("Changing subscription key from: {}".format(self.sub_key))
        # unsubscribe all keys
        self.sub_socket.setsockopt(zmq.UNSUBSCRIBE, self.sub_key.encode('ascii'))
        # subscribe to new key
        if "p0" in self.sub_key.split("."):
            self.sub_key = self.sub_key.replace(".p0", ".p1")
        elif "p1" in self.sub_key.split("."):
            self.sub_key = self.sub_key.replace(".p1", ".p0")
        self.sub_socket.setsockopt(zmq.SUBSCRIBE, self.sub_key.encode('ascii'))
        print("Changed subscription key to: {}".format(self.sub_key))

    # change to what FACS data to subscribe
    async def set_subscriber(self, sub_key):
        # unsubscribe all keys
        self.sub_socket.setsockopt(zmq.UNSUBSCRIBE, self.sub_key.encode('ascii'))
        # subscribe to new key
        self.sub_key = sub_key
        self.sub_socket.setsockopt(zmq.SUBSCRIBE, self.sub_key.encode('ascii'))


if __name__ == '__main__':
    # command line arguments
    parser = argparse.ArgumentParser()

    # subscriber to FACS / head movement data
    parser.add_argument("--sub_ip", default=argparse.SUPPRESS,
                        help="IP (e.g. 192.168.x.x) of where to sub to; Default: 127.0.0.1 (local)")
    parser.add_argument("--sub_port", default="5571",
                        help="Port of where to sub to; Default: 5571")
    parser.add_argument("--sub_key", default="openface.p0",
                        help="Key for filtering message; Default: '' (all keys)")
    parser.add_argument("--sub_bind", default=False,
                        help="True: socket.bind() / False: socket.connect(); Default: False")

    # publisher of DNN generated FACS data
    parser.add_argument("--pub_ip", default=argparse.SUPPRESS,
                        help="IP (e.g. 192.168.x.x) of where to pub to; Default: 127.0.0.1 (local)")
    parser.add_argument("--pub_port", default="5570",
                        help="Port of where to pub to; Default: 5570")
    parser.add_argument("--pub_key", default="facsvatar.facs",
                        help="Key for filtering message; Default: facsvatar.facs")
    parser.add_argument("--pub_bind", default=False,
                        help="True: socket.bind() / False: socket.connect(); Default: True")

    # router
    parser.add_argument("--rout_ip", default=argparse.SUPPRESS,
                        help="This PC's IP (e.g. 192.168.x.x) router listens to; Default: 127.0.0.1 (local)")
    parser.add_argument("--rout_port", default="5581",
                        help="Port dealers message to; Default: 5581")
    parser.add_argument("--rout_bind", default=True,
                        help="True: socket.bind() / False: socket.connect(); Default: True")

    args, leftovers = parser.parse_known_args()
    print("The following arguments are used: {}".format(args))
    print("The following arguments are ignored: {}\n".format(leftovers))

    # init FACSvatar message class
    facsvatar_messages = FACSvatarMessages(**vars(args))
    # start processing messages; give list of functions to call async
    facsvatar_messages.start([facsvatar_messages.deep_sub_pub, facsvatar_messages.set_parameters])
