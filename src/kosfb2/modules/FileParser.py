# -*- coding: utf-8 -*-



import lxml.etree as LX
import base64
import shutil
import zipfile
import os
import uuid
from fb2tools import encodeUTF8str as es
import functools
import re
import time
import logging



root = __name__.partition('.')[0]
print "root = ", root
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

        self.loggername = kwargs['loggername']
        self.logger = logging.getLogger(self.loggername)

    def show_book_info(self, Book):
        print Book

    def errplus1(self, filepath):
        self.errorcount = self.errorcount + 1
        shutil.copy(filepath, self.fb2errfolder)

    #Парсер для одной итерации. Разбирает передаваемый ему filename и возвращает словарь Book с метаданными
    def one_book_parser(self, filepath):

        print "Разбираются мета-данные файла: ", filepath
        time.sleep(0.1)
        err = functools.partial(self.errplus1, filepath)

        self.callcount = self.callcount + 1
        print "Файл №[%s]" % self.callcount

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

        isvalid = False
        try:
            fb2schemafile = os.path.join(root, "fb2schema", "FictionBook_2_2.xsd")
            with open(fb2schemafile, 'r') as f:
                schema = LX.XMLSchema(file = f)

            myparser = LX.XMLParser(recover = True, schema = schema)
            book = LX.parse(filepath, myparser)
            isvalid = True
        except LX.XMLSyntaxError:
            print "XMLSyntaxError"

            try:
                fb2schemafile = os.path.join(root, "fb2schema", "FictionBook_2_0.xsd")
                with open(fb2schemafile, 'r') as f:
                    schema = LX.XMLSchema(file = f)

                myparser = LX.XMLParser(recover = True, schema = schema)

                book = LX.parse(filepath, myparser)
                isvalid = True
            except LX.XMLSyntaxError:
                print "XMLSyntaxError"
                isvalid = False
            except LX.SchematronError:
                print "SchematronError"
            except LX.XMLSchemaError:
                print "XMLSchemaError"
            except LX.XMLSchemaParseError:
                print "XMLSchemaParseError"
            except LX.XMLSchemaValidateError:
                print "XMLSchemaValidateError"

        except LX.SchematronError:
            print "SchematronError"
        except LX.XMLSchemaError:
            print "XMLSchemaError"
        except LX.XMLSchemaParseError:
            print "XMLSchemaParseError"
        except LX.XMLSchemaValidateError:
            print "XMLSchemaValidateError"

#
        #--------------------------------------------------------------------------------------------------------

        if isvalid:
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
                                    Sequence["Name"] = es(sequence.attrib["name"])
                                    print "Серия книги: ", es(sequence.attrib["name"])
                                except:
                                    print "Ошибка. Название серии не распознано"

                                try:
                                    Sequence["Volume"] = es(sequence.attrib["number"])
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
                                    print "Издательская серия книги: ", es(publish_sequence.attrib["name"])
                                    PubSequence["Name"] = es(publish_sequence.attrib["name"])
                                except:
                                    print "Ошибка. Название издательской серии не распознано"
                                try:
                                    PubSequence["Volume"] = es(publish_sequence.attrib["number"])
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
                                    Book["Publisher"] = es(publisher.text)
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
                                    Book["ID"] = es(itag.text)
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
                                    Book["Version"] = es(itag.text)
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
                    Book["Title"] = es(title.text) # Пробуем получить название книги, не смотря ни на что
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
                    newgenre = es(genre.text)
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
                    if child is not None:
                        if isinstance(child.text, str):
                            try:
                                childtext = es(child.text) #Пробуем получить очередную строку из тега <annotation>
                            except:
                                pass

                            Annotation = "{0} {1}".format(Annotation, childtext)

            Book["Annotation"] = Annotation
            print "Описание книги: ", Annotation
            #--------------------------------------------------------------------------------------------------------
            #Собираем всех АВТОРОВ в список
            i = 0
            #author_prefix = ['Первый', 'Второй', 'Третий', 'Четвертый', 'Пятый', 'Шестой', 'Седьмой', 'Восьмой', 'Девятый']
            print "Авторы книги: "
            for author in description.findall(ns + "author"):
                Author = {}
                author_first_name = author.find(ns + "first-name")
                if author_first_name.text is not None:
                    #if isinstance(author_first_name.text, str):
                    Author['FirstName'] = es(author_first_name.text)
                author_last_name = author.find(ns + "last-name")
                if author_last_name is not None:
                    #if isinstance(author_last_name.text, str):
                    Author['LastName'] = es(author_last_name.text)
                author_middle_name = author.find(ns + "middle-name")
                if author_middle_name is not None:
                    #if isinstance(author_middle_name.text, str):
                    Author['MiddleName'] = es(author_middle_name.text)
                author_nick_name = author.find(ns + "nickname")
                if author_nick_name is not None:
                    #if isinstance(author_nick_name.text, str):
                    Author['NickName'] = es(author_nick_name.text)
                Authors.append(Author) #Добавляем еще одного автора в список
                #print author_prefix[i], " автор: ",
                try:
                    print es(Author['FirstName']),
                except:
                    pass
                try:
                    print es(Author['LastName']),
                except:
                    pass
                try:
                    print es(Author['MiddleName']),
                except:
                    pass
                try:
                    print es(Author['NickName'])
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
                    coverfilename = "{0}{1}".format(Book['ID'], ".jpg")

                elif (conttype == 'image/png'):
                    print "Найдено изображение типа: png"
                    coverfilename = "{0}{1}".format(Book['ID'], ".png")

                Book["CoverFile"] = os.path.join("books", coverfilename)
                coverfile = os.path.join(self.fb2prepfolder, coverfilename)

                coverimg = open(coverfile, 'wb') #Временно сохраняем обложку

                coverimg.write(bincover) #Записываем в файл обложки в побитовом режиме
                coverimg.close() #Закрываем файл обложки

                coverexist = True
                #print binary.text #Выводим на экран бинарное представление jpg изображения, вложенного в fb2 файл
            except:
                Book["CoverFile"] = os.path.join("images", "default.jpg")
                print "Обложка не найдена в файле"
                coverexist = False

            Book["CoverExist"] = coverexist


            #Завершаем запись обложки
            #--------------------------------------------------------------------------------------------------------
            #Копируем файл книги с новым названием и кладем рядом с обложкой во временный каталог
            bookfilename = "{0}{1}".format(Book['ID'], ".fb2")
            zipfilename = "{0}{1}".format(Book['ID'], ".zip")
            bookfile = os.path.join(self.fb2prepfolder, bookfilename)
            archfile = os.path.join(self.fb2prepfolder, zipfilename)

            print bookfile
            if(os.path.exists(bookfile)):
                print "Временный файл книги уже существует и будет заменен на более новый"
                os.remove(bookfile) #Удаляем файл с временной книгой

            if(os.path.exists(archfile)):
                print "Временный файл архива книги уже существует и будет заменен на более новый"
                os.remove(archfile) #Удаляем файл с временным

            #Переносим разбираемый файл с книгой в каталог fb2prep для  архивации
            #shutil.copy(filepath, bookfile)
            #--------------------------------------------------------------------------------------------------------

            #Упаковываем файл книги в архив

            #try:
            with zipfile.ZipFile(archfile, 'w') as myzip:

                myzip.write(filepath, bookfilename, zipfile.ZIP_DEFLATED)
                myzip.close()

                Book["ZipFile"] = os.path.join("books", zipfilename)
#            except:
#                print "Архив с файлом fb2 создать не удалось"
#                err()
#                return {}
            #--------------------------------------------------------------------------------------------------------


            return Book #Возвращаем готовую для импорта в БД книгу со всеми полями
        else:
            print "Ошибка. Книга не прошла валидацию по схеме XML"
            err()
            return {}

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
