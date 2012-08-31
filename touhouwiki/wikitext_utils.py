import re

import itertools
import functools

import unicodedata

import mwlib
import mwlib.uparser # for some reason, this import is neccessary
import mwlib.parser
import mwlib.refine.core
import mwlib.refine.compat
import mwlib.nshandling
import mwlib.templ.parser
import mwlib.templ.nodes
import mwlib.expander

def find_template(text, template_name, wikidb=None, expand=False):
    """Extracts a template from a text.

    Arguments:
    text - source text
    template_name - template name
    wikidb - used for further expansion if expand is True
    expand - expand template calls in subject template's arguments
    """
    template_name = template_name.strip()
    if not wikidb:
        wikidb = mwlib.expander.DictDB()

    m = re.search("{{\s*" + template_name, text)
    if m == None:
        return None
    
    i = m.start()
    j = m.end()
    s = text[m.end():]

    nested = 1

    while nested > 0:
        m = re.search("(?:{{|}})", s)
       
        if not m:
            raise ValueError, "cannot find template closing"

        if m.group(0) == "{{":
            nested += 1
        else:
            nested -= 1
        s = s[m.end():]
        j += m.end()
        
    template = mwlib.templ.parser.parse(text[i:j])
    te = mwlib.expander.Expander("", wikidb=wikidb)

    args = mwlib.expander.get_template_args(template, te)

    d = {}
    
    counter = itertools.count(start=1)

    for x in args.args:
        if isinstance(x, tuple):
            # ('Released', '=', '2009/03/08')
            
            if expand:
                x = map(te._expand, x)
            else:
                x = map(fold_templates, x)

            k = x[0]
            v = "".join(x[2:])
            
            k = k.strip()

            d[k] = v
        else:
            if expand:
                x = te._expand(x)
            else:
                x = fold_templates(x)

            d[unicode(next(counter))] = x

    return d

def fold_templates(x):
    """"""
    if isinstance(x, mwlib.templ.nodes.Template):
        buf = []
        for arg in x:
            if isinstance(arg, tuple):
                # argument tuple
                arg = map(fold_templates, arg)
                buf.extend(arg)
            else:
                buf.append(arg)
        return "{{%s}}" % "|".join(buf)
    elif isinstance(x, tuple):
        return "".join(map(fold_templates, x))
    else:
        return x


def sanitize_text_jp(text, wikidb=None, inline=False):
    """Special version of sanitize_text, uses the second
    argument (Japanese) of Nihongo template"""

    if not wikidb:
        wikidb = mwlib.expander.DictDB()

    try:
        old_nihongo = wikidb.d["Nihongo"]
    except KeyError:
        has_key = False
    else:
        has_key = True

    
    wikidb.d["Nihongo"] = "{{{2|}}}"
    try:
        return sanitize_text(text, wikidb, inline)
    finally:
        if has_key:
            wikidb.d["Nihongo"] = old_nihongo

def sanitize_text(text, wikidb=None, inline=False):
    """Expands templates and removes markup"""
    if not text: return text

    if inline:
        text = "<span>%s</span>" % text

    if not wikidb:
        wikidb = mwlib.expander.DictDB()
    
    te = mwlib.expander.Expander(text, wikidb=wikidb)
    text = te.expandTemplates()

    xopts = mwlib.refine.core.XBunch()
    xopts.expander = mwlib.expander.Expander("", "pagename", wikidb=wikidb)
    xopts.nshandler = mwlib.nshandling.nshandler(wikidb.get_siteinfo())

    parsed = mwlib.refine.core.parse_txt(text, xopts)
    mwlib.refine.compat._change_classes(parsed)

    s = sanitize_nodes(parsed).strip()

    return s

def sanitize_nodes(nodes_):
    """Given an iterable of nodes, returns plain text
    without links, images, etc."""
    l = [] 
    nodes = mwlib.parser.nodes

    for node in mwlib.refine.core.walknode(nodes_):
        if isinstance(node, nodes.Text):
            l.append(node.caption)
        elif isinstance(node, nodes.Link):
            if not node.children:
                l.append(node.caption or node.target)
        elif isinstance(node, nodes.NamedURL):
            if not node.children:
                l.append(node.caption or node.target)

    return u_normalize(u"".join(l))

u_normalize = functools.partial(unicodedata.normalize, "NFC")
