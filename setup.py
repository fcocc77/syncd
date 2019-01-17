#!/usr/bin/python

import shutil
import os

path = os.path.dirname(os.path.abspath(__file__))

installFolder = "/opt/syncd"


def install():
    os.mkdir(installFolder)
    shutil.copy(path+"/bin/syncd.py", installFolder)
    shutil.copy(path+"/bin/syncd.service", installFolder)
    shutil.copy(path+"/bin/syncd.sh", installFolder)

    shutil.copy(path+"/bin/syncd.service", "/etc/systemd/system")
	
    os.system("sed -i -e 's/\r//g' " + installFolder + "/syncd.sh")

    os.system("systemctl daemon-reload")
    os.system("systemctl start syncd")
    os.system("systemctl enable syncd")
	
    print "Installing completed."

def uninstall():

    os.system("systemctl stop syncd")
    shutil.rmtree(installFolder)

    try:
        os.remove("/etc/systemd/system/syncd.service")
    except:
        None

    print "Uninstalled completed."


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
