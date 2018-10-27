# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from flask import Markup

from ..helpers import get_list_url_filtered_by_field_value


def search_field_formatter(view, context, model, name):
    filter_url = get_list_url_filtered_by_field_value(view, model, name)
    filter_applied = False

    if filter_url is None:  # currently filtered
        filter_url = get_list_url_filtered_by_field_value(
            view, model, name, reverse=True
        )
        filter_applied = True

    return Markup(
        ''.join(
            [
                model[name],
                '&nbsp;',
                '<a href="{href}" class="{classname}" data-role="tooltip"'.format(
                    href=filter_url,
                    classname='fa fa-{icon} glyphicon glyphicon-{icon}'.format(
                        icon='search' if not filter_applied else 'remove'
                    ),
                ),
                'title data-original-title="{}"'.format(
                    'Filter {} by {}'.format(name, model[name])
                    if not filter_applied
                    else 'Clear filter'
                ),
                'style="text-decoration:none"',
                '></a>',
            ]
        )
    )
