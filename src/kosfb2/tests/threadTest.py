#!/usr/bin/env python
# -*- coding: utf-8 -*-

import threading
import datetime


def run_in_thread(fn): #Декоратор для запуска метода в новом потоке

    def wrapper(*k, **kw): #Оборачиваем метод fn
        t = threading.Thread(target = fn, args = k, kwargs = kw)
        t.start()
        return t
    return wrapper #Возвращаем обернутый метод fn

class ThreadClass(threading.Thread):
    def run(self):
        now = datetime.datetime.now()
        print "%s says Hello World at time: %s" % (self.getName(), now)

    def infCycle(self):
        while 1:
            print "Ok"

if __name__ == '__main__':
    for i in range(4):
        t = ThreadClass()
        t.start()
