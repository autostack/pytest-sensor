#!/usr/bin/ctx python
# -*- coding: UTF-8 -*-

import pytest
from pprint import pprint as pp


def test_ctx(context):
    print
    model, _ = context
    print model
    print type(model)
    pp(model)
    l1 = len(model)
    print 'Adding test group'
    model['test'] = []
    print 'ctx.test >>', model.test
    print 'type(ctx.test) >>', type(model.test)
    assert len(model) - 1 == l1, 'Length was not increased'

    print 'Deleting test group'
    del model['test']
    l1 = len(model)
    pp(model)
    assert len(model) == l1, 'Length was not increased'


def test_all_attr_exists(context):
    model, _ = context
    assert hasattr(model, 'all'), 'all attr does not exists'
    assert hasattr(model, 'hosts'), 'hosts attr does not exists'
    model['test'] = []
    assert hasattr(model, 'test'), 'Failed to add new attr'
    del model['test']
    assert not hasattr(model, 'test'), 'Failed to delete new attr'


def test_slice(context):
    print
    model, _ = context
    pp(model.all[:2])
    pp(model.hosts[1])
    pp(model.all[-1])


def test_ping(context):
    print
    model, run = context
    pp(run.ping(model.all))
    pp(run.ping(model.all[0]))
    pp(run.ping(model.all[:-1]))


def test_hosts_uname(context):
    print
    model, run = context
    future = run.command(model.hosts, 'uname -a', run_async=True)
    print 'Future >>> ', future
    pp(future.wait(60, 2))


@pytest.mark.parametrize('playbook', ['/Users/avi/git/pytest-ansible/tests/play1.yml'])
def test_play1(context, playbook):
    print
    model, run = context
    pp(run.run_playbook(model.hosts, playbook))


def test_setup_factory(context):
    print
    model, _ = context
    pp(model)
    pp(model.hosts[1].facts)
    pp(model)
    print(type(model.hosts[1].facts))


def test_only_ctx_facts(context):
    print
    model, _ = context
    pp(model.hosts[1].facts)
    pp(model)
    print(type(model.hosts[1].facts))
