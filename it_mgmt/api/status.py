#######################
from __future__ import print_function, unicode_literals

from django.conf.urls import url
from django.core.paginator import InvalidPage, Paginator
from django.http import Http404

from tastypie import fields

# from tastypie.authorization import Authorization
from tastypie.resources import ALL, ALL_WITH_RELATIONS, ModelResource
from tastypie.utils import trailing_slash

from ..models import Status, StatusKey
from . import (
    ComputerRelatedResourceMixin,
    ItMgmtAuthentication,
    ItMgmtAuthorization,
    PrettyJSONSerializer,
)
from .computer import ComputerResource

#######################
"""
API for Status updates.
"""

#######################################################################

#######################################################################


class StatusKeyResource(ModelResource):
    class Meta:
        queryset = StatusKey.objects.active()
        serializer = PrettyJSONSerializer()
        authentication = ItMgmtAuthentication()
        authorization = ItMgmtAuthorization()
        filtering = {"slug": ALL}


#######################################################################


class StatusResource(ComputerRelatedResourceMixin, ModelResource):
    computer = fields.ForeignKey(ComputerResource, "computer")
    key = fields.ForeignKey(StatusKeyResource, "key")

    class Meta:
        queryset = Status.objects.active()
        serializer = PrettyJSONSerializer()
        authentication = ItMgmtAuthentication()
        authorization = ItMgmtAuthorization()
        filtering = {"key": ALL_WITH_RELATIONS, "computer": ALL_WITH_RELATIONS}
        # required for _latest dispatch...
        latest_allowed_methods = ["get"]

    def prepend_urls(self):
        return [
            url(
                r"^(?P<resource_name>{0})/latest{1}$".format(
                    self._meta.resource_name, trailing_slash()
                ),
                self.wrap_view("dispatch_latest"),
                name="api_get_latest",
            )
        ]

    def dispatch_latest(self, request, **kwargs):
        """
        Relies on ``Resource.dispatch`` for the heavy-lifting.
        """
        return self.dispatch("latest", request, **kwargs)

    def get_latest(self, request, **kwargs):
        """
        Just like ``Resource.get_list`` except for the queryset
        Get the latest status updates by key.
        """
        """
        Returns a serialized list of resources.

        Calls ``obj_get_list`` to provide the data, then handles that result
        set and serializes it.

        Should return a HttpResponse (200 OK).
        """
        # TODO: Uncached for now. Invalidation that works for everyone may be
        #       impossible.
        base_bundle = self.build_bundle(request=request)
        # next line is the only variation between this and get_list:
        objects = self.obj_get_latest(
            bundle=base_bundle, **self.remove_api_resource_names(kwargs)
        )
        sorted_objects = self.apply_sorting(objects, options=request.GET)

        paginator = self._meta.paginator_class(
            request.GET,
            sorted_objects,
            resource_uri=self.get_resource_uri(),
            limit=self._meta.limit,
            max_limit=self._meta.max_limit,
            collection_name=self._meta.collection_name,
        )
        to_be_serialized = paginator.page()

        # Dehydrate the bundles in preparation for serialization.
        bundles = []

        for obj in to_be_serialized[self._meta.collection_name]:
            bundle = self.build_bundle(obj=obj, request=request)
            bundles.append(self.full_dehydrate(bundle))

        to_be_serialized[self._meta.collection_name] = bundles
        to_be_serialized = self.alter_list_data_to_serialize(request, to_be_serialized)
        return self.create_response(request, to_be_serialized)

    def obj_get_latest(self, bundle, **kwargs):
        """
        A a clone of ``ModelResource.obj_get_list``.

        Takes an optional ``request`` object, whose ``GET`` dictionary can be
        used to narrow the query.
        """
        filters = {}

        if hasattr(bundle.request, "GET"):
            # Grab a mutable copy.
            filters = bundle.request.GET.copy()

        # Update with the provided kwargs.
        filters.update(kwargs)
        # Added to obj.get_list
        keys = filters.pop("keys", None)
        key_slugs = []
        for k in keys:
            key_slugs.extend(k.split(","))

        applicable_filters = self.build_filters(filters=filters)

        try:
            objects = self.apply_filters(bundle.request, applicable_filters)
            # added to obj_get_list:
            objects = objects.latest_by_key(key_slugs)
            return self.authorized_read_list(objects, bundle)
        except ValueError:
            raise BadRequest("Invalid resource lookup data provided (mismatched type).")


#######################################################################
