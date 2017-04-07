import codecs
import os


def string_or_path(string_or_file, use_unicode=True):
    if os.path.isfile(string_or_file):
        if use_unicode:
            ret = codecs.open(string_or_file, 'r', encoding='utf-8').read()
        else:
            ret = open(string_or_file, 'r').read()
    else:
        ret = string_or_file
    return ret