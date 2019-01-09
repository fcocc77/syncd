#!/usr/bin/python

import shutil
import os

path = os.path.dirname(os.path.abspath(__file__))

installFolder = "/opt/syncDirectory"


def install():
    os.mkdir(installFolder)
    shutil.copy(path+"/bin/syncd.py", "/opt/syncDirectory")
    shutil.copy(path+"/bin/syncd", "/opt/syncDirectory")
    shutil.copy(path+"/bin/syncd_run.py", "/opt/syncDirectory")

    shutil.copy(path+"/bin/syncd", "/etc/init.d")

    os.system("service syncd start")
    os.system("chkconfig syncd on")


def uninstall():

    os.system("service syncd stop")
    shutil.rmtree(installFolder)

    try:
        os.remove("/etc/init.d/syncd")
    except:
        None


is_admin = os.getuid() == 0

if not is_admin:
    print "-------------------------------------"
    print "sync_directory Install must be run as root"
    print "-------------------------------------"

else:

    if not os.path.isdir(installFolder):
        install()
    else:
        uninstall()
