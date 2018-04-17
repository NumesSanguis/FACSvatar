============================================
Environment setup for running Python modules
============================================

The easiest way to use the modules will be through Docker images, but since those are not ready yet, we'll have to set-up a Python environment.

FACSvatar recommends using `Anaconda <https://www.anaconda.com/download/>`_ for managing packages and virtual environments for Python, therefore code instructions assume Anaconda. Probably ``pip install ..`` will do the same without problems.
This project uses the `Asyncio library <https://asyncio.readthedocs.io/en/latest/>`_ for asynchronous code execution, hence we use Python 3.6.
I wanted to keep it Python 3.5 compatible, but due to the use of asynchronous generators used in the standard modules, the minimum version is 3.6.
You can still create your modules with Python < 3.6, but it will be harder to separate the network logic with your Python classes. Or `use an import <https://quentin.pradet.me/blog/using-asynchronous-for-loops-in-python.html>`_ .

For cross-language & cross-platform support for modules (or to only use some of FACSvatar's modules), we use a pub-sub distributed messaging pattern through `ØMQ (ZeroMQ) <http://zeromq.org/>`_ . `Pip install <http://zeromq.org/bindings:python>`_ .
More information about creating your own modules can be found ...

--------------
Anaconda setup
--------------

.. code-block:: bash

   conda create --name facsvatar python=3.6  # new virtual env and force python 3.6
   #conda install python=3.6  # IF you already have an existing env
   source activate facsvatar  # activate env (Windows: conda activate facsvatar)
   
   conda install pyzmq  # make sure it's for py3.6
   conda install pandas  # library for dataframes; used for .csv reading and JSON-to-Dataframe

   # maybe test new env first with instructions below
   conda install ipykernel  # allows the use of env kernels
   python -m ipykernel install --user --display-name "py3 facsvatar"  # enable our env as kernel

--------------------
Test new environment
--------------------

.. code-block:: python

   import zmq
   print("Current libzmq version is %s" % zmq.zmq_version())  # 4.2.3 in my case
   print("Current  pyzmq version is %s" % zmq.__version__)  # 17.0.0 in my case

-------
Modules
-------

:doc:`input-facsfromcsv`
