#######################
from __future__ import print_function, unicode_literals

from django.utils import six
from django.utils.encoding import smart_text
from rest_framework import renderers

#######################
###############################################################

###############################################################


class PlainTextRenderer(renderers.BaseRenderer):
    media_type = "text/plain"
    format = "txt"

    def _data_render(self, obj, indent=-1):
        """
        Good enough for government work...
        """
        # compound values
        if isinstance(obj, dict):
            return "\n".join(
                [
                    self._data_render(key, indent + 1) + self._data_render(value, 1)
                    for key, value in obj.items()
                ]
            )
        if isinstance(obj, list):
            return "\n".join([self._data_render(e, indent + 1) for e in obj])
        # atomic values
        if isinstance(obj, six.string_types):
            return "\t" * indent + smart_text(obj)
        if isinstance(obj, int):
            return "\t" * indent + smart_text("{0}".format(obj))
        if obj is None:
            return "\t" * indent + ""
        raise RuntimeError("uknown object type: {0!r}".format(type(obj)))

    def render(self, data, media_type=None, renderer_context=None):
        return self._data_render(data).encode(self.charset)
        # return data.encode(self.charset)


###############################################################
