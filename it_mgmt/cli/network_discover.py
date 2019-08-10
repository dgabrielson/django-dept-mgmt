#######################
from __future__ import print_function, unicode_literals

import socket

from netaddr import IPNetwork

from .ipaddress_cu import get_details

#######################
"""
Probe for ip addresses and hostnames on the given network(s).

This utility is designed to be used in a pipeline with ipaddress_cu:

./manage.py it_mgmt network_discover 130.179.24.0/22 | grep stats.uman | cut -f 1 | xargs ./manage.py it_mgmt ipaddress_cu
"""
################################################################

HELP_TEXT = __doc__.strip()
DJANGO_COMMAND = "main"
OPTION_LIST = ()
ARGS_USAGE = "IP/CIDR [IP/CIDR ...]"

################################################################

################################################################


def discover(ip_cidr, verbosity):
    """
    verbosity fields:
        0 - ipaddress only
        1 - ipaddress hostname
        2 - ipaddress hostname aliases
    """
    network = IPNetwork(ip_cidr)
    ip_list = list(network)[1:-1]
    for ip in ip_list:
        number = ip.format()
        try:
            hostname, alias_list, ipaddress_list = get_details(number)
        except (socket.herror, socket.gaierror):
            hostname = "<unknown>"
            alias_list = []
            ipaddress_list = [number]
        for ipaddr in ipaddress_list:
            line = ipaddr
            if verbosity > 0:
                line += "\t" + hostname
            if verbosity > 1:
                line += "\t" + " ".join(alias_list)
            print(line)


################################################################


def main(options, args):
    verbosity = int(options["verbosity"])
    for arg in args:
        discover(arg, verbosity)


################################################################
