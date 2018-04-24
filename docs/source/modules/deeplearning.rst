===================
Deep learning setup
===================
We're going to add the deep learning library requirements `TensorFlow` & `Keras`
to our `facsvatar` anaconda environment.

Currently tested with Ubuntu 16.04 (not yet on Windows, but instructions provided)

If you didn't setup your Python environment yet, look here: :doc:`modules/env-setup`
Make sure your terminal has `facsvatar active`:

.. code-block:: bash

   source/conda activate facsvatar  # Ubuntu: `source`, Windows `conda`

------------
Dependencies
------------
- Python 3.4+ (tested 3.6)

   - TensorFlow 1.7.0

      - CUDA Toolkit v9.0  # GPU training
      - cuDNN v7.1.3  # GPU training

   - Keras (TensorFlow backend)


-------------------------------
Anaconda install all - untested
-------------------------------
Make sure your terminal has `facsvatar active`.

.. code-block:: bash

   source/conda activate facsvatar  # Ubuntu: `source`, Windows `conda`

   # Keras
   conda install -c anaconda keras-gpu

-------------------
TensorFlow - Manual
-------------------
Instructions are based on the Anaconda instructions found here: `<https://www.tensorflow.org/install/>`_ ,
so look there for the most recent instructions.

You can skip the GPU sections if you want to run it on a CPU ((much) slower).
Untested for now on Windows.


^^^
GPU
^^^

"""""""""""""""""
CUDA Toolkit v9.0
"""""""""""""""""
Official instructions (Ubuntu): `<https://docs.nvidia.com/cuda/cuda-installation-guide-linux/#axzz4VZnqTJ2A>`_
Official instructions (Windows): `<https://docs.nvidia.com/cuda/cuda-installation-guide-microsoft-windows/>`_

Short instructions:

1. Go to: `<https://developer.nvidia.com/cuda-90-download-archive>`_
#. Select .deb / .exe for your system
#. Download file (and Ubuntu: open terminal at download location)
#. Follow instructions

   - Ubuntu: Do step 1 for all patches before step 2 (`sudo dpkg -i cuda-xxx-update-xxx.deb`)
   - Ubuntu: If this fails, install 'GDebi Package Installer' from Ubuntu Software and open '.deb' with that.


""""""""""""
cuDNN v7.1.3
""""""""""""

1. Go to: https://developer.nvidia.com/cudnn --> DOWNLOAD cuDNN --> Join / Login
#. Download cuDNN v7.1.3 (April 17, 2018) (or newer?), for CUDA 9.0

   - Ubuntu: cuDNN v7.1.3 Runtime Library for Ubuntu16.04 (Deb)
   - Ubuntu: cuDNN v7.1.3 Developer Library for Ubuntu16.04 (Deb)
   - Windows: cuDNN v7.1.3 Library for Windows 7/10

#. Install by running in terminal:
   - Ubuntu: `sudo dpkg -i libcudnn7_7.1.3.16-1+cuda9.0_amd64.deb`
   - Ubuntu: `sudo dpkg -i libcudnn7-dev_7.1.3.16-1+cuda9.0_amd64.deb`
   - Windows:

#. Setup your environment variable to link to cuDNN

   - Ubuntu (in terminal): `echo 'export PATH=/usr/local/cuda-9.0/bin${PATH:+:${PATH}}' >> ~/.bashrc`

      - Manually: Add above line to .bashrc (in your home directory, ctrl+h to show hidden files)

   - Windows: add the directory where you installed the cuDNN DLL to your %PATH% environment variable.


""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
NVIDIA CUDA Profile Tools Interface (Ubuntu only) - untested
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
`<https://github.com/tensorflow/tensorflow/issues/16214>`_

1. Locate cuda-command-line-tools: `sudo apt-cache search cuda-command-line-tools-9-0`
#. Install: `sudo apt install cuda-command-line-tools-9-0`
#. Path to environment variable:
`echo 'export LD_LIBRARY_PATH=${LD_LIBRARY_PATH:+${LD_LIBRARY_PATH}:}/usr/local/cuda/extras/CUPTI/lib64' >> ~/.bashrc`



^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Install TensorFlow with Anaconda (GPU/CPU)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
If you didn't setup your Python environment yet, look here: :doc:`modules/env-setup`
Make sure your terminal has `facsvatar active`:

.. code-block:: bash

   source/conda activate facsvatar  # Ubuntu: `source`, Windows `conda`

   # GPU - Python 3.6
   pip install --ignore-installed --upgrade \
   https://storage.googleapis.com/tensorflow/linux/gpu/tensorflow_gpu-1.7.0-cp36-cp36m-linux_x86_64.whl

   # CPU - Python 3.6
   pip install --ignore-installed --upgrade \
   https://storage.googleapis.com/tensorflow/linux/cpu/tensorflow-1.7.0-cp36-cp36m-linux_x86_64.whl

   # test installation
   python
   >>> import tensorflow as tf  # no error
   >>> tf.__version__  # 1.7.0
   >>> ctrl+z / ctrl+Break  # leave Python; z: Ubuntu, Break: Windows




--------------
Keras - Manual
--------------
Official instructions: `<https://keras.io/>`_

Make sure your terminal has `facsvatar active`.

.. code-block:: bash

   source/conda activate facsvatar  # Ubuntu: `source`, Windows `conda`

   # Keras
   pip install keras

   # Only do the following commands if Keras doesn't use GPU
   pip uninstall keras  # Remove only Keras, but keep dependencies
   pip install --upgrade --no-deps keras  # and install it again without dependencies

^^^^^^^^^^^^^^
Test Keras GPU
^^^^^^^^^^^^^^
.. code-block:: bash

   cd jupyter_notebooks  # FACSvatar folder containing Jupyter notebooks
   jupyter notebook  # starts jupyter notebook and opens browser page

1. Click Keras_GPU_test.ipynb
#. Check right-top shows "py3 facsvatar" (our python env)
#. Kernel --> Restart & Run All
#. If you can find a `device_type: "GPU"`, Keras should be using GPU
#. Congratulations, Deep Learning setup complete!

