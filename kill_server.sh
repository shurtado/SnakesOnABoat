#!/bin/sh
# This will grab twistd's PID and kill that server

PID="`pwd`/twistd.pid"

kill $(cat $PID)
