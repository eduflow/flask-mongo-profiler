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


def setup_flask_admin(app):
    from flask_admin import Admin
    from flask_mongo_profiler.contrib.flask_admin.views import (
        profiling as profiling_views
    )
    from flask_mongo_profiler.contrib.mongoengine import profiling as profiling_models

    admin = Admin(name='Peergrade', template_mode='bootstrap3')
    admin.add_view(
        profiling_views.ProfilingRequestView(
            profiling_models.ProfilingRequest, category='Profiling', name='Requests'
        )
    )
    admin.add_view(
        profiling_views.ProfilingQueryView(
            profiling_models.ProfilingQuery, category='Profiling', name='Queries'
        )
    )
    admin.init_app(app)
    return app


@pytest.fixture
def app():
    app = create_app()
    app.debug = True
    setup_profiler(app)
    setup_flask_admin(app)
    return app


def test_example(app, client):
    client.get(url_for('index'))
    client.get(url_for('admin.index'))
