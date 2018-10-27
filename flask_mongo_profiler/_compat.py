# -*- coding: utf-8 -*-
# flake8: noqa F401

try:
    try:
        from cProfile import Profile
    except ImportError:
        from profile import Profile
    from pstats import Stats

    stdlib_profiling_available = True
except ImportError:
    stdlib_profiling_available = False
