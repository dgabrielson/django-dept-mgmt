#!/usr/bin/env python
#######################
from __future__ import print_function, unicode_literals

from .. import get_page


#######################
"""
brother_printer.status

Collect information from a brother printer by accessing
/printer/maininfo.html
/printer/main.html

"""


def get_status(address):
    url = "http://" + address + "/printer/main.html"
    page = get_page.get_page(url)
    chunks = get_page.get_chunks(page, "<td NOWRAP><TT>", "</TT></td>")
    assert len(chunks) == 2  # unexpected result.
    # text = get_page.strip_html(chunks[0])
    # status0 = brother_unquote(text)  # strips out all the non-breaking spaces
    statuses = [brother_unquote(get_page.strip_html(chunk)) for chunk in chunks]
    # status = ' '.join(statuses).strip()
    status = statuses[0]
    return status


def get_drum_pages_left(info):
    drum_pages_left = None
    if drum_pages_left is None:
        try:
            drum_pages_left = int(
                info["* Drum Information"]["Estimated Pages Remaining"].split()[0]
            )
        except KeyError:
            pass
    if drum_pages_left is None:
        try:
            drum_pages_left = int(info["Remaining Life"]["*Drum Unit"].split()[0])
        except KeyError:
            pass
    if drum_pages_left is None:
        try:
            drum_pages_left = int(info["Remaining Life"]["* Drum Unit"].split()[0])
        except KeyError:
            pass
    assert (
        drum_pages_left is not None
    )  # could not find drum page count (check info dictionary)
    return drum_pages_left


def get_model(info):
    desc = None
    if not desc:
        try:
            desc = info["Node Information"]["Printer Type"]
        except KeyError:
            pass
    if not desc:
        try:
            desc = info["Node Information"]["Model Name"]
        except KeyError:
            pass

    assert desc  # could not find printer model description (check info dictionary)
    return desc


def brother_unquote(s):
    result = s
    while True:
        i = result.find("&#")
        if i == -1:
            break
        j = result.find(";", i)
        if j == -1:
            break
        c = int(result[i + 2 : j])
        result = result[:i] + chr(c) + result[j + 1 :]

    return result.replace("&nbsp;", " ").strip()


def get_maininfo(address):
    url = "http://" + address + "/printer/maininfo.html"
    page = get_page.get_page(url)
    tables = get_page.extract_tables_from_text(page)
    assert len(tables) == 5  # unexpected result.
    table = tables[3]  # 0--1 are config, 2 is the header, 4 is the footer
    rows = get_page.get_chunks(table, "<TR ", "</TR>")
    results = {}
    for row in rows:
        tds = get_page.get_chunks(row, "<TD", "</TD>")
        data = [brother_unquote(get_page.strip_html(elem)) for elem in tds]
        if len(data) == 1:
            header = data[0]
            results[header] = {}
        elif len(data) == 2:
            results[header][data[0]] = data[1]
        else:  # error history
            if len(data) % 2:  # odd length
                data = data[:-1]  # truncate the last one
            i = 0
            while i < len(data):
                results[header][data[i]] = data[i + 1]
                i += 2
    return results


def main(address):
    """
    Take the address of a printer, and return it's status and info.
    """
    status = get_status(address)
    info = get_maininfo(address)
    return status, info


if __name__ == "__main__":
    import pprint
    import sys

    for arg in sys.argv[1:]:
        data = main(arg)
        pprint.pprint(data)

#
