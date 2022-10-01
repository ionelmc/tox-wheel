========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - tests
      - | |github-actions| |requires|
        | |coveralls| |codecov|
    * - package
      - | |version| |wheel| |supported-versions| |supported-implementations|
        | |commits-since|

.. |github-actions| image:: https://github.com/ionelmc/tox-wheel/actions/workflows/github-actions.yml/badge.svg
    :alt: GitHub Actions Build Status
    :target: https://github.com/ionelmc/tox-wheel/actions

.. |requires| image:: https://requires.io/github/ionelmc/tox-wheel/requirements.svg?branch=master
    :alt: Requirements Status
    :target: https://requires.io/github/ionelmc/tox-wheel/requirements/?branch=master

.. |coveralls| image:: https://coveralls.io/repos/ionelmc/tox-wheel/badge.svg?branch=master&service=github
    :alt: Coverage Status
    :target: https://coveralls.io/r/ionelmc/tox-wheel

.. |codecov| image:: https://codecov.io/gh/ionelmc/tox-wheel/branch/master/graphs/badge.svg?branch=master
    :alt: Coverage Status
    :target: https://codecov.io/github/ionelmc/tox-wheel

.. |version| image:: https://img.shields.io/pypi/v/tox-wheel.svg
    :alt: PyPI Package latest release
    :target: https://pypi.org/project/tox-wheel

.. |wheel| image:: https://img.shields.io/pypi/wheel/tox-wheel.svg
    :alt: PyPI Wheel
    :target: https://pypi.org/project/tox-wheel

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/tox-wheel.svg
    :alt: Supported versions
    :target: https://pypi.org/project/tox-wheel

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/tox-wheel.svg
    :alt: Supported implementations
    :target: https://pypi.org/project/tox-wheel

.. |commits-since| image:: https://img.shields.io/github/commits-since/ionelmc/tox-wheel/v1.0.0.svg
    :alt: Commits since latest release
    :target: https://github.com/ionelmc/tox-wheel/compare/v1.0.0...master



.. end-badges

A `tox <http://tox.readthedocs.org>`_ plugin that builds and installs wheels instead of sdist.

* Free software: BSD 2-Clause License

Installation
============

::

    pip install tox-wheel

You can also install the in-development version with::

    pip install https://github.com/ionelmc/tox-wheel/archive/master.zip


Documentation
=============

Enabling
--------

To enable either use ``tox --wheel`` or change your ``tox.ini`` if you always want the plugin to be enabled:

.. code-block:: ini

    [testenv]
    wheel = true

You can also use factors in ``tox.ini``:

.. code-block:: ini

    [tox]
    envlist = {py27,py35,py36,py37,py38,pypy,pypy3}-{cover,nocov}

    [testenv]
    wheel =
        cover: false
        nocov: true


Build configuration
-------------------

This plugin will build wheels for all the active environments. Note that building will be done in a batch before any testing starts
(in order to support ``tox --parallel`` mode).

If you can produce universal wheels you might want to configure the build env so that the wheel is only built once for all the envs:

.. code-block:: ini

    [testenv]
    wheel_build_env = build

    [testenv:build]

Note that you can also use ``wheel_build_env`` for situation where you have many environments for the same interpreter:

.. code-block:: ini

    [testenv:py38]
    ; regular testing

    [testenv:py38-extras]
    ; tests with optional dependencies
    wheel_build_env = py38

    [testenv:docs]
    ; docs building
    wheel_build_env = py38

The plugin cleans the build dir by default, in case you want to speed things further (at the risk of build caching problems)
you could use ``tox --wheel-dirty``.

You can also place this configuration in ``tox.ini`` but there will be a unpleasant surprise factor if you
ever hit the aforementioned build problems:

.. code-block:: ini

    [testenv]
    wheel_dirty = true

PEP517 support
--------------

If you have a custom ``[build-system] build-backend`` in your ``pyproject.toml`` you need to enable the PEP517 builder by
having this in your ``tox.ini``:

.. code-block:: ini

    [testenv]
    wheel_pep517 = true

Enabling this will delegate building to ``pip wheel --use-pep517``.

Development
===========

To run the all tests run::

    tox
