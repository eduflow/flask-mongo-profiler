# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pytest

import requests
from examples.flask_todo.app import create_app
from flask import url_for
from wsgi_intercept.interceptor import RequestsInterceptor

from flask_mongo_profiler.contrib.mongoengine import profiling as profiling_models


@pytest.fixture
def app():
    app = create_app()
    app.debug = True
    return app


@pytest.fixture(autouse=True)
def clear_db():
    profiling_models.ProfilingRequest.objects.delete()
    profiling_models.ProfilingQuery.objects.delete()


def test_example(app, client):
    with RequestsInterceptor(lambda: app.wsgi_app, host='localhost', port=5000) as url:
        response = requests.get(url)
        assert response.status_code == 200

    assert profiling_models.ProfilingRequest.objects.count() == 1
    assert profiling_models.ProfilingQuery.objects.count() == 1
    client.get(url_for('admin.index'))

    # List of requests
    client.get(url_for('profilingrequest.index_view'))

    # Pull a profiling artifact of the request created when visiting 'index'
    request_profile = profiling_models.ProfilingRequest.objects.first()
    client.get(url_for('profilingrequest.details_view', id=request_profile.id))

    client.get(url_for('profilingquery.index_view'))

    # Same as above,
    query_profile = profiling_models.ProfilingQuery.objects.first()
    client.get(url_for('profilingquery.details_view', id=query_profile.id))
