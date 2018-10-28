# -*- coding: utf-8 -*-
# flake8: noqa F401
import sys

try:
    try:
        from cProfile import Profile
    except ImportError:
        from profile import Profile
    from pstats import Stats

    stdlib_profiling_available = True
except ImportError:
    stdlib_profiling_available = False

PY2 = sys.version_info[0] == 2

if PY2:
    import ushlex as shlex
else:
    import shlex
