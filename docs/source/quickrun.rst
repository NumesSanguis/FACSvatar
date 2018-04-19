==================
FACSvatar quickrun
==================

FACSvatar can currently be ran in 2 modes:

- Offline

   - Requires Python >= 3.6

- Online

   - Requires Python >= 3.5
   - Requires Windows (on at least 1 PC for OpenFace)

We hope this process will be simplified with the use of Docker containers in the future.

------------
Prerequisite
------------
^^^^^^^
Both
^^^^^^^
1. Get the code of this project through 1 of these method:

   - Terminal: :code:`git clone https://github.com/NumesSanguis/FACSvatar.git`
   - GitHub Desktop: `https://desktop.github.com/ <https://desktop.github.com/>`_

#. Follow Python env setup here: :doc:`modules/env-setup`
#. Install Unity 3D (Personal, tested with 2017.3)

   - `Windows <https://store.unity.com/download?ref=personal>`_
   - `Ubuntu <https://forum.unity.com/threads/unity-on-linux-release-notes-and-known-issues.350256/page-2>`_

^^^^^^^
Offline
^^^^^^^
pub_facs.py requires Python 3.6 due to a async generator function.


^^^^^^
Online
^^^^^^

1. Download modified OpenFace (more info coming)

   - All copyright of OpenFace belongs to Carnegie Mellon University. By using that software, you agree to their licensing terms found here: `https://github.com/TadasBaltrusaitis/OpenFace/ <https://github.com/TadasBaltrusaitis/OpenFace/>`_


-----------------
Running FACSvatar
-----------------
These steps are intended to work on a single PC, due the address being localhost.
For across computer data transport, give address arguments to the functions (more instructions in the future).

0. Open Unity 3D, navigate to FACSvatar/unity_FACSvatar and open project
#. Press 'play' in the Unity editor
#. Open new terminals and don't forget to run :code:`source/conda activate facsvatar`!
#. Terminal: :code:`python n_proxy_m_bus.py` (/modules/)
#. Terminal: :code:`python pub_blend.py` (/modules/process_facstoblend/)
#. One of the following:

   - Offline, Terminal: :code:`python pub_facs.py` (/modules/input_facsfromcsv/)
   - Online (On Windows): run :code:`OpenFaceOffline.exe` --> File --> Open Webcam
   - All copyright of OpenFace belongs to Carnegie Mellon University. By using that software, you agree to their licensing terms found here: `https://github.com/TadasBaltrusaitis/OpenFace/ <https://github.com/TadasBaltrusaitis/OpenFace/>`_

#. See an avatar move its head and make facial expressions!