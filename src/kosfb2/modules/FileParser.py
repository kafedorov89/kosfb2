# -*- coding: utf-8 -*-
# kosfb2.fb2parse
# book's tags for finding: genre lang first-name last-name book-title binary(jpg)
#import xml.etree.ElementTree as ET

import lxml.etree as LX
import base64
import shutil
import zipfile
import os
import uuid
from fb2tools import decodestr as ds
import functools
import re

#import DBManager

#Тестовая функция для вывода полученных метаданных по книге
class FileParser:
    def __init__(self, *args, **kwargs):
        #Указываем общий рабочий каталог с фалами fb2, которые необходимо разобрать
        self.fb2prepfolder = args[0]
        #Указыаем каталог, куда будем складывать разобранные книги в архивах с обложками
        self.staticfolder = args[1]
        self.destfolder = args[2]
        self.fb2errfolder = args[3]
        self.callcount = 0
        self.errorcount = 0
        #print "foldername = ", self.fb2prepfolder

    def show_book_info(self, Book):
        print Book

    def errplus1(self, filepath):
        self.errorcount = self.errorcount + 1
        shutil.copy(filepath, self.fb2errfolder)

    #Парсер для одной итерации. Разбирает передаваемый ему filename и возвращает словарь Book с метаданными
    def one_book_parser(self, filepath):
        err = functools.partial(self.errplus1, filepath)

        self.callcount = self.callcount + 1
        Book = {}
        Annotation = ""
        Genres = []
        Authors = []
        Sequences = []
        PubSequences = []

        ns = "{http://www.gribuser.ru/xml/fictionbook/2.0}" #Схема по которой будем парсить книгу в формате fb2
        #ns = "{http://www.w3.org/1999/xlink}"
        #myparser = LX.XMLParser(ns_clean = True, recover = True, encoding = 'utf-8')
        #schema_root = LX.XML('''\<xsd:schema xmlns="http://www.gribuser.ru/xml/fictionbook/2.0" xmlns:l="http://www.w3.org/1999/xlink"><xsd:element name="a" type="xsd:integer"/></xsd:schema>''')



        myparser = LX.XMLParser(recover = True)

        #--------------------------------------------------------------------------------------------------------

        print "filepath = ", filepath

        #Получаем полный путь к файлу книги
        #filepath = os.path.join(self.fb2prepfolder, filename)
        book = LX.parse(filepath, myparser)
        #book = LX.parse(newfb2file, myparser)

        #Определяем КОДИРОВКУ книги
        encoding = "utf-8"
        # FIXME Добавить использование кодировки при получении мета-данных из книги
        try:
            Book["Encoding"] = book.docinfo.encoding
            print "Кодировка книги: ", book.docinfo.encoding
        except:
            print "Ошибка. Кодировка не указана в файле"
            Book["Encoding"] = encoding

        #--------------------------------------------------------------------------------------------------------

        #myparser = LX.XMLParser(encoding = book.docinfo.encoding)
        #myparser = LX.XMLParser(encoding = 'ascii')
        #book = LX.parse(filename, myparser)

        #В корне файла fb2 находим тег description в котором и лежит нужная информация о книге
        try:
            description = book.getroot().find(ns + "description/")
        except:
            err()
            print "Ошибка. В файле fb2 отсутствует раздел description"

            return {}

        #Получаем ссылку на корень дерева XML
        bookchilds = book.getroot()
        #--------------------------------------------------------------------------------------------------------
        #Перебираем все теги ВЕРХНЕГО уровня

        idtag = False
        versiontag = False

        for child1 in bookchilds:
            #print "book childs: ", child1.tag
            #Перебираем теги ВТОРОГО уровня пока не найдем раздел "title-info"
            for child2 in child1:
                #--------------------------------------------------------------------------------------------------------
                #Находим раздел "title-info"
                if (ns + "title-info" == child2.tag):
                    #print "    title-info child: ", child2.tag
                    titleinfo = child2
                    for itag in titleinfo:
                        #--------------------------------------------------------------------------------------------------------
                        #Узнаем на каком ЯЗЫКЕ написана книга
                        if (ns + "lang" == itag.tag):
                            try:
                                print "Язык книги: ", itag.text.encode(encoding, 'ignore')
                                Book["Lang"] = itag.text.encode(encoding, 'ignore')
                            except:
                                print "Ошибка. Язык книги не определен"

                        #--------------------------------------------------------------------------------------------------------
                        #Узнаем к какой СЕРИИ относится книга
                        if (ns + "sequence" == itag.tag):
                            Sequence = {}
                            sequence = itag
                            print "Книга относится к серии"

                            try:
                                Sequence["Name"] = ds(sequence.attrib["name"])
                                print "Серия книги: ", ds(sequence.attrib["name"])
                            except:
                                print "Ошибка. Название серии не распознано"

                            try:
                                Sequence["Volume"] = ds(sequence.attrib["number"])
                                print "Tom: ", Sequence["Volume"], "из серии"
                            except:
                                Sequence["Volume"] = 1
                                print "Ошибка. Номер тома в серии не определен"

                            Sequences.append(Sequence) # Добавляем еще одну серию, в которую входит книга

                    Book["Sequences"] = Sequences # Упаковываем все найденные серии в структуру книги
                #--------------------------------------------------------------------------------------------------------
                #Находим раздел "publish-info"
                if (ns + "publish-info" == child2.tag):
                    #print "    publish-info child: ", child2.tag
                    publishinfo = child2
                    for itag in publishinfo:
                        #--------------------------------------------------------------------------------------------------------

                        #Узнаем к какой ИЗДАТЕЛЬСКОЙ СЕРИИ относится книга
                        if (ns + "sequence" == itag.tag):
                            PubSequence = {}
                            publish_sequence = itag
                            print "Книга относится к издательской серии"

                            try:
                                print "Издательская серия книги: ", ds(publish_sequence.attrib["name"])
                                PubSequence["Name"] = ds(publish_sequence.attrib["name"])
                            except:
                                print "Ошибка. Название издательской серии не распознано"
                            try:
                                PubSequence["Volume"] = ds(publish_sequence.attrib["number"])
                                print "Tom: ", PubSequence["Volume"], "из серии"
                            except:
                                PubSequence["Volume"] = 1
                                print "Ошибка. Номер тома в издательской серии не определен. По умочланию установлен 1-ый том"


                            PubSequences.append(PubSequence) # Добавляем еще одну издательскую серию, в которую входит книга

                        #Узнаем название ИЗДАТЕЛЬСТВА книги
                        if (ns + "publisher" == itag.tag):
                            PubSequence = {}
                            publisher = itag
                            print "В книге указано издательство"
                            print 'publisher = ', publisher
                            try:
                                Book["Publisher"] = ds(publisher.text)
                                print "Издательство: ", Book["Publisher"]
                            except:
                                print "Ошибка. Название издательства не распознано"


                    Book["PubSequences"] = PubSequences # Упаковываем все найденные издательские серии в структуру книги
                #--------------------------------------------------------------------------------------------------------

                if (ns + "document-info" == child2.tag):
                    #print "    document-info child: ", child2.tag
                    docinfo = child2


                    for itag in docinfo:
                        #--------------------------------------------------------------------------------------------------------
                        #Узнаем на УНИКАЛЬНЫЙ ID книги
                        if (ns + "id" == itag.tag):
                            idtag = True
                            try:
                                Book["ID"] = ds(itag.text)
                                print "ID книги: ", Book["ID"]
                            except:
                                print "Ошибка. ID книги не распознан"
                                err()
                                return {}
                        #--------------------------------------------------------------------------------------------------------
                        #Узнаем ВЕРСИЮ книги
                        if (ns + "version" == itag.tag):
                            versiontag = True
                            try:
                                Book["Version"] = ds(itag.text)
                                print "Версия книги: ", Book["Version"]
                            except:
                                print "Ошибка. Версия книги не распознана"
                                err()
                                return {}
        if not idtag:
            print "Ошибка. Не найден ID книги"
            err()
            return {}

        if not versiontag:
            print "Ошибка. Не найдена версия книги"
            err()
            return {}

        #--------------------------------------------------------------------------------------------------------
        #Получаем НАЗВАНИЕ книги
        for title in description.findall(ns + "book-title"):
            try:
                Book["Title"] = ds(title.text) # Пробуем получить название книги, не смотря ни на что
                print "Название книги: " + Book["Title"]
            except:
                print "Ошибка. Не найдено название книги"
                err()
                return {}

            #print "Название книги: " + description.findall(ns + "book-title")[0].text #Альтернативный вариант доступа к элементу
            #print "Название книги: " + description.find(ns + "book-title").text #Альтернативный вариант доступа к элементу
        #--------------------------------------------------------------------------------------------------------
        #Получаем список ЖАНРОВ в которых написана книга
        for genre in description.findall(ns + "genre"):
            try:
                newgenre = ds(genre.text)
                Genres.append(newgenre) #Добавляем еще один жанр, к которому относится книга
                print "Жанр книги: ", newgenre
            except:
                print "Ошибка. Название жанра не распознано"

        if len(Genres) > 0:
            Book["Genres"] = Genres
        #--------------------------------------------------------------------------------------------------------
        #Получаем АННОТАЦИЮ к книге
        for annotation in description.findall(ns + "annotation"):
            for child in annotation:
                try:
                    childtext = ds(child.text) #Пробуем получить очередную строку из тега <annotation>
                except:
                    pass

                if (child is not None) and isinstance(childtext, str):
                    Annotation = "{0} {1}".format(Annotation, childtext)

                Book["Annotation"] = Annotation
        print "Описание книги: ", Annotation
        #--------------------------------------------------------------------------------------------------------
        #Собираем всех АВТОРОВ в список
        i = 0
        author_prefix = ['Первый', 'Второй', 'Третий', 'Четвертый', 'Пятый', 'Шестой', 'Седьмой', 'Восьмой', 'Девятый']
        for author in description.findall(ns + "author"):
            Author = {}
            author_first_name = author.find(ns + "first-name")
            if isinstance(author_first_name, str):
                Author['FirstName'] = ds(author_first_name.text)
            author_last_name = author.find(ns + "last-name")
            if isinstance(author_last_name, str):
                Author['LastName'] = ds(author_last_name.text)
            author_middle_name = author.find(ns + "middle-name")
            if isinstance(author_middle_name, str):
                Author['MiddleName'] = ds(author_middle_name.text)
            author_nick_name = author.find(ns + "nickname")
            if isinstance(author_nick_name, str):
                Author['NickName'] = ds(author_nick_name.text)
            Authors.append(Author) #Добавляем еще одного автора в список
            #print author_prefix[i], " автор: ",
            try:
                print Author['FirstName'],
            except:
                pass
            try:
                print Author['LastName'],
            except:
                pass
            try:
                print Author['MiddleName'],
            except:
                pass
            try:
                print Author['NickName']
            except:
                pass
            i += 1

        Book["Authors"] = Authors

        print "" #Для переноса стоки
        #С текстовыми полями покончено
        #--------------------------------------------------------------------------------------------------------
        #Принимаемся за обложку
        try:
            binary = book.find(ns + "binary")
            bincover = base64.b64decode(binary.text) #Конвертируем обложку из base64 для записи в файл
            conttype = binary.attrib["content-type"] #Получаем тип изображения обложки (jpg или png)

            if (conttype == 'image/jpeg'):
                print "Найдено изображение типа: jpeg"

                Book["CoverFile"] = "{0}{1}".format(Book['ID'], ".jpg")
                coverfile = os.path.join(self.fb2prepfolder, Book["CoverFile"])

                coverimg = open(coverfile, 'wb') #Временно сохраняем обложку в jpg


            elif (conttype == 'image/png'):
                print "Найдено изображение типа: png"

                Book["CoverFile"] = "{0}{1}".format(Book['ID'], ".png")
                coverfile = os.path.join(self.fb2prepfolder, "{0}{1}".format(Book['ID'], ".png"))

                coverimg = open(coverfile, 'wb') #Временно сохраняем обложку в png

            coverimg.write(bincover) #Записываем в файл обложки в побитовом режиме
            coverimg.close() #Закрываем файл обложки

            coverexist = True
            #print binary.text #Выводим на экран бинарное представление jpg изображения, вложенного в fb2 файл
        except:
            Book["CoverFile"] = os.path.join(self.destfolder, "", "default.jpg")
            print "Обложка не найдена в файле"
            coverexist = False

        Book["CoverExist"] = coverexist


        #Завершаем запись обложки
        #--------------------------------------------------------------------------------------------------------
        #Копируем файл книги с новым названием и кладем рядом с обложкой во временный каталог
        newbookfile = os.path.join("{0}{1}".format(Book['ID'], ".fb2"))
        newbookzipfile = os.path.join("{0}{1}".format(Book['ID'], ".zip"))

        print newbookfile
        if(os.path.exists(newbookfile)):
            print "Временный файл книги уже существует и будет заменен на более новый"
            os.remove(newbookfile) #Удаляем файл с временной книгой

        if(os.path.exists(newbookzipfile)):
            print "Временный файл архива книги уже существует и будет заменен на более новый"
            os.remove(newbookzipfile) #Удаляем файл с временным

        #Переносим разбираемый файл с книгой в текущий каталог для архивации без вложенных каталогов
        shutil.copy(filepath, newbookfile)
        #--------------------------------------------------------------------------------------------------------

        #Упаковываем файл книги в архив

        try:
            with zipfile.ZipFile(newbookzipfile, 'w') as myzip:
                myzip.write(newbookfile)
                myzip.close()

                #Переносим упакованный архив с книгой в временный каталог
                shutil.copy(newbookzipfile, self.fb2prepfolder)

                #Удаляем временный файл fb2
                if(os.path.exists(newbookfile)):
                    os.remove(newbookfile)
                #Удаляем временный файл zip
                if(os.path.exists(newbookzipfile)):
                    os.remove(newbookzipfile)

                Book["ZipFile"] = os.path.join(self.destfolder, newbookzipfile)
        except:
            print "Архив с файлом fb2 создать не удалось"
            err()
            return {}
        #--------------------------------------------------------------------------------------------------------


        return Book #Возвращаем готовую для импорта в БД книгу со всеми полями


    #----------------------------------------------------------------------------------------------------------------------------------------------------

    #Тестовые методы

    #----------------------------------------------------------------------------------------------------------------------------------------------------


    def several_book_parser(self, derictory_name):
        #derictory_name - каталог с файлами fb2 (по плану это ../uploadedbooks/fb2_<UUID>)

        derictory_name

        #Создаем временный каталог для текущего разбора
        self.create_uuid_folder()

        Books = [] #Готовим массив для книг

        #Здесь будет итератор по файлам bookfile в указанном каталоге derictory_name
            #Эта часть в цикле добавляет информацию о книгах в массив, должен быть итератор по файлам в папке derictory_name
            #bookfile = '*.fb2' #Сюда передаем путь к файлу книги
            #Books.append(self.one_book_parser(bookfile)) #Добавляем информацию о новой распарсенной книге в массив
            #Потом нужно заменить укладку в массив на укладку в БД напрямую

    def testdb(self):
        dbm = DBManager()
        dbm.testdb()

    def test(self):
        #bookfile = '/home/kos/Dropbox/workspace/rconline/pylearn/kosfb2/info/books/M/Mann Thomas - Der kleine Herr Friedemann.fb2' # For Linux
        #bookfile = '/home/kos/Dropbox/workspace/rconline/pylearn/kosfb2/info/books/П/Павлов Олег - Вниз по лестнице в небеса.fb2' # For Linux
        #bookfile = '/home/kos/Dropbox/workspace/rconline/pylearn/kosfb2/info/books/Д/Достоевский Федор - #1 Том 1. Повести и рассказы 1846-1847.fb2' # For Linux

        bookfile = '/Volumes/MACDATA/Dropbox/workspace/rconline/pylearn/kosfb2/info/books/trash/Likum_Vse_obo_vsem._Tom_2.224988.fb2' # For MacBook
        #bookfile = '/Volumes/MACDATA/Dropbox/workspace/rconline/pylearn/kosfb2/books/П/Павлов Олег - Вниз по лестнице в небеса.fb2'

        #bookfile необходимо передавать при вызове парсера
        self.show_book_info(self.one_book_parser(bookfile)) #Получаем все метаданные по книге в указанном каталоге
        #Books = []

if __name__ == "__main__":
    fp = FileParser()
    fp.test()
