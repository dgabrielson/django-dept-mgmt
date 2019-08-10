#######################
from __future__ import print_function, unicode_literals

from django.contrib import admin
from people.models import Person
from places.models import Room

#######################
"""
This module provides some common functionality, actions, and
base classes for the _mgmt appliations.
"""

##############################################################

##############################################################
##############################################################


def mark_inactive(modeladmin, request, queryset):
    queryset.update(active=False)


mark_inactive.short_description = "Mark selected items as inactive"

##############################################################


def choice_field_update(field, field_desc, code, code_desc):
    """
    Generate an update action function for all possibile options 
    in a field with choices.
    """

    def _updater(ma, r, qs):
        qs.update(**{field: code})

    _updater.short_description = "Update {0} to: {1}".format(field_desc, code_desc)
    _updater.__name__ = str("update_{0}_{1}".format(field, code))
    return _updater


##############################################################


class UsedRelatedValuesFilter(admin.SimpleListFilter):
    """
    A custom filter, so that we only see related values which are used.
    """

    # Define a subclass and set these appropriately:
    title = "SetThis"
    # the parameter_name is the name of the related field.
    parameter_name = "set_this"
    allow_none = True
    reverse = False
    model = object

    def object_label(self, o):
        """
        Override this to customize the labelling of the objects
        """
        return "{}".format(o)

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples (coded-value, title).
        """
        qs = model_admin.get_queryset(request)
        related_qs = self.model.objects.filter(
            pk__in=qs.values_list(self.parameter_name, flat=True)
        )
        lookups = [(o.pk, self.object_label(o)) for o in related_qs]
        if self.reverse:
            lookups.reverse()
        if self.allow_none:
            lookups.append(("(None)", "(None)"))
        return lookups

    def queryset(self, request, queryset):
        """
        Apply the filter to the existing queryset.
        """
        filter = self.value()
        filter_field = self.parameter_name
        if filter is None:
            return
        elif filter == "(None)":
            filter_field += "__isnull"
            filter_value = True
        else:
            filter_field += "__pk__exact"
            filter_value = filter
        return queryset.filter(**{filter_field: filter_value})


##############################################################


class PersonFilter(UsedRelatedValuesFilter):
    """
    A custom filter so that we only see people which are actually used.
    """

    title = "Person"
    parameter_name = "person"
    allow_none = True
    model = Person


##############################################################


class RoomFilter(UsedRelatedValuesFilter):
    """
    A custom filter so that we only see room which are actually used.
    """

    title = "Room"
    parameter_name = "room"
    allow_none = True
    model = Room


##############################################################


class MgmtActiveAdminMixin(object):
    """
    This mixin class restricts the queryset to only active item;
    unless the user is the super-user.
    """

    def get_queryset(self, request):
        """
        This function restricts the default queryset in the
        admin list view.
        """
        qs = super(MgmtActiveAdminMixin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.active()


##############################################################
