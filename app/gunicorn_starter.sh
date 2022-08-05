#!/bin/sh
gunicorn app:server -w 2 --preload --threads 2 -b 0.0.0.0:5050

