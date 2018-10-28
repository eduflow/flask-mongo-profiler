# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import datetime
import re

import bson
import mongoengine
from flask_admin.contrib.mongoengine.tools import parse_like_term
from flask_admin.contrib.mongoengine.view import ModelView

from ...._compat import shlex
from ....constants import RE_OBJECTID
from ..formatters.date import date_formatter
from ..formatters.polymorphic_relations import (
    generic_lazy_ref_formatter,
    generic_ref_formatter,
    generic_ref_list_formatter,
)
from ..helpers import search_relative_field


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


class RelationalFieldMixin(object):
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


class RelationalSearchMixin(object):
    # Custom used for our search
    # Note: 'fields': ['id'] is implicit, you don't need to add it.
    # Similar to form_ajax_refs's shape.
    column_searchable_refs = {}

    def _search(self, query, search_term):
        """
        Improved search between words.

        The original _search for MongoEngine dates back to November 12th, 2013 [1]_.
        In this ref it's stated that there is a bug with complex Q queries preventing
        multi-word searches. During this time, the MongoEngine version was earlier than
        0.4 (predating PyPI) [2]_. Since then, there have been multiple releases [3]_
        which appear to have fixed the query issue.

        Treats id (_id) impliticly as a member of column_searchable_list, except it's
        not computed in an OR/AND, a direct lookup is checked for.

        References
        ----------
        .. [1] Search for MongoEngine. 02b936b. November 23, 2013.
           https://git.io/fxf8C. Accessed September, 29th, 2018.
        .. [2] MongoEngine releases on PyPI.
           https://pypi.org/project/mongoengine/#history. Accessed September 29th, 2018.
        .. [3] MongoEngine release notes. http://docs.mongoengine.org/changelog.html.
           Accessed September 29th, 2018.
        """
        criterias = mongoengine.Q()
        rel_criterias = mongoengine.Q()
        terms = shlex.split(search_term)

        # If an ObjectId pattern, see if we can get an instant lookup.
        if len(terms) == 1 and re.match(RE_OBJECTID, terms[0]):
            q = query.filter(id=bson.ObjectId(terms[0]))
            if q.count() == 1:  # Note: .get doesn't work, they need a QuerySet
                return q

        for term in terms:
            op, term = parse_like_term(term)

            # Case insensitive by default
            if op == 'contains':
                op = 'icontains'

            criteria = mongoengine.Q()

            for field in self._search_fields:
                if isinstance(field, mongoengine.fields.ReferenceField):
                    rel_model = field.document_type
                    rel_fields = (
                        getattr(self, 'column_searchable_refs', {})
                        .get(field.name, {})
                        .get('fields', ['id'])
                    )

                    # If term isn't an ID, don't do an ID lookup
                    if rel_fields == ['id'] and not re.match(RE_OBJECTID, term):
                        continue

                    ids = [
                        o.id for o in search_relative_field(rel_model, rel_fields, term)
                    ]
                    rel_criterias |= mongoengine.Q(**{'%s__in' % field.name: ids})
                elif isinstance(field, mongoengine.fields.ListField):
                    if not isinstance(field.field, mongoengine.fields.ReferenceField):
                        continue  # todo: support lists of other types
                    rel_model = field.field.document_type_obj
                    rel_fields = (
                        getattr(self, 'column_searchable_refs', {})
                        .get(field.name, {})
                        .get('fields', 'id')
                    )
                    ids = [
                        o.id for o in search_relative_field(rel_model, rel_fields, term)
                    ]
                    rel_criterias |= mongoengine.Q(**{'%s__in' % field.name: ids})
                else:
                    flt = {'%s__%s' % (field.name, op): term}
                    q = mongoengine.Q(**flt)
                    criteria |= q

            criterias &= criteria

        # import pprint
        # pp = pprint.PrettyPrinter(indent=4).pprint
        # print(pp(query.filter(criterias)._query))
        return query.filter(criterias | rel_criterias)


class BaseModelView(
    ReadOnlyMixin,
    PrettyDatesMixin,
    ExtraDetailColumnsMixin,
    RelationalFieldMixin,
    RelationalSearchMixin,
    ColumnFieldTypeFormattersMixin,
    ModelView,
):
    named_filter_urls = True  # Needed for lookup fields

    def __init__(self, *args, **kwargs):
        super(ColumnFieldTypeFormattersMixin, self).__init__(*args, **kwargs)
