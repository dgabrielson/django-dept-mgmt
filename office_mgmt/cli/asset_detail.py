#######################
from __future__ import print_function, unicode_literals

from ..models import Asset as Model
from . import object_detail

#######################
#######################################################################

HELP_TEXT = "Get detail on an Asset object, including related objects"
DJANGO_COMMAND = "main"
OPTION_LIST = ()
ARGS_USAGE = "pk [pk [...]]"

#######################################################################

M2M_FIELDS = []
RELATED_ONLY = None  # Specify a list or None; None means introspect for related
RELATED_EXCLUDE = []  # any related fields to skip

#######################################################################


def main(options, args):
    for pk in args:
        # get the object
        obj = Model.objects.get(pk=pk)
        print(object_detail(obj, M2M_FIELDS, RELATED_ONLY, RELATED_EXCLUDE))


#######################################################################
