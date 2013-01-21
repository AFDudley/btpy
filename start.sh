#!/bin/bash
source virtualenvwrapper.sh;
workon btpy;
runzeo -C zeoWorld.conf &
ipython equanimity/rproxy_server.py 127.0.0.1 &
ipython equanimity/auth_server.py &
ipython equanimity/keep_alive.py &
