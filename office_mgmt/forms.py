"""
Forms for the office_mgmt application.
"""
#######################
from __future__ import print_function, unicode_literals

from django import forms

from .models import LoanGroup, LoanItem, LoanRecord

#######################
#######################################################################

#######################################################################
#######################################################################


class LoanRecordForm(forms.ModelForm):
    """
    This restricts the person selection to people who are in any of the 
    LoanGroups.  It also restricts the LoanItems to those that are currently
    *not* Loaned out.
    """

    item = forms.ModelChoiceField(queryset=LoanItem.objects.available())
    person = forms.ModelChoiceField(
        queryset=LoanGroup.objects.active().person_queryset().active()
    )

    class Meta:
        model = LoanRecord
        exclude = []


#######################################################################


class LoanItemForm(forms.ModelForm):
    """
    Form for LoadItems
    """

    class Meta:
        model = LoanItem
        exclude = []


#######################################################################


class LoanGroupForm(forms.ModelForm):
    """
    Form for LoanGroup
    """

    class Meta:
        model = LoanGroup
        exclude = []


#######################################################################
