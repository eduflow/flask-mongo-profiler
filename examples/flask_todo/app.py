# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from flask import Flask
from flask_mongoengine import MongoEngine

from .models import TodoTask


def create_app():
    app = Flask(__name__)
    app.config.from_object(__name__)
    app.config['MONGODB_SETTINGS'] = {'DB': 'testing'}
    app.config['TESTING'] = True
    db = MongoEngine()
    db.init_app(app)

    task = TodoTask(title='test title').save()

    @app.route('/')
    def index():
        return app.response_class(response=task.to_json(), mimetype='application/json')

    return app


app = create_app()
