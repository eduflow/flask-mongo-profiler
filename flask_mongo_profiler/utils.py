# -*- coding: utf-8 -*-
from __future__ import division, unicode_literals

import pymongo

from .constants import (
    MONGO_COMMAND_KEY_DOLLAR_SIGN_REPLACEMENT,
    MONGO_COMMAND_KEY_PERIOD_SIGN_REPLACEMENT,
)

try:
    import mongoengine  # NOQA: F401
    from .contrib.mongoengine.profiling import ProfilingQueryConnection
except ImportError:
    pass


def sanitize_dict(d, reverse=False):
    """
    ValidationError: ValidationError (ProfilingRequest:None) (Invalid
    dictionary key name - keys may not contain "." or "$" characters 1.Invalid
    dictionary key name - keys may not contain "." or "$" characters 2.Invalid
    dictionary key name - keys may not contain "." or "$" characters:
    ['queries'])
    """
    data = {}

    if isinstance(d, list):
        list_data = []
        for item in d:
            list_data.append(sanitize_dict(item, reverse=reverse))
        return list_data
    elif not isinstance(d, dict):
        return d

    for k, v in d.iteritems():
        if isinstance(v, dict):
            v = sanitize_dict(v, reverse=reverse)
        elif isinstance(v, list):
            list_data = []
            for item in v:
                list_data.append(item)
            v = sanitize_dict(list_data, reverse=reverse)

        if reverse:
            data[
                k.replace(MONGO_COMMAND_KEY_PERIOD_SIGN_REPLACEMENT, '.').replace(
                    MONGO_COMMAND_KEY_DOLLAR_SIGN_REPLACEMENT, '$'
                )
            ] = v
        else:
            data[
                k.replace('.', MONGO_COMMAND_KEY_PERIOD_SIGN_REPLACEMENT).replace(
                    '$', MONGO_COMMAND_KEY_DOLLAR_SIGN_REPLACEMENT
                )
            ] = v
    return data


def combine_events_to_queries(_mongo_events):
    """Combines pymongo.monitoring events to queries.

    CommandStartedEvent has queries information.
    CommandSuccessfulEvent has timing information.

    Iterate over events and map against mongo's request_id (the query).
    """
    queries = {}  # map on the request_id

    for event in _mongo_events:
        if event.request_id not in queries:
            try:
                connection = ProfilingQueryConnection(*event.connection_id)
            except NameError:
                connection = event.connection_id
            queries[event.request_id] = dict(  # all event types have this
                command_name=event.command_name,
                # Unpack host,
                connection=connection,
                operation_id=event.operation_id,
            )

        if isinstance(event, pymongo.monitoring.CommandStartedEvent):
            queries[event.request_id].update(
                command=sanitize_dict(event.command.to_dict()),
                database_name=event.database_name,
            )
        elif isinstance(event, pymongo.monitoring.CommandSucceededEvent):
            queries[event.request_id].update(duration=event.duration_micros / 1000)
        elif isinstance(event, pymongo.monitoring.CommandFailedEvent):
            queries[event.request_id].update(
                failure=sanitize_dict(event.failure),
                duration=event.duration_micros / 1000,
            )

    return queries.values()  # smoosh back together
