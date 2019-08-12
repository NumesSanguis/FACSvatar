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
else:
    from modules.facsvatarzeromq import FACSvatarZeroMQ


# process everything that is received
class FilterMsg:
    def __init__(self, difference_threshold=0.01):
        # self.au_to_blendshapes = AUtoBlendShapes(au_folder)
        self.difference_threshold = difference_threshold
        self.previous_dict = {}

    # receives unfiltered dict and index of which stored dict to compare (0 for 1st dict)
    async def filter_dict(self, dict_full, dict_idx):
        # 1st time dict_idx
        if dict_idx not in self.previous_dict:
            self.previous_dict[dict_idx] = {}

        # keep track of keys to be removed
        filtered_keys = []

        # per dict entry: check if enough change
        for key, value in dict_full.items():
            # if key not in compare dict, add it
            if key not in self.previous_dict[dict_idx]:
                self.previous_dict[dict_idx][key] = value
            # if not big enough difference: remove key
            elif value - self.difference_threshold < self.previous_dict[dict_idx][key] < value + self.difference_threshold:
                # remove dict key+value from dict
                # dict_full.pop(key)  # key we want to delete should exist
                filtered_keys.append(key)
                print(f"Filtered: {key}")
            # difference is big, so we update our compare dict
            else:
                # update compare dict with new values
                self.previous_dict[dict_idx][key] = value

        # remove keys
        for key in filtered_keys:
            dict_full.pop(key)  # key we want to delete should exist

        # return filtered dict
        return dict_full


# client to message broker server
class FACSvatarMessages(FACSvatarZeroMQ):
    """Receives FACS and Head movement data; FACS --> Blend Shapes; Publish new data"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.filter_msg = FilterMsg(float(self.misc["filter_threshold"]))

    async def filter_sub_pub(self):
        # keep listening to all published message on topic 'facs'
        while True:
            # msg = await self.sub_socket.recv_multipart()
            key, timestamp, data = await self.sub_socket.sub()
            print("Received message: {}".format([key, timestamp, data]))

            # check not finished; timestamp is empty (b'')
            if timestamp:
                # check not empty
                if data:
                    # we're filtering AU data
                    if 'au_r' in data:
                        # filter Blend Shape values that don't significantly differ from previous msgs
                        data['au_r'] = await self.filter_msg.filter_dict(data['au_r'], 0)

                    # we're filtering Blend Shape data
                    else:
                        # filter Blend Shape values that don't significantly differ from previous msgs
                        data['blendshapes'] = await self.filter_msg.filter_dict(data['blendshapes'], 0)

                    # filter head pose only if users wants that
                    if self.misc["filter_pose"]:
                        # filter bone rotation values that don't significantly differ from previous msgs
                        data['pose'] = await self.filter_msg.filter_dict(data['pose'], 1)

                #print(data)
                # publish data
                await self.pub_socket.pub(data, key)

            # send message we're done
            else:
                print("No more messages to publish; filter messages done")
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
    parser.add_argument("--sub_port", default="5572",
                        help="Port of where to sub to; Default: 5572")
    parser.add_argument("--sub_key", default=argparse.SUPPRESS,
                        help="Key for filtering message; Default: '' (all keys)")
    parser.add_argument("--sub_bind", default=False,
                        help="True: socket.bind() / False: socket.connect(); Default: False")

    # publisher of Blend Shape / head movement data
    parser.add_argument("--pub_ip", default=argparse.SUPPRESS,
                        help="IP (e.g. 192.168.x.x) of where to pub to; Default: 127.0.0.1 (local)")
    parser.add_argument("--pub_port", default="5573",
                        help="Port of where to pub to; Default: 5573")
    parser.add_argument("--pub_key", default="facsvatar.filter",
                        help="Key for filtering message; Default: blendshapes.human")
    parser.add_argument("--pub_bind", default=True,
                        help="True: socket.bind() / False: socket.connect(); Default: True")

    # module specific commandline arguments
    parser.add_argument("--filter_threshold", default="0.01",
                        help="Value that is considered big enough as value change")
    parser.add_argument("--filter_pose", default=False,
                        help="Whether head pose should also be filtered")

    args, leftovers = parser.parse_known_args()
    print("The following arguments are used: {}".format(args))
    print("The following arguments are ignored: {}\n".format(leftovers))

    # init FACSvatar message class
    facsvatar_messages = FACSvatarMessages(**vars(args))
    # start processing messages; give list of functions to call async
    facsvatar_messages.start([facsvatar_messages.filter_sub_pub])
