# encoding: UTF-8

import os
import unittest
import io
import datetime

from .. import arrangement_cd
from .. import arrangement_cd_parser

class TestParserBase(object):
    _parser_class = None

    def _load_file(self, filename):
        filename = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            filename
        )

        with io.open(filename, "rt", encoding="UTF-8") as f:
            return f.read()

    def test_retro_future_girls(self):
        parser = self._parser_class()
        text = self._load_file("article_samples/RETRO_FUTURE_GIRLS.txt")
        result = parser.parse_page(text)

        self.assertIsInstance(result, arrangement_cd.ArrangementCD)

        self.assertEqual(result.title, u"RETRO FUTURE GIRLS")
        self.assertEqual(result.titleen, u"RETRO FUTURE GIRLS")
        self.assertEqual(result.titlejp, None)
        self.assertEqual(result.titlejprom, None)
        self.assertEqual(result.group, u"ShibayanRecords") 
        self.assertEqual(result.groupjp, u"ShibayanRecords") 
        self.assertEqual(result.groupCats, [u"ShibayanRecords"]) 
        
        self.assertEqual(result.catalogno, u"STAL-1302")
        self.assertEqual(result.released, datetime.date(year=2013, month=12, day=30))
        
        self.assertEquals(len(result.tracks), 8)

        myon = result.tracks[3]
        self.assertIsInstance(myon, arrangement_cd.Song)
        self.assertEqual(myon.title, u"MyonMyonMyonMyonMyonMyonMyon!")
        self.assertEqual(myon.length, u"09:46")
        self.assertEqual(myon.translated_title, None)
        self.assertEqual(myon.arrangement, [u"Shibayan"])
        self.assertEqual(myon.lyrics, [u"黒岩サトシ"])
        self.assertEqual(myon.vocals, [u"3L"])
        #self.assertEqual(len(myon.sources), 1)
        src = myon.sources[0]
        self.assertIsInstance(src, arrangement_cd.SongSource)
        self.assertEqual(src.game, u"東方妖々夢 ～ Perfect Cherry Blossom")
        self.assertEqual(src.titles, [u"東方妖々夢 ～ Ancient Temple"])

        # random checks
        self.assertEqual(result.tracks[4].title, u"とびだせ！バンキッキ")
        self.assertEqual(result.tracks[4].translated_title, u"Fly Out! Bankikki")

    def test_tadori(self):
        parser = self._parser_class()
        text = self._load_file("article_samples/tadori.txt")
        result = parser.parse_page(text)
        
        self.assertIsInstance(result, arrangement_cd.ArrangementCD)

        self.assertEqual(result.title, u"辿")
        self.assertEqual(result.titleen, u"Follow")
        self.assertEqual(result.titlejp, u"辿")
        self.assertEqual(result.titlejprom, u"Tadori")
        self.assertEqual(result.group, u"Diao ye zong") 
        self.assertEqual(result.groupjp, u"Diao ye zong") # it's a "bug" in article itself
        self.assertEqual(result.groupCats, [u"Diao ye zong"]) 
        
        self.assertEqual(result.catalogno, u"RDWL-0010")
        self.assertEqual(result.released, datetime.date(year=2012, month=12, day=30))
        
        self.assertEquals(len(result.tracks), 7)

        song = result.tracks[3]
        self.assertEqual(song.title, u"name for the love")
        self.assertEqual(song.length, u"06:29")
        self.assertEqual(song.translated_title, None)
        self.assertEqual(song.arrangement, [u"RD-Sounds"])
        self.assertEqual(song.lyrics, [u"RD-Sounds"])
        self.assertEqual(song.vocals, [u"めらみぽっぷ"])
        #self.assertEqual(len(song.sources), 2)
        src = song.sources[0]
        self.assertIsInstance(src, arrangement_cd.SongSource)
        self.assertEqual(src.game, u"東方文花帖 ～ Shoot the Bullet")
        self.assertEqual(src.titles, [u"天狗が見ている ～ Black Eyes"])
        src = song.sources[1]
        self.assertEqual(src.game, u"東方靈異伝 ～ Highly Responsive to Prayers")
        self.assertEqual(src.titles, [u"永遠の巫女"])

    def test_white_lotus(self):
        parser = self._parser_class()
        text = self._load_file("article_samples/white_lotus.txt")
        result = parser.parse_page(text)

        src = result.tracks[1].sources[0]

        self.assertEqual(src.game, u"東方星蓮船 ～ Undefined Fantastic Object")
        self.assertEqual(src.titles, [u"キャプテン・ムラサ", u"幽霊客船の時空を越えた旅"])

    def test_touhou_bubbling_underground(self):
        parser = self._parser_class()
        text = self._load_file("article_samples/touhou_bubbling_underground.txt")
        result = parser.parse_page(text)
        
        self.assertEqual(result.title, u"東方泡沫天獄")
        self.assertEqual(result.titlejp, u"東方泡沫天獄")
        self.assertEqual(result.titlejprom, u"Touhou Baburingu Andaaguraundo")
        self.assertEqual(result.titleen, u"Touhou Bubbling Underground")

def _init_parser_tests():
    for parser in arrangement_cd_parser.get_all_parsers_classes():
        class_name = "Test" + parser.__name__

        globals()[class_name] = type(class_name, (TestParserBase, unittest.TestCase), {"_parser_class": parser})

_init_parser_tests()
del _init_parser_tests


