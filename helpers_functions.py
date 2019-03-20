import os
from urllib.parse import urlparse

import transliterate


def return_fname_ext_from_url(file_url):
    """ :return (name, extension) """
    filename = os.path.basename(urlparse(file_url).path)
    name, extension = separate_name_extension(filename)
    return name, extension

def split_filename_from_url(file_url):
    """ :return 'name.extension' like '1.jpg'"""
    return os.path.basename(urlparse(file_url).path)

def separate_name_extension(filename):
    """ :return name, extension """
    name, extension = os.path.splitext(filename)
    return name, extension


def translit(str_):
    trans = transliterate.translit(str_, reversed=True).replace("'", '')
    return trans
