import pytest
import bricks


def test_project_defines_author_and_version():
    assert hasattr(bricks, '__author__')
    assert hasattr(bricks, '__version__')
