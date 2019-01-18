#!/usr/bin/env python
import subprocess
import time
import os
import shutil
import threading
import re

# rango de timepo de backup
timeStart = 20  # hrs
timeEnd = 8  # hrs
# -------------------------------------


class sync_directory():

    def __init__(self, disk=None, backup=None, trash=None):

        self.src = disk
        self.disks_bk = backup
        self.trash_disk = trash

        self.inTimeEnd = False
        threading.Thread(target=self.inTimeStart).start()

        # reactiva el disco montado si esta durmiendo
        self.sh("cd "+self.src+" && ls")
        # -----------------------------------

        # si esta montado el disco, comienza el backup
        if self.src in (self.sh("mount")):
            self.start_buckup()
        # ----------------------------------------------

        self.inTimeEnd = True

    def inTimeStart(self):
        while 1:
            self.inTime = inTime()
            if self.inTimeEnd:
                break
            time.sleep(1)

    def start_buckup(self):

        fecha = time.strftime("%H:%M:%S")+" " + time.strftime("%d/%m/%Y")
        self.log("\n\n----------------------")
        self.log("Start Backup at "+str(fecha)+".")

        # obtiene archivos que se borraran del backup
        backup_files, dirs_to_remove, files_to_remove = self.get_files_clear()
        # ----------------------------------------------------

        # lo archivos que se borraran, antes se copian en el disco de trash si es que esta habilitado
        if self.trash_disk:
            if not self.trash_copy(files_to_remove):
                self.free_trash()
                self.trash_copy(files_to_remove)
        # ---------------------------------------------------------------------------------------------

        # borra los archivo obtenido arriba
        self.files_clear(dirs_to_remove, files_to_remove)
        # ------------------------------------------------------

        # copia los archivos nuevos y modificados
        self.backup_len = 0
        if not self.files_copy():
            # si la copia para por falta de espacio, libera espacio de los archivos pesados y copia otra vez
            self.free_space(backup_files)
            self.files_copy()
        self.log(str(self.backup_len) + " Files backed up.")
        # ---------------------------------------------------------

        # Libera la ram en cache
        self.sh('sync && sysctl -w vm.drop_caches=3')
        # ---------------------------------------

        fecha = time.strftime("%H:%M:%S")+" " + time.strftime("%d/%m/%Y")
        self.log("Finish Backup at "+str(fecha)+".")
        self.log("----------------------")

    def trash_copy(self, files_to_remove):
        self.log("Copying to the trash...")
        src_name = os.path.basename(self.src)
        trash_path = self.trash_disk+"/"+src_name+"_trash"
        if not os.path.isdir(trash_path):
            os.mkdir(trash_path)

        for size, f in sorted(files_to_remove):
            if not self.inTime:
                break

            trash_file = f
            for disk in self.disks_bk:
                trash_file = trash_file.replace(disk, "")
            trash_file = trash_path+trash_file
            trash_dir = os.path.dirname(trash_file)

            try:
                os.makedirs(trash_dir)
            except:
                None

            try:
                shutil.copy2(f, trash_file)
            except IOError, error:
                if "No space left on device" in str(error):
                    return False

        return True

    def free_trash(self):
        files_trash = []
        for root, dirs, files in os.walk(self.trash_disk):
            for f in files:
                if not self.inTime:
                    break
                file_trash = root+"/"+f
                size = self.sort_size(file_trash)
                files_trash.append((size, file_trash))

        self.free_space(files_trash)

    def get_files_clear(self):

        self.log("Getting files to be deleted...")

        # se crea lita de las carpeta y archivos que se borraran
        backup_files = []
        dirs_to_remove = []
        files_to_remove = []
        self.isBackupFiles = False
        for disk_path in self.disks_bk:
            for root, dirs, files in os.walk(disk_path):
                if not self.inTime:
                    break

                for d in dirs:
                    dir_bk = root+"/"+d
                    dir_src = dir_bk.replace(disk_path, self.src)

                    if not os.path.isdir(dir_src):
                        dirs_to_remove.append(dir_bk)

                for f in files:
                    file_bk = root+"/"+f
                    file_src = file_bk.replace(disk_path, self.src)

                    size = self.sort_size(file_bk)
                    if not os.path.isfile(file_src):
                        files_to_remove.append((size, file_bk))
                    else:
                        self.isBackupFiles = True
                        backup_files.append((size, file_bk))
        # -------------------------------------------------------

        return [backup_files, dirs_to_remove, files_to_remove]

    def files_clear(self, dirs_to_remove, files_to_remove):
        # solo si el disco esta montado borra.
        if self.src in (self.sh("mount")):
            self.log("Deleting files...")

            if self.isBackupFiles:
                for d in dirs_to_remove:
                    try:
                        shutil.rmtree(d)
                    except:
                        None
                for size, f in files_to_remove:
                    try:
                        os.remove(f)
                    except:
                        None

    def files_copy(self):
        # solo si el disco esta montado borra.
        if self.src in (self.sh("mount")):
            self.log("Getting File to be Backing up...")
            # se crea lista de los archivos que se van a copiar
            files_to_copy = []
            for root, dirs, files in os.walk(self.src):
                if not self.inTime:
                    break

                for f in files:
                    file_src = root+"/"+f

                    isfile = False
                    for disk_path in self.disks_bk:
                        file_bk = file_src.replace(self.src, disk_path)

                        if os.path.isfile(file_bk):
                            isfile = True
                            break

                    if isfile:
                        # obtiene el numero de modificacion del archivo
                        try:
                            time_src = str(os.path.getmtime(file_src))
                            time_dst = str(os.path.getmtime(file_bk))
                        except:
                            time_src = 0
                            time_dst = 0
                        # -------------------------------------------------

                        # si se modifico el archivo lo copia
                        if not time_src == time_dst:
                            size = self.sort_size(file_src)
                            files_to_copy.append((size, file_src))
                        # ------------------------------------
                    else:
                        size = self.sort_size(file_src)
                        files_to_copy.append((size, file_src))
            # ---------------------------------------------------
            self.log("Backing up...")
            for size, file_src in sorted(files_to_copy):
                if not self.inTime:
                    break
                disk_space = True
                for disk_path in self.disks_bk:
                    file_bk = file_src.replace(self.src, disk_path)

                    dirname = os.path.dirname(file_bk)
                    try:
                        os.makedirs(dirname)
                    except:
                        None

                    try:
                        shutil.copy2(file_src, file_bk)
                        disk_space = True

                        break

                    except IOError, error:
                        if "No space left on device" in str(error):
                            disk_space = False

                if not disk_space:
                    return False

            self.backup_len += len(files_to_copy)

            return True
        else:
            return False

    def free_space(self, backup_files):

        freed_space = 0
        for size, f in sorted(backup_files, reverse=True):
            freed_space += os.path.getsize(f)
            os.remove(f)

            if freed_space > 50000000000:  # libera 50 Giga Bytes
                break

    def sort_size(self, file):
        try:
            return os.path.getsize(file)
        except:
            return 0

    def sh(self, command):
        proc = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        return proc.communicate()[0]

    def log(self, info):
        log_file = "/opt/syncd/"+self.src.split("/")[-1]+"_log"
        f = open(log_file, "a")
        f.write(info+"\n")
        f.close()


def inTime():
    # si no esta en el rango de tiempo inTime es 0
    hora = int(time.strftime("%H"))

    if timeStart > timeEnd:
        if hora >= timeStart or hora <= timeEnd:
            inTime = 1
        else:
            inTime = 0
    else:
        if timeStart <= hora <= timeEnd:
            inTime = 1
        else:
            inTime = 0
    # ----------------------------------------------

    return inTime


ready = True
while 1:
    if inTime():
        if ready:
            ready = False

            # respaldo de GFX ------------------------------
            sync_directory(disk="/mnt/gfx",
                           backup=["/media/gfx_backup"],
                           trash=False,  # "/disk_disk"
                           )
            # -----------------------------------------------------

            # respaldo de server1 ------------------------------
            sync_directory(disk="/mnt/server_01",
                           backup=["/media/server_01_backup"],
                           trash=False
                           )
            # -----------------------------------------------------

    else:
        ready = True

    time.sleep(3)
