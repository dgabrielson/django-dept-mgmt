"""
Models for the it_mgmt application.
"""
#######################################################################
###############
from __future__ import print_function, unicode_literals

import hmac
import os
import uuid

from dateutil.parser import parser as DateTimeParser
from django.conf import global_settings, settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from mgmt_common.base import MgmtBaseModel
from office_mgmt.models import Asset

from . import handlers
from .managers import (
    ComputerFlagManager,
    ComputerManager,
    IPAddressManager,
    LicenceManager,
    NetworkInterfaceManager,
    StatusKeyManager,
    StatusManager,
    WorkNoteManager,
)

###############

try:
    from hashlib import sha1
except ImportError:
    import sha

    sha1 = sha.sha

#######################################################################

AUTH_USER_MODEL = "auth.User"  # fallback for pre- Django 1.5
if hasattr(global_settings, "AUTH_USER_MODEL"):
    AUTH_USER_MODEL = getattr(
        settings, "AUTH_USER_MODEL", global_settings.AUTH_USER_MODEL
    )

#######################################################################

# Probe for system's ping utility.
PING_EXE = None
for ping in ["/sbin/ping", "/bin/ping"]:
    if os.path.exists(ping):
        PING_EXE = ping
        break

#######################################################################


@python_2_unicode_compatible
class IPAddress(MgmtBaseModel):
    """
    A tracked IP address.
    """

    number = models.GenericIPAddressField(primary_key=True)
    hostname = models.CharField(max_length=64)
    aliases = models.CharField(max_length=256, null=True, blank=True)
    in_use = models.BooleanField(default=False)
    # updated by Computer.save()

    objects = IPAddressManager()

    class Meta:
        verbose_name = "IP Address"
        verbose_name_plural = "IP Addresses"
        base_manager_name = "objects"

    def __str__(self):
        return self.hostname + " (" + self.number + ")"

    @property
    def alive(self):
        if not PING_EXE:
            return None
        return (
            os.system(
                PING_EXE + " -c 1 -nq " + "{}".format(self.number) + "> /dev/null"
            )
            == 0
        )


#######################################################################


@python_2_unicode_compatible
class ComputerFlag(MgmtBaseModel):
    """
    Flags for indicating status and restricting queries on Computers.
    """

    slug = models.SlugField(max_length=64, unique=True)
    verbose_name = models.CharField(max_length=64)

    objects = ComputerFlagManager()

    class Meta:
        ordering = ["verbose_name"]
        base_manager_name = "objects"

    def __str__(self):
        return self.verbose_name


#######################################################################


@python_2_unicode_compatible
class Computer(MgmtBaseModel):
    """
    A computer or other networked device.
    """

    common_name = models.CharField(max_length=64)
    hardware = models.CharField(max_length=256)
    host_id = models.SlugField(max_length=256, blank=True)
    person = models.ForeignKey(
        "people.Person",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        limit_choices_to={"active": True, "flags__slug": "asset-owner"},
        help_text='Only people with the "asset-owner" flag are shown',
    )
    room = models.ForeignKey(
        "places.Room",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        limit_choices_to={"active": True},
    )

    operating_system = models.CharField(max_length=64, null=True, blank=True)

    asset = models.ForeignKey(
        Asset,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        limit_choices_to={"active": True},
    )

    processor = models.CharField(max_length=64, null=True, blank=True)
    ram = models.CharField(max_length=32, null=True, blank=True)
    harddrive = models.CharField(max_length=32, null=True, blank=True)
    manufacturing_year = models.PositiveSmallIntegerField(null=True, blank=True)

    admin_user = models.CharField(max_length=32, null=True, blank=True)
    admin_password = models.CharField(max_length=32, null=True, blank=True)
    ssh_port = models.PositiveSmallIntegerField(
        default=22, null=True, blank=True, verbose_name="SSH Port"
    )

    flags = models.ManyToManyField(
        ComputerFlag, blank=True, limit_choices_to={"active": True}
    )

    notes = models.TextField(null=True, blank=True)

    objects = ComputerManager()

    class Meta:
        base_manager_name = "objects"

    def __str__(self):
        return self.common_name

    @property
    def alive(self):
        if self.ip_address is not None:
            return self.ip_address.alive

    def has_flag(self, flag_slug):
        """
        Returns True if the object has a flag with the given slug
        """
        return self.flags.active().has_slug(flag_slug)

    def get_primary_net_iface(self):
        """
        Return the primary network interface object, if any.
        Return None if none can be found.
        """
        return self.networkinterface_set.active().primary().get()


models.signals.post_save.connect(handlers.create_api_key, sender=Computer)
models.signals.post_save.connect(
    handlers.computer_asset_sync_post_save, sender=Computer
)
models.signals.post_save.connect(handlers.asset_computer_sync_post_save, sender=Asset)

#######################################################################


@python_2_unicode_compatible
class NetworkInterface(MgmtBaseModel):
    """
    Flags for indicating status and restricting queries on Computers.
    """

    TypeChoices = (
        ("e", "Ethernet"),
        ("w", "Wi-Fi"),
        ("b", "Bluetooth"),
        ("t", "Thunderbolt"),
    )

    computer = models.ForeignKey(Computer, on_delete=models.CASCADE)
    name = models.CharField(max_length=64)
    primary = models.BooleanField(default=True)
    type = models.CharField(max_length=2, choices=TypeChoices)
    mac_address = models.CharField(max_length=104, verbose_name="MAC Address")
    managed = models.BooleanField(default=False)
    ip_address = models.ForeignKey(
        IPAddress,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        limit_choices_to={"active": True},
        verbose_name="IP Address",
    )

    objects = NetworkInterfaceManager()

    class Meta:
        ordering = ("-primary", "name")
        unique_together = (("computer", "name"),)
        base_manager_name = "objects"

    def __str__(self):
        return self.name


models.signals.pre_save.connect(handlers.ipaddress_fk_pre_save, sender=NetworkInterface)
models.signals.pre_delete.connect(
    handlers.ipaddress_fk_pre_delete, sender=NetworkInterface
)

#######################################################################


@python_2_unicode_compatible
class ComputerKey(MgmtBaseModel):
    """
    An API access key for this computer.
    """

    computer = models.OneToOneField(
        Computer, on_delete=models.CASCADE, related_name="api_key"
    )
    key = models.CharField(max_length=255, blank=True, default="", db_index=True)

    def __str__(self):
        return "{0} for {1}".format(self.key, self.computer)

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()

        return super(ComputerKey, self).save(*args, **kwargs)

    def generate_key(self):
        # Get a random UUID.
        new_uuid = uuid.uuid4()
        # Hmac that beast.
        return hmac.new(str(new_uuid), digestmod=sha1).hexdigest()


#######################################################################


@python_2_unicode_compatible
class ClientIdentifier(MgmtBaseModel):
    """
    A client ID for something which is computer related.
    Unlike a licence, this is always attached to a computer, and has a
    key (slug) and value
    """

    computer = models.ForeignKey(Computer, on_delete=models.CASCADE)
    key = models.SlugField()
    value = models.CharField(max_length=128)

    def __str__(self):
        return self.key + ":" + self.value


#######################################################################


@python_2_unicode_compatible
class ItMgmtComputerValueBaseModel(MgmtBaseModel):
    """
    An optionally computer attached note.
    """

    computer = models.ForeignKey(Computer, on_delete=models.CASCADE, null=True)
    value = models.TextField()

    class Meta:
        abstract = True

    def __str__(self):
        return self.value


#######################################################################


class WorkNote(ItMgmtComputerValueBaseModel):
    """
    A note pertaining to problems, issues, work, etc.
    """

    user = models.ForeignKey(
        AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True
    )

    objects = WorkNoteManager()

    class Meta:
        ordering = ["-created"]
        base_manager_name = "objects"


#######################################################################


class Licence(ItMgmtComputerValueBaseModel):
    """
    A licence key or note.
    """

    objects = LicenceManager()

    class Meta:
        base_manager_name = "objects"


#######################################################################

DATATYPE_CHOICES = (
    ("r", "raw"),
    ("dt", "datetime"),
    ("du", "disk usage"),
    ("i", "int"),
    ("f", "float"),
    ("m", "memory"),
    ("p", "percentage"),
)


@python_2_unicode_compatible
class StatusKey(MgmtBaseModel):
    """
    Key for indicating status
    """

    slug = models.SlugField(max_length=64, db_index=True)
    verbose_name = models.CharField(max_length=64)
    volatile = models.BooleanField(
        default=False,
        help_text="This should be set if the associated status values change frequently",
    )
    data_type = models.CharField(max_length=2, default="r", choices=DATATYPE_CHOICES)

    objects = StatusKeyManager()

    class Meta:
        ordering = ["verbose_name"]
        base_manager_name = "objects"

    def __str__(self):
        return self.verbose_name

    def data_type_format(self, value):
        """
        Use the  data_type to cast the value appropriately.
        """
        try:
            if self.data_type in ["i", "m"]:
                return int(value)
            if self.data_type == ["f", "p"]:
                return float(value)
            if self.data_type == "dt":
                return DateTimeParser().parse(value)
            if self.data_type == "du":
                label, amount = value.split("\t", 1)
                return {"label": label, "amount": float(amount)}
        except ValueError:
            pass
        return value


#######################################################################


@python_2_unicode_compatible
class Status(MgmtBaseModel):
    """
    A status report for a computer.
    """

    computer = models.ForeignKey(Computer, on_delete=models.CASCADE)
    key = models.ForeignKey(StatusKey, on_delete=models.CASCADE)
    value = models.TextField()

    objects = StatusManager()

    class Meta:
        get_latest_by = "created"
        base_manager_name = "objects"

    def __str__(self):
        return self.value
        # return '{self.key}: {self.value}'.format(self=self)

    def display(self):
        """
        Use the key data_type to cast the value appropriately.
        """
        return self.key.data_type_format(self.value)


#######################################################################
