# -*- coding: utf-8 -*-
import codecs
import os
import uuid
import ntpath
import chardet

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
def filesaver(savepath, filename, file):
    print "filename = ", filename
    newfilename = decodestr(filename)
    print "decodefilename = ", newfilename
    '''
    try:
        newfilename = filename.encode("utf-8", "fb2_replacer")
        #newfilename = filename
        print "Имя файла вполне себе нормальное"
    except:
        postfix = filename[-3:]
        newfilename = "{0}.{1}".format(str(uuid.uuid1()), postfix)
        print "Имя файла не удалось декодировать"
    '''


    #savepath ----------------------------------------------------------------------------
    filepath = os.path.join(savepath, newfilename)
    print "filename for save = ", filepath

    with open(filepath, 'w') as f:
        f.write(file.read())

def clearfilename(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

def decodestr(str):
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
    return result
