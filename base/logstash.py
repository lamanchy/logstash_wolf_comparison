import os
from os.path import join

from base.app import App
from helpers.helpers import get_folder_size, stop_when, run, download_tar


class Logstash(App):
    _name = "logstash"
    jre_url = 'https://javadl.oracle.com/webapps/download/AutoDL?BundleId=240718_5b13a193868b4bf28bcb45c792fce896'
    logstash_url = 'https://artifacts.elastic.co/downloads/logstash/logstash-6.3.0.tar.gz'

    _status_messages = {
        "starting": "Starting Logstash",
        "started": "Successfully started Logstash API endpoint",
        "ending": "SIGINT received"
    }

    def queue_path(self):
        return join(self.source_dir(), self.executable, "queue")

    @classmethod
    def jre_file(cls):
        return join(cls.build_dir(), 'jre-8u231-linux-x64.tar.gz')

    @classmethod
    def jre_dir(cls):
        return join(cls.build_dir(), 'jre1.8.0_231')

    @classmethod
    def bin_file(cls):
        return join(cls.build_dir(), 'logstash-6.3.0.tar.gz')

    @classmethod
    def bin_dir(cls):
        return join(cls.build_dir(), "logstash-6.3.0")

    @classmethod
    @App.result
    @App.cache
    def size(cls):
        # 'docker inspect docker.elastic.co/logstash/logstash:6.3.0 --format="{{.Size}}"'
        # 660022051
        return {
            "Size without dependencies": [get_folder_size(cls.bin_dir()) / 1024 / 1024, "MB"],
            "Linux docker image size": [660022051 / 1024 / 1024, "MB"]
        }

    @classmethod
    @App.cache
    def get(cls):
        if not os.path.exists(cls.build_dir()):
            os.mkdir(cls.build_dir())

        cwd = os.getcwd()
        os.chdir(cls.build_dir())

        download_tar(cls.jre_file(), cls.jre_dir(), cls.jre_url)
        download_tar(cls.bin_file(), cls.bin_dir(), cls.logstash_url)

        # restore original working dir
        os.chdir(cwd)

        run("bin/logstash-plugin install logstash-filter-aggregate", cls.get_env(), cwd=cls.bin_dir())
        run("bin/logstash-plugin install logstash-filter-prune", cls.get_env(), cwd=cls.bin_dir())

    def base_command(self):
        config = self.get_config_path()
        return f"{self.bin_dir()}/bin/logstash --path.settings {config}"

    @App.result
    @App.cache
    def compile(self):
        return self.run_app(watcher=stop_when(cpu_percent_less_that=10), end_when="starting")

    def get_config_path(self):
        return join(self.source_dir(), self.executable)

    @classmethod
    def get_env(cls):
        return f"JAVA_HOME={cls.jre_dir()}"
