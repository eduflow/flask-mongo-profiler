# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from flask import flash, redirect
from flask_admin import expose

from ...mongoengine.profiling import ProfilingQuery, ProfilingRequest
from ..formatters.lookup import search_field_formatter
from ..formatters.profiling import (
    http_method_formatter,
    map_to_bootstrap_column_formatter,
    mongo_command_name_formatter,
    profile_pyprofile_formatter,
    profiling_pure_query_formatter,
    profiling_query_formatter,
    profiling_query_list_formatter,
    profiling_request_formatter,
    request_environ_formatter,
)
from ..formatters.relational import qs_field
from .base import BaseModelView


class ProfilingCommonView(BaseModelView):
    list_template = 'admin/model/profiling-list.html'

    @expose('clear')
    def clear_entities(self):

        ProfilingRequest.objects.delete()
        ProfilingQuery.objects.delete()
        flash('Profiling data cleared.', 'info')
        return redirect(self.model.get_admin_list_url())


class ProfilingRequestView(ProfilingCommonView):
    list_template = 'admin/model/profilingrequest-list.html'

    column_filters = [
        'method',
        'path',
        'referrer',
        'duration',
        'query_duration',
        'query_count',
        'time',
    ]
    column_list = [
        'method',
        'path',
        'referrer',
        'duration',
        'query_duration',
        'query_count',
        'time',
    ]
    column_descriptions = {
        'referrer': 'Page requesting API endpoint. If empty, is the page itself.'
    }
    column_searchable_list = ['path', 'method']

    column_labels = {
        'duration': 'Duration (ms)',
        'query_duration': 'Query Duration (ms)',
    }

    column_formatters = {
        'method': http_method_formatter,
        'path': search_field_formatter,
        'referrer': search_field_formatter,
    }

    details_extra_columns = [('queries', 'Queries'), ('pyprofile', 'Profile')]
    column_details_exclude_list = ['pyprofile']
    column_formatters_detail = {
        'method': http_method_formatter,
        'referrer': search_field_formatter,
        'pyprofile': profile_pyprofile_formatter,
        'queries': qs_field(
            ProfilingQuery, 'request', formatter=profiling_query_list_formatter
        ),
        'environ': request_environ_formatter,
        'status': map_to_bootstrap_column_formatter,
        'path': search_field_formatter,
    }


class ProfilingQueryView(ProfilingCommonView):
    column_filters = ['command_name', 'request']
    column_list = ['command_name', 'request', 'duration', 'command']
    column_searchable_list = ['command_name', 'request']

    column_labels = {'duration': 'Duration (ms)'}

    column_formatters = {
        'command_name': mongo_command_name_formatter,
        'command': profiling_pure_query_formatter,
        'request': profiling_request_formatter,
    }
    details_extra_columns = [('command_pretty', 'Command (pretty)')]
    column_formatters_detail = {
        'command_name': mongo_command_name_formatter,
        'command_pretty': profiling_query_formatter,
        'request': profiling_request_formatter,
    }
