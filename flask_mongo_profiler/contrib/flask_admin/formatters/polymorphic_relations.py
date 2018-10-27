# -*- coding: utf-8 -*-
"""
Formatters that do polymorphic relation resolution
against GenericReferienceField. They will look up the original
model in the field, then lookup like a normal relational formatter.

See Also
--------
model.AdminLog.document, model.Answer.parent :
    GenericReferenceField [1]_, GenericLazyReferenceField [2]_

References
----------
.. [1] mongoengine.fields.GenericReferenceField. MongoEngine Docs.
   http://docs.mongoengine.org/apireference.html#mongoengine.fields.GenericReferenceField

.. [2] mongoengine.fields.GenericLazyReferenceField. MongoEngine Docs.
   http://docs.mongoengine.org/apireference.html#mongoengine.fields.GenericLazyReferenceField
"""
from __future__ import absolute_import, unicode_literals

import mongoengine
import werkzeug
from flask import Markup, url_for


def generic_ref_formatter(view, context, model, name, lazy=False):
    """
    For GenericReferenceField and LazyGenericReferenceField

    See Also
    --------
    diff_formatter
    """
    try:
        if lazy:
            rel_model = getattr(model, name).fetch()
        else:
            rel_model = getattr(model, name)
    except (mongoengine.DoesNotExist, AttributeError) as e:
        # custom_field_type_formatters seems to fix the issue of stale references
        # crashing pages, since it intercepts the display of all ReferenceField's.
        return Markup(
            '<span class="label label-danger">Error</span> <small>%s</small>' % e
        )

    if rel_model is None:
        return ''

    try:
        return Markup(
            '<a href="%s">%s</a>'
            % (
                url_for(
                    # Flask-Admin creates URL's namespaced w/ model class name, lowercase.
                    '%s.details_view' % rel_model.__class__.__name__.lower(),
                    id=rel_model.id,
                ),
                rel_model,
            )
        )
    except werkzeug.routing.BuildError as e:
        return Markup(
            '<span class="label label-danger">Error</span> <small>%s</small>' % e
        )


def generic_lazy_ref_formatter(view, context, model, name):
    """
    See Also
    --------
    diff_formatter
    """
    return generic_ref_formatter(view, context, model, name, True)


def generic_document_type_formatter(view, context, model, name):
    """Return AdminLog.document field wrapped in URL to its list view."""
    _document_model = model.get('document').document_type
    url = _document_model.get_admin_list_url()
    return Markup('<a href="%s">%s</a>' % (url, _document_model.__name__))


def generic_ref_list_formatter(view, context, model, name):
    field_type = model._fields[name]
    subfield_type = getattr(field_type, 'field', None)

    if subfield_type is None:
        return model.get(name)

    if isinstance(subfield_type, mongoengine.fields.ReferenceField):
        fields = []
        for rel_model in model.get(name):
            try:
                fields.append(
                    '<a href="%s">%s</a>'
                    % (
                        url_for(
                            '%s.details_view' % rel_model.__class__.__name__.lower(),
                            id=rel_model.id,
                        ),
                        rel_model,
                    )
                )
            except (werkzeug.routing.BuildError, AttributeError) as e:
                fields.append(
                    '<span class="label label-danger">Error</span> <small>%s</small>'
                    % e
                )
        return Markup(', '.join(fields))
    else:
        return model.get(name)
