FROM python:3.10-alpine

RUN apk update && apk add --no-cache make gcc build-base

RUN adduser -D fisop
USER fisop
ENV PATH="/home/fisop/.local/bin:${PATH}"

RUN pip install ttp

WORKDIR /fork

COPY . .
