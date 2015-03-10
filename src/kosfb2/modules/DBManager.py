# -*- coding: utf-8 -*-

#import psycopg2
import cherrypy
from cherrybase import db #Нужно ли импортировать db чтобы работать с @cherrybase.db.use_db?

'''
def chbasedb(*args, **kwargs):
    db_decorator = db.use_db(*args, **kwargs) #Здесь важно создавать декоратор от того имени пула, которое было передано при выполнении db.auto_config()
    return db_decorator
'''
'''
def usedb(*args, **kwargs):
    pool_name = __name__.rpartition('.')[0]
    print "pool_name = ", pool_name

    db_decorator = db.use_db(pool_name, *args, **kwargs) #Здесь важно создавать декоратор от того имени пула, которое было передано при выполнении db.auto_config()
    return db_decorator
'''

#pool_name = __package__
pool_name = __name__.partition('.')[0]
print "pool_name = ", pool_name


print "DBManager - pool_name = ", pool_name

usedb = db.use_db(pool_name)

class DBManager:
    def __init__(self, *args, **kwargs):
        pass

    #Тестовый метод для проверки работоспособности очереди запросов к БД
    def queue (self, task):
        try:
            cherrypy.engine.bg_tasks_queue.queue.put (task)
        except Exception: # FIXME: Посмотреть какое исключение возникает в момент неудачноного добавления задачи в очередь
            print "Error when task put to queue"
        return 'Task was executed {} times'.format (self.excount)

    #Можно ли добавить insert в ShortcutsMixin?
    @usedb
    def insert (self, db, query):
        cursor = db.cursor()
        query = query
        cursor.execute(query)
        cursor.close()


    def find_row(self, *args, **kwargs):
        itemlist = []

        #Делаем запрос к БД по заданным параметрам
        ##группировки
        ##поиска в подстроке
        return itemlist

    #Функции (запросы к БД)
        #Дай мне все книги в названии которых есть текст (текст)
        #Дай мне все книги в названии серии которых есть текст (текст)
        #Дай мне все книги в названии издательской серии которых есть текст (текст)
        #Дай мне все книги в имени автора (имя автора)
        #Дай мне все книги по жанру (имя серии)
        #Дай мне ссылку на файл книги (id книги)
        #Дай мне ссылку на файл обложки книги (id книги)

    def query_insert_row(self, *args, **kwargs):
        table = kwargs['table']
        fields = ', '.join(kwargs['fields'])
        values = ', '.join(kwargs['values'])
        print fields
        print values
        query_str = "INSERT INTO {0} ({1}) VALUES ({2})".format(table, fields, values)
        return query_str

    #Запиши всю информацию по книгам (книги)
    def insert_several_items(self, items = []):
        #Запуск insert_one_book(myitems[i]) по списку переданных книг
        #for item in myitems:
            #insert_one_book(item)
        pass

    #Проверяем есть ли значение value поля field в указанной таблице table
    #Существует?
    def check_value_exist(self, table, field, value):
        select_query = "SELECT count(*) from {0} WHERE {1} = {2}".format(table, field, value)
        select_result = cursor.execute(select_query)
        cursor.close()

        if int(select_result['count']) > 0:
            return True
        else:
            return False

    #Проверяем больше ли значение value чем? то которое уже записано в таблицу table в записи с id_value
    #Больше?
    def check_value_bigger(self, table, field, value, id_name, id_value):
        select_query = "SELECT {1} from {0} WHERE {2} = {3}".format(table, field, id_name, id_value)
        select_result = cursor.execute(select_query)
        cursor.close()

        if value > float(select_result[field]):
            return True
        else:
            return False

    #Запиши всю информацию по одной книге (книга)
    def insert_one_book(self, Book):

        newer_version = False
        exists = False
        #Проверь есть ли книга с таким id в БД
        if(check_value_exist(cursor, 'book', "bookid", Book["ID"])):
            exists = True
            #Проверь верcию книги, если книга уже есть в БД
            if(check_value_bigger(cursor, 'book', 'version', Book["Version"], 'bookid', Book["ID"])):
                newer_version = True
            else:
                newer_version = False
        else:
            exists = False

        #Добавь мета-данные книги в БД, если ее нет в базе, или книга имеет более новую версию чем существующая в БД
        if (not exists) or newer_version:
            #Формируем запрос к БД
            '''
            Book["Lang"]
            
            for sequence in Book["Sequences"]: 
                sequence["Name"]
                sequence["Volume"]
            
            for pubsequence in Book["PubSequences"]: 
                pubsequence["Name"]
                pubsequence["Volume"]
            
            Book["Publisher"]
            Book["ID"]
            Book["Version"]
            Book["Title"]
            Book["Genres"]
            Book["Annotation"]
            Book["Authors"]
                Author['FirstName']
                Author['LastName']
                Author['MiddleName']
                Author['NickName']
            Book["CoverFile"]
            Book["CoverExist"]
            Book["ZipFile"]
            '''

        #cur.execute("INSERT INTO book (apoint) VALUES (%s)",
        #    ...             (Point(1.23, 4.56),))
        return "book was added to"

    #Создай все таблицы для проекта kosfb2
    @usedb
    def init_mydb(self, db):
        #Создаем БД
        #Создаем пользователя
        #Задаем права доступа пользователя

        #Автор (пополняемый словарь)
        create_author = "DROP TABLE IF EXISTS author;" + \
                "CREATE TABLE author (" + \
                "uid SERIAL PRIMARY KEY," + \
                "firstname varchar(40) NOT NULL," + \
                "lastname varchar(40) DEFAULT NULL," + \
                "middlename varchar(40) DEFAULT NULL," + \
                "nickname varchar(40) DEFAULT NULL," + \
                "email varchar(40) DEFAULT NULL" + \
                ");"

        #Книга (основной объект)
        create_book = "DROP TABLE IF EXISTS book;" + \
                "CREATE TABLE book (" + \
                "uid SERIAL PRIMARY KEY," + \
                "title varchar(300) NOT NULL," + \
                "encoding varchar(20) NOT NULL," + \
                "lang varchar(15) DEFAULT NULL," + \
                "bookid varchar(100) NOT NULL, " + \
                "version float NOT NULL," + \
                "annotation text DEFAULT NULL," + \
                "coverfile text NOT NULL," + \
                "coverexist boolean DEFAULT NULL," + \
                "zipfile text NOT NULL" + \
                ");"

        #Жанр (пополняемый словарь)
        create_genre = "DROP TABLE IF EXISTS genre;" + \
                "CREATE TABLE genre (" + \
                "uid SERIAL PRIMARY KEY," + \
                "genrename integer NOT NULL," + \
                "genrecode integer NOT NULL" + \
                ");"

        #Книга(m) - Автор(m)
        create_bookauthor = "DROP TABLE IF EXISTS bookauthor;" + \
                "CREATE TABLE bookauthor (" + \
                "uid SERIAL PRIMARY KEY," + \
                "bookid integer NOT NULL," + \
                "authorid integer NOT NULL" + \
                ");"

        #Книга(m) - Жанр(m)
        create_bookgenre = "DROP TABLE IF EXISTS bookgenre;" + \
                "CREATE TABLE bookgenre (" + \
                "uid SERIAL PRIMARY KEY," + \
                "bookid integer NOT NULL," + \
                "genreid integer NOT NULL" + \
                ");"

        #Серия (пополняемый словарь)
        create_sequence = "DROP TABLE IF EXISTS sequence;" + \
                "CREATE TABLE sequence (" + \
                "uid SERIAL PRIMARY KEY," + \
                "name text NOT NULL" + \
                ");"

        #Книга(m) - Серия(m)
        create_booksequence = "DROP TABLE IF EXISTS booksequence;" + \
                "CREATE TABLE booksequence (" + \
                "uid SERIAL PRIMARY KEY," + \
                "bookid integer NOT NULL," + \
                "sequenceid integer NOT NULL," + \
                "volume integer NOT NULL" + \
                ");"

        #Издательская серия (пополняемый словарь)
        create_pubsequence = "DROP TABLE IF EXISTS pubsequence;" + \
                "CREATE TABLE pubsequence (" + \
                "uid SERIAL PRIMARY KEY," + \
                "name text NOT NULL" + \
                ");"

        #Книга(m) - Издательская серия (m)
        create_bookpubsequence = "DROP TABLE IF EXISTS bookpubsequence;" + \
                "CREATE TABLE bookpubsequence (" + \
                "uid SERIAL PRIMARY KEY," + \
                "bookid integer NOT NULL," + \
                "pubsequenceid integer NOT NULL," + \
                "volume integer NOT NULL" + \
                ");"

        myquery = create_author + \
                    create_book + \
                    create_genre + \
                    create_bookauthor + \
                    create_bookgenre + \
                    create_sequence + \
                    create_booksequence + \
                    create_pubsequence + \
                    create_bookpubsequence

        mycursor = db.cursor() #.select_all('SELECT count(*) FROM author;')
        myquery = myquery
        mycursor.execute(myquery)

        #db.cursor().execute(sqlquery)
        #conn.commit() #Подтвержаем изменения, сделанные в базе
        print u"Таблицы созданы"

        #sqlquery = "DROP TABLE public.author;"
        # retrieve the records from the database
        #records = cursor.fetchall()
