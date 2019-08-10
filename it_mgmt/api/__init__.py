#######################
from __future__ import print_function, unicode_literals

import logging

from ..models import Computer, ComputerKey, NetworkInterface, Status, StatusKey

#######################
"""
Core API for IT Management application.

Tastypie References:
* https://django-tastypie.readthedocs.org/en/latest/toc.html
* http://blog.gingerlime.com/2012/keep-your-hands-off-my-tastypie/
"""
#######################################################################


# from django.core.serializers.json import DjangoJSONEncoder
# import json

# from tastypie.authentication import ApiKeyAuthentication, MultiAuthentication
# from tastypie.authorization import DjangoAuthorization
# from tastypie.exceptions import Unauthorized
# from tastypie.http import HttpUnauthorized
# from tastypie.serializers import Serializer


#######################################################################

# Get an instance of a logger
logger = logging.getLogger(__name__)

#######################################################################

COMPUTER_RELATED_MODELS = [NetworkInterface, Status]

#######################################################################

# class PrettyJSONSerializer(Serializer):
#     json_indent = 4
#
#     def to_json(self, data, options=None):
#         options = options or {}
#         data = self.to_simple(data, options)
#         return json.dumps(data, cls=DjangoJSONEncoder,
#                 sort_keys=True, ensure_ascii=False,
#                 indent=self.json_indent) + '\n'

#######################################################################

# class ComputerAuthentication(ApiKeyAuthentication):
#     """
#     Heavily based on ApiKeyAuthentication.
#
#     Handles API key auth, in which a user provides a computer id & API key.
#
#     Uses the ``ComputerKey`` model.
#     """
#     def extract_credentials(self, request):
#         logger.debug('ComputerAuthentication: trying to extract credentials...')
#         if 'HTTP_AUTHORIZATION' in request.META:
#             logger.debug('ComputerAuthentication: Found HTTP_AUTHORIZATION = {0!r}'.format(request.META['HTTP_AUTHORIZATION']))
#         if request.META.get('HTTP_AUTHORIZATION') and request.META['HTTP_AUTHORIZATION'].lower().startswith('computerkey '):
#             (auth_type, data) = request.META['HTTP_AUTHORIZATION'].split(None, 1)
#
#             if auth_type.lower() != 'computerkey':
#                 raise ValueError("Incorrect authorization header.")
#
#             computer, api_key = data.split(':', 1)
#         else:
#             computer = request.GET.get('computer') or request.POST.get('computer')
#             api_key = request.GET.get('api_key') or request.POST.get('api_key')
#             logger.debug('ComputerAuthentication: Auth from GET or POST; computer={0!r}; api_key={1!r}'.format(computer, api_key))
#
#         return computer, api_key
#
#
#     def is_authenticated(self, request, **kwargs):
#         """
#         Finds the computer and checks the corresponding API key.
#        ``HttpResponse`` if you need something custom.
#         """
#         try:
#             computer_id, api_key = self.extract_credentials(request)
#             logger.debug('ComputerAuthentication: computer_id = {0!r}; api_key = {1!r}'.format(computer_id, api_key))
#         except ValueError:
#             logger.debug('ComputerAuthentication: extracting credentials resulted in ValueError')
#             return self._unauthorized()
#
#         if not computer_id or not api_key:
#             logger.debug('ComputerAuthentication: missing either id or key')
#             return self._unauthorized()
#
#         try:
#             computer = Computer.objects.get(pk=computer_id)
#         except (Computer.DoesNotExist, Computer.MultipleObjectsReturned):
#             logger.debug('ComputerAuthentication: unique computer for this id does not exist')
#             return self._unauthorized()
#
#         if not computer.active:
#             logger.debug('ComputerAuthentication: computer not active')
#             return False
#
#         key_auth_check = self.get_key(computer, api_key)
#         if key_auth_check:
#             # insert the computer object into the request.
#             logger.info('ComputerAuthentication: computer object {0} authorized'.format(computer))
#             request.computer = computer
#             logger.debug('ComputerAuthentication: request id = {0}'.format(id(request)))
#         else:
#             logger.info('ComputerAuthentication: key check failed for computer object {0}'.format(computer))
#         return key_auth_check
#
#
#     def get_key(self, computer, api_key):
#         """
#         Attempts to find the API key for the computer.
#         This returns ``True`` when found and ``False`` otherwise.
#         """
#         try:
#             ComputerKey.objects.get(active=True, computer=computer,
#                                     key=api_key)
#         except ComputerKey.DoesNotExist:
#             return False
#         else:
#             return True
#         # fall-through returns None (equivalent to False).
#
#
# #######################################################################
#
# def ItMgmtAuthentication():
#     """
#     A helper function so that ItMgmt Authentication is handled consistently.
#     (DRY helper.)
#     """
#     return MultiAuthentication(ComputerAuthentication(),
#                                ApiKeyAuthentication(),
#                                )
#
# #######################################################################
#
# class ItMgmtAuthorization(DjangoAuthorization):
#     """
#     A specialized authorization object that deals with
#     request.computer as well as request.user.
#     """
#     # The related models *must* have a computer ForeignKey.
#     computer_related_models = (NetworkInterface, Status, )
#     computer_full_access_models = (StatusKey, )
#
#
#     def base_checks(self, request, model_cls):
#         if not hasattr(request, 'computer'):
#             # Django Authorization
#             result = super(ItMgmtAuthorization, self).base_checks(request, model_cls)
#         else:
#             # Computer Authorization
#             result = model_cls or getattr(model_cls, '_meta', None)
#         return result   # for compatibility
#
#
#     def computer_auth_list(self, object_list, bundle):
#         """
#         Inspect object_list; return a subset for access or
#         raise Unauthorized
#         """
#         logger.debug('ItMgmtAuthorization [list]: request id = {0}'.format(id(bundle.request)))
#         cls = self.base_checks(bundle.request, object_list.model)
#         logger.debug('ItMgmtAuthorization [list]: cls = {0!r}'.format(cls.__name__))
#         computer = bundle.request.computer
#         logger.debug('ItMgmtAuthorization [list]: computer = {0}'.format(computer))
#
#         result = []
#         if cls == Computer:
#             logger.debug('ItMgmtAuthorization [list]: this *is* a Computer')
#             result = object_list.filter(pk=computer.pk)
#         elif cls in self.computer_related_models:
#             logger.debug('ItMgmtAuthorization [list]: class is related')
#             result = object_list.filter(computer=computer)
#         elif cls in self.computer_full_access_models:
#             logger.debug('ItMgmtAuthorization [list]: computers have full access to this class')
#             result = object_list
#         else:
#             logger.debug('ItMgmtAuthorization [list]: Some unrelated class... not authorized')
#             raise Unauthorized()
#         return result
#
#
#     def computer_auth_detail(self, object_list, bundle):
#         """
#         Inspect bundle.obj.  Retur True for access or raise Unauthorized
#         """
#         logger.debug('ItMgmtAuthorization [detail]: request id = {0}'.format(id(bundle.request)))
#         cls = self.base_checks(bundle.request, object_list.model)
#         logger.debug('ItMgmtAuthorization [detail]: cls = {0!r}'.format(cls.__name__))
#         computer = bundle.request.computer
#         logger.debug('ItMgmtAuthorization [detail]: computer = {0}'.format(computer))
#         result = False
#         logger.debug('ItMgmtAuthorization [detail]: bundle.obj = {0}'.format(bundle.obj))
#         if cls == Computer:
#             logger.debug('ItMgmtAuthorization [detail]: this *is* a Computer')
#             result = bundle.obj == computer
#         elif cls in self.computer_related_models:
#             logger.debug('ItMgmtAuthorization [detail]: class is related')
#             result = bundle.obj.computer == computer
#         elif cls in self.computer_full_access_models:
#             logger.debug('ItMgmtAuthorization [detail]: computers have full access to this class')
#             result = True
#         else:
#             logger.debug('ItMgmtAuthorization [detail]: Some unrelated class... not authorized')
#             raise Unauthorized()
#         return result
#
#
#     def read_list(self, object_list, bundle):
#         if not hasattr(bundle.request, 'computer'):
#             logger.debug('ItMgmtAuthorization: read_list(): doing DjangoAuthorization')
#             return super(ItMgmtAuthorization, self).read_list(object_list, bundle)
#         # computer authorization
#         logger.debug('ItMgmtAuthorization: read_list(): doing Computer Authorization')
#         return self.computer_auth_list(object_list, bundle)
#
#
#     def read_detail(self, object_list, bundle):
#         if not hasattr(bundle.request, 'computer'):
#             logger.debug('ItMgmtAuthorization: read_detail(): doing DjangoAuthorization')
#             return super(ItMgmtAuthorization, self).read_detail(object_list, bundle)
#         # computer authorization
#         logger.debug('ItMgmtAuthorization: read_detail(): doing Computer Authorization')
#         return self.computer_auth_detail(object_list, bundle)
#
#
#     def create_list(self, object_list, bundle):
#         if not hasattr(bundle.request, 'computer'):
#             logger.debug('ItMgmtAuthorization: create_list(): doing DjangoAuthorization')
#             return super(ItMgmtAuthorization, self).create_list(object_list, bundle)
#         # computer authorization
#         logger.debug('ItMgmtAuthorization: create_list(): doing Computer Authorization')
#         return self.computer_auth_list(object_list, bundle)
#
#
#     def create_detail(self, object_list, bundle):
#         if not hasattr(bundle.request, 'computer'):
#             logger.debug('ItMgmtAuthorization: create_detail(): doing DjangoAuthorization')
#             return super(ItMgmtAuthorization, self).create_detail(object_list, bundle)
#         # computer authorization
#         logger.debug('ItMgmtAuthorization: create_detail(): doing Computer Authorization')
#         return self.computer_auth_detail(object_list, bundle)
#
#
#     def update_list(self, object_list, bundle):
#         if not hasattr(bundle.request, 'computer'):
#             logger.debug('ItMgmtAuthorization: update_list(): doing DjangoAuthorization')
#             return super(ItMgmtAuthorization, self).update_list(object_list, bundle)
#         # computer authorization
#         logger.debug('ItMgmtAuthorization: update_list(): doing Computer Authorization')
#         return self.computer_auth_list(object_list, bundle)
#
#
#     def update_detail(self, object_list, bundle):
#         if not hasattr(bundle.request, 'computer'):
#             logger.debug('ItMgmtAuthorization: update_detail(): doing DjangoAuthorization')
#             return super(ItMgmtAuthorization, self).update_detail(object_list, bundle)
#         # computer authorization
#         logger.debug('ItMgmtAuthorization: update_detail(): doing Computer Authorization')
#         return self.computer_auth_detail(object_list, bundle)
#
#
#     def delete_list(self, object_list, bundle):
#         if not hasattr(bundle.request, 'computer'):
#             logger.debug('ItMgmtAuthorization: delete_list(): doing DjangoAuthorization')
#             return super(ItMgmtAuthorization, self).delete_list(object_list, bundle)
#         logger.debug('ItMgmtAuthorization: delete_list(): doing Computer Authorization')
#         raise Unauthorized()
#
#
#     def delete_detail(self, object_list, bundle):
#         if not hasattr(bundle.request, 'computer'):
#             logger.debug('ItMgmtAuthorization: delete_detail(): doing DjangoAuthorization')
#             return super(ItMgmtAuthorization, self).delete_detail(object_list, bundle)
#         logger.debug('ItMgmtAuthorization: delete_detail(): doing Computer Authorization')
#         raise Unauthorized()
#
#
# #######################################################################
#
# class ComputerRelatedResourceMixin(object):
#     """
#     Related resource which use ItMgmtAuthorization should inherit from
#     this mixin.
#     """
#     def obj_create(self, bundle, **kwargs):
#         """
#         Create a new object through the API.
#         Note that this is going to get called *before* the authorization
#         checks.
#         """
#         if hasattr(bundle.request, 'computer'):
#             kwargs['computer'] = bundle.request.computer
#         return super(ComputerRelatedResourceMixin, self).obj_create(bundle, **kwargs)
#

#######################################################################
