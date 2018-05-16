"""FACSvatar base classes"""

# Copyright (c) Stef van der Struijk.
# License: GNU Lesser General Public License

import traceback
import logging
from abc import ABC, abstractmethod
import asyncio
import zmq.asyncio
from zmq.asyncio import Context


# setup ZeroMQ publisher / subscriber
class FACSvatarZeroMQ(abstractmethod(ABC)):
    """Base class for initializing FACSvatar ZeroMQ sockets"""

    def __init__(self, pub_ip='127.0.0.1', pub_port=None, pub_key=b'', pub_bind=True,
                 sub_ip='127.0.0.1', sub_port=None, sub_key=b'', sub_bind=False):
        """Sets-up a socket bound/connected to an url

        xxx_ip: ip of publisher/subscriber
        xxx_port: port of publisher/subscriber
        xxx_key: key for filtering out messages (leave empty to receive all)
        xxx_bind: True for bind (only 1 socket can bind to 1 address) or false for connect (many can connect)
        """

        if pub_port:
            self.pub_socket = self.zeromq_context(pub_ip, pub_port, zmq.PUB, pub_bind)
            # add variable with key
            self.pub_socket.pub_key = pub_key
        else:
            print("port_pub not specified, not setting-up publisher")

        if sub_port:
            self.sub_socket = self.zeromq_context(sub_ip, sub_port, zmq.SUB, sub_bind)
            self.sub_socket.setsockopt(zmq.SUBSCRIBE, sub_key)
        else:
            print("port_sub not specified, not setting-up subscriber")

    def zeromq_context(self, ip, port, socket_type, bind):
        """Returns an bound / connected ZeroMQ socket through tcp with given ip and port"""

        url = "tcp://{}:{}".format(ip, port)
        print("Creating ZeroMQ context with tcp on: {}".format(url))
        ctx = Context.instance()
        socket = ctx.socket(socket_type)
        if bind:
            socket.bind(url)
        else:
            socket.connect(url)
        return socket

    def start(self, async_func_list=None):
        """Starts asynchronously any given function"""

        # activate publishers / subscribers
        if async_func_list:
            # capture ZeroMQ errors; ZeroMQ using asyncio doesn't print out errors
            try:
                asyncio.get_event_loop().run_until_complete(asyncio.wait(async_func_list))
            except Exception as e:
                print("Error with blendshape")
                # print(e)
                logging.error(traceback.format_exc())
                print()

            finally:
                # TODO disconnect pub/sub
                pass

        else:
            print("No functions given, nothing to start")

    # @abstractmethod
    # async def pub(self):
    #     pass
