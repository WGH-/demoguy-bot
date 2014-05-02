#!/usr/bin/env python2

from __future__ import print_function

import sys
import os

import time
import datetime

import argparse
import traceback
import collections
import itertools
import tempfile
import subprocess

import touhouwiki.arrangement_cd
import touhouwiki.arrangement_cd_parser
import touhouwiki.wikitext_utils

import interactive_diff

import pywikibot
import pywikibot.catlib
import pywikibot.pagegenerators

default_category_name = "Category:" + touhouwiki.arrangement_cd_parser.ArrangementCDParser.category_name

def normalize_title(title):
    return pywikibot.Link(title).canonical_title()

def get_pages(cat=None):
    if not cat:
        cat = default_category_name
    assert cat.startswith("Category:")

    pages = pywikibot.catlib.Category(pywikibot.getSite(), cat).articles()

    # TODO filter out pages tha don't belong to `default_category_name'
    # if `cat' is set
    # TODO could be done better with special generators

    return (page for page in pywikibot.pagegenerators.PreloadingGenerator(pages)
            if page.namespace() == 0 # only main namespace
    )

def interactive_edit(article_name, old_text, new_text):
    backup = (old_text, new_text)

    while True:
        print(article_name)
        interactive_diff.diff(old_text, new_text)
        print("eo - edit old")
        print("en - edit new")
        print("s  - save")
        print("n  - next (do nothing)")
        print("r  - reset")

        x = raw_input("Action: ").strip()

        if x in ("eo", "edit old"):
            new_text = interactive_diff.run_diff_editor([old_text, new_text], ["old", "generated"])
        elif x in ("en", "edit new"):
            new_text = interactive_diff.run_diff_editor([new_text, old_text], ["generated", "old"])
        elif x in ("s", "save"):
            return new_text
        elif x in ("r", "reset"):
            old_text, new_text = backup
        elif x in ("n", "next"):
            return None
        else:
            print("unknown command")

class NavigationalTemplateUpdater(object):
    def __init__(self, force, cat):
        self.force = force
        self.cat = cat

        self.group_cats = collections.defaultdict(list)

    def on_album(self, page, cd):
        """Extracts required data for later batch update"""
        assert isinstance(page, pywikibot.Page)
        assert isinstance(cd, touhouwiki.arrangement_cd.ArrangementCD)
        
        for group_cat in cd.groupCats:
            group_cat = normalize_title("Category:" + group_cat)
            self.group_cats[group_cat].append((page, cd))

    def is_up_to_date(self, pagecds):
        return False 

    def update_categories(self):
        for group_cat, pagecds in self.group_cats.iteritems():
            self.update_category(group_cat, pagecds) 

    def update_category(self, group_cat, pagecds):
        assert group_cat.startswith("Category:")
        
        if self.cat and self.cat != group_cat:
            return

        if not self.force and self.is_up_to_date(pagecds):
            return

        group_cat = group_cat.replace("Category:", "")
        template = pywikibot.Page(
            pywikibot.getSite(), u"Template:%s Albums" % group_cat)

        try:
            pagecds.sort(key=lambda pagecd: (pagecd[1].released or datetime.date(datetime.MINYEAR, 1, 1), pagecd[1].catalogno))
        except Exception as e:
            print("Category:", group_cat, file=sys.stderr)
            traceback.print_exc()
            return
        try:
            old_text = template.get(get_redirect=True)
        except pywikibot.exceptions.NoPage:
            old_text = u""
        
        new_text = self.generate_template(
            pagecds,
            template
        )

        if new_text.strip() == old_text.strip():
            print("Skipping not changed", template.title())
            return

        result = interactive_edit(template.title(), old_text, new_text)

        if result is not None:
            template.put(result, u"updating (semi-automatic mode)", minorEdit=False, botflag=False) 

    def generate_template(self, pagecds, old_template):
        l = []
        
        if len(pagecds) > 1:
            try:
                old_dict = touhouwiki.wikitext_utils.find_template(old_template.get(get_redirect=True), "Navbox")
                if old_dict is None:
                    old_dict = {}
            except pywikibot.exceptions.NoPage:
                old_dict = {}
            
            l.append(u"{{Navbox\n")
            l.append(u"|type = music\n")
            l.append(u"|name = {{subst:PAGENAME}}\n")

            l.append(u"|title = %s\n" % 
                (old_dict.get("title", "").strip() or u"{{subst:PAGENAME}}"))

            for k, v in old_dict.iteritems():
                if (k == "name" or
                    k == "title" or
                    k == "type" or 
                    k.startswith("group") or
                    k.startswith("list")):
                        continue
                
                l.append(u"|%s = %s\n" % (k.strip(), v.strip()))

            cur_idx = cur_year = 0
            for page, cd in pagecds:
                if cd.released is None or cd.released.year > cur_year:
                    if cd.released is None:
                        cur_year = None
                    else:
                        cur_year = cd.released.year
                    cur_idx += 1
                    l.append(u"\n")
                    l.append(u"|group%d = %s\n" % (cur_idx, unicode(cur_year or "Unknown")))
                    l.append(u"|list%d = %s" % (cur_idx, self.get_link(page, cd)))
                else:
                    l.append(u" &bull; %s" % self.get_link(page, cd))

            l.append(u"\n}}\n")
       
        l.append(u"<noinclude>\n")
        l.append(u"[[Category:Arrange CDs navigational templates]]\n")
        l.append(u"</noinclude>");

        res = u"".join(l)

        # replace subst:PAGENAME here to avoid cluttering the diff
        res = res.replace(u"{{subst:PAGENAME}}", old_template.title(withNamespace=False))

        return res
        
    def get_link(self, page, cd):
        if page.title() == cd.title:
            return u"[[%s]]" % page.title()
        else:
            return u"[[%s | %s]]" % (page.title(), cd.title)

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("source", nargs="?",
        help="Category to load pages from")
    parser.add_argument("--force", dest="force", action="store_true")
    args = parser.parse_args()

    if args.source:
        args.source = normalize_title(args.source)

    parser = touhouwiki.arrangement_cd_parser.get_parser()
    
    updater = NavigationalTemplateUpdater(
        force=args.force,
        cat=args.source)

    for page in get_pages(args.source):
        try:
            print(page.title())
            cd = parser.parse_page(page.get())
        except Exception as exc:
            print(exc)
        else:
            updater.on_album(page, cd)

    updater.update_categories()

if __name__ == "__main__":
    try:
        main()
    finally:
        pywikibot.stopme()
