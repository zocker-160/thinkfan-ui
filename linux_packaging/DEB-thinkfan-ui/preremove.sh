#! /usr/bin/env bash

find /opt/thinkfan-ui -type f -iname \*.pyc -delete
find /opt/thinkfan-ui -type d -iname __pycache__ -delete
