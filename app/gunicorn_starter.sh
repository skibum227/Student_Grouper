#!/bin/sh
gunicorn app:server -w 2 --threads 2 -b 0.0.0.0:5050

