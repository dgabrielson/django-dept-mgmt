"""
Views for the it_mgmt application
"""
#######################################################################
#######################
from __future__ import print_function, unicode_literals

import logging

from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic.base import RedirectView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from office_mgmt.models import Asset

from .models import Computer, NetworkInterface, Status

#######################

#######################################################################

# Get an instance of a logger
logger = logging.getLogger(__name__)

#######################################################################


class ComputerStatusMixin(object):
    queryset = Status.objects.active().computers()

    def get_template_names(self):
        names = super(ComputerStatusMixin, self).get_template_names()
        names.insert(
            0, "it_mgmt/computerstatus{0}.html".format(self.template_name_suffix)
        )
        return names


#######################################################################


class ComputerStatusListView(ComputerStatusMixin, ListView):
    """
    List the model
    """


computer_status_list = ComputerStatusListView.as_view()
computer_status_list_permreq = permission_required("it_mgmt.change_computer")(
    computer_status_list
)

#######################################################################


class ComputerStatusDetailView(ComputerStatusMixin, DetailView):
    """
    Detail for the model
    """


computer_status_detail = ComputerStatusDetailView.as_view()
computer_status_detail_permreq = permission_required("it_mgmt.change_computer")(
    computer_status_detail
)

#######################################################################
#######################################################################
#######################################################################


@permission_required("it_mgmt.change_computer")
def this_computer(request):
    """
    Find the computer record that corresponds to the remote IP address,
    redirect to the appropriate record in the admin form.

    NOTE:
    This relies on the _meta options:
        Computer._meta.app_label and Computer._meta.object_name
    It also uses the admin change view.
    """
    ip_string = request.META.get("REMOTE_ADDR", None)
    if ip_string is None:
        raise Http404

    iface_list = NetworkInterface.objects.filter(ip_address__number__exact=ip_string)
    pk_set = iface_list.values_list("computer", flat=True).distinct()
    computer_list = Computer.objects.filter(pk__in=pk_set)
    count = computer_list.count()
    if count == 0:
        raise Http404

    app_label = Computer._meta.app_label.lower()
    obj_name = Computer._meta.object_name.lower()

    if count == 1:
        computer = computer_list.get()
        url = reverse(
            "admin:{0}_{1}_change".format(app_label, obj_name), args=[computer.pk]
        )
        return HttpResponseRedirect(url)

    if count > 1:
        # return the admin view with the restricted queryset.
        url = reverse("admin:{0}_{1}_changelist".format(app_label, obj_name))
        request.session["admin:computer-restrict-queryset"] = {"pk__in": pk_set}
        return HttpResponseRedirect(url)

    # This should never happen.
    raise Http404


#######################################################################


class RedirectFromAssetToComputer(RedirectView):
    """
    This is a special view that does something a little bit "naughty":
    - check to see if there is an existing Computer for this asset.
    - if not, create one, using the asset as a starting point.
    - redirect to the computer.
    - this view expects "asset=<pk>" as a query string ; or <asset>
      as a primary key to be specified in the url pattern.
    """

    permanent = False

    def get_redirect_url(self, **kwargs):
        logger.debug("RedirectFromAssetToComputer.get_redirect_url()")
        app_label = Computer._meta.app_label.lower()
        obj_name = Computer._meta.object_name.lower()
        asset_pk = kwargs.get("asset", None)
        logger.debug("got asset pk = {0}".format(asset_pk))
        if asset_pk is None:
            # just go to the computer list.
            logger.debug("asset pk is None, going to changelist")
            return reverse("admin:{0}_{1}_changelist".format(app_label, obj_name))
        try:
            asset = Asset.objects.get(pk=asset_pk)
        except Asset.DoesNotExist:
            logger.debug("asset does not exist, going to changelist")
            return reverse("admin:{0}_{1}_changelist".format(app_label, obj_name))
        # check for pre-existing computer record.
        count = asset.computer_set.count()
        logger.debug("asset loaded, computer set count = {0}".format(count))

        if count == 1:
            computer = asset.computer_set.get()
            logger.debug(
                "computer loaded, going to change form for computer.pk = {0}".format(
                    computer.pk
                )
            )
            return reverse(
                "admin:{0}_{1}_change".format(app_label, obj_name), args=(computer.pk,)
            )

        if count > 1:
            # return the admin view with the restricted queryset.
            pk_set = asset.computer_set.values_list("pk", flat=True)
            request.session["admin:computer-restrict-queryset"] = {"pk__in": pk_set}
            logger.debug(
                "multiple computers for this asset, going to restricted change list form for computer.pk = {0}".format(
                    list(pk_set)
                )
            )
            return reverse("admin:{0}_{1}_changelist".format(app_label, obj_name))

        if count == 0:
            computer = Computer(
                common_name="asset computer record",
                hardware=asset.description,
                asset=asset,
                person=asset.person,
                room=asset.room,
            )
            computer.save()
            logger.debug(
                "computer CREATED, going to change form for computer.pk = {0}".format(
                    computer.pk
                )
            )
            msg = "New computer record created"
            messages.success(self.request, msg, fail_silently=True)
            return reverse(
                "admin:{0}_{1}_change".format(app_label, obj_name), args=(computer.pk,)
            )

        # This should never happen.
        logger.error("invalid execution path for this view")
        raise Http404


redirect_asset_to_computer = permission_required("it_mgmt.create_computer")(
    RedirectFromAssetToComputer.as_view()
)

#######################################################################
