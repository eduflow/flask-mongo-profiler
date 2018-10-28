# -*- coding: utf-8 -*-
import os

import jinja2


def add_template_dirs(app):
    """Add flask_mongo_profiler's template directories.

    Parameters
    ----------
    app : flask.Flask
    """
    template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')

    app.jinja_loader = jinja2.ChoiceLoader(
        [app.jinja_loader, jinja2.FileSystemLoader(template_dir)]
    )
