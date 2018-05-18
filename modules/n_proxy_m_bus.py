"""Opens a proxy/function bus between 2 ports for a N-proxy-M PubSub pattern

  Additional info:
2 modes:
1. proxy (no data copying) - DEFAULT
2. function (modify pass through data)
Similar to a ROS topic (named bus)

  ZeroMQ:
Default address listening to pubs: 127.0.0.1:5570
Default address publishing to subs: 127.0.0.1:5571
Sub listen and Pub style: 4+ part envelope (including key)
Subscription Key: all (openface, dnn)
Message parts:
0. sub_key
1. frame
2. timestamp
3. data
4. (data2)

TODO: register somewhere for a bus overview"""

# Copyright (c) Stef van der Struijk.
# License: GNU Lesser General Public License


import sys
import argparse
from functools import partial
import zmq.asyncio
import traceback
import logging
import asyncio

# own import; if statement for documentation
if __name__ == '__main__':
    sys.path.append("..")
    from facsvatarzeromq import FACSvatarZeroMQ
    from smooth_data import SmoothData
else:
    from modules.facsvatarzeromq import FACSvatarZeroMQ
    from .smooth_data import SmoothData


class ProxyPub:
    def __init__(self, ip_pub='127.0.0.1', port_pub='5570', ip_sub='127.0.0.1', port_sub='5571',  # '127.0.0.1'
                 data_func='trailing_moving_average'):  # 'trailing_moving_average'
        # self.context = Context.instance()
        # 2 sockets, because we can only bind once to a socket (as opposed to connect)
        self.url1 = "tcp://{}:{}".format(ip_pub, port_pub)
        self.url2 = "tcp://{}:{}".format(ip_sub, port_sub)
        print("Publishers should pub to: {}".format(self.url1))
        print("Subscribers should sub to: {}".format(self.url2))

        # don't duplicate the message, just pass through
        if not data_func:
            self.xpub_xsub_proxy()

        # apply function to data
        else:
            import asyncio
            asyncio.get_event_loop().run_until_complete(self.pub_sub_function(data_func))
            # self.pub_sub_function(data_func)

    # N publishers to 1 sub; proxy 1 sub to 1 pub; publish to M subscribers
    def xpub_xsub_proxy(self):
        print("Init sockets")
        # Socket subscribing to publishers
        ctx = zmq.Context.instance()
        frontend_pubs = ctx.socket(zmq.XSUB)
        frontend_pubs.bind(self.url1)

        # Socket publishing to subscribers
        backend_subs = ctx.socket(zmq.XPUB)
        backend_subs.bind(self.url2)
        
        print("Try: Proxy... CONNECT!")
        zmq.proxy(frontend_pubs, backend_subs)
        print("CONNECT successful!")

    # smooth data
    async def pub_sub_function(self, data_func):  # async
        print("Init sockets")
        from zmq.asyncio import Context
        import json
        # Socket subscribing to publishers
        # ctx = zmq.Context.instance()
        ctx = zmq.asyncio.Context.instance()
        frontend_pubs = ctx.socket(zmq.SUB)
        frontend_pubs.bind(self.url1)
        frontend_pubs.setsockopt(zmq.SUBSCRIBE, b'')

        # Socket publishing to subscribers
        backend_subs = ctx.socket(zmq.PUB)
        backend_subs.bind(self.url2)

        # class with data smoothing functions
        smooth_data = SmoothData()
        # get the function we need to pass data to
        smooth_func = getattr(smooth_data, data_func)

        # await messages
        print("Awaiting FACS data...")
        # without try statement, no error output
        try:
            # keep listening to all published message on topic 'facs'
            while True:
                msg = await frontend_pubs.recv_multipart()
                print(msg)

                # check not finished; timestamp is empty (b'')
                if msg[1]:
                    msg[2] = json.loads(msg[2].decode('utf-8'))
                    # print(msg_sub)
                    # msg = json.loads(msg.decode('utf-8'))
                    # prepare for asynchronous execution; convert byte to string
                    # fut = asyncio.ensure_future
                    # facs = fut(smooth_func(msg[3].decode('utf-8'), queue_no=0))
                    # head_pose = fut(smooth_func(msg[4].decode('utf-8'), queue_no=1))

                    # run concurrently
                    # msg[3:] = await asyncio.gather(facs, head_pose)

                    # smooth facial expressions; window_size: number of past data points; steep: weight to newer data
                    msg[2]['au_r'] = smooth_func(msg[2]['au_r'], queue_no=0, window_size=3, steep=.45)
                    # smooth head position
                    msg[2]['pose'] = smooth_func(msg[2]['pose'], queue_no=1, window_size=3, steep=.2)

                    # send modified message
                    print(msg)
                    # await backend_subs.send_multipart([msg[0],  # topic
                    #                           msg[1],  # frame
                    #                           msg[2],  # timestamp
                    #                           msg[3].encode('utf-8'),  # FACS data; json
                    #                           # TODO separate msg
                    #                           msg[4].encode('utf-8')  # head pose data; json
                    #                           ])

                    await backend_subs.send_multipart([msg[0],  # topic
                                                       msg[1],  # timestamp
                                                       # data in JSON format or empty byte
                                                       json.dumps(msg[2]).encode('utf-8')
                                                       ])

                # send message we're done
                else:
                    print("No more messages to pass; finished")
                    await backend_subs.send_multipart([msg[0], b'', b''])

        except:
            print("Error with sub")
            # print(e)
            logging.error(traceback.format_exc())
            print()


class FACSvatarMessages(FACSvatarZeroMQ):
    """Publishes FACS and Head movement data from .csv files generated by OpenFace"""

    # def __init__(self, **kwargs):
    #     super().__init__(**kwargs)

    # overwrite existing start function
    def start(self, async_func_list=None):
        """No functions given --> data pass through only; else apply function on data before forwarding

        N publishers to 1 sub; proxy 1 sub to 1 pub; publish to M subscribers
        """

        # make sure pub / sub is initialised
        if not self.pub_socket or not self.sub_socket:
            print("Both pub and sub needs to be initiliased and set to bind")
            print("Pub: {}".format(self.pub_socket))
            print("Sub: {}".format(self.sub_socket))
            sys.exit()

        # apply function to data to passing through data
        if async_func_list:
            import asyncio
            # capture ZeroMQ errors; ZeroMQ using asyncio doesn't print out errors
            try:
                asyncio.get_event_loop().run_until_complete(asyncio.wait(
                    [func() for func in async_func_list]
                ))
            except Exception as e:
                print("Error with async function")
                # print(e)
                logging.error(traceback.format_exc())
                print()

            finally:
                # TODO disconnect pub/sub
                pass

        # don't duplicate the message, just pass through
        else:
            print("Try: Proxy... CONNECT!")
            zmq.proxy(self.pub_socket, self.sub_socket)
            print("CONNECT successful!")

    async def pub_sub_function(self, apply_function):  # async
        """Subscribes to FACS data, smooths, publishes it"""

        import json
        # class with data smoothing functions
        smooth_data = SmoothData()
        # get the function we need to pass data to
        smooth_func = getattr(smooth_data, apply_function)

        # await messages
        print("Awaiting FACS data...")
        # without try statement, no error output
        try:
            # keep listening to all published message on topic 'facs'
            while True:
                msg = await self.sub_socket.recv_multipart()
                print(msg)

                # check not finished; timestamp is empty (b'')
                if msg[1]:
                    msg[2] = json.loads(msg[2].decode('utf-8'))

                    # TODO check if confidence is high enough

                    # smooth facial expressions; window_size: number of past data points; steep: weight to newer data
                    msg[2]['au_r'] = smooth_func(msg[2]['au_r'], queue_no=0, window_size=3, steep=.45)
                    # smooth head position
                    msg[2]['pose'] = smooth_func(msg[2]['pose'], queue_no=1, window_size=3, steep=.2)

                    # send modified message
                    print(msg)
                    await self.pub_socket.send_multipart([msg[0],  # topic
                                                       msg[1],  # timestamp
                                                       # data in JSON format or empty byte
                                                       json.dumps(msg[2]).encode('utf-8')
                                                       ])

                # send message we're done
                else:
                    print("No more messages to pass; finished")
                    await self.pub_socket.send_multipart([msg[0], b'', b''])

        except:
            print("Error with sub")
            # print(e)
            logging.error(traceback.format_exc())
            print()


if __name__ == '__main__':
    # command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--sub_ip", default=argparse.SUPPRESS,
                        help="This PC's IP (e.g. 192.168.x.x) pubslishers pub to; Default: 127.0.0.1 (local)")
    parser.add_argument("--sub_port", default="5570",
                        help="Port publishers pub to; Default: 5570")
    parser.add_argument("--pub_ip", default=argparse.SUPPRESS,
                        help="This PC's IP (e.g. 192.168.x.x) subscribers sub to; Default: 127.0.0.1 (local)")
    parser.add_argument("--pub_port", default="5571",
                        help="Port subscribers sub to; Default: 5571")

    # sockets have to use bind for N-1-M setup
    parser.add_argument("--sub_bind", default=True,
                        help="True: socket.bind() / False: socket.connect()")
    parser.add_argument("--pub_bind", default=True,
                        help="True: socket.bind() / False: socket.connect()")

    args, leftovers = parser.parse_known_args()
    print("The following arguments are used: {}".format(args))
    print("The following arguments are ignored: {}\n".format(leftovers))

    # init FACSvatar message class
    facsvatar_messages = FACSvatarMessages(**vars(args))
    # start processing messages
    facsvatar_messages.start([partial(facsvatar_messages.pub_sub_function, "trailing_moving_average")])
