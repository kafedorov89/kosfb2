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

#Тестовая функция для вывода полученных метаданных по книге
class FileParser(object):

    def __init__(self, *args, **kwargs):
        #Указываем общий рабочий каталог для временного хранения временных каталогов для каждого разбора файлов
        self.foldername = kwargs['folderpath']
        print "foldername = ", self.foldername

        #Если общий каталог еще не был создан, создаем его
        if(not (os.path.exists(self.foldername))):
            os.mkdir(self.foldername, 0777)

        #Получаем имя уникального временного каталога для хранения подготовленных и рабранных файлов книг с обложками
        #По данному разбору
        tmpname = str(uuid.uuid1())

        self.tmpfoldername = os.path.join(self.foldername, tmpname)
        print "self.tmpfoldername = ", self.tmpfoldername

        #Если временный каталог для текущего разбора еще не был создан, создаем его
        if(not (os.path.exists(self.tmpfoldername))):
            os.mkdir(self.tmpfoldername, 0777)

    def show_book_info(self, Book):
        print Book

    #Парсер для одной итерации. Разбирает передаваемый ему filename и возвращает словарь Book с метаданными
    def one_book_parser(self, filename):
        Book = {}
        Annotation = ""
        Genres = []
        Authors = []
        Sequences = []
        PubSequences = []

        ns = "{http://www.gribuser.ru/xml/fictionbook/2.0}" #Схема по которой будем парсить книгу в формате fb2
        myparser = LX.XMLParser(recover = True)

        #--------------------------------------------------------------------------------------------------------
        #Определяем КОДИРОВКУ книги
        print "filename = ", filename
        book = LX.parse(filename, myparser)
        print "Кодировка книги: ", book.docinfo.encoding
        Book["Encoding"] = book.docinfo.encoding
        #--------------------------------------------------------------------------------------------------------

        #myparser = LX.XMLParser(encoding = book.docinfo.encoding)
        #myparser = LX.XMLParser(encoding = 'ascii')
        #book = LX.parse(filename, myparser)

        #В корне файла fb2 находим тег description в котором и лежит нужная информация о книге
        description = book.getroot().find(ns + "description/")

        #Получаем ссылку на корень дерева XML
        bookchilds = book.getroot()
        #--------------------------------------------------------------------------------------------------------
        #Перебираем все теги ВЕРХНЕГО уровня

        for child1 in bookchilds:
            #print "book childs: ", child1.tag
            #Перебираем теги ВТОРГО уровня пока не найдем раздел "title-info"
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
                            print "Язык книги: ", itag.text.encode("utf-8", 'ignore')
                            Book["Lang"] = itag.text.encode("utf-8", 'ignore')
                        #--------------------------------------------------------------------------------------------------------
                        #Узнаем к какой СЕРИИ относится книга
                        if (ns + "sequence" == itag.tag):
                            Sequence = {}
                            sequence = itag
                            print "Книга относится к серии"
                            print "Серия книги: ", sequence.attrib["name"].encode("utf-8", 'ignore')
                            Sequence["Name"] = sequence.attrib["name"].encode("utf-8", 'ignore')
                            try:
                                Sequence["Volume"] = sequence.attrib["number"].encode("utf-8", 'ignore')
                                print "Tom: ", Sequence["Volume"], "из серии"
                            except:
                                Sequence["Volume"] = 1
                                print "Номер тома в серии не определен"

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
                            print "Издательская серия книги: ", publish_sequence.attrib["name"].encode("utf-8", 'ignore')
                            PubSequence["Name"] = publish_sequence.attrib["name"].encode("utf-8", 'ignore')
                            print "Tom: ", publish_sequence.attrib["number"].encode("utf-8", 'ignore'), "из серии"
                            PubSequence["Volume"] = publish_sequence.attrib["number"].encode("utf-8", 'ignore')

                            try:
                                PubSequence["Volume"] = publish_sequence.attrib["number"].encode("utf-8", 'ignore')
                                print "Tom: ", PubSequence["Volume"], "из серии"
                            except:
                                PubSequence["Volume"] = 1
                                print "Номер тома в издательской серии не определен"


                            PubSequences.append(PubSequence) # Добавляем еще одну издательскую серию, в которую входит книга

                        #Узнаем название ИЗДАТЕЛЬСТВА книги
                        if (ns + "publisher" == itag.tag):
                            PubSequence = {}
                            publisher = itag
                            print "В книге указано издательство"
                            Book["Publisher"] = publisher.text.encode("utf-8", 'ignore')
                            print "Издательство: ", Book["Publisher"]

                    Book["PubSequences"] = PubSequences # Упаковываем все найденные издательские серии в структуру книги
                #--------------------------------------------------------------------------------------------------------
                if (ns + "document-info" == child2.tag):
                    #print "    document-info child: ", child2.tag
                    docinfo = child2
                    for itag in docinfo:
                        #--------------------------------------------------------------------------------------------------------
                        #Узнаем на УНИКАЛЬНЫЙ ID книги
                        if (ns + "id" == itag.tag):
                            Book["ID"] = itag.text.encode("utf-8", 'ignore')
                            print "ID книги: ", Book["ID"]
                        #--------------------------------------------------------------------------------------------------------
                        #Узнаем ВЕРСИЮ книги
                        if (ns + "version" == itag.tag):
                            Book["Version"] = itag.text.encode("utf-8", 'ignore')
                            print "Версия книги: ", Book["Version"]
        #--------------------------------------------------------------------------------------------------------
        #Получаем НАЗВАНИЕ книги
        for title in description.findall(ns + "book-title"):
            newbooktitle = title.text.encode("utf-8", 'ignore') # Пробуем получить название книги, не смотря ни на что
            Book["Title"] = newbooktitle
            print "Название книги: " + newbooktitle
            #print "Название книги: " + description.findall(ns + "book-title")[0].text #Альтернативный вариант доступа к элементу
            #print "Название книги: " + description.find(ns + "book-title").text #Альтернативный вариант доступа к элементу
        #--------------------------------------------------------------------------------------------------------
        #Получаем список ЖАНРОВ в которых написана книга
        for genre in description.findall(ns + "genre"):
            newgenre = genre.text.encode("utf-8", 'ignore')
            Genres.append(newgenre) #Добавляем еще один жанр, к которому относится книга
            print "Жанр книги: ", newgenre

        Book["Genres"] = Genres
        #--------------------------------------------------------------------------------------------------------
        #Получаем АННОТАЦИЮ к книге
        for annotation in description.findall(ns + "annotation"):
            for child in annotation:
                try:
                    childtext = child.text.encode("utf-8", 'ignore') #Пробуем получить очередную строку из тега <annotation>
                except:
                    pass
                #print "Test: ", childtext

                if (child is not None) and childtext:
                    Annotation += childtext
                    Book["Annotation"] = Annotation
        print "Описание книги: " + Annotation
        #--------------------------------------------------------------------------------------------------------
        #Собираем всех АВТОРОВ в список
        i = 0
        author_prefix = ['Первый', 'Второй', 'Третий', 'Четвертый']
        for author in description.findall(ns + "author"):
            Author = {}
            author_first_name = author.find(ns + "first-name")
            if author_first_name is not None:
                Author['FirstName'] = author_first_name.text.encode("utf-8", 'ignore')
            author_last_name = author.find(ns + "last-name")
            if author_last_name is not None:
                Author['LastName'] = author_last_name.text.encode("utf-8", 'ignore')
            author_middle_name = author.find(ns + "middle-name")
            if author_middle_name is not None:
                Author['MiddleName'] = author_middle_name.text.encode("utf-8", 'ignore')
            author_nick_name = author.find(ns + "nickname")
            if author_nick_name is not None:
                Author['NickName'] = author_nick_name.text.encode("utf-8", 'ignore')
            Authors.append(Author) #Добавляем еще одного автора в список
            print author_prefix[i], " автор: ",
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
                #coverfile = "../tmpbook/" + Book['ID'] + "_cover.jpg"
                coverfile = os.path.join(self.tmpfoldername, "{0}{1}".format(Book['ID'], ".jpg"))
                coverimg = open(coverfile, 'wb') #Временно сохраняем обложку в jpg
            elif (conttype == 'image/png'):
                #coverfile = "../tmpbook/" + Book['ID'] + "_cover.png"
                coverfile = os.path.join(self.tmpfoldername, "{0}{1}".format(Book['ID'], ".png"))
                coverimg = open(coverfile, 'wb') #Временно сохраняем обложку в png
                print "Найдено изображение типа: png"

            coverimg.write(bincover) #Записываем в файл обложки в побитовом режиме
            coverimg.close() #Закрываем файл обложки для записи

            coverexist = True
            Book["CoverFile"] = coverfile
            #print binary.text #Выводим на экран бинарное представление jpg изображения, вложенного в fb2 файл
        except:
            print "Обложка не найдена в файле"
            coverexist = False

        Book["CoverExist"] = coverexist
        #Завершаем запись обложки
        #--------------------------------------------------------------------------------------------------------
        #Копируем файл книги с новым названием и кладем рядом с обложкой во временный каталог
        newbookfile = os.path.join(self.tmpfoldername, "{0}{1}".format(Book['ID'], ".fb2"))
        newbookzipfile = os.path.join(self.tmpfoldername, "{0}{1}".format(Book['ID'], ".zip"))
        print newbookfile
        if(os.path.exists(newbookfile)):
            print "Временный файл книги уже существует и будет заменен на более новый"
            os.remove(newbookfile) #Удаляем файл с временной книгой

        if(os.path.exists(newbookzipfile)):
            print "Временный файл архива книги уже существует и будет заменен на более новый"
            os.remove(newbookzipfile) #Удаляем файл с временным

        shutil.copy(filename, newbookfile)
        #--------------------------------------------------------------------------------------------------------
        #Упаковываем файл книги в архив
        try:
            with zipfile.ZipFile(newbookzipfile, 'w') as myzip:
                myzip.write(newbookfile)
                myzip.close()
                Book["ZipFile"] = newbookzipfile
        except:
            print "Архив с файлом fb2 создать не удалось"
        #--------------------------------------------------------------------------------------------------------
        #Удаляем файл с временной книгой после ее упаковки в архив
        if(os.path.exists(newbookfile)):
            os.remove(newbookfile)

        return Book #Возвращаем готовую для экспорта в БД книгу со всеми полями

    def create_uuid_folder(self):
        #Получаем имя уникального временного каталога для хранения подготовленных и рабранных файлов книг с обложками
        #По данному разбору
        tmpname = str(uuid.uuid1())

        self.tmpfoldername = os.path.join(self.foldername, tmpname)
        print "self.tmpfoldername = ", self.tmpfoldername

        #Если временный каталог для текущего разбора еще не был создан, создаем его
        if(not (os.path.exists(self.tmpfoldername))):
            os.mkdir(self.tmpfoldername, 0777)

    def remove_uuid_folder(self):
        pass

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
