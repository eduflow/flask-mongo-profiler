# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from mongoengine import Document, EmbeddedDocument, fields

from .mixins import FlaskAdminURLMixin, GetAttributeMixin


class ProfilingRequest(Document, FlaskAdminURLMixin, GetAttributeMixin):
    method = fields.StringField()
    path = fields.StringField()
    referrer = fields.StringField()
    environ = fields.DictField()
    status = fields.DictField()
    pyprofile = fields.StringField()
    query_count = fields.IntField()
    duration = fields.DecimalField()
    query_duration = fields.DecimalField()
    time = fields.DateTimeField()

    def __unicode__(self):
        return '%s %s' % (self.get('method'), self.get('path'))


class ProfilingQueryConnection(EmbeddedDocument):
    """
    Examples
    --------
    Unpack ('localhost', 27017) tuple to dictionary:

    >>> params = dict(
    >>>    connection=model.ProfilingQueryConnection(*event.connection_id),
    >>> )

    All pymongo.monitoring event types include connection_id. The address (host, port)
    of the server this command was sent to.

    References
    ----------
    http://api.mongodb.com/python/current/api/pymongo/monitoring.html
    """

    host = fields.StringField()
    port = fields.IntField()


class ProfilingQuery(Document, FlaskAdminURLMixin, GetAttributeMixin):
    request = fields.ReferenceField(ProfilingRequest)
    command_name = fields.StringField()
    database_name = fields.StringField()
    operation_id = fields.IntField()
    connection = fields.EmbeddedDocumentField(ProfilingQueryConnection)  # connection_id
    request_id = fields.StringField()
    failure = fields.DictField()
    duration = fields.DecimalField()
    command = fields.DictField()

    def __unicode__(self):
        return '%s' % self.get('command_name', 'Command')
