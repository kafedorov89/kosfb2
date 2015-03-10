# -*- coding: utf-8 -*-
import codecs
import os
import uuid

def replace_error_handler(error):
    print error
    print error.start
    print error.end
    return (u'_' * (error.end - error.start), error.end)

replace_spc_error_handler = lambda error: (u'_' * (error.end - error.start), error.end)
codecs.register_error("fb2_replacer", replace_error_handler)

def filesaver(savepath, filename, file):
    print "filename = ", filename

    try:
        #newfilename = filename.encode("utf-8", "fb2_replacer")
        newfilename = filename
        print "Имя файла вполне себе нормальное"
    except:
        postfix = filename[-3:]
        newfilename = "{0}.{1}".format(str(uuid.uuid1()), postfix)
        print "Имя файла не удалось декодировать"
    print "decodefilename = ", newfilename

    #savepath ----------------------------------------------------------------------------
    filepath = os.path.join(savepath, newfilename)
    print "filename for save = ", filepath

    with open(filepath, 'w') as f:
        f.write(file.read())
