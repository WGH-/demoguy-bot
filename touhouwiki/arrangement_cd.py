# encoding: utf-8

class ArrangementCD(object):
    __slots__ = (
        "title",
        "titleen",
        "titlejp",
        "titlejprom",
        "group",
        "groupjp",
        "groupCats",
        "tracks",
        "released",
        "catalogno"
    )

    def __init__(self):
        self.tracks = []
        self.groupCats = []

ArrangeCD = ArrangementCD # legacy alias

class Song(object):
    __slots__ = (
        "title",
        "length",
        "translated_title",
        "arrangement",
        "lyrics",
        "vocals",
        "sources"
    )

    def __init__(self):
        self.translated_title = None
        self.arrangement = []
        self.lyrics = []
        self.vocals = []
        self.sources = []

class SongSource(object):
    __slots__ = (
        "game",
        "titles"
    )

    def __init__(self):
        self.game = None
        self.titles = []

    def __nonzero__(self):
        return bool(self.titles)

    def __repr__(self):
        if self.game:
            return "<SongSource %r>" % self.game
        else:
            return "<SongSource EMPTY>"


