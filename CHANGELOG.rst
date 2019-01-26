
Changelog
=========

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
