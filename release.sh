#!/bin/bash

cd "$(dirname "$0")"

rm -rf *.pyc *.pyo objproxies.egg-info __pycache__ build dist
python setup.py sdist upload
