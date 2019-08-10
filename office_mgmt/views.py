"""
Views for the office_mgmt application
"""
#######################
from __future__ import print_function, unicode_literals

from django.contrib.auth.decorators import permission_required
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404

from .models import Asset
from .utils import pdf_form

#######################
#######################################################################

# from django.views.generic.detail import BaseDetailView
# from django.views.generic.list import ListView

#######################################################################

# class OfficeMgmtModelMixin(object):
#     queryset = OfficeMgmtModel.objects.active()

#######################################################################

# class OfficeMgmtModelListView(OfficeMgmtModelMixin, ListView):
#     """
#     List the model
#     """
#
# office_mgmtmodel_list = OfficeMgmtModelListView.as_view()
#

#######################################################################

# class OfficeMgmtModelDetailView(OfficeMgmtModelMixin, DetailView):
#     """
#     Detail for the model
#     """
#
# office_mgmtmodel_detail = OfficeMgmtModelDetailView.as_view()
#

#######################################################################
#######################################################################
#######################################################################


def http_pdf(data):
    """
    Return a response as a PDF file.
    """
    if not data:
        raise Http404

    content_type = "application/pdf"
    return HttpResponse(data, content_type=content_type)


#######################################################################


@permission_required("it_mgmt.change_asset")
def asset_disposal_form(request, object_id):
    """
    Generate the PDF for the disposal of an asset.
    """
    obj = get_object_or_404(Asset, active=True, pk=object_id)
    data = pdf_form.asset_disposal_form(obj)
    response = http_pdf(data)
    filename = "{}".format(object_id) + ".pdf"
    response["Filename"] = filename  # IE needs this
    # response['Content-Disposition'] = 'attachment; filename=%s' % filename
    return response


#######################################################################
#######################################################################
#######################################################################
