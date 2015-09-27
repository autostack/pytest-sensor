#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import ansible.errors
import pprint


class GenericException(Exception):
    def __init__(self, exitstatus=1,
                 stdout='', stderr='', fatal=False):
        self.retval = None
        self.exitstatus = exitstatus
        self.out = stdout
        self.err = stderr
        self.fatal = fatal

    def __str__(self):
        msg = '{}: {}'.format(self.__class__.__name__, self.retval)
        msg += '\nExit Status: {}'.format(self.exitstatus)
        return msg


class MonitorException(GenericException):
    pass


class MonitorFatatException(GenericException):
    pass


class AnsibleNoHostsMatch(ansible.errors.AnsibleError):
    pass


class AnsibleCompoundException(ansible.errors.AnsibleError):
    '''
    :summary: A general exception that is raised when you have multiple
        hosts and at least one had an exception.
    '''
    def __init__(self, msg, dark=None, contacted=None):
        '''
        :param routines: The list of routines that some of them had exceptions.
        '''
        contacted = contacted or {}
        dark = dark or {}

        exceptions_msg = [self._format_host_exception(host, res) for
                          host, res in contacted.iteritems()
                          if res.get('failed', False) or res.get('rc', 0) != 0]
        exceptions_msg.extend([self._format_host_exception(host, res, 'Unreachable')
                               for host, res in dark.iteritems()])
        exceptions_msg = ''.join((msg, '\nInner exceptions:\n\n',
                                 '\n'.join(exceptions_msg)))
        super(AnsibleCompoundException, self).__init__(exceptions_msg)
        self._contacted = contacted

    @property
    def contacted(self):
        return self._contacted

    @staticmethod
    def _format_host_exception(host, res, msg=''):
        '''
        :summary: Get the traceback & exception str as string.
        :param routine: A routine that had an exception.
        :return: Formatted traceback as str.
        '''
        header = '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'
        footer = '<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<'
        return '\n'.join(
            (header, '{} Host: {}'.format(msg, host), pprint.pformat(res), footer))
