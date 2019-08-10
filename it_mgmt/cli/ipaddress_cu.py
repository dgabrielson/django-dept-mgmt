#######################
from __future__ import print_function, unicode_literals

import socket

from ..models import IPAddress

#######################
"""
Create or update one or more IPAddress objects.

Each argument is either a hostname or ip address to create or update.
(Remaining information is supplied by DNS information.)
"""
#######################################################################

HELP_TEXT = __doc__.strip()
DJANGO_COMMAND = "main"
OPTION_LIST = ()
ARGS_USAGE = "addr [addr ...]"

#######################################################################

#######################################################################


def get_details(addr):
    """
    ``addr`` may be a name, but it doesn't matter. Probe DNS via
    the socket library to get a 
    ``hostname, alias_list, ipaddress_list`` triple
    """
    hostname, alias_list, ipaddress_list = socket.gethostbyaddr(addr)
    try:
        hostname, alias_list, ipaddress_list = socket.gethostbyname_ex(hostname)
    except socket.gaierror:
        pass
    return hostname, alias_list, ipaddress_list


#######################################################################


def create_or_update(addr, verbosity):
    """
    Actually do the create or update.
    """
    hostname, alias_list, ipaddress_list = get_details(addr)
    for number in ipaddress_list:
        update_info = {"hostname": hostname, "aliases": " ".join(alias_list)}
        ipaddress, created = IPAddress.objects.get_or_create(
            number=number, defaults=update_info
        )
        if not created:
            for f in update_info:
                setattr(ipaddress, f, update_info[f])
            ipaddress.save()
            if verbosity > 0:
                print(ipaddress, "updated")
        else:
            if verbosity > 0:
                print(ipaddress, "created")


#######################################################################


def main(options, args):
    """
    Create or update ip addresses indicated by args.
    """
    verbosity = int(options["verbosity"])
    for arg in args:
        create_or_update(arg, verbosity)


#######################################################################
