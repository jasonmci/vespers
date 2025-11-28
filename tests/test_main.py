"""Tests for the main application module."""

from src import __version__
from src.main import VespersApp


def test_version():
    """Test that version is defined."""
    assert __version__ == "0.1.0"


def test_app_initialization():
    """Test that VespersApp can be instantiated."""
    app = VespersApp()
    assert app is not None
    assert isinstance(app, VespersApp)


def test_app_title():
    """Test that app has default title."""
    app = VespersApp()
    assert hasattr(app, "title")
