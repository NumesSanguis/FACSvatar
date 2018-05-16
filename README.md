# FACSvatar v0.2.6-Alpha

Affective computing and avatar animation both share that a person's facial expression contains useful information. Up until now, these fields use different processes to obtain and use these data. FACSvatar combines both purposes in a single framework. Empower your Embodied Conversational Agents (ECAs)!

* **Affective computing**: Facial expressions can not only be analyzed, but also be used to generate animation, purely on data.
* **Animators**: Capture facial expressions with just a camera and use it to animate any compatible avatar.

This interoperability is possible, because FACSvatar uses the [Facial Action Coding System (FACS)](https://en.wikipedia.org/wiki/Facial_Action_Coding_System "https://en.wikipedia.org/wiki/Facial_Action_Coding_System") by Paul Ekman as an intermediate data representation. FACS describes facial expressions in terms of muscle groups, called Action Units (AUs). By giving these AUs a value between 0-1, we can describe the contractions / relaxation of facial muscles.

[![FACSvatar demo 2018-02](https://img.youtube.com/vi/fI05lzXBj3s/0.jpg)](https://www.youtube.com/watch?v=fI05lzXBj3s)

# Documentation & simple how to run

Open 3 terminals and open the project `unity_FACSvatar` in Unity 3D (2017.3)

0. Press 'play' in the Unity editor
0. Install the PyZMQ library (ZeroMQ for Python)
0. Terminal: `python N_proxy_M_bus.py`  (/modules/)
0. Terminal: `python pub_blend.py`  (/modules/02_facs-to-blendshapes/)
0. Terminal: `python pub_facs.py`  (/modules/01_facs-from-csv/)
0. See an avatar move its head and make facial expressions!

For more detailed instructions, see the [FACSvatar documentation](https://facsvatar.readthedocs.io/en/latest/).


# Modules & cross-platform

This framework is tested on both Windows and Linux (Ubuntu).

Everything in this framework is modular! Models look low quality? Use different models which can be animated by FACS (or convert FACS to matching Blend Shapes). You made a better FACS extractor (with e.g. a depth camera)? Use that instead! Want more intelligence, add your own modules for extended functionality!

The modularity is made possible by using [ZeroMQ - brokerless messaging library](http://zeromq.org/). Data is transfered between sockets in a Publisher-Subscriber pattern. Therefore, modules don't need to know where the data comes from, or who uses their data. This makes it easy to add/remove modules, no matter the programming language.


# Functionality

* Stream your facial expressions in real-time into Unity 3D
* Set Shape Keys in Blender with your facial expressions for high-quality rendering and/or export your facial animation for classic trigger-based animation in e.g. games.
[![Manuel Bastioni FACS expressions](https://img.youtube.com/vi/ImB3it_26bc/0.jpg)](https://www.youtube.com/watch?v=ImB3it_26bc)
* [near-future] Deep Neural Network generation of facial expressions for Human-Agent Interaction.
* [your modules] Please add your own modules, release your code, and let's expand the functionality of this framework :) More details in the documentation.


## Detailed workings (English & 日本語)
[![FACSvatar details in English and 日本語](https://surafusoft.eu/facsvatar/files/2018/02/FACSvatar_poster_25_A4_3-liner-724x1024.png)](https://surafusoft.eu/facsvatar/files/2018/02/FACSvatar_poster_25_A4_3-liner.png)

More can be found on the project's website: [FACSvatar homepage](https://surafusoft.eu/facsvatar/ "https://surafusoft.eu/facsvatar/").

Note: The poster still shows Crossbar.io, but this has been replaced with ZeroMQ.


## Software
* [Blender](https://www.blender.org/) + [Manuel Bastioni Lab addon](http://www.manuelbastioni.com/)  (create human models)
  * [MBlab wikia](http://manuelbastionilab.wikia.com/wiki/Manuel_Bastioni_Lab_Wiki) 
* [OpenFace](https://github.com/TadasBaltrusaitis/OpenFace)  (extract FACS data)
* [Unity 3D](https://unity3d.com/) 2017.3 (animate in game engine)
* [ZeroMQ (PyZMQ)](http://zeromq.org/) (distributed messaging library)
* [Docker (future)](https://www.docker.com/)  (|future| containerization for easy distribution)
