# -*- coding: utf-8 -*-

#import psycopg2
import cherrypy
import cherrybase
#from cherrybase import *
from cherrybase import plugins
from cherrybase import db #Нужно ли импортировать db чтобы работать с @cherrybase.db.use_db?
import uuid
import time
import functools
import os

#pool_name = __package__
#cherrypy.engine.bg_tasks_queue = plugins.TasksQueue (cherrypy.engine)

pool_name = __name__.partition('.')[0]
print "pool_name = ", pool_name
print "DBManager - pool_name = ", pool_name
usedb = db.use_db(pool_name)

class DBManager:
    def __init__(self, *args, **kwargs):
        try:
            self.taskqueue = kwargs['taskqueue']
        except:
            pass
        self.readylist = {}
        self.result = {}
        #self.result = []

    #----------------------------------------------------------------------------------------------------------------------------------------------------

    #Основные методы

    #----------------------------------------------------------------------------------------------------------------------------------------------------

    #Метод добавления задач очереди запросов к БД
    def task_in_queue(self, query):
        try_count = 0
        max_try_count = 100
        wait_time = 0.5

        taskuid = str(uuid.uuid1())
        task = self.create_task(query, taskuid)

        print "self.taskqueue = ", self.taskqueue

        try:
            self.taskqueue.put(task)
            while True:
                try:
                    #print self.result[taskuid]
                    return self.result[taskuid]
                except:
                    try_count = try_count + 1
                    if try_count > max_try_count:
                        print "Error, task timeout"
                        return []
                time.sleep (wait_time)
        except: # FIXME: Посмотреть какое исключение возникает в момент неудачноного добавления задачи в очередь
            print "Error, when task put to queue"
            return []




    '''
    #Генератор задачи - task содержащей запросы к БД котрую можно добавить в очередь с помощью - put_task_to_queue(task)
    def create_task(self, query, taskuid):
        def task(*args, **kwargs):
            return self.easy_task(sqlquery = query, taskuid = taskuid)
        return task
    '''

    #Генератор задачи - task содержащей запросы к БД котрую можно добавить в очередь с помощью - put_task_to_queue(task)
    def create_task(self, query, taskuid):
        return functools.partial(self.easy_task, sqlquery = query, taskuid = taskuid)

    @usedb
    def easy_task (self, db, *args, **kwargs):
        #query = args[0]
        query = kwargs['sqlquery']
        taskuid = kwargs['taskuid']
        print 'query in task = ', query
        dbcursor = db.cursor()
        dbcursor.execute(query)
        #self.result = 1
        #self.result = dbcursor.fetchall()
        self.result[taskuid] = dbcursor.fetchall()
        dbcursor.close()
        time.sleep (3)
        self.readylist[taskuid] = True
        #return True

    '''
    @usedb
    def task(self, db, selectquery):
        cursor = db.cursor()
        cursor = db.select_all(selectquery)
        result = dbcursor.fetchall()
        result = cursor
        cursor.close()

        return result
    '''

    '''
    Использовать основные 2 метода класса можно примерно так:
    
    query = create_query_<имя конкретного генератора запроса>() ()
    task = create_task(query)
    put_task_to_queue(task)
    '''
    #----------------------------------------------------------------------------------------------------------------------------------------------------

    #Методы работы с книгами

    #----------------------------------------------------------------------------------------------------------------------------------------------------

        #Добавление новой книги

    #----------------------------------------------------------------------------------------------------------------------------------------------------

    #Запись информации по одной книге
    def add_one_book(self, Book):
        newer_version = False
        exists = False
        #Проверь есть ли книга с таким id в БД
        if(self.check_value_exist('book', "bookid", Book["ID"])):
            exists = True
            #Проверь верcию книги, если книга уже есть в БД
            if(self.check_value_bigger('book', 'version', Book["Version"], 'bookid', Book["ID"])):
                newer_version = True
            else:
                newer_version = False
        else:
            exists = False

        #Добавь мета-данные книги в БД, если ее нет в базе, или книга имеет более новую версию чем существующая в БД
        if (not exists) or newer_version:
            pass
            #Формируем запрос к БД

            '''
            #------------------------------------------  
            
            Используемые таблицы
            
            book
                bookauthor
            author
            genre
                bookgenre
            sequence
                booksequence
            pubsequence
                bookpubsequence
            publisher
            lang
             
            #------------------------------------------       
            
            Структура мета-данных книги
            
            #------------------------------------------
            
            'ID' 
                Проверяем существет ли такая книга в БД
            
            'Version'
                Проверяем версию книги
                
            Добавляем простые поля книги в таблицу book 
            'ID' в fb2id
            'Version' в version
            'Title' в title
            'Annotation' в annotation
            'CoverFile' в coverfile
            'CoverExist' в coverexist
            'ZipFile' в zipfile
                 Просто записываем значения в таблицу book
                 
                 Получаем uid новой книги из таблицы book по добавленному fb2id
                
            #------------------------------------------
            
            'Lang' в lang
            
            #------------------------------------------
            
            'Sequences'
                'Name' Проверяем есть ли такая серия в таблице sequence
                'Volume' Если серия есть. Проверяем есть ли такой том из серии в таблице booksequence
                
                Добавляем новую серию в таблицу sequence (если такой еще не было) или сразу берем uid из таблицы sequence
                Добавляем запись в таблицу booksequence
            
            #------------------------------------------  
            
            'Publisher'
                Проверяем есть ли такой издатель в таблице publisher, если нет то добавляем нового издателя
                Получаем uid издателя
                
            #------------------------------------------
            
            'PubSequences'
                Добавляем новую серию в таблицу pubsequence (если такой еще не было) или сразу берем uid из таблицы pubsequence
                Добавляем запись в bookpubsequence
            
                'Name' Проверяем есть ли такая серия в таблице sequence
                'Volume' Если серия есть. Проверяем есть ли такой том из серии в таблице bookpubsequence
                
                Указываем в таблице pubsequence publisherid = uid издателя из таблицы publisher 

            #------------------------------------------
            
            'Genres'
                Получаем список uid'ов из таблицы genres по полученным genrecode
                Добавляем записи для каждого uid в таблицу bookgenre
            
            #------------------------------------------
            
            'Authors'
                'FirstName'
                'LastName'
                'MiddleName'
                'NickName'
                
                Проверяем есть ли авторы с такими firstname и lastname и middlename и nickname в таблице author
                Если совпадение есть то берем uid'ы авторов из таблицы author
                    Если есть совпадение но одно из полей в таблице author не заполнено, дополняем запись в таблице author полученными значениями
                Если совпадений нет то создаем новых авторов в таблице author и получаем их uid'ы
                Добавляем записи в таблицу bookauthor  
                
            #------------------------------------------
            '''

        #cur.execute("INSERT INTO book (apoint) VALUES (%s)",
        #    ...             (Point(1.23, 4.56),))
        #return "book was added to"


    #----------------------------------------------------------------------------------------------------------------------------------------------------

        #Поиск книг по заданным критериям

    #----------------------------------------------------------------------------------------------------------------------------------------------------

    #Поиск книг
    def find_books(self, *args, **kwargs):
        field = kwargs['field'] #Поле книги по которому будем искать книгу
        keyword = kwargs['keyword'] #Значение поля

        query = self.create_query_find_rows(keyword = keyword, field = field, table = 'book')
        return self.task_in_queue(query)

    #----------------------------------------------------------------------------------------------------------------------------------------------------



    #----------------------------------------------------------------------------------------------------------------------------------------------------

    #Вспомогательные методы

    #----------------------------------------------------------------------------------------------------------------------------------------------------

    #Проверяем есть ли значение value поля field в указанной таблице table
    #Существует?
    @usedb
    def check_value_exist(self, db, table, field, value):
        select_query = "SELECT count(*) from {0} WHERE {1} = {2}".format(table, field, value)
        select_result = db.select_all(select_query)

        if int(select_result['count']) > 0:
            return True
        else:
            return False

    #Проверяем больше ли значение value чем? то которое уже записано в таблицу table в записи с полем id_name = id_value
    #Больше?
    @usedb
    def check_value_bigger(self, db, table, field, value, id_name, id_value):
        select_query = "SELECT {1} from {0} WHERE {2} = {3}".format(table, field, id_name, id_value)
        select_result = db.select_all(select_query)

        if value > float(select_result[field]):
            return True
        else:
            return False

    #Генератор SQL-запроса для добавления одной строки с полями fields и значениями values  в таблицу table
    def create_query_insert_row(self, *args, **kwargs):
        table = kwargs['table']                 #Имя таблицы
        fields = ', '.join(kwargs['fields'])    #Поля которым необходимо присвоить значения
        values = ', '.join(kwargs['values'])    #Значения полей
        #print fields
        #print values
        query_str = "INSERT INTO {0} ({1}) VALUES ({2})".format(table, fields, values)
        return query_str

    #Генератор SQL-запроса для поиска подстроки keyword в поле field в таблице table c необязательным упорядочиванием по orderfield
    def create_query_find_rows(self, *args, **kwargs):
        #Если orderfield не передано или пусто то используем сортировку по алфавиту
        keyword = kwargs['keyword']
        field = kwargs['field']
        table = kwargs['table']

        try:
            orderfield = kwargs['orderfield']
            useorder = True
        except:
            useorder = False

        if not useorder:
            query_str = u'SELECT * FROM {0} WHERE {1} LIKE \'%{2}%\''.format(table, field, keyword)
        else:
            query_str = u'SELECT * FROM {0} WHERE {1} LIKE \'%{2}%\' ORDER BY {3}'.format(table, field, keyword, orderfield)
        return query_str

    #Генератор SQL-запроса для поиска подстроки keyword в поле field в таблице table c необязательным упорядочиванием по orderfield
    def create_query_find_join_rows(self, *args, **kwargs):
        #Если orderfield не передано или пусто то используем сортировку по алфавиту
        keyword = kwargs['keyword']
        field = kwargs['field']
        table = kwargs['table']
        childtable = kwargs['childtable']

        try:
            orderfield = kwargs['orderfield']
            useorder = True
        except:
            useorder = False

        if not useorder:
            query_str = u'SELECT * FROM {0} WHERE {1} LIKE \'%{2}%\''.format(table, field, keyword)
        else:
            query_str = u'SELECT * FROM {0} WHERE {1} LIKE \'%{2}%\' ORDER BY {3}'.format(table, field, keyword, orderfield)
        return query_str

    #Запиши всю информацию по книгам (книги)
    def insert_several_items(self, items = []):
        #Запуск insert_item(myitems[i]) по списку переданных объектов
        #for item in myitems:
            #insert_one_book(item)
        pass

    #Создаем все таблицы для проекта kosfb2
    @usedb
    def init_db(self, db):
        #Создаем БД
        #Создаем пользователя
        #Задаем права доступа пользователя

        sqlsource = os.path.join(pool_name, "__config__/fb2data.sql")
        print sqlsource

        with open(sqlsource, 'r') as fquery:
            myquery = fquery.read()
            print myquery

        mycursor = db.cursor() #.select_all('SELECT count(*) FROM author;')
        myquery = myquery
        mycursor.execute(myquery)

        print u"Таблицы созданы"

    #----------------------------------------------------------------------------------------------------------------------------------------------------

    #Тестовые методы

    #----------------------------------------------------------------------------------------------------------------------------------------------------

    #Тестовый метод. Проверка connection usedb декоратора
    @usedb
    def testdb(self, db, *args, **kwargs):
        print db
