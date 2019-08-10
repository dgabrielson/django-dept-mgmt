from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django_select2.forms import ModelSelect2Widget
from django_select2.views import AutoResponseView
from people.models import Person
from places.models import Room

from .models import IPAddress


class LoginSelect2View(LoginRequiredMixin, AutoResponseView):
    pass


class PersonSelect2Widget(ModelSelect2Widget):
    model = Person
    queryset = Person.objects.filter(active=True, flags__slug="asset-owner")
    search_fields = [
        "cn__icontains",
        "username__icontains",
        "emailaddress__address__icontains",
    ]

    def label_from_instance(self, obj):
        if obj.username:
            return "{obj.cn} [{obj.username}]".format(obj=obj)
        return str(obj)


class RoomSelect2Widget(ModelSelect2Widget):
    model = Room
    queryset = Room.objects.filter(active=True)
    search_fields = ["number__icontains", "building__icontains"]


class IPAddressSelect2Widget(ModelSelect2Widget):
    model = IPAddress
    queryset = IPAddress.objects.filter(active=True)
    search_fields = ["number__icontains", "hostname__icontains", "aliases__icontains"]
