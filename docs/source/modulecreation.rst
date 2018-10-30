You can still create your modules with Python < 3.6, but it will be harder to separate the network logic with your Python classes. Or `use an import <https://quentin.pradet.me/blog/using-asynchronous-for-loops-in-python.html>`_ .

For cross-language & cross-platform support for modules (or to only use some of FACSvatar's modules), we use a pub-sub distributed messaging pattern through `ØMQ (ZeroMQ) <http://zeromq.org/>`_ . `Pip install <http://zeromq.org/bindings:python>`_ .
More information about creating your own modules can be found ...
