import pytest

pytest_plugins = 'pytester',


@pytest.fixture
def testdir(testdir):
    testdir.tmpdir.join('tox.ini').write("""
[tox]
envlist = py27-{a,b}
""")
    testdir.tmpdir.join('setup.py').write("""
from setuptools import setup

setup(name='foobar')
""")
    testdir.tmpdir.join('build').ensure(dir=1)
    return testdir


@pytest.fixture(params=['', '--parallel 1 --parallel-live'], ids=['sequential', 'parallel'])
def options(request):
    return ['-e', 'py27-a,py27-b'] + request.param.split()


def test_disabled(testdir, options):
    result = testdir.run('tox', *options)
    result.stdout.fnmatch_lines([
        'GLOB sdist-make: *',
    ])


def test_enabled(testdir, options):
    result = testdir.run('tox', '--wheel', *options)
    result.stdout.fnmatch_lines([
        'py* wheel-make: *',
    ])
    assert result.stdout.str().count('running bdist_wheel') == 2
    assert result.ret == 0


def test_build_env(testdir, options):
    testdir.tmpdir.join('setup.cfg').write("""
[bdist_wheel]
universal = 1
""")
    testdir.tmpdir.join('tox.ini').write("""
[testenv]
wheel = true
wheel_build_env = build

[testenv:build]
""", mode='a')
    result = testdir.run('tox', *options)
    result.stdout.fnmatch_lines([
        'build wheel-make: *',
    ])
    assert result.stdout.str().count('running bdist_wheel') == 1
    assert result.ret == 0


@pytest.mark.parametrize('wheel_build_env', ['', 'wheel_build_env'])
def test_skip_usedevelop(testdir, options, wheel_build_env):
    testdir.tmpdir.join('tox.ini').write("""
[testenv]
usedevelop = true
""" + ("""
wheel_build_env = build

[testenv:build]
""" if wheel_build_env else ""), mode='a')
    result = testdir.run('tox', '-v', '--wheel', *options)
    stdout = result.stdout.str()
    assert stdout.count('wheel-make') == 0
    assert stdout.count('bdist_wheel') == 0
    assert result.ret == 0


def test_enabled_toxini_noclean(testdir, options):
    testdir.tmpdir.join('tox.ini').write("""
[testenv]
wheel = true
wheel_dirty = true
""", mode='a')
    result = testdir.run('tox', *options)
    result.stdout.fnmatch_lines([
        'py* wheel-make: *',
    ])
    assert 'cleaning up build directory ...' not in result.stdout.str()
    assert 'cleaning up build directory ...' not in result.stderr.str()
    assert result.ret == 0


def test_enabled_cli_noclean(testdir, options):
    testdir.tmpdir.join('tox.ini').write("""
[testenv]
wheel = true
""", mode='a')
    result = testdir.run('tox', '--wheel-dirty', *options)
    result.stdout.fnmatch_lines([
        'py* wheel-make: *',
    ])
    assert 'cleaning up build directory ...' not in result.stdout.str()
    assert 'cleaning up build directory ...' not in result.stderr.str()
    assert result.ret == 0


def test_enabled_toxini(testdir, options):
    testdir.tmpdir.join('tox.ini').write("""
[testenv]
wheel = true
""", mode='a')
    result = testdir.run('tox', '-vv', *options)
    result.stdout.fnmatch_lines([
        'py* wheel-make: *',
        'py* wheel-make: cleaning up build directory ...',
        '  removing *[\\/]build',
        'py* finish: packaging *',
        'copying new sdistfile to *.whl*',
    ])
    assert 'is not a supported wheel on this platform.' not in result.stdout.str()
    assert 'is not a supported wheel on this platform.' not in result.stderr.str()
