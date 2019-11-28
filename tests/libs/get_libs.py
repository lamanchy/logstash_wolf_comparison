import os
import tarfile
from subprocess import Popen, PIPE
from urllib.request import build_opener
import git

from tests.paths import logstash_path, wolf_path, jre_file, jre_folder, jre_url, logstash_file, logstash_folder, \
    logstash_url
from tests.libs.wolf_helpers import image_name


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


def download_logstash():
    if not os.path.exists(logstash_path):
        os.mkdir(logstash_path)

    cwd = os.getcwd()
    os.chdir(logstash_path)

    download_tar(jre_file, jre_folder, jre_url)
    download_tar(logstash_file, logstash_folder, logstash_url)

    # restore original working dir
    os.chdir(cwd)

    # just to make it faster
    # return get_folder_size(logstash_path)
    return 484027772


def download_wolf():
    if not os.path.exists(wolf_path):
        git.Repo.clone_from("https://github.com/lamanchy/benchmark_wolf.git", wolf_path)

    g = git.cmd.Git(wolf_path)
    g.pull()

    rc = os.system(f"docker pull {image_name()}")
    if rc != 0:
        print("couldn't pull wolf image")
        exit(1)

    size = Popen("docker image inspect " + image_name() + " --format='{{.Size}}'",
                 shell=True, stdout=PIPE).communicate()[0]
    return int(size)


def download_libs():
    return download_logstash(), download_wolf()
