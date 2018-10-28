# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pytest

from examples.flask_todo.app import create_app
from flask import url_for


@pytest.fixture
def app():
    app = create_app()
    app.debug = True
    return app


def test_example(app, client):
    client.get(url_for('index'))
    client.get(url_for('admin.index'))
    client.get(url_for('profilingrequest.index_view'))
    client.get(url_for('profilingquery.index_view'))
