# Logstash and Wolf comparison benchmarks

This repository contains Python script which gets (downloads/compiles)
both Wolf and Logstash, runs predefined benchmarks and visualizes 
results.

Wolf pipeline configs are located and cloned from another github
[repository](https://github.com/lamanchy/benchmark_wolf).

### Requirements:

- Ubuntu 18
- to compile Wolf
    - `sudo apt install git g++ python3 python3-pip wget -y`
    - `sudo python3 -m pip install --upgrade pip`
    - `sudo python3 -m pip install cmake`
- to run the benchmarks:
    - `sudo apt install git-lfs`

### Run the benchmarks:

`python3 run_performance_tests.py`

Expect the benchmarks take up to two hours.

Results are generated in the `benchmarks` subdirectory.