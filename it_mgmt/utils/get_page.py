#!/usr/bin/env
#######################
from __future__ import print_function, unicode_literals

import glob
import os

#######################
"""
get_page.py

Provides the function get_page(url) and support functions.
"""

try:
    # Python 3:
    from urllib.request import urlopen
except ImportError:
    # Python 2:
    from urllib2 import urlopen


def get_page(url):
    """
    get_page(url) -> <string>

    Returns the contents of the given url.
    Returns None if an error was encountered during fetching.
    """
    myurl = url.replace("&amp;", "&")
    try:
        fd = urlopen(myurl)
        if fd:
            txt = fd.read()
            return txt
        else:
            return None
    except AttributeError:
        return None


def strip_html(html):
    txt = ""
    pos = 0
    while True:
        start = html.find("<", pos)
        if start == -1:
            txt += html[pos:]
            break
        txt += html[pos:start]
        stop = html.find(">", start)
        if stop == -1:
            break
        pos = stop + 1
        txt += " "
    return txt.strip()


def check_term(text, term, idx):
    """
    check_term(text, term, idx) -> <boolean>

    Check that the term occuring in text at position idx
    has non-alphanumeric characters on each side.
    If this is not true, then it is most likely part of
    a larger word.
    """
    if text[idx - 1].isalnum():
        return False
    if text[idx + len(term)].isalnum():
        return False
    return True


def extract_rows(url, search_keys):
    """
    extract_rows(url, search_keys) -> <list>

    Assume that search_keys are terms that appear in table rows.
    Returns the raw page rows that have search_keys in them.

    NOTE: do not modify this to use get_chunks() without careful
        THOUGHT and CONSIDERATION.
        This routine does a few things which are more optimal for
        search keys.
    """
    TR_START_TOKEN = "<tr>"
    TR_END_TOKEN = "</tr>"
    result = []
    hits = []
    page = get_page(url)
    lpage = page.lower()
    for key in search_keys:
        lkey = key.lower()
        idx = -1
        while True:
            idx = lpage.find(lkey, idx + 1)
            if idx == -1 or idx in hits:
                break
            hits.append(idx)
            if check_term(lpage, lkey, idx):
                tr_start = lpage.rfind(TR_START_TOKEN, 0, idx)
                tr_end = lpage.find(TR_END_TOKEN, idx)
                if tr_start != -1 and tr_end != -1:
                    row = (
                        page[tr_start : tr_end + len(TR_END_TOKEN)]
                        .replace("&nbsp;", " ")
                        .replace("\n", " ")
                        .replace("\r", " ")
                    )
                    result.append(row)
                idx = max([idx, tr_start, tr_end])
    return result


def get_chunks(text, start_tok, end_tok):
    """
    get_chunks(text, start_tok, end_tok) -> <list>

    Given the text, return a list of chunks delimited by
    (and including) the start_ and end_tok(en)s.
    """
    ltext = text.lower()
    idx = -1
    result = []
    while True:
        start = ltext.find(start_tok.lower(), idx + 1)
        if start == -1:
            break
        end = ltext.find(end_tok.lower(), start + len(start_tok))
        if start != -1 and end != -1:
            chunk = text[start : end + len(end_tok)]
            result.append(chunk)
        idx = max([idx, start, end])  # sanity

    return result


def extract_tables_from_text(text):
    """
    extract_tables(url) -> <list>

    Return a list of the table envinronments in the page.
    """
    START_TOKEN = "<table"
    END_TOKEN = "</table>"
    result = get_chunks(text, START_TOKEN, END_TOKEN)
    return result


def extract_tables(url):
    """
    extract_tables(url) -> <list>

    Return a list of the table envinronments in the page at url.
    """
    page = get_page(url)
    result = extract_tables_from_text(page)
    return result


def extract_hrefs_from_text(page, proto_filter=None):
    """
    extract_hrefs_from_page(page, proto_filter= None) -> <list>

    Extract all the href links from the given page text.
    If proto_filter is given, filter out anything that DOES NOT
    match this list of terms.
    Returns the href targets as a list.
    """
    result = []
    lpage = page.lower()
    idx = -1
    while True:
        idx = lpage.find("href=", idx + 1)
        if idx == -1:
            break
        idx += len("href=")  # maybe +1 ?
        delim = lpage[idx]
        stop = lpage.find(delim, idx + 1)
        if stop != -1:
            target = page[idx + 1 : stop]
            result.append(target)

    # result now contains ALL hrefs. Filter them
    if proto_filter:
        for pf in proto_filter:
            result = filter(lambda x: x.lower().startswith(pf.lower()), result)

    return result


def extract_hrefs(url, proto_filter=None):
    """
    extract_hrefs(url, proto_filter= None) -> <list>

    Extract all the href links from the given url.
    If proto_filter is given, filter out anything that DOES NOT
    match this list of terms.
    Returns the href targets as a list.
    """
    page = get_page(url)
    return extract_hrefs_from_text(page, proto_filter)


def filter_check_terms(s, terms):
    for t in terms:
        i = s.lower().find(t.lower())
        if i == -1:
            continue
        if check_term(s, t, i):
            return True


def filter_rows(rows, term):
    """
    filter_rows(rows, term) -> <list>

    Return only rows that have term in them.
    """
    if type(term) == type(""):
        lterm = term.lower()
        return filter(lambda r: r.lower().find(lterm) != -1, rows)
    elif type(term) == type([]):
        return filter(lambda r: filter_check_terms(r, term), rows)
    else:
        import exceptions

        raise exceptions.Exception("Unimplemented execution path")


def unescape_html(s):
    """
    unescape_html(string) -> <string>

    Resolve character sequences such as &amp; and &#039;
    """
    fixes = {"gt": ">", "lt": "<", "amp": "&"}
    result = s
    i = 0
    while True:
        i = result.find("&", i)
        j = result.find(";", i)
        if i == -1 or j == -1:
            break  # done
        if j - i > 6:  # to far apart, ignore
            i += 1
            continue
        code = result[i + 1 : j]
        if code.startswith("#"):
            # numerical expansion
            try:
                value = chr(int(code[1:].lstrip("0")))
            except:
                value = None
        else:
            value = fixes.get(code, None)
        if value:
            result = result[:i] + value + result[j + 1 :]
        i += 1
    return result
