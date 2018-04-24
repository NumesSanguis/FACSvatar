=============
Blender setup
=============

I hope everything down here can be turned into a Blender addon someday :)

-----

As described here: https://blender.stackexchange.com/questions/41258/install-python-module-for-blender/76124

We have to point to the PyZMQ library. Blender 2.79b comes with Python 3.5, but our environment uses Python 3.6, so we cannot directly point to the libraries installed here.
We have 2 options to solve this:

 - Make a new environment with Python 3.5 and PyZMQ
 - Install the latest Blender version from Blender Builder (https://builder.blender.org/download)

# Option 1: Python 3.5 env

.. code-block:: bash

   conda create --name blender python=3.5  # new virtual env and force python 3.5
   conda install python=3.5  # IF you already have an existing env
   source activate blender  # activate env
   
   conda install pyzmq  # make sure it's for py3.6
   python  # let's test our installation


# Blender

Startup Blender. Drag 1 window, and set it to the Python console.
Copy the contents of "blender/call_script.py" in the terminal (and point to the Python script "blender/AU_set_shapekey.py").
Now we c


# TODO

Copy recorded facial expressions to any MB character:
https://docs.blender.org/manual/en/dev/modeling/modifiers/deform/surface_deform.html