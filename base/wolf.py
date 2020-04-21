import os
import shutil
from os.path import exists, join

import git

from base.app import App
from helpers.helpers import run, get_folder_size


class Wolf(App):
    _name = "wolf"
    _status_messages = {
        "started": "Pipeline started",
        "ending": "stopping wolf"
    }

    def __init__(self, executable, enable_buffer=False):
        super().__init__(executable)
        self.buffer = enable_buffer

    def exec_path(self):
        return join(self.install_dir(), self.executable + "-linux")

    def queue_path(self):
        return join(self.exec_path(), "queue.tmp")

    @classmethod
    @App.cache
    def get(cls):
        cls.clone_and_update(cls.source_dir(), "https://github.com/lamanchy/benchmark_wolf.git")
        cls.clone_and_update(cls.lib_source_dir(), "https://github.com/lamanchy/wolf.git")
        return cls.install()

    @classmethod
    def lib_source_dir(cls):
        return os.path.join(cls.app_dir(), "wolf_source")

    @staticmethod
    def clone_and_update(dir, repo):
        if not exists(dir):
            git.Repo.clone_from(repo, dir)

        g = git.cmd.Git(dir)
        g.pull()

    @classmethod
    def build(cls):
        if not os.path.exists(cls.build_dir()):
            os.mkdir(cls.build_dir())
        res = cls.configure()

        res.update(cls.build_wolf())
        return res

    @classmethod
    @App.result("libraries")
    def configure(cls):
        return run(f'cmake'
                   f' -DCMAKE_BUILD_TYPE=Release'
                   f' -DCMAKE_INSTALL_PREFIX={cls.install_dir()}'
                   f' -DWOLF_PATH={cls.lib_source_dir()}'
                   f' -G "CodeBlocks - Unix Makefiles"'
                   f' {cls.source_dir()}', cwd=cls.build_dir())

    @classmethod
    @App.result
    def build_wolf(cls):
        return run(f'cmake --build . --target wolf -- -j 4', cwd=cls.build_dir())

    @classmethod
    @App.result
    @App.cache
    def size(cls):
        # 'docker inspect lamanchy/wolf_linux --format="{{.Size}}"'
        # 703487571
        # 'docker inspect lamanchy/wolf_win --format="{{.Size}}"'
        # 11087519335
        return {
            "Tool's size": [get_folder_size(cls.build_dir()) / 1024 / 1024, "MB"],
            "Linux docker image size": [703487571 / 1024 / 1024, "MB"],
            "Windows docker image size": [11087519335 / 1024 / 1024 / 1024, "GB"],
        }

    @App.result
    @App.cache
    def compile(self):
        shutil.rmtree(os.path.join(self.build_dir(), "CMakeFiles"))
        self.build()
        res = run(f'cmake --build {self.build_dir()} --target {self.executable} -- -j 4')
        self.install()
        return res

    @classmethod
    def install(cls):
        res = cls.build()
        run(f'cmake --build {cls.build_dir()} --target install -- -j 4')
        return res

    def base_command(self):
        extra = ""
        if self.buffer:
            extra = ' -p'

        return join(self.exec_path(), self.executable) + extra
