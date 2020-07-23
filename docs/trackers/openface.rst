OpenFace
========

Offline
-------
d

Real-time GUI
-------------
d


Use your own videos
-------------------
If you want to use your own FACS values extracted from a video do:

1. ``OpenFaceOffline.exe`` --> menu: ``Recording settings`` --> ``Output location``
#. ``OpenFaceOffline.exe`` --> menu: ``File`` --> ``Open Video``.
#. Copy .csv from your output location to *your_path*/FACSvatar/modules/input_facsfromcsv/*some_folder*
#. Run OpenFace offline module with: ``python main.py --csv_folder some_folder --csv_arg -1``


Building yourself
-----------------
d









------------------------
FACS input
------------------------
Animation can be either in real-time or in offline mode.
For the moment, FACSvatar is only working with OpenFace,
however any module that provides FACS based data could be used.

Real-time allows for interactive systems, but at present the quality of FACS tracking from OpenFace
is of lower quality in this mode.
If interactivity is not your goal, the offline version is most likely a better choice.

^^^^^^^^^^^^^^
Real-time
^^^^^^^^^^^^^^
Note: Requires 1 Windows PC (due to ZeroMQ being integrated in the GUI)

For the real-time version of FACSvatar we need to use a modified OpenFace which includes a ZeroMQ component
to stream AU, gaze and head pose data out of it into.
You can either

* Download a `modified OpenFace v2.1.0 <https://github.com/NumesSanguis/FACSvatar/releases/download/v0.3.4-alpha-release/openface_2.1.0_zeromq.zip>`_
   * All copyright of OpenFace belongs to Carnegie Mellon University. By using this software, you agree to their licensing terms found here: https://github.com/TadasBaltrusaitis/OpenFace/
* Or build the modified version yourself following these instructions:

""""""""""""""""""""""""""
Build OpenFace with ZeroMQ
""""""""""""""""""""""""""

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



^^^^^^^^^^^^^^
Offline
^^^^^^^^^^^^^^
- (Windows GUI) Use the modified OpenFace found under the header `Real-time`_ or
  Download OpenFace_2.0.6_win_xYY.zip from: https://github.com/TadasBaltrusaitis/OpenFace/releases
- (Other) Follow instructions here: https://github.com/TadasBaltrusaitis/OpenFace/wiki#installation