# encoding: utf-8

import os

from mwlib.templ.misc import page
import mwlib.nshandling

templates = {
    "lang": u"{{{2}}}",

    "DiPP": u"蓬莱人形　～ Dolls in Pseudo Paradise",
    "GFC": u"蓮台野夜行　～ Ghostly Field Club",
    "CoSD": u"夢違科学世紀　～ Changeability of Strange Dream",
    "R53m": u"卯酉東海道　～ Retrospective 53 minutes",
    "MA": u"大空魔術　～ Magical Astronomy",
    "TGA": u"鳥船遺跡　～ Trojan Green Asteroid",
    "UFMG": u"未知の花　魅知の旅",
  
    "Akyu": u"幺樂団の歴史{{{1}}}　～ Akyu's Untouched Score vol.{{{1}}}",

    "PMiSS": u"{{#switch: {{{1}}}|CD=東方求聞史紀 ～ Perfect Memento in Strict Sense}}",

    "EaLND": u"東方三月精　～ Eastern and Little Nature Deity",
    "SaBND": u"東方三月精 ~ Strange and Bright Nature Deity",

    "SSiB": u"東方儚月抄 ～ Silent Sinner in Blue",

    "OSP":  u"東方三月精　～ Oriental Sacred Place",

    "HRtP": u"東方靈異伝　～ Highly Responsive to Prayers",
    "SoEW": u"東方封魔録　～ Story of Eastern Wonderland",
    "PoDD": u"東方夢時空　～ Phantasmagoria of Dim.Dream",
    "LLS": u"東方幻想郷　～ Lotus Land Story",
    "MS": u"東方怪綺談　～ Mystic Square",
    "EoSD": u"東方紅魔郷　～ the Embodiment of Scarlet Devil",
    "PCB": u"東方妖々夢　～ Perfect Cherry Blossom",
    "IaMP": u"東方萃夢想　～ Immaterial and Missing Power",
    "IN": u"東方永夜抄　～ Imperishable Night",
    "PoFV": u"東方花映塚　～ Phantasmagoria of Flower View",
    "StB": u"東方文花帖　～ Shoot the Bullet",
    "MoF": u"東方風神録　～ Mountain of Faith",
    "SWR": u"東方緋想天　～ Scarlet Weather Rhapsody",
    "SA": u"東方地霊殿　～ Subterranean Animism",
    "UFO": u"東方星蓮船　～ Undefined Fantastic Object",
    "UNL": u"東方非想天則　～ 超弩級ギニョルの謎を追え",
    "HSTS": u"東方非想天則　～ 超弩級ギニョルの謎を追え",
    "DS": u"ダブルスポイラー　～ 東方文花帖",
    "FW": u"妖精大戦争　～ 東方三月精",
    "TD": u"東方神霊廟　～ Ten Desires",
    "HM": u"東方心綺楼　～ Hopeless Masquerade",
    "DDC": u"東方輝針城　～ Double Dealing Character",

    # fan games:

    "SML": "Super Marisa Land",
}

templates[u"東方妖々夢"] = templates['PCB']
templates[u"東方永夜抄"] = templates['IN']

_additional_templates = (
    ("template_track.txt", "Track"),
    ("template_nihongo.txt", "Nihongo"),
)

def _load_additional_templates():
    for filename, templname in _additional_templates:
        filename = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            filename
        )

        with open(filename, "r") as f:
            templates[templname] = f.read().decode("UTF-8").strip()

_load_additional_templates()

siteinfo = {
    "general": {},
    "interwikimap": [],
    "namespaces": {
        "0": {"*": "", "content": "", "id": 0},
    },
}

class WikiDB(object):
    def __init__(self):
        self.nshandling = mwlib.nshandling.get_nshandler_for_lang("en")
        self.d = {
            self.nshandling.get_fqname(k) : v  for
            k, v in templates.iteritems()
        }

    def get_siteinfo(self):
        return siteinfo

    def normalize_and_get_page(self, title, defaultns=0):
        title = self.nshandling.get_fqname(title)
        return page(self.d.get(title, u""))

    def getURL(self, *args, **kwargs):
        # XXX 
        return ""
