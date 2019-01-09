#!/usr/bin/python

import shutil
import os

path = os.path.dirname(os.path.abspath(__file__))

installFolder = "/opt/syncDirectory"


def install():
    os.mkdir(installFolder)
    shutil.copy(path+"/bin/syncd.py", "/opt/syncDirectory")
    shutil.copy(path+"/bin/syncd.service", "/opt/syncDirectory")
    shutil.copy(path+"/bin/syncd_run.py", "/opt/syncDirectory")

    shutil.copy(path+"/bin/syncd.service", "/etc/systemd/system")

    os.system("systemctl start syncd")
    os.system("systemctl enable syncd")


def uninstall():

    os.system("systemctl stop syncd")
    shutil.rmtree(installFolder)

    try:
        os.remove("/etc/systemd/system/syncd.service")
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
