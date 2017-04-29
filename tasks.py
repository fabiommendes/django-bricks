import sys
from invoke import task


@task
def configure(ctx):
    """
    Instructions for preparing package for development.
    """

    ctx.run("%s -m pip install .[dev] -r requirements.txt" % sys.executable)
