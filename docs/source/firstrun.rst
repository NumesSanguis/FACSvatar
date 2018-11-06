========================
First run
========================
Make sure you've setup FACSvatar by following the instructions here: :doc:`defaultsetup`

------------------------
Unity3D
------------------------

0. Have FACSvatar project opened in Unity3D
1. Press play button

------------------------
FACSvatar modules
------------------------

Open 3 terminals

1. Start bridge module

   1. ``source activate facsvatar``
   2. ``cd *your_path*/FACSvatar/modules``
   3. ``python n_bridge_m.py``

#. Start FACS to Blend Shapes module

   1. ``source activate facsvatar``
   2. ``cd *your_path*/FACSvatar/modules/process_facstoblend``
   3. ``python main.py``

#. Start OpenFace offline module (input)

   1. ``source activate facsvatar``
   2. ``cd *your_path*/FACSvatar/modules/input_facsfromcsv``
   3. ``python main.py``

Congratulations, you should now see an avatar in Unity3D move its head, eyes and face!

------------------------------------------------
Real-time (needs Windows PC)
------------------------------------------------
You want to use your own facial expressions you say?
Skip starting the OpenFace offline module and instead start the modified OpenFace GUI: ``OpenFaceOffline.exe`` –> menu: ``File`` –> ``Open Webcam``.

Warning, pretty heavy on the CPU of the PC.


------------------------------------------------
Blender
------------------------------------------------
Sorry, these instructions are still a mess.

0. Do these steps before running other FACSvatar modules.
1. Copy the first 2 lines of code found in ``FACSvatar/blender/facsvatar_zeromq.py`` into the Blender terminal (but change path to match your system's path to that file).
2. Your Blender now freezes and waits for data from Blend Shapes module. (You can safely send 1x a cancel command in terminal that runs Blender to cancel listening for data).
3. Yes, I know, the freezing part is bad. This, and all these instructions, should be gone once the Blender component of FACSvatar is turned into a Blender add-on.
4. Data is streamed into the timeline of Blender and can be modified following the normal workflow of Blender.

------------------------
Next
------------------------
Every Python module has a help function, giving more information on what arguments you can give.
Type: ``python module_x.py --help``
You can for example run modules on different PCs by changing the IP where the module is subscribed to for data with: ``python module_x.py --sub_ip 192.168.xxx.xxx``

*Coming soon*: Advanced instructions