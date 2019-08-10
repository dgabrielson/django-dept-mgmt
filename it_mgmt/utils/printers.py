#######################
from __future__ import print_function, unicode_literals

import cPickle as pickle
import json
import os
from datetime import datetime

#######################
"""
Utilities for dealing with printers, specifically.
"""
######################################################################

# from django.utils.timezone import (now, make_aware, get_current_timezone,
#                                    make_naive, is_aware, is_naive)
now = datetime.now

######################################################################

# Consider making this file configurable, eventually...
PAGE_DATA = os.path.expanduser("~/.printer_page_counts.dat")

######################################################################


def _get_status_module(computer):
    if "brother" in computer.hardware.lower():
        from .brother_printer import status

        return status
    print(
        "WARNING",
        'Could not determine status for hardware: "{0}"'.format(computer.hardware),
    )


######################################################################


def get_status(computer):
    """
    status = printers.get_status(computer)
    """
    printer_info = _get_status_module(computer)
    hostname = computer.get_primary_net_iface().ip_address.hostname
    try:
        return printer_info.main(hostname)
    except Exception as e:
        return e, None


#######################################################################


def _get_elapsed_hours(dt):
    """
    From the old timestamp, get the elapsed time.
    """
    elapsed = now() - dt
    hours = int(round(float(elapsed.seconds) / (60 ** 2)))
    return hours


#######################################################################


def pprint_status(computer, result, verbosity):
    """
    printers.pprint_status(computer, status, verbosity)
    """
    old_page_data = None
    if os.path.exists(PAGE_DATA):
        timestamp, old_page_data = pickle.load(file(PAGE_DATA, "r"))

    if old_page_data is not None:
        hours = _get_elapsed_hours(timestamp)

    key = computer.common_name.lower()
    status, info = result

    if not info:
        try:
            error_msg = status.strerror.args[1]  # socket error
        except:
            error_msg = str(status)  # some other error
        print(computer.common_name + "\n\t" + error_msg.upper())
        return None, None

    printer_info = _get_status_module(computer)

    page_count = int(info["Device Status"]["Page Count"])
    drum_pages_left = printer_info.get_drum_pages_left(info)

    line = computer.common_name + "\t" + printer_info.get_model(info) + "\n"
    line += "\t" + status

    if drum_pages_left < 1:
        # drums usually continue to work past their estimated end-of-life
        drum_msg = ", REPLACE DRUM"
    else:
        drum_msg = ""
    line += drum_msg

    page_msg = ""
    if old_page_data and old_page_data.has_key(key):
        old_status, old_page_count = old_page_data[key]
        diff_pages = page_count - old_page_count
        page_msg += "%d pages" % diff_pages
        if hours < 24:
            page_msg += " today"
        elif hours < 7 * 24:
            page_msg += " since "
            if hours == 24:
                page_msg += "yesterday"
            else:
                page_msg += timestamp.strftime("%A")
        else:
            page_msg += " since " + timestamp.strftime("%Y-%b-%d")
        page_msg += " (%d total)" % page_count
    else:
        page_msg += "%d pages" % page_count
    line += "\t" + page_msg
    if save_pages:
        line = computer.common_name + "\t" + page_msg
    if verbosity > 0:
        print(line, end=" ")
    if verbosity > 1:
        print(" \t{0}".format(status), end=" ")
    if verbosity > 0:
        print()
    if verbosity > 2:
        print(json.dumps(info, indent=4))

    return key, (status, page_count)


#######################################################################


def save_pages(pages):
    """
    printers.save_pages(status_list)
    """
    data = (now(), pages)
    pickle.dump(data, file(PAGE_DATA, "w"))


#######################################################################
