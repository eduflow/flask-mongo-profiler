Tools for profiling MongoDB on Flask / Werkzeug

|pypi| |docs| |build-status| |coverage| |license|

Installation
------------

.. code-block:: shell

   $ pip install --user flask-mongo-profiler

Project details
---------------

==============  ==========================================================
Python support  2.7, >= 3.5, pypy, pypy3
DB support      pymongo 3.7+, MongoEngine 0.15+ (optional)
Web support     Werkzeug 0.14+, Flask 1.0+ (optional)
Source          https://github.com/peergradeio/flask-mongo-profiler
Docs            https://flask-mongo-profiler.readthedocs.io
API             https://flask-mongo-profiler.readthedocs.io/en/latest/api.html
Changelog       https://flask-mongo-profiler.readthedocs.io/en/latest/history.html
Issues          https://github.com/peergradeio/flask-mongo-profiler/issues
Travis          http://travis-ci.org/peergradeio/flask-mongo-profiler
Test Coverage   https://codecov.io/gh/peergradeio/flask-mongo-profiler
pypi            https://pypi.python.org/pypi/flask-mongo-profiler
Open Hub        https://www.openhub.net/p/flask-mongo-profiler
License         `MIT`_.
git repo        .. code-block:: bash

                    $ git clone https://github.com/peergradeio/flask-mongo-profiler.git
install stable  .. code-block:: bash

                    $ pip install --user flask-mongo-profiler
install dev     .. code-block:: bash

                    $ git clone https://github.com/peergradeio/flask-mongo-profiler.git
                    $ cd ./flask-mongo-profiler
                    $ virtualenv .venv
                    $ source .venv/bin/activate
                    $ pip install -e .

                See the `developing and testing`_ page in the docs for
                more.
tests           .. code-block:: bash

                    $ make test
==============  ==========================================================

.. _MIT: http://opensource.org/licenses/MIT

.. |pypi| image:: https://img.shields.io/pypi/v/flask-mongo-profiler.svg
    :alt: Python Package
    :target: http://badge.fury.io/py/flask-mongo-profiler

.. |build-status| image:: https://img.shields.io/travis/peergradeio/flask-mongo-profiler.svg
   :alt: Build Status
   :target: https://travis-ci.org/peergradeio/flask-mongo-profiler

.. |coverage| image:: https://codecov.io/gh/peergradeio/flask-mongo-profiler/branch/master/graph/badge.svg
    :alt: Code Coverage
    :target: https://codecov.io/gh/peergradeio/flask-mongo-profiler

.. |license| image:: https://img.shields.io/github/license/peergradeio/flask-mongo-profiler.svg
    :alt: License 

.. |docs| image:: https://readthedocs.org/projects/flask-mongo-profiler/badge/?version=latest
    :alt: Documentation Status
    :scale: 100%
    :target: https://readthedocs.org/projects/flask-mongo-profiler/
