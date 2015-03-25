#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys

sys.path.append (os.path.dirname(__file__))

#print os.getcwd() #Плохо
print "cherrybased.py path = ", os.path.dirname(__file__) #Хорошо

import cherrybase, cherrypy
import argparse
from kosfb2.modules.fb2tools import create_tmp_folder

def parse_args ():
    result = argparse.ArgumentParser (description = 'CherryPy based server')
    result.add_argument ('--config', '-c', metavar = '<config file>', type = file, default = None, help = 'Path to server configuration file')
    result.add_argument ('--mode', '-m', type = str, choices = ('production', 'debug'), default = 'debug', help = 'Server mode')
    result.add_argument ('--pid', '-p', metavar = '<PID file>', type = str, default = None, help = 'PID file')
    result.add_argument ('--daemon', action = 'store_true', default = False, help = 'Daemonize and detach')
    return result.parse_args ()

if __name__ == '__main__':

    cherrypy.config.update ({
        'server.pkg_path': os.path.dirname(__file__),
        'log.f_access': None,
        'log.f_error': None
    })

    args = parse_args ()
    if not args.config:
        args.config = open ('cherrybased.conf')
    debug = args.mode == 'debug'

    server = cherrybase.Server (config = args.config, debug = debug)

    server.scan_applications ()

    if not debug and args.pid != None:
        cherrypy.config.update ({
            'daemon.on': True,
            'daemon.pid_file': args.pid
        })
    if not debug and args.daemon:
        cherrypy.config ['daemon.on'] = True

    #Создаем каталог для хранения файлов сессий если он еще не создан
    create_tmp_folder('kosfb2', 'sessions')

    server.start ()
