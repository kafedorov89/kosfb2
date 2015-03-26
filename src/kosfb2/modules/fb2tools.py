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
import re
from psycopg2.extensions import adapt

#########################################################################################################################
#Работа с кодировками

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

def decodeUTF8str(str):
    try:
        result = str.decode('utf-8', 'ignore')
        #print "decodestr.ENCODED with utf-8"
        return result
    except UnicodeEncodeError:
        return str

def encodeUTF8str(str):
    try:
        result = str.encode('utf-8', 'ignore')
        #print "decodestr.ENCODED with utf-8"
        return result
    except UnicodeDecodeError:
        try:
            enc_detect = chardet.detect(str)
            #print enc_detect['confidence']
            enc = enc_detect['encoding']
            #print enc

            try:
                result = str.decode(enc).encode('utf-8')
                #print "decodestr.DECODED"
                return result
            except UnicodeEncodeError:
                return str#print e
        except UnicodeEncodeError:
            #result = str.decode('windows-1251', 'fb2_replacer')
            #print "decodestr.CLEAR STR"
            return str

#Функция добавляет пробел перед строкой если она не пустая
def readaddspace(string):
    if string is not None and isinstance(string, str):
        text = decodeUTF8str(string)
        if text != "":
            return " %s" % (text)
        else:
            return ""
    else:
        return ""

#########################################################################################################################
#Набор функций против SQL-инъекций

#Основная функция объединяющая все проверки из замены опасных символов и конструкций
def mask_sql_injection(string, approxi = False, doadapt = True):
    if isinstance(string, str):
        clear_string = string
        if approxi:
            clear_string = "%{0}%".format(replace_err_simbols(clear_string))
        else:
            clear_string = replace_err_simbols(clear_string)

        if doadapt:
            return adapt(clear_string)
        else:
            return clear_string
    else:
        return string

def mask_sql_injection_approxi(string):
    return mask_sql_injection(string, approxi = True)

#Маскируем кавычки для записи в БД
def mask_sql_quotes(string):
    if isinstance(string, str):
        return string.replace("\'", "\\'").replace('\"', '\\"')
    else:
        return ""

def replace_err_simbols(string, mode = 'sql'):

    if isinstance(string, str):
        clear_string = string

        escape_dict = {'"': r'\"',
                       "'": r"\'",
                       "`": r"\`",
                       "*": r"\*",
                       "_": r"\_",
                       "{": r"\{",
                       "}": r"\}",
                       "[": r"\[",
                       "]": r"\]",
                       "(": r"\(",
                       ")": r"\)",
                       ">": r"\>",
                       "=": r"\=",
                       "<": r"\<",
                       "#": r"\#",
                       "+": r"\+",
                       "-": r"\-",
                       ".": r"\.",
                       "!": r"\!",
                       "$": r"\$",
                       "%": r"\%",
                       "^": r"\^",
                       ";": r"\;",
                       "\\": r"\\\\"
                       }


        paranoic_dict = {"CREATE": "",
                         "DROP": "",
                         "SELECT": "",
                         "UNION": "",
                         "UPDATE":"",
                         "INSERT":"",
                         "LIKE":"",
                         "WHERE":"",
                         "TABLE": ""
                         }

        sql_dict = {"--": "",
                    "_": "",
                    ";": "",
                    "%": "",
                    "\\": r"\\"
                    }

        if mode == 'sql':
            active_dict = sql_dict
        elif mode == 'easy_string':
            active_dict = escape_dict

        for key, value in active_dict.iteritems():
            clear_string = clear_string.replace(key, value)

        clear_string = re.sub('\s+', ' ', clear_string).strip()
        clear_string = re.sub('\s+', ' ', clear_string).strip()
        return clear_string
    else:
        return ""

########################################################################################################################
#Работа с каталогами файлами и архивами

#Функция удаляет содержимое указанного каталога - folder
def remove_all_from_folder(folder):
    files = os.listdir(folder)
    for file in files:
        filepath = os.path.join(folder, file)
        print "filepath = ", filepath
        os.remove(filepath)

def remove_tmp_folder(folder):
    if os.path.exists(folder):
        shutil.rmtree(folder)

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

def fileremover(file = None):
    if(os.path.exists(file)):
        os.remove(file)
        print "Файл удален"

#Сохраняет переданный файл - file в нужном месте - savepath под нужным именем - filename
def filesaver(Rename = True, *args, **kwargs):
    try:
        print "args[0]", kwargs['savepath']
        print "args[1]", kwargs['file']
        print "args[2]", kwargs['filename']

        savepath = kwargs['savepath']
        file = kwargs['file']
        filename = kwargs['filename']
    except KeyError:
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
                    filesaver(savepath = dest_dir,
                              file = unpackedfile,
                              filename = postfix)
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

#Получаем имя файла без пути
def clearfilename(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)
