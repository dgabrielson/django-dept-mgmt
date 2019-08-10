"""
Managers for the office_mgmt application.
"""
#######################
from __future__ import print_function, unicode_literals

from django.db import models
from mgmt_common.base import MgmtBaseManager

from .querysets import (
    AssetQuerySet,
    LoanGroupQuerySet,
    LoanItemQuerySet,
    LoanRecordQuerySet,
    PaperworkQuerySet,
)

#######################
#######################################################################

#######################################################################


class AssetManager(MgmtBaseManager):
    queryset_class = AssetQuerySet
    always_select_related = ["person", "room"]


AssetManager = AssetManager.from_queryset(AssetQuerySet)

#######################################################################


class PaperworkManager(MgmtBaseManager):
    queryset_class = PaperworkQuerySet


PaperworkManager = PaperworkManager.from_queryset(PaperworkQuerySet)

#######################################################################


class LoanGroupManager(MgmtBaseManager):
    queryset_class = LoanGroupQuerySet


LoanGroupManager = LoanGroupManager.from_queryset(LoanGroupQuerySet)

#######################################################################


class LoanItemManager(MgmtBaseManager):
    queryset_class = LoanItemQuerySet


LoanItemManager = LoanItemManager.from_queryset(LoanItemQuerySet)

#######################################################################


class LoanRecordManager(MgmtBaseManager):
    queryset_class = LoanRecordQuerySet


LoanRecordManager = LoanRecordManager.from_queryset(LoanRecordQuerySet)

#######################################################################
