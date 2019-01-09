#!/usr/bin/python
import os
import sys
import subprocess
import signal

path = os.path.dirname(os.path.abspath(__file__))

try:
    action = sys.argv[1]
except:
    action = ""
    print "Write: start or stop"


def start():

    cmd = "/opt/syncDirectory/syncd.py &> /opt/syncDirectory/log"
    started = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, shell=True, preexec_fn=os.setsid)

    f = open(path+"/syncPID", "w")
    f.write(str(started.pid))
    f.close

    print "syncDirectory: has started"


def stop():
    f = open(path+"/syncPID", "r")
    pid = int(f.readline())
    f.close

    try:
        os.killpg(pid, signal.SIGTERM)
    except:
        pass

    print "syncDirectory: has stoped"


if action == "start":
    start()

if action == "stop":
    stop()
