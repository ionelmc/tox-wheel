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


def test_disabled(testdir):
    result = testdir.run('tox', '-e', 'py27')
    result.stdout.fnmatch_lines([
        'GLOB sdist-make: *',
    ])


def test_enabled(testdir):
    result = testdir.run('tox', '-e', 'py27', '--wheel')
    result.stdout.fnmatch_lines([
        'GLOB wheel-make: *',
    ])
    assert result.ret == 0


def test_enabled_toxini_noclean(testdir):
    testdir.tmpdir.join('tox.ini').write("""
[testenv]
wheel = true
wheel_clean_build = false
""")
    result = testdir.run('tox', '-e', 'py27')
    result.stdout.fnmatch_lines([
        'GLOB wheel-make: *',
    ])
    assert 'cleaning up build directory ...' not in result.stdout.str()
    assert 'cleaning up build directory ...' not in result.stderr.str()
    assert result.ret == 0


def test_enabled_toxini(testdir):
    testdir.tmpdir.join('tox.ini').write("""
[testenv]
wheel = true
""")
    result = testdir.run('tox', '-vv', '-e', 'py27')
    result.stdout.fnmatch_lines([
        'GLOB wheel-make: *',
        'GLOB wheel-make: cleaning up build directory ...',
        '  removing *[\\/]build',
        'GLOB finish: packaging *',
        'copying new sdistfile to *.whl*',
    ])
    assert 'is not a supported wheel on this platform.' not in result.stdout.str()
    assert 'is not a supported wheel on this platform.' not in result.stderr.str()
