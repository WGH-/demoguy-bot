# encoding: UTF-8

import abc
import re

def get_parser():
    return get_all_parsers_classes()[0]()

def get_all_parsers_classes():
    return list(_get_all_parsers_classes_gen())

def _get_all_parsers_classes_gen():
    try:
        import mwlib
    except ImportError:
        pass
    else:
        from . import arrangement_cd_parser_mwlib
        yield arrangement_cd_parser_mwlib.MWLibParser

class ArrangementCDParser(object):
    __metaclass__ = abc.ABCMeta
    
    song_title_re = map(re.compile, [
            u"(?u)(?P<track>\\w+)\\. *?(?P<title>.+?) \\((?P<length>[\\d:?-]*)\\)$",
            u"(?u)(?P<track>\\w+)\\. *?(?P<title>.+?)$",
    ])

    category_name = "Arrangement CDs"
    template_name = "MusicArticle"
    tracks_section_name = "Tracks"

    @abc.abstractmethod
    def parse_page(self, text):
        raise NotImplementedError
