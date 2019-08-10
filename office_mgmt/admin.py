#######################
from __future__ import print_function, unicode_literals

from django.conf.urls import url
from django.contrib import admin
from django.utils.timezone import now
from mgmt_common.admin import (
    MgmtActiveAdminMixin,
    PersonFilter,
    RoomFilter,
    choice_field_update,
    mark_inactive,
)

from .forms import LoanGroupForm, LoanItemForm, LoanRecordForm
from .models import (
    ASSET_STATUS_CHOICES,
    CURRENT_CONDITION_CHOICES,
    Asset,
    LoanGroup,
    LoanItem,
    LoanRecord,
    Paperwork,
)
from .views import asset_disposal_form

#######################
"""
Admin classes for the  office_mgmt application
"""
#######################################################################

#######################################################################
#######################################################################

ASSET_UPDATE_ACTION_LIST = []
for code, desc in ASSET_STATUS_CHOICES:
    ASSET_UPDATE_ACTION_LIST.append(choice_field_update("status", "status", code, desc))

#######################################################################

ASSET_UPDATE_ACTION_LIST.append(
    choice_field_update("current_condition", "current condition", None, "Unknown")
)
for code, desc in CURRENT_CONDITION_CHOICES:
    ASSET_UPDATE_ACTION_LIST.append(
        choice_field_update("current_condition", "current condition", code, desc)
    )

#######################################################################


class Paperwork_Inline(admin.StackedInline):
    model = Paperwork
    extra = 0


class AssetAdmin(MgmtActiveAdminMixin, admin.ModelAdmin):
    """
    Admin class for the Asset model.
    """

    list_display = ["serial_number", "property_number", "person", "room", "description"]
    list_filter = [
        "active",
        "off_site",
        "status",
        "current_condition",
        "date_acquired",
        "date_disposed",
        PersonFilter,
        RoomFilter,
        "created",
        "modified",
    ]
    search_fields = ["serial_number", "property_number", "description"]
    #    ordering = ['serial_number', ]

    save_as = True
    save_on_top = True
    actions = [mark_inactive] + ASSET_UPDATE_ACTION_LIST
    inlines = [Paperwork_Inline]

    def get_urls(self):
        """
        Extend the admin urls for this model.
        Provide a link by subclassing the admin change_form,
        and adding to the object-tools block.
        """
        urls = super(AssetAdmin, self).get_urls()
        urls = [
            url(
                r"^(.+)/disposal-form/$",
                self.admin_site.admin_view(asset_disposal_form),
                name="office_mgmt_asset_disposalform",
            )
        ] + urls
        return urls


admin.site.register(Asset, AssetAdmin)

#######################################################################


class LoanGroupAdmin(MgmtActiveAdminMixin, admin.ModelAdmin):
    """
    Admin class for the LoanGroup model
    """

    form = LoanGroupForm


admin.site.register(LoanGroup, LoanGroupAdmin)

#######################################################################


class LoanRecordInline(admin.TabularInline):
    form = LoanRecordForm
    model = LoanRecord
    # exclude = ('notes', )
    extra = 0


class LoanItemAdmin(MgmtActiveAdminMixin, admin.ModelAdmin):
    """
    Admin class for the LoanItem model
    """

    form = LoanItemForm
    inlines = [LoanRecordInline]
    list_display = ["tag", "is_available"]
    list_filter = ["active"]
    search_fields = ["tag", "description"]


admin.site.register(LoanItem, LoanItemAdmin)

#######################################################################


class OutstandingLoanFilter(admin.SimpleListFilter):
    """
    A custom filter, so that we only see what has been returned and 
    what has not.
    """

    title = "Loan status"
    parameter_name = "loan-status"

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples (coded-value, title).
        """
        return (("outstanding", "Outstanding"), ("returned", "Returned"))
        qs = model_admin.get_queryset(request)

        pk_set = set(qs.values_list(self.field_name, flat=True))
        related_qs = self.model.objects.filter(pk__in=pk_set)
        lookups = [(o.pk, "{}".format(o)) for o in related_qs]
        if self.allow_none:
            lookups.append(("(None)", "(None)"))
        return lookups

    def queryset(self, request, queryset):
        """
        Apply the filter to the existing queryset.
        """
        filter = self.value()
        filter_field = "returned_dt__isnull"
        if filter is None:
            return queryset
        elif filter == "outstanding":
            filter_value = True
        elif filter == "returned":
            filter_value = False
        else:
            assert False, "Unknown filter_value: {0!r}".format(filter_value)
        return queryset.filter(**{filter_field: filter_value})


#######################################################################


class LoanRecordAdmin(MgmtActiveAdminMixin, admin.ModelAdmin):
    """
    Admin class for the LoanRecord model
    """

    form = LoanRecordForm
    list_filter = ["active", OutstandingLoanFilter, "loan_type", "created", "modified"]
    list_display = ["item", "person", "has_been_returned"]
    search_fields = [
        "person__cn",
        "person__sn",
        "person__given_name",
        "item__tag",
        "item__description",
    ]

    actions = [mark_inactive, "mark_returned"]

    def mark_returned(self, request, queryset):
        queryset.exclude(returned_dt__isnull=False).update(returned_dt=now())

    mark_returned.short_description = (
        "Mark the selected loan as returned (if outstanding)"
    )


admin.site.register(LoanRecord, LoanRecordAdmin)

#######################################################################


class PaperworkAdmin(MgmtActiveAdminMixin, admin.ModelAdmin):
    """
    Admin class for standalone paperwork records.
    """

    exclude = ["asset"]
    date_hierarchy = "created"
    list_display = ["description", "created", "modified"]
    list_filter = ["active", "created", "modified"]
    search_fields = ["description"]

    def get_queryset(self, request):
        qs = super(PaperworkAdmin, self).get_queryset(request)
        return qs.filter(asset__isnull=True)


admin.site.register(Paperwork, PaperworkAdmin)

#######################################################################
