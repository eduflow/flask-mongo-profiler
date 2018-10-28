# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import mongoengine


class TodoTask(mongoengine.Document):
    title = mongoengine.fields.StringField()
