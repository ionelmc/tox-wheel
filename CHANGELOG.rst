
Changelog
=========

1.0.0 (2022-10-01)
------------------

* Added option to build wheels (and sdists) in an isolated environment using `build <https://github.com/pypa/build>`_.
  Contributed by Ben Rowland in `#17 <https://github.com/ionelmc/tox-wheel/pull/17>`_.

0.7.0 (2021-12-29)
------------------

* Fixed build dir not being cleaned up in PEP 517 mode.
  Contributed by Michael Rans in `#16 <https://github.com/ionelmc/tox-wheel/pull/16>`_.
* Switched CI from Travis/AppVeyor to GitHub Actions.

0.6.0 (2020-11-06)
------------------

* Fixed unnecessary build directory cleanup and removed dead code.
  Contributed by Thomas Grainger in `#9 <https://github.com/ionelmc/tox-wheel/pull/9>`_.
* The ``isolated_build`` tox option is now an alias for ``wheel_pep517``.
  Contributed by Thomas Grainger in `#6 <https://github.com/ionelmc/tox-wheel/pull/6>`_.
* Added more configuration examples.

0.5.0 (2020-08-06)
------------------

* Added support for PEP 517/518.
  Contributed by Antonio Botelho in `#5 <https://github.com/ionelmc/tox-wheel/pull/5>`_.

0.4.2 (2019-05-15)
------------------

* Improved logging a bit so messages are less confusing (don't emit ``wheel-make path/to/setup.py``).
* Moved dist/build cleanup right before ``bdist_wheel``.

0.4.1 (2019-05-15)
------------------

* Improved error handling when no dists are built.

0.4.0 (2019-05-05)
------------------

* Fixed compatibility with tox and changed requirement for minimum tox version to 3.9.0.

0.3.0 (2019-01-26)
------------------

* Added support for ``tox --parallel`` mode.
* Added ``wheel_build_env`` config option.
* Renamed ``wheel_clean_build`` config option to ``wheel_dirty``.
* Added ``--wheel-dirty`` CLI argument.

0.2.1 (2019-01-12)
------------------

* Added ``wheel`` to dependencies.

0.2.0 (2019-01-12)
------------------

* Remove ``--wheel-clean-build`` CLI option. Build directory cleaning is now on by default.
  Correct behavior should be the default.
* Added support for ``[testenv] wheel`` (default: ``false``) and ``[testenv] wheel_clean_build`` (default: ``true``)
  in ``tox.ini``.

0.1.0 (2019-01-09)
------------------

* First release on PyPI.
