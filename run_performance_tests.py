#!/usr/bin/env python
from base.logstash import Logstash
from base.nc import Netcat
from base.wolf import Wolf
from helpers.benchmark_helpers import render_result
from helpers.helpers import extract_logs

# extract input logs
extract_logs()

# get tools
Logstash.get()
render_result("Wolf compilation",
              Wolf.get())

# size info
render_result("Disk usage",
              Wolf.size(),
              Logstash.size())

# compilation
render_result(f"Collector compilation",
              Wolf("collector").compile(),
              Logstash("collector").compile())

# empty
render_result("Empty configuration no input",
              Wolf("empty").no_input(),
              Logstash("empty").no_input(),
              Netcat("empty").no_input())

render_result("Empty configuration trickle",
              Wolf("empty").thousand_per_second(),
              Wolf("empty_with_json_conversion").thousand_per_second(),
              Logstash("empty").thousand_per_second(),
              Netcat("empty").thousand_per_second())

render_result("Empty configuration full load",
              Wolf("empty").full_load(),
              Wolf("empty_with_json_conversion").full_load(),
              Netcat("empty").full_load(),
              Logstash("empty").full_load())

render_result("Empty configuration buffer then read",
              Wolf("empty", enable_buffer=True).buffer_then_read(),
              Wolf("empty_with_json_conversion", enable_buffer=True).buffer_then_read(),
              Logstash("empty_with_buffer_enabled").buffer_then_read())

# collector
render_result("Collector trickle",
              Wolf("collector").thousand_per_second(),
              Logstash("collector").thousand_per_second())

render_result("Collector full load",
              Wolf("collector").full_load(),
              Logstash("collector").full_load())

# parser
render_result("Parser trickle",
              Wolf("parser").thousand_per_second(),
              Logstash("parser").thousand_per_second())

render_result("Parser full load",
              Wolf("parser").full_load(),
              Logstash("parser").full_load())
