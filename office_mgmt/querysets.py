"""
Models for the office_mgmt application.
"""
#######################
from __future__ import print_function, unicode_literals

from django.db import models
from mgmt_common.base import MgmtBaseQuerySet

#######################
#######################################################################

#######################################################################


class AssetQuerySet(MgmtBaseQuerySet):
    """
    Provide a custom model API.  Urls, views, etc. should only
    use these methods, never .filter(...).
    """


#######################################################################


class PaperworkQuerySet(MgmtBaseQuerySet):
    """
    Provide a custom model API.  Urls, views, etc. should only
    use these methods, never .filter(...).
    """


#######################################################################


class LoanGroupQuerySet(MgmtBaseQuerySet):
    """
    Provide a custom model API.  Urls, views, etc. should only
    use these methods, never .filter(...).
    """

    def person_queryset(self):
        """
        Return a person query set corresponding to the current queryset
        of LoanGroups.
        """
        from people.models import Person

        flag_set = self.values_list("flag", flat=True).distinct()
        return Person.objects.filter(flags__in=flag_set).distinct()


#######################################################################


class LoanItemQuerySet(MgmtBaseQuerySet):
    """
    Provide a custom model API.  Urls, views, etc. should only
    use these methods, never .filter(...).
    """

    def available(self):
        """
        Items which are *not* out. Implies active() as well.
        """
        qs = self.active()
        # ...
        return qs


#######################################################################


class LoanRecordQuerySet(MgmtBaseQuerySet):
    """
    Provide a custom model API.  Urls, views, etc. should only
    use these methods, never .filter(...).
    """


#######################################################################
