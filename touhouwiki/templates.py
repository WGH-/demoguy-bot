# encoding: utf-8

from __future__ import unicode_literals

import os
import io

templates = {
    "lang": "{{{2}}}",

    "DiPP": "蓬莱人形　～ Dolls in Pseudo Paradise",
    "GFC": "蓮台野夜行　～ Ghostly Field Club",
    "CoSD": "夢違科学世紀　～ Changeability of Strange Dream",
    "R53m": "卯酉東海道　～ Retrospective 53 minutes",
    "MA": "大空魔術　～ Magical Astronomy",
    "TGA": "鳥船遺跡　～ Trojan Green Asteroid",
    "NtoJ": "伊弉諾物質　～ Neo-traditionalism of Japan",
    "UFMG": "未知の花　魅知の旅",
  
    "Akyu": "幺樂団の歴史{{{1}}}　～ Akyu's Untouched Score vol.{{{1}}}",

    "PMiSS": "{{#switch: {{{1}}}|CD=東方求聞史紀 ～ Perfect Memento in Strict Sense}}",

    "EaLND": "東方三月精　～ Eastern and Little Nature Deity",
    "SaBND": "東方三月精 ~ Strange and Bright Nature Deity",

    "SSiB": "東方儚月抄 ～ Silent Sinner in Blue",

    "OSP":  "東方三月精　～ Oriental Sacred Place",

    "HRtP": "東方靈異伝　～ Highly Responsive to Prayers",
    "SoEW": "東方封魔録　～ Story of Eastern Wonderland",
    "PoDD": "東方夢時空　～ Phantasmagoria of Dim.Dream",
    "LLS": "東方幻想郷　～ Lotus Land Story",
    "MS": "東方怪綺談　～ Mystic Square",
    "EoSD": "東方紅魔郷　～ the Embodiment of Scarlet Devil",
    "PCB": "東方妖々夢　～ Perfect Cherry Blossom",
    "IaMP": "東方萃夢想　～ Immaterial and Missing Power",
    "IN": "東方永夜抄　～ Imperishable Night",
    "PoFV": "東方花映塚　～ Phantasmagoria of Flower View",
    "StB": "東方文花帖　～ Shoot the Bullet",
    "MoF": "東方風神録　～ Mountain of Faith",
    "SWR": "東方緋想天　～ Scarlet Weather Rhapsody",
    "SA": "東方地霊殿　～ Subterranean Animism",
    "UFO": "東方星蓮船　～ Undefined Fantastic Object",
    "UNL": "東方非想天則　～ 超弩級ギニョルの謎を追え",
    "HSTS": "東方非想天則　～ 超弩級ギニョルの謎を追え",
    "DS": "ダブルスポイラー　～ 東方文花帖",
    "FW": "妖精大戦争　～ 東方三月精",
    "TD": "東方神霊廟　～ Ten Desires",
    "HM": "東方心綺楼　～ Hopeless Masquerade",
    "DDC": "東方輝針城　～ Double Dealing Character",
    "ISC": "弾幕アマノジャク　～ Impossible Spell Card",

    # not Touhou

    "SG": "秋霜玉",
    "KG": "稀翁玉",

    # fan games:

    "SML": "Super Marisa Land",
}

# these are extremely rare
templates["東方妖々夢"] = templates['PCB']
templates["東方永夜抄"] = templates['IN']

_additional_templates = [
    ("template_track.txt", "Track"),
    ("template_nihongo.txt", "Nihongo"),
]

def _load_additional_templates():
    for filename, templname in _additional_templates:
        filename = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            filename
        )

        with io.open(filename, "r", encoding="UTF-8") as f:
            templates[templname] = f.read().strip()

_load_additional_templates()
