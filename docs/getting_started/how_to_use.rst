How to use FACSvatar (overview)
===============================

FACSvatar is a framework that let's different components communicate with each other,
so you can get facial expressions to your 3D avatars.
Follow the :doc:`Quickstart <README>` to get all components running for the first time.

The data format used for representing facial configurations is the Facial Action Coding System (FACS).
You can read more about that in :doc:`../avatars/facs_theory`.

Trackers
--------
To make facial animation possible, we have to start with getting the facial configurations from a person.
It's possible to either extract this from a video, or capture it in real-time using a camera.
At the moment, the only tracker made compatible with this framework is OpenFace v2,
as this was the best open source FACS tracker in 2016 (v1).
How to use this tracker can be found here: :doc:`../trackers/openface`.

Modules
-------
Now that we have a data representation of our facial configurations, the next step is to do some processing on it.
By choosing which modules to use, we can change the flow of data modifications.
These modules can be used either in pure Python (modules in other programming languages have not been created yet),
or by wrapping them up in Docker containers.

- To get started with running the modules 1-by-1 using Python, follow: :doc:`../modules/firstrun`.
- For your first setup with Docker, see the :doc:`Quickstart <README>`
- For more Docker instructions, check out: :doc:`../modules/docker`

You can read more about what all the modules do in: :doc:`../modules/overview`.

Visualization and Avatars
-------------------------
We have our facial data processed and in the format we want.
Next up is to see this facial data on an avatar.
We need two things for this: An engine that can render our 3D model and our 3D model itself.

   - Engines: :doc:`../visualization/blender`, :doc:`../visualization/unity3d` or :doc:`../visualization/facshuman`
   - Avatar creation: :doc:`../avatars/mblab` (Blender), :doc:`../visualization/facshuman` or
     :doc:`your own avatar <../avatars/custom_avatar>`


Have fun! & disclaimers
-----------------------
I hope that FACSvatar serves as a great starting point for your avatar (facial) animation needs.
For any issues or questions that this documentation does not answer, please create an
`issue at the GitHub repository <https://github.com/NumesSanguis/FACSvatar/issues>`_ .
Please **keep in mind** that this is an open source project without commercial support.
It is now mostly maintained by `me <https://github.com/NumesSanguis>`_ in my free time.
That means that feature request will likely have to be developed by user like you (or anyone you ask/hire).

Want to use it for commercial projects? Make sure to check out the :doc:`../misc/license` page.

You like the project and want to make it even better?
Please see :doc:`../misc/contribute` on how you can improve this project.
Thank you in advance!
