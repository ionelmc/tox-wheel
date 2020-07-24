========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - tests
      - | |travis| |appveyor| |requires|
        |
    * - package
      - | |version| |wheel| |supported-versions| |supported-implementations|
        | |commits-since|

.. |travis| image:: https://api.travis-ci.org/ionelmc/tox-wheel.svg?branch=master
    :alt: Travis-CI Build Status
    :target: https://travis-ci.org/ionelmc/tox-wheel

.. |appveyor| image:: https://ci.appveyor.com/api/projects/status/github/ionelmc/tox-wheel?branch=master&svg=true
    :alt: AppVeyor Build Status
    :target: https://ci.appveyor.com/project/ionelmc/tox-wheel

.. |requires| image:: https://requires.io/github/ionelmc/tox-wheel/requirements.svg?branch=master
    :alt: Requirements Status
    :target: https://requires.io/github/ionelmc/tox-wheel/requirements/?branch=master

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

.. |commits-since| image:: https://img.shields.io/github/commits-since/ionelmc/tox-wheel/v0.4.2.svg
    :alt: Commits since latest release
    :target: https://github.com/ionelmc/tox-wheel/compare/v0.4.2...master

.. end-badges

A `tox <http://tox.readthedocs.org>`_ plugin that builds and installs wheels instead of sdist.

* Free software: BSD 2-Clause License

What does this plugin actually do? What it doesn't?

* It builds wheels for all the active environments.
  Unfortunately it's done in a batch before any testing starts (in order to support ``tox --parallel`` mode).

  However, you can configure it so it builds only once, if your project can build universal wheels.
* Universal wheels are not detected.

A Tox plugin that builds and installs wheels instead of sdist.

* Free software: BSD 2-Clause License

Installation
============

::

    pip install tox-wheel

You can also install the in-development version with::

    pip install https://github.com/ionelmc/tox-wheel/archive/master.zip


Documentation
=============


To use the project:

.. code-block:: python

    import tox_wheel
    tox_wheel.-()


Development
===========

To run the all tests run::

    tox

Note, to combine the coverage data from all the tox environments run:

.. list-table::
    :widths: 10 90
    :stub-columns: 1

    - - Windows
      - ::

            set PYTEST_ADDOPTS=--cov-append
            tox

    - - Other
      - ::

            PYTEST_ADDOPTS=--cov-append tox
