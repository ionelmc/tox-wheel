import sys

import pytest

import tox_wheel.plugin

pytest_plugins = 'pytester',


@pytest.fixture
def testdir_legacy(testdir):
    testdir.tmpdir.join('tox.ini').write("""
[tox]
envlist = py-{a,b}
""")
    testdir.tmpdir.join('setup.py').write("""
from setuptools import setup

setup(name='foobar')
""")
    testdir.tmpdir.join('build').ensure(dir=1)
    return testdir


@pytest.fixture
def testdir_pep517(testdir):
    testdir.tmpdir.join('tox.ini').write("""
[tox]
envlist = py-{a,b}

[testenv]
wheel = true
wheel_pep517 = true
""")
    testdir.tmpdir.join('setup.py').write("""
from setuptools import setup

setup(name='foobar')
""")
    testdir.tmpdir.join('pyproject.toml').write("""
[build-system]
requires = [
    "setuptools >= 35.0.2"
]
build-backend = "setuptools.build_meta"
""")
    testdir.tmpdir.join('build').ensure(dir=1)
    return testdir


@pytest.fixture(params=['', '--parallel 1 --parallel-live'], ids=['sequential', 'parallel'])
def options(request):
    return ['-e', 'py-a,py-b'] + request.param.split()


def test_patch():
    class A(object):
        def __init__(self, a):
            self.a = a

    obj = A(10)
    with tox_wheel.plugin.patch(obj, 'a', 5):
        assert obj.a == 5
    assert obj.a == 10


def test_disabled(testdir_legacy, options):
    result = testdir_legacy.run('tox', *options)
    result.stdout.fnmatch_lines([
        'GLOB sdist-make: *',
    ])


def test_enabled_legacy(testdir_legacy, options):
    result = testdir_legacy.run('tox', '--wheel', *options)
    result.stdout.fnmatch_lines([
        'py* wheel-make: *',
    ])
    assert result.stdout.str().count('running bdist_wheel') == 2
    assert result.ret == 0


def test_enabled_pep517(testdir_pep517, options):
    result = testdir_pep517.run('tox', *options)
    result.stdout.fnmatch_lines([
        'py* wheel-make: *',
    ])
    if sys.version_info >= (3, 6):
        build_string = 'Building wheel for foobar (pyproject.toml)'
    else:
        build_string = 'Building wheel for foobar (PEP 517)'
    assert result.stdout.str().count(build_string) == 4
    assert result.ret == 0


def test_build_env_legacy(testdir_legacy, options):
    testdir_legacy.tmpdir.join('setup.cfg').write("""
[bdist_wheel]
universal = 1
""")
    testdir_legacy.tmpdir.join('tox.ini').write("""
[testenv]
wheel = true
wheel_build_env = build

[testenv:build]
""", mode='a')
    result = testdir_legacy.run('tox', *options)
    result.stdout.fnmatch_lines([
        'build wheel-make: *',
    ])
    assert result.stdout.str().count('running bdist_wheel') == 1
    assert result.ret == 0


def test_build_env_pep517(testdir_pep517, options):
    testdir_pep517.tmpdir.join('setup.cfg').write("""
[bdist_wheel]
universal = 1
""")
    testdir_pep517.tmpdir.join('tox.ini').write("""
wheel_build_env = build

[testenv:build]
""", mode='a')
    result = testdir_pep517.run('tox', *options)
    result.stdout.fnmatch_lines([
        'build wheel-make: *',
    ])
    if sys.version_info >= (3, 6):
        build_string = 'Building wheel for foobar (pyproject.toml)'
    else:
        build_string = 'Building wheel for foobar (PEP 517)'
    assert result.stdout.str().count(build_string) == 2
    assert result.ret == 0


@pytest.mark.parametrize('wheel_build_env', ['', 'wheel_build_env'])
def test_skip_usedevelop(testdir_legacy, options, wheel_build_env):
    testdir_legacy.tmpdir.join('tox.ini').write("""
[testenv]
usedevelop = true
""" + ("""
wheel_build_env = build

[testenv:build]
""" if wheel_build_env else ""), mode='a')
    result = testdir_legacy.run('tox', '-v', '--wheel', *options)
    stdout = result.stdout.str()
    assert stdout.count('wheel-make') == 0
    assert stdout.count('bdist_wheel') == 0
    assert result.ret == 0


def test_enabled_toxini_noclean_legacy(testdir_legacy, options):
    testdir_legacy.tmpdir.join('tox.ini').write("""
[testenv]
wheel = true
wheel_dirty = true
""", mode='a')
    result = testdir_legacy.run('tox', *options)
    result.stdout.fnmatch_lines([
        'py* wheel-make: *',
    ])
    assert 'cleaning up build directory ...' not in result.stdout.str()
    assert 'cleaning up build directory ...' not in result.stderr.str()
    assert result.ret == 0


def test_enabled_toxini_noclean_pep517(testdir_pep517, options):
    testdir_pep517.tmpdir.join('tox.ini').write("""
wheel_dirty = true
""", mode='a')
    result = testdir_pep517.run('tox', *options)
    result.stdout.fnmatch_lines([
        'py* wheel-make: *',
    ])
    assert 'cleaning up build directory ...' not in result.stdout.str()
    assert 'cleaning up build directory ...' not in result.stderr.str()
    assert result.ret == 0


def test_enabled_cli_noclean(testdir_legacy, options):
    testdir_legacy.tmpdir.join('tox.ini').write("""
[testenv]
wheel = true
""", mode='a')
    result = testdir_legacy.run('tox', '--wheel-dirty', *options)
    result.stdout.fnmatch_lines([
        'py* wheel-make: *',
    ])
    assert 'cleaning up build directory ...' not in result.stdout.str()
    assert 'cleaning up build directory ...' not in result.stderr.str()
    assert result.ret == 0


def test_enabled_toxini(testdir_legacy, options):
    testdir_legacy.tmpdir.join('tox.ini').write("""
[testenv]
wheel = true
""", mode='a')
    result = testdir_legacy.run('tox', '-vv', *options)
    result.stdout.fnmatch_lines([
        'py* wheel-make: *',
        'py* wheel-make: cleaning up build directory ...',
        '  removing *[\\/]build',
        'py* finish: packaging *',
        'copying new sdistfile to *.whl*',
    ])
    assert 'is not a supported wheel on this platform.' not in result.stdout.str()
    assert 'is not a supported wheel on this platform.' not in result.stderr.str()
