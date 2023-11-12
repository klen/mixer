import os

import nox

os.environ.update({"PDM_IGNORE_SAVED_PYTHON": "1"})


@nox.session
def tests(session):
    session.run_always("pdm", "install", "-G", "all", external=True)
    session.run("pytest")
