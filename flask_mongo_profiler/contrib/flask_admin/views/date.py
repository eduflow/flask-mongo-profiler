# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import logging

from flask import Markup

logger = logging.getLogger(__name__)


def date_formatter(view, value):
    """
    We appear to store naive datetimes in our database.

    Formats the date, and if the user has a timezone that's different from the
    naive date, will append the naive date below appended with UTC.

    See Also
    --------
    """
    return Markup(value.strftime('%Y-%m-%d %H:%M:%S %Z'))
