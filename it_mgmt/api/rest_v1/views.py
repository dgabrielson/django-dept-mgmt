#######################
from __future__ import print_function, unicode_literals

from it_mgmt.models import (
    ClientIdentifier,
    Computer,
    ComputerFlag,
    IPAddress,
    Licence,
    NetworkInterface,
    WorkNote,
)
from rest_framework import generics, permissions, renderers, viewsets
from rest_framework.response import Response
from rest_framework.reverse import reverse

from .serializers import (
    ClientIdentifierSerializer,
    ComputerFlagSerializer,
    ComputerSerializer,
    IPAddressSerializer,
    LicenceSerializer,
    NetworkInterfaceSerializer,
    WorkNoteSerializer,
)

#######################
###############################################################

###############################################################


class ItMgmtPermissions(object):
    """
    Permission class mixin for all IT Mgmt Views/ViewSets.
    """

    permission_classes = (permissions.IsAdminUser, permissions.DjangoModelPermissions)


###############################################################


class FilterModelViewSet(viewsets.ModelViewSet):
    """
    Specify the names of fields to allow GET query filtering.
    E.g., filter_fields = ['host_id', ]
    """

    filter_fields = []

    def get_queryset(self):
        """
        Optionally restricts the returned queryset,
        by filtering against any query parameters in the URL.
        """
        queryset = super(FilterModelViewSet, self).get_queryset()
        filter = {}
        for f in self.filter_fields:
            value = self.request.query_params.get(f, None)
            if value is not None:
                filter[f] = value
        queryset = queryset.filter(**filter)
        return queryset


###############################################################


class ItMgmtModelViewSet(ItMgmtPermissions, FilterModelViewSet):
    """
    Base class for all IT Management viewsets
    """


###############################################################


class ComputerViewSet(ItMgmtModelViewSet):
    queryset = Computer.objects.all()
    serializer_class = ComputerSerializer
    filter_fields = ["host_id"]


###############################################################


class ComputerFlagViewSet(ItMgmtModelViewSet):
    queryset = ComputerFlag.objects.all()
    serializer_class = ComputerFlagSerializer
    filter_fields = ["slug"]


###############################################################


class NetworkInterfaceViewSet(ItMgmtModelViewSet):
    queryset = NetworkInterface.objects.all()
    serializer_class = NetworkInterfaceSerializer
    filter_fields = [
        "computer__pk",
        "computer__host_id",
        "mac_address",
        "name",
        "managed",
    ]


###############################################################


class ClientIdentifierViewSet(ItMgmtModelViewSet):
    queryset = ClientIdentifier.objects.all()
    serializer_class = ClientIdentifierSerializer
    filter_fields = ["computer__pk", "computer__host_id", "key"]


###############################################################


class WorkNoteViewSet(ItMgmtModelViewSet):
    queryset = WorkNote.objects.all()
    serializer_class = WorkNoteSerializer
    filter_fields = ["computer__pk", "computer__host_id", "user__username"]


###############################################################


class LicenceViewSet(ItMgmtModelViewSet):
    queryset = Licence.objects.all()
    serializer_class = LicenceSerializer
    filter_fields = ["computer__pk", "computer__host_id"]


###############################################################


class IPAddressViewSet(ItMgmtModelViewSet):
    queryset = IPAddress.objects.all()
    serializer_class = IPAddressSerializer
    filter_fields = ["number", "hostname", "aliases", "in_use"]
    # TODO: figure out regex for ip4 or ip6.
    lookup_value_regex = "[0-9.]+"


###############################################################
