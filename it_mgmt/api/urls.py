#######################
from __future__ import print_function, unicode_literals

from django.conf.urls import include, url

from .views import (
    ComputerByHostIdClientIdentifierDetail,
    ComputerByHostIdClientIdentifierList,
    ComputerByHostIdCommonName,
    ComputerByHostIdFlags,
    ComputerByRequestClientIdentifierDetail,
    ComputerByRequestClientIdentifierList,
    ComputerByRequestCommonName,
    ComputerByRequestFlags,
    ComputerByRequestSetHostId,
    RandomName,
)

#######################
"""
API urls for IT Management.

Make sure your server configuration passes the authorization header.
Apache and mod_wsgi requires you to add:

    WSGIPassAuthorization On

See http://www.nerdydork.com/basic-authentication-on-mod_wsgi.html.

"""
#######################################################################

#######################################################################

urlpatterns = [
    url(r"^random-name/$", RandomName.as_view(), name="it-mgmt-api-random-name"),
    url(
        r"^computer-by-request/common-name/$",
        ComputerByRequestCommonName.as_view(),
        name="it-mgmt-api-computer-by-request-common-name",
    ),
    url(
        r"^computer-by-request/flags/$",
        ComputerByRequestFlags.as_view(),
        name="it-mgmt-api-computer-by-request-flags",
    ),
    url(
        r"^computer-by-request/client-id/$",
        ComputerByRequestClientIdentifierList.as_view(),
        name="it-mgmt-api-computer-by-request-client-id-list",
    ),
    url(
        r"^computer-by-request/client-id/(?P<client_id>[\w-]+)/$",
        ComputerByRequestClientIdentifierDetail.as_view(),
        name="it-mgmt-api-computer-by-request-client-id-detail",
    ),
    url(
        r"^computer-by-request/set-host-id/$",
        ComputerByRequestSetHostId.as_view(),
        name="it-mgmt-api-computer/(?<host_id>[\w-]+)-set-host-id",
    ),
    url(
        r"^computer/(?P<host_id>[\w-]+)/common-name/$",
        ComputerByHostIdCommonName.as_view(),
        name="it-mgmt-api-computer-by-hostid-common-name",
    ),
    url(
        r"^computer/(?P<host_id>[\w-]+)/flags/$",
        ComputerByHostIdFlags.as_view(),
        name="it-mgmt-api-computer-by-hostid-flags",
    ),
    url(
        r"^computer/(?P<host_id>[\w-]+)/client-id/$",
        ComputerByHostIdClientIdentifierList.as_view(),
        name="it-mgmt-api-computer-by-hostid-client-id-list",
    ),
    url(
        r"^computer/(?P<host_id>[\w-]+)/client-id/(?P<client_id>[\w-]+)/$",
        ComputerByHostIdClientIdentifierDetail.as_view(),
        name="it-mgmt-api-computer-by-hostid-client-id-detail",
    ),
    url(r"^v1/", include("it_mgmt.api.rest_v1.urls")),
]

#######################################################################
