# -*- coding: utf-8 -*-
import codecs
import os
import uuid
import ntpath
import chardet
import rarfile
import zipfile
import shutil

def maskquotes(string):
    if isinstance(string, str):
        return string.replace("\'", "\\'").replace('\"', '\\"')
    else:
        return string
    #return string

def create_tmp_folder(rootpath, foldername):
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
def filesaver(savepath, file, filename, Rename = True):
    print "filename = ", filename
    if Rename:
        prefix = str(uuid.uuid1())
        postfix = filename.split(".")[-1]
        newfilename = "{0}.{1}".format(prefix, postfix)
    else:
        newfilename = decodestr(filename)

    print "newfilename = ", newfilename

    #savepath ----------------------------------------------------------------------------
    filepath = os.path.join(savepath, newfilename)
    print "filename for save = ", filepath

    with open(filepath, 'wb') as f:
        f.write(file.read())
        print f

def safeextract(*args, **kwargs):
    source_filename = args[0]
    dest_dir = args[1]
    settype = args[2]
    #logfile = args[3]
    errorcount = 0
    archtype = -1

    #with open('logfile.txt', "wb") as archlog:
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
        print "Ошибка. Архив не распознан"
        archtype = -1

    #Выводим список файлов содержащихся в архиве
    if archtype >= 0:

        infolist = arch.infolist()

        for infoitem in infolist:

            #filename -------------------------------------------------------------------------------
            filename = infoitem.filename
            #filename = decodestr(filename) #Так не находит фалй в архиве

            print "arch filename = ", filename

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



def clearfilename(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

def decodestr(str):
    try:
        return str.encode('utf-8', 'ignore')
    except:
        try:
            enc_detect = chardet.detect(str)
            print enc_detect['confidence']
            enc = enc_detect['encoding']
            print enc

            try:
                result = str.decode(enc).encode('utf-8')
            except UnicodeDecodeError, e:
                print e
            print "DECODED"
        except:
            #result = str.decode('windows-1251', 'fb2_replacer')
            result = str
            print "CLEAR STR"
        return str
