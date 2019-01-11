from functools import partial

import pluggy
import py
from tox import package

hookimpl = pluggy.HookimplMarker("tox")


@hookimpl
def tox_addoption(parser):
    parser.add_argument("--wheel", action="store_true", help="Use bdist_wheel instead of sdist")
    parser.add_testenv_attribute(
        name="wheel",
        type="bool",
        default=False,
        help="Use bdist_wheel instead of sdist",
    )
    parser.add_testenv_attribute(
        name="wheel_clean_build",
        type="bool",
        default=True,
        help="Clean build dirs before building the wheel",
    )


@hookimpl(hookwrapper=True)
def tox_package(session, venv):
    if session.config.option.wheel or venv.envconfig.wheel:
        original = package.build_package
        package.build_package = partial(build_package, venv=venv)
        try:
            yield
        finally:
            package.build_package = original
    else:
        yield


def build_package(config, report, session, venv):
    if config.isolated_build:
        report.warning("Disabling isolated_build, not supported with wheels.")
    return make_wheel(report, config, session, venv)


def make_wheel(report, config, session, venv):
    setup = config.setupdir.join("setup.py")
    if not setup.check():
        report.error("No setup.py file found. The expected location is: {}".format(setup))
        raise SystemExit(1)
    with session.newaction(None, "packaging") as action:
        action.setactivity("wheel-make", setup)
        if venv.envconfig.wheel_clean_build:
            action.setactivity("wheel-make", "cleaning up build directory ...")
            session.make_emptydir(config.setupdir.join("build"))
        session.make_emptydir(config.distdir)

        original_is_allowed_external = venv.is_allowed_external

        def is_allowed_external(path):
            if not original_is_allowed_external(path):
                raise RuntimeError("Couldn't find interpreter inside {} for building".format(venv))
            return True

        try:
            venv.is_allowed_external = is_allowed_external
            venv.status = 0
            venv.update(action=action)
            venv.test(
                name="wheel-make",
                commands=[["python", setup, "bdist_wheel", "--dist-dir", config.distdir]],
                redirect=False,
                ignore_outcome=False,
                ignore_errors=False,
                display_hash_seed=False,
            )
        finally:
            venv.is_allowed_external = original_is_allowed_external
        try:
            return config.distdir.listdir()[0]
        except py.error.ENOENT:
            # check if empty or comment only
            data = []
            with open(str(setup)) as fp:
                for line in fp:
                    if line and line[0] == "#":
                        continue
                    data.append(line)
            if not "".join(data).strip():
                report.error("setup.py is empty")
                raise SystemExit(1)
            report.error(
                "No dist directory found. Please check setup.py, e.g with:\n"
                "     python setup.py sdist"
            )
            raise SystemExit(1)
