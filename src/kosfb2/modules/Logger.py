import logging

class Logger(object):

    def __init__(self, *args, **kwargs):
        try:
            self.type = kwargs['type'] #"file", "stream", "null"
            self.mainlevel = kwargs['mainlevel'] #logging.DEBUG, logging.INFO, logging.WARNING
            self.logid = kwargs['logid'] #__name__

            self.file = kwargs['file'] # path to log file

            #3 dicts with
            self.hlevel = kwargs['hlevel'] #logging.DEBUG, logging.INFO, logging.WARNING {}
            self.htype = kwargs['htype'] #"file", "stream", "null"
            self.format = kwargs['format']
        except KeyError:
            raise

    def create(self, *args, **kwargs):
        # create logger with 'spam_application'

        logger = logging.getLogger(self.packagepath)
        logger.setLevel(self.level)
        # create file handler which logs even debug messages

        if self.type == "file":
            hh = logging.FileHandler(self.file)
        elif self.type == "stream":
            hh = logging.StreamHandler()
        elif self.type == "null":
            hh

        else:
            raise ValueError

        formatter = logging.Formatter(self.format)
        hh.setFormatter(formatter)
        hh.setLevel(self.handlerlevel)
        logger.addHandler(hh)

        return logger



