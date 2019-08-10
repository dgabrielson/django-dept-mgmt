#######################
from __future__ import print_function, unicode_literals

import codecs

# set unicode piping/output:
import sys
from optparse import make_option

from django.db import models

from ..models import Asset

#######################
"""
Copy an asset record to a new asset; duplicating any associated paperwork.
"""
#######################################################################

HELP_TEXT = __doc__.strip()
DJANGO_COMMAND = "main"
OPTION_LIST = (
    make_option(
        "-s", "--serial", help="Supply the serial number for the new asset (required)"
    ),
)
ARGS_USAGE = "[pk]"

#######################################################################

sys.stdout = codecs.getwriter("utf-8")(sys.stdout)

#######################################################################

#######################################################################


def copy_obj(
    src,
    dst_values,
    direct_fields=None,
    exclude_fields=None,
    m2m_fields=None,
    related_fields=None,
):
    """
    Copy an original object ``src`` into a new object, and update
    values with ``dst_values``.
    
    By default, optional parameters which are ``None`` will introspect
    or use sane defaults.
    
    Returns the new object.
    
    All of the ``_fields`` options, if given, are lists; except for
    ``related_fields`` which is a list of ordered pairs:
    ``[ (field_accessor, related_object_field_name), ...]``
    
    NOTE: related_fields are *not* copied unless explicit given -- 
    this causes recursion problems.
    """
    model = src.__class__
    if exclude_fields is None:
        exclude_fields = ["created", "modified"]
    if model._meta.has_auto_field:
        exclude_fields.append(model._meta.auto_field.name)

    model_direct_fields = []
    model_m2m_fields = []
    model_related_fields = []
    for name in model._meta.get_all_field_names():
        field, field_model, direct, m2m = model._meta.get_field_by_name(name)
        if m2m:
            model_m2m_fields.append(name)
        elif direct:
            model_direct_fields.append(name)
        else:
            model_related_fields.append((field.get_accessor_name(), field.field.name))

    if direct_fields is None:
        direct_fields = model_direct_fields
    if m2m_fields is None:
        m2m_fields = model_m2m_fields
    if related_fields is None:
        related_fields = []  # model_related_fields

    direct_fields = [f for f in direct_fields if f not in exclude_fields]
    m2m_fields = [f for f in m2m_fields if f not in exclude_fields]
    related_fields = [f for f in related_fields if f[0] not in exclude_fields]

    values = dict([(f, getattr(src, f)) for f in direct_fields])
    values.update(dst_values)
    # Hmmm... what if dst_values has non-direct fields?

    # do direct -- initial create
    valid_keys = model._meta.get_all_field_names()
    remove_keys = []
    for k in values:
        if k not in valid_keys:
            remove_keys.append(k)
        if k.endswith("_id") and k[:-3] in valid_keys:
            f = model._meta.get_field(k[:-3])
            if f.is_relation and f.related_model is not None:
                if values[k] is not None:
                    values[k[:-3]] = f.related_model.objects.get(pk=values[k])
                else:
                    values[k[:-3]] = None
                remove_keys.append(k)
    for k in remove_keys:
        del values[k]
    dst = model.objects.create(**values)
    # do m2m
    for f in m2m_fields:
        m2m_manager = getattr(src, f)
        m2m_value = m2m_manager.all()
        setattr(dst, f, m2m_value)
    if m2m_fields:
        # m2m save
        dst.save()

    # do related -- deep copy
    for accessor_name, related_name in related_fields:
        related = getattr(src, accessor_name)
        if isinstance(related, models.Model):
            # OneToOne related -- we cannot copy this.
            pass
        elif isinstance(related, models.Manager):
            # ForeignKey related
            for o in related.all():
                copy_obj(o, {related_name: dst})
        else:
            assert (
                False
            ), "Some unknown type of relationship -- not direct, m2m, one-to-one, or foreign-key?!?"

    return dst


#######################################################################


def asset_copy(src, serial_number, **kwargs):
    """
    Copy the ``src`` Asset, including all related information.
    ``serial_number`` is required, and ``kwargs`` are other values to update.
    """
    kwargs["serial_number"] = serial_number
    dst = copy_obj(src, kwargs, related_fields=[("paperwork_set", "asset")])
    return dst


#######################################################################


def main(options, args):
    verbosity = int(options.get("verbosity", 1))
    serial_number = options.get("serial", None)
    if len(args) != 1:
        print("Only one source object can be copied.")
        return
    pk = args[0]
    if not serial_number:
        print("You must specify a new serial number with --serial=...")
        return
    src = Asset.objects.get(pk=pk)
    dst = asset_copy(src, serial_number)
    if verbosity > 0:
        print(src, "copied")
    if verbosity > 2:
        print("  new id =", dst.pk)


#######################################################################
