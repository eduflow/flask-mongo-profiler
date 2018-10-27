# -*- coding: utf-8 -*-
"""
See Also
--------
pymongo.monitoring :
    http://api.mongodb.com/python/current/api/pymongo/monitoring.html
"""
import logging
from pprint import pformat

import pymongo

logger = logging.getLogger(__name__)


class BaseMongoCommandLogger(pymongo.monitoring.CommandListener):
    """
    Log Mongo queries we make. Differences from plain-old listener:

    1. Turn logging output on/off since there's no public pymongo API to unregister
       or monitor queries temporarily.
    2. Enable logging to various endpoints without having to rewrite everything.
       It can be valuable to log to standard library logging (stdout, logfile), or
       database (django-silk style).
    3. Can be tailored to output only commands requested.

    Parameters
    ----------
    quiet : bool, optional
        Silence MongoDB CommandListener from logging (default: True)
    command_filter : list of str, optional
        MongoDB queries commands to send to logger

    See Also
    --------
    - https://api.mongodb.com/python/current/api/pymongo/monitoring.html
    """

    def __init__(
        self, quiet=True, command_filter=['create', 'find', 'update', 'delete']
    ):
        self.quiet = quiet  # ignore the initial updates when Peergrade starts
        self.command_filter = command_filter

    def start(self):
        self.quiet = False

    def stop(self):
        self.quiet = True

    def started(self, event):
        if self.quiet or event.command_name not in self.command_filter:
            return

    def failed(self, event):
        if self.quiet or event.command_name not in self.command_filter:
            return

    def succeeded(self, event):
        if self.quiet or event.command_name not in self.command_filter:
            return


class LoggingMongoCommandLogger(BaseMongoCommandLogger):
    def __init__(
        self, quiet=True, command_filter=['create', 'find', 'update', 'delete']
    ):
        super(LoggingMongoCommandLogger, self).__init__(
            quiet=quiet, command_filter=command_filter
        )

    def started(self, event):
        if self.quiet or event.command_name not in self.command_filter:
            return

        logger.info(pformat(event.command.to_dict()))

    def failed(self, event):
        if self.quiet or event.command_name not in self.command_filter:
            return
        logging.info(
            'Command {0.command_name} with request id '
            '{0.request_id} on server {0.connection_id} '
            'failed in {0.duration_micros} '
            'microseconds'.format(event)
        )

    def succeeded(self, event):
        if self.quiet or event.command_name not in self.command_filter:
            return

        logger.info(
            'Command {0.command_name} with request id '
            '{0.request_id} on server {0.connection_id} '
            'succeeded in {0.duration_micros} '
            'microseconds'.format(event)
        )


class QueuedMongoCommandLogger(BaseMongoCommandLogger):
    """Record the commands in self.collector list."""

    def __init__(
        self, quiet=True, command_filter=['create', 'find', 'update', 'delete']
    ):
        super(QueuedMongoCommandLogger, self).__init__(
            quiet=quiet, command_filter=command_filter
        )

    def start(self):
        super(QueuedMongoCommandLogger, self).start()
        self.collector = []

    def stop(self):
        super(QueuedMongoCommandLogger, self).stop()
        del self.collector[:]

    def started(self, event):
        if self.quiet or event.command_name not in self.command_filter:
            return
        self.collector.append(event)

    def failed(self, event):
        if self.quiet or event.command_name not in self.command_filter:
            return
        self.collector.append(event)

    def succeeded(self, event):
        if self.quiet or event.command_name not in self.command_filter:
            return
        self.collector.append(event)
