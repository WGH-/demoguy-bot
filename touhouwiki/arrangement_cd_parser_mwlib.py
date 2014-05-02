import logging
import itertools
import datetime

import mwlib
import mwlib.uparser # for some reason, this import is neccessary
import mwlib.parser
import mwlib.refine.core
import mwlib.templ.misc 

from .arrangement_cd import ArrangeCD, Song, SongSource

from . import arrangement_cd_parser
from . import templates
from . import wikitext_utils_mwlib as wikitext_utils

class MWLibParser(arrangement_cd_parser.ArrangementCDParser):
    def __init__(self):
        self.wikidb = WikiDB()
        self.logger = logging.getLogger("touhohwiki.arrangement_cd_parser_mwlib.MWLibParser")

    def parse_page(self, text):
        # XXX see https://sourceforge.net/tracker/index.php?func=detail&aid=3563812&group_id=93107&atid=603138
        text = text.replace("\r\n", "\n")

        template = wikitext_utils.find_template(text, self.template_name)

        if not template:
            raise ValueError("couldn't find template %s" % self.template_name)

        return self.parse_music_article(template)

    def parse_music_article(self, template):
        sanitize_text = self.sanitize_text
        sanitize_text_jp = self.sanitize_text_jp
        
        cd = ArrangeCD()

        cd.group = sanitize_text(template["group"])
        cd.groupjp = sanitize_text_jp(template["group"])

        cd.titlejp = sanitize_text(template.get("titlejp", "")) or None
        cd.titlejprom = sanitize_text(template.get("titlejprom", "")) or None
        cd.titleen = sanitize_text(template.get("titleen", "")) or None
        
        cd.title = cd.titlejp or cd.titleen or cd.titlejprom
        
        cd.groupCats.append(
            sanitize_text(template.get('groupCat')) or cd.group        
        )
        
        for i in itertools.count(2):
            try:
                cat = sanitize_text(template["groupCat%d" % i])
                if cat:
                    cd.groupCats.append(cat)
            except KeyError:
                break
        
        try:
            cd.released = self.parse_date(sanitize_text(template['released']))
        except ValueError:
            self.logger.error("couldn't parse release date %r" % template.get("released"))
            cd.released = None
        
        cd.catalogno = sanitize_text(template.get('catalogno')) or None
        
        try:
            tracklist = "== %s ==\n%s" % (self.tracks_section_name, template["tracklist"])
        except KeyError:
            raise ValueError("template doesn't have 'tracklist' argument")

        tracklist = self.expand_templates(tracklist)
        tracklist = mwlib.uparser.parseString("", tracklist, self.wikidb)
        
        walknode = mwlib.refine.core.walknode
        # note: unlike HTML, mwlib believes that everything
        # below heading is its child
        for section in walknode(tracklist, 
                lambda x: x.tagname == "@section"):
            section_name = section.children[0].children[0].caption.strip()
            if section_name == self.tracks_section_name:
                #for track in self.find_tracks(section):
                #    cd.tracks.append(track)
                cd.tracks.extend(self.find_tracks(section))
                break # ignore other sections
        
        return cd

    def find_tracks(self, section):
        nodes = mwlib.parser.nodes

        for songlist in self.find_songlists(section):
            for song in songlist.children:
                if not isinstance(song, nodes.Item):
                    continue
                
                o = Song()

                s = wikitext_utils.sanitize_nodes(song.children[0]).strip()
                if s == "Return to List by Groups":
                    # one could encounter that in Infobox Music articles
                    break

                try:
                    track, title, length = self.parse_song_title(s)
                except ValueError as exc:
                    logging.error("couldn't parse song title %r (%r)", s, exc)
                    continue # still try to continue

                o.title = title
                o.length = length
                
                try:
                    assert isinstance(song.children[1], nodes.ItemList)
                except IndexError:
                    pass # often there is no info
                else:
                    for item in song.children[1].children:
                        if not isinstance(item, nodes.Item):
                            continue
                        self.parse_song_info(item, o)

                # XXX hack
                if o.sources:
                    if not o.sources[-1].game and not o.sources[-1].titles:
                        o.sources.pop()

                yield o 
    

    def find_songlists(self, section, f=False):
        nodes = mwlib.parser.nodes

        for x in section.children:
            if isinstance(x, nodes.ItemList):
                yield x
            else:
                for y in self.find_songlists(x):
                    yield y

    def parse_song_info(self, item, song):
        nodes = mwlib.parser.nodes

        # do not allow nested lists
        # XXX modifies item, bad thing
        # XXX in fact, I can't remeber why it's even necessary
        item.children = [i for i in item.children 
                if not isinstance(i, nodes.ItemList)]

        item = wikitext_utils.sanitize_nodes(item).strip()

        try:
            key, value = [s.strip() for s in item.split(':', 1)]
        except ValueError:
            # not "key: value" string
            if not song.translated_title:
                # XXX should check for italics instead
                song.translated_title = item
            else:
                self.logger.warn("bad value %r", item)
        else:
            value = " ".join(value.split())

            if key == "arrangement":
                song.arrangement.extend(self.list_from_string(value))
            elif key == "lyrics":
                song.lyrics.extend(self.list_from_string(value))
            elif key == "vocals":
                song.vocals.extend(self.list_from_string(value))
            elif key == "composition":
                pass # XXX
            elif key == "guitar":
                pass # XXX
            elif key == "co-arrangement":
                pass # XXX
            # XXX other fields
            
            elif key == "original title":
                if not song.sources:
                    song.sources.append(SongSource())

                song.sources[-1].titles.append(value)

            elif key == "source":
                try:
                    song.sources[-1].game = value
                except IndexError:
                    song.sources.append(SongSource())
                    song.sources[-1].game = value
                
                song.sources.append(SongSource())

            else:
                self.logger.info("bad key %r", key) 

    def parse_date(self, s):
        # remove convention links
        try:
            s = s[:s.index("(")].strip()
        except ValueError:
            pass
        
        formats = (
            "%Y/%m/%d",
            "%Y-%m-%d",
        )
        
        for fmt in formats:
            try:
                return datetime.datetime.strptime(s, fmt).date()
            except ValueError:
                pass

        raise ValueError("couldn't parse date %r" % s)
    
    def parse_song_title(self, text):
        for re_ in self.song_title_re:
            m = re_.search(text)
            if m: break
        else:
            raise ValueError("cannot parse song title %r" % text)

        d = m.groupdict()

        track = None
        title = d['title'].strip()
        length = d.get('length')

        if length: length = length.strip()

        return track, title, length

    def expand_templates(self, text):
        te = mwlib.expander.Expander(text, wikidb=self.wikidb)
        text = te.expandTemplates()
        return text

    def sanitize_text(self, text, inline=False):
        return wikitext_utils.sanitize_text(text, self.wikidb, inline)

    def sanitize_text_jp(self, text, inline=False):
        return wikitext_utils.sanitize_text_jp(text, self.wikidb, inline)
    
    @staticmethod
    def list_from_string(s, delimiter=','):
        return [s.strip() for s in s.split(delimiter)]
    
class WikiDB(object):
    __siteinfo = {
        "general": {},
        "interwikimap": [],
        "namespaces": {
            "0": {"*": "", "content": "", "id": 0},
        },
    }
    def __init__(self):
        self.nshandling = mwlib.nshandling.get_nshandler_for_lang("en")
        self.d = {
            self.nshandling.get_fqname(k) : v  for
            k, v in templates.templates.iteritems()
        }

    def get_siteinfo(self):
        return self.__siteinfo

    def normalize_and_get_page(self, title, defaultns=0):
        title = self.nshandling.get_fqname(title)
        return mwlib.templ.misc.page(self.d.get(title, u""))

    def getURL(self, *args, **kwargs):
        # XXX 
        return ""
