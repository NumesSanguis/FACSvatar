OpenFace
========

Download OpenFace (choose 1):

* From the `official GitHub <https://github.com/TadasBaltrusaitis/OpenFace/releases>`_ (offline use only)
* Download a `modified OpenFace v2.1.0 <https://github.com/NumesSanguis/FACSvatar/releases/download/v0.3.4-alpha-release/openface_2.1.0_zeromq.zip>`_
  (offline or real-time use).
* Build OpenFace with ZeroMQ component yourself, see: :ref:`trackers_openface_build`

The modified version has ZeroMQ added to it's interface (C#), which is needed to get the AU values into FACSvatar.
The GUI is only available for Windows, therefore real-time animation requires a Windows PC
(you can still use e.g. Ubuntu for the other modules if you follow the :doc:`../advanced/multi_machines` instructions).

.. note::

   **Requested:** Help from a C++ programmer to implement a ZeroMQ component in the C++ part of OpenFace.
   That would allow OpenFace to be used on any computer OS.
   Starting point: https://github.com/TadasBaltrusaitis/OpenFace/issues/492#issuecomment-641814378
   Please make an `issue on GitHub <https://github.com/NumesSanguis/FACSvatar/issues>`_ if you want to do this.

.. warning::

   The output of the Real-time approach is slightly different from the Offline approach.
   Once OpenFace is done analyzing a video, it applies some post-processing, meaning the Offline approach is slightly
   more accurate.
   Therefore, **only use the Real-time approach for real-time use cases**.
   Otherwise, use the generated .csv.

.. warning::

   All copyright of OpenFace belongs to Carnegie Mellon University.
   By using this software, you agree to their licensing terms.
   Check the :doc:`../misc/license` page to find out more (especially if you want to use it in **commercial projects**).


Download OpenFace tracker models
--------------------------------
**TODO** Execute download scripts

.. note::

   Additional OpenFace instructions can be found here: https://github.com/TadasBaltrusaitis/OpenFace/wiki#installation

Real-time GUI
-------------
1. Double click `OpenFaceOffline.exe` –> menu: File –> Open Webcam

Windows 7, 8 and 10 Home version <2004 - only
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. Navigate inside folder `openface_x.x.x_zeromq`
#. (Windows 7/8/10 Home version <2004 - only) Get Docker machine ip by opening a 2nd terminal and execute: `docker-machine ip` (likely to be 192.168.99.100)
#. (Windows 7/8/10 Home version <2004 - only) Open `config.xml`, change `<IP>127.0.0.1</IP>` to `<IP>machine ip from step 3</IP>` (`<IP>192.168.99.100</IP>`) and save and close.
#. Double click `OpenFaceOffline.exe` –> menu: File –> Open Webcam

.. warning::

   Requires a Windows PC (for now). Also, it's pretty heavy on the CPU of the PC.

.. _trackers_openface_offline:

Offline
-------
If you analyze a video with OpenFace, it will output a .csv file with the analysis results.
FACSvatar only requires the AU values and ignores

Python
^^^^^^

1. ``conda activate facsvatar``
2. ``cd *your_path*/FACSvatar/modules/input_facsfromcsv``
3. ``python main.py``

   * Execute ``python main.py -h`` to see more possible arguments, including explanations

Docker
^^^^^^
1.. Go inside Docker container: ``docker-compose exec facsvatar_facsfromcsv bash`` (same as Quickstart)
#. ``python main.py``



.. _trackers_openface_own-videos:

Use your own videos
-------------------
If you want to use your own FACS values extracted from a video do:

1. ``OpenFaceOffline.exe`` --> menu: ``Recording settings`` --> ``Output location``
#. ``OpenFaceOffline.exe`` --> menu: ``File`` --> ``Open Video``.
#. Wait for analysis to be completed and the .csv to be created.


Python
^^^^^^
#. Copy .csv from your output location to: ``*your_path*/FACSvatar/modules/input_facsfromcsv/openface/*some_folder*``

   .. warning:: NOT in a folder with ``_clean`` at the end (e.g. not ``default_clean``).
     A ``some_folder_clean`` is automatically generated after e.g. ``some_folder/OF_output.csv`` has been been passed
     as an argument to ``main.py``.

#. Open a terminal and follow the steps under :ref:`trackers_openface_offline`, but tell it to check your "some_folder":
   ``python main.py --csv_folder some_folder --csv_arg -1``


Docker
^^^^^^
If you're using Docker to run FACSvatar, you have to do 1 step more to give the container access to your new file.

**Copy into container**:

0. Follow the :doc:`Quickstart <../getting_started/README>`
1. Copy the .csv into the container: ``docker cp foo.csv facsvatar_facsfromcsv:/openface/*your_folder*/foo.csv``
#. Open a terminal and follow the Docker steps under :ref:`trackers_openface_offline`, but tell it
   to check your "some_folder": ``python main.py --csv_folder some_folder --csv_arg -1``

**TODO: Give Docker access to folder on disk through mounting that folder via the Docker file**



.. _trackers_openface_build:

Build OpenFace with ZeroMQ
--------------------------
.. warning::

   Last tested with OpenFace v2.1.0

- Download Source code OpenFace 2.1.0 from https://github.com/TadasBaltrusaitis/OpenFace/releases
- Install Visial Studio 2015 / 2017
- Run download_models.ps1 / .sh
  or copy ``cen_patches_x.xx_of.dat`` to ``OpenFace\lib\local\LandmarkDetector\model\patch_experts``

1. Overwrite `MainWindow.xaml.cs` in `OpenFace\gui\OpenFaceOffline` with openface/MainWindow.xaml.cs from FACSvatar GitHub
#. Open visual studios:

   * Open `OpenFace/OpenFace.sln` with Visual Studio 2015
   * Open `OpenFace_vs2017.sln` with Visual Studio 2017 (didn't work for me so far)

#. (In visual studio) Right click in "Solution Explorer" on "OpenFaceOffline" --> `Manage NuGet Packages...`
#. Browse and search for `netmq`; install NetMQ by NetMQ with version v4.0.0.1 (AsyncIO.0.1.26)
   note: Search under "Browse" not "Installed"

   * Don't update AsyncIO to a newer version (v0.1.40)

#. Search for `json`; Install Newtonsoft.Json by James Newton-King v11.0.2
#. Select OpenFaceOffline --> Release, x64, OpenFaceOffline --> Build --> (Re)build OpenFaceOffline
#. Copy `config.xml` from FACSvatar GitHub and put it at `OpenFace\x64\Release\config.xml` # DON'T FORGET - otherwise crashes at startup
