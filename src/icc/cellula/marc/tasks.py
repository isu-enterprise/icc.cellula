from zope.i18nmessageid import MessageFactory
from zope.interface import implementer
from icc.cellula.interfaces import ISingletonTask
from icc.cellula.workers import Task
from zope.component import getUtility
from icc.cellula.interfaces import IRTMetadataIndex, IWorker
from icc.contentstorage.interfaces import IContentStorage
import pymarc
from marcds.importer.issuerecog import DJVUtoMARC
import logging
import tempfile

logger = logging.getLogger('icc.cellula')

_ = _N = MessageFactory("isu.webapp")


@implementer(ISingletonTask)
class IssueDataTask(Task):

    def run(self):
        logger.info("Ran {}".format(self.__class__))
        metadata = getUtility(IRTMetadataIndex, "elastic")
        count, docs = metadata.query(variant="noisbn", count=10)
        logger.debug("Found {} documents".format(count))
        if count == 0:
            logger.debug("No document for processing.")
            return
        storage = getUtility(IContentStorage, name="content")
        queue_thread = getUtility(IWorker, name="queue")
        for doc in docs:
            logger.debug(doc["File-Name"])
            logger.debug(doc["mimetype"])
            content = storage.get(doc["id"])
            if isinstance(content, (str, bytes)):
                logger.debug("Content length: {}".format(len(content)))
                tmp = tempfile.NamedTemporaryFile(dir=queue_thread.tmpdir)
                tmp.write(content)
                tmp.flush()
            else:
                raise NotImplementedError("type is not supported")
            r = DJVUtoMARC(tmp.name)
            data = r.issue_data(noexc=True)
            if data is not None:
                logger.debug("Got some data ISBN {}".format(r.isbn))
                logger.debug("Lines: {}".format(r.lines))
            else:
                logger.debug("No data found.")
                continue
