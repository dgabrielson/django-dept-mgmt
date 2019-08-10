#######################
from __future__ import print_function, unicode_literals

import codecs

# set unicode piping/output:
import sys

from ..models import Computer as Model

#######################
#######################################################################

HELP_TEXT = "Get detail on a computer object, including related objects"
DJANGO_COMMAND = "main"
OPTION_LIST = ()
ARGS_USAGE = "pk [pk [...]]"

#######################################################################

sys.stdout = codecs.getwriter("utf-8")(sys.stdout)

#######################################################################

#######################################################################

M2M_FIELDS = ["flags"]
RELATED_ONLY = None  # Specify a list or None; None means introspect for related
RELATED_EXCLUDE = ["status_set"]  # any related fields to skip

#######################################################################


def print_object(obj):
    print(obj.__class__.__name__ + "\t" + "{}".format(obj))
    fields = [f.name for f in obj.__class__._meta.fields]
    for f in fields:
        print("\t" + f + "\t" + "{}".format(getattr(obj, f)))


#######################################################################


def main(options, args):
    for pk in args:
        # get the object
        obj = Model.objects.get(pk=pk)
        print_object(obj)
        # m2m fields:
        for field in M2M_FIELDS:
            print(
                "\t"
                + field
                + "\t"
                + ", ".join(["{}".format(o) for o in getattr(obj, field).all()])
            )
        if RELATED_ONLY is None:
            related_sets = [attr for attr in dir(obj) if attr.endswith("_set")]
        else:
            related_sets = RELATED_ONLY
        for attr in related_sets:
            if attr in RELATED_EXCLUDE:
                continue
            related = getattr(obj, attr)
            for rel_obj in related.all():
                print_object(rel_obj)
        print()


#######################################################################
