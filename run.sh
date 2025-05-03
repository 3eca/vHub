#!/bin/sh

flask db upgrade
python3 main.py