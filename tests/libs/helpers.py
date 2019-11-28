import os
from _signal import SIGINT
from pathlib import Path
from platform import uname
from subprocess import Popen, PIPE, TimeoutExpired
from threading import Thread
from time import sleep, time

import psutil


def get_platform():
    if os.name == "nt":
        return "win"
    else:
        return "linux"


def win():
    return get_platform() == "win"


def linux():
    return get_platform() == "linux"


def wsl():
    return linux() and "microsoft" in uname()[3].lower()


def get_folder_size(path):
    root_directory = Path(path)
    return sum(f.stat().st_size for f in root_directory.glob('**/*') if f.is_file())


def get_measurements(output, *names):
    result = {}
    for name in names:
        lines = output.split("\n")
        res = list(filter(lambda x: name in x, lines))
        assert len(res) == 1
        parts = res[0].split(": ")
        assert len(parts) == 2
        result[name] = parts[1]
    return result


def run(command, env="", watcher=None):
    if win():
        raise RuntimeError("Windows benchamrking is not supported yet")

    # p = Popen("/usr/bin/time -v sleep 6", shell=True, encoding="ascii", stderr=PIPE)
    start = time()
    p = Popen(env + " /usr/bin/time -v " + command, shell=True, encoding="ascii", stderr=PIPE)
    t = None
    if watcher is not None:
        t = Thread(target=watcher, args=(p,))
        t.start()

    try:
        _, stderr = p.communicate()
        end = time()
    except KeyboardInterrupt:
        end = time()
        stderr = p.stderr.read()

    if t is not None:
        t.join()

    measurements = get_measurements(stderr,
                                    "User time",
                                    "System time",
                                    "Maximum resident set size",
                                    )
    measurements.update({"Elapsed time": end - start})

    return p.returncode, measurements
