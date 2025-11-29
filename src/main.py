"""Main application entry point."""

import json
from pathlib import Path

from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, Label, TabbedContent, TabPane

try:
    from .dashboard import DashboardChart
except ImportError:
    from dashboard import DashboardChart


class VespersApp(App):
    """A Textual application for Vespers."""

    BINDINGS = [
        ("q", "quit", "Quit"),
    ]

    def __init__(self, **kwargs):
        """Initialize the application."""
        super().__init__(**kwargs)
        # Load mock data from JSON file
        data = self._load_mock_data()
        self.completed_tasks: list[dict] = data.get("completed_tasks", [])
        self.words_written: list[dict] = data.get("words_written", [])
        self.outline: list[dict] = data.get("outline", [])
        self.recent_activity: list[dict] = data.get("recent_activity", [])
        self.readability: dict = data.get("readability", {})
        self.dialogue_mix: dict = data.get("dialogue_mix", {})
        self.lexical_variety: dict = data.get("lexical_variety", {})
        self.cadence: dict = data.get("cadence", {})
        self.chapter_edits: dict = data.get("chapter_edits", {})

    def _load_mock_data(self) -> dict:
        """Load mock data from JSON file."""
        mock_file = Path(__file__).parent.parent / "mock_data.json"
        if mock_file.exists():
            with open(mock_file, "r") as f:
                return json.load(f)
        return {}

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        with TabbedContent(initial="dashboard"):
            with TabPane("Dashboard", id="dashboard"):
                yield DashboardChart(
                    completed_tasks=self.completed_tasks,
                    words_written=self.words_written,
                    outline=self.outline,
                    recent_activity=self.recent_activity,
                    readability=self.readability,
                    dialogue_mix=self.dialogue_mix,
                    lexical_variety=self.lexical_variety,
                    cadence=self.cadence,
                    chapter_edits=self.chapter_edits,
                    id="dashboard-chart",
                )
            with TabPane("Task", id="task"):
                yield Label("Task content")
        yield Footer()


def main():
    """Run the Vespers application."""
    app = VespersApp()
    app.run()


if __name__ == "__main__":
    main()
