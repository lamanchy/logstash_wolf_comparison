from tests.paths import wolf_path, wolf_install_path

import shutil
from tests.libs.helpers import win, wsl, get_platform, run


def image_name():
    return "lamanchy/wolf_" + get_platform()


def compile_wolf():
    if win():
        mount_path = "C:\\wolf"
    else:
        mount_path = "/wolf"

    source_path = wolf_path
    if wsl():
        # on wsl, docker is used on windows host with linux containers, nevertheless it requires
        # windows path to source
        source_path = source_path.replace("/mnt/c", "C:")

    remove_wolf_exe()

    res = run(f"docker run --rm -v {source_path}:{mount_path} {image_name()}")

    if res[0] != 0:
        print("couldn't compile wolf")
        exit(1)
    return res[1]


def remove_wolf_exe():
    try:
        shutil.rmtree(wolf_install_path)
    except FileNotFoundError:
        pass
