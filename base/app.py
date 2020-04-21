import os
import shutil
from math import ceil
from os.path import dirname, abspath, join
from subprocess import PIPE
from threading import Thread
from time import sleep, localtime, strftime
import time

import psutil
from psutil import Popen

from helpers.cache import cache as helper_cache
from helpers.helpers import run, stop_when, subtract_measurements, add_message_count, get_folder_size
from helpers.paths import base_dir


def app_cache(fn):
    def decorator(self, *args, **kwargs):
        executable = getattr(self, "executable", "")
        name = f"{self.name()}_{executable}_{fn.__name__}"
        if len(executable) > 0:
            executable += " "
        print(f"{strftime('%Y/%m/%d %H:%M:%S', localtime())} Runnning {self.name()} {executable}{fn.__name__}")
        return helper_cache(name)(fn)(self, *args, **kwargs)

    return decorator


def app_result(fn_or_name):
    name = None
    if type(fn_or_name) == str:
        name = fn_or_name

    def wrapper(fn):
        def decorator(self, *args, **kwargs):
            res = fn(self, *args, **kwargs)
            key = self.name()
            if name is not None:
                key = name
            key = key[0].upper() + key[1:]
            executable = getattr(self, "executable", "")
            if "with_json_conversion" in executable:
                key += " with json\nconversion"
            return {key: res}

        return decorator

    if type(fn_or_name) == str:
        return wrapper
    return wrapper(fn_or_name)


class App:
    @staticmethod
    def cache(fn):
        return app_cache(fn)

    @staticmethod
    def result(fn_or_name):
        return app_result(fn_or_name)

    _name = None
    _status_messages = {
        "starting": None,
        "started": None,
        "ending": None
    }

    base_time = 60

    def __init__(self, executable):
        self.executable = executable

    @staticmethod
    def base_dir():
        return dirname(dirname(abspath(__file__)))

    @classmethod
    def name(cls):
        if cls._name is None:
            raise ValueError("Name not specified in subclass")
        return cls._name

    def queue_path(self):
        return NotImplemented

    @classmethod
    def app_dir(cls):
        return join(cls.base_dir(), cls.name())

    @classmethod
    def build_dir(cls):
        return join(cls.app_dir(), "build")

    @classmethod
    def source_dir(cls):
        return join(cls.app_dir(), "source")

    @classmethod
    def install_dir(cls):
        return join(cls.app_dir(), "install")

    @classmethod
    def get(cls):
        return NotImplemented

    @classmethod
    def size(cls):
        return NotImplemented

    def compile(self):
        return NotImplemented

    def base_command(self):
        return NotImplemented

    @classmethod
    def get_env(cls):
        return ""

    def get_inputs(self):
        if "collector" in self.executable:
            return [("nlog.txt", 9556), ("log4j.txt", 9555)]
        if "empty" in self.executable:
            return [("unified_logs.txt", 9556)]
        if "parser" in self.executable:
            return [("unified_logs.txt", 9069)]
        raise ValueError

    def run_app(self, watcher=None, start_when="start", end_when="end"):
        return run(self.base_command(), self.get_env(),
                   watcher=watcher,
                   elapsed_starts_when=self._status_messages.get(start_when, None),
                   elapsed_ends_when=self._status_messages.get(end_when, None))

    @app_result
    @app_cache
    def no_input(self):
        res = self.run_app(watcher=stop_when(seconds_passed=5),
                           start_when="started",
                           end_when="ending")
        # for more precision, run with longer time and subtract results
        res2 = self.run_app(watcher=stop_when(seconds_passed=self.base_time * 10 + 5),
                            start_when="started",
                            end_when="ending")
        res = subtract_measurements(res2, res)
        return res

    def run_and_listen(self, logs_sent, listen_after=False):
        receiver = []

        def make_receiver():
            receiver.append(Popen(f'nc -l -p 9070 | wc -l', shell=True, stderr=PIPE, stdout=PIPE))

        if not listen_after:
            make_receiver()

        def before():
            if logs_sent[0] > 0:
                qs = []
                inputs = self.get_inputs()
                for file_name, port in inputs:
                    for _ in range(logs_sent[0]):
                        file = join(base_dir, "test_logs", file_name)
                        read = f"cat {file}"
                        if logs_sent[2] > 0:
                            read = f"head -n {int(ceil(logs_sent[2] / logs_sent[0] / len(inputs)))} {file}" \
                                   f" & sleep 1"
                        cmd = f'timeout {logs_sent[1]} bash -c "' \
                              f'while true; do {read}; done' \
                              f' | nc localhost {port}' \
                              f'"'
                        q = psutil.Popen(
                            cmd,
                            shell=True)
                        qs.append(q)
                [q.wait() for q in qs]
            if listen_after:
                make_receiver()
                # sleep for a while so it can connect
                sleep(2)

        res = self.run_app(watcher=stop_when(cpu_percent_less_that=10, before=before),
                           start_when="started", end_when="ending")

        # if receiver[0].returncode is None:
        #     # send ctrl-c to nc
        #     receiver[0].children()[0].send_signal(2)

        received_messages = int(receiver[0].communicate()[0])
        add_message_count(res, received_messages)
        return res

    def run_then_listen(self, logs_sent):
        run = True
        queue_size = [0]

        def monitor_queue_size():
            path = self.queue_path()
            while run:
                try:
                    if os.path.isfile(path):
                        size = os.path.getsize(path)
                    else:
                        size = get_folder_size(path)
                    queue_size[0] = max(queue_size[0], size)
                except FileNotFoundError:
                    pass
                sleep(1)
            try:
                shutil.rmtree(path)
            except FileNotFoundError:
                pass

        t = Thread(target=monitor_queue_size)
        t.start()

        res = self.run_and_listen(logs_sent, True)

        run = False
        t.join()

        res["Queue size"] = [queue_size[0] / 1024 / 1024, "MB"]
        messages = res["Messages per second"][0] * res["Elapsed time"][0]
        res["Queue size per message"] = (queue_size[0] / messages, "B/msg")

        return res

    @app_result
    @app_cache
    def thousand_per_second(self):
        return self.run_and_listen((1, 3 * self.base_time, 1000))

    @app_result
    @app_cache
    def full_load(self):
        return self.run_and_listen((8, 3 * self.base_time, 0))

    @app_result
    @app_cache
    def buffer_then_read(self):
        return self.run_then_listen((8, 3 * self.base_time, 0))

    @app_result
    @app_cache
    def trickle_then_read(self):
        return self.run_then_listen((1, 3 * self.base_time, 1000))
