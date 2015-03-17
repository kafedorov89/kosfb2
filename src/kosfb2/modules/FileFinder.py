# -*- coding: utf-8 -*-
import uuid
import os
import shutil
import zipfile
import rarfile
import platform
import fb2tools

class FileFinder(object):
    def __init__(self, *args, **kwargs):
        self.mainfolder = args[0]
        self.heapfolder = os.path.join(self.mainfolder, 'heap')
        self.fb2folder = os.path.join(self.mainfolder, 'fb2')
        self.archnumb = 0

    def find(self, *args, **kwargs):
        #try:
        findpath = args[0]
        level = args[1]

        #print "findpath = ", findpath
        #print "find level = ", level

        #Получаем список файлов и подкаталогов в текущем каталоге
        filelist = os.listdir(findpath)

        allfiles = [ f for f in filelist if os.path.isfile(os.path.join(findpath, f)) ]
        print "allfiles = ", allfiles


        #Обработка всех найденных фалов fb2
        fb2files = [ f for f in allfiles if f.endswith(".fb2") ]
        print "fb2files = ", fb2files
        #Копируем все найденные fb2 файлы в каталог для дальнейшего парсинга
        for filename in fb2files:
            with open(os.path.join(findpath, filename) , 'r') as file:
                fb2tools.filesaver(self.fb2folder, file, ".fb2")
            #shutil.copy(os.path.join(findpath, file), self.fb2folder)


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
            fb2tools.safeextract(archfilepath, archdir, file[-3:])
            #unzip(zipfilepath, zipdir)
            #Archive(archfilepath).extractall(archdir)

            #Запускаем рекурсивный поиск в каталоге, с распакованными файлами из архива
            try:
                self.find(archdir, level + 1)
            except:
                print "Error. find function on {0} level, arch directory: {1}".format(level + 1, archdir)

            #Обработка всех найденных каталогов
            #Пока не реализована, потому как из архива распаковываются только файлы, и грузить из формы можно только файлы
            #dirs = [ f for f in filelist if not os.path.isfile(os.path.join(findpath, f)) ]
            #print "dirs = ", dirs
        return True
        #except:
        #    return False
        #else:
        #    return True

# __main__ Только для отладки
'''
if __name__ == "__main__":
    #print u"Ўaсб membuн!".encode("cp1251", "fb2_replacer")
    uidstr = 'd45f8400-c7cb-11e4-afd7-2c27d7b02944'
    ff = FileFinder("/home/kos/Dropbox/workspace/rconline/pylearn/kosfb2/src/kosfb2/uploadedbook/{0}".format(uidstr))
    ff.find("/home/kos/Dropbox/workspace/rconline/pylearn/kosfb2/src/kosfb2/uploadedbook/{0}/heap".format(uidstr), 0)
'''
