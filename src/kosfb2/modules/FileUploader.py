# -*- coding: utf-8 -*-
import os
import shutil
import uuid
#import cherrypy
from FileFinder import FileFinder
import fb2tools

class ErrorFileUploader(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class FileUploader(object):
    def __init__(self, *args, **kwargs):
        #Указываем общий рабочий каталог для временного хранения временных каталогов для каждого разбора файлов
        self.foldername = kwargs['folderpath']
        print "foldername = ", self.foldername

        #Если общий каталог еще не был создан, создаем его
        if(not (os.path.exists(self.foldername))):
            os.mkdir(self.foldername, 0777)

    def upload(self, *args, **kwargs):

        #Получаем имя уникального временного каталога для хранения подготовленных и рабранных файлов книг с обложками
        #По данному разбору
        #try:
        tmpname = str(uuid.uuid1())
        #Создаем временный каталог для работы с книгами
        mainfolder = os.path.join(self.foldername, tmpname)
        print "mainfolder = ", mainfolder
        #Если временный каталог для текущего разбора еще не был создан, создаем его
        if(not (os.path.exists(mainfolder))):
            os.mkdir(mainfolder, 0777)
        else:
            shutil.rmtree(mainfolder)
            os.mkdir(mainfolder, 0777)

        #Создаем временный каталог для загружаемых файлов
        heapfolder = os.path.join(mainfolder, 'heap')
        print "heapfolder = ", heapfolder
        #Если временный каталог для текущего разбора еще не был создан, создаем его
        if(not (os.path.exists(heapfolder))):
            os.mkdir(heapfolder, 0777)
        else:
            shutil.rmtree(heapfolder)
            os.mkdir(heapfolder, 0777)

        #Создаем временный каталог для найденных fb2 файлов
        fb2folder = os.path.join(mainfolder, 'fb2')
        print "fb2folder = ", fb2folder
        #Если временный каталог для текущего разбора еще не был создан, создаем его
        if(not (os.path.exists(fb2folder))):
            os.mkdir(fb2folder, 0777)
        else:
            shutil.rmtree(fb2folder)
            os.mkdir(fb2folder, 0777)

        #Создаем временный каталог для распаковывания архивов
        archfolder = os.path.join(mainfolder, 'arch')
        print "archfolder = ", archfolder
        #Если временный каталог для текущего разбора еще не был создан, создаем его
        if(not (os.path.exists(archfolder))):
            os.mkdir(archfolder, 0777)
        else:
            shutil.rmtree(archfolder)
            os.mkdir(archfolder, 0777)
        #---------------------------------------------------------------------------------------------

        #Получаем ссылку на файлы полученные из WEB-формы
        uploadfiles = kwargs['files']
        print "uploadfiles = ", uploadfiles

        if type(uploadfiles).__name__ == 'list':
            print "Получено несколько файлов"
            for file in uploadfiles:
                fb2tools.filesaver(heapfolder, file.filename, file.file)
        else:
            print "Получен 1 файл"
            file = uploadfiles
            fb2tools.filesaver(heapfolder, file.filename, file.file)

        #---------------------------------------------------------------------------------------------

        #Запускаем модуль FileFinder и находим все fb2 файлы внутри архива
        ff = FileFinder(mainfolder)
        ff.find(ff.heapfolder, 0)


        '''
        #Сохраняем zip-архив на сервер
        if fileitem:
            #Получаем чистое имя файла, чтобы не было никаких слэшей
            filename = os.path.basename(fileitem)
            open(os.path.join(self.heap_tmpfoldername, filename), 'wb').write(fileitem.file.read())
            print 'The file \'{0}\' was uploaded successfully'.format(filename)
        else:
            print 'No file was uploaded'
        '''


        #Запускаем модуль FileParser по списку найденных fb2 фалов
            #Для каждой разобранной книги запускаем DBManager и записываем метаданные книги в БД

if __name__ == "__main__":
    fu = FileUploader()
    fu.upload()
