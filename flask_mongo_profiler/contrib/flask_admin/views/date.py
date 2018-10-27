# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import logging

from application.utils.date import utc_time_to_local_time
from flask import Markup
from flask_login import current_user

logger = logging.getLogger(__name__)


def date_formatter(view, value):
    """
    We appear to store naive datetimes in our database.

    Formats the date, and if the user has a timezone that's different from the
    naive date, will append the naive date below appended with UTC.

    See Also
    --------
    """
    local_time = utc_time_to_local_time(value, user=current_user)
    cell = value.strftime('%Y-%m-%d %H:%M:%S %Z')
    if local_time != value:
        return Markup(
            '%s <br /><small>%s UTC</small>'
            % (
                utc_time_to_local_time(value, user=current_user).strftime(
                    '%Y-%m-%d %H:%M:%S %Z'
                ),
                cell,
            )
        )
    return cell


def object_id_creation_formatter(view, context, model, name):
    return date_formatter(view, model.id.generation_time.replace(tzinfo=None))
