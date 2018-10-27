# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from flask import Markup
from flask_admin.model.typefmt import list_formatter as base_list_formatter


def queryset_formatter(queryset):
    """
    This is used for custom detail fields returning a QuerySet of
    admin objects.
    """
    return Markup(
        base_list_formatter(
            None,
            [
                '<a href="{}">{}</a>'.format(u.get_admin_url(_external=True), u)
                for u in queryset
            ],
        )
    )


def qs_field(
    model_class,
    field,
    filters=None,
    formatter=queryset_formatter,
    manager_name='objects',
):
    """
    Show computed fields based on QuerySet's.

    This is a workaround since sometimes some filtering is involved to see if a user
    owns and object, is a student, etc.

    Example
    -------
    class MyModel(ModelView):
        details_extra_columns = [
            ('courses_owned', 'Courses (Owner of)'),
        ]
        column_formatters_detail = {
            'courses_owner': qs_field(model.Course, 'owner'),
        ]
    """
    if filters is None:
        filters = {}

    def _(view, context, _model, name):
        filters[field] = _model  # e.g. students: user

        # e.g. User.objects, User.deleted_objects
        manager = getattr(model_class, manager_name)
        return formatter(manager(**filters))

    return _
