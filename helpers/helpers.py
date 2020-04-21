import os
import tarfile
import zipfile
from os.path import join
from pathlib import Path
from platform import uname
from subprocess import PIPE
from threading import Thread
from time import sleep, time
from urllib.request import build_opener

import psutil

from helpers.paths import base_dir


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
        try:
            result[name] = float(parts[1])
        except Exception:
            result[name] = parts[1]
    return result


def run(command, env="", watcher=None, elapsed_starts_when=None, elapsed_ends_when=None, cwd=base_dir):
    if win():
        raise RuntimeError("Windows benchamrking is not supported yet")

    start, start_system, start_user, end_system, end_user = time(), 0, 0, 0, 0
    p = psutil.Popen(env + " /usr/bin/time -v " + command, shell=True, encoding="ascii", stderr=PIPE, stdout=PIPE,
                     cwd=cwd, close_fds=True, buffsize=0)
    t = None
    if watcher is not None and elapsed_starts_when is None:
        print("starting watcher1", flush=True)
        t = Thread(target=watcher, args=(p,))
        t.start()

    def get_cpu_times(p):
        try:
            for child in p.children():
                yield child.cpu_times()
                yield from get_cpu_times(child)
        except psutil.NoSuchProcess:
            pass

    stdout_lines = []
    # try:
    while True:
        line = p.stdout.readline()
        print(line, flush=True)
        if not line:
            break
        try:
            stdout_lines.append((time(), p.children()[0].children()[0].cpu_times(), line))
        except (IndexError, psutil.NoSuchProcess):
            pass
        if watcher is not None and t is None and elapsed_starts_when is not None and elapsed_starts_when in line:
            print("starting watcher", flush=True)
            t = Thread(target=watcher, args=(p,))
            t.start()

    _, stderr = p.communicate()

    end = time()
    if elapsed_starts_when is not None:
        for elapsed, cpu_times, line in stdout_lines:
            if elapsed_starts_when in line:
                start = elapsed
                start_user = cpu_times.user
                start_system = cpu_times.system
                break
        else:
            print(stdout_lines, stderr)
            raise RuntimeError("elapsed_starts_when not found")
    if elapsed_ends_when is not None:
        for elapsed, cpu_times, line in stdout_lines:
            if elapsed_ends_when in line:
                end = elapsed
                end_user = cpu_times.user
                end_system = cpu_times.system
                break
        else:
            print(stdout_lines, stderr)
            raise RuntimeError("elapsed_ends_when not found")

    if t is not None:
        t.join()
    try:
        measurements = get_measurements(stderr,
                                        "User time",
                                        "System time",
                                        "Maximum resident set size",
                                        )

        if elapsed_ends_when is None:
            end_user = measurements["User time"]
            end_system = measurements["System time"]
        res = {
            "Elapsed time": [(end - start), "s"],
            "User time": [end_user - start_user, "s"],
            "System time": [end_system - start_system, "s"],
            "Maximum memory usage": [measurements["Maximum resident set size"] / 1024, "MB"]
        }
        res["Cpu percent"] = [(res["User time"][0] + res["System time"][0]) / res["Elapsed time"][0] * 100, "%"]

    except AssertionError as e:
        print(e)
        print(stdout_lines)
        print(stderr)
        raise

    return res


def stop_when(cpu_percent_less_that=None, seconds_passed=None, before=None):
    def watcher(p):
        if before is not None:
            before()

        start = time()
        while True:
            cpu = psutil.cpu_percent(interval=.5)
            print(cpu, seconds_passed, time() - start, flush=True)
            if seconds_passed is None or time() - start >= seconds_passed:
                if cpu_percent_less_that is None or cpu < cpu_percent_less_that:
                    break

        try:
            print("killing", flush=True)
            os.kill(p.children()[0].children()[0].pid, 2)
            for i in range(300):
                if p.returncode is not None:
                    break
                sleep(0.1)
            else:
                print(time(), "killing process")
                os.kill(p.children()[0].children()[0].pid, 9)
        except (IndexError, psutil.NoSuchProcess):
            pass
        print("killed", flush=True)

    return watcher


def subtract_measurements(a, b):
    res = {
        "Elapsed time": [a["Elapsed time"][0] - b["Elapsed time"][0], a["Elapsed time"][1]],
        "User time": [a["User time"][0] - b["User time"][0], a["User time"][1]],
        "System time": [a["System time"][0] - b["System time"][0], a["System time"][1]],
        "Maximum memory usage": [b["Maximum memory usage"][0], a["Maximum memory usage"][1]],
    }
    res["Cpu percent"] = [(res["User time"][0] + res["System time"][0]) / res["Elapsed time"][0] * 100, "%"]
    return res


def add_message_count(res, count):
    res["Messages per second"] = [count / res["Elapsed time"][0], "msg/s"]
    res["CPU time per message"] = [(res["User time"][0] + res["System time"][0]) / count * 1000000, "µs/msg"]


def extract_logs():
    with zipfile.ZipFile(join(base_dir, "test_logs.zip"), 'r') as zip_ref:
        zip_ref.extractall(base_dir)


def download_tar(file, folder, url):
    if not os.path.exists(folder):
        if not os.path.exists(file):
            print(f"downloading {file}")
            f = build_opener().open(url)
            with open(file, 'wb+') as save:
                save.write(f.read())

        print(f"extracting {file}")
        with tarfile.open(file) as tar:
            tar.extractall()
    else:
        print(f"{file} already extracted")

    if os.path.exists(file):
        os.remove(file)
