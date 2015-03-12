# -*- coding: utf-8 -*-
#import pkg_resources
import cherrypy
import cgi
import tempfile
#import cherrybase
import jinja2
import os
import math
import time
#from cherrybase import db
from modules import FileUploader, DBManager, FileParser
#import kosfb2.modules

print cherrypy.engine.state

#Перенесено в DBManager
#pool_name = __package__
#usedb = db.use_db(pool_name)

class Base(object):

    #Задаем место расположения файлов tpl для jinja2
    _cp_config = {
        'tools.jinja.loader': jinja2.PackageLoader (__package__, '__views__')
    }

    def __init__ (self):
        cherrypy.tools.jinja.env.filters ['dt'] = lambda value, format = '%d.%m.%Y %H:%M:%S': value.strftime (format) #@UndefinedVariable

class BookShelf(Base):

    def __init__(self):
        self.message = u'Телепузики'
        self.excount = 0
        self.taskcount = 0
        self.group_chkd = []
        self.grouptype = -1 #Тип группировки (где искать ключевое слово?) (Жанр 0, Серия 1, Издательская серия 2, Автор 3)

        #Инициализируем массив с флагами о выборе "checked" для radio_buttons
        for i in xrange(4):
            self.group_chkd.append("")

        self.find_chkd = []
        self.findtype = -1 #Тип поиска (где искать ключевое слово?) (Название 0, Автор 1, Серия 2, Издательская серия 3)
        self.findkeyword = '' #Ключевое слово для поиска

        #Инициализируем массив с флагами о выборе "checked" для radio_buttons
        for i in xrange(4):
            self.find_chkd.append("")

        self.booklist = [] #Список книг отображаемый на странице по результатам запроса к БД
        self.pagenumb = 0 #Номер страницы
        self.pagebookcount = 20 #Кол-во книг отображаемых на странице

    #----------------------------------------------------------------------------------------------------------------------------------------------------

    #Основные методы

    #----------------------------------------------------------------------------------------------------------------------------------------------------
    @cherrypy.expose
    @cherrypy.tools.jinja (template = 'book2.tpl')
    def index(self):
        print "self.pagebookcount = ", self.pagebookcount
        print "message = ", self.message
        return {'find_chkd': self.find_chkd,
                'findkeyword': self.findkeyword,
                'group_chkd': self.group_chkd,
                'pagenumb' : self.pagenumb,
                'pagebookcount' : self.pagebookcount,
                'books' : self.booklist,
                'message' : self.message
                }

    def parsebook(self):
        #bookfile = '/Volumes/MACDATA/Dropbox/workspace/rconline/pylearn/kosfb2/info/books/trash/Likum_Vse_obo_vsem._Tom_2.224988.fb2' # For MacBook
        #bookfile = '/Volumes/MACDATA/Dropbox/workspace/rconline/pylearn/kosfb2/books/П/Павлов Олег - Вниз по лестнице в небеса.fb2'
        #bookfile необходимо передавать при вызове парсера
        #show_book_info(one_book_parser(bookfile)) #Получаем все метаданные по книге в указанном каталоге

        pass

    #Добавление новых книг в библиотеку
    @cherrypy.expose
    def uploadbook(self, *args, **kwargs):
        cherrypy.response.timeout = 3600
        print "cherrypy.response.timeout = ", cherrypy.response.timeout
        uploadfile = cherrypy.request.params.get('uploadfiles') #Можно использовать встроенный в cherrypy метод получения параметров
        #uploadfile = kwargs['uploadfiles'] #Можно получать параметры из запроса с помощью стандартных именованных параметров метода
        #print "test uploadfile = ", uploadfile

        fu = FileUploader.FileUploader(folderpath = os.path.join('kosfb2', 'uploadedbook'))

        try:
            fu.upload(files = uploadfile)
        except:
            self.message = u"Ошибка. Новые книги не добавлены в библиотеку."
        else:
            self.message = u"Новые книги добавлены в библиотеку."
        '''
        print "uploadfile = ", uploadfile

        with open('out', 'wb') as f:
            f.write(uploadfile.file.read())

        '''

        #Вызываем главную страницу с параметрами отображения элементов интерфейса и с нужным списком книг
        raise cherrypy.HTTPRedirect("/index")

    #Скачивание выбранной книги из библиотеки
    @cherrypy.expose
    def downloadbook(self):
        #Упаковываем выбранные книги , books = [] в архив
        #Передаем архив браузеру для скачивания

        return "Производится скачивание выбранной книги"

    @cherrypy.expose
    def findbook(self, *args, **kwargs):

        #Пробуем обработать параметры группировки из WEB-формы
        try:
            self.grouptype = kwargs["grouptype"]
            self.group_chkd = []
            for i in xrange(4):
                self.group_chkd.append("")
            self.group_chkd[int(self.grouptype)] = 'checked'
            print self.group_chkd, ' ', self.grouptype
        except Exception:
            self.grouptype = -1
            print "Error when get group parameters"

        #Пробуем обработать параметры поиска из WEB-формы
        try:
            self.findtype = kwargs["findtype"]
            self.findkeyword = kwargs["findkeyword"]
            self.find_chkd = []
            for i in xrange(4):
                self.find_chkd.append("")
            self.find_chkd[int(self.findtype)] = 'checked'
        except Exception:
            self.findtype = -1
            self.findkeyword = ''
            print "Error when get find parameters"

        #Обновляем количество книг отображаемых на странице, если оно было изменено пользователем
        try:
            self.pagebookcount = int(kwargs["pagebookcount"])
        except:
            self.pagebookcount = 0

        #Получаем информацию о переходе на другую страницу, если он был произведен пользователем
        try:
            self.pgnavstep = kwargs["pgnavstep"]
        except:
            self.pgnavstep = 0

        #Делаем запрос к БД и получаем список книг
        try:
            #self.booklist = DBManager.find_book(self.findtype, self.findkeyword, self.grouptype)
            self.booklist = self.testbook
        except:
            self.booklist = []
            print "По данным условиям поиска книги не найдены"

        #Получаем список книг для отображения на текущей странице
        self.booklist = self.get_page_booklist()
        '''
        try:
            self.booklist = self.get_page_booklist()
        except:
            print "Не удалось получить список книг для отображения на текущей странице"
        '''

        #Вызываем главную страницу с параметрами отображения элементов интерфейса и с нужным списком книг
        raise cherrypy.HTTPRedirect("/index")

    #----------------------------------------------------------------------------------------------------------------------------------------------------

    #Вспомогательные методы

    #----------------------------------------------------------------------------------------------------------------------------------------------------
    #Функция получает на входе результат поиска
    #На выходе функция выдает массив из книг которые должны отображаться на текущей странице
    def get_page_booklist(self):
        #booklist - результат поиска
        #pagebookcount - кол-во книг выводимых на страницу за один раз
        #pagenumb - порядковый номер страницы

        #Вычисляем кол-во страниц, необходимое для отображения результатов поиска
        #pagebookcount - задается пользователем через web-форму
        if self.pagebookcount > 0:
            self.pagecount = int(math.ceil(len(self.booklist) / self.pagebookcount))
        else:
            self.pagecount = 0

        #Тестовые значения для проверки перелистывания страниц
        #self.pagecount = 10

        print "old page = ", self.pagenumb
        print "self.pagenumb = ", self.pagenumb
        print "self.pagecount = ", self.pagecount
        print "pgnavstep = ", self.pgnavstep

        #Получаем новый номер страницы на которую перешел пользователь
        if self.pagecount > 0:
            self.pagenumb = self.pagenumb + int(self.pgnavstep)
            if self.pagenumb < 0:
                self.pagenumb = 0
            elif self.pagenumb > self.pagecount - 1:
                self.pagenumb = self.pagecount - 1
        else:
            self.pagenumb = 0
        print "new page = ", self.pagenumb

        #Получаем номер первой книги на отображаемой странице
        start_pos = self.pagenumb * self.pagebookcount
        #Получаем номер последней книги на отображаемой странице
        end_pos = start_pos + (self.pagebookcount - 1)

        print "start_pos = ", start_pos
        print "end_pos = ", end_pos

        #Берем из результа поиска книги для отображения на текущей странице
        short_booklist = []
        try:
            for i in xrange(start_pos, end_pos):
                short_booklist.append(self.booklist[i])
        except:
            pass
        return short_booklist

    #----------------------------------------------------------------------------------------------------------------------------------------------------

    #Тестовые методы

    #----------------------------------------------------------------------------------------------------------------------------------------------------

    @cherrypy.expose
    def testdb_in_FileParser (self):
        pf = FileParser.FileParser('')
        pf.testdb()

    #query = create_query_insert_row()
    #task = create_task(query)
    #put_task_to_queue(task)

    #----------------------------------------------------------------------------------------------------------------------------------------------------

    #Тестовый запрос к DBManager'у. Проверка connection usedb декоратора
    @cherrypy.expose
    def testdb (self):
        dbm = DBManager.DBManager()
        dbm.testdb()

    #Тестовый запрос к DBManager'у. Проверка идеи с конструктором задач для очереди
    @cherrypy.expose
    def test_find_books(self):
        dbm = DBManager.DBManager(taskqueue = cherrypy.engine.bg_tasks_queue)
        books = dbm.find_books(field = 'title', keyword = u'Тестовая книга для поиска')

        print 'type(books) = ', type(books).__name__
        print books

        #for book in books:
        #    print book

    #----------------------------------------------------------------------------------------------------------------------------------------------------
    #Тестовый метод с JQuery
    @cherrypy.expose
    def jquery (self):
        #Будет чуть попозже
        pass

    #----------------------------------------------------------------------------------------------------------------------------------------------------

    #Тестовый метод для проверки работоспособности очереди запросов к БД
    @cherrypy.expose
    def queue (self):
        cherrypy.engine.bg_tasks_queue.queue.put (self.tasktest)
        #cherrypy.engine.bg_tasks_queue.start () #Как стартует очередь без этой команды?
        return 'Task was executed {} times'.format (self.excount)

    #----------------------------------------------------------------------------------------------------------------------------------------------------

    #Тестовое задание для очереди
    @cherrypy.expose
    #@usedb
    def tasktest (self, db):
        print db
        cherrypy.engine.log ('Starting task execution')

        dbcursor = db.cursor() #.select_all('SELECT count(*) FROM author;')
        dbcursor = db.select_all('SELECT COUNT(*) FROM book;')
        for row in dbcursor:
            print(row)
        time.sleep (3)
        self.excount += 1
        cherrypy.engine.log ('Stopped task execution')

    #----------------------------------------------------------------------------------------------------------------------------------------------------

    #Тестовый запрос к DBManager'у. Добавление одной книги
    @cherrypy.expose
    def addbook_test (self):
        cherrypy.engine.log ('Starting task execution')

        dbm = DBManager(pool_name = '__package__')

        myquery = dbm.create_query_insert_row(table = 'book',
                                              fields = ['title',
                                                        'encoding',
                                                        'lang',
                                                        'bookid',
                                                        'version',
                                                        'annotation',
                                                        'coverfile',
                                                        'coverexist',
                                                        'zipfile'],
                                              values = [u'\'Тестовая книга\'',
                                                        u'\'utf-8\'',
                                                        u'\'ru\'',
                                                        u'\'тестовый ID\'',
                                                        u'\'1.0\'',
                                                        u'\'Тестовое описание\'',
                                                        u'\'путь к файлу обложки\'',
                                                        u'\'True\'',
                                                        u'\'Путь к архиву с файлом fb2\''
                                                        ]
                                              )
        print "DBManager.query_insert_row() = ", myquery

        dbm.dbtask(query = myquery)
        #dbm.init_mydb()

        cherrypy.engine.log ('Stopped task execution')
        print 'Stopped task execution'
    #----------------------------------------------------------------------------------------------------------------------------------------------------
    @cherrypy.expose
    def post_test(self, *args, **kwargs):
        try:
            books = ['Букварь', 'Вторая', 'Синяя']
        except:
            pass
        return {'books': books}
    #----------------------------------------------------------------------------------------------------------------------------------------------------
    @cherrypy.expose
    @cherrypy.tools.jinja (template = 'cycle.tpl')
    def cycle_test(self):
        books = ['Букварь', 'Вторая', 'Синяя']
        return {'books': books}
    #----------------------------------------------------------------------------------------------------------------------------------------------------
    @cherrypy.expose
    def hello(self):
        return "Hello!"
    #----------------------------------------------------------------------------------------------------------------------------------------------------
