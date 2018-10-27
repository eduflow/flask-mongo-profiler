# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import datetime

import mongoengine
from flask_admin.contrib.mongoengine.view import ModelView

from ..formatters.date import date_formatter
from ..formatters.polymorphic_relations import (
    generic_lazy_ref_formatter,
    generic_ref_formatter,
    generic_ref_list_formatter,
)


class ReadOnlyMixin(object):
    can_create = False
    can_delete = False
    can_edit = False
    can_view_details = True


class ExtraDetailColumnsMixin(object):
    # Not in normal Flask-Admin: Add additional columns to a details view
    # Example:
    #
    #    details_extra_columns = [
    #        ('courses_owned', 'Courses (Owner of)'),
    #    ]
    details_extra_columns = []

    def get_details_columns(self):
        """Add details_extra_columns. (Not in normal Flask-Admin)"""
        return (
            super(ExtraDetailColumnsMixin, self).get_details_columns()
            + self.details_extra_columns
        )


class RelationalModelView(object):
    allowed_search_types = ModelView.allowed_search_types + (
        mongoengine.fields.ObjectIdField,
        mongoengine.fields.ReferenceField,
        mongoengine.fields.ListField,
    )

    column_field_type_formatters = {
        mongoengine.fields.ReferenceField: generic_ref_formatter,
        mongoengine.fields.GenericLazyReferenceField: generic_lazy_ref_formatter,
        mongoengine.fields.GenericReferenceField: generic_ref_formatter,
        mongoengine.fields.ListField: generic_ref_list_formatter,
    }

    column_field_type_formatters_detail = {
        mongoengine.fields.ReferenceField: generic_ref_formatter,
        mongoengine.fields.GenericLazyReferenceField: generic_lazy_ref_formatter,
        mongoengine.fields.GenericReferenceField: generic_ref_formatter,
        mongoengine.fields.ListField: generic_ref_list_formatter,
    }


class PrettyDatesMixin(object):
    column_type_formatters = {datetime.date: date_formatter}
    column_type_formatters_detail = {datetime.date: date_formatter}


class ColumnFieldTypeFormattersMixin(object):
    def __init__(self, *args, **kwargs):
        """
        Wire-in our model field type formatters.

        We added new property not in Flask-Admin called column_field_type_formatters.
        These are based off the model's field, rather than the field's return value.
        The reason why is we're resolving referenced fields, sometimes even generic,
        lazily-loaded ones, to URL routes. Flask-Admin prefixes URL's to the model
        class name, lowercase. E.g. User -> user.details_view.
        """
        super(ColumnFieldTypeFormattersMixin, self).__init__(*args, **kwargs)
        for c in self.column_list:
            if c in self.model._fields:
                field_class = self.model._fields[c].__class__
                if c not in self.column_formatters:
                    if field_class in getattr(self, 'column_field_type_formatters', {}):
                        self.column_formatters[c] = self.column_field_type_formatters[
                            field_class
                        ]

        # Same as above, but for mapping Mongoengine field types (not return value
        # types) to formatters used in detail view.
        for c in self.model._fields:
            field_class = self.model._fields[c].__class__
            if c not in self.column_formatters_detail:
                if field_class in getattr(
                    self, 'column_field_type_formatters_detail', {}
                ):
                    self.column_formatters_detail[
                        c
                    ] = self.column_field_type_formatters_detail[field_class]


class BaseModelView(
    ReadOnlyMixin,
    PrettyDatesMixin,
    ExtraDetailColumnsMixin,
    RelationalModelView,
    ColumnFieldTypeFormattersMixin,
    ModelView,
):
    named_filter_urls = True  # Needed for lookup fields

    def __init__(self, *args, **kwargs):
        super(ColumnFieldTypeFormattersMixin, self).__init__(*args, **kwargs)
