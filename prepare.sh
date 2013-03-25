#!/bin/sh

export PROTO_PATH=./amber-python-common

for pp in hokuyo ninedof roboclaw; do
    protoc -I ${PROTO_PATH} -I ./amber-python-${pp} --python_out=./amber-python-${pp} ./amber-python-${pp}/${pp}.proto
done
