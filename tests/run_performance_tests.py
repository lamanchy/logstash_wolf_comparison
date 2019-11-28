#!/usr/bin/env python
from tests.libs.get_libs import download_libs
from tests.libs.wolf_helpers import compile_wolf
from tests.logstash_helpers import compile_logstash


def run_tests():
    logstash_build_size, wolf_build_size = download_libs()
    # logstash_build_size, wolf_build_size = 1234, 4321

    wolf_compile_time = compile_wolf()
    logstash_compile_time = compile_logstash()



    print(locals())

# JAVA_HOME=/home/lomic/caribou_target/java/app /home/lomic/caribou_target/parser/app/bin/logstash --path.settings /mnt/c/Users/lomic/PycharmProjects/mg/tests/logstash_configs/collector_config
