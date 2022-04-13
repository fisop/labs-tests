FROM ubuntu:20.04

RUN apt-get update && apt-get install -y make gcc build-essential gcc-multilib python3.8 python3-pip time

RUN adduser --disabled-login --disabled-password fisop
USER fisop
ENV PATH="/home/fisop/.local/bin:${PATH}"

RUN pip install termcolor pyyaml

WORKDIR /shell

ENV TARGET_SHELL_DIR=/shell/lab-to-test

COPY . .
