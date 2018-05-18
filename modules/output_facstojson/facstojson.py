# Copyright (c) Stef van der Struijk
# License: GNU Lesser General Public License


import sys
import argparse
from os.path import join
import json

# own imports; if statement for documentation
if __name__ == '__main__':
    sys.path.append("..")
    from facsvatarzeromq import FACSvatarZeroMQ
else:
    from modules.facsvatarzeromq import FACSvatarZeroMQ


class MessageToJSON:
    def __init__(self):
        self.counter = 0
        self.folder = "facsjson"

    def facs_json(self, facs_json):
        print(json.dumps(facs_json, indent=4))
        # save FACS data to JSON
        with open(join(self.folder, "frame_{}.json".format(self.counter)), 'w') as outfile:
            json.dump(facs_json, outfile)
        self.counter += 1

    def stop(self):
        print("All messages received")


# client to message broker server
class FACSvatarMessages(FACSvatarZeroMQ):
    """Receives FACS and Head movement data; forward to output function"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.message_to_json = MessageToJSON()

    async def sub(self):
        # keep listening to all published message on topic 'facs'
        while True:
            msg = await self.sub_socket.recv_multipart()
            print("message: {}".format(msg))

            # check not finished; timestamp is empty (b'')
            if msg[1]:
                # load message from bytes to json
                msg[2] = json.loads(msg[2].decode('utf-8'))

                # process facs data only
                self.message_to_json.facs_json(msg[2]['au_r'])

            # no more messages to be received
            else:
                print("No more messages to publish")
                self.message_to_json.stop()


if __name__ == '__main__':
    # command line arguments
    parser = argparse.ArgumentParser()

    # subscriber to FACS / head movement data
    parser.add_argument("--sub_ip", default=argparse.SUPPRESS,
                        help="IP (e.g. 192.168.x.x) of where to pub to; Default: 127.0.0.1 (local)")
    parser.add_argument("--sub_port", default="5571",
                        help="Port of where to pub to; Default: 5571")
    parser.add_argument("--sub_key", default=argparse.SUPPRESS,
                        help="Key for filtering message; Default: '' (all keys)")
    parser.add_argument("--sub_bind", default=False,
                        help="True: socket.bind() / False: socket.connect(); Default: False")

    args, leftovers = parser.parse_known_args()
    print("The following arguments are used: {}".format(args))
    print("The following arguments are ignored: {}\n".format(leftovers))

    # init FACSvatar message class
    facsvatar_messages = FACSvatarMessages(**vars(args))
    # start processing messages; give list of functions to call async
    facsvatar_messages.start([facsvatar_messages.sub])
