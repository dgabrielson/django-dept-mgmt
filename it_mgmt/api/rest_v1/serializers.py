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
from rest_framework import serializers

#######################

###############################################################

###############################################################


class ComputerFlagInlineSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ComputerFlag
        fields = ("slug", "verbose_name")


class ComputerFlagSerializer(ComputerFlagInlineSerializer):
    class Meta(ComputerFlagInlineSerializer.Meta):
        fields = ("url",) + ComputerFlagInlineSerializer.Meta.fields


###############################################################

# class IPAddressInlineSerializer(serializers.HyperlinkedModelSerializer):
#     class Meta:
#         model = IPAddress
#         fields = ('number', 'hostname', 'aliases', 'in_use', )
#
#
# class IPAddressSerializer(IPAddressInlineSerializer):
#     class Meta(IPAddressInlineSerializer.Meta):
#         fields = ('url', ) + IPAddressInlineSerializer.Meta.fields


class IPAddressSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = IPAddress
        fields = ("url", "number", "hostname", "aliases", "in_use")


###############################################################


class NetworkInterfaceInlineSerializer(serializers.HyperlinkedModelSerializer):
    # ip_address = IPAddressSerializer(read_only=True)

    class Meta:
        model = NetworkInterface
        fields = ("name", "primary", "type", "mac_address", "managed", "ip_address")


class NetworkInterfaceSerializer(NetworkInterfaceInlineSerializer):
    class Meta(NetworkInterfaceInlineSerializer.Meta):
        fields = ("url", "computer") + NetworkInterfaceInlineSerializer.Meta.fields


###############################################################


class ClientIdentifierInlineSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ClientIdentifier
        fields = ("key", "value")


class ClientIdentifierSerializer(ClientIdentifierInlineSerializer):
    class Meta(ClientIdentifierInlineSerializer.Meta):
        fields = ("url", "computer") + ClientIdentifierInlineSerializer.Meta.fields


###############################################################


class WorkNoteInlineSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.ReadOnlyField(source="user.username")

    class Meta:
        model = WorkNote
        fields = ("user", "value")


class WorkNoteSerializer(WorkNoteInlineSerializer):
    class Meta(WorkNoteInlineSerializer.Meta):
        fields = ("url", "computer") + WorkNoteInlineSerializer.Meta.fields


###############################################################


class LicenceInlineSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Licence
        fields = ("value",)


class LicenceSerializer(LicenceInlineSerializer):
    class Meta(LicenceInlineSerializer.Meta):
        fields = ("url", "computer") + LicenceInlineSerializer.Meta.fields


###############################################################


class ComputerSerializer(serializers.HyperlinkedModelSerializer):
    pk = serializers.ReadOnlyField()
    room = serializers.StringRelatedField(read_only=True)
    asset = serializers.StringRelatedField(read_only=True)
    networkinterface_set = NetworkInterfaceInlineSerializer(many=True, read_only=True)
    clientidentifier_set = ClientIdentifierInlineSerializer(many=True, read_only=True)
    worknote_set = WorkNoteInlineSerializer(many=True, read_only=True)
    licence_set = LicenceInlineSerializer(many=True, read_only=True)

    class Meta:
        model = Computer
        fields = (
            "url",
            "pk",
            "common_name",
            "hardware",
            "host_id",
            "room",
            "asset",
            "operating_system",
            "processor",
            "ram",
            "harddrive",
            "admin_user",
            "flags",
            "networkinterface_set",
            "clientidentifier_set",
            "worknote_set",
            "licence_set",
        )


###############################################################
