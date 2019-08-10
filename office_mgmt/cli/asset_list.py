#######################
from __future__ import print_function, unicode_literals

#######################################################################
from optparse import make_option

from ..models import Asset as Model
from . import resolve_fields

#######################
"""
CLI list for Asset objects.
"""
#######################################################################

HELP_TEXT = __doc__.strip()
DJANGO_COMMAND = "main"
OPTION_LIST = (
    make_option(
        "-f",
        "--fields",
        dest="field_list",
        help="Specify a comma delimited list of fields to include, e.g., -f PROVIDE,EXAMPLE",
    ),
)

# ARGS_USAGE = '...'

#######################################################################

#######################################################################


def main(options, args):

    qs = Model.objects.active()
    for item in qs:
        value_list = ["{}".format(item.pk), "{}".format(item)]
        if options["field_list"]:
            value_list += resolve_fields(item, options["field_list"].split(","))
        print("\t".join(value_list))


#######################################################################
