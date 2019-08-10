#######################
from __future__ import print_function, unicode_literals

from django.conf.urls import url

from tastypie import fields
from tastypie.authentication import ApiKeyAuthentication
from tastypie.authorization import DjangoAuthorization
from tastypie.resources import ALL, ALL_WITH_RELATIONS, ModelResource

from ..models import Computer, ComputerFlag, ComputerKey, IPAddress, NetworkInterface
from . import (
    ComputerRelatedResourceMixin,
    ItMgmtAuthentication,
    ItMgmtAuthorization,
    PrettyJSONSerializer,
)

#######################
"""
API for Computers.

These are read-only except to computer administrators.
"""

#######################################################################

#######################################################################


class ComputerFlagResource(ModelResource):
    class Meta:
        queryset = ComputerFlag.objects.active()
        serializer = PrettyJSONSerializer()
        authentication = ItMgmtAuthentication()
        authorization = ItMgmtAuthorization()


#######################################################################


class ComputerResource(ModelResource):
    flags = fields.ManyToManyField(ComputerFlagResource, "flags")

    class Meta:
        queryset = Computer.objects.active()
        excludes = ("admin_user", "admin_password", "ssh_port")
        serializer = PrettyJSONSerializer()
        authentication = ItMgmtAuthentication()
        authorization = ItMgmtAuthorization()


#######################################################################


class IPAddressResource(ModelResource):
    class Meta:
        queryset = IPAddress.objects.active()
        serializer = PrettyJSONSerializer()
        filtering = {"number": ALL, "hostname": ALL, "aliases": ALL, "in_use": ALL}
        authentication = ItMgmtAuthentication()
        authorization = ItMgmtAuthorization()

    def prepend_urls(self):
        return [
            # Need to change the pk regex, since pk's are the IP Address
            #   "number" field.
            url(
                r"^(?P<resource_name>%s)/(?P<pk>[\d.]+)/$" % self._meta.resource_name,
                self.wrap_view("dispatch_detail"),
                name="api_dispatch_detail",
            )
        ]


#######################################################################


class NetworkInterfaceResource(ComputerRelatedResourceMixin, ModelResource):
    computer = fields.ForeignKey(ComputerResource, "computer")
    ip_address = fields.ForeignKey(IPAddressResource, "ip_address")

    class Meta:
        queryset = NetworkInterface.objects.active()
        serializer = PrettyJSONSerializer()
        filtering = {"mac_address": ALL, "ip_address": ALL_WITH_RELATIONS}
        authentication = ItMgmtAuthentication()
        authorization = ItMgmtAuthorization()


#######################################################################


class ComputerKeyResource(ModelResource):
    """
    This is available to Django users with ApiKeys only.
    """

    computer = fields.ForeignKey(ComputerResource, "computer")

    class Meta:
        queryset = ComputerKey.objects.all()
        serializer = PrettyJSONSerializer()
        filtering = {"computer": ALL_WITH_RELATIONS}
        authentication = ApiKeyAuthentication()
        authorization = DjangoAuthorization()


#######################################################################
