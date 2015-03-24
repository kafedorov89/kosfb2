# -*- coding: utf-8 -*-
import codecs
import os
import uuid
import ntpath
import chardet
import rarfile
import zipfile
import shutil
import math

def readaddspace(string):
    if string is not None and isinstance(string, str):
        text = decodeUTF8str(string)
        if text != "":
            return "%s" % (text)
        else:
            return ""
    else:
        return ""

#Маскируем кавычки для записи в БД
def maskquotes(string):
    if isinstance(string, str):
        return string.replace("\'", "\'\'")#.replace('"', '\\"')
    else:
        return string
    #return string

#Удобное создание временного каталога в нужном месте
def create_tmp_folder(rootpath, foldername):
    #rootpath - где расположить каталог
    #foldername - как назвать каталог
    folderpath = os.path.join(rootpath, foldername)
    #Если временный каталог для текущего разбора еще не был создан, создаем его
    if(not (os.path.exists(folderpath))):
        os.mkdir(folderpath, 0777)
    else:
        shutil.rmtree(folderpath)
        os.mkdir(folderpath, 0777)
    print "{0}_folder  was created".format(foldername)
    return folderpath

#Обработчик декодирования неправильных символов
def replace_error_handler(error):
    print error
    print error.start
    print error.end
    return (u'_' * (error.end - error.start), error.end)

#Обработчик декодирования неправильных символов (то же самое в виде lambda функции)
replace_spc_error_handler = lambda error: (u'_' * (error.end - error.start), error.end)

#Добавляем обработчик ошибок кодирования в библиотеку codecs
codecs.register_error("fb2_replacer", replace_error_handler)

#Сохраняет переданный файл - file в нужном месте - savepath под нужным именем - filename
def filesaver(Rename = True, *args, **kwargs):
    try:
        savepath = args[0]
        file = args[1]
        filename = args[2]
    except:
        print "Ошибка аргументов функции filesaver"

    print "savefilename = ", filename
    if Rename:
        prefix = str(uuid.uuid1())
        postfix = filename.split(".")[-1]
        newfilename = "{0}.{1}".format(prefix, postfix)
    else:
        newfilename = encodeUTF8str(filename)

    print "newfilename = ", newfilename

    #savepath ----------------------------------------------------------------------------
    filepath = os.path.join(savepath, newfilename)
    print "filename for save = ", filepath

    with open(filepath, 'wb') as f:
        f.write(file.read())
        print f

#Распаковщик архивов RAR и ZIP
def safeextract(*args, **kwargs):
    source_filename = args[0] #Путь к файлу архива
    dest_dir = args[1] #Куда распаковывать
    settype = args[2] #Принудительное задание расширения файла

    archtype = -1 #Инициализация типа архива

    #logfile = args[3]
    #errorcount = 0 #Количество ошибок при распаковке архива


    #with open('logfile.txt', "wb") as archlog:
    print "source_filename = ", source_filename

    if settype == 'rar':
        if rarfile.is_rarfile(source_filename):
            print "RAR archive was found"
            try:
                arch = rarfile.RarFile(source_filename, 'r')
                archtype = 0
            except rarfile.BadRarFile:
                print "Ошибка. RAR архив поврежден"
                archtype = -1
    elif settype == 'zip':
        if zipfile.is_zipfile(source_filename):
            print "ZIP archive was found"
            try:
                arch = zipfile.ZipFile(source_filename, 'r')
                archtype = 1
            except zipfile.BadZipfile:
                print "Ошибка. ZIP архив поврежден"
                archtype = -1

    else:
        #Тип архива не распознан
        print "Ошибка. Архив не распознан"
        archtype = -1

    #Выводим список файлов содержащихся в архиве
    if archtype >= 0:

        infolist = arch.infolist()

        for infoitem in infolist:

            #filename -------------------------------------------------------------------------------
            filename = infoitem.filename
            #filename = decodestr(filename) #Так не находит фалй в архиве

            print "filename = ", filename

            #savename --------------------------------------------------------------------------------
            #Получаем имя файла из пути к файлу внутри архива
            savename = clearfilename(filename)
            #print "arch savename = ", savename
            #logfile.write("arch savename = {0}\n".format(savename))

            postfix = savename[-4:]
            #print "arch postfix = ", decodestr(postfix)
            #logfile.write("postfix = {0}\n".format(decodestr(postfix)))

            if postfix in [".fb2", ".rar", ".zip"]:
                try:
                    unpackedfile = arch.open(filename)
                    filesaver(dest_dir, unpackedfile, postfix)
                except:
                    print "Ошибка. Не удалось распаковать распознанный архив."

                '''
                try:
                    fb2tools.filesaver(dest_dir, savename, arch.read(filename))
                    archlog.write("Unpacked\n")
                except:
                    errorcount = errorcount + 1
                    archlog.write("Error when unpack\n")
                    
                '''
        #logfile.write("errorcount = {0}\n".format(errorcount))

#Получаем имя файла из пути
def clearfilename(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)


def decodeUTF8str(str):
    try:
        result = str.decode('utf-8', 'ignore')
        #print "decodestr.ENCODED with utf-8"
        return result
    except:
        return str

def encodeUTF8str(str):
    try:
        result = str.encode('utf-8', 'ignore')
        #print "decodestr.ENCODED with utf-8"
        return result
    except:
        try:
            enc_detect = chardet.detect(str)
            #print enc_detect['confidence']
            enc = enc_detect['encoding']
            #print enc

            try:
                result = str.decode(enc).encode('utf-8')
                #print "decodestr.DECODED"
                return result
            except UnicodeDecodeError, e:
                #print e
                pass
        except:
            #result = str.decode('windows-1251', 'fb2_replacer')
            #print "decodestr.CLEAR STR"
            return str
