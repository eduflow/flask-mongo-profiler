# -*- coding: utf-8 -*-
from __future__ import division, unicode_literals

import time
from datetime import datetime

import pymongo
import werkzeug
from werkzeug._compat import StringIO

from ... import utils as profiling_utils
from ..._compat import Profile, Stats, stdlib_profiling_available
from ...constants import WERKZEUG_ENVIRON_KEY_REPLACEMENT
from ..mongoengine.profiling import ProfilingQuery, ProfilingRequest
from .mongo import QueuedMongoCommandLogger


class ProfilerMiddleware(object):
    def __init__(self, app, pymongo_logger, ignored_url_patterns=None):
        if not stdlib_profiling_available:
            raise RuntimeError(
                'the profiler is not available because '
                'profile or pstat is not installed.'
            )
        if ignored_url_patterns is None:
            ignored_url_patterns = []
        self._app = app
        self._ignored_url_patterns = ignored_url_patterns
        self.logger = pymongo_logger
        pymongo.monitoring.register(self.logger)

    def __call__(self, environ, start_response):
        response_body = []
        _status = {}

        def catching_start_response(status, headers, exc_info=None):
            _status.update(code=status[0], msg=status[1])
            start_response(status, headers, exc_info)
            return response_body.append

        def runapp():
            appiter = self._app(environ, catching_start_response)
            response_body.extend(appiter)
            if hasattr(appiter, 'close'):
                appiter.close()

        p = Profile()
        self.logger.start()
        start = time.time()
        p.runcall(runapp)
        body = b''.join(response_body)

        elapsed = time.time() - start

        # Grab any information if we need it
        if isinstance(self.logger, QueuedMongoCommandLogger):
            mongo_events = list(self.logger.collector)  # copy (we empty after)

        # Stop (quiet) pymongo logger
        self.logger.stop()  # Note: Also clears QueuedMongoCommandLogger.collector

        # Dump profile to variable
        s = StringIO()
        ps = Stats(p, stream=s).sort_stats('cumulative')
        ps.print_stats()
        profile_text = s.getvalue()
        profile_text = "\n".join(profile_text.split("\n")[0:256])

        if isinstance(self.logger, QueuedMongoCommandLogger):
            queries = profiling_utils.combine_events_to_queries(mongo_events)
            path = environ.get('PATH_INFO')

            referrer = werkzeug.urls.url_parse(environ.get('HTTP_REFERER', ''))

            if len(queries) > 0 and not any(
                n in path for n in self._ignored_url_patterns
            ):  # Only record records with queries

                r = ProfilingRequest(
                    method=environ['REQUEST_METHOD'],
                    path=path,
                    referrer=referrer.path,
                    environ={
                        k.replace('.', WERKZEUG_ENVIRON_KEY_REPLACEMENT): v
                        for k, v in list(environ.items())[:18]
                        if any(
                            isinstance(v, _type)
                            for _type in [list, tuple, str, dict, int]
                        )
                    },
                    status=_status,
                    pyprofile=profile_text,
                    query_count=len(queries),
                    query_duration=sum(
                        q['duration'] for q in queries if 'duration' in q
                    ),
                    duration=elapsed * 1000,  # to milliseconds
                    time=datetime.utcnow(),
                )
                r.save()
                for q in queries:
                    ProfilingQuery(request=r, **q).save()

        return [body]
