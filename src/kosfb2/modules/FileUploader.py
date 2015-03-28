# -*- coding: utf-8 -*-
import os
import shutil
import uuid
import cherrypy
import time
# FileFinder import FileFinder
#from FileParser import FileParser
#from DBManager import DBManager
from kosfb2.modules import FileFinder, DBManager, FileParser
from fb2tools import filesaver as fs
from fb2tools import create_tmp_folder as ctf
from fb2tools import remove_tmp_folder as rtf
import logging

dbm = DBManager(taskqueue = cherrypy.engine.bg_tasks_queue)

class ErrorFileUploader(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class FileUploader:
    def __init__(self, *args, **kwargs):
        #Указываем общий рабочий каталог для временного хранения каталогов для каждого разбора файлов
        self.uploadfolder = kwargs['uploadfolder']
        self.staticfolder = kwargs['staticfolder']
        self.destfolder = kwargs['destfolder']
        self.loggername = kwargs['loggername']
        self.logger = logging.getLogger(self.loggername)

        errhand = logging.FileHandler('FileUploader.err')
        errhand.setLevel(logging.ERROR)

        infohand = logging.StreamHandler()
        infohand.setLevel(logging.INFO)

        '''
        self.logger = logging.getLogger('FileUploader')
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(errhand)
        self.logger.addHandler(infohand)

        self.logger.info("FileUploaderStarted")
        self.logger.error("FileUploaderError")
        #self.logger.addHandler(logging.NullHandler())
        '''

        print "uploadfolder = ", self.uploadfolder

        #Если общий каталог еще не был создан, создаем его
        if(not (os.path.exists(self.uploadfolder))):
            os.mkdir(self.uploadfolder, 0777)

    def upload(self, *args, **kwargs):
        time.sleep(5) #Ждем пока все уляжется и начинаем процесс загрузки новых книг в фоне
        mainfolder = ""

        try:
            tmpfoldername = kwargs['tmpfoldername']
            mainfolder = os.path.join(self.uploadfolder, tmpfoldername)
        except KeyError:
            raise
        try:
            doupload = kwargs['doupload']
        except KeyError:
            doupload = False
        try:
            dofind = kwargs['dofind']
        except KeyError:
            dofind = False
        try:
            doparse = kwargs['doparse']

        except KeyError:
            doparse = False

        if mainfolder != "":
            heapfolder = os.path.join(mainfolder, 'heap')
            fb2prepfolder = os.path.join(mainfolder, 'fb2prep')
            fb2errfolder = os.path.join(mainfolder, 'fb2error')
        else:
            raise

        oneuploadlogger = logging.getLogger(self.loggername)
        oneuploadlogger.addHandler(logging.NullHandler())

        if doupload:
            print "UPLOAD --------------------------------------------------------------------------"

            try:
                tmpfoldername = kwargs['tmpfoldername']
                print "Получен идентификатор загрузчика"
            except KeyError:
                tmpfoldername = str(uuid.uuid1())

            #Создаем временный каталог для работы с книгами
            mainfolder = os.path.join(self.uploadfolder, tmpfoldername)
            print "mainfolder = ", mainfolder
            #Если временный каталог для текущего разбора еще не был создан, создаем его
            if(not (os.path.exists(mainfolder))):
                os.mkdir(mainfolder, 0777)
            else:
                shutil.rmtree(mainfolder)
                os.mkdir(mainfolder, 0777)

            #Создаем временный каталог для всех загружаемых файлов
            heapfolder = ctf(mainfolder, 'heap')

            #Создаем временный каталог для найденных fb2 файлов
            ctf(mainfolder, 'fb2')

            #Создаем временный каталог для распаковывания архивов
            ctf(mainfolder, 'arch')

            #Создаем временный каталог для разобранных файлов fb2
            fb2prepfolder = ctf(mainfolder, 'fb2prep')

            #Создаем временный каталог для разобранных файлов fb2
            fb2errfolder = ctf(mainfolder, 'fb2error')

            #---------------------------------------------------------------------------------------------

            #Получаем ссылку на файлы полученные из WEB-формы
            try:
                uploadfiles = kwargs['files'] #SQL inj

                print "uploadfiles = ", uploadfiles

                if type(uploadfiles).__name__ == 'list':
                    print "Получено несколько файлов"
                    for file in uploadfiles:
                        try:
                            fs(savepath = heapfolder,
                                               file = file.file,
                                               filename = file.filename)
                        except AttributeError:
                            raise
                else:
                    print "Получен 1 файл"
                    file = uploadfiles

                    print "file.filename", file.filename
                    try:
                        fs(savepath = heapfolder,
                                           file = file.file,
                                           filename = file.filename)
                    except AttributeError:
                        dofind = False
                dofind = True
            except KeyError:
                dofind = False

        if dofind:
            print "FIND --------------------------------------------------------------------------"
            oneuploadlogger.info("Производится поиск fb2 файлов среди загруженных")
            #---------------------------------------------------------------------------------------------

            #Запускаем модуль FileFinder и находим все fb2 файлы внутри архива
            ff = FileFinder(mainfolder)
            #try:
            ff.find(heapfolder, 0)
            doparse = True
            #except:
            #    parse = False
            #    print "Ошибка. Поиск файлов fb2 не завершен правильно"

            #print "Всего было найдено %s fb2 файлов" % (ff.filecount,)
            oneuploadlogger.info("Всего было найдено %s fb2 файлов" % (ff.filecount,))

        if doparse:
            print "PARSE --------------------------------------------------------------------------"
            oneuploadlogger.info("Производится разбор мата-данных в найденных fb2 файлах")
            #Если поиск отработал успешно Запускаем модуль FileParser по списку найденных fb2 фалов
            fp = FileParser(fb2prepfolder, self.staticfolder, self.destfolder, fb2errfolder)

            fb2folder = os.path.join(mainfolder, 'fb2')
            fb2filelist = os.listdir(fb2folder)
            for i in xrange(0, len(fb2filelist)):
                filename = fb2filelist[i]

                #Запускаем FileParser для одного файла и Добаляем метаданные по разобранному файлу в БД
                if(dbm.add_book(fp.one_book_parser(os.path.join(fb2folder, filename)))):
                    #print "Добавление файла и метаданных произошло успешно"
                    oneuploadlogger.info("Добавление файла №{0} и метаданных произошло успешно".format(i))
                    #Переносим разобранные и добавленные файлы книг и обложек в общий каталог books
                    try:
                        prepbookfiles = os.listdir(fb2prepfolder)
                        print "prepbookfiles: ", prepbookfiles
                        for file in prepbookfiles:
                            filepath = os.path.join(fb2prepfolder, file)
                            print "filepath = ", filepath
                            shutil.copy(filepath, self.destfolder)
                        print "Разобранные книги перенесены в конечный каталог books"
                    except IOError:
                        print "Ошибка. Перенос архивов и обложек в конечный каталог books не произведен"
                else:
                    #print "Ошибка. Файл и метаданные не добавлены"
                    oneuploadlogger.info("Ошибка. Файл №{0} и метаданные не добавлены".format(i))

            print "################################################################################"
            #print "Всего разобрано %s книг" % (fp.callcount,)
            #print "Из них ошибочных %s" % (fp.errorcount,)
            oneuploadlogger.info("Всего разобрано %s книг" % (fp.callcount,))
            oneuploadlogger.info("Из них ошибочных %s" % (fp.errorcount,))


            #Получаем список неразобранных файлов
            errorbookfiles = os.listdir(fb2errfolder)
            print errorbookfiles

                #Удаляем временный каталог разбора, если все в целом прошло хорошо
#                if(os.path.exists(mainfolder)):
#                    shutil.rmtree(mainfolder)


        #if Добавление файлов произошло успешно :
        #Удаляем временный каталог
        rtf(mainfolder)


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
