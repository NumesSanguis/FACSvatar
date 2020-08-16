Programmable GUI (Jupyter Notebook)
===================================
The GUI that comes with FACSvatar allows you to manipulate AU values in real-time.
This can for example be used to exaggerated certain AUs.
Also, you can manually send AU data.
This allows for controlling (multiple) avatars in any program that's listing to FACSvatar.

This GUI is fully in Python, so you can hack away at it's functionality.
You can use `Jupyter Widgets <https://ipywidgets.readthedocs.io/en/stable/examples/Widget%20Basics.html>`_
to control create buttons, sliders, or even real-time graphs.
Anything that `Jupyter Notebook / Lab <https://jupyter.org/>`_ allows (which is a lot) is possible.

Usage
-----
1. Have a Python environment setup: :ref:`modules_firstrun`
#. Only Jup Notebook (not Lab): Especially make sure you executed (so Jupyter Notebook can see our Python environment):
   ``python -m ipykernel install --user --name facsvatar --display-name "py3 facsvatar"``
#. Open the GUI with Jupyter Notebook/Lab (in a terminal):

.. code-block:: bash

   cd *your_path*/FACSvatar/modules/gui  # in Windows, change '/' for '\'
   jupyter notebook  # this opens a tab in your webbrowser
   # Click on gui.ipynb
   # Interface: Kernel --> Change kernel --> py3 facsvatar
   # Interface: Kernel --> Restart & Run All
   # or execute individual cells with: Shift + Enter

.. warning::

   There is currently a bug, but that will be fixed (or has already been fixed, but I forgot to update this page).


A clean dashboard with Voila
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Turn a GUI notebook in a dashboard to hide all that ugly code: https://github.com/voila-dashboards/voila
