========================
FACSvatar default set-up
========================

There 3 things that have to be setup:

1. `FACS input`_ (Modified OpenFace)
#. `FACSvatar modules`_ (Python 3.5+)
#. `Animation-Visualization`_ (Unity3D / Blender)

| but before that, let's download the FACSvatar GitHub repro with:
| ``git clone https://github.com/NumesSanguis/FACSvatar.git``

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
Note: Windows only (due to ZeroMQ being integrated in the GUI)

For the real-time version of FACSvatar we need to use a modified OpenFace which includes a ZeroMQ component
to stream AU, gaze and head pose data out of it into.
You can either

* Download a `modified OpenFace v2.0.6 <https://numessanguis.stackstorage.com/s/qHqzGSi5zxC73rk/>`_
* Or build the modified version yourself following these instructions:

""""""""""""""""""""""""""
Build OpenFace with ZeroMQ
""""""""""""""""""""""""""

- Download Source code OpenFace 2.0.6 from https://github.com/TadasBaltrusaitis/OpenFace/releases
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

------------------------
FACSvatar modules
------------------------
d

------------------------
Animation-Visualization
------------------------
d