Module Overview
===============

FACSvatar is a modular framework that connects different software over ZeroMQ (data messaging library) to enable both
the animation and analysis of AUs.
At present, a standard workflow is to use a modified `OpenFace <https://github.com/TadasBaltrusaitis/OpenFace/>`_.
(FACS input) that is transported and manipulated (smoothed) through FACSvatar and then forwarded to
either Unity3D (real-time) or Blender (high-quality) animation.

Almost all modules have a ``main.py`` which functions as entry point for that module.
To see what additional arguments are available, execute: ``python main.py -h``.

.. seealso::

   First time using these modules?
   Please head over to: :doc:`firstrun`


Core modules
------------
These modules provide the basic functionality of FACSvatar and are (almost) always needed.


FACS from OpenFace csv
^^^^^^^^^^^^^^^^^^^^^^
Allows for the OpenFace's analysis results to be send as messages through FACSvatar.
Looks in the folder given as argument (``--csv_folder``) for the specified .csv file(s) ``--csv_arg``.
Well, actually it first checks ``specifed_folder_clean`` to see if a cleaned version from the .csv file already exists.
If not, it creates this ``_clean`` folder with the cleaned .csv.
"Cleaning" here means removing not used columns, removing trailing spaces from column names, etc.

In multi-avatar setups, you can send 2 or more .csv files in parallel.
For details, see:

.. _module-overview_bridge:

Bridge
^^^^^^
This module allows for modules to communicate in a m-to-n fashion.


.. _module-overview_mb-lab:

FACS to MB-Lab blend shapes
^^^^^^^^^^^^^^^^^^^^^^^^^^^
Convert AU values based on FACS to blend shape values found in avatars created with MB-Lab.


.. _module-overview_openface-offline:

OpenFace offline (use .csv files created with OpenFace)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
OpenFace creates .csv files after analyzing a video.
This module reads those .csv's and sends its data as a message per frame to FACSvatar.

Please see ':ref:`trackers_openface_own-videos`' if you want to use your own OpenFace analysis results.



Additional modules
------------------
These modules add extra functionality to FACSvatar

Deep Neural Network
^^^^^^^^^^^^^^^^^^^
d