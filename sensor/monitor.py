#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import time
import ast

from sensor.constants import TEST_CAHNNEL_ID


class RuleHandler(object):
    '''
    This is actually an action based rule that decide to raise an Exception
    or not based on Action status
    '''


class ComponentChain(object):
    '''
    Handle chain for every Node, contain RuleHandler
    '''
    def __init__(self):
        pass


class Chain(object):
    '''
    Chain contain list Component chains
    '''
    def __init__(self):
        pass


class MonitorEngine(object):
    def __init__(self, queue):
        self.active = True
        self.q = queue

        self._p = queue.pubsub()
        self._p.subscribe(TEST_CAHNNEL_ID)

        self._start()

    def _register(self, hosts, rules, delay):
        print('REGISTER', hosts, rules, delay)

    def _unregister(self, hosts, rules):
        print('UNREGISTER', hosts, rules)

    def _start(self):
        while self.active:
            msg = self._p.get_message()
            if msg is None:
                time.sleep(0.01)
            elif msg['type'] == 'message':
                data = ast.literal_eval(msg['data'])
                if data.get('type', None) == 'MONITORDONE':
                    self.active = False
                    self._p.close()
                else:
                    # TODO: handle eval exception
                    order = data.pop('type', None)
                    if order == 'REGISTER':
                        self._register(**data)
                    elif order == 'UNREGISTER':
                        self._unregister(**data)

    def stop(self):
        self.active = False
        self._p.close()
