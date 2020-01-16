#!/usr/bin/env sh

gunicorn -k gevent -b 0.0.0.0:50 app:app