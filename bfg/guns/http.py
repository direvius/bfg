import logging
import requests
from .measure import Sample
import time

requests_logger = logging.getLogger('requests')
requests_logger.setLevel(logging.WARNING)


class HttpGun(object):
    SECTION = 'http_gun'

    def __init__(self, base_address):
        self.log = logging.getLogger(__name__)
        self.base_address = base_address

    def shoot(self, missile, marker, results):
        self.log.debug("Missile: %s\n%s", marker, missile)
        self.log.debug("Sending request: %s", self.base_address + missile)
        start_time = time.time()
        r = requests.get(self.base_address + missile)
        errno = 0
        httpCode = r.status_code
        rt = int((time.time() - start_time) * 1000)
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
        results.put((int(time.time()), data_item))
