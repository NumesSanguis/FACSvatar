Module Overview
===============

FACSvatar is a modular framework that connects different software over ZeroMQ (data messaging library) to enable both
the animation and analysis of AUs.
At present, a standard workflow is to use a modified `OpenFace <https://github.com/TadasBaltrusaitis/OpenFace/>`_.
(FACS input) that is transported and manipulated (smoothed) through FACSvatar and then forwarded to
either Unity3D (real-time) or Blender (high-quality) animation.
