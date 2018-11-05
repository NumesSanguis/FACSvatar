# Copyright (c) Stef van der Struijk
# License: GNU Lesser General Public License


import os
import sys
import argparse
import json
from os.path import join
import numpy as np
import pandas as pd
#import tensorflow as tf
import keras
import traceback
import logging
import zmq.asyncio
import asyncio


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

        # TODO invert process by only keeping trained AU
        # temporary remove eye gaze AU data
        au_gaze = ('AU61', 'AU62', 'AU63', 'AU64')
        # TODO check if exists
        au_gaze_dict = {k: au_dict.pop(k) for k in au_gaze if k in au_dict}

        # for au in :
        #     if au in au_dict:
        #         au_gaze

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
        #with tf.device('/gpu:0'):
        deep_au_array_val = self.facs_model.predict(au_array_val)  # [np.newaxis]
        # print()dd ignored file
        #print(deep_au_array_val)
        # print(np.asarray(deep_au_array_val))

        # cast into dict format
        # print()
        #print(np.squeeze(deep_au_array_val))
        deep_au_dict = dict(zip(au_array_key, np.squeeze(deep_au_array_val).tolist()))
        #print(deep_au_dict)
        # change key type from byte to string
        deep_au_dict = {k.decode("utf-8"): v for k, v in deep_au_dict.items()}
        # print(deep_au_dict)

        print("")
        #print(au_dict)
        print(deep_au_dict)

        # add gaze AUs back into dict and return
        return deep_au_dict  # {**deep_au_dict, **au_gaze_dict}


# client to message broker server
class FACSvatarMessages(FACSvatarZeroMQ):
    """Receives FACS and Head movement data; FACS --> DNN --> FACS; Publish new data"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.deepfacs = DeepFACSMsg()
        self.json_file = "AU_json.json"

    # receiving data
    async def deep_sub_pub(self):
        # # 1 time fake data to init DNN model
        if os.path.exists(self.json_file):
            print("Sending fake data to DNN to reduce start-up time...")
            with open(self.json_file, 'r') as j:
                fake_data = json.load(j)
                result = await self.deepfacs.facs_deep_facs(fake_data)
                # print("Fake data: {}".format(result))
                print("Fake data done")

        print("\nListening for message...")
        # keep listening to all published message on topic 'facs'
        while True:
            # msg = await self.sub_socket.recv_multipart()
            key, timestamp, data = await self.sub_socket.sub()
            print("Received message: {}".format([key, timestamp, data]))

            # if pub key is specified
            # if self.pub_key:
            #     key = self.pub_key.encode('utf-8')
            
            # key = ("dnn." + key.decode('ascii')).encode('ascii')
            key = "dnn." + key

            # check not finished; timestamp is empty (b'')
            if timestamp:
                # generate Action Units based on user Action Units
                data['au_r'] = await self.deepfacs.facs_deep_facs(data['au_r'])

                await self.pub_socket.pub(data, key)

            # send message we're done
            else:
                print("No more messages to publish; Deep FACS done")
                await self.pub_socket.pub(b'', key)

    # receiving commands
    async def set_parameters(self):
        while True:
            try:
                [id_dealer, topic, data] = await self.rout_socket.recv_multipart()
                print("\nCommand received from '{}', with topic '{}' and msg '{}'".format(id_dealer, topic, data))

                # set subscriber key
                if topic.decode('ascii').startswith("dnn"):
                    # await self.change_user()
                    await self.set_subscriber(data.decode('utf-8'))
                else:
                    print("Command ignored")

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
    async def set_subscriber(self, user_key):
        print("Current subscription key: {}".format(self.sub_key))

        # get individual topics
        split_key = self.sub_key.split(".")

        # if not in current subscription, change subscription
        if user_key not in split_key:
            # TODO not 2 participants
            if user_key == "p0":
                user_key_old = "p1"
            elif user_key == "p1":
                user_key_old = "p0"
            else:
                print("user_key is not p0 or p1")

            # unsubscribe all keys
            self.sub_socket.setsockopt(zmq.UNSUBSCRIBE, self.sub_key.encode('ascii'))

            # change p0 to p1 or reversed
            split_key[split_key.index(user_key_old)] = user_key

            # set new subscription key
            self.sub_key = ".".join(split_key)
            self.sub_socket.setsockopt(zmq.SUBSCRIBE, self.sub_key.encode('ascii'))
            print("Changed subscription key to: {}".format(self.sub_key))

        else:
            print("Already subscribed to user: {}".format(user_key))


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
