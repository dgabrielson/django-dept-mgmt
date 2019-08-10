#######################
from __future__ import print_function, unicode_literals

from django.conf.urls import include, url
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter

from . import views

#######################
###############################################################

###############################################################

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r"computers", views.ComputerViewSet)
router.register(r"flags", views.ComputerFlagViewSet)
router.register(r"networkinterfaces", views.NetworkInterfaceViewSet)
router.register(r"clientidentifiers", views.ClientIdentifierViewSet)
router.register(r"worknotes", views.WorkNoteViewSet)
router.register(r"licences", views.LicenceViewSet)
router.register(r"ipaddresses", views.IPAddressViewSet)

###############################################################

# The API URLs are now determined automatically by the router.
# Additionally, we include the login URLs for the browsable API.
urlpatterns = [
    url(r"^", include(router.urls)),
    url(r"^api-auth/", include("rest_framework.urls", namespace="itmgmt_api")),
    url(r"^api-token-auth/", obtain_auth_token),
]

###############################################################
