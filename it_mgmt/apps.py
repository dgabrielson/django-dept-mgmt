#########################################################################

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _

#########################################################################


class ITMgmtConfig(AppConfig):
    name = "it_mgmt"
    verbose_name = _("IT Management")

    def ready(self):
        """
        Any app specific startup code, e.g., register signals,
        should go here.
        """


#########################################################################
