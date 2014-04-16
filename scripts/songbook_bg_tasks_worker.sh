#!/bin/bash
SCRIPT_DIR="$( cd "$( dirname "$0" )" && pwd )"
DAEMON=$SCRIPT_DIR/../manage.py
ARGS=process_tasks
until $DAEMON $ARGS; do
    echo "Server '$DAEMON' crashed with exit code $?.  Respawning.." >&2
    sleep 1
done
