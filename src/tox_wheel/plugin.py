import os.path
from contextlib import contextmanager
from functools import partial

import pluggy
import py
from tox import package
from tox import reporter
from tox.exception import InterpreterNotFound
from tox.package import get_package
from tox.util.path import ensure_empty_dir

hookimpl = pluggy.HookimplMarker("tox")


@hookimpl
def tox_addoption(parser):
    parser.add_argument(
        "--wheel",
        action="store_true",
        help="Build wheel instead of sdist",
    )
    parser.add_argument(
        "--wheel-dirty",
        action="store_true",
        help="Do not remove build directory (fast but dirty builds)",
    )
    parser.add_testenv_attribute(
        name="wheel",
        type="bool",
        default=False,
        help="Build wheel instead of sdist",
    )
    parser.add_testenv_attribute(
        name="wheel_pep517",
        type="string",
        default="",
        help=(
            "Build wheel using PEP 517/518 (pass true to build with pip or "
            "build to build with build)"
        ),
    )
    parser.add_testenv_attribute(
        name="wheel_dirty",
        type="bool",
        default=False,
        help="Do not remove build directory (fast but dirty builds)"
    )
    parser.add_testenv_attribute(
        name="wheel_build_env",
        type="string",
        default="{envname}",
        help="Environment to use for building the wheel. Default: %(default)r"
    )


@contextmanager
def patch(obj, attr, value):
    original = getattr(obj, attr)
    setattr(obj, attr, value)
    try:
        yield
    finally:
        setattr(obj, attr, original)


@hookimpl
def tox_testenv_install_deps(venv, action):
    if venv.envconfig.wheel_pep517 == "build":
        venv.run_install_command(["build[virtualenv]>=0.7.0"], action)
    return None


@hookimpl
def tox_package(session, venv):
    if session.config.option.wheel or venv.envconfig.wheel:
        build_venv = session.getvenv(venv.envconfig.wheel_build_env)
        if not hasattr(build_venv, "wheel_package"):
            try:
                with patch(package, "build_package", partial(wheel_build_package, venv=build_venv)):
                    build_venv.wheel_package, build_venv.wheel_dist = get_package(session)
            except InterpreterNotFound:
                if session.config.option.skip_missing_interpreters:
                    return None
                raise
        return build_venv.wheel_package

    elif hasattr(session, "package"):
        return session.package


def wheel_build_package(config, session, venv):
    if config.isolated_build or venv.envconfig.wheel_pep517:
        wheel_package = wheel_build_pep517(config, session, venv)
    else:
        wheel_package = wheel_build_legacy(config, session, venv)
    return wheel_package


def wheel_is_allowed_external(path, venv, is_allowed_external=None):
    if is_allowed_external is None:
        is_allowed_external = venv.is_allowed_external
    if not is_allowed_external(path):
        raise RuntimeError("Couldn't find interpreter inside {} for building".format(venv))
    return True


def wheel_build_legacy(config, session, venv):
    setup = config.setupdir.join("setup.py")
    if not setup.check():
        reporter.error("No setup.py file found. The expected location is: {}".format(setup))
        raise SystemExit(1)
    with session.newaction(venv.name, "packaging") as action:
        with patch(venv, "is_allowed_external", partial(wheel_is_allowed_external, venv=venv)):
            venv.update(action=action)
            if not (session.config.option.wheel_dirty or venv.envconfig.wheel_dirty):
                action.setactivity("wheel-make", "cleaning up build directory ...")
                ensure_empty_dir(config.setupdir.join("build"))
            ensure_empty_dir(config.distdir)
            venv.test(
                name="wheel-make",
                commands=[["python", setup, "bdist_wheel", "--dist-dir", config.distdir]],
                redirect=False,
                ignore_outcome=False,
                ignore_errors=False,
                display_hash_seed=False,
            )
        try:
            dists = config.distdir.listdir()
        except py.error.ENOENT:
            # check if empty or comment only
            data = []
            with open(str(setup)) as fp:
                for line in fp:
                    if line and line[0] == "#":
                        continue
                    data.append(line)
            if not "".join(data).strip():
                reporter.error("setup.py is empty")
                raise SystemExit(1)
            reporter.error(
                "No dist directory found. Please check setup.py, e.g with:\n"
                "     python setup.py bdist_wheel"
            )
            raise SystemExit(1)
        else:
            if not dists:
                reporter.error(
                    "No distributions found in the dist directory found. Please check setup.py, e.g with:\n"
                    "     python setup.py bdist_wheel"
                )
                raise SystemExit(1)
            return dists[0]


def wheel_build_pep517(config, session, venv):
    pyproject = config.setupdir.join("pyproject.toml")
    if not pyproject.check():
        reporter.error("No pyproject.toml file found. The expected location is: {}".format(pyproject))
        raise SystemExit(1)
    with session.newaction(venv.name, "packaging") as action:
        venv.update(action=action)
        if not (session.config.option.wheel_dirty or venv.envconfig.wheel_dirty):
            action.setactivity("wheel-make", "cleaning up build directory ...")
            ensure_empty_dir(config.setupdir.join("build"))
        ensure_empty_dir(config.distdir)
        if venv.envconfig.wheel_pep517 == "build":
            commands = [
                "python",
                "-Im",
                "build",
                "--outdir",
                config.distdir,
                config.setupdir,
            ]
        else:
            commands = [
                "pip",
                "wheel",
                config.setupdir,
                "--no-deps",
                "--use-pep517",
                "--wheel-dir",
                config.distdir,
            ]
        venv.test(
            name="wheel-make",
            commands=[commands],
            redirect=False,
            ignore_outcome=False,
            ignore_errors=False,
            display_hash_seed=False,
        )
        try:
            # we need to filter our list of dists to include only wheels
            dists = [dist for dist in config.distdir.listdir() if os.path.splitext(dist)[1] == ".whl"]
        except py.error.ENOENT:
            reporter.error(
                "No dist directory found. Please check pyproject.toml, e.g with:\n"
                "     pip wheel . --use-pep517"
            )
            raise SystemExit(1)
        else:
            if not dists:
                reporter.error(
                    "No distributions found in the dist directory found. Please check pyproject.toml, e.g with:\n"
                    "     pip wheel . --use-pep517"
                )
                raise SystemExit(1)
            return dists[0]
