# Copyright (c) Stef van der Struijk
# License: GNU Lesser General Public License


import sys
import json
import time

#own imports
sys.path.append(".")
from facsvatarzeromq import FACSvatarZeroMQ


class Controller(FACSvatarZeroMQ):
    """Send command messages to FACSvatar to change its behavior"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        print("init done")

    # return subdict based on key string starts with; "AU" or "pose"
    def slicedict(self, dict, s):
        return {k: v for k, v in dict.items() if k.startswith(s)}

    # set face configuration
    def face_configuration(self, dict_config):
        # print(dict_au)

        # init a message dict
        msg = dict()

        # metadata in message
        msg['frame'] = -1
        msg['timestamp'] = time.time()

        # au_regression in message as dict
        msg['au_r'] = self.slicedict(dict_config, "AU")

        # head pose in message as dict
        msg['pose'] = self.slicedict(dict_config, "pose")

        # send message
        self.pub_socket.send_multipart(["gui.face_config".encode('ascii'),  # topic
                                        str(int(time.time() * 1000)).encode('ascii'),  # timestamp
                                        json.dumps(msg).encode('utf-8')  # data in JSON format or empty byte
                                        ])

    # change AU multiplier values
    def multiplier(self, dict_au):
        # print("[Command] Set AU multiplier to: {}".format(dict_au))
        # au values to list
        au_list = list(dict_au.values())
        # list to JSON
        au_json = json.dumps(au_list)
        # print(au_json)

        # publish new multiplier
        # print(self.pub_key)
        # print(time.time())
        # print(au_json)
        self.pub_socket.send_multipart([self.pub_key.encode('ascii'),  # topic
                                        str(int(time.time()*1000)).encode('ascii'),  # timestamp
                                        au_json.encode('utf-8')  # data in JSON format or empty byte
                                        ])
