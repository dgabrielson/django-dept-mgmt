#######################
from __future__ import print_function, unicode_literals

from mgmt_common.base import MgmtBaseManager

from .querysets import (
    ComputerFlagQuerySet,
    ComputerQuerySet,
    IPAddressQuerySet,
    LicenceQuerySet,
    NetworkInterfaceQuerySet,
    StatusKeyQuerySet,
    StatusQuerySet,
    WorkNoteQuerySet,
)

#######################
"""
Managers for the it_mgmt application.
"""

#######################################################################

# from django.db import models

#######################################################################


class ComputerManager(MgmtBaseManager):
    queryset_class = ComputerQuerySet


ComputerManager = ComputerManager.from_queryset(ComputerQuerySet)

#######################################################################


class ComputerFlagManager(MgmtBaseManager):
    queryset_class = ComputerFlagQuerySet


ComputerFlagManager = ComputerFlagManager.from_queryset(ComputerFlagQuerySet)

#######################################################################


class IPAddressManager(MgmtBaseManager):
    queryset_class = IPAddressQuerySet


IPAddressManager = IPAddressManager.from_queryset(IPAddressQuerySet)

#######################################################################


class NetworkInterfaceManager(MgmtBaseManager):
    queryset_class = NetworkInterfaceQuerySet


NetworkInterfaceManager = NetworkInterfaceManager.from_queryset(
    NetworkInterfaceQuerySet
)

#######################################################################


class WorkNoteManager(MgmtBaseManager):
    queryset_class = WorkNoteQuerySet


WorkNoteManager = WorkNoteManager.from_queryset(WorkNoteQuerySet)

#######################################################################


class LicenceManager(MgmtBaseManager):
    queryset_class = LicenceQuerySet


LicenceManager = LicenceManager.from_queryset(LicenceQuerySet)

#######################################################################


class StatusKeyManager(MgmtBaseManager):
    queryset_class = StatusKeyQuerySet


StatusKeyManager = StatusKeyManager.from_queryset(StatusKeyQuerySet)

#######################################################################


class StatusManager(MgmtBaseManager):
    queryset_class = StatusQuerySet


StatusManager = StatusManager.from_queryset(StatusQuerySet)

#######################################################################
