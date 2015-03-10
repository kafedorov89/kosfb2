# -*- coding: utf-8 -*-
import uuid
import os
import shutil
import zipfile
import rarfile
import platform
import codecs

#from pyunpack import Archive

def safeextract(*args, **kwargs):
    source_filename = args[0]
    dest_dir = args[1]
    errorcount = 0
    archtype = -1

    replace_costom = lambda exc: (u'_', exc.start + 1)
    codecs.register_error('replace_costom', replace_costom)

    with open('logfile.txt', "wb") as archlog:

        if rarfile.is_rarfile(source_filename):
            print "RAR archive was found"
            arch = rarfile.RarFile(source_filename, 'r')
            archtype = 0
        elif zipfile.is_zipfile(source_filename):
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
                filename = infoitem.filename
                print "filename = ", filename
                print "decode filename = ", filename.encode("utf-8", "replace_costom")
                archlog.write("decode filename = {0}\n".format(infoitem.filename.encode("utf-8", "replace_costom")))

                '''
                if archtype == 0:
                    ostype = infoitem.host_os #(RAR_OS_MSDOS = 0, RAR_OS_OS2   = 1, RAR_OS_WIN32 = 2, RAR_OS_UNIX  = 3, RAR_OS_MACOS = 4, RAR_OS_BEOS  = 5)
                elif archtype == 1:
                    ostype = infoitem.create_system #(0 = Windows, 3 = Unix)
                else:
                    ostype = -1
                
                #Windows or Linux
                if (archtype == 0 and ostype in [0, 2]) or (archtype == 1 and ostype == 0):
                    savename = filename.split('\\')[-1]
                else:
                    savename = filename.split('/')[-1]
                    if ('\\' in savename):
                        savename = savename.split('\\')[-1]
                '''

                savename = infoitem.filename.split('\\')[-1]
                print "savename = ", savename.encode("utf-8", "replace_costom")
                archlog.write("savename = {0}\n".format(savename.encode("utf-8", "replace_costom")))

                postfix = savename[-3:]
                print "postfix = ", postfix
                archlog.write("postfix = {0}\n".format(postfix))

                if postfix in ["fb2", "rar", "zip"]:
                    savepath = os.path.join(dest_dir, savename)
                    print "savepath = ", savepath

                    try:
                        with open(savepath, "wb") as f:
                            unpackfile = arch.read(filename)
                            #print "unpackfile = ", unpackfile
                            f.write(unpackfile)
                            archlog.write("Unpacked")
                    except:
                        errorcount = errorcount + 1
                        archlog.write("Error when unpack")
                        archlog.write("------------------------------------------------\n")
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

        #or f.endswith(".rar")

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
            safeextract(archfilepath, archdir)
            #unzip(zipfilepath, zipdir)
            #Archive(archfilepath).extractall(archdir)

            #Запускаем рекурсивный поиск в распакованном архиве
            self.find(archdir, level + 1)



        '''
        #Обработка всех найденных файлов zip
        zipfiles = [ f for f in allfiles if f.endswith(".zip") ]
        print "zipfiles = ", zipfiles
        for file in zipfiles:
            zipfilepath = os.path.join(findpath, file)
            if zipfile.is_zipfile(zipfilepath):
                #Пробуем создать следующий по счету каталог с именем  "zip_<number>"
                created = False
                while not created:
                    zipdir = os.path.join(self.mainfolder, 'zip{0}'.format(self.archnumb))
                    if(not (os.path.exists(zipdir))):
                        os.mkdir(zipdir, 0777)
                        created = True
                    self.archnumb = self.archnumb + 1

                #Распаковываем архив в созданный каталог
                safeextract(zipfilepath, zipdir)
                #unzip(zipfilepath, zipdir)

                #Запускаем рекурсивный поиск в распакованном архиве
                self.find(zipdir, level + 1)
            else:
                print "Error. ZIP file is not valid and was skiped. Going to next file..."

        '''
        '''

        #Обработка всех найденных файлов rar
        rarfiles = [ f for f in allfiles if f.endswith(".rar") ]
        print "rarfiles = ", rarfiles
        for file in rarfiles:
            rarfilepath = os.path.join(findpath, file)
            if zipfile.is_zipfile(rarfilepath):
                #Пробуем создать следующий по счету каталог с именем  "zip_<number>"
                created = False
                while not created:
                    rardir = os.path.join(self.mainfolder, 'zip{0}'.format(self.archnumb))
                    if(not (os.path.exists(zipdir))):
                        os.mkdir(rardir, 0777)
                        created = True
                    self.rarnumb = self.rarnumb + 1

                #Распаковываем архив в созданный каталог
                #unrar(zipfilepath, zipdir)
                safeextract(rarfilepath, rardir)

                #Запускаем рекурсивный поиск в распакованном архиве
                self.find(zipdir, level + 1)
            else:
                print "Error. ZIP file is not valid and was skiped. Going to next file..."
        '''


        #Обработка всех найденных каталогов
        dirs = [ f for f in filelist if not os.path.isfile(os.path.join(findpath, f)) ]
        print "dirs = ", dirs

        '''
        #Распаковываем архивы в отдельные каталоги
        
        tmpname = str(uuid.uuid1())

        #Создаем временную директорию для разархивированны файлов
        self.rar_tmpfoldername = os.path.join(self.foldername, "{0}{1}".format("rar_", tmpname))
        self.zip_tmpfoldername = os.path.join(self.foldername, "{0}{1}".format("zip_", tmpname))

        print "self.heap_tmpfoldername = ", self.heap_tmpfoldername
        print "self.fb2_tmpfoldername = ", self.fb2_tmpfoldername

        #Если временный каталог для текущего разбора еще не был создан, создаем его
        if(not (os.path.exists(self.heap_tmpfoldername))):
            os.mkdir(self.heap_tmpfoldername, 0777)
        else:
            shutil.rmtree(self.heap_tmpfoldername)
            os.mkdir(self.heap_tmpfoldername, 0777)
        
        #Запускаем метод find для всех каталогов найденных в данном каталоге

        #print listdir(self.startfoldername)
        #raise ErrorWithCode(1111)
        '''
    def zipfile(self):
        pass

    def rarfile(self):
        pass

    def fb2file(self):
        pass



if __name__ == "__main__":
    ff = FileFinder("/Volumes/MACDATA/Dropbox/workspace/rconline/pylearn/kosfb2/src/kosfb2/uploadedbook/770d51d7-c6ae-11e4-9f77-3c15c2cb7e78")
    ff.find("/Volumes/MACDATA/Dropbox/workspace/rconline/pylearn/kosfb2/src/kosfb2/uploadedbook/770d51d7-c6ae-11e4-9f77-3c15c2cb7e78/heap", 0)
