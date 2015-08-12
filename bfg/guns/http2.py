import logging
from hyper import HTTP20Connection
from hyper.http20.exceptions import ConnectionError
from .measure import measure


LOG = logging.getLogger(__name__)


class HttpGun(object):
    SECTION = 'http_gun'

    def __init__(self, base_address):
        self.base_address = base_address
        LOG.info("Initialized http2 gun with target '%s'", base_address)
        self.conn = HTTP20Connection(base_address, secure=True)

    def shoot(self, task, results):
        LOG.debug("Task: %s", task)
        LOG.debug("Sending request: %s", self.base_address + task.data)
        with measure(task, results) as sw:
            stream = self.conn.request('GET', task.data)
            resp = self.conn.get_response(stream)
            sw.stop()
            sw.set_code(resp.status)


class HttpMultiGun(object):
    SECTION = 'http_gun'

    def __init__(self, base_address):
        self.base_address = base_address
        LOG.info("Initialized http2 gun with target '%s'", base_address)
        self.conn = HTTP20Connection(base_address, secure=True)

    def shoot(self, task, results):
        LOG.debug("Task: %s", task)
        scenario = task.marker
        subtasks = [
            task._replace(data=missile[1], marker=missile[0])
            for missile in task.data
        ]
        streams = []
        with measure(task, results) as overall_sw:
            for subtask in subtasks:
                with measure(subtask, results) as sw:
                    LOG.debug("Request GET %s", subtask.data)
                    streams.append(
                        (subtask, self.conn.request('GET', subtask.data)))
                    sw.stop()
                    sw.scenario = scenario
                    sw.action = "request"
            for (subtask, stream) in streams:
                with measure(subtask, results) as sw:
                    LOG.debug("Response for %s from %s ", subtask.data, stream)
                    try:
                        resp = self.conn.get_response(stream)
                    except (ConnectionError, KeyError) as e:
                        sw.stop()
                        sw.set_code(1)
                        sw.ext["error"] = str(e)
                        LOG.warning("Error getting response: %s", str(e))
                    else:
                        sw.stop()
                        sw.set_code(resp.status)
                    sw.scenario = scenario
                    sw.action = "response"
            overall_sw.stop()
            overall_sw.scenario = scenario
            overall_sw.action = "overall"
