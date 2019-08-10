#######################
from __future__ import print_function, unicode_literals

import sys
from optparse import make_option

from ..models import Computer

#######################
"""
Generate the text for an IP Management request.
Email this to Khosrow Hakimzadeh.
"""

DJANGO_COMMAND = "entrypoint"
HELP_TEXT = __doc__.strip()
OPTION_LIST = (
    make_option("--pk", action="store_true", help="Specify terms are primary keys"),
)
ARGS_USAGE = "<--pk> term <term ...>"

search_fields = ["common_name"]


def search(term):
    results = []
    for field in search_fields:
        results += list(Computer.objects.filter(**{"%s__icontains" % field: term}))
    return results


def main(term, primary_keys=False):
    if primary_keys:
        results = Computer.objects.filter(pk__in=term)
    else:
        results = search(term)
    if len(results) == 0:
        print("*** no results of search")
        return

    for comp in results:
        iface = comp.get_primary_net_iface()
        print("IP Address:", iface.ip_address.number)
        print("MAC Address:", iface.mac_address)
        wifi_list = comp.networkinterface_set.active().wifi()
        if wifi_list.count() == 1:
            wifi = wifi_list.get()
            if wifi.mac_address:
                print("Wifi MAC:", wifi.mac_address)
        if comp.asset:
            if comp.asset.serial_number:
                print("Serial Number:", comp.asset.serial_number)
            if comp.asset.security_id:
                print("Security ID:", comp.asset.security_id)
        print()
        print("Hardware:", comp.hardware)
        print("OS:", comp.operating_system)
        if comp.room:
            print("Room:", comp.room)
        if comp.person:
            print("Person:", comp.person)
        # notes_lines = comp.notes.split('\n')
        print()


def entrypoint(options, args):
    if "pk" in options and options["pk"]:
        main(args, True)
        return
    for arg in args:
        main(arg)


#
