"""Smoke test for nexlink package-level attributes."""

import nexlink


def test_version_attribute():
    assert hasattr(nexlink, "__version__")
    assert isinstance(nexlink.__version__, str)
    assert nexlink.__version__ == "0.10.6"
