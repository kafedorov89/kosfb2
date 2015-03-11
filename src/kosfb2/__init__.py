# -*- coding: utf-8 -*-
import pkg_resources
import cherrypy
from cherrybase import db, Application #бибилотека основанная на cherrypy
import os
from . import webapp
#import rco #библиотека, основанная на cherrybase и специализированная под облако RCO

cur_dir = os.path.dirname(__file__)
print 'cur_dir = ', cur_dir

#Задаем путь до файла "debug.conf" конфигурации сервиса
#Важно использовать os.path.join или pkg_resources.resource_filename
#для склеивания частей пути, чтобы путь корректировался в зависимости от ОС
path_to_config = pkg_resources.resource_filename (__package__, '__config__/debug.conf') #Первый вариант указания пути
#path_to_config = os.path.join(cur_dir, '__config__/debug.conf') #Второй вариант указания пути
print 'path_to_config = ', path_to_config

config_file = open(path_to_config)

#with open(path_to_config) as _f:
#    configstr = _f.read()

def get_applications (mode, basename):

    '''
    #Вариант создания приложения с указанием routes
    myapp = cherrybase.Application (name = __package__,
                                    vhosts = ['127.0.0.1:3030', 'kosfb2:3030'],
                                    config = config_file,
                                    routes = [('/', mywebapp.BookShelf(), None)]
                                    
    '''

    #Вариант создания приложения без указания routes. В этом случае необходимо монтировать ресурсы приложения отдельно
    myapp = Application (name = __package__,
                                    vhosts = ['127.0.0.1:3030', 'kosfb2:3030', '192.168.1.185:3030'],
                                    #config = configstr,
                                    config = config_file,
                                    routes = None
                                    )
    #config = config_file,

    #В routes можно добавлять тройные структуры формата (path, handler, cfg)
    #path - путь к web-сервису
    #handler - путь и имя класса cherrypy который может обрабатывать запросы к сервису
    #cfg - путь к файлу конфигурации cherrypy, который будет присоединен к уже применнным параметрам функцией merge

    #Дополнительный раздел config, указывающий на статические каталоги приложения
    static_config = {
        '/':
            {'tools.staticdir.on' : True,
             'tools.staticdir.root' : pkg_resources.resource_filename (__package__, '__static__'), #Можно использовать для получения абсолютного пути к ресурсу внутри проекта
             'tools.staticdir.dir' : '',
             'tools.staticfile.root' : pkg_resources.resource_filename (__package__, '__static__')},
        '/css':
            {'tools.staticdir.on' : True,
             'tools.staticdir.dir' : 'css'},
        '/images':
            {'tools.staticdir.on' : True,
             'tools.staticdir.dir' : 'images'},
        '/books':
            {'tools.staticdir.on' : True,
             'tools.staticdir.dir' : 'books'},
        '/covers':
            {'tools.staticdir.on' : True,
             'tools.staticdir.dir' : 'covers'}
    }
    #Дополняем конфиг приложения описанием статических каталогов
    myapp.app.config.update(static_config)

    encoding_config = {'tools.encode.on': True,
                       'tools.encode.encoding': 'utf-8',
                       'tools.decode.on': True }

    #Дополняем конфиг приложения описанием кодировок
    myapp.app.config.update(encoding_config)

    #cherrybase.config.update(static_config)
    myapp.tree.add ('/', webapp.BookShelf(), None) #Добавляем приложение на хост (Добавляем в корень, но можем и в любую необходимую поддиректорию)

    #print "myapp.app.config = ", myapp.app.config

    #Конфигурируем cherrybase так чтобы он работал с БД
    #myapp.app.config - Подключаем конфиг файл приложения который только что проапдейтили
    #__package__ - Называем пул соединений к БД по имени пакета (Может быть соверщенно любое имя)
    #'storage.db_' - Префикс по которому будет производится поиск параметров в конфиг файле
    #'service' - Имя раздела в конфиге которое вишется в квадратных скобках [<имя раздела>] (Если его не написать, то в конфиге ничего не найдется)
    db.auto_config(myapp.app.config, __package__, 'storage.db_', 'service')

    return myapp
