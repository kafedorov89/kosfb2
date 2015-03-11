# -*- coding: utf-8 -*-
import uuid
import os
import shutil
import zipfile
import rarfile
import platform
import fb2tools

def safeextract(*args, **kwargs):
    source_filename = args[0]
    dest_dir = args[1]
    settype = args[2]
    errorcount = 0
    archtype = -1

    with open('logfile.txt', "wb") as archlog:
        print "source_filename = ", source_filename

        if rarfile.is_rarfile(source_filename) or settype == 'rar':
            print "RAR archive was found"
            arch = rarfile.RarFile(source_filename, 'r')
            archtype = 0
        elif zipfile.is_zipfile(source_filename) or settype == 'zip':
            print "ZIP archive was found"
            arch = zipfile.ZipFile(source_filename, 'r')
            archtype = 1
        else:
            #Тип архива не распознан
            archtype = -1

        #Выводим список файлов содержащихся в архиве
        if archtype >= 0:

            infolist = arch.infolist()

            for infoitem in infolist:

                #filename -------------------------------------------------------------------------------
                filename = infoitem.filename
                filename = fb2tools.decodestr(filename)


                print "arch filename = ", filename

                #savename --------------------------------------------------------------------------------
                #Получаем имя файла из пути к файлу внутри архива
                savename = fb2tools.clearfilename(filename)
                print "arch savename = ", savename
                archlog.write("arch savename = {0}\n".format(savename))

                postfix = savename[-3:]
                print "arch postfix = ", postfix
                archlog.write("postfix = {0}\n".format(postfix))

                if postfix in ["fb2", "rar", "zip"]:
                    unpackedfile = arch.open(filename)
                    fb2tools.filesaver(dest_dir, savename, unpackedfile)
                    '''
                    try:
                        fb2tools.filesaver(dest_dir, savename, arch.read(filename))
                        archlog.write("Unpacked\n")
                    except:
                        errorcount = errorcount + 1
                        archlog.write("Error when unpack\n")
                        archlog.write("------------------------------------------------\n")
                    '''
            archlog.write("errorcount = {0}\n".format(errorcount))


class FileFinder(object):
    def __init__(self, *args, **kwargs):
        self.mainfolder = args[0]
        self.heapfolder = os.path.join(self.mainfolder, 'heap')
        self.fb2folder = os.path.join(self.mainfolder, 'fb2')
        self.archnumb = 0

    def find(self, *args, **kwargs):
        findpath = args[0]
        level = args[1]

        print "findpath = ", findpath
        print "find level = ", level

        #Получаем список файлов и подкаталогов в текущем каталоге
        filelist = os.listdir(findpath)

        allfiles = [ f for f in filelist if os.path.isfile(os.path.join(findpath, f)) ]
        print "allfiles = ", allfiles


        #Обработка всех найденных фалов fb2
        fb2files = [ f for f in allfiles if f.endswith(".fb2") ]
        print "fb2files = ", fb2files
        #Копируем все найденные fb2 файлы в каталог для дальнейшего парсинга
        for file in fb2files:
            shutil.copy(os.path.join(findpath, file), self.fb2folder)


        #Обработка всех найденных архивов
        archfiles = [ f for f in allfiles if f.endswith(".zip") or f.endswith(".rar")]
        print "archfiles = ", archfiles
        for file in archfiles:
            archfilepath = os.path.join(findpath, file)
            #Пробуем создать следующий по счету каталог с именем  "arch<number>"
            created = False
            while not created:
                archdir = os.path.join(self.mainfolder, 'arch/arch{0}'.format(self.archnumb))
                if(not (os.path.exists(archdir))):
                    os.mkdir(archdir, 0777)
                    created = True
                self.archnumb = self.archnumb + 1

            #Распаковываем архив в созданный каталог
            safeextract(archfilepath, archdir, file[-3:])
            #unzip(zipfilepath, zipdir)
            #Archive(archfilepath).extractall(archdir)

            #Запускаем рекурсивный поиск в распакованном архиве
            self.find(archdir, level + 1)


        #Обработка всех найденных каталогов
        dirs = [ f for f in filelist if not os.path.isfile(os.path.join(findpath, f)) ]
        print "dirs = ", dirs


    def zipfile(self):
        pass

    def rarfile(self):
        pass

    def fb2file(self):
        pass



if __name__ == "__main__":
    #print u"Ўaсб membuн!".encode("cp1251", "fb2_replacer")
    ff = FileFinder("/home/kos/Dropbox/workspace/rconline/pylearn/kosfb2/src/kosfb2/uploadedbook/3e1e47d0-c71f-11e4-b4ca-2c27d7b02944")
    ff.find("/home/kos/Dropbox/workspace/rconline/pylearn/kosfb2/src/kosfb2/uploadedbook/3e1e47d0-c71f-11e4-b4ca-2c27d7b02944/heap", 0)
