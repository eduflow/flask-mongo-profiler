# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import bson
from flask import Markup

from .... import constants as profiling_constants, utils as profiling_utils


def request_environ_formatter(view, context, model, name):
    def deserialize_environ_key(k):
        return k.replace(profiling_constants.WERKZEUG_ENVIRON_KEY_REPLACEMENT, '.')

    return map_to_bootstrap_column_formatter(
        view, context, model, name, key_formatter_fn=deserialize_environ_key
    )


def map_to_bootstrap_column_formatter(
    view, context, model, name, key_formatter_fn=None
):
    chunks = []
    for k, v in sorted(model[name].items()):
        if key_formatter_fn and callable(key_formatter_fn):
            k = key_formatter_fn(k)
        chunks.append('<div class="row">')
        chunks.append('<div class="col-md-6">{}</div>'.format(k))
        chunks.append('<div class="col-md-6">{}</div>'.format(v))
        chunks.append('</div>')
    return Markup(''.join(chunks))


def http_method_formatter(view, context, model, name):
    """Wrap HTTP method value in a bs3 label."""
    method_map = {
        'GET': 'label-success',
        'PUT': 'label-info',
        'POST': 'label-primary',
        'DELETE': 'label-danger',
    }
    return Markup(
        '<span class="label {}">{}</span>'.format(
            method_map.get(model[name], 'label-default'), model[name]
        )
    )


def profiling_request_formatter(view, context, model, name):
    """Wrap HTTP method value in a bs3 label."""
    document = model[name]
    return Markup(
        ''.join(
            [
                '<p class="profiling-request">',
                '<a href="{}">'.format(document.get_admin_url(_external=True)),
                http_method_formatter(view, context, document, 'method'),
                '&nbsp;',
                document.path,
                '</a>',
                '</p>',
            ]
        )
    )


def profile_pyprofile_formatter(view, context, model, name):
    """Format pyprofile output"""
    return Markup('<pre>{}</pre>'.format(model[name]))


def profiling_pure_query_formatter(view, context, model, name, tag='pre'):
    data = profiling_utils.sanitize_dict(model[name], reverse=True)
    return Markup(
        '<{}>{}</{}>'.format(tag, (bson.json_util.dumps(data, indent=2)), tag)
    )


def mongo_command_name_formatter(view, context, model, name):
    command_name_map = {
        'find': 'label-success',
        'update': 'label-info',
        'create': 'label-primary',
        'delete': 'label-danger',
    }

    return Markup(
        '<span class="label {}">{}</span>'.format(
            command_name_map.get(model.command_name, 'label-default'),
            model.command_name,
        )
    )


def profiling_query_formatter(view, context, query_document, name):
    """Format a ProfilingQuery entry for a ProfilingRequest detail field

    Parameters
    ----------
    query_document : model.ProfilingQuery
    """
    return Markup(
        ''.join(
            [
                '<div class="pymongo-query row">',
                '<div class="col-md-1">',
                '<a href="{}">'.format(query_document.get_admin_url(_external=True)),
                mongo_command_name_formatter(
                    view, context, query_document, 'command_name'
                ),
                # '<span class="label {}">{}</span>'.format(
                #     command_name_map.get(query_document.command_name, 'label-default'),
                #     query_document.command_name,
                # ),
                '</div>',
                '<div class="col-md-10">',
                profiling_pure_query_formatter(
                    None, None, query_document, 'command', tag='pre'
                ),
                '</div>',
                '<div class="col-md-1">',
                '<small>{} ms</small>'.format(query_document.duration),
                '</a>',
                '</div>',
                '</div>',
            ]
        )
    )


def profiling_query_list_formatter(queryset):
    """
    Parameters
    ----------
    queryset : mongoengine.Queryset of model.ProfilingQuery
    """
    return Markup(
        ''.join([profiling_query_formatter(None, None, doc, None) for doc in queryset])
    )
