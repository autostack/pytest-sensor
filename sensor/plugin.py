#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import os
import pytest
import time
import ast
import py
import redis
import marshal

from sensor.constants import (TEST_CAHNNEL_ID, CONFIG)
from sensor.monitor import MonitorEngine
from sensor.errors import (MonitorFatatException, MonitorException)

from _pytest import runner  # XXX load dynamically

queue = None
EXITSTATUS_TESTEXIT = 4


def pytest_addoption(parser):
    '''Add options to control monitoring engine.'''

    group = parser.getgroup('Autostack')
    group.addoption('--monitor',
                    default=False,
                    action='store_true',
                    help='Enable sensor monitoring context nodes')


def pytest_runtest_protocol(item):
    global queue
    reports = []

    if 'monitor' in item.keywords:
        queue = redis.StrictRedis(**CONFIG)
        monitor = forked_monitor_engine(queue)
        future = forked_run_report(item, queue)

        try:
            p = queue.pubsub()
            p.subscribe(TEST_CAHNNEL_ID)

            while True:
                msg = p.get_message()
                if msg is None:
                    time.sleep(0.01)
                elif msg['type'] == 'message':
                    data = ast.literal_eval(msg['data'])
                    if data.get('type', None) == 'TESTDONE':
                        break
                    elif data.get('type', None) == 'EXCEPTION':
                        try:
                            handle_monitor_exception(data, future)
                        except MonitorException as err:
                            # catch exception which doesn't cause test failure
                            reports.extend(teardown_forked_report(item, err))
        except MonitorFatatException as err:
            # catch fatal exceptions and exit test with ERROR status
            reports.extend(teardown_forked_report(item, err))
        else:
            result = future.waitfinish()
            reports.extend(teardown_forked_report(item, result))
        finally:
            p.close()
            queue.publish(TEST_CAHNNEL_ID, {'type': 'MONITORDONE'})

        for rep in reports:
            item.ihook.pytest_runtest_logreport(report=rep)
        return True


def handle_monitor_exception(data, ff):
    # TODO: check exception_type to decide what would be the next action
    if data.get('exception_type', None) == 'FATAL':
        os.kill(ff.pid, 15)
        rc = data.get('rc', 1)
        stdout = data.get('stdout', '')
        stderr = data.get('stderr', '')
        raise MonitorFatatException(rc, stdout, stderr, True)
    else:
        stdout = data.get('stdout', '')
        stderr = data.get('stderr', '')
        raise MonitorException(1, stdout, stderr)


def forked_monitor_engine(queue):
    def runforked():
        try:
            engine = MonitorEngine(queue)
        except KeyboardInterrupt:
            engine.stop()
            py.std.os._exit(EXITSTATUS_TESTEXIT)
        return engine
    return py.process.ForkedFunc(runforked)


def forked_run_report(item, queue):
    # for now, we run setup/teardown in the subprocess
    # XXX optionally allow sharing of setup/teardown
    from _pytest.runner import runtestprotocol

    def runforked():
        try:
            reports = runtestprotocol(item, log=False)
        except KeyboardInterrupt:
            py.std.os._exit(EXITSTATUS_TESTEXIT)
        finally:
            queue.publish(TEST_CAHNNEL_ID, {'type': 'TESTDONE'})
        return marshal.dumps([serialize_report(x) for x in reports])
    return py.process.ForkedFunc(runforked)


def teardown_forked_report(item, result):
    if result.retval is not None:
        report_dumps = marshal.loads(result.retval)
        return [unserialize_report("testreport", x) for x in report_dumps]
    else:
        if result.exitstatus == EXITSTATUS_TESTEXIT:
            py.test.exit("forked test item %s raised Exit" % (item,))
        return [report_process_monitor(item, result)]


def report_process_monitor(item, result):
    # TODO: generate WARNINGS to pytest report instead of FAILED
    _type = 'FATAL' if result.fatal else 'WARNING'
    info = ("Monitor process report {}:".format(_type))

    call = runner.CallInfo(lambda: 0 / 0, "???")
    call.excinfo = info
    rep = runner.pytest_runtest_makereport(item, call)

    msg = ''
    if result.out:
        msg += '\n\t{}'.format(result.out)
    if result.err:
        msg += '\n\t{}'.format(result.err)
    rep.sections.append(("Monitor Message", msg))
    return rep


def serialize_report(rep):
    d = rep.__dict__.copy()
    if hasattr(rep.longrepr, 'toterminal'):
        d['longrepr'] = str(rep.longrepr)
    else:
        d['longrepr'] = rep.longrepr
    for name in d:
        if isinstance(d[name], py.path.local):
            d[name] = str(d[name])
        elif name == "result":
            d[name] = None  # for now
    return d


def unserialize_report(name, reportdict):
    if name == "testreport":
        return runner.TestReport(**reportdict)
    elif name == "collectreport":
        return runner.CollectReport(**reportdict)


@pytest.mark.tryfirst
def pytest_exception_interact(node):
    pass


#def get_params(item):
#    """Return (timeout, method) for an item"""
#    timeout = method = None
#    if 'monitor' in item.keywords:
#        timeout, method = _parse_marker(item.keywords['monitor'])
#        timeout = _validate_timeout(timeout, 'marker')
#        method = _validate_method(method, 'marker')
#    if timeout is None:
#        timeout = item.config.getvalue('monitor')
#    if method is None:
#        method = 'thread'
#    return timeout, method


class Tracer(object):
    def __init__(self, queue):
        self._q = queue

    def register(self, nodes, rules, delay=30):
        data = {'type': 'REGISTER',
                'hosts': nodes,
                'rules': rules,
                'delay': delay,
                }
        self._q.publish(TEST_CAHNNEL_ID, data)

    def unregister(self, nodes, rules):
        data = {'type': 'UNREGISTER',
                'hosts': nodes,
                'rules': rules,
                }
        self._q.publish(TEST_CAHNNEL_ID, data)

    def close(self):
        self._q.publish(TEST_CAHNNEL_ID, {'type': 'MONITORDONE'})


@pytest.yield_fixture(scope='function')
def track(request):
    '''
    '''
    tr = Tracer(queue)
    yield tr
    tr.close()
