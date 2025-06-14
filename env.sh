#!/bin/bash

PIP_CMD=".venv/bin/pip --require-virtualenv"

# show usage
function usage {
    echo "Usage:"
    echo "- ./env.sh create         | Create a virtualenv (use first)"
    echo "- ./env.sh activate       | Activate a existing virtualenv"
    echo "- ./env.sh install        | Install requirements without version lock"
    echo "- ./env.sh install-locked | Install version-locked requirements"
    echo "- ./env.sh freeze         | Save version-locked requirements file for current environment"
}
# check args count
if [ $# -eq 0 ]; then
    usage
    exit 1
fi

# create venv
case "$1" in
"create")
    if [ -f .venv/bin/python3 ]; then
        echo "A virtualenv already exists, use './env.sh activate' to activate it, or use 'rm -rf .venv' to delete it"
        exit 1
    else
        python3 -m venv .venv --prompt sleepy
        exit 0
    fi
    ;;
esac

# check pip
if [ ! -f .venv/bin/pip ]; then
    if [ -f .venv/bin/python3 ]; then
        # python3 ok
        .venv/bin/python3 -m ensurepip
    else
        # no python3
        echo "No .venv/bin/python3 found!"
        echo "Use './env.sh create' to create a new one"
        exit 1
    fi
fi

# match args
case "$1" in
"activate")
    echo "source .venv/bin/activate"
    ;;
"install-locked")
    $PIP_CMD install -U -r requirements-lock.txt
    ;;
"install")
    $PIP_CMD install -U -r requirements.txt
    ;;
"freeze")
    datenow=$(date "+%Y-%m-%d %H:%M:%S")
    echo "# Generated on $datenow" >requirements-lock.txt
    echo "" >>requirements-lock.txt
    $PIP_CMD freeze >>requirements-lock.txt
    ;;
*)
    usage
    exit 1
    ;;

esac
