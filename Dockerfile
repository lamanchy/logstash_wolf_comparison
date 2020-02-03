#escape=`

FROM ubuntu:16.04
RUN apt update -yqq
RUN apt-get install software-properties-common -yqq
RUN add-apt-repository ppa:jonathonf/python-3.6 -y
RUN apt update -yqq
RUN apt install git g++ wget -yqq
RUN apt install python3.6-dev python3-pip -yqq
RUN python3.6 -m pip install --upgrade pip gitpython psutil
RUN python3.6 -m pip install cmake
RUN apt install time -yqq
RUN apt install pv -yqq
RUN python3.6 -m pip install numpy
RUN python3.6 -m pip install matplotlib
RUN apt install netcat-openbsd -yqq
RUN curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | sudo bash
RUN apt install git-lfs -yqq

COPY . .

#RUN python3.6 run_performance_tests.py