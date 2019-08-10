"""
Admin classes for the  it_mgmt application
"""
########################
from __future__ import print_function, unicode_literals

from django.conf import settings
from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from mgmt_common.admin import (
    MgmtActiveAdminMixin,
    PersonFilter,
    RoomFilter,
    choice_field_update,
    mark_inactive,
)

from .forms import (
    ComputerForm,
    ComputerKeyForm,
    LicenceForm,
    NetworkInterfaceForm,
    NetworkInterfaceInlineFormSet,
    WorkNoteForm,
)
from .models import (
    DATATYPE_CHOICES,
    ClientIdentifier,
    Computer,
    ComputerFlag,
    ComputerKey,
    IPAddress,
    Licence,
    NetworkInterface,
    StatusKey,
    WorkNote,
)
from .views import redirect_asset_to_computer, this_computer
from .widgets import LoginSelect2View, PersonSelect2Widget, RoomSelect2Widget

######################################################################

try:
    from django.contrib.auth import get_user_model
except ImportError:
    # pre Django 1.5 fallback.
    from django.contrib.auth.models import User

    UserModel = User
else:
    UserModel = get_user_model()

#######################################################################
#######################################################################


class WorkNoteMixin(object):
    """
    A mixin to help deal with the WorkNote form user field.
    """

    form = WorkNoteForm

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "user":
            kwargs["initial"] = request.user.pk
            kwargs["queryset"] = UserModel.objects.filter(pk=kwargs["initial"])
            return db_field.formfield(**kwargs)
        return super(WorkNoteMixin, self).formfield_for_foreignkey(
            db_field, request, **kwargs
        )

    def save_model(self, request, obj, form, change):
        if not change:
            obj.user = request.user
        obj.save()


#######################################################################


class NetworkInterfaceInline(admin.TabularInline):
    model = NetworkInterface
    # Note: We must specify both form and formset for the admin Inline.
    form = NetworkInterfaceForm
    formset = NetworkInterfaceInlineFormSet
    autocomplete_fields = ["ip_address"]
    extra = 0


#######################################################################


class WorkNoteInline(WorkNoteMixin, admin.TabularInline):
    model = WorkNote
    readonly_fields = ["created"]
    extra = 0


#######################################################################


class LicenceInline(admin.TabularInline):
    model = Licence
    form = LicenceForm
    extra = 0


#######################################################################


class ClientIdentifierInline(admin.TabularInline):
    model = ClientIdentifier
    extra = 0


#######################################################################


class ComputerKeyInline(admin.TabularInline):
    model = ComputerKey
    form = ComputerKeyForm
    extra = 0


#######################################################################


class ComputerAdmin(MgmtActiveAdminMixin, admin.ModelAdmin):
    """
    Admin class for the Computer model.
    """

    autocomplete_fields = ["asset", "flags"]
    fields = [
        "active",
        "common_name",
        "hardware",
        "host_id",
        "person",
        "room",
        "asset",
        "operating_system",
        "processor",
        "ram",
        "harddrive",
        "manufacturing_year",
        "flags",
        "notes",
    ]
    list_display = ["common_name", "hardware"]
    list_filter = ["active", "flags", PersonFilter, RoomFilter, "created", "modified"]
    search_fields = [
        "common_name",
        "hardware",
        "asset__serial_number",
        "asset__property_number",
        "networkinterface__mac_address",
        "networkinterface__ip_address__number",
        "networkinterface__ip_address__hostname",
    ]
    # filter_horizontal = ['flags', ]
    inlines = [
        NetworkInterfaceInline,
        ClientIdentifierInline,
        WorkNoteInline,
        LicenceInline,
    ]

    save_as = True
    save_on_top = True
    form = ComputerForm
    actions = [mark_inactive]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "person":
            kwargs["widget"] = PersonSelect2Widget(
                attrs={
                    "style": "width:260px;",
                    #'data-minimum-input-length': 1,
                },
                data_view="admin:it_mgmt_computer_select2-json",
            )
        if db_field.name == "room":
            kwargs["widget"] = RoomSelect2Widget(
                attrs={
                    "style": "width:260px;",
                    #'data-minimum-input-length': 1,
                },
                data_view="admin:it_mgmt_computer_select2-json",
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_actions(self, request):
        """
        https://docs.djangoproject.com/en/dev/ref/contrib/admin/actions/#django.contrib.admin.ModelAdmin.get_actions

        This returns a dictionary of actions allowed.
        The keys are action names, and the values are
        (function, name, short_description) tuples.
        """

        def _flagger(m2m_fieldname, action, flag):
            """
            Generate an update action function m2m flags.
            The 'action' must be valid on the m2m manager.
            """

            def _updater_f(ma, r, qs):
                for o in qs:
                    m2m_manager = getattr(o, m2m_fieldname)
                    f = getattr(m2m_manager, action)
                    f(flag)

            description = "{0} flag: {1}".format(action.title(), flag)
            name = "{0}_flag_{1}".format(action, flag.slug)
            return _updater_f, name, description

        # end sub-function _flagger

        actions = super(ComputerAdmin, self).get_actions(request)

        for flag in ComputerFlag.objects.active():
            for action in ["add", "remove"]:
                f, name, desc = _flagger("flags", action, flag)
                actions[name] = f, name, desc

        return actions

    def get_urls(self):
        """
        Extend the admin urls for this model.
        Provide a link by subclassing the admin change_form,
        and adding to the object-tools block.
        """
        urls = super(ComputerAdmin, self).get_urls()
        urls = [
            url(
                r"^this/$",
                self.admin_site.admin_view(this_computer),
                name="it_mgmt_computer_this",
            ),
            url(
                r"^redirect-from-asset/(?P<asset>\d+)/$",
                self.admin_site.admin_view(redirect_asset_to_computer),
                name="it_mgmt_computer_from_asset",
            ),
            url(
                r"^select2.json$",
                self.admin_site.admin_view(LoginSelect2View.as_view()),
                name="it_mgmt_computer_select2-json",
            ),
        ] + urls
        return urls

    def get_queryset(self, request):
        """
        This function restricts the default queryset in the
        admin list view.
        """
        qs = super(ComputerAdmin, self).get_queryset(request)
        if "admin:computer-restrict-queryset" in request.session:
            qs = qs.filter(**request.session["admin:computer-restrict-queryset"])
            del request.session["admin:computer-restrict-queryset"]
        if request.user.is_superuser:
            return qs
        return qs.active()


admin.site.register(Computer, ComputerAdmin)

#######################################################################


class NetworkInterfaceAdmin(MgmtActiveAdminMixin, admin.ModelAdmin):
    list_display = ["name", "computer", "primary", "type", "mac_address", "ip_address"]
    list_filter = ["type", "primary", "name"]
    search_fields = ["mac_address"]
    readonly_fields = [
        "active",
        "name",
        "computer",
        "primary",
        "type",
        "mac_address",
        "ip_address",
    ]


admin.site.register(NetworkInterface, NetworkInterfaceAdmin)

#######################################################################


class IPAddressAdmin(MgmtActiveAdminMixin, admin.ModelAdmin):
    list_display = ["number", "hostname", "in_use", "aliases"]
    list_filter = ["active", "in_use"]
    ordering = ["number"]
    actions = [mark_inactive]
    search_fields = ["hostname", "number", "aliases"]


admin.site.register(IPAddress, IPAddressAdmin)

#######################################################################


class ComputerFlagAdmin(admin.ModelAdmin):
    list_display = ["verbose_name", "slug", "active"]
    search_fields = ["slug", "verbose_name"]
    list_filter = ["active"]
    prepopulated_fields = {"slug": ("verbose_name",)}
    fieldsets = ((None, {"fields": ["active", "verbose_name", "slug"]}),)


admin.site.register(ComputerFlag, ComputerFlagAdmin)

#######################################################################


class OptionalComputerBaseAdmin(admin.ModelAdmin):
    exclude = ["computer"]

    def get_queryset(self, request):
        qs = super(OptionalComputerBaseAdmin, self).get_queryset(request)
        return qs.unattached()


#######################################################################


class WorkNoteAdmin(WorkNoteMixin, OptionalComputerBaseAdmin):
    list_display = ["value", "user"]
    raw_id_fields = ("user",)


admin.site.register(WorkNote, WorkNoteAdmin)

#######################################################################


class LicenceAdmin(OptionalComputerBaseAdmin):
    form = LicenceForm
    search_fields = ["value"]


admin.site.register(Licence, LicenceAdmin)

#######################################################################

DATATYPE_ACTION_LIST = []
for code, desc in DATATYPE_CHOICES:
    DATATYPE_ACTION_LIST.append(
        choice_field_update("data_type", "data type", code, desc)
    )


class StatusKeyAdmin(MgmtActiveAdminMixin, admin.ModelAdmin):
    """
    Admin for the StatusKey objects.
    Allows setting and clearing the volatile flag, as well as setting
    the data type to any of the available options.
    """

    list_display = ("verbose_name", "volatile", "data_type")
    search_fields = ("slug", "verbose_name")
    list_filter = ("active", "volatile", "data_type")
    actions = ["set_volatile", "clear_volatile"] + DATATYPE_ACTION_LIST

    def set_volatile(self, request, queryset):
        queryset.update(volatile=True)

    set_volatile.short_description = "Set the volatile flag"

    def clear_volatile(self, request, queryset):
        queryset.update(volatile=False)

    clear_volatile.short_description = "Clear the volatile flag"


admin.site.register(StatusKey, StatusKeyAdmin)

#######################################################################
