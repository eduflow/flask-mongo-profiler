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


class BaseModelView(
    ReadOnlyMixin,
    PrettyDatesMixin,
    ExtraDetailColumnsMixin,
    RelationalModelView,
    ModelView,
):
    pass
