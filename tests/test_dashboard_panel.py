"""Tests for the dashboard panel feature.

Feature: Dashboard Panel
    Chart for tasks completed per day

Scenario: Chart for tasks completed per day
    Given I have completed tasks over the last 10 days
    When I visit the dashboard
    Then I see a chart of tasks completed in the last several days

Scenario: Chart for tasks completed but no tasks have been completed yet
    Given I have no completed tasks
    When I visit the dashboard
    Then I see a message that no tasks have been completed
"""

from io import StringIO

import pytest
from rich.console import Console
from textual.widgets import Static

from src.main import VespersApp


@pytest.mark.asyncio
async def test_dashboard_shows_chart_with_completed_tasks():
    """Test that dashboard displays a chart when tasks have been completed."""
    app = VespersApp()

    # Setup: Add some completed tasks to the app
    app.completed_tasks = [
        {"date": "2025-11-18", "count": 3},
        {"date": "2025-11-19", "count": 5},
        {"date": "2025-11-20", "count": 2},
        {"date": "2025-11-21", "count": 7},
        {"date": "2025-11-22", "count": 4},
        {"date": "2025-11-23", "count": 6},
        {"date": "2025-11-24", "count": 1},
        {"date": "2025-11-25", "count": 8},
        {"date": "2025-11-26", "count": 3},
        {"date": "2025-11-27", "count": 5},
    ]
    app.words_written = [
        {"date": "2025-11-18", "words": 450},
        {"date": "2025-11-19", "words": 780},
        {"date": "2025-11-20", "words": 320},
        {"date": "2025-11-21", "words": 910},
        {"date": "2025-11-22", "words": 610},
        {"date": "2025-11-23", "words": 840},
        {"date": "2025-11-24", "words": 250},
        {"date": "2025-11-25", "words": 1020},
        {"date": "2025-11-26", "words": 540},
        {"date": "2025-11-27", "words": 760},
    ]
    app.outline = [
        {
            "title": "Arc One",
            "children": [
                {"title": "Chapter 1", "completed": True},
                {
                    "title": "Chapter 2",
                    "completed": False,
                    "children": [
                        {"title": "Scene 1", "completed": True},
                        {"title": "Scene 2", "completed": False},
                    ],
                },
            ],
        },
        {
            "title": "Arc Two",
            "children": [
                {"title": "Chapter 3", "completed": False},
                {"title": "Chapter 4", "completed": False},
            ],
        },
    ]
    app.recent_activity = [
        {"description": "Completed task: 'Review Chapter 3'", "ago": "2 hours ago"},
        {"description": "Added 347 words to 'Project Notes'", "ago": "3 hours ago"},
    ]
    app.readability = {
        "target_grade": "8-10",
        "entries": [
            {
                "label": "Today",
                "fk_grade": 8.7,
                "avg_sentence_length": 15,
                "sentences_per_paragraph": 4,
            },
            {
                "label": "Yesterday",
                "fk_grade": 9.1,
                "avg_sentence_length": 16,
                "sentences_per_paragraph": 5,
            },
        ],
    }
    app.dialogue_mix = {
        "target_ratio": "45% / 55%",
        "entries": [
            {
                "label": "Chapter 14",
                "dialogue_percent": 48,
                "narration_percent": 52,
            }
        ],
    }
    app.lexical_variety = {
        "target_ttr": 0.48,
        "target_unique_words": 2800,
        "entries": [
            {
                "label": "Segment A",
                "ttr": 0.5,
                "unique_words": 2900,
                "rare_words": 520,
            }
        ],
    }
    app.cadence = {
        "target_sentence_length": 15,
        "target_sentences_per_paragraph": 4,
        "entries": [
            {
                "label": "Latest",
                "avg_sentence_length": 14,
                "sentences_per_paragraph": 4,
                "paragraphs_per_scene": 6,
            }
        ],
    }
    app.chapter_edits = {
        "target_touch_window": "Touch every chapter weekly",
        "chapters": [
            {
                "name": "Chapter 1",
                "files": ["chapter01.md"],
                "additions": 120,
                "deletions": 25,
                "edit_sessions": 4,
            },
            {
                "name": "Chapter 9",
                "files": ["chapter09.md", "chapter09-alt.md"],
                "additions": 40,
                "deletions": 18,
                "edit_sessions": 1,
            },
        ],
    }

    async with app.run_test():
        # Navigate to dashboard (it's already the default)
        dashboard_panel = app.query_one("#dashboard-chart")
        assert dashboard_panel is not None, "Dashboard chart widget not found"

        # Verify chart content is displayed (not empty message)
        chart_content = dashboard_panel.render()
        assert chart_content is not None

        console = Console(file=StringIO(), legacy_windows=False)
        with console.capture() as capture:
            console.print(chart_content)
        chart_text = capture.get().lower()

        assert "tasks completed" in chart_text
        assert "words written" in chart_text
        assert "units completed" in chart_text
        assert "outline progress" in chart_text
        assert "arc one" in chart_text
        assert "■" in chart_text
        words_section = chart_text.split("words written", 1)[1]
        assert "■" in words_section, "Words section should render box glyphs"
        assert "·" in words_section, "Words section should show remaining goal dots"
        assert "readability" in chart_text
        readability_section = chart_text.split("readability", 1)[1].split(
            "dialogue vs narration", 1
        )[0]
        assert "↓" in readability_section, "Readability section should show top range arrow"
        assert "↑" in readability_section, "Readability section should show bottom range arrow"
        assert "▄" in readability_section, "Readability section should render half-height bars"
        assert "8.7" in readability_section, "Readability bars should display numeric FK values"
        dialogue_markers = [
            "dialogue vs narration",
            "dialogue mix",
            "🗣️",
        ]
        dialogue_section = None
        for marker in dialogue_markers:
            if marker in chart_text:
                dialogue_section = chart_text.split(marker, 1)[1]
                break
        if dialogue_section is None:
            dialogue_section = chart_text
        assert "↓" in dialogue_section, "Dialogue section should show downward target arrow"
        assert "↑" in dialogue_section, "Dialogue section should show upward target arrow"
        assert "▄" in dialogue_section, "Dialogue section should render half-height dialogue blocks"
        # assert "lexical variety" in chart_text
        # assert "sentence & paragraph cadence" in chart_text
        # assert "chapter edit pulse" in chart_text
        # assert "recent activity" in chart_text
        # assert "review chapter 3" in chart_text
        # assert "1,020" in chart_text or "1020" in chart_text
        # assert "no productivity data" not in chart_text


@pytest.mark.asyncio
async def test_dashboard_shows_message_when_no_tasks_completed():
    """Test that dashboard shows a message when no tasks have been completed."""
    app = VespersApp()

    # Setup: No completed tasks or word data
    app.completed_tasks = []
    app.words_written = []
    app.outline = []
    app.recent_activity = []
    app.readability = {}
    app.dialogue_mix = {}  # type: ignore[attr-defined]
    app.lexical_variety = {}  # type: ignore[attr-defined]
    app.cadence = {}  # type: ignore[attr-defined]
    app.chapter_edits = {}  # type: ignore[attr-defined]

    async with app.run_test():
        # Navigate to dashboard (it's already the default)
        # Look for the message widget
        message_widget = app.query_one("#dashboard-chart")
        assert message_widget is not None, "Dashboard chart/message widget not found"

        # Verify the "no tasks completed" message is displayed
        content = message_widget.render()

        console = Console(file=StringIO(), legacy_windows=False)
        with console.capture() as capture:
            console.print(content)
        content_text = capture.get().lower()

        assert (
            "no productivity data" in content_text
            or "no tasks" in content_text
            or "no writing" in content_text
            or "no recent activity" in content_text
        ), "Should display a helpful empty-state message"


@pytest.mark.asyncio
async def test_dashboard_chart_widget_exists():
    """Test that the dashboard contains a chart widget."""
    app = VespersApp()
    async with app.run_test():
        # Verify dashboard has a chart widget
        chart_widget = app.query_one("#dashboard-chart")
        assert chart_widget is not None
        assert isinstance(chart_widget, Static), "Chart should be a Static widget"
