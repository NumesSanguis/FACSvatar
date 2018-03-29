"""Opens a proxy bus between 2 ports for a N-proxy-M PubSub pattern

Similar to a ROS topic (named bus)
TODO: register somewhere for a bus overview"""

# Copyright (c) Stef van der Struijk.
# License: GNU Lesser General Public License


import sys
import zmq
from zmq import Context


class ProxyPub:
    def __init__(self, address='127.0.0.1', port_pubs='5570', port_subs='5571'):
        self.context = Context.instance()
        # 2 sockets, because we can only bind once to a socket (as opposed to connect)
        self.url1 = "tcp://{}:{}".format(address, port_pubs)
        self.url2 = "tcp://{}:{}".format(address, port_subs)

        self.xpub_xsub_proxy()

    # N publishers to 1 sub; proxy 1 sub to 1 pub; publish to M subscribers
    def xpub_xsub_proxy(self):
        print("Init proxy")

        # Socket subscribing to publishers
        frontend_pubs = self.context.socket(zmq.XSUB)
        frontend_pubs.bind(self.url1)

        # Socket publishing to subscribers
        backend_subs = self.context.socket(zmq.XPUB)
        backend_subs.bind(self.url2)

        print("Try: Proxy... CONNECT!")
        zmq.proxy(frontend_pubs, backend_subs)
        print("CONNECT successful!")


if __name__ == '__main__':
    # get ZeroMQ version
    print("Current libzmq version is %s" % zmq.zmq_version())
    print("Current  pyzmq version is %s" % zmq.pyzmq_version())

    print("Arguments given: {}".format(sys.argv))
    print("0, 2, or 3 arguments are expected (port_pubs, port_subs, (address)), e.g.: 5570 5571 127.0.0.1")

    # no arguments
    if len(sys.argv) == 1:
        ProxyPub()

    # local network, only ports
    elif len(sys.argv) == 3:
        ProxyPub(port_pubs=sys.argv[1], port_subs=sys.argv[2])

    # full network control
    elif len(sys.argv) == 4:
        ProxyPub(port_pubs=sys.argv[1], port_subs=sys.argv[2], address=sys.argv[3])

    else:
        print("Received incorrect number of arguments")
