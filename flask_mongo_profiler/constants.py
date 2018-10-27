# -*- coding: utf-8 -*-
import re

# Used to replace keys with for mongodb compatibility
# We will use these in admin formatters to show commands as they
# were originally outputted.

# These are found in Command's of pymongo.monitor event output

# e.g. $exists, $in
MONGO_COMMAND_KEY_DOLLAR_SIGN_REPLACEMENT = '__'

# e.g. parent.ref.$id ($ would be __ thanks to above)
MONGO_COMMAND_KEY_PERIOD_SIGN_REPLACEMENT = '-'

# Used to replace keys with . for mongodb compatibility
# e.g. wsgi.url_scheme
WERKZEUG_ENVIRON_KEY_REPLACEMENT = '-'

# Match MongoDB ObjectID pattern
RE_OBJECTID = re.compile('([0-9a-f]{24})')
