"""Tests for the base UI feature.

Feature: Base UI
    The UI has tabs for Task and Dashboard
    When starting the app, the UI defaults to Dashboard
"""

import pytest
from textual.widgets import TabbedContent, TabPane

from src.main import VespersApp


@pytest.mark.asyncio
async def test_app_has_tabbed_content():
    """Test that the app contains a TabbedContent widget."""
    app = VespersApp()
    async with app.run_test():
        tabbed_content = app.query_one(TabbedContent)
        assert tabbed_content is not None


@pytest.mark.asyncio
async def test_app_has_dashboard_tab():
    """Test that the app has a Dashboard tab."""
    app = VespersApp()
    async with app.run_test():
        tabbed_content = app.query_one(TabbedContent)
        # Query for a tab pane with id or title "dashboard"
        dashboard_tabs = [
            tab
            for tab in tabbed_content.query(TabPane)
            if "dashboard" in str(tab.id).lower()
        ]
        assert len(dashboard_tabs) > 0, "Dashboard tab not found"


@pytest.mark.asyncio
async def test_app_has_task_tab():
    """Test that the app has a Task tab."""
    app = VespersApp()
    async with app.run_test():
        tabbed_content = app.query_one(TabbedContent)
        # Query for a tab pane with id or title "task"
        task_tabs = [
            tab
            for tab in tabbed_content.query(TabPane)
            if "task" in str(tab.id).lower()
        ]
        assert len(task_tabs) > 0, "Task tab not found"


@pytest.mark.asyncio
async def test_dashboard_is_default_tab():
    """Test that the Dashboard tab is active by default on startup."""
    app = VespersApp()
    async with app.run_test():
        tabbed_content = app.query_one(TabbedContent)
        active_tab = tabbed_content.active
        assert active_tab is not None
        assert (
            "dashboard" in str(active_tab).lower()
        ), "Dashboard should be the default active tab"
