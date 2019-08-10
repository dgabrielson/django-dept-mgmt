"""
Models for the office_mgmt application.
"""
###############
from __future__ import print_function, unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.timezone import now
from mgmt_common.base import MgmtBaseModel

from . import conf
from .managers import (
    AssetManager,
    LoanGroupManager,
    LoanItemManager,
    LoanRecordManager,
    PaperworkManager,
)

###############
#######################################################################

#######################################################################
#######################################################################

CURRENT_CONDITION_CHOICES = (
    ("A", "Excellent (like new)"),
    ("B", "Good (working)"),
    ("C", "Poor (needs repair)"),
    ("D", "Not Working"),
    #    ('1', 'Sold'),
    #    ('2', 'Disposed'),
    # Sold and disposed are now covered by status.
    ("9", "Stolen"),
    ("0", "Missing"),
)

ASSET_STATUS_CHOICES = (
    ("u", "In use"),
    ("i", "Inactive"),
    ("p", "Do paperwork"),
    ("dw", "Disposed (awaiting pickup)"),
    ("dg", "Disposed (gone)"),
    ("sa", "For sale"),
    ("sw", "Sold (awaiting pickup)"),
    ("sg", "Sold (gone)"),
)

#######################################################################
#######################################################################


@python_2_unicode_compatible
class Asset(MgmtBaseModel):
    """
    An asset which needs tracking, perhaps for future asset disposal.
    """

    description = models.CharField(max_length=256)

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

    status = models.CharField(default="u", max_length=3, choices=ASSET_STATUS_CHOICES)

    serial_number = models.CharField(max_length=64)
    property_number = models.IntegerField(null=True, blank=True)
    security_id = models.CharField(
        max_length=128, blank=True, verbose_name="Security ID"
    )
    date_acquired = models.DateField(null=True, blank=True)
    purchase_order_number = models.CharField(blank=True, max_length=32)
    original_cost = models.CharField(blank=True, max_length=32)
    original_fopal = models.CharField(
        blank=True, max_length=64, verbose_name="Original FOPAL"
    )
    current_condition = models.CharField(
        blank=True, null=True, max_length=2, choices=CURRENT_CONDITION_CHOICES
    )

    off_site = models.BooleanField(default=False)

    reserve_bid = models.CharField(blank=True, max_length=32)
    sale_amount = models.CharField(blank=True, max_length=32)
    date_disposed = models.DateField(null=True, blank=True)

    notes = models.TextField(null=True, blank=True)

    objects = AssetManager()

    class Meta:
        ordering = ["-created"]
        base_manager_name = "objects"

    def __str__(self):
        if self.property_number is not None:
            return (
                "{}".format(self.serial_number)
                + "/"
                + "{}".format(self.property_number)
            )
            # careful!  property_number returns an int unless cast.
        else:
            return "{}".format(self.serial_number)


#######################################################################


@python_2_unicode_compatible
class Paperwork(MgmtBaseModel):
    """
    Paperwork.  May belong to another object, such as a particular Asset.
    """

    description = models.CharField(max_length=256)
    asset = models.ForeignKey(
        Asset, on_delete=models.CASCADE, null=True, limit_choices_to={"active": True}
    )
    attachment = models.FileField(
        upload_to=conf.get("upload_to"), storage=conf.get("storage")
    )

    objects = PaperworkManager()

    class Meta:
        verbose_name_plural = "paperwork"
        base_manager_name = "objects"

    def __str__(self):
        return self.description


#######################################################################


@python_2_unicode_compatible
class LoanGroup(MgmtBaseModel):
    """
    A LoanGroup is a group of people which may borrow LoanItems.
    """

    flag = models.OneToOneField(
        "people.PersonFlag",
        on_delete=models.CASCADE,
        help_text="The person flag corresponding to this group",
    )

    objects = LoanGroupManager()

    class Meta:
        base_manager_name = "objects"

    def __str__(self):
        return "{}".format(self.flag)


#######################################################################


@python_2_unicode_compatible
class LoanItem(MgmtBaseModel):
    """
    An which may be borrowed.
    """

    tag = models.CharField(
        max_length=128,
        help_text="A short description of the item, possibly a serial number or sticker ID",
    )
    description = models.TextField(
        blank=True, help_text="A longer description of the item"
    )

    objects = LoanItemManager()

    class Meta:
        base_manager_name = "objects"

    def __str__(self):
        return self.tag

    def is_available(self):
        """
        Returns ``True`` if the item is available for loaning, and
        ``False`` when it's already been loaned out.
        """
        try:
            record = self.loanrecord_set.active().latest()
        except LoanRecord.DoesNotExist:
            return True
        else:
            return record.has_been_returned()

    is_available.boolean = True


#######################################################################

LOAN_TYPE_CHOICES = (("s", "Short term"), ("l", "Long term"))


@python_2_unicode_compatible
class LoanRecord(MgmtBaseModel):
    """
    A record of a single loan
    """

    item = models.ForeignKey(LoanItem, on_delete=models.CASCADE)
    person = models.ForeignKey("people.Person", on_delete=models.CASCADE)
    loaned_dt = models.DateTimeField(default=now, verbose_name="Loaned")
    returned_dt = models.DateTimeField(blank=True, null=True, verbose_name="Returned")
    loan_type = models.CharField(max_length=2, choices=LOAN_TYPE_CHOICES, default="s")
    deposit = models.CharField(
        max_length=8,
        blank=True,
        default="",
        help_text="Amount of deposit taken, if any",
    )

    objects = LoanItemManager()

    class Meta:
        ordering = ["-loaned_dt"]
        get_latest_by = "loaned_dt"
        base_manager_name = "objects"

    def __str__(self):
        return "Loan: {self.item} to {self.person}".format(self=self)

    def has_been_returned(self):
        """
        Returns ``True`` if the the record indicates the item has been 
        returned, ``False`` otherwise.
        """
        return self.returned_dt is not None

    has_been_returned.boolean = True


#######################################################################
#######################################################################
