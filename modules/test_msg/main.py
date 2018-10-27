# Copyright (c) Stef van der Struijk
# License: GNU Lesser General Public License


import os
import sys
import argparse
import json
import asyncio
import time


# own imports; if statement for documentation
if __name__ == '__main__':
    sys.path.append("..")
    from facsvatarzeromq import FACSvatarZeroMQ
else:
    from modules.facsvatarzeromq import FACSvatarZeroMQ


# client to message broker server
class Messages(FACSvatarZeroMQ):
    """Test class for sending / receiving messages"""

    # def __init__(self, **kwargs):
    #     super().__init__(**kwargs)

    async def msg_sub(self):
        # keep listening to all published message on topic 'facs'
        while True:
            # key, timestamp, data = await self.sub_socket.sub()
            msg = await self.sub_socket.socket.recv_multipart()  # raw data
            print("message received: {}".format(msg))

    async def msg_pub(self):
        # keep listening to all published message on topic 'facs'
        while True:
            await asyncio.sleep(0.1)
            await self.pub_socket.send_multipart(["test".encode('ascii'),  # topic
                                                  str(int(time.time() * 1000)).encode('ascii'),  # timestamp
                                                  # data in JSON format or empty byte
                                                  json.dumps({'empty:': None}).encode('utf-8')
                                                  ])


if __name__ == '__main__':
    # command line arguments
    parser = argparse.ArgumentParser()

    # subscriber
    parser.add_argument("--sub_ip", default=argparse.SUPPRESS,
                        help="IP (e.g. 192.168.x.x) of where to sub to; Default: 127.0.0.1 (local)")
    parser.add_argument("--sub_port", default=argparse.SUPPRESS,
                        help="Port of where to sub to; Default: None")
    parser.add_argument("--sub_key", default=argparse.SUPPRESS,
                        help="Key for filtering message; Default: '' (all keys)")
    parser.add_argument("--sub_bind", default=False,
                        help="True: socket.bind() / False: socket.connect(); Default: False")

    # publisher
    parser.add_argument("--pub_ip", default=argparse.SUPPRESS,
                        help="IP (e.g. 192.168.x.x) of where to pub to; Default: 127.0.0.1 (local)")
    parser.add_argument("--pub_port", default=argparse.SUPPRESS,
                        help="Port of where to pub to; Default: None")
    parser.add_argument("--pub_key", default="test.pub",
                        help="Key for filtering message; Default: blendshapes.human")
    parser.add_argument("--pub_bind", default=False,
                        help="True: socket.bind() / False: socket.connect(); Default: False")

    args, leftovers = parser.parse_known_args()
    print("The following arguments are used: {}".format(args))
    print("The following arguments are ignored: {}\n".format(leftovers))

    # init FACSvatar message class
    messages = Messages(**vars(args))

    # list of functions
    async_list = []
    if 'sub_port' in args:
        async_list.append(messages.msg_sub)
    if 'pub_port' in args:
        async_list.append(messages.msg_pub)

    print("Starting functions: {}".format(async_list))

    # start processing messages; give list of functions to call async
    messages.start(async_list)
