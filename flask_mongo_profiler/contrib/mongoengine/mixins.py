# -*- coding: utf-8 -*-
from __future__ import unicode_literals


class GetAttributeMixin(object):
    def get(self, attr, default=None):
        if attr == '_id':
            attr = 'id'
        try:
            return self[attr]
        except KeyError:
            return default


class FlaskAdminURLMixin(object):
    """
    Add get_admin_url to models supported by Flask-Admin

    Flask-Admin creates URL's namespaced w/ model class name, lowercase.
    """

    def get_admin_url(self, _external=False):
        from flask import url_for

        return url_for(
            '%s.details_view' % self.__class__.__name__.lower(),
            id=self.id,
            _external=_external,
        )

    @classmethod
    def get_admin_list_url(_class, _external=False):
        from flask import url_for

        return url_for('%s.index_view' % _class.__name__.lower(), _external=_external)
