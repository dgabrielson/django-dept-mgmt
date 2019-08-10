#######################
from __future__ import print_function, unicode_literals

from django.conf.urls import include, url

from . import views

#######################
"""
The url patterns for the it_mgmt application.
"""

urlpatterns = [
    url(
        r"^computer-status/$",
        views.computer_status_list_permreq,
        name="it_mgmt-computer-status-list",
    ),
    url(
        r"^computer-status/(?P<pk>\d+)/$",
        views.computer_status_detail_permreq,
        name="it_mgmt-computer-status-detail",
    ),
    url(r"^api/", include("it_mgmt.api.urls")),
]
