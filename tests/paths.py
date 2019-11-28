import os

current_dir = os.path.dirname(os.path.abspath(__file__))
libs_path = os.path.join(current_dir, "libs")
logstash_path = os.path.join(libs_path, "logstash")
wolf_path = os.path.join(libs_path, "wolf")
wolf_install_path = os.path.join(wolf_path, "install")

jre_file = os.path.join(logstash_path, 'jre-8u231-linux-x64.tar.gz')
jre_folder = os.path.join(logstash_path, 'jre1.8.0_231')
jre_url = 'https://javadl.oracle.com/webapps/download/AutoDL?BundleId=240718_5b13a193868b4bf28bcb45c792fce896'

logstash_file = os.path.join(logstash_path, 'logstash-6.3.0.tar.gz')
logstash_folder = os.path.join(logstash_path, 'logstash-6.3.0')
logstash_url = 'https://artifacts.elastic.co/downloads/logstash/logstash-6.3.0.tar.gz'
logstash_configs = os.path.join(current_dir, "logstash_configs")
logstash_collector_config = os.path.join(logstash_configs, "collector_config")
logstash_parser_config = os.path.join(logstash_configs, "parser_config")