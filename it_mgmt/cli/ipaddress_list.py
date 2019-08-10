#######################
from __future__ import print_function, unicode_literals

import codecs

# set unicode piping/output:
import sys
from optparse import make_option

from django.conf import settings
from django.utils.encoding import force_text

from ..models import IPAddress as Model

#######################
"""
Generate a list of IPAddress objects.
"""
#######################################################################

HELP_TEXT = __doc__.strip()
DJANGO_COMMAND = "main"
OPTION_LIST = (
    make_option(
        "-f",
        "--fields",
        dest="field_list",
        help='Specify a comma delimited list of fields to include, e.g., -f "get_primary_net_iface.mac_address,room"',
    ),
    make_option(
        "--keyscan",
        action="store_true",
        default=False,
        help="Specify to output in ssh-keyscan format, rather than default representation",
    ),
)
# ARGS_USAGE = '...'

#######################################################################

sys.stdout = codecs.getwriter("utf-8")(sys.stdout)

#######################################################################


def _resolve_lookup(object, name):
    """
    This function originally found in django.templates.base.py, modified
    for arbitrary nested field lookups from the command line -F argument.
    
    Performs resolution of a real variable (i.e. not a literal) against the
    given context.

    As indicated by the method's name, this method is an implementation
    detail and shouldn't be called by external code. Use Variable.resolve()
    instead.
    """
    current = object
    try:  # catch-all for silent variable failures
        for bit in name.split("."):
            if current is None:
                return ""
            try:  # dictionary lookup
                current = current[bit]
            except (TypeError, AttributeError, KeyError, ValueError):
                try:  # attribute lookup
                    current = getattr(current, bit)
                except (TypeError, AttributeError):
                    try:  # list-index lookup
                        current = current[int(bit)]
                    except (
                        IndexError,  # list index out of range
                        ValueError,  # invalid literal for int()
                        KeyError,  # current is a dict without `int(bit)` key
                        TypeError,
                    ):  # unsubscriptable object
                        return "Failed lookup for [{0}]".format(
                            bit
                        )  # missing attribute
            if callable(current):
                if getattr(current, "do_not_call_in_templates", False):
                    pass
                elif getattr(current, "alters_data", False):
                    current = "<< invalid -- no data alteration >>"
                else:
                    try:  # method call (assuming no args required)
                        current = current()
                    except TypeError:  # arguments *were* required
                        # GOTCHA: This will also catch any TypeError
                        # raised in the function itself.
                        current = (
                            settings.TEMPLATE_STRING_IF_INVALID
                        )  # invalid method call
    except Exception as e:
        if getattr(e, "silent_variable_failure", False):
            current = "<< invalid -- exception >>"
        else:
            raise

    return force_text(current)


#######################################################################


def keyscan_format(object):
    """
    See ``man ssh-keyscan`` for details
    """
    elements = [object.hostname, object.hostname.split(".")[0]]

    if object.aliases:
        for part in object.aliases.split():
            for alias in part.split(","):
                elements.append(alias)
                elements.append(alias.split(".")[0])

    elements.append(object.number)
    return ",".join(elements)


#######################################################################


def main(options, args):
    for item in Model.objects.active():
        value_list = [_resolve_lookup(item, "pk")]
        if options["keyscan"]:
            value_list.append(keyscan_format(item))
        else:
            value_list.append("{}".format(item))

        if options["field_list"]:
            for field in options["field_list"].split(","):
                value_list.append(_resolve_lookup(item, field))

        print("\t".join(value_list))


#######################################################################
