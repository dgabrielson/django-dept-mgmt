"""
Forms for the it_mgmt application.
"""
########################
from __future__ import print_function, unicode_literals

from django import forms
from django.core.exceptions import ValidationError
from django.db import models

from .models import (
    Computer,
    ComputerKey,
    IPAddress,
    Licence,
    NetworkInterface,
    WorkNote,
)

######################################################################
#######################################################################


class ComputerForm(forms.ModelForm):
    """
    Form for Computer objects
    """

    class Meta:
        model = Computer
        widgets = {
            "admin_user": forms.widgets.TextInput(attrs={"autocomplete": "off"}),
            "admin_password": forms.widgets.PasswordInput(
                render_value=True, attrs={"autocomplete": "off"}
            ),
        }
        exclude = []


#######################################################################


class NetworkInterfaceForm(forms.ModelForm):
    """
    This restricts the IP Address selection to either the currently set IP
    (if one is set) or those IPs currently marked as NOT in use.
    """

    def __init__(self, *args, **kwargs):
        super(NetworkInterfaceForm, self).__init__(*args, **kwargs)
        instance = kwargs.get("instance", None)  # a NetworkInterface
        IPAddressField = self.fields["ip_address"]
        if instance is not None and instance.ip_address is not None:
            IPAddressField.queryset = IPAddressField.queryset.filter(
                models.Q(in_use=False) | models.Q(pk=instance.ip_address.pk)
            )
        else:
            IPAddressField.queryset = IPAddressField.queryset.filter(in_use=False)
        #

    class Meta:
        model = NetworkInterface
        widgets = {
            "name": forms.widgets.TextInput(attrs={"size": 16}),
            "mac_address": forms.widgets.TextInput(attrs={"size": 16}),
        }
        exclude = []


#######################################################################


class BaseNetworkInterfaceInlineFormSet(forms.models.BaseInlineFormSet):
    """
    Used for the formset when attached to a Computer,
    provide a custom clean method.
    Using this formset for multiple Computer Interfaces is pretty
    meaningless.
    """

    def _check_unique(self, list_):
        """
        Check that the list consists of unique elements.
        """
        s = set(list_)
        return len(s) == len(list_)

    def clean(self):
        """
        Custom clean method to validate that only one interface
        is set primary.
        """
        result = super(BaseNetworkInterfaceInlineFormSet, self).clean()

        # check that there is only one primary
        primary_list = [int(form.cleaned_data["primary"]) for form in self.forms]
        count = sum(primary_list)
        if count > 1:
            raise ValidationError("Only one network interface can be primary")

        # NOTE: while it *seems* like a good idea to check for unique MAC
        #   address, this fails in cases like virtual interfaces, or bridges.

        # check that all IP address are either None or unique
        ip_list = [
            form.cleaned_data.get("ip_address", None)
            for form in self.forms
            if form.cleaned_data.get("ip_address", None) is not None
        ]
        if not self._check_unique(ip_list):
            raise ValidationError("Cannot assign duplicate IP Addresses")

        return result


NetworkInterfaceInlineFormSet = forms.models.inlineformset_factory(
    Computer,
    NetworkInterface,
    form=NetworkInterfaceForm,
    formset=BaseNetworkInterfaceInlineFormSet,
)

#######################################################################


class ComputerKeyForm(forms.ModelForm):
    """
    Override the value widget
    """

    class Meta:
        model = ComputerKey
        widgets = {"key": forms.widgets.TextInput(attrs={"size": 64})}
        exclude = []


#######################################################################


class ItMgmtComputerValueForm(forms.ModelForm):
    """
    Override the value widget
    """

    class Meta:
        widgets = {"value": forms.widgets.TextInput(attrs={"size": 64})}
        exclude = []


#######################################################################


class WorkNoteForm(ItMgmtComputerValueForm):
    """
    Form for work notes.
    """

    class Meta(ItMgmtComputerValueForm.Meta):
        model = WorkNote
        exclude = []


#######################################################################


class LicenceForm(ItMgmtComputerValueForm):
    """
    Form for work notes.
    """

    class Meta(ItMgmtComputerValueForm.Meta):
        model = Licence
        exclude = []


#######################################################################
