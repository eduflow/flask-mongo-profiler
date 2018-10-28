# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pytest

from examples.flask_todo.app import (
    create_app,
    setup_flask_admin,
    setup_flask_mongo_profiler,
)
from flask import url_for


@pytest.fixture
def app():
    app = create_app()
    app.debug = True
    setup_flask_mongo_profiler(app)
    setup_flask_admin(app)
    return app


def test_example(app, client):
    client.get(url_for('index'))
    client.get(url_for('admin.index'))
