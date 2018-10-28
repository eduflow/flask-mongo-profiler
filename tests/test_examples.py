# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pytest

from examples.flask_todo.app import create_app
from flask import url_for


def setup_profiler(app):
    from flask_mongo_profiler.contrib.werkzeug.mongo import (
        LoggingMongoCommandLogger,
        QueuedMongoCommandLogger,
    )
    from flask_mongo_profiler.contrib.werkzeug.werkzeug_middleware import (
        ProfilerMiddleware
    )
    import pymongo

    mongo_logger = QueuedMongoCommandLogger()
    pymongo.monitoring.register(mongo_logger)
    app.wsgi_app = ProfilerMiddleware(
        app.wsgi_app,
        pymongo_logger=mongo_logger,
        ignored_url_patterns=['admin', 'favicon.ico'],
    )
    return app


@pytest.fixture
def app():
    app = create_app()
    app.debug = True
    setup_profiler(app)
    return app


def test_example(app, client):
    client.get(url_for('index'))
