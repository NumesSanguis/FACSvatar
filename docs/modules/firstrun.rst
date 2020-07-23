========================
First run (non-Docker)
========================
On this page are the instructions on how to run the Python modules included in FACSvatar.
For the quickstart with Docker, go here: :doc:`Quickstart <../getting_started/README>`

* Real-time: Modified OpenFace --> **FACSvatar modules** --> Unity3D
* Offline: (Modified) OpenFace --> .csv --> **FACSvatar modules** --> Blender


--------------------------
Prepare Python environment
--------------------------



------------------------
Start modules
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

Congratulations, data should be flowing between the modules now!
To see an avatar move, use Unity3D / Blender move its head, eyes and face!



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