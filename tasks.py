import sys
from invoke import task
from python_boilerplate.tasks.core import bump_version, doc_build


@task
def configure(ctx):
    """
    Instructions for preparing package for development.
    """

    ctx.run("%s -m pip install .[dev] -r requirements.txt" % sys.executable)
