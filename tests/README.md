# Functional Wolf vs. Logstash tests

## Preparation

- `python run_performance_tests.py`
- which version of python is required
- packages in `requirements.txt`
- where to download binaries of Logstash
    - or do it manually?
- probably use docker to build wolf?
- include definition of test binaries in wolf
    - or how to simply add them?
    - adjust CMake to add custom target?
        - how to manage dependencies?

## Test evaluation

### Measured stats

- per test
    - startup time
    - startup cpu usage
    - processing speed (msg / sec)
    - processing cpu usage (cpu sec / msg)
    - max memory usage
    - max disk usage
- average of all tests
    - disk size
    - installation time

### Test cases

- do nothing for one minute
    - `nc` comparison?
- clean tcp receive + send
    - wolf with / without json conversion
    - `nc` comparison
- only tcp receive, to test buffering
- collector
    - multiple tcp in
    - one tcp out
    - filtering
    - buffer enabled
- parser
    - one tcp in one out
    - lot of regexes
    - buffer disabled

## Generate graphs

- for each test case
    - some to be customized?
        - unnecessary `disk usage` when testing without persistent buffer
- some kind of overview?
- disk size & installation time
- relative comparison / how many times is logstash better?