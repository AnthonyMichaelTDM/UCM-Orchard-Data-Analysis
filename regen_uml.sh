#!/bin/sh

touch ./src/__init__.py
pyreverse -o png ./src -AS -m y --colorized --ignore=['/other_scripts/']
rm ./src/__init__.py