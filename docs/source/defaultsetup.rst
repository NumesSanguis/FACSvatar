========================
Default set-up
========================
Probably you want to either run FACSvatar in real-time mode for interactive purposes or
create high-quality facial animation/pictures.

* Real-time: Modified OpenFace --> FACSvatar modules --> Unity3D
* Offline: (Modified) OpenFace --> .csv --> FACSvatar modules --> Blender


There 3 things that have to be setup:

1. `FACS input`_ (Modified OpenFace)
#. `FACSvatar modules`_ (Python 3.5+)
#. `Animation-Visualization`_ (Unity3D / Blender)

If you're already done setting FACSvatar up, please head here: :doc:`firstrun`

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
Note: Requires 1 Windows PC (due to ZeroMQ being integrated in the GUI)

For the real-time version of FACSvatar we need to use a modified OpenFace which includes a ZeroMQ component
to stream AU, gaze and head pose data out of it into.
You can either

* Download a `modified OpenFace v2.0.6 <https://numessanguis.stackstorage.com/s/qHqzGSi5zxC73rk/>`_
   * All copyright of OpenFace belongs to Carnegie Mellon University. By using this software, you agree to their licensing terms found here: https://github.com/TadasBaltrusaitis/OpenFace/
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
- (Windows GUI) Use the modified OpenFace found under the header `Real-time`_ or
  Download OpenFace_2.0.6_win_xYY.zip from: https://github.com/TadasBaltrusaitis/OpenFace/releases
- (Other) Follow instructions here: https://github.com/TadasBaltrusaitis/OpenFace/wiki#installation

------------------------
FACSvatar modules
------------------------
At present, all the core modules work with Python, so let's setup an environment.
FACSvatar recommends using `Anaconda <https://www.anaconda.com/download/>`_ for managing packages and
virtual environments for Python, therefore code instructions assume Anaconda.
Probably ``pip install ..`` will do the same without problems.

This project uses the `Asyncio library <https://asyncio.readthedocs.io/en/latest/>`_ for
asynchronous code execution, hence we use Python 3.6+ (although some modules work with Python 3.5).
I wanted to keep it Python 3.5 compatible, but due to the use of asynchronous generators used
in some standard modules, the default version is 3.6+.

^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Anaconda setup
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   conda create --name facsvatar python=3.7  # new virtual env and force python 3.x
   #conda install python=3.7  # IF you already have an existing env
   source activate facsvatar  # activate env (Windows: conda activate facsvatar)

   conda install pyzmq  # make sure it's for py3.6
   conda install pandas  # library for dataframes; used for .csv reading and JSON-to-Dataframe

   # Basic environment setup finished, but ipykernel setup recommended for control panel GUI

   conda install ipykernel  # allows the use of env kernels in jupyter notebook
   conda install ipywidgets  # GUI elements in jupyter notebook
   python -m ipykernel install --user --name facsvatar --display-name "py3 facsvatar"  # enable our env as kernel in jupyter notebook

^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Test new environment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Go into a Python environment in your terminal with: ``python`` - `enter`

.. code-block:: python

   import zmq
   print("Current libzmq version is %s" % zmq.zmq_version())  # 4.2.5 at time of writing
   print("Current  pyzmq version is %s" % zmq.__version__)  # 17.1.2 at time of writing

------------------------
Animation-Visualization
------------------------

.. _unity3d-setup:

^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Unity3D - game engine
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Recommended for real-time or game like interaction applications. Unity3D version 2018.2.10f1 recommended.

1. Download either Unity3D (single version) or UnityHub (recommended; manages Unity3D versions)

   * Windows/Mac: `Download Unity(3D/Hub) <https://unity3d.com/get-unity/download/archive>`_
   * Linux: `Download UnityHub <https://public-cdn.cloud.unity3d.com/hub/prod/UnityHubSetup.AppImage>`_
   * Linux: `Download Unity3D <https://forum.unity.com/threads/unity-on-linux-release-notes-and-known-issues.350256/page-2>`_

2. Open the FACSvatar project in Unity3D by navigation to ``FACSvatar/unity_FACSvatar`` folder
   in the FACSvatar GitHub repro.
3. In the ``Asset Store`` tab: Search for JSON .NET for Unity (by PARENTELEMENT, LLC) and click ``Download``.

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Blender - open source 3D creation suite
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
| Sorry, these instructions are still a mess.
| Recommended for high-quality image/video rendering and post-modification.
| Hopefully going to be real-time and as a Blender add-on when version 2.8 with EEVEE is released. 

1. `Download Blender <https://www.blender.org/>`_ 
#. `Download Manuel Bastioni LAB (MBLAB) add-on for Blender <http://www.manuelbastioni.com/>`_
#. Start Blender in terminal by opening a terminal in the folder ``blender-2.79`` and run:

   * Windows: ``blender.exe`` (TODO test in Windows)
   * Ubuntu: ``./blender``

#. Import the .zip into Blender to install add-on: File --> User Preferences --> Add-ons --> Install Add-on from File
   --> manuelbastionilab_161a.zip --> check-mark in front of ``Characters: ManuelbastioniLAB``
#. Create a model with MBLAB by clicking ``Init character`` (leave default options for export to Unity3D), modify and
   press ``Finalize tools --> Finalize``
#. If Blender version is below 2.8 (likely the case if done in 2018 or earlier):

   * Create a Python 3.5 environment by following the instructions under `Anaconda setup`_ , but replacing ``--name facsvatar python=3.7`` for ``--name blender python=3.5`` (you can skip commands about ``Jupyter Notebook``)

#. Change line 7 in ``FACSvatar/blender/facsvatar_zeromq.py`` to correctly point to your blender anaconda environment.

"""""""""""""""""""""""""""""""""""""
Enabling FACS sliders in MBLAB add-on
"""""""""""""""""""""""""""""""""""""
Copy .json files found in ``FACSvatar/modules/process_facstoblend/au_json`` to:

* Windows: ``C:\Users\*user*\AppData\Roaming\Blender Foundation\Blender\2.79\scripts\addons\manuelbastionilab\data\expressions_comb\human_expressions\``
* Ubuntu: ``/home/*user*/.config/blender/2.79/scripts/addons/manuelbastionilab/data/expressions_comb/human_expressions/``

.. ------------------------
   Setup complete!
   ------------------------
   Please head to this page for how to run FACSvatar: :doc:`firstrun`