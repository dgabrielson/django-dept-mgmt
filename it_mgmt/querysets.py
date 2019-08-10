#######################
from __future__ import print_function, unicode_literals

from django.db import models
from mgmt_common.base import MgmtBaseQuerySet

#######################
"""
Models for the it_mgmt application.
"""

#######################################################################

#######################################################################


class ComputerQuerySet(MgmtBaseQuerySet):
    """
    Provide a custom model API.  Urls, views, etc. should only
    use these methods, never .filter(...).
    """

    search_fields = [
        "common_name",
        "hardware",
        "networkinterface__mac_address",
        "networkinterface__ip_address__number",
        "networkinterface__ip_address__hostname",
        "networkinterface__ip_address__aliases",
    ]


#######################################################################


class ComputerFlagQuerySet(MgmtBaseQuerySet):
    """
    Provide a custom model API.  Urls, views, etc. should only
    use these methods, never .filter(...).
    """

    def slug_list(self):
        """
        Returns a list of slugs corresponding to the current query set
        """
        return self.values_list("slug", flat=True)

    def has_flag(self, flag_slug):
        """
        Returns True if the given slug is in the current query set
        """
        return flag_slug in self.slug_list()


#######################################################################


class IPAddressQuerySet(MgmtBaseQuerySet):
    """
    Provide a custom model API.  Urls, views, etc. should only
    use these methods, never .filter(...).
    """


#######################################################################


class NetworkInterfaceQuerySet(MgmtBaseQuerySet):
    """
    Provide a custom model API.  Urls, views, etc. should only
    use these methods, never .filter(...).
    """

    def primary(self):
        """
        Restrict to primary interfaces
        """
        return self.filter(primary=True)

    def managed(self):
        """
        Restrict to primary interfaces
        """
        return self.filter(managed=True)

    def by_type(self, type_code):
        """
        Restrict by the type of interface
        """
        return self.filter(type=type_code)

    def ethernet(self):
        return self.by_type("e")

    def wifi(self):
        return self.by_type("w")


#######################################################################


class ItMgmtComputerValueBaseQuerySet(MgmtBaseQuerySet):
    """
    Provide custom queryset methods for items with the optional
    computer foreign key.
    """

    def unattached(self):
        """
        Restrict to only those items without a foreign key.
        """
        return self.filter(computer__isnull=True)


#######################################################################


class WorkNoteQuerySet(ItMgmtComputerValueBaseQuerySet):
    """
    Provide a custom model API.  Urls, views, etc. should only
    use these methods, never .filter(...).
    """


#######################################################################


class LicenceQuerySet(ItMgmtComputerValueBaseQuerySet):
    """
    Provide a custom model API.  Urls, views, etc. should only
    use these methods, never .filter(...).
    """


#######################################################################


class StatusKeyQuerySet(MgmtBaseQuerySet):
    """
    Provide a custom model API.  Urls, views, etc. should only
    use these methods, never .filter(...).
    """


#######################################################################


class StatusQuerySet(MgmtBaseQuerySet):
    """
    Provide a custom model API.  Urls, views, etc. should only
    use these methods, never .filter(...).
    """

    #     # is this one even necessary??
    #     def bulk_create_from_dict(self, computer, d):
    #         """
    #         Bulk create a new set of statuses for an individual computer.
    #         The keys of the update dictionary correspond to StatusKey slug
    #         fields, and created if they checked before creation.
    #         """
    #         from .models import StatusKey
    #         key_list = d.keys()
    #         statuskey_map = StatusKey.objects.in_bulk(key_list)
    #         result = []
    #         for slug in key_list:
    #             value = d[slug]
    #             key = statuskey_map[slug]
    #             result.append( self.create(computer=computer, key=key,
    #                                        value=value) )
    #         return result

    def computers(self):
        """
        Return the queryset of computers.
        """
        from .models import Computer

        pk_set = self.values_list("computer", flat=True).distinct()
        return Computer.objects.filter(pk__in=pk_set)

    def statuskeys(self):
        """
        Return the queryset of status keys.
        """
        from .models import StatusKey

        pk_set = self.values_list("key", flat=True).distinct()
        return StatusKey.objects.filter(pk__in=pk_set)

    def latest_by_key(self, key_slugs=None):
        """
        Return the latest status for the given key slugs.
        If ``key_slugs`` is None, then return for *all* keys.
        
        N+2 queries... is there no better way?
        """
        qs_key_slugs = self.statuskeys().values_list("slug", flat=True)
        if key_slugs is None:
            key_slugs = qs_key_slugs
        # this is probably not the most efficient way, in terms of
        # queryset, etc.
        pk_list = [
            self.filter(key__slug=slug).values_list("pk", flat=True).latest()
            for slug in key_slugs
            if slug in qs_key_slugs
        ]
        qs = self.filter(pk__in=pk_list).order_by("key")
        return qs


#######################################################################
