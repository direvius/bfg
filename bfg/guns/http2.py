import logging
import hyper
from hyper import HTTPConnection
from .measure import Sample
import time


LOG = logging.getLogger(__name__)


class HttpGun(object):
    SECTION = 'http_gun'

    def __init__(self, base_address):
        self.base_address = base_address
        LOG.info("Initialized http2 gun with target '%s'", base_address)
        self.conn = HTTPConnection(base_address, secure=True)

    def shoot(self, missile, marker, results):
        LOG.debug("Missile: %s\n%s", marker, missile)
        LOG.debug("Sending request: %s", self.base_address + missile)
        start_time = time.time()
        self.conn.request('GET', missile)
        resp = self.conn.get_response()
        end_time = time.time()
        errno = 0
        httpCode = resp.status
        rt = int((end_time - start_time) * 1000)
        data_item = Sample(
            marker,             # marker
            1,  # threads
            rt,                 # overallRT
            httpCode,           # httpCode
            errno,              # netCode
            0,                  # sent
            0,                  # received
            0,                  # connect
            0,                  # send
            rt,                 # latency
            0,                  # receive
            0,                  # accuracy
        )
        results.put((int(end_time), data_item))
