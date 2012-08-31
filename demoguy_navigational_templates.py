#!/usr/bin/env python

import sys
import os

import time
import datetime

import argparse
import traceback
import collections
import itertools

import touhouwiki.arrangement_cd
import touhouwiki.wikitext_utils

sys.path.append(os.path.join(
    os.path.abspath(os.path.dirname(__file__)),
    "pywikipedia",
))
import wikipedia
import catlib
import pagegenerators

default_category_name = "Category:" + touhouwiki.arrangement_cd.ArrangementCDParser.category_name

def normalize_title(title):
    return wikipedia.Page(None, title).title()

def get_pages(cat=None):
    if not cat:
        cat = default_category_name
    assert cat.startswith("Category:")

    pages = catlib.Category(wikipedia.getSite(), cat).articles()

    # TODO filter out pages tha don't belong to `default_category_name'
    # if `cat' is set
    # TODO could be done better with special generators

    return (page for page in pagegenerators.PreloadingGenerator(pages)
            if page.namespace() == 0 # only main namespace
    )

class NavigationalTemplateUpdater(object):
    LAST_RUN_FILE = "/var/run/navtemplates_lastrun.tmp"

    def __init__(self, dry_run, force, cat):
        self.dry_run = dry_run
        self.force = force
        self.cat = cat

        self.load_last_run()
        self.group_cats = collections.defaultdict(list)

    def on_album(self, page, cd):
        """Extracts required data for later batch update"""
        assert isinstance(page, wikipedia.Page)
        assert isinstance(cd, touhouwiki.arrangement_cd.ArrangementCD)
        
        for group_cat in cd.groupCats:
            group_cat = normalize_title("Category:" + group_cat)
            self.group_cats[group_cat].append((page, cd))

    def is_up_to_date(self, pagecds):
        last_album_change = max(
            page.editTime(datetime=True) for page, cd in pagecds)
        
        return self.last_run - last_album_change > datetime.timedelta(days=0.5) 

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
        template = wikipedia.Page(
            wikipedia.getSite(), u"Template:%s Albums" % group_cat)

        try:
            pagecds.sort(key=lambda pagecd: (pagecd[1].released, pagecd[1].catalogno))
        except Exception as e:
            traceback.print_exc()
            return
        
        new_text = self.generate_template(
            pagecds,
            template
        )

        if self.dry_run:
            print new_text
        else:
            template.put(new_text, u"updating", minorEdit=False) 

    def generate_template(self, pagecds, old_template):
        l = []
        
        if len(pagecds) > 1:
            try:
                old_dict = touhouwiki.wikitext_utils.find_template(old_template.get(get_redirect=True), "Navbox")
                if old_dict is None:
                    old_dict = {}
            except wikipedia.exceptions.NoPage:
                old_dict = {}
            
            l.append(u"{{Navbox\n")
            l.append(u"|name = {{subst:PAGENAME}}\n")

            l.append(u"|title = %s\n" % 
                (old_dict.get("title", "").strip() or u"{{subst:PAGENAME}}"))

            for k, v in old_dict.iteritems():
                if (k == "name" or
                    k == "title" or
                    k.startswith("group") or
                    k.startswith("list")):
                        continue
                
                l.append(u"|%s = %s\n" % (k.strip(), v.strip()))

            cur_idx = cur_year = 0
            for page, cd in pagecds:
                if cd.released.year > cur_year:
                    cur_year = cd.released.year
                    cur_idx += 1
                    l.append(u"\n")
                    l.append(u"|group%d = %d\n" % (cur_idx, cur_year))
                    l.append(u"|list%d = %s" % (cur_idx, self.get_link(page, cd)))
                else:
                    l.append(u" &bull; %s" % self.get_link(page, cd))

            l.append(u"\n}}\n")
       
        l.append(u"<noinclude>\n")
        l.append(u"[[Category:Arrange CDs navigational templates]]\n")
        l.append(u"</noinclude>");

        return u"".join(l)

    def get_link(self, page, cd):
        if page.title() == cd.title:
            return u"[[%s]]" % page.title()
        else:
            return u"[[%s | %s]]" % (page.title(), cd.title)

    def load_last_run(self):
        self.current_run = time.time()
        try:
            with open(self.LAST_RUN_FILE, 'r') as f:
                self.last_run = datetime.datetime.utcfromtimestamp(
                    float(f.readline())
                )
        except IOError:
            print >>sys.stderr, "couldn't load last run time"
            self.last_run = datetime.datetime(0, 0, 0)

    def save_last_run(self):
        with open(self.LAST_RUN_FILE, 'w') as f:
            print >>f, self.current_run
    

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("source", nargs="?",
        help="Category to load pages from")
    parser.add_argument("--dry", dest="dry_run", action="store_true")
    parser.add_argument("--force", dest="force", action="store_true")
    args = parser.parse_args()

    if args.source:
        args.source = normalize_title(args.source)

    parser = touhouwiki.arrangement_cd.ArrangementCDParser()
    
    updater = NavigationalTemplateUpdater(
        dry_run=args.dry_run, 
        force=args.force,
        cat=args.source)

    for page in get_pages(args.source):
        try:
            print page.title()
            cd = parser.parse_page(page.get())
        except Exception as exc:
            print exc
        else:
            updater.on_album(page, cd)

    updater.update_categories()
    
    if not args.dry_run and not args.source:
        updater.save_last_run()


if __name__ == "__main__":
    try:
        main()
    finally:
        wikipedia.stopme()
