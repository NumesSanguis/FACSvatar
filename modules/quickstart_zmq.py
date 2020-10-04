import sys
import threading
import subprocess
from multiprocessing import Pool

def module_thread(folder):
    print(f"Executing module: {folder}")
    subprocess.run([sys.executable, "main.py"], cwd=folder)  # , timeout=2
    # exec(open(f"{folder}/main.py").read())

    # with subprocess.Popen([sys.executable, "main.py"], cwd=folder) as p:  # *popenargs, **kwargs
    #     try:
    #         return p.wait()  # timeout=timeout
    #     except KeyboardInterrupt:
    #         # if not timeout:
    #         # timeout = 0.5
    #         # Wait again, now that the child has received SIGINT, too.
    #         p.wait(timeout=0.5)  # timeout
    #         raise
    #     except:
    #         p.kill()
    #         p.wait()  # timeout=1
    #         # p.send_signal(signal.SIGINT)
    #         # p.wait(timeout=1)
    #         raise

with Pool() as p:
    print(p.map(module_thread, ["module_sub", "module_pub"]))