#######################
from __future__ import print_function, unicode_literals

import codecs
import socket
import struct

# set unicode piping/output:
import sys
import time
from optparse import make_option

from django.conf import settings
from django.utils.encoding import force_text

from ..models import Computer, IPAddress

#######################
"""
Send WakeOnLan packets to either computer or IP addresses.
"""
#######################################################################

HELP_TEXT = __doc__.strip()
DJANGO_COMMAND = "main"
OPTION_LIST = (
    make_option(
        "-c",
        "--computer",
        dest="computer",
        action="store_true",
        default=False,
        help="Specify wake on lan targets by computer primary keys (default is search)",
    ),
    make_option(
        "-a",
        "--ipaddress",
        dest="ipaddress",
        action="store_true",
        default=False,
        help="Specify wake on lan targets by IP address (default is search)",
    ),
)
ARGS_USAGE = "[pk ...]"

#######################################################################

sys.stdout = codecs.getwriter("utf-8")(sys.stdout)

#######################################################################


def send_magic_packet(macaddress, ipaddr=None, verbose=False):
    """ 
    Switches on remote computers using WOL. 
    """
    # Check macaddress format and try to compensate.
    if len(macaddress) == 12:
        pass
    elif len(macaddress) == 12 + 5:
        sep = macaddress[2]
        macaddress = macaddress.replace(sep, "").lower()
    else:
        raise ValueError("Incorrect MAC address format: {0!r}".format(macaddress))

    # Pad the synchronization stream.
    data = "".join(["FFFFFFFFFFFF", macaddress * 20])
    send_data = ""

    # Split up the hex values and pack.
    for i in range(0, len(data), 2):
        send_data = "".join([send_data, struct.pack("B", int(data[i : i + 2], 16))])

    if verbose:
        print("[localhost] sending wake-on-lan magic packet with payload:", macaddress)

    # Broadcast it to the LAN.
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    if ipaddr is None:
        ipaddr = "<broadcast>"
    sock.sendto(send_data, (ipaddr, 7))


#######################################################################


def wake_object(obj):
    """
    Figure out associated networkinterface and necessary MAC info.
    """
    iface_list = obj.networkinterface_set.active()
    if len(iface_list) == 1:
        iface = iface_list[0]
    elif len(iface_list) > 1:
        iface = iface_list.primary()[0]
    else:
        print("No active interface for {0}.".format(obj))
        return

    print("Waking {0}".format(obj, type(obj)))
    send_magic_packet(iface.mac_address.strip(), verbose=True)


#######################################################################


def main(options, args):
    """
    Do it.
    """
    if sum([int(options["computer"]), int(options["ipaddress"])]) > 1:
        print("You must specify either --computer or --ipaddress, but not both")
        return
    if options["computer"]:
        object_list = Computer.objects.filter(pk__in=args)
    elif options["ipaddress"]:
        object_list = IPAddress.objects.filter(pk__in=args)
    else:
        object_list = Computer.objects.active().search(*args)
    for o in object_list:
        wake_object(o)
        time.sleep(0.25)


#######################################################################
