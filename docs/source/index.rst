.. .# with overline, for parts
   * with overline, for chapters
   =, for sections
   -, for subsections
   ^, for subsubsections
   ", for paragraphs


Welcome to FACSvatar's documentation!
=====================================
FACSvatar is a combination of the terms **FACS** and **Avatar**.
FACS stands for Facial Action Coding System and is a way to describe a person's facial expression
in terms of muscle contraction and relaxation.
A single muscle group is called an Action Unit (AU) and either has a value between 0-5 or 0-1 (FACSvatar).
It is a system found by Paul Ekman and is often used in affective research.
Since FACS describes facial configurations, it is not only useful for affective analysis,
but also for animation.
More information about FACS can be found here: https://en.wikipedia.org/wiki/Facial_Action_Coding_System

FACSvatar is a modular framework that connects different software over ZeroMQ to enable both
the animation and analysis of AUs.
At present, a standard workflow is to use a modified `OpenFace <https://github.com/TadasBaltrusaitis/OpenFace/>`_.
(FACS input) that is transported and manipulated (smoothed) through FACSvatar and then forwarded to
either Unity3D (real-time) or Blender (high-quality) animation.

Links
------
* **GitHub** code and a longer explanation of FACSvatar's usefulness can be found at:
  https://github.com/NumesSanguis/FACSvatar
* Homepage: https://surafusoft.eu/facsvatar/
* Discussion of FACSvatar on reddit (for code problems, use GitHub issue tracker):
  https://www.reddit.com/r/FACSvatar/


.. Documentation contents
   =====================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   quickstart
   defaultsetup
   firstrun
   license

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
