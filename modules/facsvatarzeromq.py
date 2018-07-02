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

    def __init__(self, pub_ip='127.0.0.1', pub_port=None, pub_key='', pub_bind=True,
                 sub_ip='127.0.0.1', sub_port=None, sub_key='', sub_bind=False,
                 deal_ip='127.0.0.1', deal_port=None, deal_key='', deal_topic='', deal_bind=False,
                 deal2_ip='127.0.0.1', deal2_port=None, deal2_key='', deal2_topic='', deal2_bind=False,
                 rout_ip='127.0.0.1', rout_port=None, rout_bind=True,
                 **misc):
        """Sets-up a socket bound/connected to an url

        xxx_ip: ip of publisher/subscriber/dealer/router
        xxx_port: port of publisher/subscriber/dealer/router
        xxx_key: key for filtering out messages (leave empty to receive all) (pub/sub only)
        xxx_bind: True for bind (only 1 socket can bind to 1 address) or false for connect (many can connect)
        """

        # get ZeroMQ version
        print("Current libzmq version is %s" % zmq.zmq_version())
        print("Current  pyzmq version is %s" % zmq.pyzmq_version())

        self.pub_socket = None
        self.sub_socket = None

        # set-up publish socket only if a port is given
        if pub_port:
            print("Publisher port is specified")
            self.pub_socket = self.zeromq_context(pub_ip, pub_port, zmq.PUB, pub_bind)
            # add variable with key
            self.pub_key = pub_key
            print("Publisher socket set-up complete")
        else:
            print("pub_port not specified, not setting-up publisher")

        # set-up subscriber socket only if a port is given
        if sub_port:
            print("Subscriber port is specified")
            self.sub_socket = self.zeromq_context(sub_ip, sub_port, zmq.SUB, sub_bind)
            self.sub_key = sub_key
            self.sub_socket.setsockopt(zmq.SUBSCRIBE, self.sub_key.encode('ascii'))
            print("Subscriber socket set-up complete")
        else:
            print("sub_port not specified, not setting-up subscriber")

        # set-up dealer socket only if a port is given
        if deal_port:
            print("Dealer port is specified")
            self.deal_socket = self.zeromq_context(deal_ip, deal_port, zmq.DEALER, deal_bind)
            self.deal_socket.setsockopt(zmq.IDENTITY, deal_key.encode('ascii'))
            # add variable with key f
            self.deal_topic = deal_topic
            print("Dealer socket set-up complete")
        else:
            print("deal_port not specified, not setting-up dealer")

        # set-up dealer socket only if a port is given; TODO better solution for multiple same sockets
        if deal2_port:
            print("Dealer port 2 is specified")
            self.deal2_socket = self.zeromq_context(deal2_ip, deal2_port, zmq.DEALER, deal2_bind)
            self.deal2_socket.setsockopt(zmq.IDENTITY, deal2_key.encode('ascii'))
            # add variable with key f
            self.deal2_topic = deal2_topic
            print("Dealer 2 socket set-up complete")
        else:
            print("deal2_port not specified, not setting-up dealer")

        # set-up router socket only if a port is given
        if rout_port:
            print("Router port is specified")
            self.rout_socket = self.zeromq_context(rout_ip, rout_port, zmq.ROUTER, rout_bind)
            print("Router socket set-up complete")
        else:
            print("rout_port not specified, not setting-up router")

        print("ZeroMQ sockets successfully set-up\n")

        # extra named arguments
        self.misc = misc

    def zeromq_context(self, ip, port, socket_type, bind):
        """Returns a bound / connected ZeroMQ socket through tcp with given ip and port

        ip+port: tcp://{ip}:{port}
        socket_type: ZeroMQ socket type; e.g. zmq.PUB / zmq.SUB
        bind: True for bind (only 1 socket can bind to 1 address) or false for connect (many can connect)
        """

        url = "tcp://{}:{}".format(ip, port)
        print("Creating ZeroMQ context on: {}".format(url))
        ctx = Context.instance()
        socket = ctx.socket(socket_type)
        if bind:
            socket.bind(url)
            print("Bind to {} successful".format(url))
        else:
            socket.connect(url)
            print("Connect to {} successful".format(url))

        return socket

    def start(self, async_func_list=None):
        """Starts asynchronously any given async function"""

        # activate publishers / subscribers
        if async_func_list:
            # capture ZeroMQ errors; ZeroMQ using asyncio doesn't print out errors
            # TODO working properly?
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

        else:
            print("No functions given, nothing to start")

    # @abstractmethod
    # async def pub(self):
    #     pass
