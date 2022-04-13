FROM ubuntu:20.04

RUN apt-get update && apt-get install -y make gcc build-essential gcc-multilib

RUN adduser -D fisop
USER fisop
ENV PATH="/home/fisop/.local/bin:${PATH}"

RUN pip install termcolor pyyaml

WORKDIR /shell

ENV TARGET_SHELL=/shell/lab-to-test

COPY . .
