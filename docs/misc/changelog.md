# Changelog
## New v0.3.4-alpha - 2019-01

* Dockerized core modules for easy setup and automatic IP configuration between modules
* Bridge and GUI are now in a separate folder, following other modules, to accommodate Docker
* Update ZeroMQ OpenFace to v2.1.0
* Unity3D to 2018.2.20f1

## New v0.3.3-alpha

* Decent improvements in documentation! (v0.3.3.1: own videos .csv + Blender FACS sliders)
* GUI in Jupyter Notebook working again with new code base
* Deep Learning module Python file renamed to `main.py` for consistency

## New/changes v0.3.2-alpha

* Simplified sending receiving messages (`facsvatarzeromq.py` now takes care of encoding / decoding and adding timestamps)
* Timestamp of message receive and send per module (`if Python >= 3.7: time.time_ns(), else time.time()`)
* Timestamp unified as string (ascii), formatted as 100 nanosecond precision integer, across modules; Default message parts: topic (string - ascii), timestamp (string - ascii), data (JSON formatted string - utf8)
* Performance improvement: Time taken for smoothing per message reduced (asynchronous): 11.90 +/- 6.91 milliseconds to 6.83 +/- 2.79 milliseconds (pandas --> direct numpy)
* In progress: print() --> logger
* `process_facstoblend` module accepts folder argument for different AU --> Blend Shape conversions
* OpenFace modification updated to v2.0.6
* Directly integrated with FACSHuman

## New v0.3.1-alpha

* OpenFace v2.0.3
* Eye movement based on eye gaze data
* Multi-user data support
* Multi-user animation in Unity3D
* Unity3D (2018.1.7f1) scene in cafe
* Scan folder and select (all) files with 1 command
* Switch targeted user of AU data for DNN (through GUI)
* Voice Activity Detection (VAD) to switch DNN user
* Mix participant AU / head pose data with DNN generated

### TODO vx.x.x

* Module management (Between modules: hearthbeat, controller, synchronized start, etc)
* Unreal Engine support
* GUI:
  * Manage Docker containers and show status
  * As web app with Voila