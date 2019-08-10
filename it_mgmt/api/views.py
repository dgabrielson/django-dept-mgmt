#######################
from __future__ import print_function, unicode_literals

import json
import logging

from django.http import Http404, HttpResponse
from django.utils import six
from django.views.generic.base import TemplateView
from django.views.generic.detail import BaseDetailView

from ..models import ClientIdentifier, Computer
from ..utils.random_names import get_random_name
from .ipware import get_ip

#######################
"""
API views
"""
#######################################################################

#######################################################################

# Get an instance of a logger
logger = logging.getLogger(__name__)

#######################################################################


class ComputerMixin(object):
    model = Computer


#######################################################################


class ComputerBaseDetailView(ComputerMixin, BaseDetailView):
    pass


#######################################################################


class ByRequestMixin(object):
    def get_object(self, queryset=None):
        """
        Returns the object the view is displaying.
        """
        # Use a custom queryset if provided; this is required for subclasses
        # like DateDetailView
        if queryset is None:
            queryset = self.get_queryset()
        ip_string = get_ip(self.request)
        if ip_string is None:
            raise Http404("Cannot determine IP address of client")
        queryset = queryset.filter(networkinterface__ip_address__number=ip_string)
        try:
            # Get the single item from the filtered queryset
            obj = queryset.get()
        except queryset.model.DoesNotExist:
            raise Http404("No computer found")
        return obj


#######################################################################


class ByHostIdMixin(object):
    def get_object(self, queryset=None):
        """
        Returns the object the view is displaying.
        Views require a host_id parameter in the url.
        """
        # Use a custom queryset if provided; this is required for subclasses
        # like DateDetailView
        if queryset is None:
            queryset = self.get_queryset()

        host_id = self.kwargs.get("host_id", None)
        if not host_id:
            raise Http404("No host ID specified")
        queryset = queryset.filter(host_id=host_id)
        try:
            # Get the single item from the filtered queryset
            obj = queryset.get()
        except queryset.model.DoesNotExist:
            raise Http404("No computer found")
        return obj


#######################################################################


class TextResponseMixin(object):
    """
    This will require one of the TextMixin-s also.
    """

    def render_to_response(self, context, **response_kwargs):
        data = self.get_data(context)
        if not isinstance(data, six.string_types):
            data = "{0}".format(data)
        response_kwargs["content_type"] = "text/plain"
        return HttpResponse(data, **response_kwargs)


#######################################################################


class JsonResponseMixin(object):
    """
    This will require one of the JsonMixin-s also.
    """

    def render_to_response(self, context, **response_kwargs):
        data = self.get_data(context)
        response_kwargs["content_type"] = "text/json"
        return HttpResponse(json.dumps(data), **response_kwargs)


#######################################################################
#######################################################################


class CommonNameTextMixin(TextResponseMixin):
    """
    Return the text string for the common name of the computer making
    this request.
    """

    def get_data(self, context):
        return context["object"].common_name


#######################################################################


class FlagsTextMixin(TextResponseMixin):
    """
    Return the text string for the common name of the computer making
    this request.
    """

    def get_data(self, context):
        obj = context["object"]
        return "\n".join(obj.flags.values_list("slug", flat=True))


#######################################################################


class ClientIdentifierListTextMixin(TextResponseMixin):
    """
    Return the text string for the common name of the computer making
    this request.
    """

    def get_data(self, context):
        obj = context["object"]
        return "\n".join(
            [
                key + "\t" + value
                for key, value in obj.clientidentifier_set.values_list("key", "value")
            ]
        )


#######################################################################


class ClientIdentifierDetailTextMixin(TextResponseMixin):
    """
    Return the text string for the common name of the computer making
    this request.
    """

    def get_data(self, context):
        obj = context["object"]
        key = self.kwargs.get("client_id", None)
        if key is None:
            raise Http404("No client identifier requested")
        try:
            client_id = obj.clientidentifier_set.get(active=True, key=key)
        except ClientIdentifier.DoesNotExist:
            raise Http404("The named client identifier does not exist")
        else:
            return client_id.value


#######################################################################


class SetHostIdTextMixin(TextResponseMixin):
    """
    Set the host_id field for this computer.
    Returns "OK" when successful.
    This really is transitional to get host_id's into the system.
    """

    def get_data(self, context):
        """
        Expect to be called with ?host_id=... GET arg.
        Although really this should be PUT.
        """
        computer = context["object"]
        host_id = self.request.GET.get("host_id", "")
        if not host_id:
            return "No host_id"
        if not computer.host_id:
            computer.host_id = host_id
            computer.save()
            return "OK"
        return "Computer host_id already: " + computer.host_id


#######################################################################
#######################################################################


class ComputerByRequestCommonName(
    CommonNameTextMixin, ByRequestMixin, ComputerBaseDetailView
):
    pass


class ComputerByHostIdCommonName(
    CommonNameTextMixin, ByHostIdMixin, ComputerBaseDetailView
):
    pass


class ComputerByRequestFlags(FlagsTextMixin, ByRequestMixin, ComputerBaseDetailView):
    pass


class ComputerByHostIdFlags(FlagsTextMixin, ByHostIdMixin, ComputerBaseDetailView):
    pass


class ComputerByRequestClientIdentifierList(
    ClientIdentifierListTextMixin, ByRequestMixin, ComputerBaseDetailView
):
    pass


class ComputerByHostIdClientIdentifierList(
    ClientIdentifierListTextMixin, ByHostIdMixin, ComputerBaseDetailView
):
    pass


class ComputerByRequestClientIdentifierDetail(
    ClientIdentifierDetailTextMixin, ByRequestMixin, ComputerBaseDetailView
):
    pass


class ComputerByHostIdClientIdentifierDetail(
    ClientIdentifierDetailTextMixin, ByHostIdMixin, ComputerBaseDetailView
):
    pass


class ComputerByRequestSetHostId(
    SetHostIdTextMixin, ByRequestMixin, ComputerBaseDetailView
):
    pass


#######################################################################


class RandomName(TemplateView):
    """
    Return a text string for a randomly generated name.
    """

    def render_to_response(self, context, **response_kwargs):
        """
        generate a random (slug-style) label
        """
        data = get_random_name()
        response_kwargs["content_type"] = "text/plain"
        return HttpResponse(data, **response_kwargs)


#######################################################################
