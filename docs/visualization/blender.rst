Blender
===============
The minimal support Blender version is v2.80.
If you need v2.79 support, check out v3.4 of this documentation (no FACSvatar Blender add-on).


FACSvatar-Blender add-on
------------------------



Modify the FACSvatar-Blender add-on
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Download the code
"""""""""""""""""

Git pull of FACSvatar with support for submodules:

.. code-block:: bash

   git clone --recurse-submodules https://github.com/NumesSanguis/FACSvatar-Blender

or manually clone latest version of the add-on:

.. code-block:: bash

   git clone https://github.com/NumesSanguis/FACSvatar  # if not cloned yet.
   cd FACSvatar/addons
   git clone https://github.com/NumesSanguis/FACSvatar-Blender

If you normally cloned FACSvatar and want to pull the add-on as submodule, or just update:

.. code-block:: bash

   git submodule init  # first time only
   git submodule update

More information on git submodules: https://git-scm.com/book/en/v2/Git-Tools-Submodules