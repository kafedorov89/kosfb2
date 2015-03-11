# -*- coding: utf-8 -*-
import os
import shutil
import uuid
#import cherrypy
from FileFinder import FileFinder
from FileParser import FileParser
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

        #Создаем временный каталог для всех загружаемых файлов
        heapfolder = fb2tools.create_tmp_folder(mainfolder, 'heap')

        #Создаем временный каталог для найденных fb2 файлов
        fb2tools.create_tmp_folder(mainfolder, 'fb2')

        #Создаем временный каталог для распаковывания архивов
        fb2tools.create_tmp_folder(mainfolder, 'arch')

        #Создаем временный каталог для разобранных файлов fb2
        fb2prepfolder = fb2tools.create_tmp_folder(mainfolder, 'fb2prep')
        #---------------------------------------------------------------------------------------------

        #Получаем ссылку на файлы полученные из WEB-формы
        uploadfiles = kwargs['files']
        print "uploadfiles = ", uploadfiles

        if type(uploadfiles).__name__ == 'list':
            print "Получено несколько файлов"
            for file in uploadfiles:
                fb2tools.filesaver(heapfolder, file.file, file.filename)
        else:
            print "Получен 1 файл"
            file = uploadfiles
            fb2tools.filesaver(heapfolder, file.file, file.filename)

        #---------------------------------------------------------------------------------------------

        #Запускаем модуль FileFinder и находим все fb2 файлы внутри архива
        ff = FileFinder(mainfolder)
        if(ff.find(heapfolder, 0)):
            #Если поиск отработал успешно Запускаем модуль FileParser по списку найденных fb2 фалов
            fp = FileParser(fb2prepfolder)

            fb2folder = os.path.join(mainfolder, 'fb2')
            fb2filelist = os.listdir(fb2folder)
            for file in fb2filelist:
                #Запускаем
                pass
        else:
            # FIXME Надо бы добавить класс ошибок и raise вместо print
            print "Ошибка. Модуль FileFinder некорректно завершил работу."

        #if Добавление файлов произошло успешно :
            #Удаляем временный каталог



if __name__ == "__main__":
    #fu = FileUploader()
    #fu.upload()
    mainfolder = '/home/kos/Dropbox/workspace/rconline/pylearn/kosfb2/src/kosfb2/uploadedbook/d45f8400-c7cb-11e4-afd7-2c27d7b02944'
    fb2folder = os.path.join(mainfolder, 'fb2')
    fb2filelist = os.listdir(fb2folder)
    #print fb2filelist
    for file in fb2filelist:
        pass
