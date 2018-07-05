"""Prepossesses openface .csv files and publishes its data to FACSvatar

Relies on Python 3.6+ due to async generator yield statement"""

# Copyright (c) Stef van der Struijk
# License: GNU Lesser General Public License
# Modification of:
# https://github.com/wiseman/py-webrtcvad (MIT Copyright (c) 2016 John Wiseman)
# https://github.com/wangshub/python-vad (MIT Copyright (c) 2017 wangshub)


import os
# from os.path import join, isfile
from pathlib import Path
import sys
# from functools import partial
import argparse
import time
# import glob
import json
import asyncio
import pyaudio
import webrtcvad



# FACSvatar imports; if statement for documentation
if __name__ == '__main__':
    # TODO work irrespectively of folder
    # sys.path.append(".")
    sys.path.append("..")
    from facsvatarzeromq import FACSvatarZeroMQ
else:
    from modules.facsvatarzeromq import FACSvatarZeroMQ


class VAD:
    def __init__(self):
        self.vad = webrtcvad.Vad(3)

        # stream info
        self.rate = 16000
        chunk_duration_ms = 30  # supports 10, 20 and 30 (ms)
        self.chunk_size = int(self.rate * chunk_duration_ms / 1000)  # chunk to read
        pa = pyaudio.PyAudio()
        self.stream = pa.open(format=pyaudio.paInt16,
                              channels=1,
                              rate=self.rate,
                              input=True,
                              start=False,
                              # input_device_index=2,
                              frames_per_buffer=self.chunk_size)

    async def msg_gen(self):
        self.stream.start_stream()
        active_count = 0

        while True:
            chunk = self.stream.read(self.chunk_size)
            # Voice Activity Detection
            active = self.vad.is_speech(chunk, self.rate)
            print("o" if active else "_", end="", flush=True)  # end= "/r" (backspace); sys.stdout.write
            # speaking
            if active:
                active_count += 1
            # reset
            else:
                active_count -= 2
                # don't go below 0
                active_count = max(active_count, 0)

            # speaking for a bit, and not a simple comment
            if active_count >= 20:
                # reset count
                active_count = 0
                yield 1
                # sleep 1 sec after sending message
                #await asyncio.sleep(1)


class FACSvatarMessages(FACSvatarZeroMQ):
    """VAD: Listens to mic and sends participant id when voice is detected to DNN"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.vad = VAD()
        # send to both deepfacs.py and n_proxy_m_bus.py
        # self.deal_socket.connect("tcp://{}:{}".format(kwargs['deal_ip'], kwargs['deal_port']))

    # publishes facs values per frame to subscription key 'facs'
    async def vad_router(self):
        """Calls openface_msg.msg_gen() and publishes returned data"""

        # when message comes, send message that this person is speaking
        async for msg in self.vad.msg_gen():
            print("Changing sub key of DNN to user: {}".format(self.misc['user']))
            # pub_deepfacs.py
            if self.deal_socket:
                self.deal_socket.send_multipart([self.deal_topic.encode('ascii'),  # topic
                                                 self.misc['user'].encode('utf-8')  # data in JSON format or empty byte
                                                 ])
            # n_proxy_m_bus.py
            if self.deal2_socket:
                self.deal2_socket.send_multipart([self.deal2_topic.encode('ascii'),  # topic
                                                  self.misc['user'].encode('utf-8')  # data in JSON format or empty byte
                                                  ])


if __name__ == '__main__':
    # command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--deal_ip", default=argparse.SUPPRESS,
                        help="IP (e.g. 192.168.x.x) of where to send commands to; Default: 127.0.0.1 (local)")
    parser.add_argument("--deal_port", default="5581",
                        help="Port of where to send commands to to; Default: 5581")
    parser.add_argument("--deal_key", default="vad",
                        help="Key to identify sender; Default: vad")
    parser.add_argument("--deal_bind", default=False,
                        help="True: socket.bind() / False: socket.connect(); Default: False")
    parser.add_argument("--deal_topic", default="dnn",
                        help="command filter for router")

    parser.add_argument("--deal2_ip", default=argparse.SUPPRESS,
                        help="IP (e.g. 192.168.x.x) of where to send commands to; Default: 127.0.0.1 (local)")
    parser.add_argument("--deal2_port", default="5582",
                        help="Port of where to send commands to to; Default: 5582")
    parser.add_argument("--deal2_key", default="vad",
                        help="Key to identify sender; Default: vad")
    parser.add_argument("--deal2_bind", default=False,
                        help="True: socket.bind() / False: socket.connect(); Default: False")
    parser.add_argument("--deal2_topic", default="dnn",
                        help="command filter for router")

    parser.add_argument("--user", default="p0",
                        help="User id of vad")

    args, leftovers = parser.parse_known_args()
    print("The following arguments are used: {}".format(args))
    print("The following arguments are ignored: {}\n".format(leftovers))

    # init FACSvatar message class
    facsvatar_messages = FACSvatarMessages(**vars(args))

    # start processing messages; give list of functions to call async
    facsvatar_messages.start([facsvatar_messages.vad_router])
