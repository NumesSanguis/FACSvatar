# Install Python packages directly in Blender environment
## Activate pip in Blender
https://blender.stackexchange.com/questions/139718/install-pip-and-packages-from-within-blender-os-independently/139720#139720

Run Blender with administration rights and execute the following code in the Blender console:
```
import subprocess
import sys
from pathlib import Path  # Object-oriented filesystem paths since Python 3.4

# OS independent (Windows: bin\python.exe; Linux: bin/python3.7m)
py_path = Path(sys.prefix) / "bin"
py_exec = str(next(py_path.glob("python*")))  # first file that starts with "python" in "bin" dir
# TODO check permission rights
subprocess.call([py_exec, "-m", "ensurepip"])
# Output should be: 0
# upgrade pip to latest version
subprocess.call([py_exec, "-m", "pip", "install", "--upgrade", "pip"])
# Output should be: 0
```
This should return 2x `0`. If it returns `1`, it's likely that you're not running Blender with Admin rights.

## Next steps
```
# autocompletion support for any editor; pip install fake-bpy-module-2.80
# https://github.com/nutti/fake-bpy-module
subprocess.call([py_exec, "-m", "pip", "install", "fake-bpy-module-2.80"])

# install any package
subprocess.call([py_exec, "-m", "pip", "install", "your package"])
# for example pyzmq
subprocess.call([py_exec, "-m", "pip", "install", "pyzmq"])
```

## Untested: Install packages through PyCharm / terminal (e.g. `*blender path*\2.80\python\bin\python.exe`)
Change: `py_exec` --> `sys.executable` in above instructions



# PyCharm
## Set Python interpreter to Blender's Python
https://www.jetbrains.com/help/pycharm/configuring-python-interpreter.html

1. Open the Add Python Interpreter dialog by either way:
  - When you're in the Editor, the most convenient way is to use the Python Interpreter widget in the Status bar. Click the widget and select Add Interpreter ...
  - If you are in the Settings/Preferences dialog (Ctrl+Alt+S), select Project <project name> | Project Interpreter. Click the The Configure project interpreter icon (cogwheel) and select Add.
  
2. System Interpreter --> `...` --> Navigate to (this is a Windows path example): `*blender-location*\2.80\python\bin\python.exe`
  - Optionnaly select: `Make available to all projects`
3. Press OK



# Blender
## Set addon path
(So it can find our add-ons under development)

Edit --> Preferences --> File Paths --> Scripts: ../FACSvatar/blender/

```
# In Console: show addon paths
import addon_utils
print(addon_utils.paths())
```

## Command to reload your addon (Blender 2.8):
Reload all add-ons: `bpy.ops.script.reload()`
You're not suppose to use: `bpy.ops.preferences.addon_enable(module='your_addon')`

### Set reload keyboard shortcut
Reload all add-ons: https://devtalk.blender.org/t/reload-button-in-2-8/1708

### More details for reloading
https://developer.blender.org/T66924
