from isu.webapp import views
from icc.cellula import views as cviews
#from icc.cellula import view_config
from zope.i18nmessageid import MessageFactory
from .tasks import IssueDataTask

import logging

_ = _N = MessageFactory("isu.webapp")

logger = logging.getLogger('icc.cellula')


#@view_config(title=_("Import book data into MARC records"))
class View(views.View, cviews.View):
    """Defines view for MARC importer.
    """
    title = _("Import book data into MARC records")

    def action(self):
        if self.request.method == "POST":
            self.progress = "Acquirement started."
            IssueDataTask().enqueue(block=False, view=self)
        pass

    def answer(self):
        return []

    def result_table(self):
        return self()