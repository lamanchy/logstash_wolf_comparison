import os
from time import sleep

import psutil

from tests.libs.helpers import run
from tests.paths import jre_folder, logstash_folder, logstash_collector_config


def java_env():
    return f"JAVA_HOME={jre_folder}"


def base_command(config):
    return f"{logstash_folder}/bin/logstash --path.settings {config}"

def stop_when(cpu_percent_less_that=None, seconds_passed=None):
    def watcher(p):
        i = 0
        while True:
            if i == seconds_passed:
                print("Timeout passed")
                os.killpg(os.getpgid(p.pid), 2)
                break

            cpu = psutil.cpu_percent()
            if i != 0 and cpu < cpu_percent_less_that:
                print("Cpu low again")
                os.killpg(os.getpgid(p.pid), 2)
                break

            i += 1
            sleep(1)

    return watcher


def compile_logstash():
    return run(base_command(logstash_collector_config), java_env(), watcher=stop_when(cpu_percent_less_that=10))
