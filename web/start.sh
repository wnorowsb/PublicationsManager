#!/usr/bin/env sh

gunicorn -k gevent -b 0.0.0.0:4000 app:app