====================
Quickstart
====================
See :doc:`defaultsetup` for FACSvatar setup without Docker.

FACSvatar is tested on Ubuntu and Windows, but should work on MacOS as well.

------------------------
0. Get the code
------------------------
Download the FACSvatar repository:

* ``git clone https://github.com/NumesSanguis/FACSvatar.git``
* Go to `FACSvatar GitHub page <https://github.com/NumesSanguis/FACSvatar>`_ and press the green ``Clone or Download`` button --> ``Download ZIP``

------------------------
1. Docker install
------------------------
It is best to follow the `official Docker instructions <https://docs.docker.com/install/#supported-platforms>`_ for installation.

^^^^^^^^^^^^^^^^^
Ubuntu
^^^^^^^^^^^^^^^^^
Direct links:

* Docker install: https://docs.docker.com/install/linux/docker-ce/ubuntu/
* Docker compose (run all Docker images and link them with 1 command): https://docs.docker.com/compose/install/
* No ``sudo`` needed anymore for Docker commands: ``sudo usermod -a -G docker $USER``

------------------------------------------------
2. Start FACSvatar Docker images
------------------------------------------------
With a terminal opened in folder `FACSvatar/modules`:

* ``docker-compose up``  (this will start all FACSvatar modules as Docker container using `docker-compose.yml`)

------------------------
3. Start Unity3D
------------------------
1. Download unity_FACSvatar compiled / run with editor:

* `unity_FACSvatar.exe (Windows) <https://>`_
* :ref:`Linux / Mac / Unity3D editor (documentation) <unity3d-setup>`.

2. Double click .exe / Press play button in Unity3D editor

------------------------
4. FACSvatar Offline
------------------------

1. Open 2nd terminal in folder `FACSvatar/modules` and execute: ``docker-compose exec facsvatar_facsfromcsv bash``
2. (Now inside Docker containter) Start facial animation with: ``python main.py --pub_ip facsvatar_bridge``


-------------------------------------------------
4. FACSvatar real-time with webcam (Windows only)
-------------------------------------------------

1. Download a `modified OpenFace with ZeroMQ (v2.0.6) <https://numessanguis.stackstorage.com/s/qHqzGSi5zxC73rk/>`_ (`see copyright <https://github.com/TadasBaltrusaitis/OpenFace/blob/master/Copyright.txt>`_) –> menu: File –> Open Webcam


------------------------------------------------
Quickstart video
------------------------------------------------
See the quickstart video:


------------------------------------------------
Docker advanced
------------------------------------------------
For more advanced Docker commands, and e.g. how to use your own .csv files created with OpenFace,
see: :doc:`docker`