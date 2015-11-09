#!/usr/bin/env bash

cd /app
export PATH=$PATH:/app
export PYTHONPATH=$PYTHONPATH:/app

coverage run -a --source="." manage.py test ajaxview
coverage report
