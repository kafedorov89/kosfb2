# -*- coding: utf-8 -*-
import os
import shutil
import uuid
import cherrypy
# FileFinder import FileFinder
#from FileParser import FileParser
#from DBManager import DBManager
from kosfb2.modules import FileFinder, DBManager, FileParser
import fb2tools

dbm = DBManager(taskqueue = cherrypy.engine.bg_tasks_queue)

class ErrorFileUploader(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class FileUploader:
    def __init__(self, *args, **kwargs):
        #Указываем общий рабочий каталог для временного хранения временных каталогов для каждого разбора файлов
        self.uploadfolder = kwargs['uploadfolder']
        self.staticfolder = kwargs['staticfolder']
        self.destfolder = kwargs['destfolder']

        print "uploadfolder = ", self.uploadfolder

        #Если общий каталог еще не был создан, создаем его
        if(not (os.path.exists(self.uploadfolder))):
            os.mkdir(self.uploadfolder, 0777)

    def upload(self, *args, **kwargs):

        #Получаем имя уникального временного каталога для хранения подготовленных и рабранных файлов книг с обложками
        #По данному разбору
        #try:
        reupload = False
        refind = True

        try:
            upload = kwargs['upload']
        except:
            upload = False
            try:
                find = kwargs['find']
                tmpfolder = kwargs['tmpfolder']
                mainfolder = os.path.join(self.uploadfolder, tmpfolder)
                heapfolder = os.path.join(mainfolder, 'heap')
                fb2prepfolder = os.path.join(mainfolder, 'fb2prep')
                fb2errfolder = os.path.join(mainfolder, 'fb2error')
            except:
                find = False
                try:
                    parse = kwargs['parse']
                    tmpfolder = kwargs['tmpfolder']
                    mainfolder = os.path.join(self.uploadfolder, tmpfolder)
                    fb2prepfolder = os.path.join(mainfolder, 'fb2prep')
                    fb2errfolder = os.path.join(mainfolder, 'fb2error')
                except:
                    parse = False

        if upload:
            print "UPLOAD --------------------------------------------------------------------------"
            tmpfolder = str(uuid.uuid1())
            #Создаем временный каталог для работы с книгами
            mainfolder = os.path.join(self.uploadfolder, tmpfolder)
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

            #Создаем временный каталог для разобранных файлов fb2
            fb2errfolder = fb2tools.create_tmp_folder(mainfolder, 'fb2error')
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
            find = True

        if find:
            print "FIND --------------------------------------------------------------------------"
            #---------------------------------------------------------------------------------------------

            #Запускаем модуль FileFinder и находим все fb2 файлы внутри архива
            ff = FileFinder(mainfolder)
            try:
                ff.find(heapfolder, 0)
                parse = True
            except:
                parse = False
                print "Ошибка. Поиск файлов fb2 не завершен правильно"

            print "Всего было найдено %s fb2 файлов" % (ff.filecount,)

        if parse:
            print "PARSE --------------------------------------------------------------------------"
            #Если поиск отработал успешно Запускаем модуль FileParser по списку найденных fb2 фалов
            fp = FileParser(fb2prepfolder, self.staticfolder, self.destfolder, fb2errfolder)

            fb2folder = os.path.join(mainfolder, 'fb2')
            fb2filelist = os.listdir(fb2folder)
            for filename in fb2filelist:
                #Запускаем FileParser для одного файла и Добаляем метаданные по разобранному файлу в БД
                if(dbm.add_book(fp.one_book_parser(os.path.join(fb2folder, filename)))):
                    print "Добавление файла и метаданных произошло успешно"
                else:
                    print "Ошибка. Файл и метаданные не добавлены"

            #Переносим разобранные и добавленные файлы книг и обложек в общий каталог books
            try:
                prepbookfiles = os.listdir(fb2prepfolder)
                print "prepbookfiles: ", prepbookfiles
                for file in prepbookfiles:
                    filepath = os.path.join(fb2prepfolder, file)
                    print "filepath = ", filepath
                    shutil.copy(filepath, self.destfolder)
                print "Разобранные книги перенесены в конечный каталог books"
            except:
                print "Ошибка. Перенос архивов и обложек в конечный каталог books не произведен"

            print "################################################################################"
            print "Всего разобрано %s книг" % (fp.callcount,)
            print "Из них ошибочных %s" % (fp.errorcount,)

            #Получаем список неразобранных файлов
            errorbookfiles = os.listdir(fb2errfolder)
            print errorbookfiles

                #Удаляем временный каталог разбора, если все в целом прошло хорошо
#                if(os.path.exists(mainfolder)):
#                    shutil.rmtree(mainfolder)


        #if Добавление файлов произошло успешно :
            #Удаляем временный каталог


'''
if __name__ == "__main__":
    #fu = FileUploader()
    #fu.upload()
    mainfolder = '/home/kos/Dropbox/workspace/rconline/pylearn/kosfb2/src/kosfb2/uploadedbook/d45f8400-c7cb-11e4-afd7-2c27d7b02944'
    destfolder = '/home/kos/Dropbox/workspace/rconline/pylearn/kosfb2/src/kosfb2/__static__/books'

    fb2folder = os.path.join(mainfolder, 'fb2')
    fb2filelist = os.listdir(fb2folder)
    #print fb2filelist
    fp = FileParser(fb2folder, destfolder)

    for file in fb2filelist:
        filepath = os.path.join(fb2folder, file)
        dbm.add_book(fp.one_book_parser(filepath))
'''
