# Copyright (c) Stef van der Struijk
# License: GNU Lesser General Public License


import sys
import json
import time

#own imports
sys.path.append(".")
from facsvatarzeromq import FACSvatarZeroMQ


class Controller(FACSvatarZeroMQ):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        print("init done")

    def multiplier(self, dict_au):
        # print("[Command] Set AU multiplier to: {}".format(dict_au))
        # au values to list
        au_list = list(dict_au.values())
        # list to JSON
        au_json = json.dumps(au_list)

        # publish new multiplier
        # print(self.pub_key)
        # print(time.time())
        # print(au_json)
        self.pub_socket.send_multipart([self.pub_key.encode('ascii'),  # topic
                                        str(int(time.time()*1000)).encode('ascii'),  # timestamp
                                        au_json.encode('utf-8')  # data in JSON format or empty byte
                                        ])
