#!/usr/bin/env python
# -*- coding: utf-8 -*-
class ErrorWithCode(Exception):
    def __init__(self, code):
        self.code = code
    def __str__(self):
        return repr(self.code)

if __name__ == '__main__':
    try:
        raise ErrorWithCode(1000)
    except ErrorWithCode as e:
        print "Received error with code:", e.code