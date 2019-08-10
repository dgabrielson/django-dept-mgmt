#######################
from __future__ import print_function, unicode_literals

import codecs

# set unicode piping/output:
import sys
from optparse import make_option

from office_mgmt.cli.asset_copy import asset_copy, copy_obj

from ..models import Computer, NetworkInterface

#######################
"""
Copy an asset record to a new asset; duplicating any associated information,
including the associated asset, if any.
"""
#######################################################################

HELP_TEXT = __doc__.strip()
DJANGO_COMMAND = "main"
OPTION_LIST = (
    make_option(
        "-c",
        "--common-name",
        help="Supply a new common name for the computer (optional)",
    ),
    make_option(
        "-i",
        "--iface",
        help="name0,type0,mac_address0[;name1,type1,address1[;...]] Supply network interface information for the computer (optional)",
    ),
    make_option(
        "-s",
        "--serial",
        help="Supply the serial number for the new asset (required if there is an associated asset)",
    ),
)
ARGS_USAGE = "[pk]"

#######################################################################

sys.stdout = codecs.getwriter("utf-8")(sys.stdout)

#######################################################################

EXCLUDE_FIELDS = [
    "api_key",
    "licence_set",
    "networkinterface_set",
    "status_set",
    "worknote_set",
    "asset",
]
NETWORK_TYPE_CODES = [p[0] for p in NetworkInterface.TypeChoices]
NETWORK_TYPE_ERROR_MSG = "The type code for an interface must be one of: "
NETWORK_TYPE_ERROR_MSG += ", ".join(
    [
        "{0} ({1})".format(code, display)
        for code, display in NetworkInterface.TypeChoices
    ]
)
NETWORK_TYPE_ERROR_MSG += " ."

#######################################################################


def computer_copy(src, iface_list=None, serial_number=None, **kwargs):
    """
    Copy the ``src`` Computer, including all related information.
    ``serial_number`` is required if the computer has an asset, and ``kwargs`` are other values to update.
    """
    if src.asset and not serial_number:
        print("A serial number is required for the new asset")
        return
    if not src.asset and serial_number:
        print("There is no asset -- do not supply a serial number")
        return
    if iface_list is None:
        iface_list = []

    dst = copy_obj(src, kwargs)
    if src.asset:
        dst.asset = asset_copy(src.asset, serial_number)
        dst.save()

    first = True
    for name, type, mac_address in iface_list:
        NetworkInterface.objects.create(
            primary=first, name=name, type=type, mac_address=mac_address, computer=dst
        )
        if first:
            first = False
    return dst


#######################################################################


def decode_mac_addr(s):
    r = ""
    count = 0
    for c in s:
        r += c
        count += 1
        if count % 2 == 0:
            r += ":"
    return r.rstrip(":").lower()


#######################################################################


def parse_iface_list(string):
    """
    Take the command line iface parameter value
    name0,type0,mac_address0[;name1,type1,address1[;...]]
    and processes into a list of triples.
    """
    if not string:
        return []
    results = []
    parts = string.split(";")
    for part in parts:
        iface = part.split(",")
        assert (
            len(iface) == 3
        ), "You must supply a name,type,mac_address triple for each network interface"
        iface[1] = iface[1][0]
        assert iface[1] in NETWORK_TYPE_CODES, NETWORK_TYPE_ERROR_MSG
        if "-" in iface[2]:
            iface[2] = iface[2].replace("-", ":")
        if ":" not in iface[2]:
            iface[2] = decode_mac_addr(iface[2])
        results.append(iface)
    return results


#######################################################################


def main(options, args):
    verbosity = int(options.get("verbosity", 1))
    serial_number = options.get("serial", None)
    common_name = options.get("common_name", None)
    iface_list = parse_iface_list(options.get("iface", None))

    if len(args) != 1:
        print("Only one source object can be copied.")
        return
    pk = args[0]
    src = Computer.objects.get(pk=pk)

    kwargs = {}
    if common_name:
        kwargs["common_name"] = common_name
    dst = computer_copy(
        src, iface_list=iface_list, serial_number=serial_number, **kwargs
    )
    if verbosity > 0:
        print(src, "copied")
    if verbosity > 2:
        print("\t new id =", dst.pk)


#######################################################################
