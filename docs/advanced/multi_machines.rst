Multi-machines setup
====================
The instructions on this page explain to you how you can let modules, that are running on multiple machines,
send data to each other.

.. warning::
   Instructions below untested

FACSvatar uses a `pub-sub <http://zguide.zeromq.org/py:chapter1#Getting-the-Message-Out>`_
pattern to exchange messages between modules.
To exchange messages, one module's socket has to **bind** to an ip address and a port.
Any number of other modules' sockets will be able to **connect** to this port to start exchanging messages
with the module's socket that has **bind** to that port.
Only 1 IP+port can be bound to at the same time.
There is no order for connecting
(a socket that wants to connect can be called before the target socket has bound to a port binding).

Both a publisher (1-n) and a subscriber (m-1) socket can bind/connect to an address.

If you want to message between modules that are running on different machines, the module that connects
need to know the IP of the host PC where a module binds.


Modules
-------
**TODO** Overview of which modules connect, and which modules bind to what port by default.

Python
^^^^^^

1. Setup Python on all machines involved, see :doc:`../modules/firstrun`.
2. Navigate with a terminal inside a terminal folder, e.g. ``cd FACSvatar/modules/input_facsfromcsv``
3. Add the IP of the machine that the module you want to **connect** to is running on (bind is always the host machine),
   e.g.: ``python main.py --pub_ip 192.168.xxx.xxx``.

To see all available arguments of a module, execute: ``python main.py -h``


Individual Docker containers
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Do not use the ``docker-compose(_x).yml`` files, and instead modify the Docker files inside module folders.
Add the target IP as extra argument.


Docker compose
^^^^^^^^^^^^^^
TODO: Should be possible to set external IPs here?


Visualization
-------------

Unity3D
^^^^^^^
1. Open the folder ``unity_FACSvatar`` with Unity3D (2018.2.20f1) as a project with Unity3D
2. Change the ``Sub_to_ip`` IP from 127.0.0.1 to the IP of the target machine running the module you want to connect to.
   (See from `8:20 (8:50) of the Quickstart video <https://youtu.be/OOoXDfkn8fk?t=500>`_)

Blender3D
^^^^^^^^^
Change IP in the FACSvatar-Blender add-on menu inside Blender.
