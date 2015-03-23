# -*- coding: utf-8 -*-
#import pkg_resources
import cherrypy
#import cgi
#import tempfile
#import cherrybase
import jinja2
import os
import math
import time
#from cherrybase import db
from kosfb2.modules import FileUploader, DBManager, FileParser
#import kosfb2.modules

print cherrypy.engine.state

#Перенесено в DBManager
#pool_name = __package__
#usedb = db.use_db(pool_name)

#dbm = DBManager.DBManager(taskqueue = cherrypy.engine.bg_tasks_queue)
dbm = DBManager(taskqueue = cherrypy.engine.bg_tasks_queue)

class Base(object):

    #Задаем место расположения файлов tpl для jinja2
    _cp_config = {
        'tools.jinja.loader': jinja2.PackageLoader (__package__, '__views__')
    }

    def __init__ (self):
        cherrypy.tools.jinja.env.filters ['dt'] = lambda value, format = '%d.%m.%Y %H:%M:%S': value.strftime (format) #@UndefinedVariable

class BookShelf(Base):

    def init_findtype(self, type = 0, text = ''):
        self.find_chkd = []
        self.findtype = type #Тип поиска (где искать ключевое слово?) (Название 0, Автор 1, Серия 2, Издательская серия 3)
        self.findkeyword = text #Ключевое слово для поиска

        #Инициализируем массив с флагами о выборе "checked" для radio_buttons
        for i in xrange(4):
            self.find_chkd.append("")
        self.find_chkd[int(self.findtype)] = 'checked'

    def init_grouptype(self, type = 3):
        self.group_chkd = []
        self.grouptype = type #Тип группировки (где искать ключевое слово?) (Жанр 0, Серия 1, Издательская серия 2, Автор 3)
        #Инициализируем массив с флагами о выборе "checked" для radio_buttons
        for i in xrange(4):
            self.group_chkd.append('')
        self.group_chkd[int(self.grouptype)] = 'checked'

    def __init__(self):
        #self.sid = cherrypy.session

        self.wasindex = False
        self.message = u'Первый запуск'

        self.init_grouptype()
        self.init_findtype()

        self.fullbooklist = []
        self.shortbooklist = []

        #self.booklist = [] #Список книг отображаемый на странице по результатам запроса к БД

        self.pagenumb = 0 #Номер страницы
        self.pagebookcount = 20 #Кол-во книг отображаемых на странице

    #----------------------------------------------------------------------------------------------------------------------------------------------------

    #Основные методы
    @cherrypy.expose
    @cherrypy.tools.jinja (template = 'book3.tpl')
    def main(self):
        sss = cherrypy.session

#        if self.wasindex:
        print "self.pagebookcount = ", self.pagebookcount
        print "main message = ", sss.get('message')

        return {'find_chkd': self.find_chkd,
                'findkeyword': self.findkeyword,
                'group_chkd': self.group_chkd,
                'pagenumb' : self.pagenumb,
                'pagebookcount' : self.pagebookcount,
                'books' : self.shortbooklist,
                'message' : self.message
                }
#        else:
#            pass

    #----------------------------------------------------------------------------------------------------------------------------------------------------
    @cherrypy.expose
    @cherrypy.tools.jinja (template = 'book3.tpl')
    def index(self):
        sss = cherrypy.session

        sss['wasindex'] = True
        #cherrypy.session.save()
        #cherrypy.response.cookie['user_name'] = 'TurboGears User' #Пишем cookies. Пример

        sss['find_chkd'] = self.find_chkd
        sss['findkeyword'] = self.findkeyword
        sss['group_chkd'] = self.group_chkd
        sss['pagenumb'] = self.pagenumb
        sss['pagebookcount'] = self.pagebookcount
        sss['shortbooklist'] = self.shortbooklist
        sss['message'] = self.message

        self.randbook()

        return {'find_chkd': self.find_chkd,
                'findkeyword': self.findkeyword,
                'group_chkd': self.group_chkd,
                'pagenumb' : self.pagenumb,
                'pagebookcount' : self.pagebookcount,
                'books' : self.shortbooklist,
                'message' : self.message
                }

    #Добавление новых книг в библиотеку
    @cherrypy.expose
    def uploadbook(self, *args, **kwargs):
        cherrypy.response.timeout = 3600
        print "cherrypy.response.timeout = ", cherrypy.response.timeout
        #try:
        uploadfile = cherrypy.request.params.get('uploadfiles') #Можно использовать встроенный в cherrypy метод получения параметров
        #uploadfile = kwargs['uploadfiles'] #Можно получать параметры из запроса с помощью стандартных именованных параметров метода
        #print "test uploadfile = ", uploadfile

        try:
            fu = FileUploader(uploadfolder = os.path.join('kosfb2', 'uploadedbook'),
                              staticfolder = os.path.join('kosfb2', '__static__'),
                              destfolder = os.path.join('kosfb2', '__static__', 'books'))

            fu.upload(upload = True, files = uploadfile)
            self.message = u"Книги успешно загружены"
        except:
            self.message = u"Ошибка. Книги не загружены"
            pass
        #Вызываем главную страницу с параметрами отображения элементов интерфейса и с нужным списком книг
        raise cherrypy.HTTPRedirect("/main")
#        except:
#            self.message = "Книги не загружены. Что-то приключилось"
#            raise cherrypy.HTTPRedirect("/main")
#            pass

    @cherrypy.expose
    def randbook(self):
        sss = cherrypy.session


        #Делаем запрос к БД и получаем случайный список книг
        #try:
        self.fullbooklist = dbm.find_books(randbook = True, count = self.pagebookcount)
        #except:
        #    self.fullbooklist = []
        #    print "По данным условиям поиска книги не найдены"

        self.showbook()

    @cherrypy.expose
    def findbook(self, *args, **kwargs):
        #Пробуем обработать параметры группировки из WEB-формы
        try:
            self.grouptype = kwargs["grouptype"]
            self.init_grouptype(type = self.grouptype)
        except:
            print "Error when get group parameters"
            self.init_grouptype()

        #Пробуем обработать параметры поиска из WEB-формы
        try:
            self.findtype = kwargs["findtype"]
            self.findkeyword = kwargs["findkeyword"]
            self.init_findtype(type = self.findtype, text = self.findkeyword)
        except:
            print "Error when get find parameters"
            self.init_findtype()

        #Делаем запрос к БД и получаем список книг
        try:
            self.fullbooklist = dbm.find_books(keyword = self.findkeyword.encode('utf-8', 'ignore'),
                                               findtype = int(self.findtype),
                                               orderby = int(self.grouptype))
        except:
            self.fullbooklist = []
            print "По данным условиям поиска книги не найдены"

        self.showbook()

    @cherrypy.expose
    def showbook(self, *args, **kwargs):
        #Обновляем количество книг отображаемых на странице, если оно было изменено пользователем
        try:
            self.pagebookcount = int(kwargs["pagebookcount"])
        except:
            pass

        #Получаем информацию о переходе на другую страницу, если он был произведен пользователем
        try:
            self.pgnavstep = kwargs["pgnavstep"]
        except:
            self.pgnavstep = 0

        #Получаем список книг для отображения на текущей странице
        try:
            self.shortbooklist = self.get_page_booklist(self.fullbooklist)
            self.message = u"Книги найдены"
        except:
            self.message = u"По данным условиям поиска книги не найдены"
            self.shortbooklist = []
        #Вызываем главную страницу с параметрами отображения элементов интерфейса и с нужным списком книг
        raise cherrypy.HTTPRedirect("/main")
    #----------------------------------------------------------------------------------------------------------------------------------------------------

    #Вспомогательные методы

    #----------------------------------------------------------------------------------------------------------------------------------------------------
    #Добавление новых книг в библиотеку после ошибки
    @cherrypy.expose
    def refindbook(self, *args, **kwargs):
        cherrypy.response.timeout = 3600
        print "cherrypy.response.timeout = ", cherrypy.response.timeout
        tmpfolder = cherrypy.request.params.get('tmpfoldername') #Можно использовать встроенный в cherrypy метод получения параметров

        fu = FileUploader(uploadfolder = os.path.join('kosfb2', 'uploadedbook'),
                          staticfolder = os.path.join('kosfb2', '__static__'),
                          destfolder = os.path.join('kosfb2', '__static__', 'books'))

        fu.upload(find = True, tmpfolder = tmpfolder)

    #Добавление новых книг в библиотеку после ошибки
    @cherrypy.expose
    def reparsebook(self, *args, **kwargs):
        cherrypy.response.timeout = 3600
        print "cherrypy.response.timeout = ", cherrypy.response.timeout
        tmpfolder = cherrypy.request.params.get('tmpfoldername') #Можно использовать встроенный в cherrypy метод получения параметров

        fu = FileUploader(uploadfolder = os.path.join('kosfb2', 'uploadedbook'),
                          staticfolder = os.path.join('kosfb2', '__static__'),
                          destfolder = os.path.join('kosfb2', '__static__', 'books'))

        fu.upload(parse = True, tmpfolder = tmpfolder)

    #Инициализация базы данных fb2data
    @cherrypy.expose
    def init_fb2_data (self):
        #dbm = DBManager()
        dbm.init_db()
        dbm.init_genre()

    #Инициализация таблицы жанров
    @cherrypy.expose
    def init_genre_table (self):
        #dbm = DBManager()
        dbm.init_genre()

    #Функция получает на входе результат поиска
    #На выходе функция выдает массив из книг которые должны отображаться на текущей странице
    def get_page_booklist(self, fullbooklist = []):
        #booklist - результат поиска
        #pagebookcount - кол-во книг выводимых на страницу за один раз
        #pagenumb - порядковый номер страницы

        #Вычисляем кол-во страниц, необходимое для отображения результатов поиска
        #pagebookcount - задается пользователем через web-форму
        if self.pagebookcount > 0:
            self.pagecount = int(math.ceil(len(fullbooklist) / self.pagebookcount))
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
        end_pos = start_pos + self.pagebookcount

        print "start_pos = ", start_pos
        print "end_pos = ", end_pos

        #Берем из результа поиска книги для отображения на текущей странице
        short_booklist = []
        try:
            for i in xrange(start_pos, end_pos):
                short_booklist.append(fullbooklist[i])
        except:
            pass
        return short_booklist

    #----------------------------------------------------------------------------------------------------------------------------------------------------

    #Тестовые методы

    #----------------------------------------------------------------------------------------------------------------------------------------------------

    #Использование сессий
    @cherrypy.expose
    def session_test(self, *args, **kwargs):
        sss = cherrypy.session

        out = ''
        for key, value in kwargs.items():
            out += key + '=' + value + '\n'
            sss[key] = value
        print sss
        return out


    #----------------------------------------------------------------------------------------------------------------------------------------------------
    #Тестовый метод с JQuery
    @cherrypy.expose
    def jquery_test (self):
        #Будет чуть попозже
        pass


    #----------------------------------------------------------------------------------------------------------------------------------------------------
