#!/usr/bin/ctx python
# -*- coding: UTF-8 -*-

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)


import pytest
import time
import redis

from pprint import pprint as pp
from sensor.constants import (TEST_CAHNNEL_ID, CONFIG)


class PublishMock(object):
    def __init__(self):
        self.q = redis.StrictRedis(**CONFIG)
#        self._p = self.q.pubsub()
#        self._p.subscribe(TEST_CAHNNEL_ID)

    def send_fatal(self):
        self.q.publish(TEST_CAHNNEL_ID, {'type': 'EXCEPTION',
                                         'exception_type': 'FATAL',
                                         'stdout': 'This is the stdout message',
                                         'stderr': 'and this is the stderr message',
                                         'rc': 444})

    def send_warning(self):
        self.q.publish(TEST_CAHNNEL_ID, {'type': 'EXCEPTION',
                                         'exception_type': 'OTHER',
                                         'stdout': 'This is the stdout message',
                                         'stderr': 'and this is the stderr message',
                                         'rc': 444})


pub = PublishMock()


@pytest.mark.monitor
def test_ctx(ctx, track):
    print()
    pp(ctx)
    l1 = len(ctx)
    print('Adding test group')
    ctx['test'] = []
    print('ctx.test >>', ctx.test)
    print ('type(ctx.test) >>', type(ctx.test))
    assert len(ctx) - 1 == l1, 'Length was not increased'

    print('Deleting test group')
    del ctx['test']
    l1 = len(ctx)
    pp(ctx)
    assert len(ctx) == l1, 'Length was not increased'

    track.register(ctx.all.address, ['netwok', 'filesystem'])
    pub.send_warning()
    time.sleep(2)
#    assert False, 'aaaaaaaaaajasd,amksndlakisdja,msdakmsndakjsd,ajksd,amn'
    track.unregister(ctx.all.address, ['netwok', 'filesystem'])
    pub.send_warning()
    time.sleep(2)

