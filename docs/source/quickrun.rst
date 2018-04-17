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

-------
Offline
-------
pub_facs.py requires Python 3.6 due to a async generator function.


-------
Online
-------

1. Download modified OpenFace (more info coming)


-------
Both
-------
These steps are intended to work on a single PC, due the address being localhost.
For across computer data transport, give address arguments to the functions.

0. Follow setup here: :doc:`modules/env-setup`
#. Press 'play' in the Unity editor
#. Terminal: :code:`python n_proxy_m_bus.py` (/modules/)
#. Terminal: :code:`python pub_blend.py` (/modules/process_facstoblend/)
#. One of the following:

   - Offline, Terminal: :code:`python pub_facs.py` (/modules/input_facsfromcsv/)
   - Online (On Windows): run :code:`OpenFaceOffline.exe`

#. See an avatar move its head and make facial expressions!