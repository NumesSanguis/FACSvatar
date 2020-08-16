First run (non-Docker)
=======================
On this page are the instructions on how to run the Python modules included in FACSvatar.
For the quickstart with Docker, go here: :doc:`Quickstart <../getting_started/README>`

* Real-time: Modified OpenFace --> **FACSvatar modules** --> Blender / Unity3D
* Offline: (Modified) OpenFace --> .csv --> **FACSvatar modules** --> Blender / Unity3D

We're assuming here that the avatar being target is created with MB-Lab.


.. _modules_firstrun:

Prepare Python environment
--------------------------
At present, all the core modules work with Python, so let's setup an environment.
FACSvatar recommends using `Anaconda <https://www.anaconda.com/download/>`_ for managing packages and
virtual environments in Python, therefore code instructions assume Anaconda.

This project uses the `Asyncio library <https://asyncio.readthedocs.io/en/latest/>`_ for
asynchronous code execution, hence we use Python 3.6+ (although some modules work with Python 3.5).

For the instructions below, replace ``/`` with ``\`` if you're on Windows and you're not using
`WSL 2 (Windows Subsystem for Linux) <https://docs.microsoft.com/en-us/windows/wsl/install-win10>`_.

Choose a setup method
^^^^^^^^^^^^^^^^^^^^^
Follow one of the 3 setup instructions below.

1. Create a new FACSvatar environment with YAML
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   cd FACSvatar/modules
   conda install -f environment.yml  # create a new env named 'facsvatar' with all required Python packages

2. Update existing conda environment with YAML
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   cd FACSvatar/modules
   conda env update --name myenv environment.yml  # update existing env with all required Python packages

3. Manually install packages
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Probably ``conda install ..`` can be replaced by ``pip install ..`` if you don't want to use Anaconda.

.. raw:: html

   <p>
   <details>
   <summary><a>Show instructions (click me)</a></summary>

.. code-block:: bash

   conda create --name facsvatar python=3.7  # new virtual env and force python 3.x
   conda activate facsvatar  # activate our environment

   conda install pyzmq  # make sure it's for py3.6+
   conda install pandas  # library for dataframes; used for .csv reading and JSON-to-Dataframe

   # Basic environment setup finished, but ipykernel setup recommended for control panel GUI
   conda install ipykernel  # allows the use of env kernels in jupyter notebook
   conda install ipywidgets  # GUI elements in jupyter notebook

Check ``FACSvatar/modules/environment.yml`` for additional packages FACSvatar uses.
E.g. building this documentation.


.. raw:: html

   </details>
   </p>


Optional setup steps
^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   # enable our conda environment as kernel in jupyter notebook
   python -m ipykernel install --user --name facsvatar --display-name "py3 facsvatar"



Start modules
-------------

Open 3 terminals

1. Start :ref:`module-overview_bridge` module

   1. ``conda activate facsvatar``
   2. ``cd *your_path*/FACSvatar/modules/process_bridge``
   3. ``python main.py``

#. Start :ref:`FACS to MB-Lab blend shapes<module-overview_mb-lab>` module

   1. ``conda activate facsvatar``
   2. ``cd *your_path*/FACSvatar/modules/process_facstoblend``
   3. ``python main.py``

#. Start :ref:`OpenFace offline<module-overview_openface-offline>` module (input)

   1. ``conda activate facsvatar``
   2. ``cd *your_path*/FACSvatar/modules/input_facsfromcsv``
   3. ``python main.py``

Congratulations, data should be flowing between the modules now!
Next is a to data-drive your avatar.


Real-time (needs Windows PC)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
You want to use your own facial expressions in real-time you say?
Skip starting the OpenFace offline FACSvatar module (step 3) and instead start the modified OpenFace GUI:
``OpenFaceOffline.exe`` --> menu: ``File`` --> ``Open Webcam``.

See for more detailed instructions: :doc:`../trackers/openface`


Data-drive your avatar
----------------------
To move an avatar's head, eyes and face, use one of these visualization engines:
:doc:`../visualization/blender` / :doc:`../visualization/unity3d` / :doc:`../visualization/facshuman`



Next
------------------------
Every Python module has a help function, giving more information on what arguments you can give.
Type: ``python module_x.py --help``
You can for example :doc:`run modules on different PCs<../advanced/multi_machines>` by changing the IP
where the module is subscribed to for data with: ``python module_x.py --sub_ip 192.168.xxx.xxx``

Use a :doc:`GUI in Jupyter Notebook<gui>` to manipulate the data flow in FACSvatar.

With FACSvatar, you can run modules on a different PC, you can create your own modules (in any programming language)
to extend FACSvatar's capabilities, and animate any number of (FACS-standard) avatar simultaneously, among others.
So check out those other pages of this documentation!