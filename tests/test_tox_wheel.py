import pytest

pytest_plugins = 'pytester',


@pytest.fixture
def testdir(testdir):
    testdir.tmpdir.join('tox.ini').write("")
    testdir.tmpdir.join('setup.py').write("""
from setuptools import setup

setup(name='foobar')
""")
    testdir.tmpdir.join('build').ensure(dir=1)
    return testdir


@pytest.fixture(params=['', '--parallel 1 --parallel-live'], ids=['sequential', 'parallel'])
def options(request):
    return request.param.split()


def test_disabled(testdir, options):
    result = testdir.run('tox', '-e', 'py27,py36', *options)
    result.stdout.fnmatch_lines([
        'GLOB sdist-make: *',
    ])


def test_enabled(testdir, options):
    result = testdir.run('tox', '-e', 'py27,py36', '--wheel', *options)
    result.stdout.fnmatch_lines([
        'GLOB wheel-make: *',
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
""")
    result = testdir.run('tox', '-e', 'py27,py36', *options)
    result.stdout.fnmatch_lines([
        'GLOB wheel-make: *',
    ])
    assert result.stdout.str().count('running bdist_wheel') == 1
    assert result.ret == 0


def test_enabled_toxini_noclean(testdir, options):
    testdir.tmpdir.join('tox.ini').write("""
[testenv]
wheel = true
wheel_dirty = true
""")
    result = testdir.run('tox', '-e', 'py27,py36', *options)
    result.stdout.fnmatch_lines([
        'GLOB wheel-make: *',
    ])
    assert 'cleaning up build directory ...' not in result.stdout.str()
    assert 'cleaning up build directory ...' not in result.stderr.str()
    assert result.ret == 0


def test_enabled_cli_noclean(testdir, options):
    testdir.tmpdir.join('tox.ini').write("""
[testenv]
wheel = true
""")
    result = testdir.run('tox', '-e', 'py27,py36', '--wheel-dirty', *options)
    result.stdout.fnmatch_lines([
        'GLOB wheel-make: *',
    ])
    assert 'cleaning up build directory ...' not in result.stdout.str()
    assert 'cleaning up build directory ...' not in result.stderr.str()
    assert result.ret == 0


def test_enabled_toxini(testdir, options):
    testdir.tmpdir.join('tox.ini').write("""
[testenv]
wheel = true
""")
    result = testdir.run('tox', '-vv', '-e', 'py27,py36', *options)
    result.stdout.fnmatch_lines([
        'GLOB wheel-make: *',
        'GLOB wheel-make: cleaning up build directory ...',
        '  removing *[\\/]build',
        'GLOB finish: packaging *',
        'copying new sdistfile to *.whl*',
    ])
    assert 'is not a supported wheel on this platform.' not in result.stdout.str()
    assert 'is not a supported wheel on this platform.' not in result.stderr.str()
