# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

from flask import Flask
from flask_mongoengine import MongoEngine

from flask_mongo_profiler.helpers import add_template_dirs

from .models import TodoTask


def setup_flask_mongo_profiler(app):
    from flask_mongo_profiler.contrib.werkzeug.mongo import QueuedMongoCommandLogger
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


def create_app(init_profiler=True, init_admin=True):
    app = Flask(__name__)
    app.config.from_object(__name__)
    app.config['MONGODB_SETTINGS'] = {'DB': 'testing'}
    app.config['TESTING'] = True

    if init_profiler:  # has to start before pymongo client created
        setup_flask_mongo_profiler(app)

    db = MongoEngine()
    db.init_app(app)

    if init_admin:
        setup_flask_admin(app)

    add_template_dirs(app)

    @app.route('/')
    def index():
        TodoTask(title='test title').save()
        task = TodoTask.objects.first()
        return app.response_class(response=task.to_json(), mimetype='application/json')

    return app


if __name__ == '__main__' or os.getenv('FLASK_RUN_FROM_CLI') == 'true':
    """
    For some reason falling back onto create_app when running ``flask run`` doesn't
    bind pymongo.monitoring. See also: http://flask.pocoo.org/docs/1.0/cli/.
    """
    app = create_app()
