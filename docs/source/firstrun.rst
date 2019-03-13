========================
First run
========================
Make sure you've setup FACSvatar (real-time with Unity3D or offline Blender)
by following the instructions here: :doc:`defaultsetup`

* Real-time: Modified OpenFace --> FACSvatar modules --> Unity3D
* Offline: (Modified) OpenFace --> .csv --> FACSvatar modules --> Blender


-----------------------------------
Visualization: Unity3D - real-time
-----------------------------------

0. Have FACSvatar project opened in Unity3D
1. Press play button

------------------------------------------------
Visualization: Blender - offline
------------------------------------------------
Sorry, these instructions are still a mess. Look at the Blender tutorial video for clearer instructions.

0. Do these steps before running other FACSvatar modules.
1. Copy the first 2 lines of code found in ``FACSvatar/blender/facsvatar_zeromq.py`` into the Blender terminal (but change path to match your system's path to that file).

* Windows: Change ``/`` to ``\\``

2. Your Blender now freezes and waits for data from Blend Shapes module. (You can safely send 1x a cancel command in terminal that runs Blender to cancel listening for data).
3. Yes, I know, the freezing part is bad. This, and all these instructions, should be gone once the Blender component of FACSvatar is turned into a Blender add-on.
4. Data is streamed into the timeline of Blender and can be modified following the normal workflow of Blender.

------------------------
FACSvatar modules
------------------------

Open 3 terminals

1. Start bridge module

   1. ``source activate facsvatar``
   2. ``cd *your_path*/FACSvatar/modules/process_bridge``
   3. ``python main.py``

#. Start FACS to Blend Shapes module

   1. ``source activate facsvatar``
   2. ``cd *your_path*/FACSvatar/modules/process_facstoblend``
   3. ``python main.py``

#. Start OpenFace offline module (input)

   1. ``source activate facsvatar``
   2. ``cd *your_path*/FACSvatar/modules/input_facsfromcsv``
   3. ``python main.py``

Congratulations, you should now see an avatar in Unity3D / Blender move its head, eyes and face!

If you want to use your own FACS values extracted from a video do:

1. ``OpenFaceOffline.exe`` --> menu: ``Recording settings`` --> ``Output location``
#. ``OpenFaceOffline.exe`` --> menu: ``File`` --> ``Open Video``.
#. Copy .csv from your output location to *your_path*/FACSvatar/modules/input_facsfromcsv/*some_folder*
#. Run OpenFace offline module with: ``python main.py --csv_folder some_folder --csv_arg -1``

------------------------------------------------
Real-time (needs Windows PC)
------------------------------------------------
You want to use your own facial expressions in real-time you say?
Skip starting the OpenFace offline FACSvatar module and instead start the modified OpenFace GUI:
``OpenFaceOffline.exe`` --> menu: ``File`` --> ``Open Webcam``.

Warning, pretty heavy on the CPU of the PC.


------------------------
Next
------------------------
Every Python module has a help function, giving more information on what arguments you can give.
Type: ``python module_x.py --help``
You can for example run modules on different PCs by changing the IP where the module is subscribed to for data with: ``python module_x.py --sub_ip 192.168.xxx.xxx``

*Coming soon*: Advanced instructions

For importing models to Unity3D, follow the instructions here: http://manuelbastionilab.wikia.com/wiki/Unity_3D