#!/bin/bash

export __dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
export __dir="$( dirname ${__dir} )"

if [ -d ${__dir}/__envi ]
then
    . ${__dir}/__envi/bin/activate
    export PYTHONPATH=${__dir}/src

    if [ -z "${_APP_PROFILE}" ];
    then
        ${__dir}/__envi/bin/python ${PYTHONPATH}/amberclient/examples/ninedof_example.py "$@"
    fi
fi
